#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单系统模块 - 交互式用户界面 (2级菜单结构)
SingTool Menu Module - 2-Level Menu System
"""

import os
import sys
import time
import json
from utils import Colors, Logger
from advanced_config import AdvancedConfigManager
from rich_menu import RichMenu

class MenuSystem:
    """菜单系统类 - 提供2级交互式用户界面"""
    
    def __init__(self, manager, node_manager):
        self.manager = manager
        self.node_manager = node_manager
        self.rich_menu = RichMenu()
    
    def show_main_menu(self):
        """显示主菜单 - 第1级"""
        while True:
            # 清屏并显示banner
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            
            # 显示当前状态概览
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            # 主菜单项
            main_items = [
                ("1", "🚀 快速操作", "一键测试、修复、配置向导"),
                ("2", "📡 节点管理", "添加、删除、切换、测速节点"),
                ("3", "🔀 分流管理", "路由规则、自定义规则配置"),
                ("4", "⚙️ 系统管理", "服务控制、配置、日志查看"),
                ("5", "🔧 高级配置", "端口、DNS、TUN、API设置"),
                ("6", "🛠️ 系统工具", "安装、卸载、诊断、帮助")
            ]
            
            self.rich_menu.show_menu("🎯 主菜单 - 请选择功能分类", main_items)
            
            choice = self.rich_menu.prompt_choice("请选择功能分类 [0-6]")
            
            if choice == "0":
                self.manager.logger.info("感谢使用！")
                sys.exit(0)
            elif choice == "1":
                self._show_quick_menu()
            elif choice == "2":
                self._show_node_menu()
            elif choice == "3":
                self._show_routing_menu()
            elif choice == "4":
                self._show_system_menu()
            elif choice == "5":
                self._show_advanced_menu()
            elif choice == "6":
                self._show_tools_menu()
            else:
                self.rich_menu.print_error("无效选项，请重新选择")
                time.sleep(1)
    
    def _show_quick_menu(self):
        """显示快速操作菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            quick_items = [
                ("1", "🧪 快速测试连接", "检查服务状态和连通性"),
                ("2", "🔧 一键修复问题", "自动检测并修复常见问题"),
                ("3", "🧙‍♂️ 配置向导", "新手引导完整配置流程"),
                ("4", "📊 详细状态信息", "查看完整的系统运行状态")
            ]
            
            self.rich_menu.show_menu("🚀 快速操作菜单", quick_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-4]")
            
            if choice == "0":
                return
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
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)
    
    def _show_node_menu(self):
        """显示节点管理菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            node_items = [
                ("1", "📋 显示节点列表", "查看所有已配置的节点"),
                ("2", "➕ 添加远程节点", "添加Trojan/VLESS/SS节点"),
                ("3", "🏠 创建本地节点", "创建本地服务器/客户端节点"),
                ("4", "🔄 切换节点", "切换到其他节点"),
                ("5", "🗑️ 删除节点", "删除不需要的节点"),
                ("6", "🚀 节点测速", "测试节点连接速度和延迟")
            ]
            
            self.rich_menu.show_menu("📡 节点管理菜单", node_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-6]")
            
            if choice == "0":
                return
            elif choice == "1":
                self.node_manager.show_nodes()
                input("按回车键继续...")
            elif choice == "2":
                self._add_remote_node_menu()
                input("按回车键继续...")
            elif choice == "3":
                self._add_local_node_menu()
                input("按回车键继续...")
            elif choice == "4":
                self._switch_node_menu()
                input("按回车键继续...")
            elif choice == "5":
                self._delete_node_menu()
                input("按回车键继续...")
            elif choice == "6":
                self._node_speed_test_menu()
                input("按回车键继续...")
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)
    
    def _show_routing_menu(self):
        """显示分流管理菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            routing_items = [
                ("1", "📋 查看分流规则", "查看当前所有路由规则"),
                ("2", "🎬 媒体分流管理", "流媒体、音乐、社交媒体规则"),
                ("3", "💻 程序分流管理", "开发工具、办公软件、游戏平台"),
                ("4", "➕ 添加自定义规则", "添加新的路由规则"),
                ("5", "🔧 编辑规则组", "修改现有规则组"),
                ("6", "⚙️ 分流设置", "配置默认出站和启用规则"),
                ("7", "🎯 完整分流管理", "进入完整的分流配置界面")
            ]
            
            self.rich_menu.show_menu("🔀 分流管理菜单", routing_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-7]")
            
            if choice == "0":
                return
            elif choice == "1":
                self._view_split_rules_menu()
                input("按回车键继续...")
            elif choice == "2":
                self._media_routing_management()
                input("按回车键继续...")
            elif choice == "3":
                self._application_routing_management()
                input("按回车键继续...")
            elif choice == "4":
                self._add_custom_rule_menu()
                input("按回车键继续...")
            elif choice == "5":
                self._edit_rule_group_menu()
                input("按回车键继续...")
            elif choice == "6":
                self._split_settings_menu()
                input("按回车键继续...")
            elif choice == "7":
                self._full_routing_management()
                input("按回车键继续...")
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)
    
    def _show_system_menu(self):
        """显示系统管理菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            system_items = [
                ("1", "▶️ 启动服务", "启动 sing-box 服务"),
                ("2", "🔄 重启服务", "重启 sing-box 服务"),
                ("3", "⏹️ 停止服务", "停止 sing-box 服务"),
                ("4", "📝 查看日志", "查看服务运行日志"),
                ("5", "📊 服务状态", "查看详细的服务状态"),
                ("6", "🔄 重新生成配置", "重新生成主配置文件")
            ]
            
            self.rich_menu.show_menu("⚙️ 系统管理菜单", system_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-6]")
            
            if choice == "0":
                return
            elif choice == "1":
                self.manager.start_service()
                input("按回车键继续...")
            elif choice == "2":
                self.manager.restart_service()
                input("按回车键继续...")
            elif choice == "3":
                self.manager.stop_service()
                input("按回车键继续...")
            elif choice == "4":
                self.manager.view_logs()
                input("按回车键继续...")
            elif choice == "5":
                self.manager.show_status()
                input("按回车键继续...")
            elif choice == "6":
                self.manager.create_main_config()
                self.manager.logger.info("✓ 配置文件已重新生成")
                input("按回车键继续...")
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)
    
    def _show_advanced_menu(self):
        """显示高级配置菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            advanced_items = [
                ("1", "🌐 代理端口配置", "混合/HTTP/SOCKS端口设置"),
                ("2", "🏠 DNS 和 FakeIP", "DNS服务器和FakeIP配置"),
                ("3", "🔌 TUN 模式配置", "TUN接口和网络路由配置"),
                ("4", "📡 Clash API设置", "API控制器和认证配置"),
                ("5", "👀 查看当前配置", "显示完整的配置文件"),
                ("6", "💾 配置管理", "备份、恢复、重置配置")
            ]
            
            self.rich_menu.show_menu("🔧 高级配置菜单", advanced_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-6]")
            
            if choice == "0":
                return
            elif choice == "1":
                self._proxy_ports_config()
                input("按回车键继续...")
            elif choice == "2":
                self._dns_fakeip_config()
                input("按回车键继续...")
            elif choice == "3":
                self._tun_mode_config()
                input("按回车键继续...")
            elif choice == "4":
                self._clash_api_config()
                input("按回车键继续...")
            elif choice == "5":
                self._view_current_config()
                input("按回车键继续...")
            elif choice == "6":
                self._config_management_menu()
                input("按回车键继续...")
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)
    
    def _show_tools_menu(self):
        """显示系统工具菜单 - 第2级"""
        while True:
            self.rich_menu.clear()
            self.rich_menu.show_banner()
            status_data = self._get_status_data()
            self.rich_menu.show_status(status_data)
            
            tools_items = [
                ("1", "📦 完整安装", "安装sing-box和所有依赖"),
                ("2", "🔍 系统诊断", "检查系统状态和配置问题"),
                ("3", "❓ 帮助信息", "显示使用帮助和说明"),
                ("4", "🗑️ 卸载程序", "完全卸载sing-box"),
                ("5", "📋 版本信息", "显示程序和组件版本")
            ]
            
            self.rich_menu.show_menu("🛠️ 系统工具菜单", tools_items, exit_text="0. 🔙 返回主菜单")
            
            choice = self.rich_menu.prompt_choice("请选择操作 [0-5]")
            
            if choice == "0":
                return
            elif choice == "1":
                self._install_menu()
                input("按回车键继续...")
            elif choice == "2":
                self._diagnostic_menu()
                input("按回车键继续...")
            elif choice == "3":
                self.show_help()
                input("按回车键继续...")
            elif choice == "4":
                if self.manager.uninstall():
                    sys.exit(0)
                input("按回车键继续...")
            elif choice == "5":
                self._show_version_info()
                input("按回车键继续...")
            else:
                self.rich_menu.print_error("无效选项")
                time.sleep(1)

    def _config_management_menu(self):
        """配置管理子菜单"""
        print()
        print(f"{Colors.CYAN}💾 配置管理{Colors.NC}")
        print("1. 💾 备份当前配置")
        print("2. 🔄 重置所有配置")
        print("3. 📂 查看备份列表")
        print("0. 🔙 返回")
        print()
        
        choice = input("请选择 [0-3]: ").strip()
        
        if choice == "1":
            self._backup_config()
        elif choice == "2":
            self._reset_config()
        elif choice == "3":
            self._list_backups()
        elif choice == "0":
            return
        else:
            self.manager.logger.error("无效选项")
    
    def _list_backups(self):
        """列出备份文件"""
        backup_dir = self.manager.paths.backup_dir
        if backup_dir.exists():
            backups = list(backup_dir.glob("config_backup_*.json"))
            if backups:
                print(f"\n找到 {len(backups)} 个备份文件:")
                for backup in sorted(backups):
                    print(f"  📄 {backup.name}")
            else:
                print("没有找到备份文件")
        else:
            print("备份目录不存在")

    def _show_version_info(self):
        """显示版本信息"""
        print()
        print(f"{Colors.CYAN}📋 版本信息{Colors.NC}")
        print("┌─────────────────────────────────────────────────────┐")
        print(f"│ SingTool 版本: {Colors.GREEN}v2.0{Colors.NC}                            │")
        print(f"│ 开发语言: {Colors.BLUE}Python 3{Colors.NC}                        │")
        print(f"│ 支持平台: {Colors.YELLOW}macOS{Colors.NC}                            │")
        
        # 检查sing-box版本
        try:
            import subprocess
            result = subprocess.run(["/opt/homebrew/bin/sing-box", "version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.strip().split('\n')[0]
                print(f"│ Sing-box: {Colors.GREEN}{version_line}{Colors.NC}                     │")
            else:
                print(f"│ Sing-box: {Colors.RED}未安装或无法检测{Colors.NC}                │")
        except:
            print(f"│ Sing-box: {Colors.RED}未安装或无法检测{Colors.NC}                │")
        
        print("└─────────────────────────────────────────────────────┘")

    def _full_routing_management(self):
        """完整分流管理"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_routing_rules()

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
                    port_info = ','.join(active_ports)
                    if inactive_ports:
                        port_info += f" ({','.join(inactive_ports)} 未活动)"
                    return port_info
                elif inactive_ports:
                    return f"{','.join(inactive_ports)} (未活动)"
                else:
                    return "未配置"
            else:
                return "未配置"
        except Exception:
            return "获取失败"
    
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
        self.rich_menu.clear()
        self.rich_menu.show_banner()
        
        # 获取节点名称，提供默认值
        import datetime
        default_name = f"节点_{datetime.datetime.now().strftime('%m%d_%H%M')}"
        
        while True:
            node_name = self.rich_menu.prompt_input(f"请输入节点名称 (输入 'q' 退出)", default=default_name)
            if not node_name:  # 处理None或空字符串
                self.rich_menu.print_warning("节点名称不能为空，请重新输入")
                continue
            if node_name.lower() in ['q', 'quit', 'exit']:
                self.rich_menu.print_info("取消添加节点")
                return
            if node_name:
                break
            self.rich_menu.print_warning("节点名称不能为空，请重新输入")
        
        # 获取节点ID
        import re
        default_id = re.sub(r'[^a-zA-Z0-9_]', '_', node_name.lower())
        node_id = self.rich_menu.prompt_input("节点ID (用于标识)", default=default_id)
        if not node_id:  # 处理None情况
            node_id = default_id
        
        # 检查节点ID是否已存在
        config = self.node_manager.load_nodes_config()
        if node_id in config.get('nodes', {}):
            self.rich_menu.print_error(f"节点ID '{node_id}' 已存在，请使用其他ID")
            return
        
        # 显示协议选择菜单
        self.rich_menu.clear()
        self.rich_menu.show_banner()
        self.rich_menu.print_info(f"正在为节点 '{node_name}' 选择协议类型")
        
        # 协议类型和推荐标签
        protocols = [
            ("1", "🔐 Trojan", "🏆 推荐", "安全可靠，伪装度高，兼容性好"),
            ("2", "⚡ VLESS", "🚀 高效", "新一代协议，性能优秀，功能丰富"),
            ("3", "🌐 VMess", "🛡️ 经典", "V2Ray原生协议，功能全面，广泛支持"),
            ("4", "👤 Shadowsocks", "💡 简单", "轻量级协议，易于配置，性能稳定"),
            ("5", "🚄 Hysteria2", "⚡ 极速", "基于QUIC，低延迟，适合游戏和流媒体"),
            ("6", "🔒 TUIC", "🔥 新兴", "QUIC协议，抗封锁能力强"),
            ("7", "🌟 Reality", "🎭 伪装", "终极伪装技术，几乎无法检测"),
            ("8", "🔗 ShadowTLS", "🛡️ 加强", "TLS伪装的Shadowsocks"),
            ("9", "🌐 WireGuard", "🔧 VPN", "现代VPN协议，简单高效"),
            ("10", "🔄 Hysteria", "📈 传统", "第一代Hysteria协议")
        ]
        
        # 创建协议选择表格
        headers = ["选项", "协议", "标签", "特点说明"]
        rows = []
        
        for num, protocol, tag, desc in protocols:
            rows.append([num, protocol, tag, desc])
        
        self.rich_menu.show_table("🚀 选择协议类型", headers, rows, styles={
            "协议": "cyan",
            "标签": "green",
            "特点说明": "white"
        })
        
        print()
        self.rich_menu.print_info("💡 推荐说明:")
        self.rich_menu.print_info("   🏆 Trojan: 最佳平衡，适合新手")
        self.rich_menu.print_info("   🚀 VLESS: 高性能，适合进阶用户") 
        self.rich_menu.print_info("   ⚡ Hysteria2: 极速体验，适合游戏")
        self.rich_menu.print_info("   🎭 Reality: 最强伪装，适合特殊环境")
        print()
        
        choice = self.rich_menu.prompt_choice("请选择协议类型 [1-10]")
        success = False
        
        try:
            choice_num = int(choice)
            if choice_num == 1:
                success = self.node_manager.add_trojan_node(node_id, node_name)
            elif choice_num == 2:
                success = self.node_manager.add_vless_node(node_id, node_name)
            elif choice_num == 3:
                success = self.node_manager.add_vmess_node(node_id, node_name)
            elif choice_num == 4:
                success = self.node_manager.add_shadowsocks_node(node_id, node_name)
            elif choice_num == 5:
                success = self.node_manager.add_hysteria2_node(node_id, node_name)
            elif choice_num == 6:
                success = self.node_manager.add_tuic_node(node_id, node_name)
            elif choice_num == 7:
                success = self.node_manager.add_reality_node(node_id, node_name)
            elif choice_num == 8:
                success = self.node_manager.add_shadowtls_node(node_id, node_name)
            elif choice_num == 9:
                success = self.node_manager.add_wireguard_node(node_id, node_name)
            elif choice_num == 10:
                success = self.node_manager.add_hysteria_node(node_id, node_name)
            else:
                self.rich_menu.print_error("无效选项")
                return
        except ValueError:
            self.rich_menu.print_error("请输入有效的数字")
            return
        
        if success:
            print()
            self.rich_menu.print_success(f"节点 '{node_name}' 添加成功！")
            
            # 询问是否切换到新节点
            switch = self.rich_menu.prompt_confirm("是否切换到新添加的节点?", default=True)
            if switch:
                config = self.node_manager.load_nodes_config()
                config['current_node'] = node_id
                self.node_manager.save_nodes_config(config)
                self.rich_menu.print_success(f"已切换到节点: {node_id}")
                
                # 重新生成配置并重启服务
                self.rich_menu.print_info("正在重新生成配置...")
                self.manager.create_main_config()
                self.manager.restart_service()
                self.rich_menu.print_success("服务已重启，新节点已生效")
        else:
            self.rich_menu.print_error("节点添加失败")
    
    def _add_local_node_menu(self):
        """添加本地节点菜单"""
        print()
        print(f"{Colors.CYAN}🏠 创建本地节点{Colors.NC}")
        print("  1) 本地服务器 - 创建代理服务供其他设备使用")
        print("  2) 本地客户端 - 连接本机其他端口的服务")
        print()
        
        choice = input("请选择 [1-2]: ").strip()
        
        # 获取节点名称
        import datetime
        default_name = f"本地节点_{datetime.datetime.now().strftime('%m%d_%H%M')}"
        
        while True:
            node_name = input(f"节点名称 [{default_name}]: ").strip()
            if not node_name:
                node_name = default_name
            if node_name.lower() in ['q', 'quit', 'exit']:
                self.manager.logger.info("取消添加节点")
                return
            if node_name:
                break
            print(f"{Colors.YELLOW}提示: 节点名称不能为空，请重新输入{Colors.NC}")
        
        # 获取节点ID
        import re
        default_id = re.sub(r'[^a-zA-Z0-9_]', '_', node_name.lower())
        node_id = input(f"节点ID (用于标识) [{default_id}]: ").strip()
        if not node_id:
            node_id = default_id
        
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
        """启动/重启服务 - 已合并到系统管理菜单"""
        is_running, _ = self.manager.check_service_status()
        if is_running:
            self.manager.restart_service()
        else:
            self.manager.start_service()
    
    def _advanced_config_menu(self):
        """高级配置菜单 - 已重构为_show_advanced_menu"""
        print()
        print(f"{Colors.CYAN}🔄 高级配置{Colors.NC}")
        print("该功能已移动到主菜单的高级配置分类中")
        print("请返回主菜单选择 '5. 🔧 高级配置'")
    
    def _proxy_ports_config(self):
        """代理端口配置"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_proxy_ports()
    
    def _dns_fakeip_config(self):
        """DNS 和 FakeIP 设置"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_dns_fakeip()
    
    def _tun_mode_config(self):
        """TUN 模式配置"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_tun_mode()
    
    def _clash_api_config(self):
        """Clash API 设置"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_clash_api()
    
    def _view_current_config(self):
        """查看当前配置"""
        if self.manager.paths.main_config.exists():
            with open(self.manager.paths.main_config, 'r') as f:
                print(f.read())
        else:
            self.manager.logger.error("配置文件不存在")
    
    def _backup_config(self):
        """备份配置"""
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
    
    def _reset_config(self):
        """重置配置"""
        confirm = input(f"{Colors.RED}确定要重置所有配置吗? (输入 'yes' 确认): {Colors.NC}")
        if confirm == 'yes':
            # 重置配置
            config = {"version": "1.0", "current_node": None, "nodes": {}}
            self.node_manager.save_nodes_config(config)
            self.manager.init_local_config()
            self.manager.logger.info("✓ 配置已重置")
    
    def _install_menu(self):
        """安装菜单"""
        self.manager.full_install()
    
    def _diagnostic_menu(self):
        """诊断菜单"""
        self.manager.show_status()
    
    def _node_speed_test_menu(self):
        """节点测速菜单"""
        print()
        print(f"{Colors.CYAN}🚀 节点测速{Colors.NC}")
        print("选择测速方式:")
        print("  1. 测试所有节点")
        print("  2. 测试指定节点")
        print("  3. 返回主菜单")
        print()
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            self.node_manager.speed_test_all_nodes()
        elif choice == "2":
            self.node_manager.speed_test_specific_node()
        elif choice == "3":
            return
        else:
            self.manager.logger.error("无效选项")
    
    def _view_split_rules_menu(self):
        """查看分流规则菜单"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        routing_config = advanced_manager.load_advanced_config().get("routing", {})
        advanced_manager._view_all_rule_sets(routing_config)
    
    def _add_custom_rule_menu(self):
        """添加自定义规则菜单"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        config = advanced_manager.load_advanced_config()
        routing_config = config.get("routing", {})
        advanced_manager._add_custom_rule(routing_config)
        config['routing'] = routing_config
        advanced_manager.save_advanced_config(config)
        self.manager.logger.info("✓ 自定义规则已保存")
        
        # 询问是否重新生成配置
        regenerate = input(f"{Colors.YELLOW}是否重新生成配置文件以应用新规则? (Y/n): {Colors.NC}").strip().lower()
        if not regenerate or regenerate.startswith('y'):
            self.manager.create_main_config()
            self.manager.restart_service()
    
    def _edit_rule_group_menu(self):
        """编辑规则组菜单"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        config = advanced_manager.load_advanced_config()
        routing_config = config.get("routing", {})
        advanced_manager._edit_rule_set(routing_config)
        config['routing'] = routing_config
        advanced_manager.save_advanced_config(config)
        
        # 询问是否重新生成配置
        regenerate = input(f"{Colors.YELLOW}是否重新生成配置文件以应用更改? (Y/n): {Colors.NC}").strip().lower()
        if not regenerate or regenerate.startswith('y'):
            self.manager.create_main_config()
            self.manager.restart_service()
    
    def _split_settings_menu(self):
        """分流设置菜单"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        config = advanced_manager.load_advanced_config()
        routing_config = config.get("routing", {})
        
        print()
        print(f"{Colors.CYAN}⚙️  分流设置{Colors.NC}")
        print()
        
        current_final = routing_config.get("final_outbound", "proxy")
        enabled_rules = routing_config.get("enabled_rules", [])
        
        print(f"当前配置:")
        print(f"  默认出站: {current_final}")
        print(f"  启用的规则组: {len(enabled_rules)} 个")
        print()
        
        print("1. 🎯 设置默认出站")
        print("2. ✅ 管理规则组启用状态")
        print("3. 🔀 完整分流管理")
        print("4. 💾 保存并返回")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            print()
            print("默认出站选项:")
            print("1. proxy - 走代理 (未匹配规则的流量)")
            print("2. direct - 直连")
            print("3. block - 拦截")
            
            outbound_choice = input("请选择 [1-3]: ").strip()
            outbound_map = {"1": "proxy", "2": "direct", "3": "block"}
            new_outbound = outbound_map.get(outbound_choice)
            
            if new_outbound:
                routing_config["final_outbound"] = new_outbound
                self.manager.logger.info(f"✓ 默认出站设置为: {new_outbound}")
            else:
                self.manager.logger.error("无效选择")
                
        elif choice == "2":
            advanced_manager._manage_enabled_rules(routing_config)
            
        elif choice == "3":
            # 进入完整的分流管理界面
            advanced_manager.configure_routing_rules()
            return  # 直接返回，不需要保存，因为完整界面会处理保存
            
        elif choice == "4":
            config['routing'] = routing_config
            advanced_manager.save_advanced_config(config)
            self.manager.logger.info("✓ 分流设置已保存")
            
            # 询问是否重新生成配置
            regenerate = input(f"{Colors.YELLOW}是否重新生成配置文件以应用更改? (Y/n): {Colors.NC}").strip().lower()
            if not regenerate or regenerate.startswith('y'):
                self.manager.create_main_config()
                self.manager.restart_service()
            return
        else:
            self.manager.logger.error("无效选项")
    
    def _media_routing_management(self):
        """媒体分流管理"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_media_routing_rules()
    
    def _application_routing_management(self):
        """程序分流管理"""
        advanced_manager = AdvancedConfigManager(self.manager.paths, self.manager.logger)
        advanced_manager.configure_application_routing_rules()
    
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
        print("  • 🌐 多协议支持: Trojan, VLESS, VMess, Shadowsocks, Hysteria2, TUIC, Reality, ShadowTLS, WireGuard, Hysteria")
        print("  • macOS 优化: 原生集成")

    def _get_status_data(self):
        """获取状态数据"""
        # 获取服务状态
        service_status = self.manager.check_service_status()
        if service_status:
            status_text = "[green]运行中[/green]"
        else:
            status_text = "[red]已停止[/red]"
        
        # 获取端口信息
        port_info = self._get_proxy_port_info()
        
        # 获取当前节点
        config = self.node_manager.load_nodes_config()
        current_node = config.get('current_node')
        if current_node and current_node in config.get('nodes', {}):
            node_info = config['nodes'][current_node]
            node_name = node_info.get('name', current_node)
            node_type = node_info.get('type', 'unknown')
            node_info_text = f"[blue]{node_name} ({node_type})[/blue]"
        else:
            node_info_text = "[yellow]未配置[/yellow]"
        
        return {
            "服务状态": status_text,
            "代理端口": f"[green]{port_info}[/green]" if port_info and "未配置" not in str(port_info) else "[yellow]未配置[/yellow]",
            "当前节点": node_info_text
        } 