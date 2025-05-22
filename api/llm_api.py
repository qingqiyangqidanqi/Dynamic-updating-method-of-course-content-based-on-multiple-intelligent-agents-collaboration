#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大模型API接口
负责调用大模型获取知识补充
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from config.settings import load_config

logger = get_logger(__name__)

class LLMAPI:
    """大模型API接口，用于获取知识补充"""
    
    def __init__(self, model_name="GLM-4"):
        """初始化大模型API接口
        
        Args:
            model_name: 模型名称，支持GLM-4、GPT-4等
        """
        self.model_name = model_name
        self.config = load_config()
        
        # 加载API密钥
        self.api_keys = {
            "openai": self.config.get("openai_api_key", ""),
            "glm": self.config.get("glm_api_key", "")
        }
        
        logger.info(f"大模型API接口初始化完成，使用模型: {model_name}")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本
        """
        logger.info(f"开始生成文本，使用模型: {self.model_name}，提示词长度: {len(prompt)}")
        
        # 根据不同模型调用不同的方法
        if "gpt" in self.model_name.lower():
            response = self._call_openai(prompt, max_tokens)
        elif "glm" in self.model_name.lower():
            response = self._call_glm(prompt, max_tokens)
        else:
            logger.warning(f"不支持的模型: {self.model_name}，将使用模拟数据")
            response = self._mock_response(prompt)
        
        logger.info(f"文本生成完成，生成长度: {len(response)}")
        return response
    
    def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """调用OpenAI API
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本
        """
        api_key = self.api_keys.get("openai")
        if not api_key:
            logger.warning("未配置OpenAI API密钥，将使用模拟数据")
            return self._mock_response(prompt)
        
        try:
            # OpenAI API的URL
            api_url = "https://api.openai.com/v1/chat/completions"
            
            # 设置请求头和参数
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            data = {
                "model": "gpt-4" if "4" in self.model_name else "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "你是一个专业的教育内容生成助手，擅长生成结构化的教学知识点。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # 发送请求
            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # 解析结果
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API返回异常: {result}")
                return self._mock_response(prompt)
        except Exception as e:
            logger.error(f"调用OpenAI API失败: {e}")
            return self._mock_response(prompt)
    
    def _call_glm(self, prompt: str, max_tokens: int) -> str:
        """调用智谱GLM API
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本
        """
        # 实际项目中需要实现GLM API调用
        # 这里使用模拟数据
        logger.warning("GLM API未实现，将使用模拟数据")
        return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """生成模拟的响应
        
        Args:
            prompt: 提示词
            
        Returns:
            模拟的响应文本
        """
        logger.info("生成模拟响应")
        
        # 根据提示词中的关键词生成不同的模拟响应
        if "数据结构" in prompt:
            if "图论" in prompt:
                return self._mock_graph_theory()
            elif "树" in prompt:
                return self._mock_tree()
            elif "排序" in prompt:
                return self._mock_sorting()
            else:
                return self._mock_data_structure()
        else:
            return "这是一个模拟的大模型响应。在实际项目中，这里会返回真实的大模型生成内容。"
    
    def _mock_data_structure(self) -> str:
        """生成数据结构相关的模拟响应"""
        return """
# 数据结构基础知识

## 数据结构的定义
数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。通常情况下，精心选择的数据结构可以带来更高的运行或者存储效率。

## 数据结构的分类
数据结构主要分为线性结构和非线性结构：
- 线性结构：数组、链表、栈、队列等
- 非线性结构：树、图、堆等

## 算法复杂度分析
算法复杂度通常用大O符号表示，常见的时间复杂度有：
- O(1)：常数时间复杂度
- O(log n)：对数时间复杂度
- O(n)：线性时间复杂度
- O(n log n)：线性对数时间复杂度
- O(n²)：平方时间复杂度
- O(2^n)：指数时间复杂度

## 考研重点
数据结构在考研中的重点内容包括：
1. 线性表的各种操作及实现
2. 栈和队列的应用
3. 树的遍历算法
4. 图的最短路径和最小生成树
5. 各种排序算法的比较
6. 查找算法的效率分析
"""
    
    def _mock_graph_theory(self) -> str:
        """生成图论相关的模拟响应"""
        return """
# 图论基础知识

## 图的基本概念
图(Graph)是由顶点的有穷非空集合和顶点之间边的集合组成，通常表示为G(V, E)，其中，G表示一个图，V表示顶点的集合，E表示边的集合。

## 图的表示方法
1. 邻接矩阵：使用二维数组表示顶点之间的连接关系
2. 邻接表：每个顶点对应一个链表，链表中存储与该顶点相邻的顶点

## 图的遍历
### 深度优先搜索(DFS)
深度优先搜索是一种用于遍历或搜索树或图的算法。沿着树的深度遍历树的节点，尽可能深的搜索树的分支。当节点v的所有边都已被探寻过，搜索将回溯到发现节点v的那条边的起始节点。

### 广度优先搜索(BFS)
广度优先搜索是一种用于遍历或搜索树或图的算法。从根节点开始，沿着树的宽度遍历树的节点。如果所有节点均被访问，则算法中止。

## 最小生成树
最小生成树是连通加权无向图中一棵权值最小的生成树。

### Kruskal算法
Kruskal算法是一种用来寻找最小生成树的算法，基于贪心策略，按权值从小到大加入边，如果该边不会与已加入的边构成环，则加入，否则舍弃。

### Prim算法
Prim算法也是一种用来寻找最小生成树的算法，从任意一个顶点开始，每次选择一个与当前最小生成树顶点集相邻的权值最小的边，将对应的顶点加入到最小生成树顶点集中。

## 最短路径
### Dijkstra算法
Dijkstra算法是一种用于计算从单个源顶点到其他所有顶点的最短路径的算法，适用于边权值为非负数的情况。

### Bellman-Ford算法
Bellman-Ford算法是一种用于计算从单个源顶点到其他所有顶点的最短路径的算法，可以处理边权值为负数的情况，但不能处理负权环。

### Floyd-Warshall算法
Floyd-Warshall算法是一种用于计算所有顶点对之间的最短路径的算法，可以处理边权值为负数的情况，但不能处理负权环。

## 考研重点
图论在考研中的重点内容包括：
1. 图的存储结构（邻接矩阵和邻接表）
2. 图的遍历（DFS和BFS）
3. 最小生成树（Kruskal和Prim算法）
4. 最短路径（Dijkstra和Floyd算法）
5. 拓扑排序
6. 关键路径
"""
    
    def _mock_tree(self) -> str:
        """生成树相关的模拟响应"""
        return """
# 树与二叉树

## 树的基本概念
树是n个节点的有限集合，有一个特殊的节点称为根节点，其余节点可以分为m个互不相交的有限集合，每个集合本身又是一棵树，称为原树的子树。

## 二叉树的定义
二叉树是每个节点最多有两个子树的树结构，通常子树被称作左子树和右子树。

## 二叉树的性质
1. 在二叉树的第i层上至多有2^(i-1)个节点
2. 深度为k的二叉树至多有2^k-1个节点
3. 对任何一棵二叉树，如果其叶节点数为n0，度为2的节点数为n2，则n0=n2+1

## 二叉树的遍历
### 先序遍历
先访问根节点，然后先序遍历左子树，最后先序遍历右子树。

### 中序遍历
先中序遍历左子树，然后访问根节点，最后中序遍历右子树。

### 后序遍历
先后序遍历左子树，然后后序遍历右子树，最后访问根节点。

### 层序遍历
从根节点开始，按照从上到下、从左到右的顺序访问每个节点。

## 线索二叉树
线索二叉树是一种利用二叉树中的空指针域来存放指向该节点在某种遍历次序下的前驱和后继的指针的二叉树。

## 哈夫曼树
哈夫曼树是一种带权路径长度最短的二叉树，也称为最优二叉树。

### 哈夫曼编码
哈夫曼编码是一种基于哈夫曼树的编码方式，用于数据压缩。

## 考研重点
树与二叉树在考研中的重点内容包括：
1. 二叉树的性质和存储结构
2. 二叉树的各种遍历算法及应用
3. 线索二叉树的概念和实现
4. 哈夫曼树和哈夫曼编码
5. 树和森林与二叉树的转换
"""
    
    def _mock_sorting(self) -> str:
        """生成排序相关的模拟响应"""
        return """
# 排序算法

## 排序的基本概念
排序是将一组数据按照特定顺序排列的过程。排序算法的稳定性是指相等的元素在排序后相对位置不变。

## 插入排序
### 直接插入排序
直接插入排序的基本思想是将一个记录插入到已经排好序的有序表中，从而得到一个新的、记录数增加1的有序表。

### 希尔排序
希尔排序是插入排序的一种改进版本，它通过将整个序列分为若干个子序列，对每个子序列进行直接插入排序，逐步缩小增量，最终完成排序。

## 交换排序
### 冒泡排序
冒泡排序是一种简单的排序算法，它重复地遍历要排序的数列，一次比较两个元素，如果他们的顺序错误就把他们交换过来。

### 快速排序
快速排序是一种分治策略的排序算法，通过选择一个基准元素，将数组分为两部分，一部分小于基准，一部分大于基准，然后递归地对两部分进行排序。

## 选择排序
### 简单选择排序
简单选择排序的基本思想是每次从待排序的数据中选出最小（或最大）的一个元素，存放在序列的起始位置，直到全部待排序的数据元素排完。

### 堆排序
堆排序是利用堆这种数据结构所设计的一种排序算法，堆是一个近似完全二叉树的结构，并同时满足堆的性质：子节点的值总是小于（或大于）它的父节点。

## 归并排序
归并排序是建立在归并操作上的一种有效的排序算法，该算法是采用分治法的一个非常典型的应用。

## 基数排序
基数排序是一种非比较型整数排序算法，其原理是将整数按位数切割成不同的数字，然后按每个位数分别比较。

## 各种排序算法的比较
| 排序算法 | 平均时间复杂度 | 最坏时间复杂度 | 空间复杂度 | 稳定性 |
| --- | --- | --- | --- | --- |
| 直接插入排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 希尔排序 | O(n^1.3) | O(n²) | O(1) | 不稳定 |
| 冒泡排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 快速排序 | O(n log n) | O(n²) | O(log n) | 不稳定 |
| 简单选择排序 | O(n²) | O(n²) | O(1) | 不稳定 |
| 堆排序 | O(n log n) | O(n log n) | O(1) | 不稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | 稳定 |
| 基数排序 | O(d(n+r)) | O(d(n+r)) | O(r) | 稳定 |

## 考研重点
排序算法在考研中的重点内容包括：
1. 各种排序算法的基本思想和实现
2. 排序算法的时间复杂度和空间复杂度分析
3. 排序算法的稳定性
4. 内部排序和外部排序的区别
5. 快速排序、堆排序和归并排序的详细过程
"""


# 测试代码
if __name__ == "__main__":
    llm_api = LLMAPI()
    response = llm_api.generate("请提供关于数据结构中图论的知识点")
    
    print("\n生成的文本:")
    print(response[:300] + "...")