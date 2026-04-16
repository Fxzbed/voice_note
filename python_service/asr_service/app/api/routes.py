from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas import CreateTaskRequest, CreateTaskResponse, TaskResponse

router = APIRouter()


def _to_task_response(task) -> TaskResponse:
    return TaskResponse(
        task_id=task.task_id,
        file_path=task.file_path,
        language=task.language,
        status=task.status,
        error_message=task.error_message,
        segment_dir=task.segment_dir,
        segment_count=task.segment_count,
        result_text=task.result_text,
        result_text_file=getattr(task, "result_text_file", None),
        note_markdown=getattr(task, "note_markdown", None),
        note_markdown_file=getattr(task, "note_markdown_file", None),
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
            file_path=payload.file_path,
            language=payload.language,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CreateTaskResponse(
        task_id=task.task_id,
        status=task.status,
        file_path=task.file_path,
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
    tasks = state.task_pool.list_tasks()
    return [_to_task_response(task) for task in tasks]