"""
WireGuard协议节点处理器
WireGuard Protocol Node Handler
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from rich_menu import RichMenu


class WireguardNodeHandler(BaseNodeHandler):
    """WireGuard节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加WireGuard节点"""
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
        node_config = self.get_base_config(node_name, "wireguard")
        node_config["config"].update({
            "server": server,
            "port": port,
            "private_key": private_key,
            "peer_public_key": peer_public_key,
            "local_address": local_address
        })
        
        self.logger.info(f"✓ WireGuard 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验WireGuard配置"""
        required_fields = ['server', 'port', 'private_key', 'peer_public_key']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换WireGuard节点"""
        # WireGuard在Clash中格式比较特殊，这里提供基础实现
        return None


class ShadowTlsNodeHandler(BaseNodeHandler):
    """ShadowTLS节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加ShadowTLS节点"""
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
        node_config = self.get_base_config(node_name, "shadowtls")
        node_config["config"].update({
            "server": server,
            "port": port,
            "password": password,
            "handshake_server": handshake_server,
            "handshake_port": handshake_port
        })
        
        self.logger.info(f"✓ ShadowTLS 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验ShadowTLS配置"""
        required_fields = ['server', 'port', 'password', 'handshake_server']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换ShadowTLS节点"""
        return None 