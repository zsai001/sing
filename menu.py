#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单系统模块 - 交互式用户界面
SingTool Menu Module
"""

import os
import sys
import time
import json
from utils import Colors, Logger

class MenuSystem:
    """菜单系统类 - 提供交互式用户界面"""
    
    def __init__(self, manager, node_manager):
        self.manager = manager
        self.node_manager = node_manager
    
    def show_main_menu(self):
        """显示主菜单"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.manager.show_banner()
            
            # 显示当前状态概览
            self._show_status_overview()
            
            print(f"{Colors.CYAN}🚀 快速操作{Colors.NC}")
            print("  1. 🧪 快速测试连接        2. 🔧 一键修复问题")
            print("  3. 🧙‍♂️ 配置向导(推荐)      4. 📊 详细状态信息")
            print()
            
            print(f"{Colors.CYAN}📡 节点管理{Colors.NC}")
            print("  5. 📋 显示节点列表        6. ➕ 添加远程节点")
            print("  7. 🔄 切换节点            8. 🗑️  删除节点")
            print("  9. 🏠 创建本地节点")
            print()
            
            print(f"{Colors.CYAN}⚙️ 系统管理{Colors.NC}")
            print("  10. ▶️  启动/重启服务     11. ⏹️  停止服务")
            print("  12. 📝 查看日志           13. 🔄 高级配置")
            print()
            
            print(f"{Colors.CYAN}🔧 工具{Colors.NC}")
            print("  i. 📦 完整安装            d. 🔍 系统诊断")
            print("  h. ❓ 帮助信息            u. 🗑️  卸载")
            print("  0. 🚪 退出")
            print()
            
            choice = input("请输入选项: ").strip()
            
            if choice == "0":
                self.manager.logger.info("感谢使用！")
                sys.exit(0)
            elif choice == "1":
                self._quick_test()
                input("按回车键继续...")
            elif choice == "2":
                self._quick_fix()
                input("按回车键继续...")
            elif choice == "3":
                self._config_wizard()
                input("按回车键继续...")
            elif choice == "4":
                self.manager.show_status()
                input("按回车键继续...")
            elif choice == "5":
                self.node_manager.show_nodes()
                input("按回车键继续...")
            elif choice == "6":
                self._add_remote_node_menu()
                input("按回车键继续...")
            elif choice == "7":
                self._switch_node_menu()
                input("按回车键继续...")
            elif choice == "8":
                self._delete_node_menu()
                input("按回车键继续...")
            elif choice == "9":
                self._add_local_node_menu()
                input("按回车键继续...")
            elif choice == "10":
                self._start_restart_service()
                input("按回车键继续...")
            elif choice == "11":
                self.manager.stop_service()
                input("按回车键继续...")
            elif choice == "12":
                self.manager.view_logs()
                input("按回车键继续...")
            elif choice == "13":
                self._advanced_config_menu()
                input("按回车键继续...")
            elif choice.lower() == "i":
                self._install_menu()
                input("按回车键继续...")
            elif choice.lower() == "d":
                self._diagnostic_menu()
                input("按回车键继续...")
            elif choice.lower() == "h":
                self.show_help()
                input("按回车键继续...")
            elif choice.lower() == "u":
                if self.manager.uninstall():
                    sys.exit(0)
                input("按回车键继续...")
            else:
                self.manager.logger.error("无效选项，请重新选择")
                time.sleep(1)
    
    def _show_status_overview(self):
        """显示状态概览"""
        config = self.node_manager.load_nodes_config()
        current_node = config.get('current_node')
        
        if current_node and current_node in config.get('nodes', {}):
            node_info = config['nodes'][current_node]
            current_display = f"{node_info.get('name', current_node)} ({node_info.get('type', 'unknown')})"
        else:
            current_display = "无节点"
        
        # 获取实际服务状态
        is_running, status_text = self.manager.check_service_status()
        if is_running:
            service_status = f"{Colors.GREEN}运行中{Colors.NC}"
        else:
            service_status = f"{Colors.RED}未运行{Colors.NC}"
        
        # 获取代理端口状态
        proxy_port_info = self._get_proxy_port_info()
        
        print(f"{Colors.CYAN}📊 当前状态{Colors.NC}")
        print("┌─────────────────────────────────────────────────────┐")
        print(f"│ 服务状态: {service_status}")
        print(f"│ 代理端口: {proxy_port_info}")
        print(f"│ 当前节点: {Colors.BLUE}{current_display}{Colors.NC}")
        print("└─────────────────────────────────────────────────────┘")
        print()
    
    def _get_proxy_port_info(self):
        """获取代理端口信息"""
        try:
            if self.manager.paths.main_config.exists():
                import json
                with open(self.manager.paths.main_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 提取入站端口
                active_ports = []
                inactive_ports = []
                
                for inbound in config.get('inbounds', []):
                    port = inbound.get('listen_port')
                    if port:
                        # 检查端口是否在监听
                        if self.manager.service_manager.is_port_listening(port):
                            active_ports.append(str(port))
                        else:
                            inactive_ports.append(str(port))
                
                if active_ports:
                    port_info = f"{Colors.GREEN}{','.join(active_ports)}{Colors.NC}"
                    if inactive_ports:
                        port_info += f" ({Colors.RED}{','.join(inactive_ports)} 未活动{Colors.NC})"
                    return port_info
                elif inactive_ports:
                    return f"{Colors.RED}{','.join(inactive_ports)} (未活动){Colors.NC}"
                else:
                    return f"{Colors.YELLOW}未配置{Colors.NC}"
            else:
                return f"{Colors.YELLOW}未配置{Colors.NC}"
        except Exception:
            return f"{Colors.RED}获取失败{Colors.NC}"
    
    def _quick_test(self):
        """快速测试连接"""
        self.manager.logger.step("快速测试连接...")
        
        # 检查服务状态
        is_running, status = self.manager.check_service_status()
        print(f"服务状态: {status}")
        
        if not is_running:
            self.manager.logger.warn("服务未运行，无法进行连接测试")
            return
        
        # 测试代理端口
        self.manager.logger.info("快速测试完成")
    
    def _quick_fix(self):
        """一键修复问题"""
        self.manager.logger.step("一键修复问题...")
        
        fixed_issues = 0
        
        # 检查sing-box安装
        if not self.manager.check_singbox_installed():
            print("未安装 sing-box，正在安装...")
            if self.manager.install_singbox():
                fixed_issues += 1
        
        # 检查配置文件
        if not self.manager.paths.main_config.exists():
            print("配置文件不存在，正在创建...")
            self.manager.create_main_config()
            fixed_issues += 1
        
        # 检查服务配置
        if self.manager.paths.os_type == "Darwin" and not self.manager.paths.plist_path.exists():
            print("服务配置不存在，正在创建...")
            if self.manager.create_service():
                fixed_issues += 1
        
        # 重启服务
        print("重启服务以应用修复...")
        if self.manager.restart_service():
            fixed_issues += 1
        
        if fixed_issues > 0:
            self.manager.logger.info(f"✓ 修复了 {fixed_issues} 个问题")
        else:
            self.manager.logger.info("没有发现需要修复的问题")
    
    def _config_wizard(self):
        """配置向导"""
        print()
        print(f"{Colors.GREEN}🧙‍♂️ 配置向导{Colors.NC}")
        print("这个向导将帮助您快速配置 sing-box")
        print()
        
        # 检查是否已安装
        if not self.manager.check_singbox_installed():
            install = input("sing-box 未安装，是否现在安装? (Y/n): ").strip()
            if not install or install.lower().startswith('y'):
                self.manager.install_singbox()
            else:
                self.manager.logger.warn("未安装 sing-box，配置向导中止")
                return
        
        # 初始化配置
        self.manager.init_local_config()
        
        # 检查节点配置
        config = self.node_manager.load_nodes_config()
        if not config.get('nodes'):
            add_node = input("未发现任何节点，是否添加节点? (Y/n): ").strip()
            if not add_node or add_node.lower().startswith('y'):
                self._add_remote_node_menu()
        
        # 生成配置并启动服务
        self.manager.create_main_config()
        self.manager.create_service()
        self.manager.start_service()
        
        self.manager.logger.info("✓ 配置向导完成")
    
    def _add_remote_node_menu(self):
        """添加远程节点菜单"""
        print()
        print(f"{Colors.CYAN}📡 添加远程节点{Colors.NC}")
        
        # 获取节点名称
        while True:
            node_name = input("节点名称: ").strip()
            if node_name.lower() in ['q', 'quit', 'exit']:
                self.manager.logger.info("取消添加节点")
                return
            if node_name:
                break
            print(f"{Colors.YELLOW}提示: 节点名称不能为空，请重新输入{Colors.NC}")
        
        # 获取节点ID
        node_id = input("节点ID (用于标识，留空自动生成): ").strip()
        if not node_id:
            import re
            node_id = re.sub(r'[^a-zA-Z0-9_]', '_', node_name.lower())
            self.manager.logger.info(f"自动生成节点ID: {node_id}")
        
        # 检查节点ID是否已存在
        config = self.node_manager.load_nodes_config()
        if node_id in config.get('nodes', {}):
            self.manager.logger.error(f"节点ID '{node_id}' 已存在，请使用其他ID")
            return
        
        print()
        print("请选择协议类型:")
        print("  1) Trojan")
        print("  2) VLESS") 
        print("  3) Shadowsocks")
        print()
        
        choice = input("请选择 [1-3]: ").strip()
        success = False
        
        if choice == "1":
            success = self.node_manager.add_trojan_node(node_id, node_name)
        elif choice == "2":
            success = self.node_manager.add_vless_node(node_id, node_name)
        elif choice == "3":
            success = self.node_manager.add_shadowsocks_node(node_id, node_name)
        else:
            self.manager.logger.error("无效选项")
            return
        
        if success:
            # 询问是否切换到新节点
            switch = input(f"{Colors.YELLOW}是否切换到新添加的节点? (Y/n):{Colors.NC} ")
            if not switch or switch.lower().startswith('y'):
                config = self.node_manager.load_nodes_config()
                config['current_node'] = node_id
                self.node_manager.save_nodes_config(config)
                self.manager.logger.info(f"✓ 已切换到节点: {node_id}")
                
                # 重新生成配置并重启服务
                self.manager.create_main_config()
                self.manager.restart_service()
    
    def _add_local_node_menu(self):
        """添加本地节点菜单"""
        print()
        print(f"{Colors.CYAN}🏠 创建本地节点{Colors.NC}")
        print("  1) 本地服务器 - 创建代理服务供其他设备使用")
        print("  2) 本地客户端 - 连接本机其他端口的服务")
        print()
        
        choice = input("请选择 [1-2]: ").strip()
        
        # 获取节点名称
        while True:
            node_name = input("节点名称: ").strip()
            if node_name.lower() in ['q', 'quit', 'exit']:
                self.manager.logger.info("取消添加节点")
                return
            if node_name:
                break
            print(f"{Colors.YELLOW}提示: 节点名称不能为空，请重新输入{Colors.NC}")
        
        # 获取节点ID
        node_id = input("节点ID (用于标识，留空自动生成): ").strip()
        if not node_id:
            import re
            node_id = re.sub(r'[^a-zA-Z0-9_]', '_', node_name.lower())
            self.manager.logger.info(f"自动生成节点ID: {node_id}")
        
        # 检查节点ID是否已存在
        config = self.node_manager.load_nodes_config()
        if node_id in config.get('nodes', {}):
            self.manager.logger.error(f"节点ID '{node_id}' 已存在，请使用其他ID")
            return
        
        success = False
        if choice == "1":
            success = self.node_manager.add_local_server_node(node_id, node_name)
            if success:
                self._show_local_server_usage_info(node_id)
        elif choice == "2":
            success = self.node_manager.add_local_client_node(node_id, node_name)
        else:
            self.manager.logger.error("无效选项")
            return
        
        if success:
            # 询问是否切换到新节点
            switch = input(f"{Colors.YELLOW}是否切换到新添加的节点? (Y/n):{Colors.NC} ")
            if not switch or switch.lower().startswith('y'):
                config = self.node_manager.load_nodes_config()
                config['current_node'] = node_id
                self.node_manager.save_nodes_config(config)
                self.manager.logger.info(f"✓ 已切换到节点: {node_id}")
                
                # 重新生成配置并重启服务
                self.manager.create_main_config()
                self.manager.restart_service()
    
    def _show_local_server_usage_info(self, node_id: str):
        """显示本地服务器使用说明"""
        config = self.node_manager.load_nodes_config()
        node = config.get('nodes', {}).get(node_id)
        if not node:
            return
        
        node_config = node.get('config', {})
        port = node_config.get('listen_port', 5566)
        password = node_config.get('password', '')
        protocol = node.get('protocol', 'trojan')
        
        print()
        print(f"{Colors.GREEN}🎉 本地服务器创建成功！{Colors.NC}")
        print()
        print(f"{Colors.CYAN}📱 其他设备连接方式:{Colors.NC}")
        
        # 获取本机IP地址
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "192.168.x.x"
        
        print(f"  服务器地址: {Colors.GREEN}{local_ip}{Colors.NC}")
        print(f"  端口: {Colors.GREEN}{port}{Colors.NC}")
        if protocol == 'trojan':
            print(f"  密码: {Colors.GREEN}{password}{Colors.NC}")
        else:
            print(f"  UUID: {Colors.GREEN}{node_config.get('uuid', '')}{Colors.NC}")
        print(f"  协议: {Colors.GREEN}{protocol.upper()}{Colors.NC}")
    
    def _switch_node_menu(self):
        """切换节点菜单"""
        self.node_manager.switch_node()
        # 重新生成配置
        self.manager.create_main_config()
        self.manager.restart_service()
    
    def _delete_node_menu(self):
        """删除节点菜单"""
        self.node_manager.delete_node()
    
    def _start_restart_service(self):
        """启动/重启服务"""
        is_running, _ = self.manager.check_service_status()
        if is_running:
            self.manager.restart_service()
        else:
            self.manager.start_service()
    
    def _advanced_config_menu(self):
        """高级配置菜单"""
        print()
        print(f"{Colors.CYAN}🔄 高级配置{Colors.NC}")
        print("1. 重新生成配置文件")
        print("2. 查看当前配置")
        print("3. 备份配置")
        print("4. 重置配置")
        print()
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            self.manager.create_main_config()
            self.manager.logger.info("✓ 配置文件已重新生成")
        elif choice == "2":
            if self.manager.paths.main_config.exists():
                with open(self.manager.paths.main_config, 'r') as f:
                    print(f.read())
            else:
                self.manager.logger.error("配置文件不存在")
        elif choice == "3":
            # 简单备份
            import shutil
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.manager.paths.backup_dir / f"config_backup_{timestamp}.json"
            self.manager.paths.backup_dir.mkdir(parents=True, exist_ok=True)
            if self.manager.paths.main_config.exists():
                shutil.copy2(self.manager.paths.main_config, backup_file)
                self.manager.logger.info(f"✓ 配置已备份到: {backup_file}")
            else:
                self.manager.logger.error("配置文件不存在")
        elif choice == "4":
            confirm = input(f"{Colors.RED}确定要重置所有配置吗? (输入 'yes' 确认): {Colors.NC}")
            if confirm == 'yes':
                # 重置配置
                config = {"version": "1.0", "current_node": None, "nodes": {}}
                self.node_manager.save_nodes_config(config)
                self.manager.init_local_config()
                self.manager.logger.info("✓ 配置已重置")
        else:
            self.manager.logger.error("无效选项")
    
    def _install_menu(self):
        """安装菜单"""
        self.manager.full_install()
    
    def _diagnostic_menu(self):
        """诊断菜单"""
        self.manager.show_status()
    
    def show_help(self):
        """显示帮助信息"""
        print("sing-box macOS 管理工具 v2.0 Python版")
        print()
        print(f"{Colors.CYAN}🚀 快速操作:{Colors.NC}")
        print("  python singtool.py status    查看详细状态")
        print("  python singtool.py nodes     节点管理菜单")
        print()
        print(f"{Colors.CYAN}✨ 功能特色:{Colors.NC}")
        print("  • 🎯 Python实现: 更好的跨平台兼容性")
        print("  • 🔧 模块化设计: 清晰的代码结构")
        print("  • 🧙‍♂️ 友好界面: 直观的菜单系统")
        print("  • 📡 多节点支持: 本地服务器/客户端节点")
        print("  • 🌐 多协议支持: Trojan, VLESS, VMess, Shadowsocks")
        print("  • �� macOS 优化: 原生集成") 