#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
动态课程内容更新系统主程序
基于多智能体协作的纯文本处理方案
"""

import os
import sys
from agents.knowledge_retriever import KnowledgeRetriever
from agents.teaching_analyzer import TeachingAnalyzer
from agents.course_engineer import CourseEngineer
from utils.logger import setup_logger
from config.settings import load_config

# 设置日志
logger = setup_logger()

def main():
    # 加载配置
    config = load_config()
    logger.info("系统初始化完成，开始课程更新流程")
    
    # 初始化模块
    retriever = KnowledgeRetriever(llm_api=config.get("llm_api", "GLM-4"))
    analyzer = TeachingAnalyzer(weight_rules=config.get("weight_rules", {
        "考研真题": 0.7, 
        "高频考点": 0.5,
        "算法复杂度": 0.6,
        "数据结构基础": 0.4
    }))
    engineer = CourseEngineer(template_path="data/data_struct.md")
    
    # 执行流程
    search_query = input("请输入需要更新的课程内容关键词(如'数据结构 图论'): ")
    logger.info(f"开始检索知识: {search_query}")
    
    # 知识检索
    raw_knowledge = retriever.retrieve(search_query)
    logger.info(f"检索到{len(raw_knowledge)}条相关知识")
    
    # 知识分析与权重计算
    weighted_topics = analyzer.analyze(raw_knowledge)
    logger.info(f"完成知识分析，共有{len(weighted_topics)}个权重化主题")
    
    # 课程内容更新
    updated_text = engineer.update(weighted_topics)
    logger.info("课程内容更新完成")
    
    # 保存结果
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "course_update.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_text)
    
    logger.info(f"更新后的课程内容已保存至: {output_path}")
    print(f"\n更新完成! 文件已保存至: {output_path}")

if __name__ == "__main__":
    main()