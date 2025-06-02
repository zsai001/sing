"""
VLESS协议节点处理器
VLESS Protocol Node Handler
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from utils import Colors


class VlessNodeHandler(BaseNodeHandler):
    """VLESS节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加VLESS节点"""
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
        
        node_config = self.get_base_config(node_name, "vless")
        node_config["config"].update({
            "server": server,
            "port": port,
            "uuid": uuid_str,
            "tls": {
                "enabled": True,
                "server_name": sni,
                "insecure": insecure
            }
        })
        
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
        
        self.logger.info(f"✓ VLESS 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
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
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换VLESS节点"""
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