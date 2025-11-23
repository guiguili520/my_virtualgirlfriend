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
WEB_PORT = 5000
DEBUG_MODE = False

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
