"""
Shadowsocks协议节点处理器
Shadowsocks Protocol Node Handler
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from utils import Colors


class ShadowsocksNodeHandler(BaseNodeHandler):
    """Shadowsocks节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加Shadowsocks节点"""
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
        
        node_config = self.get_base_config(node_name, "shadowsocks")
        node_config["config"].update({
            "server": server,
            "port": port,
            "password": password,
            "method": method
        })
        
        self.logger.info(f"✓ Shadowsocks 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
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
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换Shadowsocks节点"""
        config = {
            "type": "shadowsocks",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "password": clash_node.get('password'),
            "method": clash_node.get('cipher', 'aes-256-gcm')
        }
        
        return config 