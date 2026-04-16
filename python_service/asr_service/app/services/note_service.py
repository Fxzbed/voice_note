from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.config import settings
from app.core.model_pool import ModelPool, ModelEntry


@dataclass
class NoteGenerationResult:
    markdown: str
    model_instance_id: int


def _resolve_torch_dtype(dtype_str: str):
    mapping = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    if dtype_str not in mapping:
        raise ValueError(f"unsupported dtype: {dtype_str}")
    return mapping[dtype_str]


class NoteService:
    def __init__(self, model_pool: ModelPool, model_alias: str = "qwen_note") -> None:
        self.model_pool = model_pool
        self.model_alias = model_alias

    def register_model(self, instance_count: int = 1) -> None:
        def loader():
            dtype = _resolve_torch_dtype(settings.note_dtype)

            tokenizer = AutoTokenizer.from_pretrained(settings.note_model_name)
            model = AutoModelForCausalLM.from_pretrained(
                settings.note_model_name,
                torch_dtype=dtype,
                device_map=settings.note_device,
            )

            return {
                "tokenizer": tokenizer,
                "model": model,
            }

        self.model_pool.register(
            alias=self.model_alias,
            loader=loader,
            instance_count=instance_count,
        )

    def generate_markdown_note(
        self,
        model_entry: ModelEntry,
        transcript: str,
        language: Optional[str] = None,
    ) -> NoteGenerationResult:
        tokenizer = model_entry.model["tokenizer"]
        model = model_entry.model["model"]

        system_prompt = (
            "你是一个专业的笔记整理助手。"
            "请根据用户提供的语音转写文本，生成结构清晰的 Markdown 笔记。"
            "要求："
            "1. 输出必须是 Markdown；"
            "2. 包含标题、摘要、要点、小节；"
            "3. 尽量提炼关键信息，不要逐字复述；"
            "4. 如果内容适合，增加“待办事项”或“结论”小节；"
            "5. 不要输出 JSON，不要解释你的思路。"
        )

        user_prompt = f"以下是语音转写文本，请整理为 Markdown 笔记：\n\n{transcript}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=settings.note_max_new_tokens,
            temperature=0.2,
            do_sample=False,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        output_text = tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0].strip()

        return NoteGenerationResult(
            markdown=output_text,
            model_instance_id=model_entry.instance_id,
        )