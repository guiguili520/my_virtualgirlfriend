#!/usr/bin/env python3
"""
虚拟女友 Web 应用 (预留)
Virtual Girlfriend Web Application (placeholder)

基于 Flask 的 Web 用户界面
Flask-based Web User Interface
"""
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from config import WEB_HOST, WEB_PORT, DEBUG_MODE


if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def index():
        """主页"""
        return """
        <html>
        <head>
            <title>虚拟女友 - Virtual Girlfriend</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }
                h1 { color: #ff69b4; }
                .info { 
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <h1>💕 虚拟女友 Virtual Girlfriend 💕</h1>
            <div class="info">
                <h2>功能开发中...</h2>
                <p>Web UI 功能即将推出，敬请期待！</p>
                <p>Coming Soon...</p>
            </div>
            <div class="info">
                <h3>当前可用功能：</h3>
                <ul style="text-align: left;">
                    <li>数据集生成: <code>python scripts/generate_dataset.py</code></li>
                    <li>模型训练: <code>python scripts/lora_train.py</code></li>
                </ul>
            </div>
        </body>
        </html>
        """

    @app.route('/api/chat', methods=['POST'])
    def chat():
        """聊天 API (预留)"""
        data = request.get_json()
        message = data.get('message', '')
        
        # TODO: 集成模型推理
        reply = "功能开发中，敬请期待~ 😊"
        
        return jsonify({
            'reply': reply,
            'status': 'success'
        })


def main():
    """主函数"""
    if not FLASK_AVAILABLE:
        print("=" * 60)
        print("错误: 未安装 Flask")
        print("Error: Flask not installed")
        print("=" * 60)
        print()
        print("请安装依赖: pip install flask flask-cors")
        print("Please install dependencies: pip install flask flask-cors")
        print()
        return
    
    print("=" * 60)
    print("虚拟女友 Web 服务启动中...")
    print("Virtual Girlfriend Web Service Starting...")
    print("=" * 60)
    print()
    print(f"访问地址: http://localhost:{WEB_PORT}")
    print(f"Access URL: http://localhost:{WEB_PORT}")
    print()
    print("按 Ctrl+C 停止服务")
    print("Press Ctrl+C to stop")
    print()
    
    app.run(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE)


if __name__ == "__main__":
    main()
