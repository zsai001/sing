"""
Hysteria协议节点处理器
Hysteria Protocol Node Handlers
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from rich_menu import RichMenu


class HysteriaNodeHandler(BaseNodeHandler):
    """Hysteria协议处理器 (包含Hysteria和Hysteria2)"""
    
    def add_node(self, node_id: str, node_name: str, version: str = "hysteria2") -> bool:
        """添加Hysteria节点"""
        rich_menu = RichMenu()
        
        self.logger.step(f"配置{version.capitalize()}节点: {node_name}")
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
        
        if version == "hysteria2":
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
            node_config = self.get_base_config(node_name, "hysteria2")
            node_config["config"].update({
                "server": server,
                "port": port,
                "password": password,
                "up_mbps": up_mbps,
                "down_mbps": down_mbps
            })
            
            if obfs:
                node_config["config"]["obfs"] = obfs
                
        else:  # hysteria
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
            node_config = self.get_base_config(node_name, "hysteria")
            node_config["config"].update({
                "server": server,
                "port": port,
                "auth_str": auth_str,
                "protocol": protocol,
                "up_mbps": up_mbps,
                "down_mbps": down_mbps
            })
            
            if obfs:
                node_config["config"]["obfs"] = obfs
        
        self.logger.info(f"✓ {version.capitalize()} 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验Hysteria配置"""
        required_fields = ['server', 'port']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换Hysteria节点 (基础实现)"""
        # Hysteria的Clash格式转换比较复杂，这里提供基础实现
        return None


class TuicNodeHandler(BaseNodeHandler):
    """TUIC节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加TUIC节点"""
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
        node_config = self.get_base_config(node_name, "tuic")
        node_config["config"].update({
            "server": server,
            "port": port,
            "uuid": uuid,
            "password": password,
            "version": version,
            "alpn": alpn
        })
        
        self.logger.info(f"✓ TUIC 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验TUIC配置"""
        required_fields = ['server', 'port', 'uuid', 'password']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换TUIC节点"""
        return None


class RealityNodeHandler(BaseNodeHandler):
    """Reality节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加Reality节点"""
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
        node_config = self.get_base_config(node_name, "reality")
        node_config["config"].update({
            "server": server,
            "port": port,
            "uuid": uuid,
            "public_key": public_key,
            "short_id": short_id,
            "server_name": server_name
        })
        
        self.logger.info(f"✓ Reality 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验Reality配置"""
        required_fields = ['server', 'port', 'uuid', 'public_key', 'short_id', 'server_name']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换Reality节点"""
        return None 