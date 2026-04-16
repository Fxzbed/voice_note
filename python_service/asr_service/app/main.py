from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.task_pool import TaskPool
from app.core.model_pool import ModelPool
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.workers.asr_worker_pool import ASRWorkerPool
from app.state import AppState
from app.services.note_service import NoteService


def build_container() -> AppState:
    task_pool = TaskPool()
    model_pool = ModelPool()

    vad_service = VADService(
        output_dir="./tmp_segments",
        target_segment_duration_sec=60.0,
        max_segment_duration_sec=120.0,
    )

    asr_service = ASRService(model_pool=model_pool)
    asr_service.register_model(instance_count=2)

    note_service = NoteService(model_pool=model_pool)
    note_service.register_model(instance_count=1)

    worker_pool = ASRWorkerPool(
        task_pool=task_pool,
        vad_service=vad_service,
        asr_service=asr_service,
        note_service=note_service,
        worker_count=2,
        poll_interval=0.5,
    )

    return AppState(
        task_pool=task_pool,
        model_pool=model_pool,
        vad_service=vad_service,
        asr_service=asr_service,
        worker_pool=worker_pool,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    app.state.container = container

    container.worker_pool.start()
    try:
        yield
    finally:
        container.worker_pool.stop()


app = FastAPI(
    title="ASR Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)