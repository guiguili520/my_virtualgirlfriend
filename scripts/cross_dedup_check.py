#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练集与验证集交叉去重和质量检查工具
确保训练集和验证集之间没有重复数据
"""

import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple


class CrossDeduplicator:
    """训练集和验证集交叉去重器"""
    
    def __init__(self, similarity_threshold: float = 0.90):
        """
        初始化去重器
        
        Args:
            similarity_threshold: 相似度阈值，默认0.90
        """
        self.similarity_threshold = similarity_threshold
    
    def load_dataset(self, filepath: str) -> List[Dict[str, str]]:
        """加载数据集"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def save_dataset(self, dataset: List[Dict[str, str]], filepath: str):
        """保存数据集"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def is_duplicate(self, entry1: Dict[str, str], entry2: Dict[str, str]) -> bool:
        """
        判断两个数据条目是否重复
        
        检查instruction、input和output的相似度
        """
        # 完全相同检查
        if (entry1['instruction'] == entry2['instruction'] and 
            entry1['input'] == entry2['input'] and 
            entry1['output'] == entry2['output']):
            return True
        
        # 相似度检查 - 只要instruction和input相同，且output相似度超过阈值
        if (entry1['instruction'] == entry2['instruction'] and 
            entry1['input'] == entry2['input']):
            output_similarity = self.calculate_similarity(
                entry1['output'], 
                entry2['output']
            )
            if output_similarity >= self.similarity_threshold:
                return True
        
        return False
    
    def find_duplicates(
        self, 
        train_data: List[Dict[str, str]], 
        val_data: List[Dict[str, str]]
    ) -> Tuple[List[int], List[Tuple[int, int, float]]]:
        """
        查找训练集和验证集之间的重复数据
        
        Args:
            train_data: 训练集
            val_data: 验证集
        
        Returns:
            (重复的验证集索引列表, 重复详情列表)
        """
        duplicate_indices = []
        duplicate_details = []
        
        for val_idx, val_entry in enumerate(val_data):
            for train_idx, train_entry in enumerate(train_data):
                if self.is_duplicate(val_entry, train_entry):
                    similarity = self.calculate_similarity(
                        val_entry['output'], 
                        train_entry['output']
                    )
                    duplicate_indices.append(val_idx)
                    duplicate_details.append((val_idx, train_idx, similarity))
                    break  # 找到第一个重复就停止
        
        return duplicate_indices, duplicate_details
    
    def validate_format(self, entry: Dict[str, str]) -> Dict[str, Any]:
        """
        验证单个数据条目的格式
        
        Returns:
            验证结果字典
        """
        issues = []
        warnings = []
        
        # 检查必需字段
        required_fields = ['instruction', 'input', 'output']
        for field in required_fields:
            if field not in entry:
                issues.append(f"缺少字段: {field}")
        
        if 'output' in entry:
            output = entry['output']
            
            # 检查输出长度
            if len(output) < 5:
                issues.append(f"输出过短: {len(output)}字符")
            elif len(output) > 300:
                issues.append(f"输出过长: {len(output)}字符")
            elif len(output) < 15:
                warnings.append(f"输出较短: {len(output)}字符")
            elif len(output) > 200:
                warnings.append(f"输出较长: {len(output)}字符")
            
            # 检查emoji (注意：emoji的Unicode范围很广，需要更全面的检查)
            has_emoji = any(
                ord(char) > 0x1F000 or  # Emoticons, symbols
                0x2600 <= ord(char) <= 0x27BF or  # Misc symbols
                0x1F300 <= ord(char) <= 0x1F9FF  # Extended emoticons
                for char in output
            )
            if not has_emoji:
                warnings.append("建议添加emoji")
            
            # 检查语气词 (作为建议而非强制)
            tone_particles = ['呀', '啦', '呢', '哦', '嘛', '哒', '啊', '吧', '~', '！']
            has_tone = any(particle in output for particle in tone_particles)
            if not has_tone:
                warnings.append("建议添加语气词")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def validate_dataset_format(
        self, 
        dataset: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """验证整个数据集的格式"""
        total = len(dataset)
        invalid_entries = []
        
        for idx, entry in enumerate(dataset):
            validation = self.validate_format(entry)
            if not validation['valid']:
                invalid_entries.append({
                    'index': idx,
                    'entry': entry,
                    'issues': validation['issues']
                })
        
        return {
            'total': total,
            'valid': total - len(invalid_entries),
            'invalid': len(invalid_entries),
            'invalid_entries': invalid_entries[:10]  # 只保留前10个
        }
    
    def perform_cross_deduplication(
        self,
        train_path: str,
        val_path: str,
        output_path: str = None,
        report_only: bool = False
    ) -> Dict[str, Any]:
        """
        执行交叉去重
        
        Args:
            train_path: 训练集路径
            val_path: 验证集路径
            output_path: 输出路径（可选）
            report_only: 仅报告，不进行修改
        
        Returns:
            去重报告
        """
        print("=" * 80)
        print("训练集与验证集交叉去重检查")
        print("=" * 80)
        
        # 1. 加载数据集
        print("\n📂 加载数据集...")
        train_data = self.load_dataset(train_path)
        val_data = self.load_dataset(val_path)
        
        original_train_count = len(train_data)
        original_val_count = len(val_data)
        
        print(f"   训练集: {original_train_count} 条")
        print(f"   验证集: {original_val_count} 条")
        
        # 2. 查找重复数据
        print("\n🔍 检测交叉重复数据...")
        print(f"   相似度阈值: {self.similarity_threshold}")
        duplicate_indices, duplicate_details = self.find_duplicates(train_data, val_data)
        
        duplicate_count = len(set(duplicate_indices))
        duplication_rate = duplicate_count / original_val_count * 100 if original_val_count > 0 else 0
        
        print(f"   发现重复数据: {duplicate_count} 条 ({duplication_rate:.1f}%)")
        
        # 3. 删除重复数据（如果不是仅报告模式）
        cleaned_val_data = val_data
        
        if duplicate_count > 0 and not report_only:
            print("\n🗑️  删除验证集中的重复数据...")
            # 去重索引
            unique_indices = set(duplicate_indices)
            cleaned_val_data = [
                entry for idx, entry in enumerate(val_data) 
                if idx not in unique_indices
            ]
            print(f"   删除后验证集: {len(cleaned_val_data)} 条")
            
            # 保存清理后的验证集
            if output_path is None:
                output_path = val_path
            
            self.save_dataset(cleaned_val_data, output_path)
            print(f"   ✅ 已保存清理后的验证集: {output_path}")
        elif duplicate_count == 0:
            print("   ✅ 未发现重复数据，无需清理")
        
        # 4. 验证格式
        print("\n📋 验证数据格式...")
        train_format_check = self.validate_dataset_format(train_data)
        val_format_check = self.validate_dataset_format(cleaned_val_data)
        
        print(f"   训练集: {train_format_check['valid']}/{train_format_check['total']} 条有效 "
              f"({train_format_check['valid']/train_format_check['total']*100:.1f}%)")
        if train_format_check['invalid'] > 0:
            print(f"   ⚠️  训练集有 {train_format_check['invalid']} 条数据格式不完全符合建议")
        
        print(f"   验证集: {val_format_check['valid']}/{val_format_check['total']} 条有效 "
              f"({val_format_check['valid']/val_format_check['total']*100:.1f}%)")
        if val_format_check['invalid'] > 0:
            print(f"   ⚠️  验证集有 {val_format_check['invalid']} 条数据格式不完全符合建议")
        
        # 5. 统计分析
        print("\n📊 数据集统计分析...")
        train_instructions = set(e['instruction'] for e in train_data)
        val_instructions = set(e['instruction'] for e in cleaned_val_data)
        overlapping_instructions = train_instructions & val_instructions
        
        print(f"   训练集唯一场景数: {len(train_instructions)}")
        print(f"   验证集唯一场景数: {len(val_instructions)}")
        print(f"   场景重叠数: {len(overlapping_instructions)}")
        
        # 6. 生成报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'similarity_threshold': self.similarity_threshold,
            'original_counts': {
                'train': original_train_count,
                'validation': original_val_count
            },
            'deduplication': {
                'duplicates_found': duplicate_count,
                'duplication_rate': f"{duplication_rate:.2f}%",
                'duplicate_details': [
                    {
                        'val_index': val_idx,
                        'train_index': train_idx,
                        'similarity': round(sim, 4),
                        'val_entry': val_data[val_idx] if val_idx < len(val_data) else None
                    }
                    for val_idx, train_idx, sim in duplicate_details[:20]  # 保留前20个
                ],
                'samples_removed': duplicate_count if not report_only else 0
            },
            'final_counts': {
                'train': len(train_data),
                'validation': len(cleaned_val_data)
            },
            'format_validation': {
                'train': {
                    'total': train_format_check['total'],
                    'valid': train_format_check['valid'],
                    'invalid': train_format_check['invalid']
                },
                'validation': {
                    'total': val_format_check['total'],
                    'valid': val_format_check['valid'],
                    'invalid': val_format_check['invalid']
                }
            },
            'scenario_analysis': {
                'train_unique_scenarios': len(train_instructions),
                'val_unique_scenarios': len(val_instructions),
                'overlapping_scenarios': len(overlapping_instructions)
            },
            'files': {
                'train_dataset': train_path,
                'validation_dataset': output_path if output_path else val_path
            },
            'report_only_mode': report_only
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_dir: str = "train_data"):
        """保存质量检测报告"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{output_dir}/cross_dedup_report_{timestamp}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report_path
    
    def print_report(self, report: Dict[str, Any]):
        """打印格式化的报告"""
        print("\n" + "=" * 80)
        print("质量检测报告")
        print("=" * 80)
        
        print(f"\n📅 生成时间: {report['timestamp']}")
        print(f"🎯 相似度阈值: {report['similarity_threshold']}")
        
        print("\n📊 原始数据统计:")
        print(f"   训练集: {report['original_counts']['train']} 条")
        print(f"   验证集: {report['original_counts']['validation']} 条")
        
        print("\n🔄 去重统计:")
        dedup = report['deduplication']
        print(f"   发现重复: {dedup['duplicates_found']} 条 ({dedup['duplication_rate']})")
        print(f"   已删除: {dedup['samples_removed']} 条")
        
        if dedup['duplicates_found'] > 0:
            print("\n   重复样本示例（前5条）:")
            for idx, detail in enumerate(dedup['duplicate_details'][:5], 1):
                if detail['val_entry']:
                    print(f"\n   [{idx}] 验证集索引 {detail['val_index']} "
                          f"与训练集索引 {detail['train_index']} 重复 "
                          f"(相似度: {detail['similarity']:.2%})")
                    print(f"       指令: {detail['val_entry']['instruction']}")
                    print(f"       输入: {detail['val_entry']['input']}")
                    print(f"       输出: {detail['val_entry']['output'][:60]}...")
        
        print("\n📋 格式验证:")
        train_fmt = report['format_validation']['train']
        val_fmt = report['format_validation']['validation']
        print(f"   训练集: {train_fmt['valid']}/{train_fmt['total']} 有效 "
              f"({train_fmt['valid']/train_fmt['total']*100:.1f}%)")
        print(f"   验证集: {val_fmt['valid']}/{val_fmt['total']} 有效 "
              f"({val_fmt['valid']/val_fmt['total']*100:.1f}%)")
        
        print("\n🎭 场景分析:")
        scenario = report['scenario_analysis']
        print(f"   训练集唯一场景: {scenario['train_unique_scenarios']}")
        print(f"   验证集唯一场景: {scenario['val_unique_scenarios']}")
        print(f"   场景重叠: {scenario['overlapping_scenarios']}")
        
        print("\n✅ 最终数据统计:")
        print(f"   训练集: {report['final_counts']['train']} 条")
        print(f"   验证集: {report['final_counts']['validation']} 条")
        
        print("\n📁 数据文件:")
        print(f"   训练集: {report['files']['train_dataset']}")
        print(f"   验证集: {report['files']['validation_dataset']}")
        
        print("\n" + "=" * 80)
        
        # 最终确认和建议
        if dedup['duplicates_found'] == 0:
            print("✅ 质量检查通过！训练集和验证集无重复数据。")
        elif dedup['samples_removed'] > 0:
            print("✅ 去重完成！验证集已清理。")
            print(f"\n⚠️  建议: 验证集从 {report['original_counts']['validation']} 条减少到 "
                  f"{report['final_counts']['validation']} 条")
            print(f"   建议重新生成完整的验证集（至少400条）以确保充足的验证数据。")
        else:
            print(f"⚠️  检测到 {dedup['duplicates_found']} 条重复数据（报告模式，未删除）")
            print(f"   建议清理重复数据或重新生成验证集。")
        
        print("=" * 80)


def main():
    """主函数"""
    # 配置
    train_path = "data/train/girlfriend_chat_dataset_20251117_055552.json"
    val_path = "data/validation/girlfriend_chat_validation_20251123_074751.json"
    similarity_threshold = 0.90
    
    # 创建去重器
    deduplicator = CrossDeduplicator(similarity_threshold=similarity_threshold)
    
    # 执行交叉去重（报告模式，不删除数据）
    report = deduplicator.perform_cross_deduplication(
        train_path=train_path,
        val_path=val_path,
        report_only=True  # 仅报告，不删除数据
    )
    
    # 打印报告
    deduplicator.print_report(report)
    
    # 保存报告
    report_path = deduplicator.save_report(report)
    print(f"\n💾 详细报告已保存: {report_path}")
    
    # 询问是否执行清理
    print("\n" + "=" * 80)
    print("📢 重要提示:")
    print("=" * 80)
    print("\n由于发现大量重复（96.5%），建议采取以下措施之一:")
    print("\n1. 重新生成验证集（推荐）:")
    print("   - 使用不同的随机种子")
    print("   - 确保与训练集生成策略有所区别")
    print("   - 建议使用 generate_girlfriend_dataset.py 重新生成")
    print("\n2. 使用当前去重后的数据:")
    print("   - 将会保留 14 条非重复验证样本")
    print("   - 不足以进行充分的模型验证")
    print("   - 需要补充更多数据")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
