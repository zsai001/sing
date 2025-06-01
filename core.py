#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SingTool核心管理器 - 统一管理所有功能模块
Core Manager for SingTool
"""

import os
import sys
import platform
import subprocess
import time
import socket
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from threading import Thread, Event
from pathlib import Path
from utils import Colors, Logger
from paths import PathManager
from config_manager import ConfigManager
from nodes import NodeManager
from menu import MenuSystem
from service import ServiceManager

class SingToolManager:
    """SingTool核心管理器"""
    
    def __init__(self):
        # 初始化路径管理器
        self.paths = PathManager()
        
        # 日志记录器（静态类）
        self.logger = Logger
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self.paths, self.logger)
        
        # 初始化节点管理器
        self.node_manager = NodeManager(self.paths, self.logger)
        
        # 初始化菜单系统
        self.menu = MenuSystem(self, self.node_manager)
        
        # sing-box进程相关
        self.sing_box_process = None
        self.monitor_thread = None
        self.stop_monitoring = Event()
        
        # 状态标志
        self.is_running = False
        
        # 确保配置目录存在
        self.config_manager.ensure_config_directories()
        
        self.service_manager = ServiceManager(self.paths, self.logger)
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        self.config_manager.ensure_config_directories()
    
    def show_banner(self):
        """显示横幅"""
        print(f"""
{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        sing-box macOS 管理工具 v2.0                          ║
║                              Python 模块化版本                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.NC}""")
    
    def detect_os(self):
        """检测操作系统"""
        return self.service_manager.detect_os()
    
    def check_homebrew(self):
        """检查 Homebrew 安装状态"""
        return self.service_manager.check_homebrew()
    
    def install_homebrew(self):
        """安装 Homebrew"""
        return self.service_manager.install_homebrew()
    
    def check_singbox_installed(self):
        """检查 sing-box 是否已安装"""
        return self.service_manager.check_singbox_installed()
    
    def install_singbox(self):
        """安装 sing-box"""
        return self.service_manager.install_singbox()
    
    def create_service(self):
        """创建系统服务"""
        return self.service_manager.create_service()
    
    def check_service_status(self) -> tuple:
        """检查服务状态"""
        return self.service_manager.check_service_status()
    
    def start_service(self):
        """启动服务"""
        return self.service_manager.start_service()
    
    def stop_service(self):
        """停止服务"""
        return self.service_manager.stop_service()
    
    def restart_service(self):
        """重启服务"""
        return self.service_manager.restart_service()
    
    def view_logs(self):
        """查看日志"""
        self.service_manager.view_logs()
    
    def uninstall(self):
        """卸载 sing-box"""
        return self.service_manager.uninstall()
    
    def show_status(self):
        """显示详细状态信息"""
        self.logger.step("获取系统状态...")
        print()
        
        # 基本信息
        self._show_system_info()
        
        # 服务状态
        print(f"{Colors.CYAN}📋 服务状态{Colors.NC}")
        print("----------------------------------------")
        
        is_running, status_text = self.check_service_status()
        print(f"sing-box 服务: {status_text}")
        
        # 获取实际PID
        if is_running:
            pid = self._get_service_pid()
            if pid:
                print(f"PID: {Colors.GREEN}{pid}{Colors.NC}")
            else:
                print(f"PID: {Colors.YELLOW}无法获取{Colors.NC}")
        else:
            print(f"PID: {Colors.YELLOW}未运行{Colors.NC}")
        
        # 当前节点信息
        self._show_current_node_info()
        
        # 端口状态
        print()
        self._check_port_status()
        
        # 配置文件状态
        print()
        print(f"{Colors.CYAN}📄 配置文件{Colors.NC}")
        print("----------------------------------------")
        
        config_files = [
            ("主配置", self.paths.main_config),
            ("节点配置", self.paths.nodes_config),
            ("本地配置", self.paths.local_config),
            ("DNS配置", self.paths.dns_config)
        ]
        
        for name, path in config_files:
            if path.exists():
                size = path.stat().st_size
                print(f"{name}: {Colors.GREEN}存在{Colors.NC} ({size} bytes)")
            else:
                print(f"{name}: {Colors.RED}缺失{Colors.NC}")
        
        # 日志文件
        print()
        print(f"{Colors.CYAN}📝 日志文件{Colors.NC}")
        print("----------------------------------------")
        
        log_file = self.paths.log_dir / "sing-box.log"
        if log_file.exists():
            size = log_file.stat().st_size / 1024  # KB
            print(f"主日志: {Colors.GREEN}存在{Colors.NC} ({size:.1f} KB)")
        else:
            print(f"主日志: {Colors.YELLOW}不存在{Colors.NC}")
        
        error_log = self.paths.log_dir / "sing-box.error.log"
        if error_log.exists():
            size = error_log.stat().st_size / 1024  # KB
            print(f"错误日志: {Colors.GREEN}存在{Colors.NC} ({size:.1f} KB)")
        else:
            print(f"错误日志: {Colors.YELLOW}不存在{Colors.NC}")
    
    def _get_service_pid(self):
        """获取服务进程ID"""
        try:
            if self.paths.os_type == "Darwin":
                # 方法1：通过launchctl list检查服务状态
                result = subprocess.run(["launchctl", "list", self.paths.service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    # launchctl list输出格式：PID Status Label
                    for line in lines:
                        if self.paths.service_name in line:
                            parts = line.strip().split()
                            if len(parts) >= 3:
                                pid = parts[0]
                                if pid.isdigit():
                                    return pid
                                elif pid == "-":
                                    # 服务已加载但未运行
                                    return None
                
                # 方法2：直接查找进程
                result = subprocess.run(["pgrep", "-f", "sing-box"], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
                
                # 方法3：通过ps查找
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'sing-box' in line and 'grep' not in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                return parts[1]  # PID是第二列
            else:
                # Linux系统
                result = subprocess.run(["systemctl", "show", self.paths.service_name, 
                                       "--property=MainPID", "--value"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    pid = result.stdout.strip()
                    if pid and pid != "0":
                        return pid
        except Exception as e:
            pass
        return None
    
    def _show_current_node_info(self):
        """显示当前节点信息"""
        print()
        print(f"{Colors.CYAN}📡 当前节点{Colors.NC}")
        print("----------------------------------------")
        
        try:
            config = self.node_manager.load_nodes_config()
            current_node = config.get('current_node')
            nodes = config.get('nodes', {})
            
            if current_node and current_node in nodes:
                node_info = nodes[current_node]
                node_name = node_info.get('name', current_node)
                node_type = node_info.get('type', 'unknown')
                protocol = node_info.get('protocol', '')
                
                print(f"节点ID: {Colors.GREEN}{current_node}{Colors.NC}")
                print(f"节点名称: {Colors.GREEN}{node_name}{Colors.NC}")
                print(f"节点类型: {Colors.GREEN}{node_type}{Colors.NC}")
                if protocol:
                    print(f"协议: {Colors.GREEN}{protocol.upper()}{Colors.NC}")
                
                # 显示连接信息
                if node_type in ['trojan', 'vless', 'shadowsocks']:
                    config_data = node_info.get('config', {})
                    if 'server' in config_data and 'port' in config_data:
                        print(f"服务器: {Colors.GREEN}{config_data['server']}:{config_data['port']}{Colors.NC}")
                elif node_type == 'local_server':
                    config_data = node_info.get('config', {})
                    if 'listen_port' in config_data:
                        print(f"监听端口: {Colors.GREEN}{config_data['listen_port']}{Colors.NC}")
            else:
                print(f"当前节点: {Colors.YELLOW}未设置{Colors.NC}")
        except Exception as e:
            print(f"当前节点: {Colors.RED}信息获取失败{Colors.NC}")
    
    def _check_port_status(self):
        """检查端口状态"""
        print(f"{Colors.CYAN}🌐 网络端口{Colors.NC}")
        print("----------------------------------------")
        
        # 检查配置文件中的端口
        config_ports = []
        try:
            if self.paths.main_config.exists():
                with open(self.paths.main_config, 'r', encoding='utf-8') as f:
                    import json
                    config = json.load(f)
                    
                # 提取入站端口
                for inbound in config.get('inbounds', []):
                    port = inbound.get('listen_port')
                    if port:
                        config_ports.append(port)
        except:
            pass
        
        # 检查配置的端口
        if config_ports:
            print("配置的端口:")
            for port in config_ports:
                if self.service_manager.is_port_listening(port):
                    print(f"  端口 {port}: {Colors.GREEN}监听中{Colors.NC}")
                else:
                    print(f"  端口 {port}: {Colors.RED}未监听{Colors.NC}")
        
        # 检查常用代理端口
        common_ports = [7890, 7891, 1080, 8080, 9090]
        listening_ports = []
        
        for port in common_ports:
            if port not in config_ports and self.service_manager.is_port_listening(port):
                listening_ports.append(port)
        
        if listening_ports:
            print("其他监听端口:")
            for port in listening_ports:
                print(f"  端口 {port}: {Colors.GREEN}监听中{Colors.NC}")
        
        if not config_ports and not listening_ports:
            print("未检测到活动的代理端口")
    
    def _show_system_info(self):
        """显示系统信息"""
        print(f"{Colors.CYAN}💻 系统信息{Colors.NC}")
        print("----------------------------------------")
        
        # 操作系统信息
        system = platform.system()
        if system == "Darwin":
            version = platform.mac_ver()[0]
            print(f"系统: {Colors.GREEN}macOS {version}{Colors.NC}")
        else:
            version = platform.release()
            print(f"系统: {Colors.GREEN}{system} {version}{Colors.NC}")
        
        # 架构信息
        arch = platform.machine()
        print(f"架构: {Colors.GREEN}{arch}{Colors.NC}")
        
        # Python版本
        python_version = platform.python_version()
        print(f"Python: {Colors.GREEN}{python_version}{Colors.NC}")
        
        # sing-box版本
        if self.check_singbox_installed():
            try:
                result = subprocess.run([self.paths.sing_box_bin, "version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version_line = result.stdout.strip().split('\n')[0]
                    print(f"sing-box: {Colors.GREEN}{version_line}{Colors.NC}")
                else:
                    print(f"sing-box: {Colors.YELLOW}版本获取失败{Colors.NC}")
            except:
                print(f"sing-box: {Colors.RED}无法获取版本{Colors.NC}")
        else:
            print(f"sing-box: {Colors.RED}未安装{Colors.NC}")
        
        # 网络接口
        try:
            local_ip = self.config_manager.get_local_ip()
            print(f"本机IP: {Colors.GREEN}{local_ip}{Colors.NC}")
        except:
            print(f"本机IP: {Colors.YELLOW}获取失败{Colors.NC}")
        
        print()
    
    def create_main_config(self):
        """创建主配置文件"""
        self.logger.step("生成主配置文件...")
        
        config = self.node_manager.load_nodes_config()
        current_node = config.get('current_node')
        nodes = config.get('nodes', {})
        
        if not current_node or current_node not in nodes:
            # 没有当前节点时生成基本配置
            self.logger.info("当前无活动节点，生成基本配置")
            basic_config = self._generate_basic_config()
            return self.config_manager.save_config(basic_config)
        
        # 有当前节点时生成相应配置
        node_info = nodes[current_node]
        node_type = node_info.get('type', 'unknown')
        
        if node_type in ['trojan', 'vless', 'shadowsocks']:
            # 远程节点 - 生成客户端配置
            node_config = node_info['config'].copy()
            node_config['name'] = node_info['name']
            node_config['type'] = node_type
            
            # 确保包含TLS设置（如果原配置中有的话）
            if 'tls' in node_info['config']:
                # 从节点配置的TLS设置中获取skip_cert_verify，保持原始配置值
                node_config['skip_cert_verify'] = node_info['config']['tls'].get('insecure', False)
                node_config['sni'] = node_info['config']['tls'].get('server_name', node_config.get('server', ''))
            
            # 传输设置已经在node_config中，不需要重复设置
            
            selected_nodes = [node_config]
            config = self.config_manager.generate_local_proxy_config(selected_nodes)
        elif node_type in ['local_server']:
            # 本地服务器 - 生成服务器配置
            server_type = node_info.get('protocol', 'trojan')
            config_data = node_info.get('config', {})
            config = self.config_manager.generate_local_server_config(server_type, config_data)
        elif node_type in ['local_client']:
            # 本地客户端 - 生成客户端配置
            config = self._generate_local_client_config(node_info)
        else:
            self.logger.warn(f"未知节点类型: {node_type}")
            config = self._generate_basic_config()
        
        if config:
            # 备份并保存配置
            self.config_manager.backup_config()
            return self.config_manager.save_config(config)
        else:
            self.logger.error("配置生成失败")
            return False
    
    def _generate_basic_config(self) -> Dict[str, Any]:
        """生成基础配置"""
        return {
            "log": {
                "level": "info",
                "timestamp": True,
                "output": str(self.paths.log_dir / "sing-box.log")
            },
            "inbounds": [
                {
                    "type": "mixed",
                    "tag": "mixed-in",
                    "listen": "127.0.0.1",
                    "listen_port": 7890
                }
            ],
            "outbounds": [
                {"type": "direct", "tag": "direct"}
            ],
            "route": {
                "rules": [],
                "final": "direct"
            }
        }
    
    def _generate_local_client_config(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成本地客户端配置"""
        config_data = node_info.get('config', {})
        protocol = node_info.get('protocol', 'trojan')
        
        # 转换为标准节点格式
        node_config = {
            'name': node_info['name'],
            'type': protocol,
            'server': config_data.get('server', '127.0.0.1'),
            'port': config_data.get('port', 5566)
        }
        
        if protocol == 'trojan':
            node_config['password'] = config_data.get('password', '')
        elif protocol == 'vless':
            node_config['uuid'] = config_data.get('uuid', '')
        elif protocol == 'shadowsocks':
            node_config['password'] = config_data.get('password', '')
            node_config['method'] = config_data.get('method', 'aes-256-gcm')
        
        return self.config_manager.generate_local_proxy_config([node_config])
    
    def init_local_config(self):
        """初始化本地代理配置"""
        self.logger.step("初始化本地代理配置...")
        
        if not self.paths.local_config.exists():
            config = {
                "version": "1.0",
                "socks_port": 0,
                "http_port": 0,
                "mixed_port": 7890,
                "tun_enabled": False,
                "enhanced_mode": False,
                "fake_ip_enabled": False,
                "dns_enabled": True,
                "auto_route": True,
                "stack": "mixed"
            }
            
            with open(self.paths.local_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("✓ 创建默认本地代理配置 (混合端口: 7890)")
        
        if not self.paths.dns_config.exists():
            dns_config = {
                "version": "1.0",
                "servers": [
                    {
                        "tag": "cloudflare",
                        "address": "https://1.1.1.1/dns-query",
                        "strategy": "prefer_ipv4"
                    },
                    {
                        "tag": "google",
                        "address": "https://8.8.8.8/dns-query",
                        "strategy": "prefer_ipv4"
                    },
                    {
                        "tag": "local",
                        "address": "223.5.5.5",
                        "detour": "direct"
                    }
                ],
                "rules": [
                    {
                        "domain_suffix": [".cn", ".中国", ".公司", ".网络"],
                        "server": "local"
                    }
                ],
                "final": "cloudflare",
                "strategy": "prefer_ipv4"
            }
            
            with open(self.paths.dns_config, 'w', encoding='utf-8') as f:
                json.dump(dns_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("✓ 创建默认DNS配置")
        
        self.logger.info("✓ 本地代理配置初始化完成")
    
    def full_install(self):
        """完整安装流程"""
        self.logger.step("开始完整安装流程...")
        
        # 1. 检测系统
        if not self.detect_os():
            return False
        
        # 2. 检查并安装依赖
        if not self.check_homebrew():
            return False
        
        # 3. 安装 sing-box
        if not self.check_singbox_installed():
            if not self.install_singbox():
                return False
        else:
            self.logger.info("✓ sing-box 已安装，跳过安装步骤")
        
        # 4. 初始化配置
        self.init_local_config()
        
        # 5. 创建配置文件
        self.create_main_config()
        
        # 6. 创建服务
        if not self.create_service():
            return False
        
        # 7. 启动服务
        if not self.start_service():
            return False
        
        print()
        self.logger.info("🎉 安装完成！")
        print()
        self._show_connection_info()
        return True
    
    def _show_connection_info(self):
        """显示连接信息"""
        try:
            with open(self.paths.local_config, 'r', encoding='utf-8') as f:
                local_config = json.load(f)
            
            print(f"{Colors.CYAN}代理配置信息:{Colors.NC}")
            
            if local_config.get('mixed_port', 0) > 0:
                port = local_config['mixed_port']
                print(f"  混合代理: {Colors.GREEN}127.0.0.1:{port}{Colors.NC}")
                print(f"    (支持HTTP和SOCKS5协议)")
            
            if local_config.get('socks_port', 0) > 0:
                port = local_config['socks_port']
                print(f"  SOCKS5代理: {Colors.GREEN}127.0.0.1:{port}{Colors.NC}")
            
            if local_config.get('http_port', 0) > 0:
                port = local_config['http_port']
                print(f"  HTTP代理: {Colors.GREEN}127.0.0.1:{port}{Colors.NC}")
            
            print()
            print(f"{Colors.YELLOW}📱 浏览器设置示例:{Colors.NC}")
            if local_config.get('mixed_port', 0) > 0:
                port = local_config['mixed_port']
                print(f"  Chrome: 设置 → 高级 → 代理设置 → HTTP代理 127.0.0.1:{port}")
                print(f"  Safari: 系统偏好设置 → 网络 → 高级 → 代理 → Web代理 127.0.0.1:{port}")
        except:
            print(f"{Colors.YELLOW}连接信息获取失败，请检查配置文件{Colors.NC}") 