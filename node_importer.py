"""
节点导入模块
Node Import Module
"""

import yaml
import re
from typing import Dict, Optional
from utils import Logger
from node_protocols import (
    TrojanNodeHandler, VlessNodeHandler, VmessNodeHandler, 
    ShadowsocksNodeHandler
)


class NodeImporter:
    """节点导入器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        # 初始化协议处理器
        self.handlers = {
            'trojan': TrojanNodeHandler(logger),
            'vless': VlessNodeHandler(logger), 
            'vmess': VmessNodeHandler(logger),
            'shadowsocks': ShadowsocksNodeHandler(logger),
            'ss': ShadowsocksNodeHandler(logger)  # shadowsocks的别名
        }
    
    def import_nodes_from_yaml(self, yaml_text: str) -> int:
        """从YAML文本导入节点配置
        
        Args:
            yaml_text: YAML格式的节点配置文本
            
        Returns:
            int: 成功导入的节点数量
        """
        try:
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
            
            success_count = 0
            converted_nodes = []
            
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
                
                # 转换节点配置
                converted_node = self._convert_clash_node_to_sing(node_data)
                if converted_node:
                    converted_nodes.append({
                        'id': node_id,
                        'name': name,
                        'type': node_type,
                        'config': converted_node
                    })
                    success_count += 1
                    self.logger.info(f"✓ 转换节点: {name} ({node_type})")
                else:
                    self.logger.warn(f"✗ 跳过不支持的节点: {name} ({node_type})")
            
            if success_count > 0:
                self.logger.info(f"成功转换 {success_count} 个节点")
                return converted_nodes
            
            return []
            
        except Exception as e:
            self.logger.error(f"导入节点失败: {str(e)}")
            return []
    
    def _convert_clash_node_to_sing(self, clash_node: dict) -> Optional[dict]:
        """将Clash格式节点转换为sing-box格式
        
        Args:
            clash_node: Clash格式的节点配置
            
        Returns:
            dict: sing-box格式的节点配置，如果不支持则返回None
        """
        node_type = clash_node.get('type', '').lower()
        
        # 查找对应的处理器
        handler = self.handlers.get(node_type)
        if handler:
            return handler.convert_from_clash(clash_node)
        else:
            return None
    
    def import_from_url(self, url: str) -> int:
        """从URL导入节点配置"""
        try:
            import requests
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'yaml' in content_type or url.endswith('.yaml') or url.endswith('.yml'):
                return self.import_nodes_from_yaml(response.text)
            else:
                # 尝试按YAML格式解析
                return self.import_nodes_from_yaml(response.text)
                
        except Exception as e:
            self.logger.error(f"从URL导入失败: {str(e)}")
            return []
    
    def import_from_file(self, file_path: str) -> int:
        """从文件导入节点配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return self.import_nodes_from_yaml(content)
            else:
                # 尝试按YAML格式解析
                return self.import_nodes_from_yaml(content)
                
        except Exception as e:
            self.logger.error(f"从文件导入失败: {str(e)}")
            return [] 