"""
推理模块
Inference Module

提供完整的推理流水线，包括增强、模型调用和人格化处理
"""

from .pipeline import InferencePipeline, get_pipeline, run_chat

__all__ = [
    'InferencePipeline',
    'get_pipeline',
    'run_chat',
]
