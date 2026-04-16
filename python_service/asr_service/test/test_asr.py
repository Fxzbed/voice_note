import os
import re
import time
from pathlib import Path

from app.core.model_pool import ModelPool
from app.services.asr_service import ASRService
from app.services.vad_service import AudioSegment


def load_segments_from_task_dir(task_dir: str) -> list[AudioSegment]:
    path = Path(task_dir)
    if not path.exists():
        raise FileNotFoundError(f"task dir not found: {task_dir}")

    files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".wav"]
    if not files:
        return []

    def extract_segment_index(file_path: Path) -> int:
        match = re.search(r"segment_(\d+)_", file_path.name)
        if not match:
            raise ValueError(f"invalid segment file name: {file_path.name}")
        return int(match.group(1))

    files.sort(key=extract_segment_index)

    segments: list[AudioSegment] = []
    for file_path in files:
        segment_id = extract_segment_index(file_path)

        segments.append(
            AudioSegment(
                segment_id=segment_id,
                start_sec=0.0,
                end_sec=0.0,
                file_path=str(file_path),
            )
        )

    return segments


def main():
    task_dir = "./tmp_segments/task_1"

    model_pool = ModelPool()
    asr_service = ASRService(model_pool=model_pool)
    asr_service.register_model(3)

    segments = load_segments_from_task_dir(task_dir)
    print(f"loaded segments: {len(segments)}")

    if not segments:
        print("no segments found")
        return

    t0 = time.perf_counter()
    result = asr_service.transcribe_segments(segments)
    t1 = time.perf_counter()

    for item in result.segments:
        print(f"[segment {item.segment_id}] text={item.text}")

    print("----------")
    print(f"language: {result.language}")
    print("full text:")
    print(result.text)
    print("----------")
    print(f"asr cost: {t1 - t0:.4f}s")


if __name__ == "__main__":
    main()