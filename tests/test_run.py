import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel  # 加载LoRA需要
import os

# 内存优化设置
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

print('MPS可用 === ', torch.backends.mps.is_available())

# 本地模型路径
base_model_path = "./Qwen2.5-7B-Instruct"  # 基础模型
lora_model_path = "./qwen-ai-girlfriend-lora"  # LoRA适配器

print("正在为24GB Mac内存优化加载模型...")


def load_model_optimized():
    """为24GB内存优化的模型加载（支持MPS + LoRA）"""
    
    # 检测可用设备
    if torch.backends.mps.is_available():
        device = "mps"
        print("✅ 检测到MPS设备，使用GPU加速")
    elif torch.cuda.is_available():
        device = "cuda"
        print("✅ 检测到CUDA设备，使用GPU加速")
    else:
        device = "cpu"
        print("⚠️ 未检测到GPU，使用CPU")
    
    try:
        # 先加载基础模型
        if device == "mps":
            print("正在加载基础模型到MPS (float32)...")
            model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                dtype=torch.float32,  # 使用float32保证数值稳定性
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            model = model.to(device)
            print("✅ 基础模型加载成功")
            
            # 加载LoRA适配器
            print("正在加载LoRA适配器...", flush=True)
            try:
                model = PeftModel.from_pretrained(model, lora_model_path)
                print("✅ LoRA适配器加载成功")
            except Exception as lora_error:
                print(f"❌ LoRA加载失败: {lora_error}")
                print("尝试检查 LoRA 路径和文件...")
                import os
                print(f"LoRA路径存在: {os.path.exists(lora_model_path)}")
                if os.path.exists(lora_model_path):
                    print(f"LoRA目录内容: {os.listdir(lora_model_path)}")
                raise
        
        # CUDA设备可以尝试量化
        elif device == "cuda":
            try:
                print("尝试8位量化加载...")
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_compute_dtype=torch.float16
                )
                model = AutoModelForCausalLM.from_pretrained(
                    base_model_path,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
                model = PeftModel.from_pretrained(model, lora_model_path)
                print("✅ 8位量化+LoRA加载成功")
            except Exception as e:
                print(f"量化失败: {e}，使用float16...")
                model = AutoModelForCausalLM.from_pretrained(
                    base_model_path,
                    dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                model = PeftModel.from_pretrained(model, lora_model_path)
                print("✅ CUDA float16+LoRA加载成功")
        
        # CPU加载
        else:
            print("正在加载模型到CPU...")
            model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            model = PeftModel.from_pretrained(model, lora_model_path)
            print("✅ CPU+LoRA加载成功")
            
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        raise

    return model


# 加载tokenizer和模型
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
model = load_model_optimized()

# 确保tokenizer设置
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"模型设备: {model.device}")
print(f"模型内存占用: 约{model.get_memory_footprint() / 1024 ** 3:.2f} GB")


def optimized_chat(user_input, max_tokens=200):
    """内存优化的对话函数"""

    # 清理GPU内存（如果使用MPS）
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # 构建输入
    messages = [{"role": "user", "content": user_input}]

    try:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    except:
        # 备用手动格式化
        text = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

    # 编码 - 使用更小的批处理
    inputs = tokenizer(text, return_tensors="pt")

    # 移动到设备
    if hasattr(model, 'device'):
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # 内存优化的生成参数
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,  # 限制生成长度
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=40,  # 限制候选词
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            num_beams=1,  # 不使用beam search节省内存
            early_stopping=True
        )

    # 解码回复
    input_length = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)

    return response.strip()


# 测试对话
print("\n🧪 测试对话...")
test_prompts = [
    "请用一句话介绍你自己",
    "写一个简短的问候",
    "早上好呀"
]

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n[{i}/{len(test_prompts)}] 用户: {prompt}")
    try:
        response = optimized_chat(prompt, max_tokens=512)
        print(f"AI: {response}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        # 尝试清理内存后重试
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()