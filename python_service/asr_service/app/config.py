from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    asr_model_name: str = os.getenv("ASR_MODEL_NAME", "Qwen/Qwen3-ASR-0.6B")
    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_dtype: str = os.getenv("ASR_DTYPE", "float32")
    asr_max_batch_size: int = int(os.getenv("ASR_MAX_BATCH_SIZE", "1"))
    asr_max_new_tokens: int = int(os.getenv("ASR_MAX_NEW_TOKENS", "256"))

    note_model_name: str = os.getenv("NOTE_MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
    note_device: str = os.getenv("NOTE_DEVICE", "cpu")
    note_dtype: str = os.getenv("NOTE_DTYPE", "float32")
    note_max_new_tokens: int = int(os.getenv("NOTE_MAX_NEW_TOKENS", "1024"))


settings = Settings()