#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理工具
负责文件的读写操作，支持纯文本处理
"""

import os
import re
from typing import Dict, List, Any
from datetime import datetime


def read_markdown(file_path: str) -> str:
    """读取Markdown文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""


def write_markdown(file_path: str, content: str) -> bool:
    """写入Markdown文件内容
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        
    Returns:
        是否写入成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False


def compare_markdown(old_content: str, new_content: str) -> Dict[str, Any]:
    """比较两个Markdown文本的差异
    
    Args:
        old_content: 旧内容
        new_content: 新内容
        
    Returns:
        包含差异信息的字典
    """
    # 简单的行级别比较
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    # 计算添加和删除的行数
    added_lines = [line for line in new_lines if line not in old_lines]
    removed_lines = [line for line in old_lines if line not in new_lines]
    
    # 计算标题级别的变化
    old_headers = extract_headers(old_content)
    new_headers = extract_headers(new_content)
    
    added_headers = [h for h in new_headers if h not in old_headers]
    removed_headers = [h for h in old_headers if h not in new_headers]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "added_lines_count": len(added_lines),
        "removed_lines_count": len(removed_lines),
        "added_headers": added_headers,
        "removed_headers": removed_headers,
        "diff_summary": f"添加了{len(added_lines)}行，删除了{len(removed_lines)}行，"
                       f"新增{len(added_headers)}个标题，移除{len(removed_headers)}个标题"
    }


def extract_headers(markdown_text: str) -> List[str]:
    """从Markdown文本中提取标题
    
    Args:
        markdown_text: Markdown文本
        
    Returns:
        标题列表
    """
    # 匹配Markdown标题格式 (# 标题)
    header_pattern = r'^(#{1,6})\s+(.+)$'
    headers = []
    
    for line in markdown_text.split('\n'):
        match = re.match(header_pattern, line)
        if match:
            level = len(match.group(1))  # #的数量表示标题级别
            title = match.group(2).strip()
            headers.append(f"{'#' * level} {title}")
    
    return headers


def parse_markdown_structure(markdown_text: str) -> Dict[str, Any]:
    """解析Markdown文本的结构
    
    Args:
        markdown_text: Markdown文本
        
    Returns:
        解析后的结构字典
    """
    lines = markdown_text.split('\n')
    structure = {
        "title": "",
        "chapters": []
    }
    
    current_chapter = None
    current_section = None
    current_subsection = None
    
    for line in lines:
        # 匹配一级标题 (# 标题)
        if line.startswith('# '):
            structure["title"] = line[2:].strip()
        
        # 匹配二级标题 (## 标题) - 章
        elif line.startswith('## '):
            current_chapter = {
                "title": line[3:].strip(),
                "sections": []
            }
            structure["chapters"].append(current_chapter)
            current_section = None
            current_subsection = None
        
        # 匹配三级标题 (### 标题) - 节
        elif line.startswith('### ') and current_chapter is not None:
            current_section = {
                "title": line[4:].strip(),
                "subsections": []
            }
            current_chapter["sections"].append(current_section)
            current_subsection = None
        
        # 匹配四级标题 (#### 标题) - 小节
        elif line.startswith('#### ') and current_section is not None:
            current_subsection = {
                "title": line[5:].strip(),
                "content": ""
            }
            current_section["subsections"].append(current_subsection)
    
    return structure


# 测试代码
if __name__ == "__main__":
    # 测试读写功能
    test_content = "# 测试标题\n\n## 第一章\n\n这是测试内容。\n"
    write_markdown("test_output.md", test_content)
    read_content = read_markdown("test_output.md")
    print(f"读写测试: {'成功' if read_content == test_content else '失败'}")
    
    # 测试比较功能
    new_content = "# 测试标题\n\n## 第一章\n\n这是测试内容。\n\n## 第二章\n\n新增内容。\n"
    diff = compare_markdown(test_content, new_content)
    print(f"差异比较: {diff['diff_summary']}")