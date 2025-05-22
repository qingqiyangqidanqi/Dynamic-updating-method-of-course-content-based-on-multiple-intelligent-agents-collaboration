#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
课程更新工程师模块
负责根据权重化的知识点生成更新后的课程内容
"""

import os
import sys
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from utils.file_handler import read_markdown, write_markdown

logger = get_logger(__name__)

class CourseEngineer:
    """课程更新工程师，负责生成更新后的课程内容"""
    
    def __init__(self, template_path):
        """初始化课程更新工程师
        
        Args:
            template_path: 课程模板文件路径
        """
        self.template_path = template_path
        self.template = self._load_template(template_path)
        self.chapter_mapping = self._build_chapter_mapping()
        logger.info(f"课程更新工程师初始化完成，使用模板: {template_path}")
    
    def _load_template(self, template_path):
        """加载课程模板
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            解析后的模板结构
        """
        try:
            content = read_markdown(template_path)
            return content
        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            # 返回空字符串作为默认值
            return ""
    
    def _build_chapter_mapping(self):
        """构建知识点到章节的映射关系
        
        Returns:
            知识点关键词到章节的映射字典
        """
        # 基于数据结构课程内容构建映射
        return {
            # 第1章 绪论
            "算法": "1.2",
            "数据结构基本概念": "1.1",
            "时间复杂度": "1.2",
            "空间复杂度": "1.2",
            
            # 第2章 线性表
            "线性表": "2.1",
            "顺序表": "2.2",
            "链表": "2.3",
            "单链表": "2.3",
            "双链表": "2.3",
            "循环链表": "2.3",
            "静态链表": "2.3",
            
            # 第3章 栈、队列和数组
            "栈": "3.1",
            "队列": "3.2",
            "双端队列": "3.2",
            "数组": "3.4",
            "矩阵": "3.4",
            "特殊矩阵": "3.4",
            "稀疏矩阵": "3.4",
            "表达式求值": "3.3",
            "递归": "3.3",
            
            # 第4章 串
            "串": "4.1",
            "字符串": "4.1",
            "模式匹配": "4.2",
            "KMP算法": "4.2",
            
            # 第5章 树与二叉树
            "树": "5.1",
            "二叉树": "5.2",
            "遍历": "5.3",
            "线索二叉树": "5.3",
            "森林": "5.4",
            "哈夫曼树": "5.5",
            "哈夫曼编码": "5.5",
            "并查集": "5.5",
            
            # 第6章 图
            "图": "6.1",
            "邻接矩阵": "6.2",
            "邻接表": "6.2",
            "十字链表": "6.2",
            "邻接多重表": "6.2",
            "广度优先搜索": "6.3",
            "深度优先搜索": "6.3",
            "最小生成树": "6.4",
            "最短路径": "6.4",
            "拓扑排序": "6.4",
            "关键路径": "6.4",
            
            # 第7章 查找
            "查找": "7.1",
            "顺序查找": "7.2",
            "折半查找": "7.2",
            "分块查找": "7.2",
            "二叉排序树": "7.3",
            "平衡二叉树": "7.3",
            "红黑树": "7.3",
            "B树": "7.4",
            "B+树": "7.4",
            "散列表": "7.5",
            "哈希表": "7.5",
            
            # 第8章 排序
            "排序": "8.1",
            "插入排序": "8.2",
            "希尔排序": "8.2",
            "冒泡排序": "8.3",
            "快速排序": "8.3",
            "选择排序": "8.4",
            "堆排序": "8.4",
            "归并排序": "8.5",
            "基数排序": "8.5",
            "计数排序": "8.5",
            "外部排序": "8.7"
        }
    
    def update(self, weighted_topics: List[Dict[str, Any]]) -> str:
        """根据权重化的知识点更新课程内容
        
        Args:
            weighted_topics: 权重化的知识点列表
            
        Returns:
            更新后的课程内容文本
        """
        logger.info(f"开始更新课程内容，共有{len(weighted_topics)}个知识点")
        
        # 1. 按章节组织知识点
        chapter_content = self._organize_by_chapter(weighted_topics)
        
        # 2. 生成更新后的课程内容
        updated_content = self._generate_content(chapter_content)
        
        logger.info("课程内容更新完成")
        return updated_content
    
    def _organize_by_chapter(self, topics: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """将知识点按章节组织
        
        Args:
            topics: 权重化的知识点列表
            
        Returns:
            按章节组织的知识点字典
        """
        # 初始化章节内容字典
        chapter_content = {}
        
        # 遍历每个知识点，分配到对应章节
        for topic in topics:
            chapter = self._determine_chapter(topic)
            if chapter not in chapter_content:
                chapter_content[chapter] = []
            chapter_content[chapter].append(topic)
        
        # 对每个章节内的知识点按权重排序
        for chapter in chapter_content:
            chapter_content[chapter] = sorted(
                chapter_content[chapter], 
                key=lambda x: x.get("weight", 0), 
                reverse=True
            )
        
        return chapter_content
    
    def _determine_chapter(self, topic: Dict[str, Any]) -> str:
        """确定知识点应该属于哪个章节
        
        Args:
            topic: 知识点字典
            
        Returns:
            章节编号，如"1.1"
        """
        # 默认章节
        default_chapter = "1.1"
        
        # 合并标题和内容用于匹配
        text = f"{topic.get('title', '')} {topic.get('content', '')}"
        
        # 尝试匹配最具体的关键词
        best_match = None
        best_match_len = 0
        
        for keyword, chapter in self.chapter_mapping.items():
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                if len(keyword) > best_match_len:
                    best_match = chapter
                    best_match_len = len(keyword)
        
        return best_match or default_chapter
    
    def _generate_content(self, chapter_content: Dict[str, List[Dict[str, Any]]]) -> str:
        """生成更新后的课程内容
        
        Args:
            chapter_content: 按章节组织的知识点字典
            
        Returns:
            更新后的课程内容文本
        """
        # 如果模板为空，创建一个基本结构
        if not self.template:
            output = "# 数据结构课程更新内容\n\n"
            output += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # 按章节顺序添加内容
            for chapter in sorted(chapter_content.keys()):
                topics = chapter_content[chapter]
                if not topics:
                    continue
                
                # 添加章节标题
                chapter_parts = chapter.split('.')
                if len(chapter_parts) >= 2:
                    main_chapter = chapter_parts[0]
                    sub_chapter = '.'.join(chapter_parts[1:])
                    
                    # 查找章节名称
                    chapter_name = self._find_chapter_name(main_chapter, sub_chapter)
                    output += f"## {chapter} {chapter_name}\n\n"
                else:
                    output += f"## 章节 {chapter}\n\n"
                
                # 添加知识点内容
                for topic in topics:
                    weight = topic.get("weight", 0)
                    title = topic.get("title", "未命名知识点")
                    content = topic.get("content", "")
                    source = topic.get("source", "未知来源")
                    
                    output += f"### {title} [权重:{weight:.2f}]\n\n"
                    output += f"{content}\n\n"
                    output += f"*来源: {source}*\n\n"
            
            return output
        else:
            # 基于现有模板生成更新内容
            output = "# 数据结构课程更新内容\n\n"
            output += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            output += "## 更新摘要\n\n"
            output += "本次更新基于最新教学资源和考研真题，对以下章节进行了内容补充和优化：\n\n"
            
            # 添加更新摘要
            for chapter in sorted(chapter_content.keys()):
                topics = chapter_content[chapter]
                if not topics:
                    continue
                
                # 查找章节名称
                chapter_parts = chapter.split('.')
                if len(chapter_parts) >= 2:
                    main_chapter = chapter_parts[0]
                    sub_chapter = '.'.join(chapter_parts[1:])
                    chapter_name = self._find_chapter_name(main_chapter, sub_chapter)
                    
                    # 添加章节更新摘要
                    topic_count = len(topics)
                    top_topic = topics[0] if topics else None
                    if top_topic:
                        output += f"- **{chapter} {chapter_name}**: 新增{topic_count}个知识点，"
                        output += f"重点包括《{top_topic.get('title', '')}》(权重:{top_topic.get('weight', 0):.2f})\n"
            
            output += "\n## 详细更新内容\n\n"
            
            # 按章节添加详细内容
            for chapter in sorted(chapter_content.keys()):
                topics = chapter_content[chapter]
                if not topics:
                    continue
                
                # 添加章节标题
                chapter_parts = chapter.split('.')
                if len(chapter_parts) >= 2:
                    main_chapter = chapter_parts[0]
                    sub_chapter = '.'.join(chapter_parts[1:])
                    chapter_name = self._find_chapter_name(main_chapter, sub_chapter)
                    output += f"### {chapter} {chapter_name}\n\n"
                else:
                    output += f"### 章节 {chapter}\n\n"
                
                # 添加知识点内容
                for topic in topics:
                    weight = topic.get("weight", 0)
                    title = topic.get("title", "未命名知识点")
                    content = topic.get("content", "")
                    source = topic.get("source", "未知来源")
                    
                    # 标记高权重知识点
                    weight_marker = ""
                    if weight > 0.7:
                        weight_marker = "⭐⭐⭐ 高频考点"
                    elif weight > 0.5:
                        weight_marker = "⭐⭐ 重要知识点"
                    elif weight > 0.3:
                        weight_marker = "⭐ 基础知识点"
                    
                    output += f"#### {title} {weight_marker}\n\n"
                    output += f"{content}\n\n"
                    output += f"*权重: {weight:.2f}, 来源: {source}*\n\n"
            
            return output
    
    def _find_chapter_name(self, main_chapter: str, sub_chapter: str) -> str:
        """查找章节名称
        
        Args:
            main_chapter: 主章节编号
            sub_chapter: 子章节编号
            
        Returns:
            章节名称
        """
        # 硬编码章节名称映射
        chapter_names = {
            "1": {
                "1": "数据结构的基本概念",
                "2": "算法和算法评价"
            },
            "2": {
                "1": "线性表的定义和基本操作",
                "2": "线性表的顺序表示",
                "3": "线性表的链式表示"
            },
            "3": {
                "1": "栈",
                "2": "队列",
                "3": "栈和队列的应用",
                "4": "数组和特殊矩阵"
            },
            "4": {
                "1": "串的定义和实现",
                "2": "串的模式匹配"
            },
            "5": {
                "1": "树的基本概念",
                "2": "二叉树的概念",
                "3": "二叉树的遍历和线索二叉树",
                "4": "树、森林",
                "5": "树与二叉树的应用"
            },
            "6": {
                "1": "图的基本概念",
                "2": "图的存储及基本操作",
                "3": "图的遍历",
                "4": "图的应用"
            },
            "7": {
                "1": "查找的基本概念",
                "2": "顺序查找和折半查找",
                "3": "树形查找",
                "4": "B树和B+树",
                "5": "散列表"
            },
            "8": {
                "1": "排序的基本概念",
                "2": "插入排序",
                "3": "交换排序",
                "4": "选择排序",
                "5": "归并排序、基数排序和计数排序",
                "6": "各种内部排序算法的比较及应用",
                "7": "外部排序"
            }
        }
        
        # 尝试查找章节名称
        if main_chapter in chapter_names and sub_chapter in chapter_names[main_chapter]:
            return chapter_names[main_chapter][sub_chapter]
        
        return "未知章节"


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = [
        {"title": "最小生成树算法", "content": "最小生成树是连通加权无向图中一棵权值最小的生成树。常见算法有Kruskal和Prim算法。", "source": "textbook", "weight": 0.85},
        {"title": "Kruskal算法详解", "content": "Kruskal算法是一种用来寻找最小生成树的算法，基于贪心策略，按权值从小到大加入边。", "source": "lecture", "weight": 0.75},
        {"title": "图的遍历方法", "content": "图的遍历主要有两种方法：深度优先搜索(DFS)和广度优先搜索(BFS)。", "source": "exam", "weight": 0.9},
    ]
    
    engineer = CourseEngineer(template_path="data/data_struct.md")
    result = engineer.update(test_data)
    
    print("\n更新后的课程内容预览:\n")
    print(result[:500] + "...")