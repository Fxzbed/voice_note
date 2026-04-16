from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class CreateTaskRequest(BaseModel):
    task_id: int
    file_path: str
    language: Optional[str] = None


class CreateTaskResponse(BaseModel):
    task_id: int
    status: str
    file_path: str
    language: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: int
    file_path: str
    language: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    segment_dir: Optional[str] = None
    segment_count: int = 0
    result_text: Optional[str] = None
    result_text_file: Optional[str] = None
    note_markdown: Optional[str] = None
    note_markdown_file: Optional[str] = None
    created_at: float
    updated_at: float