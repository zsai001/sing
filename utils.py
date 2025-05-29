#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块 - 颜色定义和日志管理
SingTool Utils Module
"""

class Colors:
    """终端颜色定义"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class Logger:
    """日志管理类"""
    
    @staticmethod
    def info(message):
        """显示信息日志"""
        print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")
    
    @staticmethod
    def warn(message):
        """显示警告日志"""
        print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")
    
    @staticmethod
    def error(message):
        """显示错误日志"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    @staticmethod
    def step(message):
        """显示步骤日志"""
        print(f"{Colors.BLUE}[STEP]{Colors.NC} {message}") 