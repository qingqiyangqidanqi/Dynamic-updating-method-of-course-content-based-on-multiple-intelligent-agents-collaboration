#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
负责系统运行时的日志记录
"""

import os
import sys
import logging
from datetime import datetime

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger(name=None, level="info", log_file=None, log_format=None):
    """设置日志记录器
    
    Args:
        name: 日志记录器名称，默认为根记录器
        level: 日志级别，可选值：debug, info, warning, error, critical
        log_file: 日志文件路径，如果为None则输出到控制台
        log_format: 日志格式，如果为None则使用默认格式
        
    Returns:
        配置好的日志记录器
    """
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    logger.setLevel(log_level)
    
    # 清除现有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建处理器
    if log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler = logging.FileHandler(log_file, encoding='utf-8')
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    # 设置格式
    formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(handler)
    
    return logger


def get_logger(name=None):
    """获取已配置的日志记录器，如果不存在则创建一个新的
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果记录器没有处理器，则进行配置
    if not logger.handlers:
        # 创建logs目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{today}.log")
        
        return setup_logger(name, log_file=log_file)
    
    return logger


# 测试代码
if __name__ == "__main__":
    # 测试日志记录
    logger = get_logger("test")
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    
    print("日志测试完成")