#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级配置管理模块 - sing-box 高级功能配置 (重构版)
SingTool Advanced Config Module (Refactored)

此版本使用模块化设计，将配置功能拆分为独立的管理器：
- ProxyConfigManager: 代理端口配置
- DNSConfigManager: DNS和FakeIP配置  
- TUNConfigManager: TUN模式配置
- ClashConfigManager: Clash API配置
- SystemProxyManager: 系统代理配置
- RoutingConfigManager: 路由规则配置
"""

import json
from typing import Dict, Any, List
from utils import Colors, Logger
from paths import PathManager
from config import (
    ProxyConfigManager,
    DNSConfigManager,
    TUNConfigManager,
    ClashConfigManager,
    SystemProxyManager,
    RoutingConfigManager
)


class AdvancedConfigManager:
    """高级配置管理类 - 协调各个配置模块"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
        
        # 初始化各个配置管理器
        self.proxy_manager = ProxyConfigManager(paths, logger)
        self.dns_manager = DNSConfigManager(paths, logger)
        self.tun_manager = TUNConfigManager(paths, logger)
        self.clash_manager = ClashConfigManager(paths, logger)
        self.system_proxy_manager = SystemProxyManager(paths, logger)
        self.routing_manager = RoutingConfigManager(paths, logger)
        
        # 初始化高级配置文件
        self._init_advanced_config()
    
    def _init_advanced_config(self):
        """初始化高级配置文件"""
        if not self.advanced_config_file.exists():
            default_config = {
                "version": "2.0",
                "description": "SingTool高级配置文件 - 模块化设计",
                "modules": {
                    "proxy_ports": "代理端口配置",
                    "dns": "DNS和FakeIP配置",
                    "clash_api": "Clash API配置",
                    "system_proxy": "系统代理配置",
                    "routing": "路由规则配置"
                },
                "last_updated": None
            }
            
            self.advanced_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    def load_advanced_config(self) -> Dict[str, Any]:
        """加载高级配置"""
        try:
            with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_advanced_config()
            return self.load_advanced_config()
    
    def save_advanced_config(self, config: Dict[str, Any]):
        """保存高级配置"""
        import datetime
        config["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    # === 代理端口配置 ===
    def configure_proxy_ports(self):
        """配置代理端口"""
        return self.proxy_manager.configure_proxy_ports()
    
    def generate_inbounds_config(self) -> List[Dict[str, Any]]:
        """根据配置生成入站配置"""
        return self.proxy_manager.generate_inbounds_config()
    
    # === DNS配置 ===
    def configure_dns_fakeip(self):
        """配置DNS和FakeIP"""
        return self.dns_manager.configure_dns_fakeip()
    
    def generate_dns_config(self) -> Dict[str, Any]:
        """根据配置生成DNS配置"""
        return self.dns_manager.generate_dns_config()
    
    # === TUN模式配置 ===
    def configure_tun_mode(self):
        """配置TUN模式"""
        return self.tun_manager.configure_tun_mode()
    
    # === Clash API配置 ===
    def configure_clash_api(self):
        """配置Clash API"""
        return self.clash_manager.configure_clash_api()
    
    def generate_experimental_config(self) -> Dict[str, Any]:
        """根据配置生成实验性功能配置"""
        return self.clash_manager.generate_experimental_config()
    
    # === 系统代理配置 ===
    def configure_system_proxy(self):
        """配置系统代理"""
        return self.system_proxy_manager.configure_system_proxy()
    
    # === 路由规则配置 ===
    def configure_routing_rules(self):
        """配置分流规则"""
        return self.routing_manager.configure_routing_rules()
    
    def generate_route_config(self) -> Dict[str, Any]:
        """根据配置生成路由配置"""
        return self.routing_manager.generate_route_config()
    
    # === 媒体分流配置 (简化版) ===
    def configure_media_routing_rules(self):
        """配置媒体分流规则"""
        print()
        print(f"{Colors.CYAN}🎬 媒体分流管理{Colors.NC}")
        print("管理流媒体、音乐、社交媒体等媒体服务的分流规则")
        print()
        print("此功能已集成到路由规则管理中，请使用「配置分流规则」功能。")
        input("按Enter键返回...")
    
    def configure_application_routing_rules(self):
        """配置程序分流规则"""
        print()
        print(f"{Colors.CYAN}💻 程序分流管理{Colors.NC}")
        print("管理开发工具、办公软件、游戏平台等应用程序的分流规则")
        print()
        print("此功能已集成到路由规则管理中，请使用「配置分流规则」功能。")
        input("按Enter键返回...")
    
    # === 配置状态和信息 ===
    def get_config_status(self) -> Dict[str, Any]:
        """获取配置状态信息"""
        status = {
            "proxy_ports": {
                "enabled": True,
                "config": self.proxy_manager.load_proxy_config()
            },
            "dns": {
                "enabled": True, 
                "config": self.dns_manager.generate_dns_config()
            },
            "clash_api": {
                "enabled": True,
                "config": self.clash_manager.load_clash_config()
            },
            "system_proxy": {
                "enabled": True,
                "config": self.system_proxy_manager.load_system_proxy_config()
            },
            "routing": {
                "enabled": True,
                "config": self.routing_manager.load_routing_config()
            }
        }
        return status
    
    def show_config_overview(self):
        """显示配置概览"""
        print()
        print(f"{Colors.CYAN}📊 配置概览{Colors.NC}")
        print("=" * 60)
        
        status = self.get_config_status()
        
        # 代理端口状态
        proxy_config = status["proxy_ports"]["config"]
        enabled_ports = proxy_config.get("enabled", [])
        print(f"🔗 代理端口: {len(enabled_ports)} 个端口启用 ({', '.join(enabled_ports)})")
        
        # DNS状态
        dns_config = status["dns"]["config"]
        dns_servers = len(dns_config.get("servers", []))
        print(f"🌐 DNS配置: {dns_servers} 个DNS服务器")
        
        # Clash API状态
        clash_config = status["clash_api"]["config"]
        clash_enabled = clash_config.get("enabled", False)
        print(f"📡 Clash API: {'启用' if clash_enabled else '禁用'}")
        
        # 系统代理状态
        sys_proxy_config = status["system_proxy"]["config"]
        sys_proxy_enabled = sys_proxy_config.get("enabled", False)
        print(f"🌍 系统代理: {'启用' if sys_proxy_enabled else '禁用'}")
        
        # 路由规则状态
        routing_config = status["routing"]["config"]
        enabled_rules = len(routing_config.get("enabled_rules", []))
        total_rules = len(routing_config.get("rule_sets", {}))
        print(f"🔀 路由规则: {enabled_rules}/{total_rules} 个规则组启用")
        
        print("=" * 60)
        
    # === 兼容性方法 ===
    def update_proxy_ports(self, proxy_config: Dict[str, Any]):
        """更新代理端口配置（兼容性方法）"""
        self.proxy_manager.save_proxy_config(proxy_config)
    
    def load_system_proxy_config(self) -> Dict[str, Any]:
        """加载系统代理配置（兼容性方法）"""
        return self.system_proxy_manager.load_system_proxy_config()
    
    def save_system_proxy_config(self, config: Dict[str, Any]):
        """保存系统代理配置（兼容性方法）"""
        return self.system_proxy_manager.save_system_proxy_config(config)
    
    def get_proxy_ports_config(self) -> Dict[str, Any]:
        """获取代理端口配置（兼容性方法）"""
        return self.proxy_manager.load_proxy_config()
    
    def get_routing_config(self) -> Dict[str, Any]:
        """获取路由配置（兼容性方法）"""
        return self.routing_manager.load_routing_config()
    
    # === 配置导入导出 ===
    def export_config(self, export_file: str = None):
        """导出配置"""
        if not export_file:
            export_file = str(self.paths.config_dir / "advanced_config_export.json")
        
        export_data = {
            "version": "2.0",
            "export_time": __import__('datetime').datetime.now().isoformat(),
            "proxy_ports": self.proxy_manager.load_proxy_config(),
            "clash_api": self.clash_manager.load_clash_config(),
            "system_proxy": self.system_proxy_manager.load_system_proxy_config(),
            "routing": self.routing_manager.load_routing_config()
        }
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✓ 配置已导出到: {export_file}")
        except Exception as e:
            self.logger.error(f"导出配置失败: {e}")
    
    def import_config(self, import_file: str):
        """导入配置"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 导入各个模块的配置
            if "proxy_ports" in import_data:
                self.proxy_manager.save_proxy_config(import_data["proxy_ports"])
            
            if "clash_api" in import_data:
                self.clash_manager.save_clash_config(import_data["clash_api"])
            
            if "system_proxy" in import_data:
                self.system_proxy_manager.save_system_proxy_config(import_data["system_proxy"])
            
            if "routing" in import_data:
                self.routing_manager.save_routing_config(import_data["routing"])
            
            self.logger.info(f"✓ 配置已从 {import_file} 导入")
        except Exception as e:
            self.logger.error(f"导入配置失败: {e}")
    
    # === 配置重置 ===
    def reset_config(self, module: str = None):
        """重置配置"""
        if module == "proxy_ports":
            # 重置代理端口配置
            self.proxy_manager.save_proxy_config({
                "mixed_port": 7890,
                "http_port": 7891, 
                "socks_port": 7892,
                "enabled": ["mixed"]
            })
            self.logger.info("✓ 代理端口配置已重置")
            
        elif module == "all":
            # 重置所有配置
            confirm = input(f"{Colors.RED}确定要重置所有高级配置吗? (输入 'yes' 确认): {Colors.NC}")
            if confirm == 'yes':
                # 删除配置文件，重新初始化
                if self.advanced_config_file.exists():
                    self.advanced_config_file.unlink()
                self._init_advanced_config()
                self.logger.info("✓ 所有高级配置已重置")
            else:
                self.logger.info("重置操作已取消")
        else:
            self.logger.error("无效的模块名称") 