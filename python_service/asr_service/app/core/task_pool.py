from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Optional


TASK_PENDING = "pending"

TASK_DOWNLOAD_PROCESSING = "download_processing"
TASK_DOWNLOAD_DONE = "download_done"
TASK_DOWNLOAD_FAILED = "download_failed"

TASK_VAD_PROCESSING = "vad_processing"
TASK_VAD_DONE = "vad_done"
TASK_VAD_FAILED = "vad_failed"

TASK_ASR_PROCESSING = "asr_processing"
TASK_ASR_DONE = "asr_done"
TASK_ASR_FAILED = "asr_failed"

TASK_NOTE_GENERATING = "note_generating"
TASK_NOTE_DONE = "note_done"
TASK_NOTE_FAILED = "note_failed"


@dataclass
class Task:
    task_id: int
    original_name: str
    oss_object_key: str
    language: str | None = None

    local_file_path: str | None = None

    status: str = TASK_PENDING
    error_message: str | None = None

    segment_dir: str | None = None
    segment_count: int = 0

    result_text: str | None = None
    result_text_file: str | None = None

    structured_note_json: dict | None = None
    structured_note_file: str | None = None

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class TaskPool:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._pending_queue: queue.Queue[int] = queue.Queue()
        self._tasks: dict[int, Task] = {}
        self._running_task_ids: set[int] = set()

    def create_task(
        self,
        task_id: int,
        original_name: str,
        oss_object_key: str,
        language: str | None = None,
    ) -> Task:
        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"task already exists: {task_id}")

            task = Task(
                task_id=task_id,
                original_name=original_name,
                oss_object_key=oss_object_key,
                language=language,
            )
            self._tasks[task.task_id] = task

        self._pending_queue.put(task.task_id)
        return task

    def get_next_task_id(self, timeout: float | None = None) -> Optional[int]:
        try:
            task_id = self._pending_queue.get(timeout=timeout)
        except queue.Empty:
            return None

        with self._lock:
            self._running_task_ids.add(task_id)

        return task_id

    def mark_done(self, task_id: int) -> None:
        with self._lock:
            self._running_task_ids.discard(task_id)
        self._pending_queue.task_done()

    def get_task(self, task_id: int) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    def update_status(
        self,
        task_id: int,
        status: str,
        error_message: str | None = None,
    ) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.status = status
            task.error_message = error_message
            task.updated_at = time.time()

    def set_local_file_path(self, task_id: int, local_file_path: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.local_file_path = local_file_path
            task.updated_at = time.time()

    def set_vad_result(self, task_id: int, segment_dir: str, segment_count: int) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.segment_dir = segment_dir
            task.segment_count = segment_count
            task.updated_at = time.time()

    def set_asr_result(self, task_id: int, text: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.result_text = text
            task.updated_at = time.time()

    def set_asr_result_file(self, task_id: int, file_path: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.result_text_file = file_path
            task.updated_at = time.time()

    def set_structured_note_result(self, task_id: int, data: dict) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.structured_note_json = data
            task.updated_at = time.time()

    def set_structured_note_file(self, task_id: int, file_path: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise ValueError(f"task not found: {task_id}")
            task.structured_note_file = file_path
            task.updated_at = time.time()

    def get_queue_size(self) -> int:
        return self._pending_queue.qsize()

    def get_running_task_ids(self) -> list[int]:
        with self._lock:
            return list(self._running_task_ids)