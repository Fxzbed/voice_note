from __future__ import annotations

import os
import threading
import uuid
from dataclasses import dataclass
from typing import List

from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
import torchaudio


@dataclass
class AudioSegment:
    segment_id: int
    start_sec: float
    end_sec: float
    file_path: str


class VADService:
    def __init__(
        self,
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 400,
        speech_pad_ms: int = 0,
        target_segment_duration_sec: float = 60.0,
        max_segment_duration_sec: float = 120.0,
        output_dir: str = "./tmp_segments",
    ) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        self.target_segment_duration_sec = target_segment_duration_sec
        self.max_segment_duration_sec = max_segment_duration_sec
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        # 最小修复：串行化整个 VAD 流程，避免多线程并发触发底层库崩溃
        self._lock = threading.Lock()
        self.model = load_silero_vad()

    def split_audio(self, file_path: str, task_id: int) -> List[AudioSegment]:
        """
        输入原始音频，输出切片后的 segment 列表。

        规则：
        1. VAD 只负责找语音时间戳
        2. 不删除静音，最终切片是原音频上的连续时间块
        3. 先按时间戳聚合，尽量让每段 >= target_segment_duration_sec
        4. 如果连续时间块过长，再按 max_segment_duration_sec 切开
        5. 除最后一个片段外，尽量不小于 target_segment_duration_sec

        注意：
        - 这里通过实例级锁串行化 VAD，避免两个 worker 并发执行时崩溃
        """
        with self._lock:
            wav = read_audio(file_path, sampling_rate=self.sample_rate)

            speech_timestamps = get_speech_timestamps(
                wav,
                self.model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
                min_speech_duration_ms=self.min_speech_duration_ms,
                min_silence_duration_ms=self.min_silence_duration_ms,
                speech_pad_ms=self.speech_pad_ms,
                return_seconds=True,
            )

            if not speech_timestamps:
                return []

            aggregated_segments = self._aggregate_segments(speech_timestamps)
            final_segments = self._split_long_segments(aggregated_segments)

            task_dir = os.path.join(self.output_dir, f"task_{task_id}")
            os.makedirs(task_dir, exist_ok=True)

            segments: List[AudioSegment] = []
            for idx, seg in enumerate(final_segments):
                start_sec = float(seg["start"])
                end_sec = float(seg["end"])

                segment_path = os.path.join(
                    task_dir,
                    f"segment_{idx}_{uuid.uuid4().hex[:8]}.wav",
                )

                self._save_segment(
                    source_file=file_path,
                    start_sec=start_sec,
                    end_sec=end_sec,
                    output_file=segment_path,
                )

                segments.append(
                    AudioSegment(
                        segment_id=idx,
                        start_sec=start_sec,
                        end_sec=end_sec,
                        file_path=segment_path,
                    )
                )

            return segments

    def _aggregate_segments(self, speech_timestamps: list[dict]) -> list[dict]:
        """
        基于 VAD 的时间戳做连续时间窗口聚合。

        注意：
        - 不删除静音
        - 只用时间戳决定连续裁切区间的起止
        - 除最后一个片段外，尽量保证长度 >= target_segment_duration_sec
        """
        if not speech_timestamps:
            return []

        result: list[dict] = []

        current_start = float(speech_timestamps[0]["start"])
        current_end = float(speech_timestamps[0]["end"])

        for seg in speech_timestamps[1:]:
            next_start = float(seg["start"])
            next_end = float(seg["end"])

            current_duration = current_end - current_start
            merged_duration = next_end - current_start

            # 还没达到最短目标长度，继续向后扩展时间窗口
            if current_duration < self.target_segment_duration_sec:
                current_end = next_end
                continue

            # 达到目标长度后，如果继续扩展会超过最大长度，则先切开
            if merged_duration > self.max_segment_duration_sec:
                result.append({"start": current_start, "end": current_end})
                current_start = next_start
                current_end = next_end
                continue

            # 否则继续扩展，形成更完整的连续时间块
            current_end = next_end

        result.append({"start": current_start, "end": current_end})
        return result

    def _split_long_segments(self, segments: list[dict]) -> list[dict]:
        """
        对超过 max_segment_duration_sec 的连续时间块做二次切分。
        不做 padding。
        除最后一个子片段外，尽量保证 >= target_segment_duration_sec。
        """
        result: list[dict] = []

        for seg in segments:
            start = float(seg["start"])
            end = float(seg["end"])
            duration = end - start

            if duration <= self.max_segment_duration_sec:
                result.append({"start": start, "end": end})
                continue

            pieces: list[dict] = []
            current_start = start

            while (end - current_start) > self.max_segment_duration_sec:
                current_end = current_start + self.max_segment_duration_sec
                pieces.append({"start": current_start, "end": current_end})
                current_start = current_end

            tail = {"start": current_start, "end": end}
            tail_duration = tail["end"] - tail["start"]

            if not pieces:
                pieces.append(tail)
            else:
                # 尾巴太短时，并回前一段，避免出现非最后片过短
                if tail_duration < self.target_segment_duration_sec:
                    prev = pieces[-1]
                    pieces[-1] = {"start": prev["start"], "end": tail["end"]}
                else:
                    pieces.append(tail)

            result.extend(pieces)

        return result

    def _save_segment(
        self,
        source_file: str,
        start_sec: float,
        end_sec: float,
        output_file: str,
    ) -> None:
        """
        从原始音频裁出一段连续时间块并保存成 wav。
        注意：这会保留区间内部的静音。
        """
        waveform, sr = torchaudio.load(source_file)

        if sr != self.sample_rate:
            waveform = torchaudio.functional.resample(
                waveform,
                orig_freq=sr,
                new_freq=self.sample_rate,
            )
            sr = self.sample_rate

        start_frame = int(start_sec * sr)
        end_frame = int(end_sec * sr)

        segment_waveform = waveform[:, start_frame:end_frame]

        if segment_waveform.numel() == 0:
            raise ValueError("empty segment generated")

        torchaudio.save(output_file, segment_waveform, sr)