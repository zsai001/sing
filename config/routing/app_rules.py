#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
程序分流规则管理器  
Application Routing Rules Manager
"""

from typing import Dict, Any
from utils import Colors, Logger


class AppRulesManager:
    """程序分流规则管理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        
        # 程序相关的规则集定义
        self.app_rule_sets = {
            "development_tools": "🔧 开发工具",
            "office_tools": "📄 办公软件",
            "gaming_platforms": "🎮 游戏平台",
            "messaging_apps": "💬 聊天通讯"
        }
    
    def configure_application_routing_rules(self, routing_config: Dict[str, Any], save_callback):
        """配置程序分流规则管理"""
        print()
        print(f"{Colors.CYAN}💻 程序分流管理{Colors.NC}")
        print("管理开发工具、办公软件、游戏平台等应用程序的分流规则")
        print()
        
        rule_sets = routing_config.get("rule_sets", {})
        
        while True:
            self._show_app_rules_status(rule_sets)
            
            print("程序分流管理选项:")
            print("1. ⚡ 一键启用所有程序分流")
            print("2. ⏹️  一键禁用所有程序分流")
            print("3. 🔧 单独管理规则组")
            print("4. 📋 查看规则详情")
            print("5. ➕ 添加自定义程序规则")
            print("6. 🎯 设置优先级")
            print("7. 💾 保存并返回")
            print()
            
            choice = input("请选择 [1-7]: ").strip()
            
            if choice == "1":
                self._enable_all_app_rules(routing_config)
            elif choice == "2":
                self._disable_all_app_rules(routing_config)
            elif choice == "3":
                self._manage_single_app_rule(routing_config)
            elif choice == "4":
                self._view_app_rule_details(rule_sets)
            elif choice == "5":
                self._add_custom_app_rule(routing_config)
            elif choice == "6":
                self._set_app_rule_priorities(rule_sets)
            elif choice == "7":
                save_callback(routing_config)
                self.logger.info("✓ 程序分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def _show_app_rules_status(self, rule_sets: Dict[str, Any]):
        """显示程序规则状态"""
        print(f"{Colors.YELLOW}当前程序分流规则状态:{Colors.NC}")
        print()
        for rule_id, rule_name in self.app_rule_sets.items():
            if rule_id in rule_sets:
                rule_set = rule_sets[rule_id]
                status = f"{Colors.GREEN}启用{Colors.NC}" if rule_set.get("enabled", False) else f"{Colors.RED}禁用{Colors.NC}"
                rules_count = len(rule_set.get("rules", []))
                priority = rule_set.get("priority", 0)
                print(f"  {rule_name}: {status} ({rules_count} 条规则, 优先级: {priority})")
            else:
                print(f"  {rule_name}: {Colors.YELLOW}未配置{Colors.NC}")
        print()
    
    def _enable_all_app_rules(self, routing_config: Dict[str, Any]):
        """一键启用所有程序分流"""
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.setdefault("enabled_rules", [])
        
        for rule_id in self.app_rule_sets.keys():
            if rule_id in rule_sets:
                rule_sets[rule_id]["enabled"] = True
                if rule_id not in enabled_rules:
                    enabled_rules.append(rule_id)
        
        self.logger.info("✓ 已启用所有程序分流规则")
    
    def _disable_all_app_rules(self, routing_config: Dict[str, Any]):
        """一键禁用所有程序分流"""
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.get("enabled_rules", [])
        
        for rule_id in self.app_rule_sets.keys():
            if rule_id in rule_sets:
                rule_sets[rule_id]["enabled"] = False
                if rule_id in enabled_rules:
                    enabled_rules.remove(rule_id)
        
        self.logger.info("✓ 已禁用所有程序分流规则")
    
    def _manage_single_app_rule(self, routing_config: Dict[str, Any]):
        """单独管理规则组"""
        rule_sets = routing_config.get("rule_sets", {})
        
        print("\n选择要管理的程序规则组:")
        rule_list = list(self.app_rule_sets.items())
        for i, (rule_id, rule_name) in enumerate(rule_list, 1):
            status = "启用" if rule_sets.get(rule_id, {}).get("enabled", False) else "禁用"
            print(f"{i}. {rule_name} ({status})")
        
        try:
            choice_idx = int(input("请选择规则组编号: ")) - 1
            if 0 <= choice_idx < len(rule_list):
                rule_id, rule_name = rule_list[choice_idx]
                if rule_id in rule_sets:
                    self._manage_single_rule(rule_id, rule_sets[rule_id], routing_config)
                else:
                    self.logger.error("该规则组未配置")
            else:
                self.logger.error("无效选择")
        except ValueError:
            self.logger.error("请输入有效数字")
    
    def _view_app_rule_details(self, rule_sets: Dict[str, Any]):
        """查看规则详情"""
        print("\n选择要查看的程序规则组:")
        rule_list = list(self.app_rule_sets.items())
        for i, (rule_id, rule_name) in enumerate(rule_list, 1):
            print(f"{i}. {rule_name}")
        
        try:
            choice_idx = int(input("请选择规则组编号: ")) - 1
            if 0 <= choice_idx < len(rule_list):
                rule_id, rule_name = rule_list[choice_idx]
                if rule_id in rule_sets:
                    self._view_rule_set_details(rule_id, rule_sets[rule_id])
                else:
                    self.logger.error("该规则组未配置")
            else:
                self.logger.error("无效选择")
        except ValueError:
            self.logger.error("请输入有效数字")
    
    def _add_custom_app_rule(self, routing_config: Dict[str, Any]):
        """添加自定义程序规则"""
        print()
        print(f"{Colors.CYAN}添加自定义程序规则{Colors.NC}")
        print("为特定的应用程序添加分流规则")
        print()
        
        app_name = input("应用程序名称 (如: GitHub): ").strip()
        if not app_name:
            self.logger.error("应用程序名称不能为空")
            return
        
        print()
        print("选择规则类型:")
        print("1. 域名后缀 (如: .github.com)")
        print("2. 域名关键词 (如: github)")
        print("3. 完整域名 (如: api.github.com)")
        
        rule_type = input("请选择 [1-3]: ").strip()
        
        if rule_type not in ["1", "2", "3"]:
            self.logger.error("无效选项")
            return
        
        domains = input("输入域名 (多个用逗号分隔): ").strip()
        if not domains:
            self.logger.error("域名不能为空")
            return
        
        domain_list = [d.strip() for d in domains.split(",")]
        
        # 选择出站
        print()
        print("选择出站方式:")
        print("1. 🚀 节点选择 - 走代理")
        print("2. direct - 直连")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择 [1-3]: ").strip()
        outbound_map = {"1": "🚀 节点选择", "2": "direct", "3": "block"}
        outbound = outbound_map.get(outbound_choice, "🚀 节点选择")
        
        # 创建规则
        rule = {"outbound": outbound}
        if rule_type == "1":
            rule["domain_suffix"] = domain_list
        elif rule_type == "2":
            rule["domain_keyword"] = domain_list
        elif rule_type == "3":
            rule["domain"] = domain_list
        
        # 添加到custom规则集
        rule_sets = routing_config.setdefault("rule_sets", {})
        custom_rules = rule_sets.setdefault("custom", {
            "name": "自定义规则",
            "enabled": True,
            "priority": 400,
            "rules": []
        })
        
        custom_rules["rules"].append(rule)
        
        self.logger.info(f"✓ 已添加 {app_name} 的自定义程序规则")
    
    def _set_app_rule_priorities(self, rule_sets: Dict[str, Any]):
        """设置程序规则优先级"""
        print()
        print(f"{Colors.CYAN}设置程序规则优先级{Colors.NC}")
        print("数字越小优先级越高，建议范围: 1-500")
        print()
        
        for rule_id, rule_name in self.app_rule_sets.items():
            if rule_id in rule_sets:
                current_priority = rule_sets[rule_id].get("priority", 100)
                try:
                    new_priority = input(f"{rule_name} (当前: {current_priority}): ").strip()
                    if new_priority:
                        rule_sets[rule_id]["priority"] = int(new_priority)
                        self.logger.info(f"✓ {rule_name} 优先级设置为: {new_priority}")
                except ValueError:
                    self.logger.error(f"跳过 {rule_name}: 输入无效")
    
    def _manage_single_rule(self, rule_id: str, rule_set: Dict[str, Any], routing_config: Dict[str, Any]):
        """管理单个程序规则"""
        print()
        print(f"{Colors.CYAN}管理规则组: {rule_set.get('name', rule_id)}{Colors.NC}")
        print()
        print("1. 启用/禁用规则组")
        print("2. 修改优先级")
        print("3. 查看规则详情")
        print("4. 返回")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            current_status = rule_set.get("enabled", False)
            rule_set["enabled"] = not current_status
            new_status = "启用" if not current_status else "禁用"
            
            # 更新enabled_rules列表
            enabled_rules = routing_config.get("enabled_rules", [])
            if not current_status and rule_id not in enabled_rules:
                enabled_rules.append(rule_id)
            elif current_status and rule_id in enabled_rules:
                enabled_rules.remove(rule_id)
            routing_config["enabled_rules"] = enabled_rules
            
            self.logger.info(f"✓ 规则组已{new_status}")
            
        elif choice == "2":
            try:
                new_priority = int(input(f"当前优先级: {rule_set.get('priority', 100)}, 输入新优先级: "))
                rule_set["priority"] = new_priority
                self.logger.info(f"✓ 优先级已设置为: {new_priority}")
            except ValueError:
                self.logger.error("请输入有效数字")
                
        elif choice == "3":
            self._view_rule_set_details(rule_id, rule_set)
            
        elif choice == "4":
            return
        else:
            self.logger.error("无效选项")
    
    def _view_rule_set_details(self, rule_id: str, rule_set: Dict[str, Any]):
        """查看规则集详情"""
        print()
        print(f"{Colors.CYAN}规则集详情: {rule_set.get('name', rule_id)}{Colors.NC}")
        print(f"ID: {rule_id}")
        print(f"启用状态: {'启用' if rule_set.get('enabled', False) else '禁用'}")
        print(f"优先级: {rule_set.get('priority', 100)}")
        print(f"规则数量: {len(rule_set.get('rules', []))}")
        print()
        
        rules = rule_set.get("rules", [])
        if rules:
            print("规则详情:")
            for i, rule in enumerate(rules, 1):
                print(f"  {i}. 出站: {rule.get('outbound', 'proxy')}")
                if 'domain_suffix' in rule:
                    domains = rule['domain_suffix'][:5]  # 只显示前5个
                    suffix = f" (共{len(rule['domain_suffix'])}个)" if len(rule['domain_suffix']) > 5 else ""
                    print(f"     域名后缀: {', '.join(domains)}{suffix}")
                if 'domain_keyword' in rule:
                    keywords = rule['domain_keyword'][:5]
                    suffix = f" (共{len(rule['domain_keyword'])}个)" if len(rule['domain_keyword']) > 5 else ""
                    print(f"     域名关键词: {', '.join(keywords)}{suffix}")
                if 'domain' in rule:
                    domains = rule['domain'][:5]
                    suffix = f" (共{len(rule['domain'])}个)" if len(rule['domain']) > 5 else ""
                    print(f"     完整域名: {', '.join(domains)}{suffix}")
                if 'ip_cidr' in rule:
                    cidrs = rule['ip_cidr'][:3]
                    suffix = f" (共{len(rule['ip_cidr'])}个)" if len(rule['ip_cidr']) > 3 else ""
                    print(f"     IP段: {', '.join(cidrs)}{suffix}")
        else:
            print("该规则集为空") 