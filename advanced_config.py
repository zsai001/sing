#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级配置管理模块 - sing-box 高级功能配置
SingTool Advanced Config Module
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from utils import Colors, Logger
from paths import PathManager

class AdvancedConfigManager:
    """高级配置管理类 - 管理代理端口、DNS、TUN模式等高级设置"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
        self._init_advanced_config()
    
    def _init_advanced_config(self):
        """初始化高级配置文件"""
        if not self.advanced_config_file.exists():
            default_config = {
                "version": "1.0",
                "proxy_ports": {
                    "mixed_port": 7890,
                    "http_port": 7891,
                    "socks_port": 7892,
                    "enabled": ["mixed"]  # mixed, http, socks
                },
                "dns": {
                    "fakeip_enabled": False,
                    "fakeip_range": "198.18.0.0/15",
                    "fakeip_range_v6": "fc00::/18",
                    "servers": [
                        {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                        {"tag": "google", "address": "https://8.8.8.8/dns-query"},
                        {"tag": "local", "address": "223.5.5.5"}
                    ],
                    "rules": [
                        {"domain_suffix": [".cn", ".中国"], "server": "local"},
                        {"clash_mode": "direct", "server": "local"},
                        {"clash_mode": "global", "server": "cloudflare"}
                    ],
                    "final": "cloudflare"
                },
                "tun": {
                    "enabled": False,
                    "interface_name": "utun-sing",
                    "inet4_address": "172.19.0.1/30",
                    "inet6_address": "fdfe:dcba:9876::1/126",
                    "mtu": 9000,
                    "auto_route": True,
                    "strict_route": True,
                    "stack": "system"
                },
                "clash_api": {
                    "enabled": True,
                    "external_controller": "127.0.0.1:9090",
                    "external_ui": "ui",
                    "secret": "",
                    "default_mode": "rule"
                },
                "experimental": {
                    "cache_enabled": True,
                    "cache_file": "cache.db",
                    "store_fakeip": False
                },
                "routing": {
                    "enabled_rules": ["china_direct", "private_direct", "block_ads"],
                    "rule_sets": {
                        "china_direct": {
                            "name": "中国大陆直连",
                            "enabled": True,
                            "priority": 100,
                            "rules": [
                                {"domain_suffix": [".cn", ".中国", ".公司", ".网络"], "outbound": "direct"},
                                {"domain_keyword": ["cn", "china", "baidu", "qq", "taobao", "jd", "tmall"], "outbound": "direct"},
                                {"domain": ["qq.com", "baidu.com", "taobao.com", "tmall.com", "jd.com", "weibo.com"], "outbound": "direct"}
                            ]
                        },
                        "private_direct": {
                            "name": "私有地址直连",
                            "enabled": True,
                            "priority": 200,
                            "rules": [
                                {"ip_cidr": ["127.0.0.0/8", "169.254.0.0/16", "224.0.0.0/4", "::1/128", "fc00::/7", "fe80::/10", "ff00::/8"], "outbound": "direct"},
                                {"ip_cidr": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"], "outbound": "direct"}
                            ]
                        },
                        "block_ads": {
                            "name": "广告拦截",
                            "enabled": True,
                            "priority": 300,
                            "rules": [
                                {"domain_suffix": [".doubleclick.net", ".googleadservices.com", ".googlesyndication.com"], "outbound": "block"},
                                {"domain_keyword": ["analytics", "ads", "adservice", "adsystem"], "outbound": "block"}
                            ]
                        },
                        "streaming_global": {
                            "name": "国际流媒体",
                            "enabled": False,
                            "priority": 50,
                            "rules": [
                                {"domain_suffix": [".netflix.com", ".nflxso.net", ".nflxext.com", ".nflximg.net"], "outbound": "proxy"},
                                {"domain_suffix": [".youtube.com", ".googlevideo.com", ".ytimg.com", ".youtu.be"], "outbound": "proxy"},
                                {"domain_suffix": [".hulu.com", ".hulustream.com", ".hulu.hb.omtrdc.net"], "outbound": "proxy"},
                                {"domain_suffix": [".disney.com", ".disneyplus.com", ".dssott.com", ".bamgrid.com"], "outbound": "proxy"},
                                {"domain_suffix": [".primevideo.com", ".amazon.com", ".amazonvideo.com"], "outbound": "proxy"},
                                {"domain_suffix": [".hbomax.com", ".hbo.com", ".max.com"], "outbound": "proxy"},
                                {"domain_suffix": [".twitch.tv", ".ttvnw.net", ".jtvnw.net"], "outbound": "proxy"},
                                {"domain_suffix": [".crunchyroll.com", ".vrv.co"], "outbound": "proxy"},
                                {"domain_keyword": ["netflix", "youtube", "hulu", "disney", "primevideo", "hbomax", "twitch"], "outbound": "proxy"}
                            ]
                        },
                        "music_streaming": {
                            "name": "音乐流媒体",
                            "enabled": False,
                            "priority": 60,
                            "rules": [
                                {"domain_suffix": [".spotify.com", ".scdn.co", ".spoti.fi"], "outbound": "proxy"},
                                {"domain_suffix": [".apple.com", ".mzstatic.com", ".itunes.apple.com"], "outbound": "proxy"},
                                {"domain_suffix": [".pandora.com", ".p-cdn.com"], "outbound": "proxy"},
                                {"domain_suffix": [".soundcloud.com", ".sndcdn.com"], "outbound": "proxy"},
                                {"domain_suffix": [".tidal.com"], "outbound": "proxy"},
                                {"domain_keyword": ["spotify", "applemusic", "pandora", "soundcloud", "tidal"], "outbound": "proxy"}
                            ]
                        },
                        "social_media": {
                            "name": "社交媒体",
                            "enabled": False,
                            "priority": 70,
                            "rules": [
                                {"domain_suffix": [".twitter.com", ".twimg.com", ".t.co", ".x.com"], "outbound": "proxy"},
                                {"domain_suffix": [".facebook.com", ".fbcdn.net", ".fb.com"], "outbound": "proxy"},
                                {"domain_suffix": [".instagram.com", ".cdninstagram.com"], "outbound": "proxy"},
                                {"domain_suffix": [".tiktok.com", ".musical.ly", ".tiktokcdn.com"], "outbound": "proxy"},
                                {"domain_suffix": [".snapchat.com", ".snap.com"], "outbound": "proxy"},
                                {"domain_suffix": [".reddit.com", ".redd.it", ".redditstatic.com"], "outbound": "proxy"},
                                {"domain_suffix": [".linkedin.com", ".licdn.com"], "outbound": "proxy"},
                                {"domain_keyword": ["twitter", "facebook", "instagram", "tiktok", "snapchat", "reddit", "linkedin"], "outbound": "proxy"}
                            ]
                        },
                        "messaging_apps": {
                            "name": "聊天通讯",
                            "enabled": False,
                            "priority": 80,
                            "rules": [
                                {"domain_suffix": [".telegram.org", ".t.me", ".tg.dev"], "outbound": "proxy"},
                                {"domain_suffix": [".whatsapp.com", ".whatsapp.net"], "outbound": "proxy"},
                                {"domain_suffix": [".discord.com", ".discordapp.com", ".discord.gg"], "outbound": "proxy"},
                                {"domain_suffix": [".signal.org"], "outbound": "proxy"},
                                {"domain_suffix": [".line.me", ".line-apps.com", ".line-scdn.net"], "outbound": "proxy"},
                                {"domain_suffix": [".skype.com", ".skypeassets.com"], "outbound": "proxy"},
                                {"domain_suffix": [".slack.com", ".slack-edge.com"], "outbound": "proxy"},
                                {"domain_keyword": ["telegram", "whatsapp", "discord", "signal", "line", "skype", "slack"], "outbound": "proxy"}
                            ]
                        },
                        "development_tools": {
                            "name": "开发工具",
                            "enabled": False,
                            "priority": 90,
                            "rules": [
                                {"domain_suffix": [".github.com", ".githubusercontent.com", ".githubassets.com"], "outbound": "proxy"},
                                {"domain_suffix": [".gitlab.com"], "outbound": "proxy"},
                                {"domain_suffix": [".stackoverflow.com", ".stackexchange.com"], "outbound": "proxy"},
                                {"domain_suffix": [".npmjs.com", ".npmjs.org"], "outbound": "proxy"},
                                {"domain_suffix": [".docker.com", ".docker.io"], "outbound": "proxy"},
                                {"domain_suffix": [".pypi.org", ".pythonhosted.org"], "outbound": "proxy"},
                                {"domain_suffix": [".golang.org", ".golang.dev"], "outbound": "proxy"},
                                {"domain_suffix": [".rustup.rs", ".crates.io"], "outbound": "proxy"},
                                {"domain_keyword": ["github", "gitlab", "stackoverflow", "npm", "docker", "pypi", "golang", "rust"], "outbound": "proxy"}
                            ]
                        },
                        "gaming_platforms": {
                            "name": "游戏平台",
                            "enabled": False,
                            "priority": 110,
                            "rules": [
                                {"domain_suffix": [".steampowered.com", ".steamcommunity.com", ".steamgames.com"], "outbound": "proxy"},
                                {"domain_suffix": [".epicgames.com", ".unrealengine.com"], "outbound": "proxy"},
                                {"domain_suffix": [".battle.net", ".blizzard.com"], "outbound": "proxy"},
                                {"domain_suffix": [".ea.com", ".origin.com"], "outbound": "proxy"},
                                {"domain_suffix": [".ubisoft.com", ".ubi.com"], "outbound": "proxy"},
                                {"domain_suffix": [".riotgames.com", ".leagueoflegends.com"], "outbound": "proxy"},
                                {"domain_suffix": [".minecraft.net", ".mojang.com"], "outbound": "proxy"},
                                {"domain_keyword": ["steam", "epic", "battle", "origin", "ubisoft", "riot", "minecraft"], "outbound": "proxy"}
                            ]
                        },
                        "office_tools": {
                            "name": "办公软件",
                            "enabled": False,
                            "priority": 120,
                            "rules": [
                                {"domain_suffix": [".office.com", ".office365.com", ".outlook.com", ".live.com"], "outbound": "proxy"},
                                {"domain_suffix": [".microsoft.com", ".microsoftonline.com", ".windows.net"], "outbound": "proxy"},
                                {"domain_suffix": [".google.com", ".googleapis.com", ".googleusercontent.com"], "outbound": "proxy"},
                                {"domain_suffix": [".zoom.us", ".zoom.com"], "outbound": "proxy"},
                                {"domain_suffix": [".teams.microsoft.com", ".skype.com"], "outbound": "proxy"},
                                {"domain_suffix": [".dropbox.com", ".dropboxusercontent.com"], "outbound": "proxy"},
                                {"domain_suffix": [".notion.so", ".notion.com"], "outbound": "proxy"},
                                {"domain_keyword": ["office365", "microsoft", "google", "zoom", "teams", "dropbox", "notion"], "outbound": "proxy"}
                            ]
                        },
                        "ai_services": {
                            "name": "AI服务",
                            "enabled": False,
                            "priority": 40,
                            "rules": [
                                {"domain_suffix": [".openai.com", ".chatgpt.com"], "outbound": "proxy"},
                                {"domain_suffix": [".anthropic.com", ".claude.ai"], "outbound": "proxy"},
                                {"domain_suffix": [".midjourney.com"], "outbound": "proxy"},
                                {"domain_suffix": [".character.ai"], "outbound": "proxy"},
                                {"domain_suffix": [".replicate.com"], "outbound": "proxy"},
                                {"domain_suffix": [".huggingface.co"], "outbound": "proxy"},
                                {"domain_keyword": ["openai", "chatgpt", "anthropic", "claude", "midjourney", "character", "replicate", "huggingface"], "outbound": "proxy"}
                            ]
                        },
                        "news_media": {
                            "name": "新闻媒体",
                            "enabled": False,
                            "priority": 130,
                            "rules": [
                                {"domain_suffix": [".bbc.com", ".bbc.co.uk"], "outbound": "proxy"},
                                {"domain_suffix": [".nytimes.com", ".nyti.ms"], "outbound": "proxy"},
                                {"domain_suffix": [".cnn.com"], "outbound": "proxy"},
                                {"domain_suffix": [".reuters.com"], "outbound": "proxy"},
                                {"domain_suffix": [".theguardian.com"], "outbound": "proxy"},
                                {"domain_suffix": [".wsj.com"], "outbound": "proxy"},
                                {"domain_suffix": [".ft.com"], "outbound": "proxy"},
                                {"domain_keyword": ["bbc", "nytimes", "cnn", "reuters", "guardian", "wsj"], "outbound": "proxy"}
                            ]
                        },
                        "streaming": {
                            "name": "流媒体代理(旧)",
                            "enabled": False,
                            "priority": 50,
                            "rules": [
                                {"domain_suffix": [".netflix.com", ".youtube.com", ".hulu.com", ".disney.com"], "outbound": "proxy"},
                                {"domain_keyword": ["netflix", "youtube", "hulu", "disney"], "outbound": "proxy"}
                            ]
                        },
                        "custom": {
                            "name": "自定义规则",
                            "enabled": True,
                            "priority": 400,
                            "rules": []
                        }
                    },
                    "final_outbound": "proxy"
                }
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
        with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def configure_proxy_ports(self):
        """配置代理端口"""
        print()
        print(f"{Colors.CYAN}🌐 代理端口配置{Colors.NC}")
        print("配置不同类型的代理端口，可以同时启用多个")
        print()
        
        config = self.load_advanced_config()
        proxy_config = config.get("proxy_ports", {})
        
        print(f"{Colors.YELLOW}当前配置:{Colors.NC}")
        print(f"  混合端口 (HTTP+SOCKS): {proxy_config.get('mixed_port', 7890)}")
        print(f"  HTTP 端口: {proxy_config.get('http_port', 7891)}")
        print(f"  SOCKS 端口: {proxy_config.get('socks_port', 7892)}")
        enabled = proxy_config.get('enabled', ['mixed'])
        print(f"  已启用: {', '.join(enabled)}")
        print()
        
        print("选择要配置的端口类型:")
        print("1. 混合端口 (HTTP+SOCKS5)")
        print("2. 独立HTTP端口") 
        print("3. 独立SOCKS端口")
        print("4. 启用/禁用端口")
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
            print()
            print("选择要启用的端口类型 (可多选，用空格分隔):")
            print("  mixed - 混合端口 (推荐)")
            print("  http  - HTTP端口")
            print("  socks - SOCKS端口")
            print()
            
            enabled_input = input("请输入 (例: mixed http): ").strip()
            if enabled_input:
                enabled_types = enabled_input.split()
                valid_types = [t for t in enabled_types if t in ['mixed', 'http', 'socks']]
                if valid_types:
                    proxy_config['enabled'] = valid_types
                    self.logger.info(f"✓ 已启用端口类型: {', '.join(valid_types)}")
                else:
                    self.logger.error("无效的端口类型")
                    
        elif choice == "5":
            config['proxy_ports'] = proxy_config
            self.save_advanced_config(config)
            self.logger.info("✓ 代理端口配置已保存")
            return
        else:
            self.logger.error("无效选项")
    
    def configure_dns_fakeip(self):
        """配置DNS和FakeIP"""
        print()
        print(f"{Colors.CYAN}🏠 DNS 和 FakeIP 配置{Colors.NC}")
        print()
        
        config = self.load_advanced_config()
        dns_config = config.get("dns", {})
        
        print(f"{Colors.YELLOW}当前DNS配置:{Colors.NC}")
        print(f"  FakeIP: {'启用' if dns_config.get('fakeip_enabled', False) else '禁用'}")
        if dns_config.get('fakeip_enabled', False):
            print(f"  FakeIP范围: {dns_config.get('fakeip_range', '198.18.0.0/15')}")
            print(f"  FakeIP IPv6: {dns_config.get('fakeip_range_v6', 'fc00::/18')}")
        
        servers = dns_config.get('servers', [])
        print(f"  DNS服务器: {len(servers)} 个")
        for server in servers:
            print(f"    - {server.get('tag', 'unknown')}: {server.get('address', 'unknown')}")
        print()
        
        print("配置选项:")
        print("1. 启用/禁用 FakeIP")
        print("2. 设置 FakeIP 范围")
        print("3. 添加 DNS 服务器")
        print("4. 删除 DNS 服务器")
        print("5. 保存并返回")
        print()
        
        choice = input("请选择 [1-5]: ").strip()
        
        if choice == "1":
            current = dns_config.get('fakeip_enabled', False)
            toggle = input(f"FakeIP当前{'启用' if current else '禁用'}，是否切换? (y/N): ").strip().lower()
            if toggle in ['y', 'yes']:
                dns_config['fakeip_enabled'] = not current
                status = '启用' if not current else '禁用'
                self.logger.info(f"✓ FakeIP已{status}")
                
                if not current:  # 如果要启用FakeIP
                    print()
                    print(f"{Colors.YELLOW}FakeIP说明:{Colors.NC}")
                    print("FakeIP可以提高DNS解析性能，但可能与某些应用不兼容")
                    print("建议在了解其工作原理后再启用")
                    
        elif choice == "2":
            if dns_config.get('fakeip_enabled', False):
                current_range = dns_config.get('fakeip_range', '198.18.0.0/15')
                new_range = input(f"设置FakeIP范围 (当前: {current_range}): ").strip()
                if new_range:
                    dns_config['fakeip_range'] = new_range
                    self.logger.info(f"✓ FakeIP范围设置为: {new_range}")
                    
                current_range_v6 = dns_config.get('fakeip_range_v6', 'fc00::/18')
                new_range_v6 = input(f"设置FakeIP IPv6范围 (当前: {current_range_v6}): ").strip()
                if new_range_v6:
                    dns_config['fakeip_range_v6'] = new_range_v6
                    self.logger.info(f"✓ FakeIP IPv6范围设置为: {new_range_v6}")
            else:
                self.logger.warn("请先启用FakeIP")
                
        elif choice == "3":
            tag = input("DNS服务器标签 (例: custom): ").strip()
            address = input("DNS服务器地址 (例: 8.8.8.8 或 https://8.8.8.8/dns-query): ").strip()
            if tag and address:
                if 'servers' not in dns_config:
                    dns_config['servers'] = []
                dns_config['servers'].append({"tag": tag, "address": address})
                self.logger.info(f"✓ 已添加DNS服务器: {tag} - {address}")
                
        elif choice == "4":
            servers = dns_config.get('servers', [])
            if servers:
                print()
                print("现有DNS服务器:")
                for i, server in enumerate(servers, 1):
                    print(f"  {i}. {server.get('tag', 'unknown')}: {server.get('address', 'unknown')}")
                
                try:
                    index = int(input("请选择要删除的服务器编号: ").strip()) - 1
                    if 0 <= index < len(servers):
                        removed = servers.pop(index)
                        self.logger.info(f"✓ 已删除DNS服务器: {removed.get('tag', 'unknown')}")
                    else:
                        self.logger.error("无效的编号")
                except ValueError:
                    self.logger.error("请输入有效的数字")
            else:
                self.logger.warn("没有DNS服务器可删除")
                
        elif choice == "5":
            config['dns'] = dns_config
            self.save_advanced_config(config)
            self.logger.info("✓ DNS配置已保存")
            return
        else:
            self.logger.error("无效选项")
    
    def configure_tun_mode(self):
        """配置TUN模式"""
        print()
        print(f"{Colors.CYAN}🔌 TUN 模式配置{Colors.NC}")
        print()
        
        config = self.load_advanced_config()
        tun_config = config.get("tun", {})
        
        print(f"{Colors.YELLOW}当前TUN配置:{Colors.NC}")
        print(f"  状态: {'启用' if tun_config.get('enabled', False) else '禁用'}")
        if tun_config.get('enabled', False):
            print(f"  接口名: {tun_config.get('interface_name', 'utun-sing')}")
            print(f"  IPv4地址: {tun_config.get('inet4_address', '172.19.0.1/30')}")
            print(f"  IPv6地址: {tun_config.get('inet6_address', 'fdfe:dcba:9876::1/126')}")
            print(f"  MTU: {tun_config.get('mtu', 9000)}")
            print(f"  自动路由: {'启用' if tun_config.get('auto_route', True) else '禁用'}")
            print(f"  严格路由: {'启用' if tun_config.get('strict_route', True) else '禁用'}")
        print()
        
        print("配置选项:")
        print("1. 启用/禁用 TUN 模式")
        print("2. 设置接口名称")
        print("3. 设置IP地址")
        print("4. 设置MTU")
        print("5. 路由设置")
        print("6. 保存并返回")
        print()
        
        choice = input("请选择 [1-6]: ").strip()
        
        if choice == "1":
            current = tun_config.get('enabled', False)
            toggle = input(f"TUN模式当前{'启用' if current else '禁用'}，是否切换? (y/N): ").strip().lower()
            if toggle in ['y', 'yes']:
                tun_config['enabled'] = not current
                status = '启用' if not current else '禁用'
                self.logger.info(f"✓ TUN模式已{status}")
                
                if not current:  # 如果要启用TUN
                    print()
                    print(f"{Colors.YELLOW}TUN模式说明:{Colors.NC}")
                    print("TUN模式可以接管系统的所有网络流量")
                    print("需要管理员权限，且可能需要额外配置")
                    print("建议先测试代理端口模式是否满足需求")
                    
        elif choice == "2":
            current_name = tun_config.get('interface_name', 'utun-sing')
            new_name = input(f"设置接口名称 (当前: {current_name}): ").strip()
            if new_name:
                tun_config['interface_name'] = new_name
                self.logger.info(f"✓ 接口名称设置为: {new_name}")
                
        elif choice == "3":
            current_ipv4 = tun_config.get('inet4_address', '172.19.0.1/30')
            new_ipv4 = input(f"设置IPv4地址 (当前: {current_ipv4}): ").strip()
            if new_ipv4:
                tun_config['inet4_address'] = new_ipv4
                self.logger.info(f"✓ IPv4地址设置为: {new_ipv4}")
                
            current_ipv6 = tun_config.get('inet6_address', 'fdfe:dcba:9876::1/126')
            new_ipv6 = input(f"设置IPv6地址 (当前: {current_ipv6}): ").strip()
            if new_ipv6:
                tun_config['inet6_address'] = new_ipv6
                self.logger.info(f"✓ IPv6地址设置为: {new_ipv6}")
                
        elif choice == "4":
            try:
                current_mtu = tun_config.get('mtu', 9000)
                new_mtu = int(input(f"设置MTU (当前: {current_mtu}): ").strip())
                tun_config['mtu'] = new_mtu
                self.logger.info(f"✓ MTU设置为: {new_mtu}")
            except ValueError:
                self.logger.error("MTU必须是数字")
                
        elif choice == "5":
            auto_route = tun_config.get('auto_route', True)
            toggle_auto = input(f"自动路由当前{'启用' if auto_route else '禁用'}，是否切换? (y/N): ").strip().lower()
            if toggle_auto in ['y', 'yes']:
                tun_config['auto_route'] = not auto_route
                self.logger.info(f"✓ 自动路由已{'禁用' if auto_route else '启用'}")
            
            strict_route = tun_config.get('strict_route', True)
            toggle_strict = input(f"严格路由当前{'启用' if strict_route else '禁用'}，是否切换? (y/N): ").strip().lower()
            if toggle_strict in ['y', 'yes']:
                tun_config['strict_route'] = not strict_route
                self.logger.info(f"✓ 严格路由已{'禁用' if strict_route else '启用'}")
                
        elif choice == "6":
            config['tun'] = tun_config
            self.save_advanced_config(config)
            self.logger.info("✓ TUN配置已保存")
            return
        else:
            self.logger.error("无效选项")
    
    def configure_clash_api(self):
        """配置Clash API"""
        print()
        print(f"{Colors.CYAN}📡 Clash API 配置{Colors.NC}")
        print()
        
        config = self.load_advanced_config()
        clash_config = config.get("clash_api", {})
        
        print(f"{Colors.YELLOW}当前Clash API配置:{Colors.NC}")
        print(f"  状态: {'启用' if clash_config.get('enabled', True) else '禁用'}")
        if clash_config.get('enabled', True):
            print(f"  控制器地址: {clash_config.get('external_controller', '127.0.0.1:9090')}")
            print(f"  WebUI: {clash_config.get('external_ui', 'ui')}")
            print(f"  密钥: {'已设置' if clash_config.get('secret', '') else '未设置'}")
            print(f"  默认模式: {clash_config.get('default_mode', 'rule')}")
        print()
        
        print("配置选项:")
        print("1. 启用/禁用 Clash API")
        print("2. 设置控制器地址")
        print("3. 设置访问密钥")
        print("4. 设置默认模式")
        print("5. 保存并返回")
        print()
        
        choice = input("请选择 [1-5]: ").strip()
        
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
            current_secret = clash_config.get('secret', '')
            print(f"当前密钥: {'已设置' if current_secret else '未设置'}")
            new_secret = input("设置新密钥 (留空不修改): ").strip()
            if new_secret:
                clash_config['secret'] = new_secret
                self.logger.info("✓ 访问密钥已更新")
                
        elif choice == "4":
            current_mode = clash_config.get('default_mode', 'rule')
            print(f"当前默认模式: {current_mode}")
            print("可用模式: rule, global, direct")
            new_mode = input("设置默认模式: ").strip()
            if new_mode in ['rule', 'global', 'direct']:
                clash_config['default_mode'] = new_mode
                self.logger.info(f"✓ 默认模式设置为: {new_mode}")
            else:
                self.logger.error("无效的模式")
                
        elif choice == "5":
            config['clash_api'] = clash_config
            self.save_advanced_config(config)
            self.logger.info("✓ Clash API配置已保存")
            return
        else:
            self.logger.error("无效选项")
    
    def configure_routing_rules(self):
        """配置分流规则管理"""
        print()
        print(f"{Colors.CYAN}🔀 分流规则管理{Colors.NC}")
        print("管理路由规则，决定不同流量的处理方式")
        print()
        
        config = self.load_advanced_config()
        routing_config = config.get("routing", {})
        
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
                config['routing'] = routing_config
                self.save_advanced_config(config)
                self.logger.info("✓ 分流规则配置已保存")
                break
            else:
                self.logger.error("无效选项")
            
            print()
    
    def configure_media_routing_rules(self):
        """配置媒体分流规则管理"""
        print()
        print(f"{Colors.CYAN}🎬 媒体分流管理{Colors.NC}")
        print("管理流媒体、音乐、社交媒体等媒体服务的分流规则")
        print()
        
        config = self.load_advanced_config()
        routing_config = config.get("routing", {})
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
                config['routing'] = routing_config
                self.save_advanced_config(config)
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
        
        config = self.load_advanced_config()
        routing_config = config.get("routing", {})
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
                config['routing'] = routing_config
                self.save_advanced_config(config)
                self.logger.info("✓ 程序分流规则配置已保存")
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
        print("4. 添加规则")
        print("5. 删除规则")
        print("6. 返回上级")
        
        choice = input("请选择 [1-6]: ").strip()
        
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
            self._add_rule_to_set(rule_set)
            
        elif choice == "5":
            self._remove_rule_from_set(rule_set)
            
        elif choice == "6":
            return
        else:
            self.logger.error("无效选项")
    
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
    
    def _add_rule_to_set(self, rule_set: Dict[str, Any]):
        """向规则组添加规则"""
        # 复用_add_custom_rule的逻辑，但直接添加到指定规则组
        print()
        print("添加新规则到当前规则组")
        # 这里可以复用_add_custom_rule的逻辑
        self.logger.info("功能开发中...")
    
    def _remove_rule_from_set(self, rule_set: Dict[str, Any]):
        """从规则组删除规则"""
        rules = rule_set.get('rules', [])
        if not rules:
            self.logger.warn("该规则组暂无规则")
            return
        
        print()
        print("选择要删除的规则:")
        for i, rule in enumerate(rules, 1):
            self._print_rule_details(i, rule)
        
        try:
            choice = int(input("请输入要删除的规则编号: ").strip()) - 1
            if 0 <= choice < len(rules):
                removed_rule = rules.pop(choice)
                self.logger.info("✓ 规则已删除")
            else:
                self.logger.error("无效的编号")
        except ValueError:
            self.logger.error("请输入有效的数字")
    
    def _delete_rule(self, routing_config: Dict[str, Any]):
        """删除规则组"""
        self.logger.info("删除规则组功能开发中...")
    
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
            self.logger.info("功能开发中...")
    
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
    
    def generate_inbounds_config(self) -> List[Dict[str, Any]]:
        """根据高级配置生成入站配置"""
        config = self.load_advanced_config()
        proxy_config = config.get("proxy_ports", {})
        tun_config = config.get("tun", {})
        enabled_ports = proxy_config.get("enabled", ["mixed"])
        
        inbounds = []
        
        # 添加代理端口配置
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
        
        # 添加TUN配置
        if tun_config.get("enabled", False):
            tun_inbound = {
                "type": "tun",
                "tag": "tun-in",
                "interface_name": tun_config.get("interface_name", "utun-sing"),
                "inet4_address": tun_config.get("inet4_address", "172.19.0.1/30"),
                "inet6_address": tun_config.get("inet6_address", "fdfe:dcba:9876::1/126"),
                "mtu": tun_config.get("mtu", 9000),
                "auto_route": tun_config.get("auto_route", True),
                "strict_route": tun_config.get("strict_route", True),
                "stack": tun_config.get("stack", "system"),
                "sniff": True,
                "sniff_override_destination": True
            }
            inbounds.append(tun_inbound)
        
        return inbounds
    
    def generate_dns_config(self) -> Dict[str, Any]:
        """根据高级配置生成DNS配置"""
        config = self.load_advanced_config()
        dns_config = config.get("dns", {})
        
        dns_result = {
            "servers": dns_config.get("servers", [
                {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                {"tag": "local", "address": "223.5.5.5"}
            ]),
            "rules": dns_config.get("rules", [
                {"domain_suffix": [".cn", ".中国"], "server": "local"},
                {"clash_mode": "direct", "server": "local"},
                {"clash_mode": "global", "server": "cloudflare"}
            ]),
            "final": dns_config.get("final", "cloudflare")
        }
        
        # 添加FakeIP配置
        if dns_config.get("fakeip_enabled", False):
            dns_result["fakeip"] = {
                "enabled": True,
                "inet4_range": dns_config.get("fakeip_range", "198.18.0.0/15"),
                "inet6_range": dns_config.get("fakeip_range_v6", "fc00::/18")
            }
        
        return dns_result
    
    def generate_experimental_config(self) -> Dict[str, Any]:
        """根据高级配置生成实验性功能配置"""
        config = self.load_advanced_config()
        clash_config = config.get("clash_api", {})
        experimental_config = config.get("experimental", {})
        
        result = {}
        
        # Clash API配置
        if clash_config.get("enabled", True):
            result["clash_api"] = {
                "external_controller": clash_config.get("external_controller", "127.0.0.1:9090"),
                "external_ui": clash_config.get("external_ui", "ui"),
                "secret": clash_config.get("secret", ""),
                "default_mode": clash_config.get("default_mode", "rule")
            }
        
        # 缓存配置
        if experimental_config.get("cache_enabled", True):
            result["cache_file"] = {
                "enabled": True,
                "path": str(self.paths.config_dir / experimental_config.get("cache_file", "cache.db")),
                "cache_id": "default",
                "store_fakeip": experimental_config.get("store_fakeip", False)
            }
        
        return result
    
    def generate_route_config(self) -> Dict[str, Any]:
        """生成路由配置"""
        config = self.load_advanced_config()
        routing_config = config.get("routing", {})
        
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