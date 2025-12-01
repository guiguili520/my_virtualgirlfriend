#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型推理接口
Model inference interface

- 支持 CPU/MPS 推理
- 在服务启动时初始化模型（单例）
- 当 ./models 目录不存在或为空时，自动降级为模拟模式
"""
import os
import torch
from pathlib import Path
from typing import Optional, List, Dict, Any

_MODEL_SINGLETON = None
_MODELS_DIR = Path(__file__).parent.parent.parent / "models"


def _has_models() -> bool:
    try:
        return _MODELS_DIR.exists() and any(_MODELS_DIR.iterdir())
    except Exception:
        return False


class GirlfriendChatModel:
    """聊天模型封装，提供 generate_reply"""
    def __init__(self, model_path: Optional[str] = None, use_mock: bool = True):
        self.model_path = Path(model_path) if model_path else _MODELS_DIR
        self.use_mock = use_mock or (not _has_models())
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"

        # 初始化真实模型
        self.model = None
        self.tokenizer = None

        if not self.use_mock:
            self._load_model()

    def _load_model(self):
        """加载真实模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            print(f"⏳ 正在加载模型到 {self.device.upper()}...")

            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                str(self.model_path),
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            ).to(self.device)

            print(f"✅ 模型加载完成！设备: {self.device}")

        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("⚠️  切换到模拟模式")
            self.use_mock = True

    def generate_reply(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """生成回复"""
        if self.use_mock:
            # 模拟模式
            base = "嗯嗯~ " if "~" not in prompt else ""
            return f"{base}{prompt} 我会一直陪着你的呀！💕"
        else:
            # 真实模型推理
            return self._generate_with_model(prompt, context)

    def _generate_with_model(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """使用真实模型生成回复"""
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": "你是一个温柔体贴、俏皮可爱的AI女友。"},
                {"role": "user", "content": prompt}
            ]

            # 应用对话模板
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # 编码并移动到设备
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

            # 生成回复
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.85,
                    top_k=20,
                    repetition_penalty=1.15,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # 解码
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            return response.strip()

        except Exception as e:
            print(f"❌ 模型推理失败: {e}")
            return "抱歉呀，我刚才走神了~ 能再说一遍吗？😊"


def init_model(model_path: Optional[str] = None, use_mock: Optional[bool] = None) -> None:
    """在应用启动时初始化全局模型实例（单例）"""
    global _MODEL_SINGLETON
    if _MODEL_SINGLETON is not None:
        return
    if use_mock is None:
        use_mock = not _has_models()
    _MODEL_SINGLETON = GirlfriendChatModel(model_path=model_path, use_mock=use_mock)


def generate_girlfriend_reply(text: str, context: Optional[List[Dict[str, str]]] = None) -> str:
    """使用全局模型实例生成回复，若未初始化则自动初始化（并按规范降级）"""
    global _MODEL_SINGLETON
    if _MODEL_SINGLETON is None:
        init_model(model_path=str(_MODELS_DIR))
    assert _MODEL_SINGLETON is not None
    return _MODEL_SINGLETON.generate_reply(text, context)
