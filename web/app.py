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

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 添加 web 目录到 Python 路径（优先）
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("错误: 未安装 Flask。请运行: pip install flask flask-cors")
    sys.exit(1)

import config as web_config
from models.inference import generate_girlfriend_reply


app = Flask(__name__)
app.config['SECRET_KEY'] = web_config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = web_config.MAX_CONTENT_LENGTH
CORS(app)


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
        
        # 生成虚拟女友的回复
        girlfriend_reply = generate_girlfriend_reply(user_message, context)
        
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
            
            # 生成女友的回复
            girlfriend_reply = generate_girlfriend_reply("发送了一张图片")
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
    print("⚠️  当前使用模拟模式（Mock Mode）")
    print("   如需使用真实模型，请在 src/models/inference.py 中配置模型路径")
    print()
    print("🛑 按 Ctrl+C 停止服务")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host=web_config.HOST, port=web_config.PORT, debug=web_config.DEBUG)


if __name__ == "__main__":
    main()
