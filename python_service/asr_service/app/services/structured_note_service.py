from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from app.config import settings
from app.core.model_pool import ModelPool, ModelEntry

import time


logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """请根据下面的课堂文本生成严格 JSON 输出。
要求：
1. summary 为简洁摘要；
2. knowledge_points 为 3-8 条高度概括的知识点；
3. 输出格式必须为：{{"summary": "...", "knowledge_points": ["...", "..."]}}；
4. 只输出合法 JSON，不要输出额外解释。


课堂文本：
{input_text}

输出：
"""


@dataclass
class StructuredNoteResult:
    data: dict
    raw_output: str
    parse_ok: bool
    field_ok: bool
    model_instance_id: int


def safe_json_parse(text: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    text = text.strip()

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return True, obj
    except Exception:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            obj = json.loads(text[start:end + 1])
            if isinstance(obj, dict):
                return True, obj
    except Exception:
        pass

    return False, None


def has_required_fields(obj: Dict[str, Any]) -> bool:
    if not isinstance(obj, dict):
        return False
    if "summary" not in obj or "knowledge_points" not in obj:
        return False
    if not isinstance(obj["summary"], str):
        return False
    if not isinstance(obj["knowledge_points"], list):
        return False
    return True


def _resolve_torch_dtype(dtype_str: str):
    mapping = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    if dtype_str not in mapping:
        raise ValueError(f"unsupported dtype: {dtype_str}")
    return mapping[dtype_str]


class StructuredNoteService:
    def __init__(self, model_pool: ModelPool, model_alias: str = "qwen_structured_note") -> None:
        self.model_pool = model_pool
        self.model_alias = model_alias

    def register_model(self, instance_count: int = 1) -> None:
        def loader():
            dtype = _resolve_torch_dtype(settings.note_dtype)

            logger.info(
                "loading structured note model: base=%s lora=%s device=%s dtype=%s",
                settings.note_base_model_name,
                settings.note_lora_path,
                settings.note_device,
                settings.note_dtype,
            )

            tokenizer = AutoTokenizer.from_pretrained(
                settings.note_base_model_name,
                use_fast=False,
                trust_remote_code=True,
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            base_model = AutoModelForCausalLM.from_pretrained(
                settings.note_base_model_name,
                dtype=dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=False,
            )

            if settings.note_device == "cpu":
                base_model = base_model.to("cpu")
            elif settings.note_device.startswith("cuda"):
                base_model = base_model.to(settings.note_device)

            model = PeftModel.from_pretrained(
                base_model,
                settings.note_lora_path,
            )
            model.eval()

            logger.info("structured note model loaded successfully")

            return {
                "tokenizer": tokenizer,
                "model": model,
            }

        self.model_pool.register(
            alias=self.model_alias,
            loader=loader,
            instance_count=instance_count,
        )

    @torch.no_grad()
    def generate_structured_note(
        self,
        model_entry: ModelEntry,
        text_segment: str,
        language: Optional[str] = None,
    ) -> StructuredNoteResult:
        tokenizer = model_entry.model["tokenizer"]
        model = model_entry.model["model"]

        prompt = PROMPT_TEMPLATE.format(input_text=text_segment)

        logger.info(
            "structured generation start: model_instance=%s input_chars=%s preview=%r",
            model_entry.instance_id,
            len(text_segment),
            text_segment[:120],
        )

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=settings.note_max_length,
        )
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        gen_start = time.time()

        outputs = model.generate(
            **inputs,
            max_new_tokens=settings.note_max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

        gen_elapsed = time.time() - gen_start
        logger.info(
            "structured generation finished: model_instance=%s elapsed=%.2fs",
            model_entry.instance_id,
            gen_elapsed,
        )

        input_len = inputs["input_ids"].shape[1]
        new_tokens = outputs[0][input_len:]
        raw_output = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        parse_ok, obj = safe_json_parse(raw_output)
        field_ok = parse_ok and obj is not None and has_required_fields(obj)

        logger.info(
            "structured generation done: model_instance=%s raw_output_len=%s parse_ok=%s field_ok=%s",
            model_entry.instance_id,
            len(raw_output),
            parse_ok,
            field_ok,
        )
        logger.debug("structured raw output: %s", raw_output)

        if not parse_ok or obj is None:
            raise RuntimeError(f"structured note json parse failed; raw_output={raw_output}")

        if not has_required_fields(obj):
            raise RuntimeError(f"structured note missing required fields; parsed_obj={obj}")

        logger.info(
            "structured result summary_len=%s knowledge_points_count=%s",
            len(obj["summary"]),
            len(obj["knowledge_points"]),
        )

        return StructuredNoteResult(
            data={
                "summary": obj["summary"],
                "knowledge_points": obj["knowledge_points"],
            },
            raw_output=raw_output,
            parse_ok=parse_ok,
            field_ok=True,
            model_instance_id=model_entry.instance_id,
        )