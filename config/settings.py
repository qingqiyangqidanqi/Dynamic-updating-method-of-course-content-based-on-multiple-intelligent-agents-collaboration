#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件
存储API密钥和系统参数
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 默认配置
DEFAULT_CONFIG = {
    # API配置
    "llm_api": "GLM-4",  # 默认使用的大模型
    "search_engine": "bing",  # 默认搜索引擎
    
    # 权重规则配置
    "weight_rules": {
        "考研真题": 0.7,
        "高频考点": 0.5,
        "算法复杂度": 0.6,
        "数据结构基础": 0.4,
        "图论": 0.65,
        "树": 0.6,
        "排序": 0.55,
        "查找": 0.55,
        "动态规划": 0.5,
        "贪心算法": 0.45,
        "哈希表": 0.45,
        "栈": 0.4,
        "队列": 0.4,
        "链表": 0.4,
        "数组": 0.35,
        "字符串": 0.35,
        "递归": 0.3,
        "分治": 0.3
    },
    
    # 系统配置
    "max_results": 20,  # 最大检索结果数
    "similarity_threshold": 0.7,  # 相似度阈值
    "output_dir": "output",  # 输出目录
    
    # 模板配置
    "template_path": "data/data_struct.md"  # 课程模板路径
}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """加载配置
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    # 如果指定了配置文件，尝试加载
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 更新配置，但不覆盖嵌套字典
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                        # 对于嵌套字典，进行深度更新
                        config[key].update(value)
                    else:
                        config[key] = value
        except Exception as e:
            print(f"加载配置文件失败: {e}，将使用默认配置")
    
    # 从环境变量加载API密钥
    if os.getenv("OPENAI_API_KEY"):
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    
    if os.getenv("BING_SEARCH_KEY"):
        config["bing_search_key"] = os.getenv("BING_SEARCH_KEY")
    
    return config


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """保存配置到文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
        
    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    # 测试加载配置
    config = load_config()
    print("加载的配置:")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    
    # 测试保存配置
    test_config = {"test_key": "test_value"}
    save_result = save_config(test_config, "test_config.json")
    print(f"保存配置: {'成功' if save_result else '失败'}")