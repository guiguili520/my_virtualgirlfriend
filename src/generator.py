#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟女友数据集生成器
负责从场景目录生成训练数据集
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any
from scenarios import SCENARIO_CATALOG, validate_catalog, get_catalog_metadata


class GirlfriendDatasetGenerator:
    """虚拟女友数据集生成器类"""
    
    def __init__(self, scenarios=None):
        """
        初始化生成器
        
        Args:
            scenarios: 场景列表，如果为None则使用默认的SCENARIO_CATALOG
        """
        self.scenarios = scenarios if scenarios is not None else SCENARIO_CATALOG
        validate_catalog()
        self.metadata = get_catalog_metadata()
    
    def generate_single_entry(self, scenario, variation_index: int = 0) -> Dict[str, str]:
        """
        从单个场景生成一条数据
        
        Args:
            scenario: 场景对象
            variation_index: 变体索引，用于选择不同的响应模板
        
        Returns:
            包含instruction, input, output的字典
        """
        # 循环选择响应模板
        response_template = scenario.response_templates[
            variation_index % len(scenario.response_templates)
        ]
        
        return {
            "instruction": scenario.instruction,
            "input": scenario.input,
            "output": response_template
        }
    
    def generate_deterministic_dataset(self, variations_per_scenario: int = 1) -> List[Dict[str, str]]:
        """
        确定性地生成数据集（每个场景按顺序生成）
        
        Args:
            variations_per_scenario: 每个场景生成的变体数量
        
        Returns:
            数据集列表
        """
        dataset = []
        
        # 按顺序遍历所有场景
        for scenario in self.scenarios:
            # 为每个场景生成指定数量的变体
            for i in range(variations_per_scenario):
                entry = self.generate_single_entry(scenario, i)
                dataset.append(entry)
        
        return dataset
    
    def generate_random_dataset(self, num_samples: int = 500, seed: int = None) -> List[Dict[str, str]]:
        """
        随机生成数据集（旧版兼容模式）
        
        Args:
            num_samples: 要生成的样本数量
            seed: 随机种子，用于复现
        
        Returns:
            数据集列表
        """
        if seed is not None:
            random.seed(seed)
        
        dataset = []
        
        for _ in range(num_samples):
            # 随机选择一个场景
            scenario = random.choice(self.scenarios)
            # 随机选择一个响应模板
            response = random.choice(scenario.response_templates)
            
            entry = {
                "instruction": scenario.instruction,
                "input": scenario.input,
                "output": response
            }
            dataset.append(entry)
        
        return dataset
    
    def generate_balanced_dataset(self, samples_per_scenario: int = 10) -> List[Dict[str, str]]:
        """
        生成平衡的数据集（每个场景生成相同数量的样本）
        
        Args:
            samples_per_scenario: 每个场景生成的样本数量
        
        Returns:
            数据集列表
        """
        dataset = []
        
        for scenario in self.scenarios:
            for _ in range(samples_per_scenario):
                # 随机选择一个响应模板
                response = random.choice(scenario.response_templates)
                
                entry = {
                    "instruction": scenario.instruction,
                    "input": scenario.input,
                    "output": response
                }
                dataset.append(entry)
        
        # 打乱数据集
        random.shuffle(dataset)
        
        return dataset
    
    def generate_dataset_with_metadata(
        self,
        num_samples: int = 500,
        mode: str = "random",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成带元数据的数据集
        
        Args:
            num_samples: 样本数量（仅在random模式下使用）
            mode: 生成模式，可选 "random", "deterministic", "balanced"
            **kwargs: 其他参数
        
        Returns:
            包含数据集和元数据的字典
        """
        if mode == "deterministic":
            variations_per_scenario = kwargs.get("variations_per_scenario", 1)
            dataset = self.generate_deterministic_dataset(variations_per_scenario)
        elif mode == "balanced":
            samples_per_scenario = kwargs.get("samples_per_scenario", 10)
            dataset = self.generate_balanced_dataset(samples_per_scenario)
        else:  # random
            seed = kwargs.get("seed", None)
            dataset = self.generate_random_dataset(num_samples, seed)
        
        return {
            "data": dataset,
            "metadata": {
                "total_samples": len(dataset),
                "total_scenarios": len(self.scenarios),
                "mode": mode,
                "generation_time": datetime.now().isoformat(),
                **kwargs
            }
        }
    
    def save_dataset(
        self,
        dataset: List[Dict[str, str]],
        output_path: str = None,
        include_metadata: bool = False
    ) -> str:
        """
        保存数据集到JSON文件
        
        Args:
            dataset: 数据集列表
            output_path: 输出文件路径，如果为None则自动生成
            include_metadata: 是否在文件中包含元数据
        
        Returns:
            保存的文件路径
        """
        import os
        
        # 创建输出目录
        output_dir = "train_data/dataset"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{output_dir}/girlfriend_chat_dataset_{timestamp}.json"
        
        # 准备保存的数据
        if include_metadata:
            save_data = {
                "dataset": dataset,
                "metadata": self.metadata
            }
        else:
            save_data = dataset
        
        # 保存为JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def get_statistics(self, dataset: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        获取数据集统计信息
        
        Args:
            dataset: 数据集列表
        
        Returns:
            统计信息字典
        """
        # 统计各个指令的出现次数
        instruction_counts = {}
        for entry in dataset:
            instruction = entry["instruction"]
            instruction_counts[instruction] = instruction_counts.get(instruction, 0) + 1
        
        # 统计emoji覆盖率
        emoji_count = sum(1 for entry in dataset if any(
            char for char in entry["output"] 
            if ord(char) > 0x1F000
        ))
        
        # 统计输入为空的比例
        empty_input_count = sum(1 for entry in dataset if not entry["input"])
        
        return {
            "total_samples": len(dataset),
            "unique_instructions": len(instruction_counts),
            "instruction_distribution": instruction_counts,
            "emoji_coverage": f"{emoji_count / len(dataset) * 100:.2f}%",
            "empty_input_ratio": f"{empty_input_count / len(dataset) * 100:.2f}%",
            "avg_output_length": sum(len(entry["output"]) for entry in dataset) / len(dataset)
        }
    
    def print_sample_data(self, dataset: List[Dict[str, str]], num_samples: int = 3):
        """
        打印示例数据
        
        Args:
            dataset: 数据集列表
            num_samples: 要打印的样本数量
        """
        print(f"\n示例数据:")
        for i in range(min(num_samples, len(dataset))):
            print(f"\n--- 样本 {i+1} ---")
            print(f"Instruction: {dataset[i]['instruction']}")
            print(f"Input: {dataset[i]['input']}")
            print(f"Output: {dataset[i]['output']}")


def generate_dataset(num_samples: int = 500) -> List[Dict[str, str]]:
    """
    生成数据集的快捷函数（向后兼容）
    
    Args:
        num_samples: 要生成的样本数量
    
    Returns:
        数据集列表
    """
    generator = GirlfriendDatasetGenerator()
    return generator.generate_random_dataset(num_samples)


if __name__ == "__main__":
    # 测试生成器
    print("测试虚拟女友数据集生成器\n")
    
    # 创建生成器
    generator = GirlfriendDatasetGenerator()
    
    # 显示场景目录信息
    print(f"📊 场景目录信息:")
    print(f"   总场景数: {generator.metadata['total_scenarios']}")
    print(f"   分类数: {len(generator.metadata['categories'])}")
    print(f"   分类列表: {', '.join(generator.metadata['categories'])}")
    
    # 测试确定性生成（每个场景生成一次）
    print(f"\n🔍 测试确定性生成模式...")
    deterministic_dataset = generator.generate_deterministic_dataset(variations_per_scenario=1)
    print(f"   生成样本数: {len(deterministic_dataset)}")
    print(f"   应等于场景数: {len(SCENARIO_CATALOG)}")
    assert len(deterministic_dataset) == len(SCENARIO_CATALOG), "确定性生成失败"
    
    # 验证每个场景的指令都是唯一的
    instructions = [entry["instruction"] for entry in deterministic_dataset]
    assert len(instructions) == len(set(instructions)), "指令存在重复"
    print(f"   ✅ 确定性生成验证通过")
    
    # 显示前3个样本
    generator.print_sample_data(deterministic_dataset, 3)
    
    # 获取统计信息
    stats = generator.get_statistics(deterministic_dataset)
    print(f"\n📈 数据集统计:")
    print(f"   总样本数: {stats['total_samples']}")
    print(f"   唯一指令数: {stats['unique_instructions']}")
    print(f"   Emoji覆盖率: {stats['emoji_coverage']}")
    print(f"   空输入比例: {stats['empty_input_ratio']}")
    print(f"   平均输出长度: {stats['avg_output_length']:.1f}字符")
