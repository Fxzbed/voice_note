from __future__ import annotations

import logging
import os
import threading
import time

from app.core.task_pool import (
    TaskPool,
    TASK_VAD_PROCESSING,
    TASK_VAD_DONE,
    TASK_VAD_FAILED,
    TASK_ASR_PROCESSING,
    TASK_ASR_DONE,
    TASK_ASR_FAILED,
    TASK_NOTE_GENERATING,
    TASK_NOTE_DONE,
    TASK_NOTE_FAILED,
)
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.services.note_service import NoteService

logger = logging.getLogger(__name__)


class ASRWorker:
    def __init__(
        self,
        worker_id: int,
        task_pool: TaskPool,
        vad_service: VADService,
        asr_service: ASRService,
        note_service: NoteService,
        poll_interval: float = 1.0,
    ) -> None:
        self.worker_id = worker_id
        self.task_pool = task_pool
        self.vad_service = vad_service
        self.asr_service = asr_service
        self.note_service = note_service
        self.poll_interval = poll_interval

    def run(self, stop_event: threading.Event) -> None:
        logger.info("worker-%s started", self.worker_id)

        while not stop_event.is_set():
            task_id = self.task_pool.get_next_task_id(timeout=self.poll_interval)
            if task_id is None:
                continue

            try:
                self._process_task(task_id)
            except Exception:
                logger.exception("worker-%s process task failed: task_id=%s", self.worker_id, task_id)
            finally:
                self.task_pool.mark_done(task_id)

        logger.info("worker-%s stopped", self.worker_id)

    def _process_task(self, task_id: int) -> None:
        task = self.task_pool.get_task(task_id)
        if task is None:
            raise ValueError(f"task not found: {task_id}")

        logger.info(
            "worker-%s picked task: task_id=%s file_path=%s",
            self.worker_id,
            task.task_id,
            task.file_path,
        )

        # Step 1: VAD
        vad_started_at = time.time()
        self.task_pool.update_status(task_id, TASK_VAD_PROCESSING)

        try:
            segments = self.vad_service.split_audio(
                file_path=task.file_path,
                task_id=task.task_id,
            )
        except Exception as e:
            self.task_pool.update_status(task_id, TASK_VAD_FAILED, str(e))
            raise

        task_dir = f"{self.vad_service.output_dir}/task_{task.task_id}"

        self.task_pool.set_vad_result(
            task_id=task_id,
            segment_dir=task_dir,
            segment_count=len(segments),
        )
        self.task_pool.update_status(task_id, TASK_VAD_DONE)

        logger.info(
            "worker-%s VAD done: task_id=%s segments=%s elapsed=%.3fs",
            self.worker_id,
            task.task_id,
            len(segments),
            time.time() - vad_started_at,
        )

        # Step 2: ASR
        asr_started_at = time.time()
        self.task_pool.update_status(task_id, TASK_ASR_PROCESSING)

        asr_model_entry = self.asr_service.model_pool.acquire(self.asr_service.model_alias)
        try:
            asr_result = self.asr_service.transcribe_task_dir(
                model_entry=asr_model_entry,
                task_dir=task_dir,
                language=task.language,
            )
        except Exception as e:
            self.task_pool.update_status(task_id, TASK_ASR_FAILED, str(e))
            raise
        finally:
            self.asr_service.model_pool.release(asr_model_entry)

        self.task_pool.set_asr_result(task_id, asr_result.text)

        result_text_file = os.path.join(task_dir, "asr_result.txt")
        with open(result_text_file, "w", encoding="utf-8") as f:
            f.write(asr_result.text)

        self.task_pool.set_asr_result_file(task_id, result_text_file)
        self.task_pool.update_status(task_id, TASK_ASR_DONE)

        logger.info(
            "worker-%s ASR done: task_id=%s elapsed=%.3fs result_file=%s",
            self.worker_id,
            task.task_id,
            time.time() - asr_started_at,
            result_text_file,
        )

        # Step 3: Note generation
        note_started_at = time.time()
        self.task_pool.update_status(task_id, TASK_NOTE_GENERATING)

        note_model_entry = self.note_service.model_pool.acquire(self.note_service.model_alias)
        try:
            note_result = self.note_service.generate_markdown_note(
                model_entry=note_model_entry,
                transcript=asr_result.text,
                language=task.language,
            )
        except Exception as e:
            self.task_pool.update_status(task_id, TASK_NOTE_FAILED, str(e))
            raise
        finally:
            self.note_service.model_pool.release(note_model_entry)

        self.task_pool.set_note_result(task_id, note_result.markdown)

        note_file = os.path.join(task_dir, "note.md")
        with open(note_file, "w", encoding="utf-8") as f:
            f.write(note_result.markdown)

        self.task_pool.set_note_result_file(task_id, note_file)
        self.task_pool.update_status(task_id, TASK_NOTE_DONE)

        logger.info(
            "worker-%s NOTE done: task_id=%s elapsed=%.3fs note_file=%s",
            self.worker_id,
            task.task_id,
            time.time() - note_started_at,
            note_file,
        )