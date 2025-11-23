"""
虚拟女友 Web 应用配置文件
Virtual Girlfriend Web Application Configuration
"""
import os
from pathlib import Path

# Web 应用目录
WEB_ROOT = Path(__file__).parent.absolute()
PROJECT_ROOT = WEB_ROOT.parent

# 数据存储路径
DATA_DIR = WEB_ROOT / "data"
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"

# 上传文件配置
UPLOAD_DIR = WEB_ROOT / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Flask 配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'virtual-girlfriend-secret-key-2024')
MAX_CONTENT_LENGTH = MAX_FILE_SIZE

# 服务器配置
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5555))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# 聊天配置
MAX_HISTORY_SIZE = 1000  # 最多保存1000条聊天记录
MAX_MESSAGE_LENGTH = 500  # 单条消息最大长度

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
