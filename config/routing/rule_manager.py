#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
规则集管理器
Rule Set Manager
"""

from typing import Dict, Any, List
from utils import Colors, Logger


class RuleManager:
    """规则集管理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def view_all_rule_sets(self, routing_config: Dict[str, Any]):
        """查看所有规则组"""
        print()
        print(f"{Colors.CYAN}📋 所有规则组{Colors.NC}")
        print("=" * 80)
        
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.get("enabled_rules", [])
        
        if not rule_sets:
            print("暂无规则组")
            return
        
        # 按优先级排序
        sorted_rules = sorted(rule_sets.items(), key=lambda x: x[1].get('priority', 999))
        
        for rule_id, rule_set in sorted_rules:
            name = rule_set.get('name', rule_id)
            enabled = rule_set.get('enabled', True)
            priority = rule_set.get('priority', 999)
            rules = rule_set.get('rules', [])
            is_active = rule_id in enabled_rules
            
            status = f"{Colors.GREEN}●{Colors.NC}" if (enabled and is_active) else f"{Colors.RED}○{Colors.NC}"
            print(f"{status} {name} (优先级: {priority})")
            print(f"    规则数量: {len(rules)} 条")
            
            if rules:
                print("    规则预览:")
                for i, rule in enumerate(rules[:3]):  # 只显示前3条
                    rule_type = list(rule.keys())[0] if rule else "unknown"
                    outbound = rule.get('outbound', 'unknown')
                    if rule_type == 'domain_suffix':
                        preview = f"域名后缀: {rule[rule_type][:2]}..."
                    elif rule_type == 'domain_keyword':
                        preview = f"域名关键词: {rule[rule_type][:2]}..."
                    elif rule_type == 'ip_cidr':
                        preview = f"IP段: {rule[rule_type][:2]}..."
                    else:
                        preview = f"{rule_type}: ..."
                    
                    print(f"      {i+1}. {preview} → {outbound}")
                
                if len(rules) > 3:
                    print(f"      ... 还有 {len(rules) - 3} 条规则")
            print()
    
    def edit_rule_set(self, routing_config: Dict[str, Any]):
        """编辑规则组"""
        rule_sets = routing_config.get("rule_sets", {})
        
        if not rule_sets:
            self.logger.warn("暂无规则组可编辑")
            return
        
        print()
        print(f"{Colors.CYAN}选择要编辑的规则组:{Colors.NC}")
        rule_list = list(rule_sets.items())
        
        for i, (rule_id, rule_set) in enumerate(rule_list, 1):
            name = rule_set.get('name', rule_id)
            enabled = "✓" if rule_set.get('enabled', True) else "✗"
            print(f"  {i}. {enabled} {name}")
        
        try:
            choice = int(input("请选择规则组编号: ").strip()) - 1
            if 0 <= choice < len(rule_list):
                rule_id, rule_set = rule_list[choice]
                self.edit_single_rule_set(rule_id, rule_set, routing_config)
            else:
                self.logger.error("无效的编号")
        except ValueError:
            self.logger.error("请输入有效的数字")
    
    def edit_single_rule_set(self, rule_id: str, rule_set: Dict[str, Any], routing_config: Dict[str, Any]):
        """编辑单个规则组"""
        print()
        print(f"{Colors.CYAN}编辑规则组: {rule_set.get('name', rule_id)}{Colors.NC}")
        print()
        
        print("1. 启用/禁用规则组")
        print("2. 修改优先级")
        print("3. 查看详细规则")
        print("4. 返回上级")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            current = rule_set.get('enabled', True)
            rule_set['enabled'] = not current
            status = '启用' if not current else '禁用'
            self.logger.info(f"✓ 规则组已{status}")
            
        elif choice == "2":
            try:
                current_priority = rule_set.get('priority', 999)
                new_priority = int(input(f"设置优先级 (当前: {current_priority}, 数字越小优先级越高): ").strip())
                rule_set['priority'] = new_priority
                self.logger.info(f"✓ 优先级设置为: {new_priority}")
            except ValueError:
                self.logger.error("优先级必须是数字")
                
        elif choice == "3":
            rules = rule_set.get('rules', [])
            print()
            print(f"规则详情 (共 {len(rules)} 条):")
            for i, rule in enumerate(rules, 1):
                self.print_rule_details(i, rule)
                
        elif choice == "4":
            return
        else:
            self.logger.error("无效选项")
    
    def print_rule_details(self, index: int, rule: Dict[str, Any]):
        """打印规则详情"""
        outbound = rule.get('outbound', 'unknown')
        
        for rule_type, rule_value in rule.items():
            if rule_type != 'outbound':
                if isinstance(rule_value, list):
                    value_str = ', '.join(str(v) for v in rule_value[:3])
                    if len(rule_value) > 3:
                        value_str += f" ... (共{len(rule_value)}个)"
                else:
                    value_str = str(rule_value)
                    
                print(f"  {index}. {rule_type}: {value_str} → {outbound}")
                break
    
    def add_custom_rule(self, routing_config: Dict[str, Any]):
        """添加自定义规则"""
        print()
        print(f"{Colors.CYAN}➕ 添加自定义规则{Colors.NC}")
        print()
        
        # 获取自定义规则组
        rule_sets = routing_config.setdefault("rule_sets", {})
        custom_rules = rule_sets.setdefault("custom", {
            "name": "自定义规则",
            "enabled": True,
            "priority": 400,
            "rules": []
        })
        
        print("规则类型:")
        print("1. 域名规则 (domain)")
        print("2. 域名后缀 (domain_suffix)")
        print("3. 域名关键词 (domain_keyword)")
        print("4. IP/CIDR规则 (ip_cidr)")
        print("5. 端口规则 (port)")
        print()
        
        rule_type_choice = input("请选择规则类型 [1-5]: ").strip()
        
        rule_types = {
            "1": "domain",
            "2": "domain_suffix", 
            "3": "domain_keyword",
            "4": "ip_cidr",
            "5": "port"
        }
        
        rule_type = rule_types.get(rule_type_choice)
        if not rule_type:
            self.logger.error("无效的规则类型")
            return
        
        # 获取规则值
        if rule_type == "port":
            value_input = input("请输入端口 (例: 80 或 80,443): ").strip()
            try:
                if ',' in value_input:
                    values = [int(p.strip()) for p in value_input.split(',')]
                else:
                    values = [int(value_input)]
            except ValueError:
                self.logger.error("端口必须是数字")
                return
        else:
            value_input = input(f"请输入{rule_type}值 (多个用逗号分隔): ").strip()
            values = [v.strip() for v in value_input.split(',') if v.strip()]
        
        if not values:
            self.logger.error("规则值不能为空")
            return
        
        # 选择出站
        print()
        print("出站选择:")
        print("1. direct - 直连")
        print("2. 🚀 节点选择 - 代理")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择出站 [1-3]: ").strip()
        outbound_map = {"1": "direct", "2": "🚀 节点选择", "3": "block"}
        outbound = outbound_map.get(outbound_choice, "🚀 节点选择")
        
        # 创建规则
        new_rule = {rule_type: values, "outbound": outbound}
        custom_rules["rules"].append(new_rule)
        
        # 确保自定义规则组在启用列表中
        enabled_rules = routing_config.setdefault("enabled_rules", [])
        if "custom" not in enabled_rules:
            enabled_rules.append("custom")
        
        self.logger.info(f"✓ 已添加自定义规则: {rule_type}={values} → {outbound}")
    
    def delete_rule(self, routing_config: Dict[str, Any]):
        """删除规则组"""
        rule_sets = routing_config.get("rule_sets", {})
        
        if not rule_sets:
            self.logger.warn("暂无规则组可删除")
            return
        
        print()
        print("选择要删除的规则组:")
        rule_list = list(rule_sets.keys())
        
        for i, rule_id in enumerate(rule_list, 1):
            rule_set = rule_sets[rule_id]
            name = rule_set.get('name', rule_id)
            print(f"  {i}. {name}")
        
        try:
            choice = int(input("请选择规则组编号: ").strip()) - 1
            if 0 <= choice < len(rule_list):
                rule_id = rule_list[choice]
                confirm = input(f"确定要删除规则组 '{rule_id}' 吗? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    del rule_sets[rule_id]
                    # 从启用列表中移除
                    enabled_rules = routing_config.get("enabled_rules", [])
                    if rule_id in enabled_rules:
                        enabled_rules.remove(rule_id)
                    self.logger.info(f"✓ 已删除规则组: {rule_id}")
            else:
                self.logger.error("无效的编号")
        except ValueError:
            self.logger.error("请输入有效的数字")
    
    def manage_enabled_rules(self, routing_config: Dict[str, Any]):
        """管理启用的规则组"""
        rule_sets = routing_config.get("rule_sets", {})
        enabled_rules = routing_config.setdefault("enabled_rules", [])
        
        print()
        print("规则组启用状态:")
        
        for rule_id, rule_set in rule_sets.items():
            name = rule_set.get('name', rule_id)
            is_enabled = rule_id in enabled_rules
            status = "✓" if is_enabled else "✗"
            print(f"  {status} {name}")
        
        print()
        toggle_rule = input("请输入要切换状态的规则组ID: ").strip()
        
        if toggle_rule in rule_sets:
            if toggle_rule in enabled_rules:
                enabled_rules.remove(toggle_rule)
                self.logger.info(f"✓ 已禁用规则组: {toggle_rule}")
            else:
                enabled_rules.append(toggle_rule)
                self.logger.info(f"✓ 已启用规则组: {toggle_rule}")
        else:
            self.logger.error("规则组不存在")
    
    def view_rule_set_details(self, rule_id: str, rule_set: Dict[str, Any]):
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

    def reset_rules(self, routing_config: Dict[str, Any]):
        """重置规则为默认值"""
        confirm = input(f"{Colors.RED}确定要重置所有分流规则吗? (输入 'yes' 确认): {Colors.NC}")
        if confirm == 'yes':
            # 重新初始化路由配置
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
            routing_config.clear()
            routing_config.update(default_config)
            self.logger.info("✓ 规则已重置为默认配置") 