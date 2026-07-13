from __future__ import annotations

import logging
import os
import threading
import time
import json
from pathlib import Path
import jieba.analyse

from app.core.task_pool import (
    TaskPool,
    TASK_DOWNLOAD_PROCESSING,
    TASK_DOWNLOAD_DONE,
    TASK_DOWNLOAD_FAILED,
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
from app.services.structured_note_service import StructuredNoteService
from app.services.oss_download_service import OSSDownloadService

logger = logging.getLogger(__name__)


class ASRWorker:
    def __init__(
        self,
        worker_id: int,
        task_pool: TaskPool,
        vad_service: VADService,
        asr_service: ASRService,
        structured_note_service: StructuredNoteService,
        oss_download_service: OSSDownloadService,
        poll_interval: float = 1.0,
    ) -> None:
        self.worker_id = worker_id
        self.task_pool = task_pool
        self.vad_service = vad_service
        self.asr_service = asr_service
        self.structured_note_service = structured_note_service
        self.oss_download_service = oss_download_service
        self.poll_interval = poll_interval
        
    @staticmethod
    def _load_asr_text(file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"asr text file not found: {file_path}")
        return file_path.read_text(encoding="utf-8").strip()

    @staticmethod
    def _split_by_lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]
    
    @staticmethod
    def _extract_keywords_textrank(text: str, top_k: int = 3) -> list[str]:
        if not text or not text.strip():
            return []

        keywords = jieba.analyse.textrank(
            text,
            topK=top_k,
            withWeight=False,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz')
        )

        return [kw.strip() for kw in keywords if kw and kw.strip()]

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
            "worker-%s picked task: task_id=%s oss_object_key=%s",
            self.worker_id,
            task.task_id,
            task.oss_object_key,
        )

        # Step 0: 从 OSS 下载文件到本地
        self.task_pool.update_status(task_id, TASK_DOWNLOAD_PROCESSING)

        try:
            local_file_path = self.oss_download_service.download_to_local(
                task_id=task.task_id,
                original_name=task.original_name,
                object_key=task.oss_object_key,
            )
        except Exception as e:
            self.task_pool.update_status(task_id, TASK_DOWNLOAD_FAILED, str(e))
            raise

        self.task_pool.set_local_file_path(task_id, local_file_path)
        self.task_pool.update_status(task_id, TASK_DOWNLOAD_DONE)

        logger.info(
            "worker-%s download done: task_id=%s local_file_path=%s",
            self.worker_id,
            task.task_id,
            local_file_path,
        )

        # Step 1: VAD
        vad_started_at = time.time()
        self.task_pool.update_status(task_id, TASK_VAD_PROCESSING)

        try:
            segments = self.vad_service.split_audio(
                file_path=local_file_path,
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

        model_entry = self.asr_service.model_pool.acquire(self.asr_service.model_alias)
        try:
            result = self.asr_service.transcribe_task_dir(
                model_entry=model_entry,
                task_dir=task_dir,
                language=task.language,
            )
        except Exception as e:
            self.task_pool.update_status(task_id, TASK_ASR_FAILED, str(e))
            raise
        finally:
            self.asr_service.model_pool.release(model_entry)

        self.task_pool.set_asr_result(task_id, result.text)

        result_text_file = os.path.join(task_dir, "asr_result.txt")
        with open(result_text_file, "w", encoding="utf-8") as f:
            f.write(result.text)

        self.task_pool.set_asr_result_file(task_id, result_text_file)
        self.task_pool.update_status(task_id, TASK_ASR_DONE)

        logger.info(
            "worker-%s ASR done: task_id=%s elapsed=%.3fs result_file=%s",
            self.worker_id,
            task.task_id,
            time.time() - asr_started_at,
            result_text_file,
        )

                # Step 3: 完全按 ASR 行分段做结构化生成
        note_started_at = time.time()
        self.task_pool.update_status(task_id, TASK_NOTE_GENERATING)

        asr_text = self._load_asr_text(Path(result_text_file))
        text_segments = self._split_by_lines(asr_text)

        logger.info(
            "worker-%s NOTE start: task_id=%s line_segments=%s",
            self.worker_id,
            task.task_id,
            len(text_segments),
        )

        if not text_segments:
            self.task_pool.update_status(task_id, TASK_NOTE_FAILED, "no valid line segments found")
            raise ValueError("no valid line segments found")

        note_model_entry = self.structured_note_service.model_pool.acquire(
            self.structured_note_service.model_alias
        )

        try:
            notes = []

            for idx, seg_text in enumerate(text_segments):
                logger.info(
                    "worker-%s generating note for segment %s/%s: task_id=%s input_chars=%s",
                    self.worker_id,
                    idx + 1,
                    len(text_segments),
                    task.task_id,
                    len(seg_text),
                )

                result = self.structured_note_service.generate_structured_note(
                    model_entry=note_model_entry,
                    text_segment=seg_text,
                    language=task.language,
                )

                note_item = {
                    "summary": result.data.get("summary", ""),
                    "knowledge_points": result.data.get("knowledge_points", []),
                }
                notes.append(note_item)

                logger.info(
                    "worker-%s generated note for segment %s/%s: task_id=%s summary_len=%s knowledge_points=%s",
                    self.worker_id,
                    idx + 1,
                    len(text_segments),
                    task.task_id,
                    len(note_item["summary"]),
                    len(note_item["knowledge_points"]),
                )

        except Exception as e:
            self.task_pool.update_status(task_id, TASK_NOTE_FAILED, str(e))
            raise
        finally:
            self.structured_note_service.model_pool.release(note_model_entry)

        keywords = self._extract_keywords_textrank(asr_text, top_k=3)

        structured_note_payload = {
            "notes": notes,
            "keywords": keywords,
        }

        self.task_pool.set_structured_note_result(task_id, structured_note_payload)

        structured_note_file = os.path.join(task_dir, "structured_note.json")
        with open(structured_note_file, "w", encoding="utf-8") as f:
            json.dump(structured_note_payload, f, ensure_ascii=False, indent=2)

        self.task_pool.set_structured_note_file(task_id, structured_note_file)
        self.task_pool.update_status(task_id, TASK_NOTE_DONE)

        logger.info(
            "worker-%s NOTE done: task_id=%s elapsed=%.3fs note_file=%s",
            self.worker_id,
            task.task_id,
            time.time() - note_started_at,
            structured_note_file,
        )