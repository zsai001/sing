#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块 - sing-box 配置文件生成和管理
SingTool Config Module
"""

import json
import socket
from pathlib import Path
from typing import Dict, Any, List
from utils import Colors, Logger
from paths import PathManager

class ConfigManager:
    """配置管理类 - 负责生成和管理 sing-box 配置文件"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
    
    def ensure_config_directories(self):
        """确保配置目录存在"""
        for dir_path in [self.paths.config_dir, self.paths.log_dir, 
                        self.paths.backup_dir, self.paths.nodes_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        self.logger.info("✓ 配置目录检查完成")
    
    def generate_local_proxy_config(self, selected_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成本地代理配置（客户端模式）"""
        if not selected_nodes:
            self.logger.error("未选择节点")
            return {}
        
        # 外出连接配置
        outbounds = []
        
        # 添加选择的节点
        for node in selected_nodes:
            if node['type'] == 'trojan':
                outbound = {
                    "type": "trojan",
                    "tag": node['name'],
                    "server": node['server'],
                    "server_port": node['port'],
                    "password": node['password'],
                    "tls": {
                        "enabled": True,
                        "server_name": node.get('sni', node['server']),
                        "insecure": node.get('skip_cert_verify', True)
                    }
                }
                
                # 添加WebSocket传输配置
                if 'transport' in node and node['transport'].get('type') == 'ws':
                    outbound["transport"] = {
                        "type": "ws",
                        "path": node['transport'].get('path', '/'),
                        "headers": node['transport'].get('headers', {})
                    }
                    
            elif node['type'] == 'vless':
                outbound = {
                    "type": "vless",
                    "tag": node['name'],
                    "server": node['server'],
                    "server_port": node['port'],
                    "uuid": node['uuid'],
                    "flow": node.get('flow', ''),
                    "tls": {
                        "enabled": True,
                        "server_name": node.get('sni', node['server']),
                        "insecure": node.get('skip_cert_verify', True)
                    }
                }
                
                # 添加传输配置
                if 'transport' in node:
                    if node['transport'].get('type') == 'ws':
                        outbound["transport"] = {
                            "type": "ws",
                            "path": node['transport'].get('path', '/'),
                            "headers": node['transport'].get('headers', {})
                        }
                    elif node['transport'].get('type') == 'grpc':
                        outbound["transport"] = {
                            "type": "grpc",
                            "service_name": node['transport'].get('service_name', '')
                        }
                        
            elif node['type'] == 'shadowsocks':
                outbound = {
                    "type": "shadowsocks",
                    "tag": node['name'],
                    "server": node['server'],
                    "server_port": node['port'],
                    "method": node['method'],
                    "password": node['password']
                }
            else:
                continue
            
            outbounds.append(outbound)
        
        # 添加 direct 和 block 出站
        outbounds.extend([
            {"type": "direct", "tag": "direct"},
            {"type": "block", "tag": "block"}
        ])
        
        # 生成选择器配置
        proxy_tags = [node['name'] for node in selected_nodes]
        selector_outbound = {
            "type": "selector",
            "tag": "🚀 节点选择",
            "outbounds": proxy_tags + ["direct"]
        }
        outbounds.insert(0, selector_outbound)
        
        # 生成入站配置
        inbounds = [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "127.0.0.1",
                "listen_port": 7890,
                "sniff": True,
                "sniff_override_destination": True
            }
        ]
        
        # 生成路由规则（移除已弃用的geoip和geosite）
        route_rules = [
            {"ip_cidr": ["224.0.0.0/3", "ff00::/8"], "outbound": "block"},
            {"ip_cidr": ["127.0.0.0/8", "169.254.0.0/16", "224.0.0.0/4", "::1/128", "fc00::/7", "fe80::/10", "ff00::/8"], "outbound": "direct"},
            {"ip_cidr": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"], "outbound": "direct"},
            {"domain_keyword": ["cn", "china"], "outbound": "direct"},
            {"domain_suffix": [".cn", ".中国", ".公司", ".网络"], "outbound": "direct"},
            {"domain": ["qq.com", "baidu.com", "taobao.com", "tmall.com", "jd.com"], "outbound": "direct"}
        ]
        
        config = {
            "log": {
                "level": "info",
                "timestamp": True,
                "output": str(self.paths.log_dir / "sing-box.log")
            },
            "experimental": {
                "clash_api": {
                    "external_controller": "127.0.0.1:9090",
                    "external_ui": "ui",
                    "secret": "",
                    "default_mode": "rule"
                },
                "cache_file": {
                    "enabled": True,
                    "path": str(self.paths.config_dir / "cache.db"),
                    "cache_id": "default",
                    "store_fakeip": False
                }
            },
            "dns": {
                "servers": [
                    {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                    {"tag": "local", "address": "223.5.5.5", "detour": "direct"}
                ],
                "rules": [
                    {"domain_suffix": [".cn", ".中国"], "server": "local"},
                    {"clash_mode": "direct", "server": "local"},
                    {"clash_mode": "global", "server": "cloudflare"}
                ],
                "final": "cloudflare"
            },
            "inbounds": inbounds,
            "outbounds": outbounds,
            "route": {
                "rules": route_rules,
                "final": "🚀 节点选择",
                "auto_detect_interface": True
            }
        }
        
        return config
    
    def generate_local_server_config(self, server_type: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成本地服务器配置（服务端模式）"""
        if server_type == "trojan":
            return self._generate_trojan_server_config(config_data)
        elif server_type == "shadowsocks":
            return self._generate_shadowsocks_server_config(config_data)
        elif server_type == "vless":
            return self._generate_vless_server_config(config_data)
        else:
            self.logger.error(f"不支持的服务器类型: {server_type}")
            return {}
    
    def _generate_trojan_server_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成 Trojan 服务器配置"""
        config = {
            "log": {
                "level": "info",
                "timestamp": True,
                "output": str(self.paths.log_dir / "sing-box.log")
            },
            "inbounds": [
                {
                    "type": "trojan",
                    "tag": "trojan-in",
                    "listen": "0.0.0.0",
                    "listen_port": config_data['port'],
                    "users": [
                        {"password": config_data['password']}
                    ],
                    "tls": {
                        "enabled": True,
                        "server_name": config_data['domain'],
                        "certificate_path": config_data.get('cert_path', ''),
                        "key_path": config_data.get('key_path', ''),
                        "acme": {
                            "domain": [config_data['domain']],
                            "data_directory": str(self.paths.config_dir / "acme"),
                            "default_server_name": config_data['domain']
                        } if not config_data.get('cert_path') else None
                    }
                }
            ],
            "outbounds": [
                {"type": "direct", "tag": "direct"},
                {"type": "block", "tag": "block"}
            ],
            "route": {
                "rules": [
                    {"ip_cidr": ["224.0.0.0/3", "ff00::/8"], "outbound": "block"}
                ],
                "final": "direct"
            }
        }
        
        # 如果没有提供证书路径，移除证书配置，使用自动证书
        if not config_data.get('cert_path'):
            del config['inbounds'][0]['tls']['certificate_path']
            del config['inbounds'][0]['tls']['key_path']
        else:
            del config['inbounds'][0]['tls']['acme']
        
        return config
    
    def _generate_shadowsocks_server_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成 Shadowsocks 服务器配置"""
        return {
            "log": {
                "level": "info",
                "timestamp": True,
                "output": str(self.paths.log_dir / "sing-box.log")
            },
            "inbounds": [
                {
                    "type": "shadowsocks",
                    "tag": "ss-in",
                    "listen": "0.0.0.0",
                    "listen_port": config_data['port'],
                    "method": config_data['method'],
                    "password": config_data['password']
                }
            ],
            "outbounds": [
                {"type": "direct", "tag": "direct"},
                {"type": "block", "tag": "block"}
            ],
            "route": {
                "rules": [
                    {"ip_cidr": ["224.0.0.0/3", "ff00::/8"], "outbound": "block"}
                ],
                "final": "direct"
            }
        }
    
    def _generate_vless_server_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成 VLESS 服务器配置"""
        config = {
            "log": {
                "level": "info",
                "timestamp": True,
                "output": str(self.paths.log_dir / "sing-box.log")
            },
            "inbounds": [
                {
                    "type": "vless",
                    "tag": "vless-in",
                    "listen": "0.0.0.0",
                    "listen_port": config_data['port'],
                    "users": [
                        {"uuid": config_data['uuid']}
                    ],
                    "tls": {
                        "enabled": True,
                        "server_name": config_data['domain'],
                        "certificate_path": config_data.get('cert_path', ''),
                        "key_path": config_data.get('key_path', ''),
                        "acme": {
                            "domain": [config_data['domain']],
                            "data_directory": str(self.paths.config_dir / "acme"),
                            "default_server_name": config_data['domain']
                        } if not config_data.get('cert_path') else None
                    }
                }
            ],
            "outbounds": [
                {"type": "direct", "tag": "direct"},
                {"type": "block", "tag": "block"}
            ],
            "route": {
                "rules": [
                    {"ip_cidr": ["224.0.0.0/3", "ff00::/8"], "outbound": "block"}
                ],
                "final": "direct"
            }
        }
        
        # 如果没有提供证书路径，移除证书配置，使用自动证书
        if not config_data.get('cert_path'):
            del config['inbounds'][0]['tls']['certificate_path']
            del config['inbounds'][0]['tls']['key_path']
        else:
            del config['inbounds'][0]['tls']['acme']
        
        return config
    
    def save_config(self, config: Dict[str, Any], config_path: Path = None) -> bool:
        """保存配置文件"""
        if config_path is None:
            config_path = self.paths.main_config
        
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✓ 配置文件已保存: {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def backup_config(self, config_path: Path = None) -> bool:
        """备份配置文件"""
        if config_path is None:
            config_path = self.paths.main_config
        
        if not config_path.exists():
            self.logger.warn("配置文件不存在，无需备份")
            return True
        
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}.json"
            backup_path = self.paths.backup_dir / backup_name
            
            # 确保备份目录存在
            self.paths.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            import shutil
            shutil.copy2(config_path, backup_path)
            
            self.logger.info(f"✓ 配置已备份: {backup_name}")
            return True
        except Exception as e:
            self.logger.error(f"备份配置失败: {e}")
            return False
    
    def load_config(self, config_path: Path = None) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = self.paths.main_config
        
        if not config_path.exists():
            self.logger.warn(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置文件格式"""
        required_keys = ['inbounds', 'outbounds', 'route']
        for key in required_keys:
            if key not in config:
                self.logger.error(f"配置文件缺少必需字段: {key}")
                return False
        
        if not config['inbounds']:
            self.logger.error("配置文件中没有定义入站规则")
            return False
        
        if not config['outbounds']:
            self.logger.error("配置文件中没有定义出站规则")
            return False
        
        self.logger.info("✓ 配置文件格式验证通过")
        return True
    
    def get_local_ip(self) -> str:
        """获取本机 IP 地址"""
        try:
            # 创建一个连接来获取本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1" 