#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
节点管理模块 - 负责管理所有代理节点
Node Management Module - Managing all proxy nodes
"""

import socket
import secrets
import string
import subprocess
import uuid
import json
import time
import requests
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils import Colors, Logger
from paths import PathManager
from rich_menu import RichMenu

class NodeManager:
    """节点管理类 - 负责节点的增删改查和连接测试"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
    
    def init_nodes_config(self):
        """初始化节点配置"""
        self.logger.step("初始化节点配置...")
        
        if not self.paths.nodes_config.exists():
            config = {
                "version": "1.0",
                "current_node": None,
                "nodes": {}
            }
            
            with open(self.paths.nodes_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("✓ 创建空节点配置文件")
            self.logger.info("✓ 请通过菜单添加您需要的节点")
        
        self.logger.info("✓ 节点管理初始化完成")
    
    def load_nodes_config(self) -> Dict:
        """加载节点配置"""
        try:
            with open(self.paths.nodes_config, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"version": "1.0", "current_node": None, "nodes": {}}
    
    def save_nodes_config(self, config: Dict):
        """保存节点配置"""
        # 备份原配置
        import shutil
        if self.paths.nodes_config.exists():
            backup_file = self.paths.backup_dir / f"nodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.paths.backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.paths.nodes_config, backup_file)
        
        with open(self.paths.nodes_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def show_nodes(self):
        """显示节点列表"""
        rich_menu = RichMenu()
        self.logger.step("显示节点列表...")
        
        config = self.load_nodes_config()
        current_node = config.get('current_node')
        nodes = config.get('nodes', {})
        
        if not nodes:
            rich_menu.print_warning("暂无节点，请添加节点")
            return
        
        # 缓存文件路径
        cache_file = self.paths.config_dir / "node_cache.json"
        cache_data = self._load_cache(cache_file)
        
        print()
        rich_menu.print_info(f"检测到 {len(nodes)} 个节点")
        
        # 先校验配置
        config_status = self._validate_sing_box_config()
        if config_status['valid']:
            rich_menu.print_success("✓ 当前配置文件校验通过")
        else:
            rich_menu.print_error("✗ 当前配置文件校验失败")
            if config_status['error']:
                rich_menu.print_warning(f"错误信息: {config_status['error']}")
        
        # 准备初始表格数据
        headers = ["状态", "节点ID", "节点名称", "协议", "国别", "延迟", "配置状态"]
        rows = []
        
        # 先显示基本信息
        for node_id, node_info in nodes.items():
            name = node_info.get('name', node_id)
            node_type = node_info.get('type', 'unknown')
            enabled = node_info.get('enabled', False)
            
            # 状态标识
            status_style = "[green]●[/green]" if node_id == current_node else "[white]○[/white]"
            
            # 从缓存获取或设置默认值
            cache_key = self._get_cache_key(node_info)
            cached_info = cache_data.get(cache_key, {})
            cache_expired = self._is_cache_expired(cached_info.get('timestamp'))
            
            if not cache_expired and cached_info:
                # 使用缓存数据
                country = cached_info.get('country', '未知')
                latency = cached_info.get('latency', 'N/A')
                country_emoji = self._get_country_flag(country)
                
                if isinstance(latency, (int, float)):
                    if latency < 100:
                        latency_str = f"[green]{latency}ms[/green]"
                    elif latency < 300:
                        latency_str = f"[yellow]{latency}ms[/yellow]"
                    else:
                        latency_str = f"[red]{latency}ms[/red]"
                else:
                    latency_str = f"[red]{latency}[/red]"
            else:
                # 显示检测中状态
                country_emoji = "🔍"
                latency_str = "[yellow]检测中...[/yellow]"
            
            # 检查单个节点配置状态
            node_config_status = self._validate_node_config(node_info)
            if node_config_status['valid']:
                config_status_str = "[green]✓ 有效[/green]"
            else:
                config_status_str = "[red]✗ 错误[/red]"
            
            rows.append([
                status_style,
                node_id,
                name,
                node_type,
                country_emoji,
                latency_str,
                config_status_str
            ])
        
        # 先显示表格
        print()
        rich_menu.show_table("📡 节点列表", headers, rows, styles={
            "节点ID": "cyan",
            "节点名称": "blue",
            "协议": "magenta"
        })
        
        print()
        rich_menu.print_info("● = 当前节点  ○ = 其他节点")
        if current_node:
            rich_menu.print_success(f"当前活动节点: {current_node}")
        else:
            rich_menu.print_warning("当前活动节点: 无节点")
        
        # 显示配置错误的详细信息
        error_nodes = []
        for node_id, node_info in nodes.items():
            node_config_status = self._validate_node_config(node_info)
            if not node_config_status['valid']:
                error_nodes.append((node_id, node_info.get('name', node_id), node_config_status['error']))
        
        if error_nodes:
            print()
            rich_menu.print_warning("⚠️ 发现配置错误的节点:")
            for node_id, name, error in error_nodes:
                rich_menu.print_error(f"  {name} ({node_id}): {error}")
        
        # 异步检测需要更新的节点
        nodes_to_update = []
        for node_id, node_info in nodes.items():
            cache_key = self._get_cache_key(node_info)
            cached_info = cache_data.get(cache_key, {})
            cache_expired = self._is_cache_expired(cached_info.get('timestamp'))
            
            if cache_expired or not cached_info:
                nodes_to_update.append((node_id, node_info))
        
        if nodes_to_update:
            print()
            rich_menu.print_info(f"正在后台检测 {len(nodes_to_update)} 个节点的速度和地理位置...")
            
            # 启动异步检测
            self._async_update_nodes(nodes_to_update, cache_file, cache_data)
    
    def _async_update_nodes(self, nodes_to_update, cache_file, cache_data):
        """异步更新节点信息"""
        import concurrent.futures
        import sys
        
        def update_single_node(node_item):
            node_id, node_info = node_item
            country, latency = self._test_node_speed_and_country(node_info)
            return node_id, country, latency
        
        # 使用线程池异步检测
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            future_to_node = {
                executor.submit(update_single_node, node_item): node_item[0] 
                for node_item in nodes_to_update
            }
            
            updated_count = 0
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_node):
                try:
                    node_id, country, latency = future.result()
                    
                    # 更新缓存
                    cache_key = self._get_cache_key(next(info for nid, info in nodes_to_update if nid == node_id))
                    cache_data[cache_key] = {
                        'country': country,
                        'latency': latency,
                        'timestamp': time.time()
                    }
                    
                    updated_count += 1
                    
                    # 显示更新进度
                    country_emoji = self._get_country_flag(country)
                    
                    if isinstance(latency, (int, float)):
                        if latency < 100:
                            latency_display = f"{latency}ms (优秀)"
                        elif latency < 300:
                            latency_display = f"{latency}ms (良好)"
                        else:
                            latency_display = f"{latency}ms (较慢)"
                    else:
                        latency_display = str(latency)
                    
                    print(f"  ✓ {node_id}: {country_emoji} {latency_display}")
                    
                except Exception as e:
                    print(f"  ✗ {future_to_node[future]}: 检测失败")
        
        # 保存更新的缓存
        self._save_cache(cache_file, cache_data)
        
        if updated_count > 0:
            print()
            from rich_menu import RichMenu
            rich_menu = RichMenu()
            rich_menu.print_success(f"已完成 {updated_count} 个节点的检测，缓存已更新")
            rich_menu.print_info("再次运行 'python3 sing.py nodes' 查看完整结果")
    
    def _get_country_flag(self, country: str) -> str:
        """获取国家对应的旗帜emoji"""
        flag_map = {
            # 中文国家名
            '中国': '🇨🇳', '香港': '🇭🇰', '台湾': '🇹🇼', '澳门': '🇲🇴',
            '日本': '🇯🇵', '韩国': '🇰🇷', '新加坡': '🇸🇬', '马来西亚': '🇲🇾',
            '美国': '🇺🇸', '加拿大': '🇨🇦', '英国': '🇬🇧', '德国': '🇩🇪',
            '法国': '🇫🇷', '意大利': '🇮🇹', '荷兰': '🇳🇱', '俄罗斯': '🇷🇺',
            '澳大利亚': '🇦🇺', '印度': '🇮🇳', '巴西': '🇧🇷', '泰国': '🇹🇭',
            '越南': '🇻🇳', '菲律宾': '🇵🇭', '印度尼西亚': '🇮🇩', '土耳其': '🇹🇷',
            '瑞士': '🇨🇭', '瑞典': '🇸🇪', '挪威': '🇳🇴', '芬兰': '🇫🇮',
            '丹麦': '🇩🇰', '西班牙': '🇪🇸', '葡萄牙': '🇵🇹', '波兰': '🇵🇱',
            '捷克': '🇨🇿', '匈牙利': '🇭🇺', '奥地利': '🇦🇹', '比利时': '🇧🇪',
            '爱尔兰': '🇮🇪', '以色列': '🇮🇱', '阿联酋': '🇦🇪', '南非': '🇿🇦',
            '阿根廷': '🇦🇷', '智利': '🇨🇱', '墨西哥': '🇲🇽', '埃及': '🇪🇬',
            
            # 英文国家名
            'China': '🇨🇳', 'Hong Kong': '🇭🇰', 'Taiwan': '🇹🇼', 'Macao': '🇲🇴',
            'Japan': '🇯🇵', 'South Korea': '🇰🇷', 'Singapore': '🇸🇬', 'Malaysia': '🇲🇾',
            'United States': '🇺🇸', 'Canada': '🇨🇦', 'United Kingdom': '🇬🇧', 'Germany': '🇩🇪',
            'France': '🇫🇷', 'Italy': '🇮🇹', 'Netherlands': '🇳🇱', 'Russia': '🇷🇺',
            'Australia': '🇦🇺', 'India': '🇮🇳', 'Brazil': '🇧🇷', 'Thailand': '🇹🇭',
            'Vietnam': '🇻🇳', 'Philippines': '🇵🇭', 'Indonesia': '🇮🇩', 'Turkey': '🇹🇷',
            'Switzerland': '🇨🇭', 'Sweden': '🇸🇪', 'Norway': '🇳🇴', 'Finland': '🇫🇮',
            'Denmark': '🇩🇰', 'Spain': '🇪🇸', 'Portugal': '🇵🇹', 'Poland': '🇵🇱',
            'Czech Republic': '🇨🇿', 'Hungary': '🇭🇺', 'Austria': '🇦🇹', 'Belgium': '🇧🇪',
            'Ireland': '🇮🇪', 'Israel': '🇮🇱', 'United Arab Emirates': '🇦🇪', 'South Africa': '🇿🇦',
            'Argentina': '🇦🇷', 'Chile': '🇨🇱', 'Mexico': '🇲🇽', 'Egypt': '🇪🇬',
            
            # 特殊情况
            '本地': '🏠', '未知': '🌍', 'localhost': '🏠', 'unknown': '🌍'
        }
        return flag_map.get(country, '🌍')
    
    def _load_cache(self, cache_file: Path) -> dict:
        """加载缓存数据"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warn(f"加载缓存失败: {e}")
        return {}
    
    def _save_cache(self, cache_file: Path, cache_data: dict):
        """保存缓存数据"""
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warn(f"保存缓存失败: {e}")
    
    def _get_cache_key(self, node_info: dict) -> str:
        """生成缓存键"""
        config = node_info.get('config', {})
        server = config.get('server', config.get('address', 'localhost'))
        port = config.get('port', config.get('listen_port', 0))
        return f"{server}:{port}"
    
    def _is_cache_expired(self, timestamp: float, expiry_hours: int = 6) -> bool:
        """检查缓存是否过期"""
        if not timestamp:
            return True
        return time.time() - timestamp > expiry_hours * 3600
    
    def _test_node_speed_and_country(self, node_info: dict) -> tuple:
        """测试节点速度和国别"""
        config = node_info.get('config', {})
        server = config.get('server', config.get('address'))
        port = config.get('port', config.get('listen_port'))
        
        if not server or not port:
            return '本地', 'N/A'
        
        # 测试延迟
        try:
            is_connected, response_time = self._test_tcp_connection(server, port, timeout=3)
            if is_connected and response_time is not None:
                latency = int(response_time * 1000)  # 转换为毫秒
                # 限制最大显示延迟
                if latency > 5000:
                    latency = 'timeout'
            else:
                latency = 'timeout'
        except Exception:
            latency = 'error'
        
        # 获取国别信息
        country = self._get_server_country(server)
        
        return country, latency
    
    def _get_server_country(self, server: str) -> str:
        """获取服务器国别"""
        if server in ['localhost', '127.0.0.1', '0.0.0.0']:
            return '本地'
        
        try:
            # 使用ip-api.com获取地理位置信息
            response = requests.get(f"http://ip-api.com/json/{server}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    country = data.get('country', '未知')
                    return country
        except Exception:
            pass
        
        # 备用方案：根据域名猜测
        domain_country_map = {
            '.jp': '日本', '.kr': '韩国', '.hk': '香港', '.tw': '台湾',
            '.sg': '新加坡', '.us': '美国', '.uk': '英国', '.de': '德国',
            '.fr': '法国', '.ca': '加拿大', '.au': '澳大利亚'
        }
        
        for suffix, country in domain_country_map.items():
            if suffix in server.lower():
                return country
        
        return '未知'
    
    def add_local_server_node(self, node_id: str, node_name: str) -> bool:
        """添加本地服务器节点"""
        print()
        print(f"{Colors.BLUE}配置本地服务器节点:{Colors.NC}")
        print(f"{Colors.YELLOW}此节点将在本机启动服务器，供其他设备连接{Colors.NC}")
        print()
        
        # 获取配置参数
        port = input("监听端口 (默认 5566): ").strip() or "5566"
        try:
            port = int(port)
        except ValueError:
            self.logger.error("端口必须是数字")
            return False
        
        # 生成随机密码
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        print(f"{Colors.CYAN}自动生成密码: {Colors.GREEN}{password}{Colors.NC}")
        
        use_custom = input("是否使用自定义密码? (y/N): ").strip().lower()
        if use_custom in ['y', 'yes']:
            custom_password = input("请输入自定义密码: ").strip()
            if custom_password:
                password = custom_password
        
        protocol = input("协议类型 (trojan/vless, 默认 trojan): ").strip().lower() or "trojan"
        transport = input("传输类型 (tcp/ws, 默认 ws): ").strip().lower() or "ws"
        
        ws_path = "/trojan-ws"
        ws_host = "www.bing.com"
        if transport == "ws":
            ws_path = input("WebSocket 路径 (默认 /trojan-ws): ").strip() or "/trojan-ws"
            ws_host = input("WebSocket Host (默认 www.bing.com): ").strip() or "www.bing.com"
        
        # 检查端口是否被占用
        if self._is_port_in_use(port):
            self.logger.warn(f"端口 {port} 已被占用，请选择其他端口")
            return False
        
        # 创建节点配置
        node_config = {
            "name": node_name,
            "type": "local_server",
            "protocol": protocol,
            "enabled": True,
            "config": {
                "listen_port": port,
                "created_at": datetime.now().isoformat()
            }
        }
        
        if protocol == "trojan":
            node_config["config"]["password"] = password
        else:  # vless
            node_config["config"]["uuid"] = str(uuid.uuid4())
        
        if transport == "ws":
            node_config["config"]["transport"] = {
                "type": "ws",
                "path": ws_path,
                "headers": {"Host": ws_host}
            }
        
        node_config["config"]["tls"] = {
            "enabled": True,
            "server_name": ws_host if transport == "ws" else "localhost",
            "insecure": True
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        print()
        self.logger.info(f"✓ 本地服务器节点添加成功: {node_name}")
        print(f"{Colors.CYAN}连接信息:{Colors.NC}")
        print(f"  端口: {Colors.GREEN}{port}{Colors.NC}")
        if protocol == "trojan":
            print(f"  密码: {Colors.GREEN}{password}{Colors.NC}")
        else:
            print(f"  UUID: {Colors.GREEN}{node_config['config']['uuid']}{Colors.NC}")
        print(f"  协议: {Colors.GREEN}{protocol}{Colors.NC}")
        print(f"  传输: {Colors.GREEN}{transport}{Colors.NC}")
        if transport == "ws":
            print(f"  路径: {Colors.GREEN}{ws_path}{Colors.NC}")
            print(f"  Host: {Colors.GREEN}{ws_host}{Colors.NC}")
        
        return True
    
    def add_local_client_node(self, node_id: str, node_name: str) -> bool:
        """添加本地客户端节点"""
        print()
        print(f"{Colors.BLUE}配置本地客户端节点:{Colors.NC}")
        print(f"{Colors.YELLOW}此节点将连接到本机其他端口的服务{Colors.NC}")
        print()
        
        server = input("目标服务器地址 (默认 127.0.0.1): ").strip() or "127.0.0.1"
        port_str = input("目标端口: ").strip()
        
        try:
            port = int(port_str)
        except ValueError:
            self.logger.error("端口必须是数字")
            return False
        
        protocol = input("协议类型 (trojan/vless/shadowsocks): ").strip().lower()
        
        node_config = {
            "name": node_name,
            "type": "local_client",
            "protocol": protocol,
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "created_at": datetime.now().isoformat()
            }
        }
        
        if protocol == "trojan":
            password = input("密码: ").strip()
            if not password:
                self.logger.error("密码不能为空")
                return False
            node_config["config"]["password"] = password
            
            transport = input("传输类型 (tcp/ws, 默认 tcp): ").strip().lower() or "tcp"
            if transport == "ws":
                ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
                ws_host = input("WebSocket Host: ").strip() or server
                node_config["config"]["transport"] = {
                    "type": "ws",
                    "path": ws_path,
                    "headers": {"Host": ws_host}
                }
            
            node_config["config"]["tls"] = {
                "enabled": True,
                "server_name": server,
                "insecure": True
            }
        
        elif protocol == "vless":
            uuid_str = input("UUID: ").strip()
            if not uuid_str:
                self.logger.error("UUID不能为空")
                return False
            node_config["config"]["uuid"] = uuid_str
            
            transport = input("传输类型 (tcp/ws, 默认 tcp): ").strip().lower() or "tcp"
            if transport == "ws":
                ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
                ws_host = input("WebSocket Host: ").strip() or server
                node_config["config"]["transport"] = {
                    "type": "ws",
                    "path": ws_path,
                    "headers": {"Host": ws_host}
                }
            
            node_config["config"]["tls"] = {
                "enabled": True,
                "server_name": server,
                "insecure": True
            }
        
        elif protocol == "shadowsocks":
            password = input("密码: ").strip()
            if not password:
                self.logger.error("密码不能为空")
                return False
            method = input("加密方式 (默认 aes-256-gcm): ").strip() or "aes-256-gcm"
            node_config["config"]["password"] = password
            node_config["config"]["method"] = method
        
        else:
            self.logger.error(f"不支持的协议类型: {protocol}")
            return False
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ 本地客户端节点添加成功: {node_name}")
        return True
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def switch_node(self, target_node_id: str = None) -> bool:
        """切换节点"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        
        if not nodes:
            self.logger.error("暂无可用节点，请先添加节点")
            return False
        
        if not target_node_id:
            # 显示可用节点并让用户选择
            self.show_nodes()
            print()
            
            while True:
                target_node_id = input("请输入要切换到的节点ID: ").strip()
                
                if target_node_id.lower() in ['q', 'quit', 'exit']:
                    self.logger.info("取消切换")
                    return False
                
                if not target_node_id:
                    print(f"{Colors.YELLOW}提示: 节点ID不能为空{Colors.NC}")
                    continue
                
                if target_node_id in nodes:
                    break
                else:
                    self.logger.error(f"节点 '{target_node_id}' 不存在")
                    print(f"{Colors.CYAN}可用的节点ID:{Colors.NC}")
                    for node_id in nodes.keys():
                        print(f"  - {node_id}")
        
        if target_node_id not in nodes:
            self.logger.error(f"节点 '{target_node_id}' 不存在")
            return False
        
        # 显示将要切换的节点信息
        node_info = nodes[target_node_id]
        self.logger.info(f"准备切换到节点: {target_node_id}")
        print(f"节点名称: {node_info.get('name', target_node_id)}")
        print(f"节点类型: {node_info.get('type', 'unknown')}")
        print()
        
        # 确认切换
        confirm = input(f"{Colors.YELLOW}确认切换到此节点? (Y/n):{Colors.NC} ")
        if confirm and not confirm.lower().startswith('y'):
            self.logger.info("取消切换")
            return False
        
        # 更新当前节点
        config['current_node'] = target_node_id
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ 已切换到节点: {target_node_id}")
        return True
    
    def delete_node(self, node_name: str = None) -> bool:
        """删除节点 - 支持按名称删除"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        current_node = config.get('current_node')
        
        if not nodes:
            self.logger.error("暂无节点可删除")
            return False
        
        target_node_id = None
        target_node_name = None
        
        if not node_name:
            # 显示可删除的节点列表
            print()
            print(f"{Colors.CYAN}📋 可删除的节点列表:{Colors.NC}")
            print("----------------------------------------")
            
            node_list = []
            for node_id, node_info in nodes.items():
                name = node_info.get('name', node_id)
                node_type = node_info.get('type', 'unknown')
                is_current = '●' if node_id == current_node else '○'
                current_text = ' (当前活动)' if node_id == current_node else ''
                
                print(f"  {is_current} {name} - {node_type}{current_text}")
                node_list.append((node_id, name))
            
            print("----------------------------------------")
            print(f"{Colors.YELLOW}● = 当前活动节点  ○ = 其他节点{Colors.NC}")
            print()
            
            # 让用户输入要删除的节点名称
            while True:
                user_input = input("请输入要删除的节点名称 (或输入 'q' 退出): ").strip()
                
                if user_input.lower() in ['q', 'quit', 'exit']:
                    self.logger.info("取消删除")
                    return False
                
                if not user_input:
                    print(f"{Colors.YELLOW}提示: 节点名称不能为空{Colors.NC}")
                    continue
                
                # 查找匹配的节点
                matches = []
                for node_id, name in node_list:
                    if user_input == name or user_input == node_id:
                        matches.append((node_id, name))
                    elif user_input.lower() in name.lower():
                        matches.append((node_id, name))
                
                if len(matches) == 0:
                    print(f"{Colors.YELLOW}未找到匹配的节点: '{user_input}'{Colors.NC}")
                    print("可用的节点名称:")
                    for _, name in node_list:
                        print(f"  - {name}")
                    continue
                elif len(matches) == 1:
                    target_node_id, target_node_name = matches[0]
                    break
                else:
                    print(f"{Colors.YELLOW}找到多个匹配的节点:{Colors.NC}")
                    for i, (node_id, name) in enumerate(matches, 1):
                        print(f"  {i}. {name} ({node_id})")
                    
                    try:
                        choice = int(input("请选择要删除的节点编号: ").strip())
                        if 1 <= choice <= len(matches):
                            target_node_id, target_node_name = matches[choice - 1]
                            break
                        else:
                            print(f"{Colors.YELLOW}无效的选择{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.YELLOW}请输入有效的数字{Colors.NC}")
        else:
            # 通过传入的名称查找节点
            for node_id, node_info in nodes.items():
                if node_name == node_info.get('name', node_id) or node_name == node_id:
                    target_node_id = node_id
                    target_node_name = node_info.get('name', node_id)
                    break
            
            if not target_node_id:
                self.logger.error(f"节点 '{node_name}' 不存在")
                return False
        
        # 检查是否要删除当前活动节点
        is_current_node = (target_node_id == current_node)
        if is_current_node:
            print()
            print(f"{Colors.YELLOW}⚠️  警告: 您正在删除当前活动的节点!{Colors.NC}")
            print("删除后需要选择其他节点作为活动节点")
        
        # 显示要删除的节点信息
        node_info = nodes[target_node_id]
        node_type = node_info.get('type', 'unknown')
        print()
        print(f"{Colors.CYAN}📋 节点信息:{Colors.NC}")
        print(f"  节点名称: {Colors.GREEN}{target_node_name}{Colors.NC}")
        print(f"  节点ID: {Colors.GREEN}{target_node_id}{Colors.NC}")
        print(f"  节点类型: {Colors.GREEN}{node_type}{Colors.NC}")
        if 'config' in node_info:
            config_data = node_info['config']
            if 'server' in config_data and 'port' in config_data:
                print(f"  服务器: {Colors.GREEN}{config_data['server']}:{config_data['port']}{Colors.NC}")
        
        # 确认删除
        print()
        print(f"{Colors.RED}⚠️  确定要删除节点 '{target_node_name}' 吗?{Colors.NC}")
        confirm = input(f"{Colors.YELLOW}请输入 'yes' 确认删除:{Colors.NC} ")
        
        if confirm != 'yes':
            self.logger.info("取消删除")
            return False
        
        # 删除节点
        del config['nodes'][target_node_id]
        
        # 如果删除的是当前节点，需要处理当前节点选择
        if is_current_node:
            remaining_nodes = config.get('nodes', {})
            if remaining_nodes:
                # 有其他节点，让用户选择新的活动节点
                print()
                print(f"{Colors.CYAN}选择新的活动节点:{Colors.NC}")
                node_list = list(remaining_nodes.items())
                for i, (node_id, node_info) in enumerate(node_list, 1):
                    name = node_info.get('name', node_id)
                    node_type = node_info.get('type', 'unknown')
                    print(f"  {i}. {name} - {node_type}")
                
                while True:
                    try:
                        choice = input("请选择新的活动节点编号 (或输入 'none' 不设置): ").strip()
                        if choice.lower() == 'none':
                            config['current_node'] = None
                            break
                        
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(node_list):
                            new_node_id = node_list[choice_num - 1][0]
                            config['current_node'] = new_node_id
                            new_node_name = node_list[choice_num - 1][1].get('name', new_node_id)
                            self.logger.info(f"✓ 已切换到节点: {new_node_name}")
                            break
                        else:
                            print(f"{Colors.YELLOW}请输入 1-{len(node_list)} 之间的数字{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.YELLOW}请输入有效的数字或 'none'{Colors.NC}")
            else:
                # 没有其他节点了
                config['current_node'] = None
                self.logger.warn("所有节点已删除，当前无活动节点")
        
        # 保存配置
        self.save_nodes_config(config)
        self.logger.info(f"✓ 节点 '{target_node_name}' 删除成功")
        return True
    
    def add_trojan_node(self, node_id: str, node_name: str) -> bool:
        """添加 Trojan 节点"""
        print()
        print(f"{Colors.BLUE}🔐 配置 Trojan 节点:{Colors.NC}")
        print(f"{Colors.YELLOW}Trojan 是一个高性能的代理协议，使用 TLS 加密{Colors.NC}")
        print()
        
        # 服务器地址
        while True:
            server = input("服务器地址 (例: example.com): ").strip()
            if not server:
                print(f"{Colors.YELLOW}提示: 服务器地址不能为空{Colors.NC}")
                continue
            # 简单验证域名/IP格式
            if '.' not in server:
                confirm = input(f"{Colors.YELLOW}'{server}' 看起来不像一个有效的域名或IP，是否继续? (y/N): {Colors.NC}").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        
        # 端口
        while True:
            port_str = input("端口 (默认 443): ").strip() or "443"
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    print(f"{Colors.YELLOW}提示: 端口范围应在 1-65535 之间{Colors.NC}")
                    continue
                break
            except ValueError:
                print(f"{Colors.YELLOW}提示: 端口必须是数字{Colors.NC}")
        
        # 密码
        while True:
            password = input("密码: ").strip()
            if not password:
                print(f"{Colors.YELLOW}提示: 密码不能为空{Colors.NC}")
                continue
            if len(password) < 6:
                confirm = input(f"{Colors.YELLOW}密码较短，建议使用更长的密码，是否继续? (y/N): {Colors.NC}").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        
        # SNI/服务器名称设置
        print()
        print(f"{Colors.CYAN}🌐 TLS 服务器名称 (SNI):{Colors.NC}")
        print("SNI (Server Name Indication) 用于指定TLS握手时的服务器名称")
        sni = input(f"SNI/服务器名称 (默认 {server}): ").strip() or server
        
        # 证书验证
        print()
        print(f"{Colors.CYAN}🔒 证书验证配置:{Colors.NC}")
        print(f"{Colors.GREEN}选项说明:{Colors.NC}")
        print("  1. 严格验证 (推荐) - 验证服务器证书，确保连接安全")
        print("     ✓ 更安全，防止中间人攻击")
        print("     ✗ 需要服务器有有效的SSL证书")
        print()
        print("  2. 跳过验证 - 不验证证书，允许自签名证书")
        print("     ✓ 兼容性好，适用于自建服务器")
        print("     ✗ 安全性较低，可能受到中间人攻击")
        print()
        
        while True:
            verify_choice = input("请选择证书验证方式 [1=严格验证/2=跳过验证] (默认 1): ").strip() or "1"
            if verify_choice in ["1", "2"]:
                insecure = (verify_choice == "2")
                break
            else:
                print(f"{Colors.YELLOW}请输入 1 或 2{Colors.NC}")
        
        if insecure:
            print(f"{Colors.YELLOW}⚠️  已选择跳过证书验证，请确保服务器可信{Colors.NC}")
        else:
            print(f"{Colors.GREEN}✓ 已选择严格验证，将验证服务器证书{Colors.NC}")
        
        # 传输协议
        print()
        print(f"{Colors.CYAN}传输协议选项:{Colors.NC}")
        print("  1) TCP - 直接TCP连接 (默认)")
        print("  2) WebSocket - 通过WebSocket传输，可伪装成网页流量")
        transport_choice = input("请选择传输协议 [1-2]: ").strip() or "1"
        
        transport = "tcp"
        ws_config = None
        
        if transport_choice == "2":
            transport = "ws"
            print()
            print(f"{Colors.CYAN}WebSocket 配置:{Colors.NC}")
            ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
            ws_host = input(f"WebSocket Host (默认 {sni}): ").strip() or sni
            ws_config = {
                "type": "ws",
                "path": ws_path,
                "headers": {"Host": ws_host}
            }
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "trojan",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "password": password,
                "tls": {
                    "enabled": True,
                    "server_name": sni,
                    "insecure": insecure
                },
                "created_at": datetime.now().isoformat()
            }
        }
        
        if ws_config:
            node_config["config"]["transport"] = ws_config
        
        # 显示配置摘要
        print()
        print(f"{Colors.GREEN}📋 配置摘要:{Colors.NC}")
        print(f"  节点名称: {Colors.CYAN}{node_name}{Colors.NC}")
        print(f"  服务器: {Colors.CYAN}{server}:{port}{Colors.NC}")
        print(f"  SNI: {Colors.CYAN}{sni}{Colors.NC}")
        print(f"  证书验证: {Colors.CYAN}{'跳过' if insecure else '严格'}{Colors.NC}")
        print(f"  传输: {Colors.CYAN}{transport.upper()}{Colors.NC}")
        if ws_config:
            print(f"  WS路径: {Colors.CYAN}{ws_config['path']}{Colors.NC}")
            print(f"  WS Host: {Colors.CYAN}{ws_config['headers']['Host']}{Colors.NC}")
        
        # 确认保存
        print()
        confirm = input(f"{Colors.YELLOW}确认添加此节点? (Y/n): {Colors.NC}").strip().lower()
        if confirm and not confirm.startswith('y'):
            self.logger.info("取消添加节点")
            return False
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        print()
        self.logger.info(f"✓ Trojan 节点添加成功: {node_name}")
        
        # 提示连接测试
        test_now = input(f"{Colors.YELLOW}是否现在测试节点连通性? (Y/n): {Colors.NC}").strip().lower()
        if not test_now or test_now.startswith('y'):
            print()
            self.test_node_connectivity(node_id)
        
        return True
    
    def add_vless_node(self, node_id: str, node_name: str) -> bool:
        """添加 VLESS 节点"""
        print()
        print(f"{Colors.BLUE}配置 VLESS 节点:{Colors.NC}")
        
        server = input("服务器地址: ").strip()
        if not server:
            self.logger.error("服务器地址不能为空")
            return False
        
        port_str = input("端口 (默认 443): ").strip() or "443"
        try:
            port = int(port_str)
        except ValueError:
            self.logger.error("端口必须是数字")
            return False
        
        uuid_str = input("UUID: ").strip()
        if not uuid_str:
            self.logger.error("UUID不能为空")
            return False
        
        sni = input(f"SNI (默认 {server}): ").strip() or server
        transport = input("传输类型 (tcp/ws/grpc, 默认 tcp): ").strip().lower() or "tcp"
        
        # 询问是否跳过证书验证
        skip_verify = input("是否跳过证书验证? (y/N): ").strip().lower()
        insecure = skip_verify in ['y', 'yes']
        
        node_config = {
            "name": node_name,
            "type": "vless",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "uuid": uuid_str,
                "tls": {
                    "enabled": True,
                    "server_name": sni,
                    "insecure": insecure
                },
                "created_at": datetime.now().isoformat()
            }
        }
        
        if transport == "tcp":
            flow = input("Flow (留空为默认): ").strip()
            if flow:
                node_config["config"]["flow"] = flow
        elif transport == "ws":
            ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
            ws_host = input(f"WebSocket Host (默认 {sni}): ").strip() or sni
            node_config["config"]["transport"] = {
                "type": "ws",
                "path": ws_path,
                "headers": {"Host": ws_host}
            }
        elif transport == "grpc":
            grpc_service = input("gRPC Service Name: ").strip()
            node_config["config"]["transport"] = {
                "type": "grpc",
                "service_name": grpc_service
            }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ VLESS 节点添加成功: {node_name}")
        return True
    
    def add_shadowsocks_node(self, node_id: str, node_name: str) -> bool:
        """添加 Shadowsocks 节点"""
        print()
        print(f"{Colors.BLUE}配置 Shadowsocks 节点:{Colors.NC}")
        
        server = input("服务器地址: ").strip()
        if not server:
            self.logger.error("服务器地址不能为空")
            return False
        
        port_str = input("端口: ").strip()
        try:
            port = int(port_str)
        except ValueError:
            self.logger.error("端口必须是数字")
            return False
        
        password = input("密码: ").strip()
        if not password:
            self.logger.error("密码不能为空")
            return False
        
        print()
        print(f"{Colors.CYAN}支持的加密方式:{Colors.NC}")
        print("  1) aes-256-gcm (推荐)")
        print("  2) aes-128-gcm")
        print("  3) chacha20-ietf-poly1305")
        print("  4) xchacha20-ietf-poly1305")
        print()
        
        method_choice = input("请选择加密方式 [1-4]: ").strip()
        method_map = {
            "1": "aes-256-gcm",
            "2": "aes-128-gcm", 
            "3": "chacha20-ietf-poly1305",
            "4": "xchacha20-ietf-poly1305"
        }
        method = method_map.get(method_choice, "aes-256-gcm")
        
        node_config = {
            "name": node_name,
            "type": "shadowsocks",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "password": password,
                "method": method,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ Shadowsocks 节点添加成功: {node_name}")
        return True
    
    def test_node_connectivity(self, node_id: str = None) -> bool:
        """测试节点连通性"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        
        if not nodes:
            self.logger.error("暂无节点可测试")
            return False
        
        if node_id:
            nodes_to_test = {node_id: nodes.get(node_id)} if node_id in nodes else {}
        else:
            nodes_to_test = nodes
        
        if not nodes_to_test:
            self.logger.error(f"节点 '{node_id}' 不存在")
            return False
        
        self.logger.step("测试节点连通性...")
        print()
        
        results = []
        for test_node_id, node_info in nodes_to_test.items():
            name = node_info.get('name', test_node_id)
            node_type = node_info.get('type', 'unknown')
            config_data = node_info.get('config', {})
            
            print(f"测试节点: {name} ({test_node_id})")
            
            if node_type in ['local_server', 'local_client']:
                print("  本地节点 - 跳过网络测试")
            elif node_type in ['trojan', 'vless', 'shadowsocks', 'vmess', 'hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
                # 远程节点
                server = config_data.get('server', '')
                port = config_data.get('port', 443)
                
                if not server:
                    status = f"{Colors.RED}错误{Colors.NC}"
                    latency = f"{Colors.RED}N/A{Colors.NC}"
                    note = "配置错误"
                else:
                    success, latency_ms = self._test_tcp_connection(server, port, timeout=10)
                    
                    if success:
                        if latency_ms < 100:
                            status = f"{Colors.GREEN}优秀{Colors.NC}"
                            latency = f"{Colors.GREEN}{latency_ms}ms{Colors.NC}"
                        elif latency_ms < 300:
                            status = f"{Colors.YELLOW}良好{Colors.NC}"
                            latency = f"{Colors.YELLOW}{latency_ms}ms{Colors.NC}"
                        else:
                            status = f"{Colors.RED}较慢{Colors.NC}"
                            latency = f"{Colors.RED}{latency_ms}ms{Colors.NC}"
                        note = f"{server}:{port}"
                    else:
                        status = f"{Colors.RED}离线{Colors.NC}"
                        latency = f"{Colors.RED}超时{Colors.NC}"
                        note = "连接失败"
                        
                # 记录结果用于排序
                results.append((latency_ms if success else 9999, test_node_id, name, node_type))
            else:
                status = f"{Colors.YELLOW}未知{Colors.NC}"
                latency = f"{Colors.YELLOW}N/A{Colors.NC}"
                note = "未知类型"
            
            print(f"{name:<25} {node_type:<12} {status:<15} {latency:<15} {note}")
        
        print("-" * 80)
        
        # 显示最快的节点推荐
        if results:
            # 按延迟排序
            results.sort(key=lambda x: x[0])
            fastest = results[0]
            if fastest[0] < 9999:  # 有成功的连接
                print(f"{Colors.GREEN}🏆 推荐最快节点: {fastest[2]} ({fastest[0]}ms){Colors.NC}")
                
                # 询问是否切换到最快节点
                if fastest[1] != config.get('current_node'):
                    switch = input(f"{Colors.YELLOW}是否切换到最快节点? (Y/n): {Colors.NC}").strip().lower()
                    if not switch or switch.startswith('y'):
                        config['current_node'] = fastest[1]
                        self.save_nodes_config(config)
                        self.logger.info(f"✓ 已切换到节点: {fastest[2]}")
                        
                        # 重新生成配置并重启服务
                        try:
                            from core import SingToolManager
                            manager = SingToolManager()
                            manager.create_main_config()
                            manager.restart_service()
                        except:
                            self.logger.warn("请手动重启服务以应用新节点")
        
        print()
        print(f"{Colors.CYAN}说明:{Colors.NC}")
        print("  ● = 当前活动节点  ○ = 其他节点")
        print("  延迟测试仅测试TCP连接，实际使用速度可能有所不同")
    
    def speed_test_specific_node(self):
        """测试指定节点的速度"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        
        if not nodes:
            self.logger.error("暂无节点可测试")
            return
        
        # 显示节点列表
        print()
        print(f"{Colors.CYAN}📋 选择要测试的节点:{Colors.NC}")
        print("----------------------------------------")
        
        node_list = []
        for node_id, node_info in nodes.items():
            name = node_info.get('name', node_id)
            node_type = node_info.get('type', 'unknown')
            is_current = '●' if node_id == config.get('current_node') else '○'
            
            print(f"  {is_current} {len(node_list) + 1}. {name} ({node_type})")
            node_list.append((node_id, name, node_type))
        
        print("----------------------------------------")
        print(f"  0. 返回上级菜单")
        print()
        
        while True:
            try:
                choice = input("请选择要测试的节点编号: ").strip()
                if choice == "0":
                    return
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(node_list):
                    selected_node = node_list[choice_num - 1]
                    break
                else:
                    print(f"{Colors.YELLOW}请输入 0-{len(node_list)} 之间的数字{Colors.NC}")
            except ValueError:
                print(f"{Colors.YELLOW}请输入有效的数字{Colors.NC}")
        
        # 测试选定的节点
        node_id, name, node_type = selected_node
        node_info = nodes[node_id]
        config_data = node_info.get('config', {})
        
        print()
        self.logger.step(f"测试节点: {name}")
        print()
        
        if node_type in ['local_server', 'local_client']:
            if node_type == 'local_server':
                port = config_data.get('listen_port', 5566)
                if self._is_port_in_use(port):
                    print(f"✓ 本地服务器端口 {port} 正在监听")
                    print(f"✓ 延迟: < 1ms (本地连接)")
                else:
                    print(f"✗ 本地服务器端口 {port} 未监听")
            else:
                server = config_data.get('server', '127.0.0.1')
                port = config_data.get('port', 5566)
                print(f"测试连接: {server}:{port}")
                
                success, latency = self._test_tcp_connection(server, port)
                if success:
                    print(f"✓ 连接成功")
                    print(f"✓ 延迟: {latency}ms")
                else:
                    print(f"✗ 连接失败")
                    
        elif node_type in ['trojan', 'vless', 'shadowsocks', 'vmess', 'hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
            server = config_data.get('server', '')
            port = config_data.get('port', 443)
            
            if not server:
                print(f"✗ 节点配置错误: 缺少服务器地址")
                return
            
            print(f"测试连接: {server}:{port}")
            print("正在测试TCP连接...")
            
            # 进行多次测试取平均值
            test_times = 3
            successful_tests = []
            
            for i in range(test_times):
                print(f"  第 {i+1}/{test_times} 次测试...", end=" ")
                success, latency = self._test_tcp_connection(server, port, timeout=10)
                
                if success:
                    successful_tests.append(latency)
                    print(f"✓ {latency}ms")
                else:
                    print(f"✗ 超时")
            
            if successful_tests:
                avg_latency = sum(successful_tests) / len(successful_tests)
                min_latency = min(successful_tests)
                max_latency = max(successful_tests)
                
                print()
                print(f"📊 测试结果:")
                print(f"  成功率: {len(successful_tests)}/{test_times} ({len(successful_tests)/test_times*100:.1f}%)")
                print(f"  平均延迟: {avg_latency:.1f}ms")
                print(f"  最低延迟: {min_latency}ms")
                print(f"  最高延迟: {max_latency}ms")
                
                # 评估连接质量
                if avg_latency < 100:
                    quality = f"{Colors.GREEN}优秀{Colors.NC}"
                elif avg_latency < 300:
                    quality = f"{Colors.YELLOW}良好{Colors.NC}"
                else:
                    quality = f"{Colors.RED}较慢{Colors.NC}"
                
                print(f"  连接质量: {quality}")
            else:
                print()
                print(f"✗ 所有测试均失败，节点可能不可用")
        else:
            print(f"✗ 未知节点类型: {node_type}")
        
        print()

    def add_vmess_node(self, node_id: str, node_name: str) -> bool:
        """添加VMess节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置VMess节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        uuid = rich_menu.prompt_input("UUID")
        if not uuid:
            return False
            
        alter_id = rich_menu.prompt_input("AlterID [0]", default="0")
        try:
            alter_id = int(alter_id)
        except ValueError:
            alter_id = 0
            
        security = rich_menu.prompt_input("加密方式 [auto]", default="auto")
        network = rich_menu.prompt_input("传输协议 [tcp]", default="tcp")
        
        # TLS配置
        tls = rich_menu.prompt_confirm("启用TLS?", default=True)
        sni = ""
        if tls:
            sni = rich_menu.prompt_input("SNI (留空使用服务器地址)", default=server)
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "vmess",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "uuid": uuid,
                "alter_id": alter_id,
                "security": security,
                "network": network,
                "tls": tls
            }
        }
        
        if sni:
            node_config["config"]["sni"] = sni
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ VMess 节点添加成功: {node_name}")
        return True

    def add_hysteria2_node(self, node_id: str, node_name: str) -> bool:
        """添加Hysteria2节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置Hysteria2节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        password = rich_menu.prompt_input("密码")
        if not password:
            return False
            
        # 可选配置
        obfs = rich_menu.prompt_input("混淆密码 (留空不使用)")
        up_mbps = rich_menu.prompt_input("上行带宽限制(Mbps) [100]", default="100")
        down_mbps = rich_menu.prompt_input("下行带宽限制(Mbps) [100]", default="100")
        
        try:
            up_mbps = int(up_mbps)
            down_mbps = int(down_mbps)
        except ValueError:
            up_mbps = 100
            down_mbps = 100
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "hysteria2",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "password": password,
                "up_mbps": up_mbps,
                "down_mbps": down_mbps
            }
        }
        
        if obfs:
            node_config["config"]["obfs"] = obfs
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ Hysteria2 节点添加成功: {node_name}")
        return True

    def add_tuic_node(self, node_id: str, node_name: str) -> bool:
        """添加TUIC节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置TUIC节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        uuid = rich_menu.prompt_input("UUID")
        if not uuid:
            return False
            
        password = rich_menu.prompt_input("密码")
        if not password:
            return False
            
        version = rich_menu.prompt_input("TUIC版本 [5]", default="5")
        alpn = rich_menu.prompt_input("ALPN [h3]", default="h3")
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "tuic",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "uuid": uuid,
                "password": password,
                "version": version,
                "alpn": alpn
            }
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ TUIC 节点添加成功: {node_name}")
        return True

    def add_reality_node(self, node_id: str, node_name: str) -> bool:
        """添加Reality节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置Reality节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        uuid = rich_menu.prompt_input("UUID")
        if not uuid:
            return False
            
        public_key = rich_menu.prompt_input("公钥")
        if not public_key:
            return False
            
        short_id = rich_menu.prompt_input("Short ID")
        if not short_id:
            return False
            
        server_name = rich_menu.prompt_input("伪装域名")
        if not server_name:
            return False
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "reality",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "uuid": uuid,
                "public_key": public_key,
                "short_id": short_id,
                "server_name": server_name
            }
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ Reality 节点添加成功: {node_name}")
        return True

    def add_shadowtls_node(self, node_id: str, node_name: str) -> bool:
        """添加ShadowTLS节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置ShadowTLS节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        password = rich_menu.prompt_input("密码")
        if not password:
            return False
            
        handshake_server = rich_menu.prompt_input("握手服务器")
        if not handshake_server:
            return False
            
        handshake_port = rich_menu.prompt_input("握手端口 [443]", default="443")
        try:
            handshake_port = int(handshake_port)
        except ValueError:
            handshake_port = 443
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "shadowtls",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "password": password,
                "handshake_server": handshake_server,
                "handshake_port": handshake_port
            }
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ ShadowTLS 节点添加成功: {node_name}")
        return True

    def add_wireguard_node(self, node_id: str, node_name: str) -> bool:
        """添加WireGuard节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置WireGuard节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [51820]", default="51820")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        private_key = rich_menu.prompt_input("客户端私钥")
        if not private_key:
            return False
            
        peer_public_key = rich_menu.prompt_input("服务器公钥")
        if not peer_public_key:
            return False
            
        local_address = rich_menu.prompt_input("本地IP地址 [10.0.0.2/24]", default="10.0.0.2/24")
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "wireguard",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "private_key": private_key,
                "peer_public_key": peer_public_key,
                "local_address": local_address
            }
        }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ WireGuard 节点添加成功: {node_name}")
        return True

    def add_hysteria_node(self, node_id: str, node_name: str) -> bool:
        """添加Hysteria节点"""
        from rich_menu import RichMenu
        rich_menu = RichMenu()
        
        self.logger.step(f"配置Hysteria节点: {node_name}")
        print()
        
        # 获取服务器信息
        server = rich_menu.prompt_input("服务器地址")
        if not server:
            return False
            
        port = rich_menu.prompt_input("端口 [443]", default="443")
        try:
            port = int(port)
        except ValueError:
            rich_menu.print_error("端口必须是数字")
            return False
            
        auth_str = rich_menu.prompt_input("认证字符串")
        if not auth_str:
            return False
            
        # 可选配置
        obfs = rich_menu.prompt_input("混淆密码 (留空不使用)")
        protocol = rich_menu.prompt_input("协议 [udp]", default="udp")
        up_mbps = rich_menu.prompt_input("上行带宽限制(Mbps) [100]", default="100")
        down_mbps = rich_menu.prompt_input("下行带宽限制(Mbps) [100]", default="100")
        
        try:
            up_mbps = int(up_mbps)
            down_mbps = int(down_mbps)
        except ValueError:
            up_mbps = 100
            down_mbps = 100
        
        # 构建节点配置
        node_config = {
            "name": node_name,
            "type": "hysteria",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "auth_str": auth_str,
                "protocol": protocol,
                "up_mbps": up_mbps,
                "down_mbps": down_mbps
            }
        }
        
        if obfs:
            node_config["config"]["obfs"] = obfs
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ Hysteria 节点添加成功: {node_name}")
        return True

    def import_nodes_from_yaml(self, yaml_text: str) -> int:
        """从YAML文本导入节点配置
        
        Args:
            yaml_text: YAML格式的节点配置文本
            
        Returns:
            int: 成功导入的节点数量
        """
        try:
            import yaml
            import re
            
            # 尝试解析YAML
            try:
                # 处理包含列表的YAML
                if yaml_text.strip().startswith('-'):
                    data = yaml.safe_load(yaml_text)
                else:
                    # 如果不是列表格式，尝试包装成列表
                    data = yaml.safe_load(f"proxies:\n{yaml_text}")
                    if isinstance(data, dict) and 'proxies' in data:
                        data = data['proxies']
            except yaml.YAMLError:
                # 如果YAML解析失败，尝试逐行解析
                data = []
                for line in yaml_text.strip().split('\n'):
                    line = line.strip()
                    if line.startswith('- {') and line.endswith('}'):
                        try:
                            # 移除开头的 "- " 
                            node_str = line[2:]
                            node_data = yaml.safe_load(node_str)
                            data.append(node_data)
                        except:
                            continue
            
            if not isinstance(data, list):
                self.logger.error("配置格式错误: 期望节点列表")
                return 0
            
            # 加载现有配置
            config = self.load_nodes_config()
            success_count = 0
            
            for node_data in data:
                if not isinstance(node_data, dict):
                    continue
                    
                name = node_data.get('name')
                node_type = node_data.get('type')
                
                if not name or not node_type:
                    self.logger.warn(f"跳过无效节点: 缺少name或type字段")
                    continue
                
                # 生成唯一的节点ID
                node_id = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
                original_id = node_id
                counter = 1
                while node_id in config.get('nodes', {}):
                    node_id = f"{original_id}_{counter}"
                    counter += 1
                
                # 转换节点配置
                converted_node = self._convert_clash_node_to_sing(node_data)
                if converted_node:
                    config['nodes'][node_id] = {
                        'name': name,
                        'type': node_type,
                        'protocol': node_type,
                        'config': converted_node
                    }
                    success_count += 1
                    self.logger.info(f"✓ 导入节点: {name} ({node_type})")
                else:
                    self.logger.warn(f"✗ 跳过不支持的节点: {name} ({node_type})")
            
            # 保存配置
            if success_count > 0:
                self.save_nodes_config(config)
                self.logger.info(f"成功导入 {success_count} 个节点")
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"导入节点失败: {str(e)}")
            return 0
    
    def _convert_clash_node_to_sing(self, clash_node: dict) -> dict:
        """将Clash格式节点转换为sing-box格式
        
        Args:
            clash_node: Clash格式的节点配置
            
        Returns:
            dict: sing-box格式的节点配置，如果不支持则返回None
        """
        node_type = clash_node.get('type', '').lower()
        
        if node_type == 'trojan':
            return self._convert_trojan_node(clash_node)
        elif node_type == 'vless':
            return self._convert_vless_node(clash_node)
        elif node_type == 'vmess':
            return self._convert_vmess_node(clash_node)
        elif node_type == 'ss' or node_type == 'shadowsocks':
            return self._convert_shadowsocks_node(clash_node)
        else:
            return None
    
    def _convert_trojan_node(self, clash_node: dict) -> dict:
        """转换Trojan节点"""
        config = {
            "type": "trojan",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "password": clash_node.get('password'),
            "tls": {
                "enabled": True,
                "insecure": clash_node.get('skip-cert-verify', False),
                "server_name": clash_node.get('sni', clash_node.get('servername', ''))
            }
        }
        
        # 处理WebSocket传输
        network = clash_node.get('network')
        if network == 'ws':
            ws_opts = clash_node.get('ws-opts', {})
            config["transport"] = {
                "type": "ws",
                "path": ws_opts.get('path', '/'),
                "headers": ws_opts.get('headers', {})
            }
        
        return config
    
    def _convert_vless_node(self, clash_node: dict) -> dict:
        """转换VLESS节点"""
        config = {
            "type": "vless",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "uuid": clash_node.get('uuid'),
            "tls": {
                "enabled": clash_node.get('tls', True),
                "insecure": clash_node.get('skip-cert-verify', False),
                "server_name": clash_node.get('servername', clash_node.get('sni', ''))
            }
        }
        
        # 处理WebSocket传输
        network = clash_node.get('network')
        if network == 'ws':
            ws_opts = clash_node.get('ws-opts', {})
            config["transport"] = {
                "type": "ws",
                "path": ws_opts.get('path', '/'),
                "headers": ws_opts.get('headers', {})
            }
        
        return config
    
    def _convert_vmess_node(self, clash_node: dict) -> dict:
        """转换VMess节点"""
        config = {
            "type": "vmess",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "uuid": clash_node.get('uuid'),
            "security": clash_node.get('cipher', 'auto'),
            "alter_id": clash_node.get('alterId', 0)
        }
        
        # 处理TLS
        if clash_node.get('tls'):
            config["tls"] = {
                "enabled": True,
                "insecure": clash_node.get('skip-cert-verify', False),
                "server_name": clash_node.get('servername', clash_node.get('sni', ''))
            }
        
        # 处理WebSocket传输
        network = clash_node.get('network')
        if network == 'ws':
            ws_opts = clash_node.get('ws-opts', {})
            config["transport"] = {
                "type": "ws",
                "path": ws_opts.get('path', '/'),
                "headers": ws_opts.get('headers', {})
            }
        
        return config
    
    def _convert_shadowsocks_node(self, clash_node: dict) -> dict:
        """转换Shadowsocks节点"""
        config = {
            "type": "shadowsocks",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "password": clash_node.get('password'),
            "method": clash_node.get('cipher', 'aes-256-gcm')
        }
        
        return config

    def _validate_sing_box_config(self) -> dict:
        """校验sing-box配置文件
        
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        try:
            # 检查配置文件是否存在
            if not self.paths.main_config.exists():
                return {'valid': False, 'error': '配置文件不存在'}
            
            # 使用sing-box check命令校验配置
            import subprocess
            result = subprocess.run(
                ['/opt/homebrew/bin/sing-box', 'check', '-c', str(self.paths.main_config)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {'valid': True, 'error': None}
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return {'valid': False, 'error': error_msg}
                
        except FileNotFoundError:
            return {'valid': False, 'error': 'sing-box 未安装或不在PATH中'}
        except subprocess.TimeoutExpired:
            return {'valid': False, 'error': '校验超时'}
        except Exception as e:
            return {'valid': False, 'error': f'校验失败: {str(e)}'}
    
    def _validate_node_config(self, node_info: dict) -> dict:
        """校验单个节点配置
        
        Args:
            node_info: 节点信息
            
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        try:
            node_type = node_info.get('type', '')
            config = node_info.get('config', {})
            
            # 基本字段检查
            if not node_type:
                return {'valid': False, 'error': '缺少节点类型'}
            
            if not config:
                return {'valid': False, 'error': '缺少配置信息'}
            
            # 根据节点类型进行特定校验
            if node_type == 'trojan':
                return self._validate_trojan_config(config)
            elif node_type == 'vless':
                return self._validate_vless_config(config)
            elif node_type == 'vmess':
                return self._validate_vmess_config(config)
            elif node_type == 'shadowsocks':
                return self._validate_shadowsocks_config(config)
            elif node_type in ['hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
                return self._validate_other_config(config, node_type)
            elif node_type in ['local_server', 'local_client']:
                return self._validate_local_config(config, node_type)
            else:
                return {'valid': False, 'error': f'不支持的节点类型: {node_type}'}
                
        except Exception as e:
            return {'valid': False, 'error': f'校验出错: {str(e)}'}
    
    def _validate_trojan_config(self, config: dict) -> dict:
        """校验Trojan配置"""
        required_fields = ['server', 'port', 'password']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        # 检查端口范围
        port = config.get('port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            return {'valid': False, 'error': f'端口号无效: {port}'}
        
        return {'valid': True, 'error': None}
    
    def _validate_vless_config(self, config: dict) -> dict:
        """校验VLESS配置"""
        required_fields = ['server', 'port', 'uuid']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        # 检查UUID格式
        uuid_str = config.get('uuid', '')
        if len(uuid_str) != 36 or uuid_str.count('-') != 4:
            return {'valid': False, 'error': 'UUID格式无效'}
        
        return {'valid': True, 'error': None}
    
    def _validate_vmess_config(self, config: dict) -> dict:
        """校验VMess配置"""
        required_fields = ['server', 'port', 'uuid']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        # 检查UUID格式
        uuid_str = config.get('uuid', '')
        if len(uuid_str) != 36 or uuid_str.count('-') != 4:
            return {'valid': False, 'error': 'UUID格式无效'}
        
        return {'valid': True, 'error': None}
    
    def _validate_shadowsocks_config(self, config: dict) -> dict:
        """校验Shadowsocks配置"""
        required_fields = ['server', 'port', 'password', 'method']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        # 检查加密方法
        valid_methods = [
            'aes-256-gcm', 'aes-128-gcm', 'chacha20-ietf-poly1305', 
            'xchacha20-ietf-poly1305', 'aes-256-cfb', 'aes-128-cfb'
        ]
        method = config.get('method')
        if method not in valid_methods:
            return {'valid': False, 'error': f'不支持的加密方法: {method}'}
        
        return {'valid': True, 'error': None}
    
    def _validate_other_config(self, config: dict, node_type: str) -> dict:
        """校验其他类型节点配置"""
        required_fields = ['server', 'port']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def _validate_local_config(self, config: dict, node_type: str) -> dict:
        """校验本地节点配置"""
        if node_type == 'local_server':
            if not config.get('listen_port'):
                return {'valid': False, 'error': '缺少监听端口'}
        elif node_type == 'local_client':
            required_fields = ['server', 'port']
            for field in required_fields:
                if not config.get(field):
                    return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}