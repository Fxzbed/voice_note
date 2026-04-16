from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import torch
from qwen_asr import Qwen3ASRModel

from app.config import settings
from app.core.model_pool import ModelPool, ModelEntry


@dataclass
class SegmentFile:
    segment_id: int
    file_path: str


@dataclass
class ASRSegmentResult:
    segment_id: int
    file_path: str
    text: str


@dataclass
class ASRTranscriptionResult:
    text: str
    language: Optional[str]
    segments: List[ASRSegmentResult]


def _resolve_torch_dtype(dtype_str: str):
    mapping = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    if dtype_str not in mapping:
        raise ValueError(f"unsupported dtype: {dtype_str}")
    return mapping[dtype_str]


class ASRService:
    def __init__(self, model_pool: ModelPool, model_alias: str = "qwen_asr") -> None:
        self.model_pool = model_pool
        self.model_alias = model_alias

    def register_model(self, instance_count: int = 1) -> None:
        def loader():
            dtype = _resolve_torch_dtype(settings.asr_dtype)
            model = Qwen3ASRModel.from_pretrained(
                settings.asr_model_name,
                dtype=dtype,
                device_map=settings.asr_device,
                max_inference_batch_size=settings.asr_max_batch_size,
                max_new_tokens=settings.asr_max_new_tokens,
            )
            return model

        self.model_pool.register(
            alias=self.model_alias,
            loader=loader,
            instance_count=instance_count,
        )

    def load_segment_files(self, task_dir: str) -> List[SegmentFile]:
        path = Path(task_dir)
        if not path.exists():
            raise FileNotFoundError(f"task dir not found: {task_dir}")

        files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".wav"]
        if not files:
            return []

        pattern = re.compile(r"segment_(\d+)_")

        def parse_segment_id(file_path: Path) -> int:
            match = pattern.search(file_path.name)
            if not match:
                raise ValueError(f"invalid segment filename: {file_path.name}")
            return int(match.group(1))

        files.sort(key=parse_segment_id)

        return [
            SegmentFile(
                segment_id=parse_segment_id(file_path),
                file_path=str(file_path),
            )
            for file_path in files
        ]

    def transcribe_task_dir(
        self,
        model_entry: ModelEntry,
        task_dir: str,
        language: Optional[str] = None,
    ) -> ASRTranscriptionResult:
        segment_files = self.load_segment_files(task_dir)
        if not segment_files:
            return ASRTranscriptionResult(text="", language=language, segments=[])

        results: List[ASRSegmentResult] = []
        detected_language: Optional[str] = None

        for seg in segment_files:
            output = model_entry.model.transcribe(
                audio=seg.file_path,
                language=language,
            )

            if not output:
                raise RuntimeError(f"empty ASR result for file: {seg.file_path}")

            item = output[0]
            text = (getattr(item, "text", "") or "").strip()

            if detected_language is None:
                detected_language = getattr(item, "language", None)

            results.append(
                ASRSegmentResult(
                    segment_id=seg.segment_id,
                    file_path=seg.file_path,
                    text=text,
                )
            )

        full_text = "\n".join([x.text for x in results if x.text])

        return ASRTranscriptionResult(
            text=full_text,
            language=detected_language or language,
            segments=results,
        )