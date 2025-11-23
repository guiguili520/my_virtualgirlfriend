import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import time

# 内存优化设置
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

# 配置
MODEL_PATH = "./models"
ROLE_PROMPT_PATH = "./data/role/atri.md"  # 可选: mono.md, nijiko.md

# 检查模型路径
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ 模型路径不存在: {MODEL_PATH}")

# 读取角色提示词
if os.path.exists(ROLE_PROMPT_PATH):
    with open(ROLE_PROMPT_PATH, 'r', encoding='utf-8') as f:
        ROLE_PROMPT = f.read().strip()
    print(f"✅ 已加载角色: {ROLE_PROMPT_PATH}")
else:
    ROLE_PROMPT = "你是一个温柔体贴、俏皮可爱的AI女友。"
    print(f"⚠️  使用默认角色设定")


def load_model():
    """加载模型到MPS设备"""
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"\n⏳ 正在加载模型到 {device.upper()}...")
    
    start_time = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    ).to(device)
    
    print(f"✅ 模型加载完成！耗时: {time.time() - start_time:.1f}秒")
    print(f"   设备: {device} | 内存: {model.get_memory_footprint() / 1024**3:.2f} GB\n")
    return model


# 加载模型和tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = load_model()


def chat(user_input, max_tokens=150):
    """对话函数"""
    print(f"\n💭 思考中...", end="", flush=True)
    
    # 构建消息
    messages = [
        {"role": "system", "content": ROLE_PROMPT},
        {"role": "user", "content": user_input}
    ]
    
    # 应用对话模板
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # 编码并移动到设备
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    # 生成回复
    gen_start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.85,
            top_k=20,
            repetition_penalty=1.15,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    print(f" ({time.time() - gen_start:.1f}秒)")
    
    # 解码
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )
    return response.strip()


# 交互式对话
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI女友聊天系统")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 输入消息开始聊天")
    print("   - 输入 'exit' 或 'quit' 退出")
    print("   - 输入 'clear' 清空对话历史")
    print("\n" + "=" * 60 + "\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', '退出', '再见']:
                print("\n👋 再见！期待下次聊天~")
                break
            
            if user_input.lower() in ['clear', '清空']:
                conversation_history.clear()
                print("\n✅ 对话历史已清空\n")
                continue
            
            response = chat(user_input)
            print(f"🤖 AI女友: {response}\n")
            
            # 保存对话历史（可选，用于多轮对话）
            conversation_history.append({"user": user_input, "assistant": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")
            continue