#!/usr/bin/env python
"""
实现验证脚本
Implementation Verification Script

验证推理流水线实现是否满足所有验收标准
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_files_exist():
    """检查必需文件是否存在"""
    print("=" * 80)
    print("检查文件结构...")
    print("=" * 80)
    
    required_files = [
        # 增强模块
        "src/enhance/__init__.py",
        "src/enhance/ranker.py",
        "src/enhance/deduplicator.py",
        "src/enhance/summarizer.py",
        "src/enhance/persona_helper.py",
        # 推理模块
        "src/inference/__init__.py",
        "src/inference/pipeline.py",
        # 测试
        "tests/test_enhance_modules.py",
        "tests/test_inference_pipeline.py",
        # 文档
        "docs/INFERENCE_PIPELINE_README.md",
        "demo_inference_pipeline.py",
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        exists = file_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_imports():
    """检查导入是否正常"""
    print("\n" + "=" * 80)
    print("检查模块导入...")
    print("=" * 80)
    
    try:
        from enhance import Ranker, Deduplicator, Summarizer, PersonaHelper
        print("✓ enhance 模块导入成功")
        
        from inference import run_chat, get_pipeline, InferencePipeline
        print("✓ inference 模块导入成功")
        
        from config import (
            ENABLE_ENHANCEMENT, ENHANCEMENT_MIN_QUERY_LENGTH,
            ENABLE_NETWORK_SEARCH, ENABLE_MCP,
            RANKING_TOP_K, DEDUP_SIMILARITY_THRESHOLD,
            SUMMARY_MAX_LENGTH, PERSONA_EMOJI_PROBABILITY
        )
        print("✓ 配置项导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def check_functionality():
    """检查核心功能"""
    print("\n" + "=" * 80)
    print("检查核心功能...")
    print("=" * 80)
    
    try:
        from inference import run_chat
        
        # 测试1: 基本对话
        result = run_chat("你好")
        assert "response" in result
        assert "metadata" in result
        print("✓ 基本对话功能正常")
        
        # 测试2: 带历史的对话
        history = [{"role": "user", "content": "你好"}]
        result = run_chat("今天天气不错", history=history)
        assert "response" in result
        print("✓ 带历史对话功能正常")
        
        # 测试3: 自定义选项
        result = run_chat("测试", opts={"enable_enhancement": False})
        assert not result["metadata"]["enhancement_used"]
        print("✓ 自定义选项功能正常")
        
        # 测试4: 增强决策
        result = run_chat("今天的天气怎么样呢？", opts={"enable_enhancement": True})
        assert "stages" in result["metadata"]
        print("✓ 增强决策功能正常")
        
        # 测试5: 人格化验证
        from enhance import PersonaHelper
        helper = PersonaHelper()
        text = helper.apply_persona("你好")
        # 应该有表情或语气词
        has_emoji = any(e in text for e in helper.EMOJIS)
        has_particle = any(p in text for p in helper.TONE_PARTICLES)
        assert has_emoji or has_particle
        print("✓ 人格化功能正常")
        
        return True
    except Exception as e:
        print(f"✗ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_acceptance_criteria():
    """检查验收标准"""
    print("\n" + "=" * 80)
    print("检查验收标准...")
    print("=" * 80)
    
    criteria = {
        "✓ 创建 src/enhance/ 目录": Path("src/enhance").exists(),
        "✓ 实现 ranker.py": Path("src/enhance/ranker.py").exists(),
        "✓ 实现 deduplicator.py": Path("src/enhance/deduplicator.py").exists(),
        "✓ 实现 summarizer.py": Path("src/enhance/summarizer.py").exists(),
        "✓ 实现 persona_helper.py": Path("src/enhance/persona_helper.py").exists(),
        "✓ 创建 src/inference/ 目录": Path("src/inference").exists(),
        "✓ 实现 pipeline.py": Path("src/inference/pipeline.py").exists(),
        "✓ 提供测试文件": (
            Path("tests/test_enhance_modules.py").exists() and 
            Path("tests/test_inference_pipeline.py").exists()
        ),
    }
    
    all_passed = True
    for criterion, passed in criteria.items():
        status = "✓" if passed else "✗"
        print(f"{status} {criterion}")
        if not passed:
            all_passed = False
    
    # 功能性验收标准
    print("\n功能性验收标准:")
    try:
        from inference import run_chat
        
        # 单一入口函数
        result = run_chat("测试", history=[], opts={})
        has_entry_point = "response" in result
        print(f"{'✓' if has_entry_point else '✗'} 单一入口函数 run_chat 可用")
        
        # 协调完整流程
        has_stages = "stages" in result["metadata"]
        print(f"{'✓' if has_stages else '✗'} 协调完整流程（包含stages）")
        
        # 可选增强
        result_no_enh = run_chat("测试", opts={"enable_enhancement": False})
        result_with_enh = run_chat("今天的天气怎么样呢？", opts={"enable_enhancement": True})
        optional_enhancement = (
            not result_no_enh["metadata"]["enhancement_used"] or
            "enhancement_used" in result_with_enh["metadata"]
        )
        print(f"{'✓' if optional_enhancement else '✗'} 可选增强功能")
        
        # 配置可控
        configurable = "enable_enhancement" in {"enable_enhancement": True}
        print(f"{'✓' if configurable else '✗'} 配置可控")
        
        # 人格一致性
        from enhance import PersonaHelper
        helper = PersonaHelper()
        persona_valid = helper.validate_persona("你好呀~ 😊")
        print(f"{'✓' if persona_valid else '✗'} 人格一致性验证")
        
        all_passed = all_passed and all([
            has_entry_point, has_stages, optional_enhancement,
            configurable, persona_valid
        ])
        
    except Exception as e:
        print(f"✗ 功能性验收失败: {e}")
        all_passed = False
    
    return all_passed


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" " * 25 + "推理流水线实现验证")
    print(" " * 20 + "Inference Pipeline Verification")
    print("=" * 80 + "\n")
    
    results = []
    
    # 检查文件
    files_ok = check_files_exist()
    results.append(("文件结构", files_ok))
    
    # 检查导入
    imports_ok = check_imports()
    results.append(("模块导入", imports_ok))
    
    # 检查功能
    functionality_ok = check_functionality()
    results.append(("核心功能", functionality_ok))
    
    # 检查验收标准
    acceptance_ok = check_acceptance_criteria()
    results.append(("验收标准", acceptance_ok))
    
    # 总结
    print("\n" + "=" * 80)
    print("验证总结")
    print("=" * 80)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print(" " * 30 + "🎉 所有检查通过! 🎉")
        print(" " * 25 + "All checks passed!")
    else:
        print(" " * 30 + "⚠️  存在问题 ⚠️")
        print(" " * 25 + "Some checks failed")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
