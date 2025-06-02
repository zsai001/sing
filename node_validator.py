"""
节点校验模块
Node Validation Module
"""

import subprocess
from typing import Dict
from pathlib import Path
from utils import Logger


class NodeValidator:
    """节点配置校验器"""
    
    def __init__(self, paths, logger: Logger):
        self.paths = paths
        self.logger = logger
    
    def validate_sing_box_config(self) -> dict:
        """校验sing-box配置文件
        
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        try:
            # 检查配置文件是否存在
            if not self.paths.main_config.exists():
                return {'valid': False, 'error': '配置文件不存在'}
            
            # 使用sing-box check命令校验配置
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
    
    def validate_node_config(self, node_info: dict) -> dict:
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