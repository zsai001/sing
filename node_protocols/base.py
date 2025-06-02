"""
基础节点处理器
Base Node Handler
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime


class BaseNodeHandler(ABC):
    """节点处理器基类"""
    
    def __init__(self, logger):
        self.logger = logger
    
    @abstractmethod
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加节点"""
        pass
    
    @abstractmethod
    def validate_config(self, config: dict) -> dict:
        """校验节点配置
        
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        pass
    
    @abstractmethod
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换节点配置"""
        pass
    
    def get_base_config(self, name: str, node_type: str) -> dict:
        """获取基础节点配置"""
        return {
            "name": name,
            "type": node_type,
            "enabled": True,
            "config": {
                "created_at": datetime.now().isoformat()
            }
        } 