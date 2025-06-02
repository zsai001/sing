"""
重构后的节点管理器
Refactored Node Manager
"""

import json
import shutil
import time
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils import Colors, Logger
from paths import PathManager
from rich_menu import RichMenu

# 导入各个子模块
from node_tester import NodeTester
from node_validator import NodeValidator
from node_importer import NodeImporter
from node_display import NodeDisplay

# 导入协议处理器
from node_protocols import (
    TrojanNodeHandler, VlessNodeHandler, VmessNodeHandler,
    ShadowsocksNodeHandler, HysteriaNodeHandler, TuicNodeHandler,
    RealityNodeHandler, WireguardNodeHandler, ShadowTlsNodeHandler,
    LocalNodeHandler
)


class NodeManager:
    """重构后的节点管理类 - 负责节点的增删改查和协调各个子模块"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
        self.rich_menu = RichMenu()
        
        # 初始化子模块
        self.tester = NodeTester(logger)
        self.validator = NodeValidator(paths, logger)
        self.importer = NodeImporter(logger)
        self.display = NodeDisplay(logger)
        
        # 初始化协议处理器
        self.protocol_handlers = {
            'trojan': TrojanNodeHandler(logger),
            'vless': VlessNodeHandler(logger),
            'vmess': VmessNodeHandler(logger),
            'shadowsocks': ShadowsocksNodeHandler(logger),
            'hysteria2': HysteriaNodeHandler(logger),
            'hysteria': HysteriaNodeHandler(logger),
            'tuic': TuicNodeHandler(logger),
            'reality': RealityNodeHandler(logger),
            'wireguard': WireguardNodeHandler(logger),
            'shadowtls': ShadowTlsNodeHandler(logger),
            'local_server': LocalNodeHandler(logger),
            'local_client': LocalNodeHandler(logger)
        }
    
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
        if self.paths.nodes_config.exists():
            backup_file = self.paths.backup_dir / f"nodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.paths.backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.paths.nodes_config, backup_file)
        
        with open(self.paths.nodes_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def show_nodes(self):
        """显示节点列表"""
        self.logger.step("显示节点列表...")
        
        config = self.load_nodes_config()
        current_node = config.get('current_node')
        nodes = config.get('nodes', {})
        
        if not nodes:
            self.rich_menu.print_warning("暂无节点，请添加节点")
            return
        
        # 缓存文件路径
        cache_file = self.paths.config_dir / "node_cache.json"
        cache_data = self._load_cache(cache_file)
        
        print()
        self.rich_menu.print_info(f"检测到 {len(nodes)} 个节点")
        
        # 先校验配置
        config_status = self.validator.validate_sing_box_config()
        if config_status['valid']:
            self.rich_menu.print_success("✓ 当前配置文件校验通过")
        else:
            self.rich_menu.print_error("✗ 当前配置文件校验失败")
            if config_status['error']:
                self.rich_menu.print_warning(f"错误信息: {config_status['error']}")
        
        # 显示节点表格
        self.display.show_nodes_table(nodes, current_node, cache_data)
        
        # 显示配置错误的详细信息
        error_nodes = []
        for node_id, node_info in nodes.items():
            node_config_status = self.validator.validate_node_config(node_info)
            if not node_config_status['valid']:
                error_nodes.append((node_id, node_info.get('name', node_id), node_config_status['error']))
        
        if error_nodes:
            print()
            self.rich_menu.print_warning("⚠️ 发现配置错误的节点:")
            for node_id, name, error in error_nodes:
                self.rich_menu.print_error(f"  {name} ({node_id}): {error}")
        
        print()
        self.rich_menu.print_info("节点操作选项:")
        print("1. 🔄 开始测试节点")
        print("0. 🔙 返回上级菜单")
        print()
        
        while True:
            choice = self.rich_menu.prompt_choice("请选择操作 [0-1]")
            
            if choice == "1":
                # 开始测试节点
                print()
                self.rich_menu.print_info("🔄 开始动态刷新节点状态...")
                self.rich_menu.print_warning("按回车键退出监控")
                print()
                self._start_dynamic_refresh(nodes, current_node, cache_file, cache_data)
                break
                
            elif choice == "0":
                # 返回上级菜单
                break
                
            else:
                self.rich_menu.print_error("无效选项，请重新选择")
    
    def add_node(self, protocol_type: str, node_id: str = None, node_name: str = None) -> bool:
        """添加节点 - 统一接口"""
        if not node_id:
            node_id = input("请输入节点ID: ").strip()
            if not node_id:
                self.logger.error("节点ID不能为空")
                return False
        
        if not node_name:
            node_name = input("请输入节点名称: ").strip()
            if not node_name:
                self.logger.error("节点名称不能为空")
                return False
        
        # 检查节点ID是否已存在
        config = self.load_nodes_config()
        if node_id in config.get('nodes', {}):
            self.logger.error(f"节点ID '{node_id}' 已存在")
            return False
        
        # 获取对应的协议处理器
        handler = self.protocol_handlers.get(protocol_type)
        if not handler:
            self.logger.error(f"不支持的协议类型: {protocol_type}")
            return False
        
        # 调用协议处理器添加节点
        if protocol_type in ['local_server', 'local_client']:
            node_config = handler.add_node(node_id, node_name, protocol_type)
        else:
            node_config = handler.add_node(node_id, node_name)
        
        if node_config:
            # 保存配置
            config['nodes'][node_id] = node_config
            self.save_nodes_config(config)
            return True
        
        return False
    
    def delete_node(self, node_name: str = None) -> bool:
        """删除节点 - 支持按名称删除"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        current_node = config.get('current_node')
        
        if not nodes:
            self.logger.error("暂无节点可删除")
            return False
        
        target_node_id = None
        target_node_name = None
        
        if not node_name:
            # 显示可删除的节点列表
            print()
            print(f"{Colors.CYAN}📋 可删除的节点列表:{Colors.NC}")
            print("----------------------------------------")
            
            node_list = []
            for node_id, node_info in nodes.items():
                name = node_info.get('name', node_id)
                node_type = node_info.get('type', 'unknown')
                is_current = '●' if node_id == current_node else '○'
                current_text = ' (当前活动)' if node_id == current_node else ''
                
                print(f"  {is_current} {name} - {node_type}{current_text}")
                node_list.append((node_id, name))
            
            print("----------------------------------------")
            print(f"{Colors.YELLOW}● = 当前活动节点  ○ = 其他节点{Colors.NC}")
            print()
            
            # 让用户输入要删除的节点名称
            while True:
                user_input = input("请输入要删除的节点名称 (或输入 'q' 退出): ").strip()
                
                if user_input.lower() in ['q', 'quit', 'exit']:
                    self.logger.info("取消删除")
                    return False
                
                if not user_input:
                    print(f"{Colors.YELLOW}提示: 节点名称不能为空{Colors.NC}")
                    continue
                
                # 查找匹配的节点
                matches = []
                for node_id, name in node_list:
                    if user_input == name or user_input == node_id:
                        matches.append((node_id, name))
                    elif user_input.lower() in name.lower():
                        matches.append((node_id, name))
                
                if len(matches) == 0:
                    print(f"{Colors.YELLOW}未找到匹配的节点: '{user_input}'{Colors.NC}")
                    print("可用的节点名称:")
                    for _, name in node_list:
                        print(f"  - {name}")
                    continue
                elif len(matches) == 1:
                    target_node_id, target_node_name = matches[0]
                    break
                else:
                    print(f"{Colors.YELLOW}找到多个匹配的节点:{Colors.NC}")
                    for i, (node_id, name) in enumerate(matches, 1):
                        print(f"  {i}. {name} ({node_id})")
                    
                    try:
                        choice = int(input("请选择要删除的节点编号: ").strip())
                        if 1 <= choice <= len(matches):
                            target_node_id, target_node_name = matches[choice - 1]
                            break
                        else:
                            print(f"{Colors.YELLOW}无效的选择{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.YELLOW}请输入有效的数字{Colors.NC}")
        else:
            # 通过传入的名称查找节点
            for node_id, node_info in nodes.items():
                if node_name == node_info.get('name', node_id) or node_name == node_id:
                    target_node_id = node_id
                    target_node_name = node_info.get('name', node_id)
                    break
            
            if not target_node_id:
                self.logger.error(f"节点 '{node_name}' 不存在")
                return False
        
        # 执行删除逻辑
        return self._execute_delete_node(config, target_node_id, target_node_name, current_node)
    
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
        
        # 重新生成配置并重启服务
        try:
            from core import SingToolManager
            manager = SingToolManager()
            self.logger.info("正在重新生成配置...")
            if manager.create_main_config():
                self.logger.info("正在重启服务...")
                if manager.restart_service():
                    self.logger.info("✓ 节点切换完成，服务已重启")
                else:
                    self.logger.warn("⚠️  配置已更新，但服务重启失败，请手动重启")
            else:
                self.logger.error("配置生成失败")
                return False
        except Exception as e:
            self.logger.error(f"重新生成配置时出错: {e}")
            self.logger.warn("请手动重新生成配置并重启服务")
        
        return True
    
    def test_node_connectivity(self, node_id: str = None) -> bool:
        """测试节点连通性"""
        config = self.load_nodes_config()
        nodes = config.get('nodes', {})
        
        return self.tester.test_node_connectivity(nodes, node_id)
    
    def import_nodes_from_yaml(self, yaml_text: str) -> int:
        """从YAML文本导入节点配置"""
        converted_nodes = self.importer.import_nodes_from_yaml(yaml_text)
        
        if converted_nodes:
            config = self.load_nodes_config()
            
            for node_data in converted_nodes:
                node_id = node_data['id']
                
                # 确保节点ID唯一
                original_id = node_id
                counter = 1
                while node_id in config.get('nodes', {}):
                    node_id = f"{original_id}_{counter}"
                    counter += 1
                
                config['nodes'][node_id] = {
                    'name': node_data['name'],
                    'type': node_data['type'],
                    'protocol': node_data['type'],
                    'config': node_data['config']
                }
            
            self.save_nodes_config(config)
            self.logger.info(f"成功导入 {len(converted_nodes)} 个节点")
            return len(converted_nodes)
        
        return 0
    
    def _start_dynamic_refresh(self, nodes, current_node, cache_file, cache_data):
        """开始动态刷新节点状态"""
        # 这里可以调用原来的动态刷新逻辑，或者重新实现
        # 为了简化，这里只是一个占位符
        print("动态刷新功能需要进一步实现...")
        input("按回车键返回...")
    
    def _load_cache(self, cache_file: Path) -> dict:
        """加载缓存文件"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _execute_delete_node(self, config: Dict, target_node_id: str, target_node_name: str, current_node: str) -> bool:
        """执行删除节点的具体逻辑"""
        # 检查是否要删除当前活动节点
        is_current_node = (target_node_id == current_node)
        if is_current_node:
            print()
            print(f"{Colors.YELLOW}⚠️  警告: 您正在删除当前活动的节点!{Colors.NC}")
            print("删除后需要选择其他节点作为活动节点")
        
        # 显示要删除的节点信息
        node_info = config['nodes'][target_node_id]
        node_type = node_info.get('type', 'unknown')
        print()
        print(f"{Colors.CYAN}📋 节点信息:{Colors.NC}")
        print(f"  节点名称: {Colors.GREEN}{target_node_name}{Colors.NC}")
        print(f"  节点ID: {Colors.GREEN}{target_node_id}{Colors.NC}")
        print(f"  节点类型: {Colors.GREEN}{node_type}{Colors.NC}")
        if 'config' in node_info:
            config_data = node_info['config']
            if 'server' in config_data and 'port' in config_data:
                print(f"  服务器: {Colors.GREEN}{config_data['server']}:{config_data['port']}{Colors.NC}")
        
        # 确认删除
        print()
        print(f"{Colors.RED}⚠️  确定要删除节点 '{target_node_name}' 吗?{Colors.NC}")
        confirm = input(f"{Colors.YELLOW}请输入 'yes' 确认删除:{Colors.NC} ")
        
        if confirm != 'yes':
            self.logger.info("取消删除")
            return False
        
        # 删除节点
        del config['nodes'][target_node_id]
        
        # 如果删除的是当前节点，需要处理当前节点选择
        if is_current_node:
            remaining_nodes = config.get('nodes', {})
            if remaining_nodes:
                # 有其他节点，让用户选择新的活动节点
                print()
                print(f"{Colors.CYAN}选择新的活动节点:{Colors.NC}")
                node_list = list(remaining_nodes.items())
                for i, (node_id, node_info) in enumerate(node_list, 1):
                    name = node_info.get('name', node_id)
                    node_type = node_info.get('type', 'unknown')
                    print(f"  {i}. {name} - {node_type}")
                
                while True:
                    try:
                        choice = input("请选择新的活动节点编号 (或输入 'none' 不设置): ").strip()
                        if choice.lower() == 'none':
                            config['current_node'] = None
                            break
                        
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(node_list):
                            new_node_id = node_list[choice_num - 1][0]
                            config['current_node'] = new_node_id
                            new_node_name = node_list[choice_num - 1][1].get('name', new_node_id)
                            self.logger.info(f"✓ 已切换到节点: {new_node_name}")
                            break
                        else:
                            print(f"{Colors.YELLOW}请输入 1-{len(node_list)} 之间的数字{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.YELLOW}请输入有效的数字或 'none'{Colors.NC}")
            else:
                # 没有其他节点了
                config['current_node'] = None
                self.logger.warn("所有节点已删除，当前无活动节点")
        
        # 保存配置
        self.save_nodes_config(config)
        self.logger.info(f"✓ 节点 '{target_node_name}' 删除成功")
        return True 