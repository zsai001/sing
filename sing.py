#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SingTool 主入口文件 - 模块化版本
sing-box macOS 管理工具 v2.0 Python版

使用模块化设计，将功能分散到不同模块中：
- utils: 通用工具类
- paths: 路径管理
- service: 服务管理  
- config: 配置管理
- nodes: 节点管理
- menu: 菜单系统
- core: 核心管理器
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import Colors, Logger
from core import SingToolManager
from nodes import NodeManager
from menu import MenuSystem


def main():
    """主函数"""
    try:
        # 初始化核心管理器
        manager = SingToolManager()
        
        # 检测系统
        if not manager.detect_os():
            sys.exit(1)
        
        # 初始化节点管理
        node_manager = NodeManager(manager.paths, manager.logger)
        node_manager.init_nodes_config()
        
        # 启动菜单系统
        menu = MenuSystem(manager, node_manager)
        
        # 处理命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == "nodes":
                node_manager.show_nodes()
            elif command == "status":
                manager.show_status()
            elif command == "help":
                menu.show_help()
            elif command == "start":
                manager.start_service()
            elif command == "stop":
                manager.stop_service()
            elif command == "restart":
                manager.restart_service()
            elif command == "install":
                manager.full_install()
            elif command == "uninstall":
                manager.uninstall()
            elif command == "logs":
                manager.view_logs()
            elif command == "test":
                node_manager.test_node_connectivity()
            elif command == "config":
                manager.create_main_config()
                manager.logger.info("✓ 配置文件已重新生成")
            else:
                manager.logger.error(f"未知命令: {command}")
                print()
                print(f"{Colors.CYAN}可用命令:{Colors.NC}")
                print("  nodes     - 显示节点列表")
                print("  status    - 显示详细状态")
                print("  start     - 启动服务")
                print("  stop      - 停止服务")
                print("  restart   - 重启服务")
                print("  install   - 完整安装")
                print("  uninstall - 卸载")
                print("  logs      - 查看日志")
                print("  test      - 测试节点连通性")
                print("  config    - 重新生成配置")
                print("  help      - 显示帮助")
                print()
                print("不带参数运行进入交互式菜单")
        else:
            # 启动交互式菜单
            menu.show_main_menu()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}用户中断操作{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}发生错误: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main() 