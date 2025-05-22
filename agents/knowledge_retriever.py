#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识检索专家模块
负责从搜索引擎和大模型API获取最新的知识内容
"""

import os
import sys
import random
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.search_engine_api import SearchEngineAPI
from api.llm_api import LLMAPI
from utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeRetriever:
    """知识检索专家，负责从多个来源获取最新的知识内容"""
    
    def __init__(self, llm_api="GLM-4", search_engine="bing"):
        """初始化知识检索专家
        
        Args:
            llm_api: 使用的大模型API名称
            search_engine: 使用的搜索引擎名称
        """
        self.llm_api = LLMAPI(model_name=llm_api)
        self.search_engine = SearchEngineAPI(engine=search_engine)
        logger.info(f"知识检索专家初始化完成，使用模型: {llm_api}, 搜索引擎: {search_engine}")
    
    def retrieve(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """检索与查询相关的知识
        
        Args:
            query: 搜索查询关键词
            max_results: 最大返回结果数量
            
        Returns:
            包含检索到的知识条目的列表，每个条目为字典格式
        """
        logger.info(f"开始检索知识: {query}")
        
        # 从搜索引擎获取结果
        search_results = self.search_engine.search(query, max_results=max_results//2)
        logger.info(f"从搜索引擎获取了{len(search_results)}条结果")
        
        # 从大模型获取知识补充
        prompt = f"请提供关于'{query}'的最新教学知识，特别是考研考点和重要算法。格式为多个知识点条目，每个条目包含标题和内容。"
        llm_results = self.llm_api.generate(prompt)
        
        # 解析大模型返回的知识点
        knowledge_items = self._parse_llm_results(llm_results, query)
        logger.info(f"从大模型获取了{len(knowledge_items)}条知识点")
        
        # 合并结果
        all_results = search_results + knowledge_items
        
        # 为每个知识点添加元数据
        for item in all_results:
            if "metadata" not in item:
                item["metadata"] = {}
            item["metadata"]["retrieved_at"] = datetime.now().isoformat()
            item["metadata"]["source"] = item.get("source", "llm_generated")
        
        logger.info(f"知识检索完成，共获取{len(all_results)}条知识点")
        return all_results
    
    def _parse_llm_results(self, llm_text: str, query: str) -> List[Dict[str, Any]]:
        """解析大模型返回的文本，提取结构化的知识点
        
        Args:
            llm_text: 大模型返回的文本
            query: 原始查询关键词
            
        Returns:
            结构化的知识点列表
        """
        # 这里使用简单的分割方法，实际项目中可能需要更复杂的解析
        # 模拟解析结果
        knowledge_items = []
        
        # 简单模拟，实际实现需要根据LLM返回格式进行解析
        lines = llm_text.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#') or line.startswith('标题:') or line.startswith('知识点:'):
                # 如果已经有一个条目在处理中，先保存它
                if current_item and 'title' in current_item and 'content' in current_item:
                    knowledge_items.append(current_item)
                
                # 开始一个新条目
                current_item = {
                    "title": line.lstrip('#').lstrip(':').strip(),
                    "content": "",
                    "source": "llm_generated",
                    "query": query
                }
            elif current_item and 'title' in current_item:
                # 将这一行添加到当前条目的内容中
                if current_item["content"]:
                    current_item["content"] += "\n"
                current_item["content"] += line
        
        # 添加最后一个条目
        if current_item and 'title' in current_item and 'content' in current_item:
            knowledge_items.append(current_item)
        
        return knowledge_items


# 测试代码
if __name__ == "__main__":
    retriever = KnowledgeRetriever()
    results = retriever.retrieve("数据结构 图论")
    for i, result in enumerate(results[:3]):
        print(f"\n知识点 {i+1}: {result['title']}")
        print(f"来源: {result.get('source', '未知')}")
        print(f"内容: {result['content'][:100]}...")