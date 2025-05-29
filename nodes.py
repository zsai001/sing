#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
节点管理模块 - 节点增删改查和连接测试
SingTool Nodes Module
"""

import json
import socket
import time
import uuid
import secrets
import string
from datetime import datetime
from typing import Dict
from utils import Colors, Logger
from paths import PathManager

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
        self.logger.step("显示节点列表...")
        print()
        
        config = self.load_nodes_config()
        current_node = config.get('current_node')
        nodes = config.get('nodes', {})
        
        if current_node:
            print(f"{Colors.CYAN}当前活动节点: {Colors.GREEN}{current_node}{Colors.NC}")
        else:
            print(f"{Colors.CYAN}当前活动节点: {Colors.YELLOW}无节点{Colors.NC}")
        
        print()
        print(f"{Colors.CYAN}可用节点列表:{Colors.NC}")
        print("----------------------------------------")
        
        if not nodes:
            print("  暂无节点，请添加节点")
        else:
            for node_id, node_info in nodes.items():
                name = node_info.get('name', node_id)
                node_type = node_info.get('type', 'unknown')
                enabled = node_info.get('enabled', False)
                
                status = '●' if node_id == current_node else '○'
                enabled_str = '启用' if enabled else '禁用'
                
                print(f"  {status} {node_id:<15} | {name:<20} | {node_type:<15} | {enabled_str}")
        
        print("----------------------------------------")
        print(f"{Colors.YELLOW}● = 当前节点  ○ = 其他节点{Colors.NC}")
    
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return False
            except OSError:
                return True
    
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
    
    def delete_node(self, node_id: str = None) -> bool:
        """删除节点"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        
        if not nodes:
            self.logger.error("暂无节点可删除")
            return False
        
        if not node_id:
            self.show_nodes()
            print()
            node_id = input("请输入要删除的节点ID: ").strip()
        
        if not node_id or node_id.lower() in ['q', 'quit', 'exit']:
            self.logger.info("取消删除")
            return False
        
        if node_id not in nodes:
            self.logger.error(f"节点 '{node_id}' 不存在")
            return False
        
        # 确认删除
        node_name = nodes[node_id].get('name', node_id)
        print(f"{Colors.RED}警告: 确定要删除节点 '{node_name}' ({node_id}) 吗?{Colors.NC}")
        confirm = input(f"{Colors.YELLOW}请输入 'yes' 确认删除:{Colors.NC} ")
        
        if confirm != 'yes':
            self.logger.info("取消删除")
            return False
        
        # 删除节点
        del config['nodes'][node_id]
        
        # 如果删除的是当前节点，清空当前节点选择
        if config.get('current_node') == node_id:
            config['current_node'] = None
            self.logger.warn("已删除当前活动节点，请选择新的节点")
        
        self.save_nodes_config(config)
        self.logger.info(f"✓ 节点 '{node_name}' 删除成功")
        return True
    
    def add_trojan_node(self, node_id: str, node_name: str) -> bool:
        """添加 Trojan 节点"""
        print()
        print(f"{Colors.BLUE}配置 Trojan 节点:{Colors.NC}")
        
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
        
        password = input("密码: ").strip()
        if not password:
            self.logger.error("密码不能为空")
            return False
        
        sni = input(f"SNI (默认 {server}): ").strip() or server
        transport = input("传输类型 (tcp/ws, 默认 tcp): ").strip().lower() or "tcp"
        
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
                    "insecure": False
                },
                "created_at": datetime.now().isoformat()
            }
        }
        
        if transport == "ws":
            ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
            ws_host = input(f"WebSocket Host (默认 {sni}): ").strip() or sni
            node_config["config"]["transport"] = {
                "type": "ws",
                "path": ws_path,
                "headers": {"Host": ws_host}
            }
        
        # 保存配置
        config = self.load_nodes_config()
        config["nodes"][node_id] = node_config
        self.save_nodes_config(config)
        
        self.logger.info(f"✓ Trojan 节点添加成功: {node_name}")
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
        
        transport = input("传输类型 (tcp/ws/grpc, 默认 tcp): ").strip().lower() or "tcp"
        
        node_config = {
            "name": node_name,
            "type": "vless",
            "enabled": True,
            "config": {
                "server": server,
                "port": port,
                "uuid": uuid_str,
                "transport": transport,
                "created_at": datetime.now().isoformat()
            }
        }
        
        if transport == "tcp":
            flow = input("Flow (留空为默认): ").strip()
            if flow:
                node_config["config"]["flow"] = flow
        elif transport == "ws":
            ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
            ws_host = input("WebSocket Host: ").strip() or server
            node_config["config"]["ws_path"] = ws_path
            node_config["config"]["ws_host"] = ws_host
        elif transport == "grpc":
            grpc_service = input("gRPC Service Name: ").strip()
            node_config["config"]["grpc_service"] = grpc_service
        
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
        
        for test_node_id, node_info in nodes_to_test.items():
            name = node_info.get('name', test_node_id)
            node_type = node_info.get('type', 'unknown')
            config_data = node_info.get('config', {})
            
            print(f"测试节点: {name} ({test_node_id})")
            
            if node_type in ['local_server', 'local_client']:
                print("  本地节点 - 跳过网络测试")
            elif node_type in ['trojan', 'vless', 'vmess', 'shadowsocks']:
                server = config_data.get('server', '')
                port = config_data.get('port', 443)
                
                if server:
                    success, latency = self._test_tcp_connection(server, port)
                    if success:
                        print(f"  ✓ 连接成功 - 延迟: {latency}ms")
                    else:
                        print("  ✗ 连接失败")
                else:
                    print("  ✗ 服务器地址为空")
            else:
                print("  ? 未知节点类型")
            
            print()
        
        return True
    
    def _test_tcp_connection(self, host: str, port: int, timeout: int = 5) -> tuple:
        """测试TCP连接 (success, latency_ms)"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            end_time = time.time()
            sock.close()
            
            if result == 0:
                latency = int((end_time - start_time) * 1000)
                return True, latency
            else:
                return False, 0
        except Exception:
            return False, 0 