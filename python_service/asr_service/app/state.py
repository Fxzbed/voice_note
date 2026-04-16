from __future__ import annotations

from dataclasses import dataclass

from app.core.task_pool import TaskPool
from app.core.model_pool import ModelPool
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.workers.asr_worker_pool import ASRWorkerPool


@dataclass
class AppState:
    task_pool: TaskPool
    model_pool: ModelPool
    vad_service: VADService
    asr_service: ASRService
    worker_pool: ASRWorkerPool