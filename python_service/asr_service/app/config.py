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

    note_base_model_name: str = os.getenv("NOTE_BASE_MODEL_NAME", "Qwen/Qwen2.5-3B-Instruct")
    note_lora_path: str = os.getenv("NOTE_LORA_PATH", "../model/checkpoint-140")
    note_device: str = os.getenv("NOTE_DEVICE", "auto")
    note_dtype: str = os.getenv("NOTE_DTYPE", "bfloat16")
    note_max_length: int = int(os.getenv("NOTE_MAX_LENGTH", "512"))
    note_max_new_tokens: int = int(os.getenv("NOTE_MAX_NEW_TOKENS", "512"))

    oss_region: str = "cn-chengdu"
    oss_bucket: str = "voice-note-fxzbed"
    oss_endpoint: str = "https://oss-cn-chengdu.aliyuncs.com"
    ACCESS_KEY_ID = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    ACCESS_KEY_SECRET = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")


settings = Settings()
