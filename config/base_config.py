#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础配置管理模块
Base Configuration Manager
"""

import json
from pathlib import Path
from typing import Dict, Any
from utils import Colors, Logger
from paths import PathManager


class BaseConfigManager:
    """基础配置管理类，提供通用的配置管理功能"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
        self.config_file = self.paths.config_dir / "config.json"
    
    def load_sing_box_config(self) -> Dict[str, Any]:
        """加载 sing-box 配置文件"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"读取 sing-box 配置失败: {e}")
            return {}
    
    def save_sing_box_config(self, config: Dict[str, Any]):
        """保存 sing-box 配置文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存 sing-box 配置失败: {e}")
            raise
    
    def save_config_and_restart(self, config: Dict[str, Any], message: str):
        """保存配置并根据服务状态决定是否重启"""
        try:
            self.save_sing_box_config(config)
            
            # 检查服务是否运行
            from service import ServiceManager
            service_manager = ServiceManager(self.paths, self.logger)
            is_running, _ = service_manager.check_service_status()
            
            if is_running:
                print()
                print(f"{Colors.YELLOW}检测到服务正在运行，正在重启以应用新配置...{Colors.NC}")
                
                # 重启服务
                success = service_manager.restart_service()
                if success:
                    self.logger.info(f"✓ {message}，服务已重启")
                else:
                    self.logger.error(f"✓ {message}，但服务重启失败")
            else:
                self.logger.info(f"✓ {message}，配置已保存")
                print(f"{Colors.YELLOW}提示: 服务未运行，配置将在下次启动时生效{Colors.NC}")
                
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}") 