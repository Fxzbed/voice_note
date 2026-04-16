from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from app.core.task_pool import TaskPool
from app.core.model_pool import ModelPool
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.workers.asr_worker_pool import ASRWorkerPool


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("test_worker_pool_integration")


FINAL_STATES = {"asr_done", "vad_failed", "asr_failed"}


def format_task_line(task) -> str:
    return (
        f"task_id={task.task_id}, "
        f"status={task.status}, "
        f"segments={task.segment_count}, "
        f"segment_dir={task.segment_dir}, "
        f"result_text_file={task.result_text_file}, "
        f"error={task.error_message}"
    )


def log_task_status_change(task) -> None:
    logger.info("task changed: %s", format_task_line(task))


def validate_audio_files(audio_files: list[Path]) -> None:
    for path in audio_files:
        if not path.exists():
            raise FileNotFoundError(f"audio file not found: {path}")


def all_tasks_finished(task_pool: TaskPool) -> bool:
    for task in task_pool.list_tasks():
        current = task_pool.get_task(task.task_id)
        if current is None:
            continue
        if current.status not in FINAL_STATES:
            return False
    return True


def any_task_failed(task_pool: TaskPool) -> bool:
    for task in task_pool.list_tasks():
        current = task_pool.get_task(task.task_id)
        if current is None:
            continue
        if current.status in {"vad_failed", "asr_failed"}:
            return True
    return False


def print_final_summary(task_pool: TaskPool) -> None:
    logger.info("===== final task summary =====")

    for task in task_pool.list_tasks():
        current = task_pool.get_task(task.task_id)
        if current is None:
            continue

        logger.info(format_task_line(current))

        if current.result_text_file:
            logger.info("task_id=%s result file: %s", current.task_id, current.result_text_file)

        if current.result_text:
            preview = current.result_text[:1000]
            logger.info("task_id=%s ASR text preview:\n%s", current.task_id, preview)


def main() -> None:
    audio_files = [
        Path("./file/test4.mp3").resolve(),
        Path("./file/test.mp3").resolve(),
        Path("./file/test1.mp3").resolve(),
    ]
    validate_audio_files(audio_files)

    task_pool = TaskPool()
    model_pool = ModelPool()

    vad_service = VADService(
        output_dir="./tmp_segments",
        target_segment_duration_sec=60.0,
        max_segment_duration_sec=120.0,
    )

    asr_service = ASRService(model_pool=model_pool)
    asr_service.register_model(instance_count=2)

    worker_pool = ASRWorkerPool(
        task_pool=task_pool,
        vad_service=vad_service,
        asr_service=asr_service,
        worker_count=2,
        poll_interval=0.5,
    )

    worker_pool.start()
    logger.info("worker pool started")

    created_tasks = []
    for file_path in audio_files:
        task = task_pool.create_task(file_path=str(file_path), language=None)
        created_tasks.append(task)
        logger.info("submitted task: task_id=%s, file_path=%s", task.task_id, task.file_path)

    start_time = time.perf_counter()
    timeout_sec = 3600
    last_status_map: dict[int, str] = {}

    try:
        while True:
            for task in task_pool.list_tasks():
                current = task_pool.get_task(task.task_id)
                if current is None:
                    continue

                previous = last_status_map.get(current.task_id)
                if previous != current.status:
                    log_task_status_change(current)
                    last_status_map[current.task_id] = current.status

            logger.info(
                "runtime snapshot: model_pool=%s, queue_size=%s, running_task_ids=%s",
                model_pool.status(),
                task_pool.get_queue_size(),
                task_pool.get_running_task_ids(),
            )

            if all_tasks_finished(task_pool):
                break

            elapsed = time.perf_counter() - start_time
            if elapsed > timeout_sec:
                raise TimeoutError(f"test timeout after {timeout_sec}s")

            time.sleep(2.0)

        elapsed = time.perf_counter() - start_time
        logger.info("all tasks finished in %.2fs", elapsed)

        print_final_summary(task_pool)

        if any_task_failed(task_pool):
            raise RuntimeError("one or more tasks failed")

    finally:
        worker_pool.stop()
        logger.info("worker pool stopped")


if __name__ == "__main__":
    main()