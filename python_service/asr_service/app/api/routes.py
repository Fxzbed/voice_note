from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.schemas import CreateTaskRequest, CreateTaskResponse, TaskResponse
from app.core.task_pool import TASK_NOTE_GENERATING, TASK_NOTE_DONE, TASK_NOTE_FAILED

router = APIRouter()



def _to_task_response(task) -> TaskResponse:
    return TaskResponse(
        task_id=task.task_id,
        original_name=task.original_name,
        oss_object_key=task.oss_object_key,
        local_file_path=task.local_file_path,
        language=task.language,
        status=task.status,
        error_message=task.error_message,
        segment_dir=task.segment_dir,
        segment_count=task.segment_count,
        result_text=task.result_text,
        result_text_file=task.result_text_file,
        structured_note_json=task.structured_note_json,
        structured_note_file=task.structured_note_file,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/health")
def health(request: Request):
    state = request.app.state.container
    return {
        "status": "ok",
        "worker_pool_running": state.worker_pool.is_running(),
        "queue_size": state.task_pool.get_queue_size(),
        "running_task_ids": state.task_pool.get_running_task_ids(),
    }


@router.get("/models/status")
def model_status(request: Request):
    state = request.app.state.container
    return state.model_pool.status()


@router.post("/tasks", response_model=CreateTaskResponse)
def create_task(payload: CreateTaskRequest, request: Request):
    state = request.app.state.container

    try:
        task = state.task_pool.create_task(
            task_id=payload.task_id,
            original_name=payload.original_name,
            oss_object_key=payload.oss_object_key,
            language=payload.language,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CreateTaskResponse(
        task_id=task.task_id,
        status=task.status,
        original_name=task.original_name,
        oss_object_key=task.oss_object_key,
        language=task.language,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, request: Request):
    state = request.app.state.container
    task = state.task_pool.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return _to_task_response(task)


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(request: Request):
    state = request.app.state.container
    return [_to_task_response(task) for task in state.task_pool.list_tasks()]

@router.post("/tasks/{task_id}/generate_note")
def generate_note(task_id: int, request: Request):
    state = request.app.state.container
    task = state.task_pool.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")

    if not task.result_text_file:
        raise HTTPException(status_code=400, detail="asr result file not found")

    state.task_pool.update_status(task_id, TASK_NOTE_GENERATING)

    input_file = Path(task.result_text_file)
    text = input_file.read_text(encoding="utf-8").strip()
    if not text:
        state.task_pool.update_status(task_id, TASK_NOTE_FAILED, "input text is empty")
        raise HTTPException(status_code=400, detail="input text is empty")

    segments = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            segments.append(line)

    if not segments:
        state.task_pool.update_status(task_id, TASK_NOTE_FAILED, "no valid line segments found")
        raise HTTPException(status_code=400, detail="no valid line segments found")

    model_entry = state.structured_note_service.model_pool.acquire(
        state.structured_note_service.model_alias
    )

    try:
        notes = []
        for seg_text in segments:
            result = state.structured_note_service.generate_structured_note(
                model_entry=model_entry,
                text_segment=seg_text,
                language=None,
            )
            notes.append(
                {
                    "summary": result.data.get("summary", ""),
                    "knowledge_points": result.data.get("knowledge_points", []),
                }
            )
    except Exception as e:
        state.task_pool.update_status(task_id, TASK_NOTE_FAILED, str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        state.structured_note_service.model_pool.release(model_entry)

    structured_note_payload = {"notes": notes}
    state.task_pool.set_structured_note_result(task_id, structured_note_payload)

    structured_note_file = Path(task.result_text_file).with_name("structured_note.json")
    with open(structured_note_file, "w", encoding="utf-8") as f:
        json.dump(structured_note_payload, f, ensure_ascii=False, indent=2)

    state.task_pool.set_structured_note_file(task_id, str(structured_note_file))
    state.task_pool.update_status(task_id, TASK_NOTE_DONE)

    return structured_note_payload