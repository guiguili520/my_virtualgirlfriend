#!/bin/bash
# 虚拟女友 Flask Web 应用验收测试
# Acceptance Test for Virtual Girlfriend Flask Web Application

echo "=========================================="
echo "🧪 虚拟女友 Web 应用验收测试"
echo "🧪 Virtual Girlfriend Web App Acceptance Test"
echo "=========================================="
echo ""

PASS=0
FAIL=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_item() {
    local name=$1
    local result=$2
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $name"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}✗${NC} $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "1. 文件和目录结构检查"
echo "----------------------------"

# 检查主要文件
test_item "Flask应用文件 (web/app.py)" "$([ -f web/app.py ] && echo 0 || echo 1)"
test_item "配置文件 (web/config.py)" "$([ -f web/config.py ] && echo 0 || echo 1)"
test_item "HTML模板 (web/templates/index.html)" "$([ -f web/templates/index.html ] && echo 0 || echo 1)"
test_item "CSS样式 (web/static/css/style.css)" "$([ -f web/static/css/style.css ] && echo 0 || echo 1)"
test_item "JavaScript (web/static/js/chat.js)" "$([ -f web/static/js/chat.js ] && echo 0 || echo 1)"
test_item "模型推理 (src/models/inference.py)" "$([ -f src/models/inference.py ] && echo 0 || echo 1)"
test_item "启动脚本 (start_web.sh)" "$([ -f start_web.sh ] && [ -x start_web.sh ] && echo 0 || echo 1)"

# 检查目录
test_item "上传目录 (web/uploads/)" "$([ -d web/uploads ] && echo 0 || echo 1)"
test_item "数据目录 (web/data/)" "$([ -d web/data ] && echo 0 || echo 1)"
test_item "静态资源目录 (web/static/images/)" "$([ -d web/static/images ] && echo 0 || echo 1)"

echo ""
echo "2. 文档检查"
echo "----------------------------"

test_item "Web应用文档 (web/README.md)" "$([ -f web/README.md ] && [ $(wc -l < web/README.md) -gt 100 ] && echo 0 || echo 1)"
test_item "演示文档 (web/DEMO.md)" "$([ -f web/DEMO.md ] && [ $(wc -l < web/DEMO.md) -gt 50 ] && echo 0 || echo 1)"
test_item "实施总结 (IMPLEMENTATION_SUMMARY.md)" "$([ -f IMPLEMENTATION_SUMMARY.md ] && echo 0 || echo 1)"
test_item "主README更新" "$(grep -q 'Web聊天界面' README.md && echo 0 || echo 1)"

echo ""
echo "3. 代码质量检查"
echo "----------------------------"

# 检查Python文件语法
python -m py_compile web/app.py 2>/dev/null
test_item "app.py 语法检查" "$?"

python -m py_compile web/config.py 2>/dev/null
test_item "config.py 语法检查" "$?"

python -m py_compile src/models/inference.py 2>/dev/null
test_item "inference.py 语法检查" "$?"

# 检查文件大小（确保不是空文件）
test_item "app.py 内容完整 (>5KB)" "$([ $(stat -f%z web/app.py 2>/dev/null || stat -c%s web/app.py) -gt 5000 ] && echo 0 || echo 1)"
test_item "style.css 内容完整 (>3KB)" "$([ $(stat -f%z web/static/css/style.css 2>/dev/null || stat -c%s web/static/css/style.css) -gt 3000 ] && echo 0 || echo 1)"
test_item "chat.js 内容完整 (>10KB)" "$([ $(stat -f%z web/static/js/chat.js 2>/dev/null || stat -c%s web/static/js/chat.js) -gt 10000 ] && echo 0 || echo 1)"

echo ""
echo "4. 功能测试"
echo "----------------------------"

# 测试Python模块导入
python -c "import sys; sys.path.insert(0, 'web'); import config" 2>/dev/null
test_item "配置模块导入" "$?"

python -c "import sys; sys.path.insert(0, 'src'); from models.inference import generate_girlfriend_reply" 2>/dev/null
test_item "推理模块导入" "$?"

# 测试模型推理功能
REPLY=$(python -c "import sys; sys.path.insert(0, 'src'); from models.inference import generate_girlfriend_reply; print(generate_girlfriend_reply('你好'))" 2>/dev/null)
test_item "模型推理功能" "$([ -n "$REPLY" ] && echo 0 || echo 1)"

echo ""
echo "5. 依赖检查"
echo "----------------------------"

# 检查requirements.txt
test_item "requirements.txt 包含 flask" "$(grep -q 'flask' requirements.txt && echo 0 || echo 1)"
test_item "requirements.txt 包含 flask-cors" "$(grep -q 'flask-cors' requirements.txt && echo 0 || echo 1)"
test_item "requirements.txt 包含 werkzeug" "$(grep -q 'werkzeug' requirements.txt && echo 0 || echo 1)"

echo ""
echo "6. .gitignore 配置检查"
echo "----------------------------"

test_item ".gitignore 忽略上传文件" "$(grep -q 'web/uploads/\*' .gitignore && echo 0 || echo 1)"
test_item ".gitignore 忽略聊天历史" "$(grep -q 'chat_history.json' .gitignore && echo 0 || echo 1)"

echo ""
echo "=========================================="
echo "📊 测试结果统计"
echo "=========================================="
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${RED}失败: $FAIL${NC}"
echo "总计: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有验收测试通过！${NC}"
    echo -e "${GREEN}✅ All acceptance tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAIL 项测试失败${NC}"
    echo -e "${RED}❌ $FAIL test(s) failed${NC}"
    exit 1
fi
