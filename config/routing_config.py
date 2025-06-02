#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
路由配置管理模块
Routing Configuration Manager
"""

import json
from typing import Dict, Any, List
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager
from .routing import RuleManager, MediaRulesManager, AppRulesManager, RuleImportExportManager


class RoutingConfigManager(BaseConfigManager):
    """路由配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
        
        # 初始化子模块管理器
        self.rule_manager = RuleManager(logger)
        self.media_rules_manager = MediaRulesManager(logger)
        self.app_rules_manager = AppRulesManager(logger)
        self.import_export_manager = RuleImportExportManager(self.paths.config_dir, logger)
    
    def load_routing_config(self) -> Dict[str, Any]:
        """加载路由配置"""
        default_config = {
            "enabled_rules": ["china_direct", "private_direct"],
            "final_outbound": "🚀 节点选择",
            "rule_sets": {
                "china_direct": {
                    "name": "中国直连",
                    "enabled": True,
                    "priority": 100,
                    "rules": [
                        {"domain_suffix": [".cn", ".中国"], "outbound": "direct"},
                        {"ip_cidr": ["223.5.5.5/32", "114.114.114.114/32"], "outbound": "direct"}
                    ]
                },
                "private_direct": {
                    "name": "私有网络直连",
                    "enabled": True,
                    "priority": 200,
                    "rules": [
                        {"ip_cidr": ["127.0.0.1/32", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"], "outbound": "direct"}
                    ]
                }
            }
        }
        
        if not self.advanced_config_file.exists():
            return default_config
        
        try:
            with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                routing = config.get("routing", {})
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in routing:
                        routing[key] = value
                return routing
        except (FileNotFoundError, json.JSONDecodeError):
            return default_config
    
    def save_routing_config(self, routing_config: Dict[str, Any]):
        """保存路由配置"""
        if self.advanced_config_file.exists():
            try:
                with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
        else:
            config = {}
        
        config["routing"] = routing_config
        
        try:
            self.advanced_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存路由配置失败: {e}")
    
    def configure_routing_rules(self):
        """配置分流规则管理"""
        print()
        print(f"{Colors.CYAN}🔀 分流规则管理{Colors.NC}")
        print("管理路由规则，决定不同流量的处理方式")
        print()
        
        routing_config = self.load_routing_config()
        
        while True:
            print("选择分流规则操作:")
            print("1. 📋 查看所有规则集")
            print("2. 🔧 编辑规则集")
            print("3. ➕ 添加自定义规则")
            print("4. 🗑️  删除规则")
            print("5. 📤 导出规则")
            print("6. 📥 导入规则")
            print("7. 🔄 重置规则")
            print("8. ⚙️  高级设置")
            print("9. 🎬 媒体分流管理")
            print("10. 💻 程序分流管理")
            print("11. 💾 保存并返回")
            print()
            
            choice = input("请选择 [1-11]: ").strip()
            
            if choice == "1":
                self.rule_manager.view_all_rule_sets(routing_config)
            elif choice == "2":
                self.rule_manager.edit_rule_set(routing_config)
            elif choice == "3":
                self.rule_manager.add_custom_rule(routing_config)
            elif choice == "4":
                self.rule_manager.delete_rule(routing_config)
            elif choice == "5":
                self.import_export_manager.export_rules(routing_config)
            elif choice == "6":
                self.import_export_manager.import_rules(routing_config)
            elif choice == "7":
                self.rule_manager.reset_rules(routing_config)
            elif choice == "8":
                self._advanced_routing_settings(routing_config)
            elif choice == "9":
                self.configure_media_routing_rules(routing_config)
            elif choice == "10":
                self.configure_application_routing_rules(routing_config)
            elif choice == "11":
                self.save_routing_config(routing_config)
                self.logger.info("✓ 分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def configure_media_routing_rules(self, routing_config: Dict[str, Any] = None):
        """配置媒体分流规则管理"""
        if routing_config is None:
            routing_config = self.load_routing_config()
        
        self.media_rules_manager.configure_media_routing_rules(
            routing_config, 
            self.save_routing_config
        )
    
    def configure_application_routing_rules(self, routing_config: Dict[str, Any] = None):
        """配置程序分流规则管理"""
        if routing_config is None:
            routing_config = self.load_routing_config()
        
        self.app_rules_manager.configure_application_routing_rules(
            routing_config,
            self.save_routing_config
        )
    
    def _advanced_routing_settings(self, routing_config: Dict[str, Any]):
        """高级路由设置"""
        print()
        print(f"{Colors.CYAN}⚙️  高级路由设置{Colors.NC}")
        print()
        
        current_final = routing_config.get("final_outbound", "proxy")
        # 显示实际使用的outbound名称
        display_final = "🚀 节点选择" if current_final == "proxy" else current_final
        print(f"当前默认出站: {current_final} (实际使用: {display_final})")
        print()
        
        print("1. 设置默认出站")
        print("2. 规则组启用/禁用")
        print("3. 备份与恢复")
        print("4. 返回上级")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            self._set_final_outbound(routing_config)
        elif choice == "2":
            self.rule_manager.manage_enabled_rules(routing_config)
        elif choice == "3":
            self._backup_restore_menu(routing_config)
        elif choice == "4":
            return
        else:
            self.logger.error("无效选项")
    
    def _set_final_outbound(self, routing_config: Dict[str, Any]):
        """设置默认出站"""
        print("默认出站选项:")
        print("1. proxy - 走代理 (实际使用: 🚀 节点选择)")
        print("2. direct - 直连")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择 [1-3]: ").strip()
        outbound_map = {"1": "proxy", "2": "direct", "3": "block"}
        new_outbound = outbound_map.get(outbound_choice)
        
        if new_outbound:
            routing_config["final_outbound"] = new_outbound
            display_new = "🚀 节点选择" if new_outbound == "proxy" else new_outbound
            self.logger.info(f"✓ 默认出站设置为: {new_outbound} (实际使用: {display_new})")
        else:
            self.logger.error("无效选择")
    
    def _backup_restore_menu(self, routing_config: Dict[str, Any]):
        """备份与恢复菜单"""
        print()
        print("备份与恢复:")
        print("1. 备份当前规则")
        print("2. 从备份恢复")
        print("3. 返回")
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            self.import_export_manager.backup_rules(routing_config)
        elif choice == "2":
            self.import_export_manager.restore_from_backup(routing_config)
        elif choice == "3":
            return
        else:
            self.logger.error("无效选项")
    
    def generate_route_config(self) -> Dict[str, Any]:
        """生成路由配置"""
        routing_config = self.load_routing_config()
        
        if not routing_config.get("enabled_rules"):
            return {}
        
        # 生成路由规则
        route_rules = []
        enabled_rules = routing_config.get("enabled_rules", [])
        rule_sets = routing_config.get("rule_sets", {})
        
        # 按优先级排序规则集
        sorted_rules = []
        for rule_name in enabled_rules:
            if rule_name in rule_sets and rule_sets[rule_name].get("enabled", True):
                rule_set = rule_sets[rule_name]
                priority = rule_set.get("priority", 100)
                sorted_rules.append((priority, rule_name, rule_set))
        
        sorted_rules.sort(key=lambda x: x[0])  # 按优先级排序
        
        # 生成规则
        for priority, rule_name, rule_set in sorted_rules:
            for rule in rule_set.get("rules", []):
                route_rule = {}
                
                # 复制规则条件
                for key, value in rule.items():
                    if key != "outbound":
                        route_rule[key] = value
                
                # 设置出站，转换proxy为实际的outbound名称
                original_outbound = rule.get("outbound", "proxy")
                if original_outbound == "proxy":
                    route_rule["outbound"] = "🚀 节点选择"
                else:
                    route_rule["outbound"] = original_outbound
                    
                route_rules.append(route_rule)
        
        # 获取final outbound设置，确保使用正确的outbound名称
        final_outbound = routing_config.get("final_outbound", "proxy")
        
        # 如果final_outbound是"proxy"，则改为"🚀 节点选择"（这是实际存在的outbound）
        if final_outbound == "proxy":
            final_outbound = "🚀 节点选择"
        
        route_config = {
            "auto_detect_interface": True,
            "final": final_outbound,
            "rules": route_rules
        }
        
        return route_config 