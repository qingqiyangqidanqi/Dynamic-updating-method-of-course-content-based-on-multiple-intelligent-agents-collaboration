#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
教学分析师模块
负责对检索到的知识进行分析和权重计算，采用纯文本分析方式替代知识图谱
"""

import os
import sys
import re
from typing import List, Dict, Any
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger

logger = get_logger(__name__)

class TeachingAnalyzer:
    """教学分析师，负责对知识进行分析和权重计算"""
    
    def __init__(self, weight_rules=None):
        """初始化教学分析师
        
        Args:
            weight_rules: 预定义的权重规则，如考研分数分布
        """
        self.weight_rules = weight_rules or self._load_rules()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        logger.info(f"教学分析师初始化完成，加载了{len(self.weight_rules)}条权重规则")
    
    def analyze(self, new_knowledge: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析新知识并计算权重
        
        Args:
            new_knowledge: 检索到的新知识列表
            
        Returns:
            按权重排序的知识点列表
        """
        logger.info(f"开始分析{len(new_knowledge)}条知识点")
        
        # 1. 文本去重（基于TF-IDF相似度）
        cleaned = self._remove_duplicates(new_knowledge)
        logger.info(f"去重后剩余{len(cleaned)}条知识点")
        
        # 2. 权重计算（基于规则匹配）
        weighted = []
        for topic in cleaned:
            weight = self._calculate_weight(topic)
            weighted.append({**topic, "weight": weight})
        
        # 3. 按权重排序
        result = sorted(weighted, key=lambda x: x["weight"], reverse=True)
        logger.info(f"完成权重计算和排序，权重范围: {result[-1]['weight']:.2f} - {result[0]['weight']:.2f}")
        
        return result
    
    def _load_rules(self) -> Dict[str, float]:
        """加载预定义的权重规则
        
        Returns:
            权重规则字典，关键词到权重的映射
        """
        # 默认权重规则
        return {
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
        }
    
    def _remove_duplicates(self, topics: List[Dict[str, Any]], threshold: float = 0.7) -> List[Dict[str, Any]]:
        """基于TF-IDF相似度去除重复的知识点
        
        Args:
            topics: 知识点列表
            threshold: 相似度阈值，超过此值视为重复
            
        Returns:
            去重后的知识点列表
        """
        if not topics:
            return []
        
        # 提取文本内容
        texts = [f"{topic.get('title', '')} {topic.get('content', '')}" for topic in topics]
        
        # 计算TF-IDF向量
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            # 计算余弦相似度
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        except Exception as e:
            logger.error(f"计算文本相似度时出错: {e}")
            return topics
        
        # 标记要保留的索引
        to_keep = set(range(len(topics)))
        
        # 检查每对文档
        for i in range(len(topics)):
            if i not in to_keep:
                continue
                
            for j in range(i+1, len(topics)):
                if j not in to_keep:
                    continue
                    
                # 如果相似度超过阈值，移除权重较低的
                if cosine_sim[i, j] > threshold:
                    # 简单比较标题长度，假设更长的标题包含更多信息
                    if len(topics[i].get('title', '')) < len(topics[j].get('title', '')):
                        to_keep.discard(i)
                    else:
                        to_keep.discard(j)
        
        # 返回未被移除的主题
        return [topics[i] for i in sorted(to_keep)]
    
    def _calculate_weight(self, topic: Dict[str, Any]) -> float:
        """计算知识点的权重
        
        Args:
            topic: 知识点字典
            
        Returns:
            计算得到的权重值
        """
        score = 0.0
        base_score = 0.2  # 基础分
        
        # 合并标题和内容用于匹配
        text = f"{topic.get('title', '')} {topic.get('content', '')}"
        
        # 根据规则计算权重
        for keyword, boost in self.weight_rules.items():
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                score += boost
        
        # 考虑来源因素
        source = topic.get('source', '').lower()
        if 'textbook' in source or '教材' in source:
            score += 0.3
        elif 'paper' in source or '论文' in source:
            score += 0.4
        elif 'exam' in source or '考试' in source or '真题' in source:
            score += 0.5
        
        # 考虑内容长度，假设更长的内容可能包含更多信息
        content_length = len(topic.get('content', ''))
        if content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # 确保最终分数在合理范围内
        return min(max(base_score + score, 0.1), 1.0)


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = [
        {"title": "最小生成树算法", "content": "最小生成树是连通加权无向图中一棵权值最小的生成树。常见算法有Kruskal和Prim算法。", "source": "textbook"},
        {"title": "Kruskal算法详解", "content": "Kruskal算法是一种用来寻找最小生成树的算法，基于贪心策略，按权值从小到大加入边。", "source": "lecture"},
        {"title": "图的遍历方法", "content": "图的遍历主要有两种方法：深度优先搜索(DFS)和广度优先搜索(BFS)。", "source": "exam"},
    ]
    
    analyzer = TeachingAnalyzer()
    results = analyzer.analyze(test_data)
    
    for i, result in enumerate(results):
        print(f"\n知识点 {i+1}: {result['title']}")
        print(f"权重: {result['weight']:.2f}")
        print(f"来源: {result.get('source', '未知')}")
        print(f"内容: {result['content'][:100]}...")