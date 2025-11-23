# 💕 虚拟女友聊天界面 Web 应用

## 📖 项目简介

这是一个基于 Flask + TailwindCSS 开发的虚拟女友聊天界面 Web 应用，提供二次元风格、可爱暖色系的聊天体验。支持文本聊天、图片上传、聊天历史持久化等功能。

Virtual Girlfriend Chat Web Application - A cute anime-style chat interface built with Flask and TailwindCSS.

## ✨ 主要功能

- ✅ **二次元风格聊天界面** - 可爱的暖色系设计（米白、浅粉、浅橙配色）
- ✅ **文本聊天** - 实时对话，支持 Enter 发送，Shift+Enter 换行
- ✅ **图片上传** - 支持 JPG、PNG、GIF 等格式，自动保存和显示
- ✅ **聊天历史持久化** - 自动保存到 JSON 文件，重启后可恢复
- ✅ **响应式设计** - 支持桌面和移动端自适应
- ✅ **大模型集成准备** - 提供模型推理接口，支持切换真实模型
- ✅ **模拟模式** - 基于场景库的智能回复（演示用）

## 🏗️ 项目结构

```
web/
├── app.py                      # Flask 应用主文件
├── config.py                   # 配置文件
├── templates/
│   └── index.html              # 聊天界面 HTML
├── static/
│   ├── css/
│   │   └── style.css           # TailwindCSS 样式
│   ├── js/
│   │   └── chat.js             # 聊天交互逻辑
│   └── images/                 # 虚拟女友头像等资源
├── uploads/                    # 用户上传的图片/表情包
├── data/
│   └── chat_history.json       # 聊天记录持久化
└── README.md                   # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install flask flask-cors werkzeug

# 或安装完整依赖
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 方式1: 直接运行
cd my_virtualgirlfriend
python web/app.py

# 方式2: 使用 Python 模块方式
python -m web.app

# 访问地址: http://localhost:5000
```

### 3. 环境变量（可选）

```bash
# 设置主机和端口
export HOST=0.0.0.0
export PORT=5000

# 开启调试模式
export DEBUG=true

# 自定义密钥
export SECRET_KEY=your-secret-key
```

## 🎨 界面设计

### 配色方案（暖色系）

- **背景色**: 米白色 `#FFFBF0`
- **虚拟女友气泡**: 浅粉色 `#FFE5E5`
- **用户气泡**: 浅橙色 `#FFF5E1`
- **重点色**: 暖粉色 `#FFB6C1`
- **辅助色**: 淡黄色 `#FFFACD`

### 布局结构

```
┌─────────────────────────────────────────────┐
│            💕 虚拟女友聊天 💕                  │
├──────────┬──────────────────────────────────┤
│          │  ┌────────────────────────────┐  │
│  虚拟    │  │                            │  │
│  女友    │  │      聊天消息区域            │  │
│  形象    │  │                            │  │
│  区域    │  └────────────────────────────┘  │
│          │  ┌────────────────────────────┐  │
│          │  │  [📷] [输入框...] [发送]   │  │
│          │  └────────────────────────────┘  │
└──────────┴──────────────────────────────────┘
```

## 🔌 API 接口

### 1. 发送文本消息

```http
POST /api/chat
Content-Type: application/json

{
  "message": "你好呀~"
}

Response:
{
  "status": "success",
  "reply": "嗨~ 你好呀亲爱的! 💕",
  "timestamp": "2024-11-23T10:30:00.000Z"
}
```

### 2. 上传图片

```http
POST /api/upload
Content-Type: multipart/form-data

file: [图片文件]

Response:
{
  "status": "success",
  "filename": "20241123_103000_image.jpg",
  "url": "/uploads/20241123_103000_image.jpg",
  "reply": "哇~ 这张图片好好看呀! ✨"
}
```

### 3. 获取聊天历史

```http
GET /api/history

Response:
{
  "status": "success",
  "history": [
    {
      "sender": "user",
      "type": "text",
      "content": "你好",
      "timestamp": "2024-11-23T10:00:00.000Z"
    },
    {
      "sender": "girlfriend",
      "type": "text",
      "content": "你好呀~ 💕",
      "timestamp": "2024-11-23T10:00:01.000Z"
    }
  ]
}
```

### 4. 清空聊天历史

```http
DELETE /api/history

Response:
{
  "status": "success",
  "message": "聊天记录已清空"
}
```

### 5. 获取上传的图片

```http
GET /uploads/{filename}

Response: 图片文件
```

## 🤖 模型集成

### 模拟模式（默认）

应用默认使用模拟模式，基于 71 个场景模板智能匹配回复，无需加载大模型。

### 真实模型模式

要使用真实的大语言模型，请按以下步骤操作：

1. **下载模型**

```bash
# 将模型放在 models/ 目录下
models/
└── Qwen2.5-7B-Instruct/
    ├── config.json
    ├── pytorch_model.bin
    └── ...
```

2. **修改推理配置**

编辑 `src/models/inference.py`，修改模型加载配置：

```python
# 在 app.py 或调用处设置
from models.inference import get_model_instance

model = get_model_instance(
    model_path="/path/to/your/model",
    use_mock=False  # 关闭模拟模式
)
```

3. **安装模型依赖**

```bash
pip install torch transformers accelerate
```

## ⚙️ 配置说明

主要配置项在 `web/config.py` 中：

```python
# 文件上传配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 聊天配置
MAX_HISTORY_SIZE = 1000  # 最多保存1000条记录
MAX_MESSAGE_LENGTH = 500  # 单条消息最大长度

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False
```

## 📱 功能特性

### 1. 聊天交互

- **Enter 发送**: 按 Enter 键发送消息
- **Shift+Enter 换行**: 支持多行文本输入
- **字符计数**: 实时显示输入字符数（0/500）
- **自动滚动**: 新消息自动滚动到可见区域
- **加载提示**: 等待回复时显示"小可爱正在输入中..."

### 2. 图片功能

- **点击上传**: 点击 📷 按钮选择图片
- **格式支持**: JPG、PNG、GIF、WebP
- **大小限制**: 最大 10MB
- **图片预览**: 点击图片查看大图
- **安全文件名**: 自动生成带时间戳的安全文件名

### 3. 历史记录

- **自动保存**: 每条消息自动保存到 JSON 文件
- **持久化存储**: 重启后自动恢复历史记录
- **消息类型**: 区分文本和图片消息
- **时间戳**: 记录每条消息的准确时间
- **容量限制**: 最多保存 1000 条消息

### 4. 用户体验

- **响应式设计**: 自适应桌面和移动设备
- **动画效果**: 消息淡入、按钮悬停等动画
- **消息计数**: 实时显示聊天记录数量
- **在线状态**: 显示虚拟女友在线状态
- **通知提示**: 操作成功/失败的友好提示

## 🧪 测试要求

### 功能测试

```bash
# 1. 启动应用
python web/app.py

# 2. 测试项目
- [ ] 访问 http://localhost:5000 正常加载
- [ ] 发送文本消息正常显示
- [ ] 收到虚拟女友回复
- [ ] 上传图片成功并显示
- [ ] 刷新页面后历史记录保留
- [ ] 清空历史记录功能正常
- [ ] 响应式布局在不同屏幕尺寸正常
```

### API 测试

```bash
# 使用 curl 测试 API

# 1. 发送消息
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好呀"}'

# 2. 获取历史
curl http://localhost:5000/api/history

# 3. 清空历史
curl -X DELETE http://localhost:5000/api/history

# 4. 上传图片
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/image.jpg"
```

## 📂 数据存储

### 聊天历史格式

聊天记录保存在 `web/data/chat_history.json`：

```json
[
  {
    "sender": "user",
    "type": "text",
    "content": "你好呀~",
    "timestamp": "2024-11-23T10:00:00.123Z"
  },
  {
    "sender": "girlfriend",
    "type": "text",
    "content": "嗨~ 你好呀亲爱的! 💕",
    "timestamp": "2024-11-23T10:00:01.456Z"
  },
  {
    "sender": "user",
    "type": "image",
    "content": "20241123_100500_photo.jpg",
    "timestamp": "2024-11-23T10:05:00.789Z"
  }
]
```

### 上传文件命名

上传的文件保存在 `web/uploads/`，文件名格式：

```
{timestamp}_{original_name}.{ext}
例如: 20241123_103000_avatar.png
```

## 🎯 技术栈

### 后端
- **Flask** - Web 框架
- **Flask-CORS** - 跨域支持
- **Werkzeug** - 文件上传处理

### 前端
- **HTML5** - 页面结构
- **TailwindCSS** - CSS 框架（CDN）
- **JavaScript (ES6)** - 交互逻辑
- **Fetch API** - HTTP 请求

### 模型推理
- **Transformers** - Hugging Face 模型库（可选）
- **PyTorch** - 深度学习框架（可选）
- **场景库** - 自研的 71 个场景模板系统

## 🔧 开发指南

### 添加新功能

1. **后端 API**：在 `web/app.py` 中添加路由
2. **前端 UI**：修改 `web/templates/index.html`
3. **样式**：在 `web/static/css/style.css` 中添加
4. **交互逻辑**：在 `web/static/js/chat.js` 中实现

### 自定义配置

修改 `web/config.py` 中的配置参数：

```python
# 例如: 修改最大消息长度
MAX_MESSAGE_LENGTH = 1000

# 修改历史记录容量
MAX_HISTORY_SIZE = 5000
```

### 更换虚拟女友头像

1. 将头像图片放在 `web/static/images/` 目录
2. 修改 `web/templates/index.html` 中的头像代码

## 📚 相关文档

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [TailwindCSS 文档](https://tailwindcss.com/)
- [项目主 README](../README.md)
- [模型推理接口](../src/models/inference.py)
- [场景库说明](../src/scenarios.py)

## 🐛 故障排除

### 问题1: Flask 未安装

```bash
错误: ModuleNotFoundError: No module named 'flask'
解决: pip install flask flask-cors
```

### 问题2: 端口被占用

```bash
错误: Address already in use
解决: 修改 web/config.py 中的 PORT 配置，或杀掉占用进程
```

### 问题3: 图片上传失败

```bash
错误: 不支持的文件类型
解决: 检查文件扩展名是否在 ALLOWED_EXTENSIONS 中
```

### 问题4: 聊天历史丢失

```bash
原因: web/data/chat_history.json 文件损坏
解决: 删除该文件，应用会自动创建新的
```

## 📝 更新日志

### v1.0.0 (2024-11-23)
- ✅ 完整的聊天界面实现
- ✅ 文本和图片消息支持
- ✅ 聊天历史持久化
- ✅ 响应式设计
- ✅ 模拟模式和真实模型支持
- ✅ 二次元可爱风格 UI

## 📄 许可证

本项目是虚拟女友项目的一部分，遵循项目整体许可证。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

---

**Enjoy chatting with your virtual girlfriend! 💕✨**
