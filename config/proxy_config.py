#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理端口配置管理模块
Proxy Port Configuration Manager
"""

import json
from typing import Dict, Any, List
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager


class ProxyConfigManager(BaseConfigManager):
    """代理端口配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
    
    def load_proxy_config(self) -> Dict[str, Any]:
        """加载代理端口配置"""
        if not self.advanced_config_file.exists():
            return {
                "mixed_port": 7890,
                "http_port": 7891,
                "socks_port": 7892,
                "enabled": ["mixed"]
            }
        
        try:
            with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("proxy_ports", {
                    "mixed_port": 7890,
                    "http_port": 7891,
                    "socks_port": 7892,
                    "enabled": ["mixed"]
                })
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "mixed_port": 7890,
                "http_port": 7891,
                "socks_port": 7892,
                "enabled": ["mixed"]
            }
    
    def save_proxy_config(self, proxy_config: Dict[str, Any]):
        """保存代理端口配置"""
        if self.advanced_config_file.exists():
            try:
                with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
        else:
            config = {}
        
        config["proxy_ports"] = proxy_config
        
        try:
            self.advanced_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存代理端口配置失败: {e}")
    
    def configure_proxy_ports(self):
        """配置代理端口"""
        print()
        print(f"{Colors.CYAN}🔗 代理端口配置{Colors.NC}")
        print("管理混合端口、HTTP端口、SOCKS端口等代理入站设置")
        print()
        
        proxy_config = self.load_proxy_config()
        
        print(f"{Colors.YELLOW}当前配置:{Colors.NC}")
        print(f"  混合端口: {proxy_config.get('mixed_port', 7890)}")
        print(f"  HTTP端口: {proxy_config.get('http_port', 7891)}")
        print(f"  SOCKS端口: {proxy_config.get('socks_port', 7892)}")
        print(f"  启用端口: {', '.join(proxy_config.get('enabled', ['mixed']))}")
        print()
        
        while True:
            print("配置选项:")
            print("1. 设置混合端口")
            print("2. 设置HTTP端口")
            print("3. 设置SOCKS端口")
            print("4. 启用/禁用端口类型")
            print("5. 保存并返回")
            print()
            
            choice = input("请选择 [1-5]: ").strip()
            
            if choice == "1":
                try:
                    port = int(input(f"设置混合端口 (当前: {proxy_config.get('mixed_port', 7890)}): ").strip())
                    proxy_config['mixed_port'] = port
                    self.logger.info(f"✓ 混合端口设置为: {port}")
                except ValueError:
                    self.logger.error("端口必须是数字")
                    
            elif choice == "2":
                try:
                    port = int(input(f"设置HTTP端口 (当前: {proxy_config.get('http_port', 7891)}): ").strip())
                    proxy_config['http_port'] = port
                    self.logger.info(f"✓ HTTP端口设置为: {port}")
                except ValueError:
                    self.logger.error("端口必须是数字")
                    
            elif choice == "3":
                try:
                    port = int(input(f"设置SOCKS端口 (当前: {proxy_config.get('socks_port', 7892)}): ").strip())
                    proxy_config['socks_port'] = port
                    self.logger.info(f"✓ SOCKS端口设置为: {port}")
                except ValueError:
                    self.logger.error("端口必须是数字")
                    
            elif choice == "4":
                print("可用类型: mixed, http, socks")
                enabled_input = input("输入要启用的端口类型 (用逗号分隔): ").strip()
                valid_types = []
                for port_type in enabled_input.split(','):
                    port_type = port_type.strip()
                    if port_type in ['mixed', 'http', 'socks']:
                        valid_types.append(port_type)
                
                if valid_types:
                    proxy_config['enabled'] = valid_types
                    self.logger.info(f"✓ 已启用端口类型: {', '.join(valid_types)}")
                else:
                    self.logger.error("无效的端口类型")
                    
            elif choice == "5":
                self.save_proxy_config(proxy_config)
                self.logger.info("✓ 代理端口配置已保存")
                return
            else:
                self.logger.error("无效选项")
    
    def generate_inbounds_config(self) -> List[Dict[str, Any]]:
        """根据代理配置生成入站配置"""
        proxy_config = self.load_proxy_config()
        enabled_ports = proxy_config.get("enabled", ["mixed"])
        
        inbounds = []
        
        if "mixed" in enabled_ports:
            inbounds.append({
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "127.0.0.1",
                "listen_port": proxy_config.get("mixed_port", 7890),
                "sniff": True,
                "sniff_override_destination": True
            })
        
        if "http" in enabled_ports:
            inbounds.append({
                "type": "http",
                "tag": "http-in", 
                "listen": "127.0.0.1",
                "listen_port": proxy_config.get("http_port", 7891),
                "sniff": True,
                "sniff_override_destination": True
            })
        
        if "socks" in enabled_ports:
            inbounds.append({
                "type": "socks",
                "tag": "socks-in",
                "listen": "127.0.0.1", 
                "listen_port": proxy_config.get("socks_port", 7892),
                "sniff": True,
                "sniff_override_destination": True
            })
        
        return inbounds 