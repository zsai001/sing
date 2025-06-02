"""
VMess协议节点处理器
VMess Protocol Node Handler
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from rich_menu import RichMenu


class VmessNodeHandler(BaseNodeHandler):
    """VMess节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加VMess节点"""
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
        node_config = self.get_base_config(node_name, "vmess")
        node_config["config"].update({
            "server": server,
            "port": port,
            "uuid": uuid,
            "alter_id": alter_id,
            "security": security,
            "network": network,
            "tls": tls
        })
        
        if sni:
            node_config["config"]["sni"] = sni
        
        self.logger.info(f"✓ VMess 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
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
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换VMess节点"""
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