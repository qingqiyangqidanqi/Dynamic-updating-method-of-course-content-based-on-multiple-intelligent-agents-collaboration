#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本清洗模块
负责对检索到的文本进行清洗和去重
"""

import os
import sys
import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger

logger = get_logger(__name__)

class TextCleaner:
    """文本清洗器，负责对检索到的文本进行清洗和去重"""
    
    def __init__(self, similarity_threshold=0.7):
        """初始化文本清洗器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值视为重复
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        logger.info(f"文本清洗器初始化完成，相似度阈值: {similarity_threshold}")
    
    def clean(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗文本
        
        Args:
            texts: 待清洗的文本列表，每个元素为字典格式
            
        Returns:
            清洗后的文本列表
        """
        logger.info(f"开始清洗{len(texts)}条文本")
        
        # 1. 基本清洗（去除HTML标签、多余空格等）
        cleaned_texts = [self._basic_clean(text) for text in texts]
        logger.info("基本清洗完成")
        
        # 2. 去重
        unique_texts = self._remove_duplicates(cleaned_texts)
        logger.info(f"去重完成，剩余{len(unique_texts)}条文本")
        
        return unique_texts
    
    def _basic_clean(self, text_item: Dict[str, Any]) -> Dict[str, Any]:
        """基本清洗，去除HTML标签、多余空格等
        
        Args:
            text_item: 待清洗的文本字典
            
        Returns:
            清洗后的文本字典
        """
        result = text_item.copy()
        
        # 清洗标题
        if "title" in result:
            result["title"] = self._clean_text(result["title"])
        
        # 清洗内容
        if "content" in result:
            result["content"] = self._clean_text(result["content"])
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """清洗文本字符串
        
        Args:
            text: 待清洗的文本字符串
            
        Returns:
            清洗后的文本字符串
        """
        if not text:
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff,.，。?？!！:：;；()（）\[\]【】\-]', '', text)
        
        return text.strip()
    
    def _remove_duplicates(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复文本
        
        Args:
            texts: 待去重的文本列表
            
        Returns:
            去重后的文本列表
        """
        if not texts:
            return []
        
        # 提取文本内容
        content_texts = []
        for item in texts:
            title = item.get("title", "")
            content = item.get("content", "")
            content_texts.append(f"{title} {content}")
        
        # 计算TF-IDF向量
        try:
            tfidf_matrix = self.vectorizer.fit_transform(content_texts)
            # 计算余弦相似度
            cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        except Exception as e:
            logger.error(f"计算文本相似度时出错: {e}")
            return texts
        
        # 标记要保留的索引
        to_keep = set(range(len(texts)))
        
        # 检查每对文档
        for i in range(len(texts)):
            if i not in to_keep:
                continue
                
            for j in range(i+1, len(texts)):
                if j not in to_keep:
                    continue
                    
                # 如果相似度超过阈值，移除较短的文本
                if cosine_sim[i, j] > self.similarity_threshold:
                    i_content = texts[i].get("content", "")
                    j_content = texts[j].get("content", "")
                    
                    if len(i_content) < len(j_content):
                        to_keep.discard(i)
                    else:
                        to_keep.discard(j)
        
        # 返回未被移除的文本
        return [texts[i] for i in sorted(to_keep)]


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = [
        {"title": "数据结构基础", "content": "数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。"},
        {"title": "数据结构简介", "content": "数据结构是计算机存储、组织数据的方式。通常情况下，精心选择的数据结构可以带来更高的运行或者存储效率。"},
        {"title": "图论基础", "content": "图论是数学的一个分支，它以图为研究对象，研究顶点和边组成的图形的数学理论和方法。"},
    ]
    
    cleaner = TextCleaner(similarity_threshold=0.6)
    results = cleaner.clean(test_data)
    
    print(f"\n清洗结果 ({len(results)} 条):")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['title']}")
        print(f"内容: {result['content']}")