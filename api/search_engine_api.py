#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
搜索引擎API接口
负责调用外部搜索引擎获取最新知识
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from config.settings import load_config

logger = get_logger(__name__)

class SearchEngineAPI:
    """搜索引擎API接口，用于获取最新的知识内容"""
    
    def __init__(self, engine="bing"):
        """初始化搜索引擎API接口
        
        Args:
            engine: 搜索引擎名称，支持bing、google等
        """
        self.engine = engine
        self.config = load_config()
        
        # 加载API密钥
        self.api_keys = {
            "bing": self.config.get("bing_search_key", ""),
            "google": self.config.get("google_search_key", "")
        }
        
        logger.info(f"搜索引擎API接口初始化完成，使用引擎: {engine}")
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """搜索相关知识
        
        Args:
            query: 搜索查询关键词
            max_results: 最大返回结果数量
            
        Returns:
            搜索结果列表，每个结果为字典格式
        """
        logger.info(f"开始搜索: {query}，最大结果数: {max_results}")
        
        # 根据不同搜索引擎调用不同的方法
        if self.engine.lower() == "bing":
            results = self._search_bing(query, max_results)
        elif self.engine.lower() == "google":
            results = self._search_google(query, max_results)
        else:
            logger.warning(f"不支持的搜索引擎: {self.engine}，将使用模拟数据")
            results = self._mock_search_results(query, max_results)
        
        logger.info(f"搜索完成，获取到{len(results)}条结果")
        return results
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Bing搜索引擎搜索
        
        Args:
            query: 搜索查询关键词
            max_results: 最大返回结果数量
            
        Returns:
            搜索结果列表
        """
        api_key = self.api_keys.get("bing")
        if not api_key:
            logger.warning("未配置Bing搜索API密钥，将使用模拟数据")
            return self._mock_search_results(query, max_results)
        
        try:
            # Bing搜索API的URL
            search_url = "https://api.bing.microsoft.com/v7.0/search"
            
            # 设置请求头和参数
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            params = {"q": query, "count": max_results, "textDecorations": True, "textFormat": "HTML"}
            
            # 发送请求
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            # 解析结果
            results = []
            if "webPages" in search_results and "value" in search_results["webPages"]:
                for item in search_results["webPages"]["value"]:
                    results.append({
                        "title": item["name"],
                        "content": item["snippet"],
                        "url": item["url"],
                        "source": "bing_search",
                        "metadata": {
                            "search_engine": "bing",
                            "query": query
                        }
                    })
            
            return results
        except Exception as e:
            logger.error(f"Bing搜索失败: {e}")
            return self._mock_search_results(query, max_results)
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Google搜索引擎搜索
        
        Args:
            query: 搜索查询关键词
            max_results: 最大返回结果数量
            
        Returns:
            搜索结果列表
        """
        # 实际项目中需要实现Google搜索API调用
        # 这里使用模拟数据
        logger.warning("Google搜索API未实现，将使用模拟数据")
        return self._mock_search_results(query, max_results)
    
    def _mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """生成模拟的搜索结果
        
        Args:
            query: 搜索查询关键词
            max_results: 最大返回结果数量
            
        Returns:
            模拟的搜索结果列表
        """
        logger.info(f"生成模拟搜索结果: {query}")
        
        # 数据结构相关的模拟数据
        mock_data = {
            "数据结构": [
                {
                    "title": "数据结构基础概念",
                    "content": "数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。通常情况下，精心选择的数据结构可以带来更高的运行或者存储效率。",
                    "url": "https://example.com/data-structure-basics",
                    "source": "mock_search"
                },
                {
                    "title": "常见数据结构分类",
                    "content": "数据结构主要分为线性结构和非线性结构。线性结构包括数组、链表、栈、队列等；非线性结构包括树、图、堆等。不同的数据结构适用于不同的应用场景。",
                    "url": "https://example.com/data-structure-types",
                    "source": "mock_search"
                }
            ],
            "图论": [
                {
                    "title": "图论基础知识",
                    "content": "图论是数学的一个分支，它以图为研究对象，研究顶点和边组成的图形的数学理论和方法。图论在计算机科学中有广泛应用，如网络流、最短路径、最小生成树等问题。",
                    "url": "https://example.com/graph-theory",
                    "source": "mock_search"
                },
                {
                    "title": "最小生成树算法",
                    "content": "最小生成树是连通加权无向图中一棵权值最小的生成树。常见的最小生成树算法有Kruskal算法和Prim算法，这两种算法都是基于贪心策略实现的。",
                    "url": "https://example.com/minimum-spanning-tree",
                    "source": "mock_search"
                },
                {
                    "title": "最短路径算法",
                    "content": "最短路径问题是图论研究中的一个经典算法问题，旨在寻找图（由结点和路径组成的）中两结点之间的最短路径。常见的最短路径算法有Dijkstra算法、Bellman-Ford算法和Floyd-Warshall算法。",
                    "url": "https://example.com/shortest-path",
                    "source": "mock_search"
                }
            ],
            "树": [
                {
                    "title": "二叉树及其应用",
                    "content": "二叉树是每个节点最多有两个子树的树结构，通常子树被称作左子树和右子树。二叉树常用于实现二叉搜索树和二叉堆，在数据存储、查找和排序等方面有重要应用。",
                    "url": "https://example.com/binary-tree",
                    "source": "mock_search"
                },
                {
                    "title": "平衡二叉树详解",
                    "content": "平衡二叉树是一种特殊的二叉搜索树，其中每个节点的左右子树的高度差最多为1。常见的平衡二叉树有AVL树和红黑树，它们能够保证查找、插入和删除操作的时间复杂度为O(log n)。",
                    "url": "https://example.com/balanced-binary-tree",
                    "source": "mock_search"
                }
            ],
            "排序": [
                {
                    "title": "常见排序算法比较",
                    "content": "排序算法是将一组数据按照特定顺序排列的方法。常见的排序算法包括冒泡排序、选择排序、插入排序、希尔排序、归并排序、快速排序、堆排序等，它们在时间复杂度、空间复杂度和稳定性等方面各有特点。",
                    "url": "https://example.com/sorting-algorithms",
                    "source": "mock_search"
                },
                {
                    "title": "快速排序详解",
                    "content": "快速排序是一种分治策略的排序算法，通过选择一个基准元素，将数组分为两部分，一部分小于基准，一部分大于基准，然后递归地对两部分进行排序。快速排序的平均时间复杂度为O(n log n)，是实际应用中最常用的排序算法之一。",
                    "url": "https://example.com/quicksort",
                    "source": "mock_search"
                }
            ]
        }
        
        # 根据查询关键词选择模拟数据
        results = []
        for key, data in mock_data.items():
            if key in query:
                results.extend(data)
        
        # 如果没有匹配的关键词，返回数据结构的基础数据
        if not results:
            results = mock_data["数据结构"]
        
        # 限制结果数量
        return results[:max_results]


# 测试代码
if __name__ == "__main__":
    search_api = SearchEngineAPI()
    results = search_api.search("数据结构 图论", max_results=3)
    
    print(f"\n搜索结果 ({len(results)} 条):")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['title']}")
        print(f"来源: {result.get('source', '未知')}")
        print(f"内容: {result['content'][:100]}...")
        if 'url' in result:
            print(f"URL: {result['url']}")