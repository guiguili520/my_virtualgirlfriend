"""
虚拟女友项目配置文件
Configuration file for Virtual Girlfriend project
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 应用版本
APP_VERSION = "2.0.0"

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

# 模型配置（2.0：在线模型 API）
# 可选供应商：mock, openai, anthropic, deepseek, deepseek-anthropic, glm, kimi,
# custom-openai, custom-anthropic
DEFAULT_MODEL_PROVIDER = os.getenv("VG_MODEL_PROVIDER", "mock")
DEFAULT_MODEL_API_FORMAT = os.getenv("VG_MODEL_API_FORMAT", "")
DEFAULT_MODEL_NAME = os.getenv("VG_MODEL_NAME", "")
DEFAULT_MODEL_BASE_URL = os.getenv("VG_MODEL_BASE_URL", "")
MODEL_NAME = DEFAULT_MODEL_NAME or "online-api"
LORA_NAME = "deprecated-local-lora"

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
ENHANCEMENT_MIN_QUERY_LENGTH = 4  # 触发增强的最小查询长度
ENHANCEMENT_KEYWORDS = [
    # 疑问词
    "什么", "为什么", "怎么", "如何", "谁", "哪里", "哪个", "多少",
    "什么时候", "是否", "能不能", "可以吗", "告诉我", "查一下",
    # 天气相关
    "天气", "气温", "温度", "下雨", "下雪", "预报",
    # 新闻相关
    "新闻", "头条", "热点"
]  # 触发增强的关键词

# 网络搜索配置
ENABLE_NETWORK_SEARCH = True
SEARCH_MAX_RESULTS = 3
SEARCH_TIMEOUT = 5  # 秒

# MCP配置
ENABLE_MCP = True
MCP_TIMEOUT = 3  # 秒

# 模型工具调用配置（默认关闭，避免普通聊天启动时初始化外部MCP工具）
ENABLE_MODEL_TOOL_CALLS = os.getenv("ENABLE_MODEL_TOOL_CALLS", "false").lower() == "true"

# 增强模块配置
RANKING_TOP_K = 5  # 保留前K个结果
DEDUP_SIMILARITY_THRESHOLD = 0.85  # 去重相似度阈值
SUMMARY_MAX_LENGTH = 500  # 摘要最大长度
PERSONA_EMOJI_PROBABILITY = 0.8  # 表情符号出现概率
