# Web UI 目录 / Web UI Directory

## 📁 目录说明

本目录用于虚拟女友 Web 用户界面的开发。

This directory is for the Virtual Girlfriend Web User Interface development.

## 🌐 目录结构

```
web/
├── app.py                 # Flask/FastAPI 应用主文件
├── static/                # 静态资源
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript 文件
│   └── images/           # 图片资源
├── templates/             # HTML 模板
│   ├── index.html        # 主页
│   ├── chat.html         # 聊天界面
│   └── ...
└── README.md             # 本文件
```

## 🚀 功能规划

### Phase 1: 基础聊天界面
- [x] 项目结构搭建
- [ ] 简单的聊天界面
- [ ] 消息发送与接收
- [ ] 基本的 UI 样式

### Phase 2: 模型集成
- [ ] 集成 Qwen2.5 模型
- [ ] 实时对话生成
- [ ] 流式输出支持
- [ ] 上下文管理

### Phase 3: 高级功能
- [ ] 多轮对话记忆
- [ ] 个性化设置
- [ ] 情感分析展示
- [ ] 对话历史保存

### Phase 4: 优化增强
- [ ] 响应速度优化
- [ ] UI/UX 改进
- [ ] 移动端适配
- [ ] 多语言支持

## 🔧 技术栈

### 后端框架 (二选一)
- **Flask**: 轻量级，易于上手
- **FastAPI**: 高性能，支持异步

### 前端技术
- **HTML5/CSS3**: 基础页面结构和样式
- **JavaScript**: 交互逻辑
- **可选框架**: Vue.js / React

### 模型推理
- **Transformers**: Hugging Face 模型库
- **vLLM**: 高性能推理引擎 (可选)

## 📝 快速开始 (即将推出)

### 安装依赖
```bash
pip install flask flask-cors
# 或
pip install fastapi uvicorn
```

### 启动 Web 服务
```bash
# Flask 版本
python web/app.py

# FastAPI 版本
uvicorn web.app:app --reload --host 0.0.0.0 --port 5000
```

### 访问界面
打开浏览器访问: http://localhost:5000

## 🎨 UI 设计要求

1. **简洁清爽**: 采用现代化、简洁的设计风格
2. **聊天体验**: 参考微信、钉钉等即时通讯工具
3. **女友人设**: 
   - 温柔体贴的配色 (粉色、浅紫等)
   - 可爱的头像和表情
   - 俏皮的动画效果
4. **响应式设计**: 支持桌面端和移动端

## 📂 静态资源说明

### static/css/
- `main.css`: 主样式文件
- `chat.css`: 聊天界面样式
- `theme.css`: 主题配色

### static/js/
- `main.js`: 主 JavaScript 逻辑
- `chat.js`: 聊天功能实现
- `api.js`: API 调用封装

### static/images/
- `avatar/`: 虚拟女友头像
- `emoji/`: 自定义表情包
- `background/`: 背景图片

## 🔌 API 接口设计

### 1. 发送消息
```
POST /api/chat
Body: {"message": "你好呀"}
Response: {"reply": "你好呀亲爱的~😊"}
```

### 2. 获取历史记录
```
GET /api/history
Response: [{"role": "user", "content": "..."}, ...]
```

### 3. 清除历史
```
DELETE /api/history
Response: {"status": "ok"}
```

## 🛠️ 开发指南

### 1. 创建新页面
```python
# web/app.py
@app.route('/new_page')
def new_page():
    return render_template('new_page.html')
```

### 2. 添加 API 端点
```python
@app.route('/api/endpoint', methods=['POST'])
def api_endpoint():
    data = request.get_json()
    # 处理逻辑
    return jsonify(result)
```

### 3. 集成模型
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.config import MODELS_DIR, MODEL_NAME

model_path = MODELS_DIR / MODEL_NAME
model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
```

## 🔗 相关资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Transformers 文档](https://huggingface.co/docs/transformers)

## 📝 待办事项

- [ ] 创建 app.py 主文件
- [ ] 设计聊天界面 HTML/CSS
- [ ] 实现基础 API 接口
- [ ] 集成大模型推理
- [ ] 添加流式输出支持
- [ ] 前端交互优化
