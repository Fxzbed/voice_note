import time

from app.services.vad_service import VADService

vad = VADService(
    sample_rate=16000,
    target_segment_duration_sec=60.0,
    max_segment_duration_sec=120.0,
    max_merge_silence_gap_sec=1.5,
    output_dir="./tmp_segments",
)

audio_path = "./file/test4.mp3"

start_time = time.perf_counter()
segments = vad.split_audio(audio_path, task_id=1)
end_time = time.perf_counter()

total_segment_duration = 0.0

for seg in segments:
    duration = seg.end_sec - seg.start_sec
    total_segment_duration += duration
    print(
        f"segment_id={seg.segment_id}, "
        f"start={seg.start_sec:.2f}s, "
        f"end={seg.end_sec:.2f}s, "
        f"duration={duration:.2f}s, "
        f"path={seg.file_path}"
    )

print(f"segments count: {len(segments)}")
print(f"total speech duration: {total_segment_duration:.2f}s")
print(f"total cost: {end_time - start_time:.4f}s")