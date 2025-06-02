#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
媒体分流规则管理器
Media Routing Rules Manager
"""

from typing import Dict, Any
from utils import Colors, Logger


class MediaRulesManager:
    """媒体分流规则管理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        
        # 媒体相关的规则集定义
        self.media_rule_sets = {
            "streaming_global": "🎬 国际流媒体",
            "music_streaming": "🎵 音乐流媒体", 
            "social_media": "📱 社交媒体",
            "ai_services": "🤖 AI服务",
            "news_media": "📰 新闻媒体"
        }
    
    def configure_media_routing_rules(self, routing_config: Dict[str, Any], save_callback):
        """配置媒体分流规则管理"""
        print()
        print(f"{Colors.CYAN}🎬 媒体分流管理{Colors.NC}")
        print("管理流媒体、音乐、社交媒体等媒体服务的分流规则")
        print()
        
        rule_sets = routing_config.get("rule_sets", {})
        
        while True:
            self._show_media_rules_status(rule_sets)
            
            print("媒体分流管理选项:")
            print("1. ⚡ 一键启用所有媒体分流")
            print("2. ⏹️  一键禁用所有媒体分流")
            print("3. 🔧 单独管理规则组")
            print("4. 📋 查看规则详情")
            print("5. ➕ 添加自定义媒体规则")
            print("6. 🎯 设置优先级")
            print("7. 💾 保存并返回")
            print()
            
            choice = input("请选择 [1-7]: ").strip()
            
            if choice == "1":
                self._enable_all_media_rules(routing_config)
            elif choice == "2":
                self._disable_all_media_rules(routing_config)
            elif choice == "3":
                self._manage_single_media_rule(routing_config)
            elif choice == "4":
                self._view_media_rule_details(rule_sets)
            elif choice == "5":
                self._add_custom_media_rule(routing_config)
            elif choice == "6":
                self._set_media_rule_priorities(rule_sets)
            elif choice == "7":
                save_callback(routing_config)
                self.logger.info("✓ 媒体分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def _show_media_rules_status(self, rule_sets: Dict[str, Any]):
        """显示媒体规则状态"""
        print(f"{Colors.YELLOW}当前媒体分流规则状态:{Colors.NC}")
        print()
        for rule_id, rule_name in self.media_rule_sets.items():
            if rule_id in rule_sets:
                rule_set = rule_sets[rule_id]
                status = f"{Colors.GREEN}启用{Colors.NC}" if rule_set.get("enabled", False) else f"{Colors.RED}禁用{Colors.NC}"
                rules_count = len(rule_set.get("rules", []))
                priority = rule_set.get("priority", 0)
                print(f"  {rule_name}: {status} ({rules_count} 条规则, 优先级: {priority})")
            else:
                print(f"  {rule_name}: {Colors.YELLOW}未配置{Colors.NC}")
        print()
    
    def _enable_all_media_rules(self, routing_config: Dict[str, Any]):
        """一键启用所有媒体分流"""
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.setdefault("enabled_rules", [])
        
        for rule_id in self.media_rule_sets.keys():
            if rule_id in rule_sets:
                rule_sets[rule_id]["enabled"] = True
                if rule_id not in enabled_rules:
                    enabled_rules.append(rule_id)
        
        self.logger.info("✓ 已启用所有媒体分流规则")
    
    def _disable_all_media_rules(self, routing_config: Dict[str, Any]):
        """一键禁用所有媒体分流"""
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.get("enabled_rules", [])
        
        for rule_id in self.media_rule_sets.keys():
            if rule_id in rule_sets:
                rule_sets[rule_id]["enabled"] = False
                if rule_id in enabled_rules:
                    enabled_rules.remove(rule_id)
        
        self.logger.info("✓ 已禁用所有媒体分流规则")
    
    def _manage_single_media_rule(self, routing_config: Dict[str, Any]):
        """单独管理规则组"""
        rule_sets = routing_config.get("rule_sets", {})
        
        print("\n选择要管理的媒体规则组:")
        rule_list = list(self.media_rule_sets.items())
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
    
    def _view_media_rule_details(self, rule_sets: Dict[str, Any]):
        """查看规则详情"""
        print("\n选择要查看的媒体规则组:")
        rule_list = list(self.media_rule_sets.items())
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
    
    def _add_custom_media_rule(self, routing_config: Dict[str, Any]):
        """添加自定义媒体规则"""
        print()
        print(f"{Colors.CYAN}添加自定义媒体规则{Colors.NC}")
        print("为特定的媒体服务添加分流规则")
        print()
        
        service_name = input("媒体服务名称 (如: Netflix): ").strip()
        if not service_name:
            self.logger.error("服务名称不能为空")
            return
        
        print()
        print("选择规则类型:")
        print("1. 域名后缀 (如: .netflix.com)")
        print("2. 域名关键词 (如: netflix)")
        print("3. 完整域名 (如: www.netflix.com)")
        
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
        
        self.logger.info(f"✓ 已添加 {service_name} 的自定义媒体规则")
    
    def _set_media_rule_priorities(self, rule_sets: Dict[str, Any]):
        """设置媒体规则优先级"""
        print()
        print(f"{Colors.CYAN}设置媒体规则优先级{Colors.NC}")
        print("数字越小优先级越高，建议范围: 1-500")
        print()
        
        for rule_id, rule_name in self.media_rule_sets.items():
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
        """管理单个媒体规则"""
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