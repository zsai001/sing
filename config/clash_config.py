#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash API配置管理模块
Clash API Configuration Manager
"""

import json
from typing import Dict, Any
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager


class ClashConfigManager(BaseConfigManager):
    """Clash API配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
    
    def load_clash_config(self) -> Dict[str, Any]:
        """加载Clash API配置"""
        if not self.advanced_config_file.exists():
            return {
                "enabled": True,
                "external_controller": "127.0.0.1:9090",
                "external_ui": "ui",
                "secret": "",
                "default_mode": "rule"
            }
        
        try:
            with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("clash_api", {
                    "enabled": True,
                    "external_controller": "127.0.0.1:9090",
                    "external_ui": "ui",
                    "secret": "",
                    "default_mode": "rule"
                })
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "enabled": True,
                "external_controller": "127.0.0.1:9090",
                "external_ui": "ui",
                "secret": "",
                "default_mode": "rule"
            }
    
    def save_clash_config(self, clash_config: Dict[str, Any]):
        """保存Clash API配置"""
        if self.advanced_config_file.exists():
            try:
                with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
        else:
            config = {}
        
        config["clash_api"] = clash_config
        
        try:
            self.advanced_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存Clash API配置失败: {e}")
    
    def configure_clash_api(self):
        """配置Clash API"""
        print()
        print(f"{Colors.CYAN}📡 Clash API 配置{Colors.NC}")
        print("配置Clash兼容API，支持第三方客户端连接")
        print()
        
        clash_config = self.load_clash_config()
        
        print(f"{Colors.YELLOW}当前Clash API配置:{Colors.NC}")
        print(f"  状态: {'启用' if clash_config.get('enabled', True) else '禁用'}")
        if clash_config.get('enabled', True):
            print(f"  控制器地址: {clash_config.get('external_controller', '127.0.0.1:9090')}")
            print(f"  WebUI: {clash_config.get('external_ui', 'ui')}")
            print(f"  密钥: {'已设置' if clash_config.get('secret', '') else '未设置'}")
            print(f"  默认模式: {clash_config.get('default_mode', 'rule')}")
        print()
        
        while True:
            print("配置选项:")
            print("1. 启用/禁用 Clash API")
            print("2. 设置控制器地址")
            print("3. 设置WebUI目录")
            print("4. 设置访问密钥")
            print("5. 设置默认模式")
            print("6. 保存并返回")
            print()
            
            choice = input("请选择 [1-6]: ").strip()
            
            if choice == "1":
                current = clash_config.get('enabled', True)
                toggle = input(f"Clash API当前{'启用' if current else '禁用'}，是否切换? (y/N): ").strip().lower()
                if toggle in ['y', 'yes']:
                    clash_config['enabled'] = not current
                    status = '启用' if not current else '禁用'
                    self.logger.info(f"✓ Clash API已{status}")
                    
            elif choice == "2":
                current_controller = clash_config.get('external_controller', '127.0.0.1:9090')
                new_controller = input(f"设置控制器地址 (当前: {current_controller}): ").strip()
                if new_controller:
                    clash_config['external_controller'] = new_controller
                    self.logger.info(f"✓ 控制器地址设置为: {new_controller}")
                    
            elif choice == "3":
                current_ui = clash_config.get('external_ui', 'ui')
                new_ui = input(f"设置WebUI目录 (当前: {current_ui}): ").strip()
                if new_ui:
                    clash_config['external_ui'] = new_ui
                    self.logger.info(f"✓ WebUI目录设置为: {new_ui}")
                    
            elif choice == "4":
                current_secret = clash_config.get('secret', '')
                print(f"当前密钥: {'已设置' if current_secret else '未设置'}")
                new_secret = input("设置新密钥 (留空不修改): ").strip()
                if new_secret:
                    clash_config['secret'] = new_secret
                    self.logger.info("✓ 访问密钥已更新")
                    
            elif choice == "5":
                current_mode = clash_config.get('default_mode', 'rule')
                print(f"当前默认模式: {current_mode}")
                print("可用模式: rule, global, direct")
                new_mode = input("设置默认模式: ").strip()
                if new_mode in ['rule', 'global', 'direct']:
                    clash_config['default_mode'] = new_mode
                    self.logger.info(f"✓ 默认模式设置为: {new_mode}")
                else:
                    self.logger.error("无效的模式")
                    
            elif choice == "6":
                self.save_clash_config(clash_config)
                self.logger.info("✓ Clash API配置已保存")
                return
            else:
                self.logger.error("无效选项")
    
    def generate_experimental_config(self) -> Dict[str, Any]:
        """根据配置生成实验性功能配置"""
        clash_config = self.load_clash_config()
        
        result = {}
        
        # Clash API配置
        if clash_config.get("enabled", True):
            result["clash_api"] = {
                "external_controller": clash_config.get("external_controller", "127.0.0.1:9090"),
                "external_ui": clash_config.get("external_ui", "ui"),
                "secret": clash_config.get("secret", ""),
                "default_mode": clash_config.get("default_mode", "rule")
            }
        
        # 默认缓存配置
        result["cache_file"] = {
            "enabled": True,
            "path": str(self.paths.config_dir / "cache.db"),
            "cache_id": "default",
            "store_fakeip": False
        }
        
        return result 