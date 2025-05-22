#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
关键词提取模块
负责从文本中提取重要关键词
"""

import os
import sys
import re
import jieba
import jieba.analyse
from typing import List, Dict, Any, Tuple
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger

logger = get_logger(__name__)

class KeywordExtractor:
    """关键词提取器，负责从文本中提取重要关键词"""
    
    def __init__(self, topk=20, allow_pos=('n', 'vn', 'v', 'nr', 'ns')):
        """初始化关键词提取器
        
        Args:
            topk: 提取的关键词数量
            allow_pos: 允许的词性，默认为名词、动名词、动词、人名、地名
        """
        self.topk = topk
        self.allow_pos = allow_pos
        
        # 加载停用词
        self.stopwords = self._load_stopwords()
        
        # 加载自定义词典
        self._load_custom_dict()
        
        logger.info(f"关键词提取器初始化完成，提取数量: {topk}")
    
    def extract(self, text: str) -> List[Tuple[str, float]]:
        """从文本中提取关键词
        
        Args:
            text: 待提取关键词的文本
            
        Returns:
            关键词列表，每个元素为(关键词, 权重)元组
        """
        if not text or len(text) < 10:
            return []
        
        logger.info(f"开始提取关键词，文本长度: {len(text)}")
        
        # 使用TF-IDF算法提取关键词
        tfidf_keywords = self._extract_by_tfidf(text)
        
        # 使用TextRank算法提取关键词
        textrank_keywords = self._extract_by_textrank(text)
        
        # 合并结果并去重
        merged_keywords = self._merge_keywords(tfidf_keywords, textrank_keywords)
        
        logger.info(f"关键词提取完成，共提取{len(merged_keywords)}个关键词")
        return merged_keywords
    
    def extract_from_items(self, items: List[Dict[str, Any]], key="content") -> Dict[str, List[Tuple[str, float]]]:
        """从多个文本项中提取关键词
        
        Args:
            items: 文本项列表，每个元素为字典格式
            key: 字典中文本内容的键名
            
        Returns:
            文本ID到关键词列表的映射
        """
        results = {}
        
        for i, item in enumerate(items):
            item_id = item.get("id", str(i))
            text = item.get(key, "")
            
            if text:
                keywords = self.extract(text)
                results[item_id] = keywords
        
        return results
    
    def _extract_by_tfidf(self, text: str) -> List[Tuple[str, float]]:
        """使用TF-IDF算法提取关键词
        
        Args:
            text: 待提取关键词的文本
            
        Returns:
            关键词列表，每个元素为(关键词, 权重)元组
        """
        try:
            # 使用jieba的TF-IDF算法提取关键词
            keywords = jieba.analyse.extract_tags(
                text,
                topK=self.topk,
                withWeight=True,
                allowPOS=self.allow_pos
            )
            
            # 过滤停用词
            filtered_keywords = [(word, weight) for word, weight in keywords if word not in self.stopwords]
            
            return filtered_keywords
        except Exception as e:
            logger.error(f"TF-IDF提取关键词失败: {e}")
            return []
    
    def _extract_by_textrank(self, text: str) -> List[Tuple[str, float]]:
        """使用TextRank算法提取关键词
        
        Args:
            text: 待提取关键词的文本
            
        Returns:
            关键词列表，每个元素为(关键词, 权重)元组
        """
        try:
            # 使用jieba的TextRank算法提取关键词
            keywords = jieba.analyse.textrank(
                text,
                topK=self.topk,
                withWeight=True,
                allowPOS=self.allow_pos
            )
            
            # 过滤停用词
            filtered_keywords = [(word, weight) for word, weight in keywords if word not in self.stopwords]
            
            return filtered_keywords
        except Exception as e:
            logger.error(f"TextRank提取关键词失败: {e}")
            return []
    
    def _merge_keywords(self, keywords1: List[Tuple[str, float]], keywords2: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """合并两组关键词并去重
        
        Args:
            keywords1: 第一组关键词
            keywords2: 第二组关键词
            
        Returns:
            合并后的关键词列表
        """
        # 合并关键词，如果有重复，取较大的权重
        keyword_dict = {}
        
        for word, weight in keywords1:
            keyword_dict[word] = weight
        
        for word, weight in keywords2:
            if word in keyword_dict:
                keyword_dict[word] = max(keyword_dict[word], weight)
            else:
                keyword_dict[word] = weight
        
        # 按权重排序
        sorted_keywords = sorted(keyword_dict.items(), key=lambda x: x[1], reverse=True)
        
        # 限制数量
        return sorted_keywords[:self.topk]
    
    def _load_stopwords(self) -> set:
        """加载停用词表
        
        Returns:
            停用词集合
        """
        # 常见停用词
        common_stopwords = {
            "的", "了", "和", "是", "在", "有", "与", "这", "那", "也", "都", "而", "及", "或", "等",
            "被", "比", "较", "把", "对", "用", "由", "向", "给", "但", "并", "如", "当", "只", "则",
            "可以", "因为", "所以", "因此", "如果", "虽然", "但是", "然后", "之后", "之前", "一个", "一种",
            "一些", "一样", "一般", "一直", "一定", "一方面", "一旦", "一次", "一片", "一边", "一面",
            "上", "下", "不", "不同", "不少", "不断", "不是", "不能", "不过", "不再", "中", "为", "为了",
            "为什么", "主要", "人", "什么", "什么样", "今", "今天", "今年", "从", "他", "他们", "以",
            "以及", "以前", "以后", "以外", "们", "任何", "会", "你", "你们", "使", "使用", "例如", "依",
            "依靠", "做", "其", "其他", "其实", "其中", "前", "前面", "去", "又", "及其", "双方", "反映",
            "发生", "取得", "受到", "变成", "可", "可能", "各", "各个", "各种", "同", "同时", "后",
            "后来", "后面", "向", "吗", "否则", "吧", "含有", "吧", "呀", "呢", "呵", "呵呵", "呼哧",
            "咋", "和", "咱", "咱们", "咳", "哇", "哈", "哈哈", "哉", "哎", "哎呀", "哎哟", "哗", "哟",
            "哦", "哩", "哪", "哪个", "哪些", "哪儿", "哪天", "哪年", "哪怕", "哪样", "哪边", "哪里",
            "哼", "哼唷", "唉", "唯有", "啊", "啐", "啥", "啦", "啪达", "啷当", "喂", "喏", "喔唷",
            "喽", "嗡", "嗡嗡", "嗬", "嗯", "嗳", "嘎", "嘎登", "嘘", "嘛", "嘻", "嘿", "因", "因为",
            "因此", "固然", "在", "在下", "地", "坚决", "坚持", "基本", "处理", "复杂", "多", "多少",
            "多数", "多次", "大", "大力", "大多数", "大大", "大家", "大批", "大约", "大量", "失去", "她",
            "她们", "好", "好的", "好象", "如", "如上", "如下", "如何", "如其", "如果", "如此", "如若",
            "存在", "宁", "宁可", "宁愿", "宁肯", "它", "它们", "对", "对于", "对方", "对比", "将",
            "小", "尔", "尔后", "尚且", "就", "就是", "就算", "尽", "尽管", "尽量", "局外", "居然",
            "届时", "属于", "岂", "岂但", "岂止", "岂非", "己", "已", "已经", "已矣", "巨大", "巩固",
            "差不多", "差一点", "己", "已", "已经", "已矣", "巨大", "巩固", "差不多", "差一点"
        }
        
        # 尝试从文件加载停用词
        try:
            stopwords_path = os.path.join(os.path.dirname(__file__), "stopwords.txt")
            if os.path.exists(stopwords_path):
                with open(stopwords_path, 'r', encoding='utf-8') as f:
                    file_stopwords = set(line.strip() for line in f if line.strip())
                common_stopwords.update(file_stopwords)
                logger.info(f"从文件加载了{len(file_stopwords)}个停用词")
        except Exception as e:
            logger.warning(f"加载停用词文件失败: {e}")
        
        return common_stopwords
    
    def _load_custom_dict(self):
        """加载自定义词典"""
        # 数据结构领域的专业词汇
        custom_words = [
            ("数据结构", 100),
            ("算法", 100),
            ("时间复杂度", 100),
            ("空间复杂度", 100),
            ("线性表", 100),
            ("链表", 100),
            ("栈", 100),
            ("队列", 100),
            ("树", 100),
            ("二叉树", 100),
            ("图", 100),
            ("哈希表", 100),
            ("排序算法", 100),
            ("查找算法", 100),
            ("动态规划", 100),
            ("贪心算法", 100),
            ("分治算法", 100),
            ("回溯算法", 100),
            ("最小生成树", 100),
            ("最短路径", 100),
            ("拓扑排序", 100),
            ("关键路径", 100),
            ("哈夫曼树", 100),
            ("哈夫曼编码", 100),
            ("B树", 100),
            ("B+树", 100),
            ("红黑树", 100),
            ("AVL树", 100),
            ("邻接矩阵", 100),
            ("邻接表", 100),
            ("深度优先搜索", 100),
            ("广度优先搜索", 100),
            ("Dijkstra算法", 100),
            ("Floyd算法", 100),
            ("Kruskal算法", 100),
            ("Prim算法", 100),
            ("快速排序", 100),
            ("归并排序", 100),
            ("堆排序", 100),
            ("冒泡排序", 100),
            ("插入排序", 100),
            ("选择排序", 100),
            ("希尔排序", 100),
            ("基数排序", 100),
            ("计数排序", 100),
            ("桶排序", 100),
            ("二分查找", 100),
            ("顺序查找", 100),
            ("散列查找", 100),
            ("考研真题", 200),
            ("高频考点", 200)
        ]
        
        # 添加自定义词汇到jieba词典
        for word, weight in custom_words:
            jieba.add_word(word, freq=weight)
        
        logger.info(f"加载了{len(custom_words)}个自定义词汇")


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_text = """
    数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。
    常见的数据结构包括数组、链表、栈、队列、树、图、堆和散列表等。
    图论是数学的一个分支，它以图为研究对象，研究顶点和边组成的图形的数学理论和方法。
    图论在计算机科学中有广泛应用，如网络流、最短路径、最小生成树等问题。
    最小生成树是连通加权无向图中一棵权值最小的生成树。常见的最小生成树算法有Kruskal算法和Prim算法。
    """
    
    extractor = KeywordExtractor(topk=10)
    keywords = extractor.extract(test_text)
    
    print("\n提取的关键词:")
    for word, weight in keywords:
        print(f"{word}: {weight:.4f}")