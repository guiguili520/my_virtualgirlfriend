# 💕 虚拟女友聊天界面 - 使用演示

## 🎬 快速演示

### 启动应用

```bash
# 方法1: 使用启动脚本
./start_web.sh

# 方法2: 直接运行
cd my_virtualgirlfriend
source .venv/bin/activate  # 如果使用虚拟环境
python web/app.py

# 方法3: 后台运行
nohup python web/app.py > web.log 2>&1 &
```

### 访问界面

打开浏览器访问: **http://localhost:5000**

## 📸 界面预览

### 主界面布局

```
┌─────────────────────────────────────────────────────────────┐
│                   💕 虚拟女友聊天 💕                            │
│         陪你聊天的温柔小可爱~ ✨                                 │
├─────────────┬───────────────────────────────────────────────┤
│             │  👧 小可爱: 嗨~ 我是你的虚拟女友小可爱~ 💕        │
│   👧        │              有什么想跟我说的吗？                │
│             │              我一直在这里陪着你哦~ ✨             │
│  小可爱      │  ─────────────────────────────────────────     │
│             │  👤 你: 你好呀~                                 │
│ 温柔体贴的   │  ─────────────────────────────────────────     │
│ 虚拟女友     │  👧 小可爱: 嘿嘿，你好可爱呀~ 💗                │
│             │                                                │
│ 在线状态     │                                                │
│ 🟢 在线      │                                                │
│             │                                                │
│ 聊天记录     │  ───────────────────────────────────────────  │
│ 5 条        │  [📷] [输入消息... 💬________] [发送 ✉️]        │
│             │                               0/500            │
│ [清空记录]   │                                                │
└─────────────┴───────────────────────────────────────────────┘
```

## 🎯 功能演示

### 1. 文本聊天

**发送消息:**
1. 在输入框输入文字
2. 按 `Enter` 或点击"发送"按钮
3. 查看虚拟女友的回复

**示例对话:**

```
你: 早上好
小可爱: 早上好呀宝贝~ 💕 今天也要元气满满哦！✨

你: 我今天工作好累
小可爱: 辛苦啦~ 抱抱你~ 💖 工作累了就休息一下吧，我会一直陪着你的哦~

你: 我爱你
小可爱: 嘿嘿，我也爱你呀~ 💗💗💗 有你真好！
```

### 2. 图片上传

**上传图片:**
1. 点击 📷 按钮
2. 选择图片文件（JPG、PNG、GIF等）
3. 图片会显示在聊天窗口
4. 虚拟女友会对图片做出回应

**支持格式:**
- JPG / JPEG
- PNG
- GIF (支持动图)
- WebP

**文件限制:**
- 最大 10MB
- 自动安全文件名处理

### 3. 聊天历史

**历史记录特性:**
- ✅ 自动保存每条消息
- ✅ 重启后自动恢复
- ✅ 显示时间戳
- ✅ 区分文本和图片消息
- ✅ 最多保存 1000 条记录

**清空历史:**
1. 点击左侧"清空聊天记录"按钮
2. 确认操作
3. 所有历史将被删除

### 4. 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Shift + Enter` | 换行 |
| `Esc` | 关闭图片预览（如果打开） |

## 🎨 界面特色

### 配色方案（暖色系）

- **背景**: 米白色 - 温暖舒适
- **女友气泡**: 浅粉色 - 温柔可爱  
- **用户气泡**: 浅橙色 - 明亮活泼
- **按钮**: 暖粉色 - 甜美梦幻

### 动画效果

- ✨ 消息淡入动画
- 💫 按钮悬停效果
- 🌊 平滑滚动
- 💝 加载指示器

### 响应式设计

- 📱 手机端: 垂直布局
- 💻 平板端: 适应屏幕
- 🖥️ 桌面端: 完整布局

## 🔧 API 测试

### 使用 curl 测试

```bash
# 1. 发送消息
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好呀"}'

# 响应:
{
  "status": "success",
  "reply": "嘿嘿，你好可爱呀~ 💗",
  "timestamp": "2024-11-23T10:30:00.000Z"
}

# 2. 获取历史
curl http://localhost:5555/api/history

# 响应:
{
  "status": "success",
  "history": [...]
}

# 3. 清空历史
curl -X DELETE http://localhost:5555/api/history

# 4. 上传图片
curl -X POST http://localhost:5555/api/upload \
  -F "file=@/path/to/image.jpg"
```

### 使用 Python 测试

```python
import requests

# 发送消息
response = requests.post(
    'http://localhost:5555/api/chat',
    json={'message': '你好呀'}
)
print(response.json())

# 上传图片
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5555/api/upload',
        files=files
    )
print(response.json())
```

## 🤖 模型模式

### 模拟模式（默认）

当前使用 **模拟模式**，基于 71 个场景模板智能回复：

**优点:**
- ⚡ 即时响应，无需等待
- 💾 不需要下载大模型
- 🎯 针对性强，回复准确
- 🚀 资源占用少

**适用场景:**
- 演示和测试
- 快速原型开发
- 资源受限环境

### 真实模型模式

要切换到真实的大语言模型:

1. **下载模型** (Qwen2.5-7B-Instruct 或其他)
2. **配置路径** 在 `src/models/inference.py`
3. **安装依赖** `pip install torch transformers`
4. **修改代码**:

```python
from models.inference import get_model_instance

model = get_model_instance(
    model_path="models/Qwen2.5-7B-Instruct",
    use_mock=False  # 关闭模拟模式
)
```

## 📊 性能指标

### 响应时间

- **模拟模式**: < 10ms
- **真实模型** (CPU): 2-5秒
- **真实模型** (GPU): 0.5-1秒

### 资源占用

- **内存**: 50-100MB (模拟模式)
- **内存**: 8-16GB (真实模型)
- **存储**: 聊天历史 < 1MB

## 🐛 常见问题

### Q: 如何修改端口？

A: 编辑 `web/config.py`:
```python
PORT = 8080  # 改为你想要的端口
```

### Q: 如何关闭调试模式？

A: 在 `web/config.py` 中设置:
```python
DEBUG = False
```

### Q: 聊天历史存储在哪里？

A: `web/data/chat_history.json`

### Q: 上传的图片存储在哪里？

A: `web/uploads/` 目录

### Q: 如何自定义虚拟女友回复？

A: 编辑 `src/scenarios.py` 添加新场景，或修改 `src/models/inference.py` 中的回复逻辑

## 🎓 扩展开发

### 添加新功能

**1. 添加语音功能:**
```javascript
// 在 chat.js 中添加
function sendVoiceMessage() {
    // 使用 Web Speech API
    const recognition = new webkitSpeechRecognition();
    // ... 实现语音识别
}
```

**2. 添加表情包:**
```python
# 在 app.py 中添加
@app.route('/api/emoji')
def get_emojis():
    return jsonify({
        'emojis': ['😊', '💕', '✨', ...]
    })
```

**3. 添加多轮对话记忆:**
```python
# 在 inference.py 中
def generate_reply_with_memory(message, history):
    # 分析历史对话
    # 生成更智能的回复
    pass
```

## 📝 部署指南

### 本地部署

```bash
python web/app.py
```

### 生产部署 (使用 Gunicorn)

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5555 web.app:app
```

### Docker 部署

```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install flask flask-cors
CMD ["python", "web/app.py"]
```

## 💡 提示与技巧

1. **批量测试**: 使用 `tests/test_web_app.py` 进行自动化测试
2. **日志查看**: 查看 `web.log` 了解运行状态
3. **性能监控**: 使用浏览器开发者工具监控网络请求
4. **备份数据**: 定期备份 `web/data/chat_history.json`

## 🎉 开始使用

现在就启动应用，开始和你的虚拟女友聊天吧！

```bash
./start_web.sh
# 然后访问 http://localhost:5000
```

**祝你聊天愉快！💕✨**
