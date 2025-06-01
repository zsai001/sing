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


class RoutingConfigManager(BaseConfigManager):
    """路由配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
    
    def load_routing_config(self) -> Dict[str, Any]:
        """加载路由配置"""
        default_config = {
            "enabled_rules": ["china_direct", "private_direct"],
            "final_outbound": "proxy",
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
            print("9. 💾 保存并返回")
            print()
            
            choice = input("请选择 [1-9]: ").strip()
            
            if choice == "1":
                self._view_all_rule_sets(routing_config)
            elif choice == "2":
                self._edit_rule_set(routing_config)
            elif choice == "3":
                self._add_custom_rule(routing_config)
            elif choice == "4":
                self._delete_rule(routing_config)
            elif choice == "5":
                self._export_rules(routing_config)
            elif choice == "6":
                self._import_rules(routing_config)
            elif choice == "7":
                self._reset_rules(routing_config)
            elif choice == "8":
                self._advanced_routing_settings(routing_config)
            elif choice == "9":
                self.save_routing_config(routing_config)
                self.logger.info("✓ 分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def _view_all_rule_sets(self, routing_config: Dict[str, Any]):
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
    
    def _edit_rule_set(self, routing_config: Dict[str, Any]):
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
                self._edit_single_rule_set(rule_id, rule_set, routing_config)
            else:
                self.logger.error("无效的编号")
        except ValueError:
            self.logger.error("请输入有效的数字")
    
    def _edit_single_rule_set(self, rule_id: str, rule_set: Dict[str, Any], routing_config: Dict[str, Any]):
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
                self._print_rule_details(i, rule)
                
        elif choice == "4":
            return
        else:
            self.logger.error("无效选项")
    
    def _print_rule_details(self, index: int, rule: Dict[str, Any]):
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
    
    def _add_custom_rule(self, routing_config: Dict[str, Any]):
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
        print("2. proxy - 代理")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择出站 [1-3]: ").strip()
        outbound_map = {"1": "direct", "2": "proxy", "3": "block"}
        outbound = outbound_map.get(outbound_choice, "proxy")
        
        # 创建规则
        new_rule = {rule_type: values, "outbound": outbound}
        custom_rules["rules"].append(new_rule)
        
        # 确保自定义规则组在启用列表中
        enabled_rules = routing_config.setdefault("enabled_rules", [])
        if "custom" not in enabled_rules:
            enabled_rules.append("custom")
        
        self.logger.info(f"✓ 已添加自定义规则: {rule_type}={values} → {outbound}")
    
    def _delete_rule(self, routing_config: Dict[str, Any]):
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
    
    def _advanced_routing_settings(self, routing_config: Dict[str, Any]):
        """高级路由设置"""
        print()
        print(f"{Colors.CYAN}⚙️  高级路由设置{Colors.NC}")
        print()
        
        current_final = routing_config.get("final_outbound", "proxy")
        print(f"当前默认出站: {current_final}")
        print()
        
        print("1. 设置默认出站")
        print("2. 规则组启用/禁用")
        print("3. 返回上级")
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            print("默认出站选项:")
            print("1. proxy - 走代理")
            print("2. direct - 直连")
            print("3. block - 拦截")
            
            outbound_choice = input("请选择 [1-3]: ").strip()
            outbound_map = {"1": "proxy", "2": "direct", "3": "block"}
            new_outbound = outbound_map.get(outbound_choice)
            
            if new_outbound:
                routing_config["final_outbound"] = new_outbound
                self.logger.info(f"✓ 默认出站设置为: {new_outbound}")
            else:
                self.logger.error("无效选择")
                
        elif choice == "2":
            self._manage_enabled_rules(routing_config)
        elif choice == "3":
            return
        else:
            self.logger.error("无效选项")
    
    def _manage_enabled_rules(self, routing_config: Dict[str, Any]):
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
                
                # 设置出站
                route_rule["outbound"] = rule.get("outbound", "proxy")
                route_rules.append(route_rule)
        
        route_config = {
            "auto_detect_interface": True,
            "final": routing_config.get("final_outbound", "proxy"),
            "rules": route_rules
        }
        
        return route_config
    
    def configure_media_routing_rules(self):
        """配置媒体分流规则管理"""
        print()
        print(f"{Colors.CYAN}🎬 媒体分流管理{Colors.NC}")
        print("管理流媒体、音乐、社交媒体等媒体服务的分流规则")
        print()
        
        routing_config = self.load_routing_config()
        rule_sets = routing_config.get("rule_sets", {})
        
        # 媒体相关的规则集
        media_rule_sets = {
            "streaming_global": "🎬 国际流媒体",
            "music_streaming": "🎵 音乐流媒体", 
            "social_media": "📱 社交媒体",
            "ai_services": "🤖 AI服务",
            "news_media": "📰 新闻媒体"
        }
        
        while True:
            print(f"{Colors.YELLOW}当前媒体分流规则状态:{Colors.NC}")
            print()
            for rule_id, rule_name in media_rule_sets.items():
                if rule_id in rule_sets:
                    rule_set = rule_sets[rule_id]
                    status = f"{Colors.GREEN}启用{Colors.NC}" if rule_set.get("enabled", False) else f"{Colors.RED}禁用{Colors.NC}"
                    rules_count = len(rule_set.get("rules", []))
                    priority = rule_set.get("priority", 0)
                    print(f"  {rule_name}: {status} ({rules_count} 条规则, 优先级: {priority})")
                else:
                    print(f"  {rule_name}: {Colors.YELLOW}未配置{Colors.NC}")
            print()
            
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
                # 一键启用所有媒体分流
                for rule_id in media_rule_sets.keys():
                    if rule_id in rule_sets:
                        rule_sets[rule_id]["enabled"] = True
                        if rule_id not in routing_config.get("enabled_rules", []):
                            routing_config.setdefault("enabled_rules", []).append(rule_id)
                self.logger.info("✓ 已启用所有媒体分流规则")
                
            elif choice == "2":
                # 一键禁用所有媒体分流
                for rule_id in media_rule_sets.keys():
                    if rule_id in rule_sets:
                        rule_sets[rule_id]["enabled"] = False
                        if rule_id in routing_config.get("enabled_rules", []):
                            routing_config["enabled_rules"].remove(rule_id)
                self.logger.info("✓ 已禁用所有媒体分流规则")
                
            elif choice == "3":
                # 单独管理规则组
                print("\n选择要管理的媒体规则组:")
                rule_list = list(media_rule_sets.items())
                for i, (rule_id, rule_name) in enumerate(rule_list, 1):
                    status = "启用" if rule_sets.get(rule_id, {}).get("enabled", False) else "禁用"
                    print(f"{i}. {rule_name} ({status})")
                
                try:
                    choice_idx = int(input("请选择规则组编号: ")) - 1
                    if 0 <= choice_idx < len(rule_list):
                        rule_id, rule_name = rule_list[choice_idx]
                        if rule_id in rule_sets:
                            self._manage_single_media_rule(rule_id, rule_sets[rule_id], routing_config)
                        else:
                            self.logger.error("该规则组未配置")
                    else:
                        self.logger.error("无效选择")
                except ValueError:
                    self.logger.error("请输入有效数字")
                    
            elif choice == "4":
                # 查看规则详情
                print("\n选择要查看的媒体规则组:")
                rule_list = list(media_rule_sets.items())
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
                    
            elif choice == "5":
                # 添加自定义媒体规则
                self._add_custom_media_rule(routing_config)
                
            elif choice == "6":
                # 设置优先级
                self._set_media_rule_priorities(rule_sets, media_rule_sets)
                
            elif choice == "7":
                self.save_routing_config(routing_config)
                self.logger.info("✓ 媒体分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def configure_application_routing_rules(self):
        """配置程序分流规则管理"""
        print()
        print(f"{Colors.CYAN}💻 程序分流管理{Colors.NC}")
        print("管理开发工具、办公软件、游戏平台等应用程序的分流规则")
        print()
        
        routing_config = self.load_routing_config()
        rule_sets = routing_config.get("rule_sets", {})
        
        # 程序相关的规则集
        app_rule_sets = {
            "development_tools": "🔧 开发工具",
            "office_tools": "📄 办公软件",
            "gaming_platforms": "🎮 游戏平台",
            "messaging_apps": "💬 聊天通讯"
        }
        
        while True:
            print(f"{Colors.YELLOW}当前程序分流规则状态:{Colors.NC}")
            print()
            for rule_id, rule_name in app_rule_sets.items():
                if rule_id in rule_sets:
                    rule_set = rule_sets[rule_id]
                    status = f"{Colors.GREEN}启用{Colors.NC}" if rule_set.get("enabled", False) else f"{Colors.RED}禁用{Colors.NC}"
                    rules_count = len(rule_set.get("rules", []))
                    priority = rule_set.get("priority", 0)
                    print(f"  {rule_name}: {status} ({rules_count} 条规则, 优先级: {priority})")
                else:
                    print(f"  {rule_name}: {Colors.YELLOW}未配置{Colors.NC}")
            print()
            
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
                # 一键启用所有程序分流
                for rule_id in app_rule_sets.keys():
                    if rule_id in rule_sets:
                        rule_sets[rule_id]["enabled"] = True
                        if rule_id not in routing_config.get("enabled_rules", []):
                            routing_config.setdefault("enabled_rules", []).append(rule_id)
                self.logger.info("✓ 已启用所有程序分流规则")
                
            elif choice == "2":
                # 一键禁用所有程序分流
                for rule_id in app_rule_sets.keys():
                    if rule_id in rule_sets:
                        rule_sets[rule_id]["enabled"] = False
                        if rule_id in routing_config.get("enabled_rules", []):
                            routing_config["enabled_rules"].remove(rule_id)
                self.logger.info("✓ 已禁用所有程序分流规则")
                
            elif choice == "3":
                # 单独管理规则组
                print("\n选择要管理的程序规则组:")
                rule_list = list(app_rule_sets.items())
                for i, (rule_id, rule_name) in enumerate(rule_list, 1):
                    status = "启用" if rule_sets.get(rule_id, {}).get("enabled", False) else "禁用"
                    print(f"{i}. {rule_name} ({status})")
                
                try:
                    choice_idx = int(input("请选择规则组编号: ")) - 1
                    if 0 <= choice_idx < len(rule_list):
                        rule_id, rule_name = rule_list[choice_idx]
                        if rule_id in rule_sets:
                            self._manage_single_app_rule(rule_id, rule_sets[rule_id], routing_config)
                        else:
                            self.logger.error("该规则组未配置")
                    else:
                        self.logger.error("无效选择")
                except ValueError:
                    self.logger.error("请输入有效数字")
                    
            elif choice == "4":
                # 查看规则详情
                print("\n选择要查看的程序规则组:")
                rule_list = list(app_rule_sets.items())
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
                    
            elif choice == "5":
                # 添加自定义程序规则
                self._add_custom_app_rule(routing_config)
                
            elif choice == "6":
                # 设置优先级
                self._set_app_rule_priorities(rule_sets, app_rule_sets)
                
            elif choice == "7":
                self.save_routing_config(routing_config)
                self.logger.info("✓ 程序分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def _export_rules(self, routing_config: Dict[str, Any]):
        """导出规则"""
        export_file = self.paths.config_dir / "routing_rules_export.json"
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(routing_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✓ 规则已导出到: {export_file}")
        except Exception as e:
            self.logger.error(f"导出失败: {e}")
    
    def _import_rules(self, routing_config: Dict[str, Any]):
        """导入规则"""
        import_file = input("请输入要导入的文件路径: ").strip()
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 合并规则
            if 'rule_sets' in imported_config:
                routing_config.setdefault('rule_sets', {})
                routing_config['rule_sets'].update(imported_config['rule_sets'])
                self.logger.info("✓ 规则导入成功")
            else:
                self.logger.error("导入文件格式不正确")
        except Exception as e:
            self.logger.error(f"导入失败: {e}")
    
    def _reset_rules(self, routing_config: Dict[str, Any]):
        """重置规则为默认值"""
        confirm = input(f"{Colors.RED}确定要重置所有分流规则吗? (输入 'yes' 确认): {Colors.NC}")
        if confirm == 'yes':
            # 重新初始化路由配置
            default_config = {
                "enabled_rules": ["china_direct", "private_direct"],
                "final_outbound": "proxy",
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
    
    def _manage_single_media_rule(self, rule_id: str, rule_set: Dict[str, Any], routing_config: Dict[str, Any]):
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
    
    def _manage_single_app_rule(self, rule_id: str, rule_set: Dict[str, Any], routing_config: Dict[str, Any]):
        """管理单个程序规则"""
        self._manage_single_media_rule(rule_id, rule_set, routing_config)  # 逻辑相同
    
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
        print("1. proxy - 走代理")
        print("2. direct - 直连")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择 [1-3]: ").strip()
        outbound_map = {"1": "proxy", "2": "direct", "3": "block"}
        outbound = outbound_map.get(outbound_choice, "proxy")
        
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
        print("1. proxy - 走代理")
        print("2. direct - 直连")
        print("3. block - 拦截")
        
        outbound_choice = input("请选择 [1-3]: ").strip()
        outbound_map = {"1": "proxy", "2": "direct", "3": "block"}
        outbound = outbound_map.get(outbound_choice, "proxy")
        
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
    
    def _set_media_rule_priorities(self, rule_sets: Dict[str, Any], media_rule_sets: Dict[str, str]):
        """设置媒体规则优先级"""
        print()
        print(f"{Colors.CYAN}设置媒体规则优先级{Colors.NC}")
        print("数字越小优先级越高，建议范围: 1-500")
        print()
        
        for rule_id, rule_name in media_rule_sets.items():
            if rule_id in rule_sets:
                current_priority = rule_sets[rule_id].get("priority", 100)
                try:
                    new_priority = input(f"{rule_name} (当前: {current_priority}): ").strip()
                    if new_priority:
                        rule_sets[rule_id]["priority"] = int(new_priority)
                        self.logger.info(f"✓ {rule_name} 优先级设置为: {new_priority}")
                except ValueError:
                    self.logger.error(f"跳过 {rule_name}: 输入无效")
    
    def _set_app_rule_priorities(self, rule_sets: Dict[str, Any], app_rule_sets: Dict[str, str]):
        """设置程序规则优先级"""
        print()
        print(f"{Colors.CYAN}设置程序规则优先级{Colors.NC}")
        print("数字越小优先级越高，建议范围: 1-500")
        print()
        
        for rule_id, rule_name in app_rule_sets.items():
            if rule_id in rule_sets:
                current_priority = rule_sets[rule_id].get("priority", 100)
                try:
                    new_priority = input(f"{rule_name} (当前: {current_priority}): ").strip()
                    if new_priority:
                        rule_sets[rule_id]["priority"] = int(new_priority)
                        self.logger.info(f"✓ {rule_name} 优先级设置为: {new_priority}")
                except ValueError:
                    self.logger.error(f"跳过 {rule_name}: 输入无效") 