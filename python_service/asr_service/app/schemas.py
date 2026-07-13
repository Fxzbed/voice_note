from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class CreateTaskRequest(BaseModel):
    task_id: int
    original_name: str
    oss_object_key: str
    language: Optional[str] = None


class CreateTaskResponse(BaseModel):
    task_id: int
    status: str
    original_name: str
    oss_object_key: str
    language: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: int
    original_name: str
    oss_object_key: str
    local_file_path: Optional[str] = None
    language: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    segment_dir: Optional[str] = None
    segment_count: int = 0
    result_text: Optional[str] = None
    result_text_file: Optional[str] = None
    structured_note_json: Optional[dict] = None
    structured_note_file: Optional[str] = None
    created_at: float
    updated_at: float