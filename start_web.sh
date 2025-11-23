#!/bin/bash
# 虚拟女友 Web 应用启动脚本
# Virtual Girlfriend Web Application Start Script

echo "=========================================="
echo "💕 虚拟女友 Web 应用启动"
echo "💕 Virtual Girlfriend Web App"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    uv venv
    echo "✓ 虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 检查依赖
echo "检查依赖..."
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask未安装，正在安装依赖..."
    uv pip install flask flask-cors werkzeug
    echo "✓ 依赖安装完成"
    echo ""
fi

echo ""
echo "🚀 启动 Web 应用..."
echo ""

# 启动应用
python web/app.py
