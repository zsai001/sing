#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DNS和FakeIP配置管理模块
DNS and FakeIP Configuration Manager
"""

import json
from typing import Dict, Any
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager


class DNSConfigManager(BaseConfigManager):
    """DNS和FakeIP配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
    
    def configure_dns_fakeip(self):
        """配置DNS和FakeIP - 直接修改sing-box配置"""
        print()
        print(f"{Colors.CYAN}🌐 DNS & FakeIP 配置{Colors.NC}")
        print("配置DNS服务器和FakeIP功能，优化域名解析")
        print()
        
        # 读取当前sing-box配置
        config = self.load_sing_box_config()
        if not config:
            self.logger.error("未找到 sing-box 配置文件")
            return
        
        dns_config = config.get("dns", {})
        fakeip_config = dns_config.get("fakeip", {})
        
        print(f"{Colors.YELLOW}当前DNS配置:{Colors.NC}")
        
        # 显示DNS服务器
        servers = dns_config.get("servers", [])
        print(f"  DNS服务器数量: {len(servers)}")
        for server in servers[:3]:  # 只显示前3个
            tag = server.get("tag", "unknown")
            address = server.get("address", "unknown")
            print(f"    {tag}: {address}")
        if len(servers) > 3:
            print(f"    ... 还有 {len(servers) - 3} 个服务器")
        
        # 显示FakeIP状态
        fakeip_enabled = fakeip_config.get("enabled", False)
        print(f"  FakeIP状态: {'启用' if fakeip_enabled else '禁用'}")
        if fakeip_enabled:
            print(f"  IPv4范围: {fakeip_config.get('inet4_range', '198.18.0.0/15')}")
            print(f"  IPv6范围: {fakeip_config.get('inet6_range', 'fc00::/18')}")
        
        print()
        
        while True:
            print("配置选项:")
            print("1. 配置DNS服务器")
            print("2. 启用/禁用 FakeIP")
            print("3. 设置FakeIP范围")
            print("4. 配置DNS规则")
            print("5. 保存并返回")
            print()
            
            choice = input("请选择 [1-5]: ").strip()
            
            if choice == "1":
                self._configure_dns_servers(config)
            elif choice == "2":
                self._toggle_fakeip(config)
            elif choice == "3":
                self._configure_fakeip_range(config)
            elif choice == "4":
                self._configure_dns_rules(config)
            elif choice == "5":
                self.save_config_and_restart(config, "DNS配置已更新")
                return
            else:
                self.logger.error("无效选项")
    
    def _configure_dns_servers(self, config: Dict[str, Any]):
        """配置DNS服务器"""
        dns_config = config.setdefault("dns", {})
        servers = dns_config.setdefault("servers", [])
        
        print()
        print("当前DNS服务器:")
        for i, server in enumerate(servers, 1):
            tag = server.get("tag", f"server{i}")
            address = server.get("address", "unknown")
            print(f"  {i}. {tag}: {address}")
        
        print()
        print("1. 添加DNS服务器")
        print("2. 删除DNS服务器")
        print("3. 重置为默认服务器")
        print("4. 返回上级")
        
        sub_choice = input("请选择 [1-4]: ").strip()
        
        if sub_choice == "1":
            tag = input("服务器标签: ").strip()
            address = input("服务器地址 (如 https://1.1.1.1/dns-query): ").strip()
            if tag and address:
                servers.append({"tag": tag, "address": address})
                self.logger.info(f"✓ 已添加DNS服务器: {tag}")
        
        elif sub_choice == "2":
            if servers:
                try:
                    index = int(input("输入要删除的服务器编号: ").strip()) - 1
                    if 0 <= index < len(servers):
                        removed = servers.pop(index)
                        self.logger.info(f"✓ 已删除DNS服务器: {removed.get('tag', 'unknown')}")
                    else:
                        self.logger.error("无效编号")
                except ValueError:
                    self.logger.error("请输入有效数字")
            else:
                self.logger.warn("没有可删除的DNS服务器")
        
        elif sub_choice == "3":
            dns_config["servers"] = [
                {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                {"tag": "google", "address": "https://8.8.8.8/dns-query"},
                {"tag": "local", "address": "223.5.5.5"}
            ]
            self.logger.info("✓ 已重置为默认DNS服务器")
    
    def _toggle_fakeip(self, config: Dict[str, Any]):
        """切换FakeIP状态"""
        dns_config = config.setdefault("dns", {})
        fakeip_config = dns_config.setdefault("fakeip", {})
        
        current_enabled = fakeip_config.get("enabled", False)
        fakeip_config["enabled"] = not current_enabled
        
        if not current_enabled:
            # 启用FakeIP时设置默认范围
            fakeip_config.setdefault("inet4_range", "198.18.0.0/15")
            fakeip_config.setdefault("inet6_range", "fc00::/18")
        
        status = "启用" if not current_enabled else "禁用"
        self.logger.info(f"✓ FakeIP已{status}")
    
    def _configure_fakeip_range(self, config: Dict[str, Any]):
        """配置FakeIP地址范围"""
        dns_config = config.setdefault("dns", {})
        fakeip_config = dns_config.setdefault("fakeip", {})
        
        current_v4 = fakeip_config.get("inet4_range", "198.18.0.0/15")
        current_v6 = fakeip_config.get("inet6_range", "fc00::/18")
        
        print()
        print(f"当前IPv4范围: {current_v4}")
        print(f"当前IPv6范围: {current_v6}")
        print()
        
        new_v4 = input(f"设置IPv4范围 (当前: {current_v4}, 留空不修改): ").strip()
        if new_v4:
            fakeip_config["inet4_range"] = new_v4
            self.logger.info(f"✓ IPv4范围设置为: {new_v4}")
        
        new_v6 = input(f"设置IPv6范围 (当前: {current_v6}, 留空不修改): ").strip()
        if new_v6:
            fakeip_config["inet6_range"] = new_v6
            self.logger.info(f"✓ IPv6范围设置为: {new_v6}")
    
    def _configure_dns_rules(self, config: Dict[str, Any]):
        """配置DNS规则"""
        dns_config = config.setdefault("dns", {})
        rules = dns_config.setdefault("rules", [])
        
        print()
        print("当前DNS规则:")
        for i, rule in enumerate(rules, 1):
            server = rule.get("server", "unknown")
            conditions = []
            if "domain_suffix" in rule:
                conditions.append(f"域名后缀: {rule['domain_suffix'][:2]}...")
            if "clash_mode" in rule:
                conditions.append(f"模式: {rule['clash_mode']}")
            print(f"  {i}. 服务器: {server}, 条件: {', '.join(conditions)}")
        
        print()
        print("1. 添加DNS规则")
        print("2. 删除DNS规则")
        print("3. 重置为默认规则")
        print("4. 返回上级")
        
        sub_choice = input("请选择 [1-4]: ").strip()
        
        if sub_choice == "1":
            server = input("DNS服务器标签: ").strip()
            if server:
                print("规则类型:")
                print("1. 域名后缀")
                print("2. Clash模式")
                rule_type = input("选择规则类型 [1-2]: ").strip()
                
                if rule_type == "1":
                    suffixes = input("域名后缀 (多个用逗号分隔): ").strip()
                    if suffixes:
                        suffix_list = [s.strip() for s in suffixes.split(",")]
                        rules.append({"domain_suffix": suffix_list, "server": server})
                        self.logger.info(f"✓ 已添加域名后缀规则")
                elif rule_type == "2":
                    mode = input("Clash模式 (direct/global): ").strip()
                    if mode in ["direct", "global"]:
                        rules.append({"clash_mode": mode, "server": server})
                        self.logger.info(f"✓ 已添加Clash模式规则")
        
        elif sub_choice == "2":
            if rules:
                try:
                    index = int(input("输入要删除的规则编号: ").strip()) - 1
                    if 0 <= index < len(rules):
                        rules.pop(index)
                        self.logger.info("✓ 已删除DNS规则")
                    else:
                        self.logger.error("无效编号")
                except ValueError:
                    self.logger.error("请输入有效数字")
        
        elif sub_choice == "3":
            dns_config["rules"] = [
                {"domain_suffix": [".cn", ".中国"], "server": "local"},
                {"clash_mode": "direct", "server": "local"},
                {"clash_mode": "global", "server": "cloudflare"}
            ]
            self.logger.info("✓ 已重置为默认DNS规则")
    
    def generate_dns_config(self) -> Dict[str, Any]:
        """根据配置生成DNS配置"""
        config = self.load_sing_box_config()
        dns_config = config.get("dns", {})
        
        if not dns_config:
            return {
                "servers": [
                    {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                    {"tag": "local", "address": "223.5.5.5"}
                ],
                "rules": [
                    {"domain_suffix": [".cn", ".中国"], "server": "local"},
                    {"clash_mode": "direct", "server": "local"},
                    {"clash_mode": "global", "server": "cloudflare"}
                ],
                "final": "cloudflare"
            }
        
        return dns_config 