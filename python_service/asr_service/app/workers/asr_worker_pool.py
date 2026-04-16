from __future__ import annotations

import logging
import threading

from app.core.task_pool import TaskPool
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.services.note_service import NoteService
from app.workers.asr_worker import ASRWorker

logger = logging.getLogger(__name__)


class ASRWorkerPool:
    def __init__(
        self,
        task_pool: TaskPool,
        vad_service: VADService,
        asr_service: ASRService,
        note_service: NoteService,
        worker_count: int = 1,
        poll_interval: float = 1.0,
    ) -> None:
        if worker_count <= 0:
            raise ValueError("worker_count must be greater than 0")

        self.task_pool = task_pool
        self.vad_service = vad_service
        self.asr_service = asr_service
        self.note_service = note_service
        self.worker_count = worker_count
        self.poll_interval = poll_interval

        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        alive_threads = [t for t in self._threads if t.is_alive()]
        if alive_threads:
            logger.warning("worker pool already started")
            return

        self._stop_event.clear()
        self._threads = []

        for i in range(self.worker_count):
            worker = ASRWorker(
                worker_id=i + 1,
                task_pool=self.task_pool,
                vad_service=self.vad_service,
                asr_service=self.asr_service,
                note_service=self.note_service,
                poll_interval=self.poll_interval,
            )

            thread = threading.Thread(
                target=worker.run,
                args=(self._stop_event,),
                daemon=True,
                name=f"asr-worker-{i + 1}",
            )
            thread.start()
            self._threads.append(thread)

        logger.info("worker pool started: worker_count=%s", self.worker_count)

    def stop(self, join_timeout: float = 3.0) -> None:
        self._stop_event.set()

        for thread in self._threads:
            thread.join(timeout=join_timeout)

        logger.info("worker pool stopped")

    def is_running(self) -> bool:
        return any(thread.is_alive() for thread in self._threads)