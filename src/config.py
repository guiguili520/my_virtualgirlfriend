"""
虚拟女友项目配置文件
Configuration file for Virtual Girlfriend project
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
TRAIN_DATA_DIR = DATA_DIR / "train"
VALIDATION_DATA_DIR = DATA_DIR / "validation"

# 模型目录
MODELS_DIR = PROJECT_ROOT / "models"

# 默认数据集生成参数
DEFAULT_NUM_SAMPLES = 500
DEFAULT_VARIANTS_PER_SCENARIO = 8
DEFAULT_MIN_LENGTH = 15
DEFAULT_MAX_LENGTH = 200
DEFAULT_SIMILARITY_THRESHOLD = 0.90

# 模型配置
MODEL_NAME = "Qwen2.5-7B-Instruct"
LORA_NAME = "qwen-ai-girlfriend-lora"

# Web UI 配置
WEB_HOST = "0.0.0.0"
WEB_PORT = 5555
DEBUG_MODE = False

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 推理增强配置
# Inference Enhancement Configuration
ENABLE_ENHANCEMENT = True  # 全局开关
ENHANCEMENT_MIN_QUERY_LENGTH = 5  # 触发增强的最小查询长度
ENHANCEMENT_KEYWORDS = [
    "什么", "为什么", "怎么", "如何", "谁", "哪里", "哪个", "多少",
    "什么时候", "是否", "能不能", "可以吗", "告诉我", "查一下"
]  # 触发增强的关键词

# 网络搜索配置
ENABLE_NETWORK_SEARCH = True
SEARCH_MAX_RESULTS = 3
SEARCH_TIMEOUT = 5  # 秒

# MCP配置
ENABLE_MCP = True
MCP_TIMEOUT = 3  # 秒

# 增强模块配置
RANKING_TOP_K = 5  # 保留前K个结果
DEDUP_SIMILARITY_THRESHOLD = 0.85  # 去重相似度阈值
SUMMARY_MAX_LENGTH = 200  # 摘要最大长度
PERSONA_EMOJI_PROBABILITY = 0.8  # 表情符号出现概率
