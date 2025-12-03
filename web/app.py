#!/usr/bin/env python3
"""
虚拟女友 Web 应用
Virtual Girlfriend Web Application

基于 Flask 的聊天界面应用
"""
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

# 添加项目根目录到 Python 路径（必须最先添加）
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("错误: 未安装 Flask。请运行: pip install flask flask-cors")
    sys.exit(1)

# 导入 web 配置（使用相对路径导入避免冲突）
import importlib.util
web_config_path = Path(__file__).parent / "config.py"
spec = importlib.util.spec_from_file_location("web_config", web_config_path)
web_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web_config)

from src.inference.pipeline import run_chat


app = Flask(__name__)
app.config['SECRET_KEY'] = web_config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = web_config.MAX_CONTENT_LENGTH
CORS(app)

# 在应用启动时初始化推理流水线（加载本地大模型）
print("\n🚀 初始化虚拟女友推理流水线...\n")
print("💡 注意: 正在加载真实大模型，可能需要几分钟时间...\n")

# 初始化推理流水线
def initialize_inference_pipeline():
    """初始化推理流水线，支持自动降级"""
    try:
        from src.inference.pipeline import get_pipeline

        # 尝试加载真实模型
        print("   正在加载真实大模型...")
        pipeline = get_pipeline(use_mock_model=False)

        if pipeline.model.use_mock:
            print("   ⚠️  模型加载失败，已自动降级到模拟模式")
            print("   模型文件提示: 请确保 ./models 目录存在且包含模型文件")
        else:
            print("   ✅ 真实大模型加载成功！")

        return pipeline
    except Exception as e:
        print(f"   ❌ 推理流水线初始化失败: {e}")
        print("   💡 错误详情: 请检查模型文件或系统环境")
        raise

# 应用启动时初始化
try:
    pipeline = initialize_inference_pipeline()
    print("   ✅ Web应用初始化完成，可以开始聊天了！\n")
except Exception as e:
    print(f"   ❌ 应用启动失败: {e}\n")
    raise


def load_chat_history():
    """加载聊天历史"""
    if web_config.CHAT_HISTORY_FILE.exists():
        try:
            with open(web_config.CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载聊天历史失败: {e}")
            return []
    return []


def save_chat_history(history):
    """保存聊天历史"""
    try:
        # 限制历史记录数量
        if len(history) > web_config.MAX_HISTORY_SIZE:
            history = history[-web_config.MAX_HISTORY_SIZE:]
        
        with open(web_config.CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存聊天历史失败: {e}")


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in web_config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页 - 聊天界面"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天 API - 发送消息并获取回复"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': '消息不能为空'
            }), 400
        
        if len(user_message) > web_config.MAX_MESSAGE_LENGTH:
            return jsonify({
                'status': 'error',
                'message': f'消息长度不能超过{web_config.MAX_MESSAGE_LENGTH}字符'
            }), 400
        
        # 加载聊天历史作为上下文
        history = load_chat_history()
        context = [
            {'role': msg['sender'], 'content': msg['content']}
            for msg in history[-10:]  # 最近10条作为上下文
            if msg['type'] == 'text'
        ]
        
        # 使用推理流水线生成回复（支持MCP和联网搜索）
        result = run_chat(
            user_message,
            history=context,
            opts={"enable_enhancement": True}
        )
        girlfriend_reply = result["response"]
        
        # 保存到历史记录
        timestamp = datetime.now().isoformat()
        
        # 用户消息
        user_msg = {
            'sender': 'user',
            'type': 'text',
            'content': user_message,
            'timestamp': timestamp
        }
        
        # 女友回复
        girlfriend_msg = {
            'sender': 'girlfriend',
            'type': 'text',
            'content': girlfriend_reply,
            'timestamp': datetime.now().isoformat()
        }
        
        history.append(user_msg)
        history.append(girlfriend_msg)
        save_chat_history(history)
        
        return jsonify({
            'status': 'success',
            'reply': girlfriend_reply,
            'timestamp': girlfriend_msg['timestamp']
        })
        
    except Exception as e:
        print(f"聊天处理失败: {e}")
        return jsonify({
            'status': 'error',
            'message': '处理消息时出错，请稍后重试'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图片 API"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '没有文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '未选择文件'
            }), 400
        
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            new_filename = f"{timestamp}_{name}{ext}"
            
            # 保存文件
            filepath = web_config.UPLOAD_DIR / new_filename
            file.save(str(filepath))
            
            # 保存到聊天历史
            history = load_chat_history()
            image_msg = {
                'sender': 'user',
                'type': 'image',
                'content': new_filename,
                'timestamp': datetime.now().isoformat()
            }
            history.append(image_msg)
            
            # 使用推理流水线生成回复
            result = run_chat("发送了一张图片", opts={"enable_enhancement": False})
            girlfriend_reply = result["response"]
            girlfriend_msg = {
                'sender': 'girlfriend',
                'type': 'text',
                'content': girlfriend_reply,
                'timestamp': datetime.now().isoformat()
            }
            history.append(girlfriend_msg)
            
            save_chat_history(history)
            
            return jsonify({
                'status': 'success',
                'filename': new_filename,
                'url': f'/uploads/{new_filename}',
                'reply': girlfriend_reply
            })
        
        return jsonify({
            'status': 'error',
            'message': '不支持的文件类型'
        }), 400
        
    except Exception as e:
        print(f"文件上传失败: {e}")
        return jsonify({
            'status': 'error',
            'message': '上传失败，请稍后重试'
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取聊天历史 API"""
    try:
        history = load_chat_history()
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        print(f"获取历史记录失败: {e}")
        return jsonify({
            'status': 'error',
            'message': '获取历史记录失败'
        }), 500


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """清空聊天历史 API"""
    try:
        save_chat_history([])
        return jsonify({
            'status': 'success',
            'message': '聊天记录已清空'
        })
    except Exception as e:
        print(f"清空历史记录失败: {e}")
        return jsonify({
            'status': 'error',
            'message': '清空失败'
        }), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(web_config.UPLOAD_DIR, filename)


def main():
    """主函数"""
    print("=" * 60)
    print("💕 虚拟女友 Web 服务启动中...")
    print("💕 Virtual Girlfriend Web Service Starting...")
    print("=" * 60)
    print()
    print(f"🌐 访问地址: http://localhost:{web_config.PORT}")
    print(f"🌐 Access URL: http://localhost:{web_config.PORT}")
    print()
    print("✨ 功能特性:")
    print("   • 本地大模型推理 (Qwen2.5-7B)")
    print("   • MCP服务集成 (天气、新闻、知识)")
    print("   • 联网搜索增强")
    print("   • 智能对话历史")
    print()
    print("🛑 按 Ctrl+C 停止服务")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host=web_config.HOST, port=web_config.PORT, debug=web_config.DEBUG)


if __name__ == "__main__":
    main()
