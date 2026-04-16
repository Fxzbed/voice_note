from __future__ import annotations

import time
from pathlib import Path

from app.core.task_pool import TaskPool, ASRTask
from app.core.model_pool import ModelPool
from app.services.vad_service import VADService
from app.services.asr_service import ASRService
from app.workers.asr_worker import ASRWorker
from app.workers.asr_worker_pool import ASRWorkerPool


def print_task_snapshot(task: ASRTask) -> None:
    print("---------- TASK SNAPSHOT ----------")
    print(f"task_id       : {task.task_id}")
    print(f"file_path     : {task.file_path}")
    print(f"language      : {task.language}")
    print(f"status        : {task.status}")
    print(f"segment_dir   : {task.segment_dir}")
    print(f"segment_count : {task.segment_count}")
    print(f"text length   : {len(task.text)}")
    print(f"error_message : {task.error_message}")
    print(f"created_at    : {task.created_at}")
    print(f"updated_at    : {task.updated_at}")
    print("-----------------------------------")


def main() -> None:
    # 1. 准备测试音频
    audio_path = Path("./file/test4.mp3").resolve()
    if not audio_path.exists():
        raise FileNotFoundError(f"test audio not found: {audio_path}")

    # 2. 初始化核心组件
    task_pool = TaskPool()
    model_pool = ModelPool()

    vad_service = VADService(output_dir="./tmp_segments")
    asr_service = ASRService(model_pool=model_pool)

    asr_worker_pool = ASRWorkerPool(task_pool=task_pool, asr_service=asr_service, vad_service=vad_service, )

    # 根据你的机器资源调整实例数
    asr_service.register_model(instance_count=2)

    worker = ASRWorker(
        task_pool=task_pool,
        vad_service=vad_service,
        asr_service=asr_service,
        poll_interval=0.5,
    )

    # 3. 启动 worker
    worker.start()
    print("worker started")

    # 4. 添加测试任务
    task = ASRTask(
        task_id=1,
        file_path=str(audio_path),
        language=None,
    )
    task_pool.add_task(task)
    print(f"task submitted: task_id={task.task_id}, file={task.file_path}")

    # 5. 轮询任务状态
    timeout_sec = 1800
    start_time = time.perf_counter()
    last_status = None

    try:
        while True:
            current = task_pool.get_task(task.task_id)
            if current is None:
                raise RuntimeError(f"task disappeared: {task.task_id}")

            # 只有状态变化时才打印，避免刷屏
            if current.status != last_status:
                elapsed = time.perf_counter() - start_time
                print(f"[{elapsed:.2f}s] status -> {current.status}")
                last_status = current.status

            # 成功结束
            if current.status == "asr_done":
                elapsed = time.perf_counter() - start_time
                print(f"\nTask finished successfully in {elapsed:.2f}s")
                print_task_snapshot(current)

                print("\n========== ASR TEXT ==========")
                print(current.text)
                print("========== END ==========\n")
                break

            # 失败结束
            if current.status == "failed":
                elapsed = time.perf_counter() - start_time
                print(f"\nTask failed in {elapsed:.2f}s")
                print_task_snapshot(current)
                raise RuntimeError(current.error_message or "unknown task failure")

            # 超时退出
            elapsed = time.perf_counter() - start_time
            if elapsed > timeout_sec:
                print_task_snapshot(current)
                raise TimeoutError(f"task timeout after {timeout_sec}s")

            time.sleep(1.0)

    finally:
        worker.stop()
        print("worker stopped")


if __name__ == "__main__":
    main()