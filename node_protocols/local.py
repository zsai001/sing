"""
本地节点处理器
Local Node Handler
"""

import socket
import secrets
import string
import uuid
from typing import Dict, Optional
from .base import BaseNodeHandler
from utils import Colors
from datetime import datetime


class LocalNodeHandler(BaseNodeHandler):
    """本地节点处理器 (包含服务器和客户端)"""
    
    def add_server_node(self, node_id: str, node_name: str) -> dict:
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
            return None
        
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
            return None
        
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
        
        return node_config
    
    def add_client_node(self, node_id: str, node_name: str) -> dict:
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
            return None
        
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
                return None
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
                return None
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
                return None
            method = input("加密方式 (默认 aes-256-gcm): ").strip() or "aes-256-gcm"
            node_config["config"]["password"] = password
            node_config["config"]["method"] = method
        
        else:
            self.logger.error(f"不支持的协议类型: {protocol}")
            return None
        
        self.logger.info(f"✓ 本地客户端节点添加成功: {node_name}")
        return node_config
    
    def add_node(self, node_id: str, node_name: str, node_type: str = "local_server") -> dict:
        """添加本地节点 (统一接口)"""
        if node_type == "local_server":
            return self.add_server_node(node_id, node_name)
        elif node_type == "local_client":
            return self.add_client_node(node_id, node_name)
        else:
            self.logger.error(f"不支持的本地节点类型: {node_type}")
            return None
    
    def validate_config(self, config: dict, node_type: str = None) -> dict:
        """校验本地节点配置"""
        if not node_type:
            # 从配置中推断类型
            if 'listen_port' in config:
                node_type = 'local_server'
            else:
                node_type = 'local_client'
        
        if node_type == 'local_server':
            if not config.get('listen_port'):
                return {'valid': False, 'error': '缺少监听端口'}
        elif node_type == 'local_client':
            required_fields = ['server', 'port']
            for field in required_fields:
                if not config.get(field):
                    return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """本地节点不支持从Clash格式转换"""
        return None
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False 