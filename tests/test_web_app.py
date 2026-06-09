#!/usr/bin/env python3
"""
虚拟女友 Web 应用测试
Test Virtual Girlfriend Web Application
"""
import sys
import json
import importlib.util
from pathlib import Path

# 添加必要路径
PROJECT_ROOT = Path(__file__).parent.parent
WEB_ROOT = PROJECT_ROOT / "web"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(WEB_ROOT))


def load_web_config():
    """按文件路径加载 web/config.py，避免和 src/config.py 混淆"""
    spec = importlib.util.spec_from_file_location("test_web_config", WEB_ROOT / "config.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_web_app():
    """按文件路径加载 web/app.py，避免受 sys.path 中 app/config 名称影响"""
    module_name = "test_web_runtime_app"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, WEB_ROOT / "app.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# 测试模块导入
def test_imports():
    """测试所有必要的模块可以正常导入"""
    try:
        web_config = load_web_config()
        from src.models.inference import generate_girlfriend_reply
        from flask import Flask
        assert hasattr(web_config, 'SECRET_KEY')
        print("✓ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False


def test_config():
    """测试配置文件"""
    web_config = load_web_config()
    
    assert hasattr(web_config, 'SECRET_KEY'), "配置中缺少 SECRET_KEY"
    assert hasattr(web_config, 'MAX_FILE_SIZE'), "配置中缺少 MAX_FILE_SIZE"
    assert hasattr(web_config, 'UPLOAD_DIR'), "配置中缺少 UPLOAD_DIR"
    assert hasattr(web_config, 'CHAT_HISTORY_FILE'), "配置中缺少 CHAT_HISTORY_FILE"
    assert hasattr(web_config, 'MODEL_CONFIG_FILE'), "配置中缺少 MODEL_CONFIG_FILE"
    
    print("✓ 配置文件测试通过")


def test_model_inference():
    """测试模型推理功能"""
    from src.models.inference import generate_girlfriend_reply
    
    # 测试基本回复
    reply = generate_girlfriend_reply("你好")
    assert isinstance(reply, str), "回复应该是字符串"
    assert len(reply) > 0, "回复不应为空"
    
    # 测试多个消息
    messages = ["早上好", "我好累", "我爱你"]
    for msg in messages:
        reply = generate_girlfriend_reply(msg)
        assert isinstance(reply, str), f"'{msg}' 的回复应该是字符串"
        assert len(reply) > 0, f"'{msg}' 的回复不应为空"
    
    print("✓ 模型推理测试通过")


def test_flask_app():
    """测试Flask应用"""
    try:
        from flask import Flask
        web_config = load_web_config()
        
        # 创建测试app
        app = Flask(__name__)
        app.config['SECRET_KEY'] = web_config.SECRET_KEY
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # 测试主页（注意：这里只是创建了app，没有路由）
            print("✓ Flask应用创建成功")
            
    except Exception as e:
        print(f"✗ Flask应用测试失败: {e}")
        raise


def test_model_provider_presets():
    """测试2.0模型供应商预设"""
    from src.models.inference import get_provider_presets

    providers = {item["key"]: item for item in get_provider_presets()}
    for key in ["openai", "anthropic", "deepseek", "glm", "kimi"]:
        assert key in providers, f"缺少模型供应商: {key}"

    assert providers["openai"]["api_format"] == "openai"
    assert providers["anthropic"]["api_format"] == "anthropic"
    print("✓ 2.0模型供应商预设测试通过")


def test_directory_structure():
    """测试目录结构"""
    project_root = PROJECT_ROOT
    web_root = WEB_ROOT
    
    # 检查必要的目录
    required_dirs = [
        web_root / "templates",
        web_root / "static" / "css",
        web_root / "static" / "js",
        web_root / "static" / "images",
        web_root / "uploads",
        web_root / "data",
        project_root / "src" / "models",
    ]
    
    for dir_path in required_dirs:
        assert dir_path.exists(), f"目录不存在: {dir_path}"
    
    # 检查必要的文件
    required_files = [
        web_root / "app.py",
        web_root / "config.py",
        web_root / "templates" / "index.html",
        web_root / "static" / "css" / "style.css",
        web_root / "static" / "js" / "chat.js",
        project_root / "src" / "models" / "inference.py",
        project_root / "src" / "models" / "__init__.py",
    ]
    
    for file_path in required_files:
        assert file_path.exists(), f"文件不存在: {file_path}"
    
    print("✓ 目录结构测试通过")


def test_chat_history_operations():
    """测试聊天历史操作"""
    import json
    import os

    web_config = load_web_config()
    
    # 确保目录存在
    web_config.DATA_DIR.mkdir(exist_ok=True)
    
    # 测试数据
    test_history = [
        {
            "sender": "user",
            "type": "text",
            "content": "测试消息",
            "timestamp": "2024-11-23T10:00:00.000Z"
        },
        {
            "sender": "girlfriend",
            "type": "text",
            "content": "测试回复",
            "timestamp": "2024-11-23T10:00:01.000Z"
        }
    ]
    
    # 写入测试数据
    test_file = web_config.DATA_DIR / "test_history.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_history, f, ensure_ascii=False, indent=2)
    
    # 读取并验证
    with open(test_file, 'r', encoding='utf-8') as f:
        loaded_history = json.load(f)
    
    assert len(loaded_history) == 2, "历史记录数量不正确"
    assert loaded_history[0]['sender'] == 'user', "发送者不正确"
    
    # 清理测试文件
    os.remove(test_file)
    
    print("✓ 聊天历史操作测试通过")


def test_model_config_api_masks_and_clears_key(tmp_path, monkeypatch):
    """测试模型配置接口保存Key但不回显明文"""
    web_app = load_web_app()

    config_file = tmp_path / "model_config.json"
    monkeypatch.setattr(web_app.web_config, "MODEL_CONFIG_FILE", config_file)
    web_app.app.config["TESTING"] = True

    with web_app.app.test_client() as client:
        response = client.post('/api/model/config', json={
            "provider": "kimi",
            "api_format": "openai",
            "model": "kimi-k2.6",
            "base_url": "https://api.moonshot.cn/v1",
            "api_key": "local-secret-key",
        })
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["status"] == "success"
        assert payload["config"]["key_configured"] is True
        assert "local-secret-key" not in response.get_data(as_text=True)

        saved = json.loads(config_file.read_text(encoding='utf-8'))
        assert saved["api_key"] == "local-secret-key"

        get_response = client.get('/api/model/config')
        assert get_response.status_code == 200
        assert "local-secret-key" not in get_response.get_data(as_text=True)
        assert get_response.get_json()["config"]["key_configured"] is True

        providers_response = client.get('/api/model/providers')
        providers = {
            item["key"]: item
            for item in providers_response.get_json()["providers"]
        }
        assert providers["kimi"]["configured"] is True

        opts = web_app.build_model_opts({"provider": "kimi"})
        assert opts["api_key"] == "local-secret-key"
        assert "api_key" not in web_app.build_model_opts({"provider": "openai"})

        clear_response = client.post('/api/model/config', json={
            "provider": "kimi",
            "api_format": "openai",
            "model": "kimi-k2.6",
            "base_url": "https://api.moonshot.cn/v1",
            "clear_api_key": True,
        })
        assert clear_response.status_code == 200
        assert clear_response.get_json()["config"]["key_configured"] is False
        assert "api_key" not in json.loads(config_file.read_text(encoding='utf-8'))

    print("✓ 模型配置接口脱敏与清除测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("虚拟女友 Web 应用测试")
    print("Virtual Girlfriend Web Application Tests")
    print("=" * 60)
    print()
    
    try:
        print("1. 测试模块导入...")
        test_imports()
        print()
        
        print("2. 测试配置文件...")
        test_config()
        print()
        
        print("3. 测试模型推理...")
        test_model_inference()
        print()
        
        print("4. 测试Flask应用...")
        test_flask_app()
        print()
        
        print("5. 测试目录结构...")
        test_directory_structure()
        print()
        
        print("6. 测试聊天历史操作...")
        test_chat_history_operations()
        print()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        sys.exit(1)
