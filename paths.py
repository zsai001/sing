#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
路径管理模块 - 跨平台路径处理
SingTool Paths Module
"""

import platform
from pathlib import Path

class PathManager:
    """路径管理类 - 处理跨平台路径配置"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.arch = platform.machine()
        self._setup_paths()
    
    def _setup_paths(self):
        """设置平台特定的路径"""
        if self.os_type == "Darwin":
            # macOS 路径配置
            self.config_dir = Path.home() / ".config/sing-box"
            self.log_dir = Path.home() / ".local/share/sing-box/logs"
            self.service_name = "com.singtool.sing-box"
            self.plist_path = Path.home() / f"Library/LaunchAgents/{self.service_name}.plist"
            
            # Intel vs Apple Silicon 二进制路径
            if self.arch == "x86_64":
                self.sing_box_bin = "/usr/local/bin/sing-box"
            else:
                self.sing_box_bin = "/opt/homebrew/bin/sing-box"
        else:
            # Linux 路径配置（兼容）
            self.config_dir = Path("/etc/sing-box")
            self.log_dir = Path("/var/log/sing-box")
            self.service_name = "sing-box"
            self.plist_path = None
            self.sing_box_bin = "sing-box"
        
        # 节点管理相关路径
        self.nodes_dir = self.config_dir / "nodes"
        self.nodes_config = self.config_dir / "nodes.json"
        self.backup_dir = self.config_dir / "backup"
        
        # 本地代理配置路径
        self.local_config = self.config_dir / "local_proxy.json"
        self.dns_config = self.config_dir / "dns_rules.json"
        self.main_config = self.config_dir / "config.json" 