#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务管理模块 - sing-box 服务控制
SingTool Service Module
"""

import os
import subprocess
import time
import platform
import socket
from utils import Colors, Logger
from paths import PathManager

class ServiceManager:
    """服务管理类 - 负责 sing-box 服务的安装、启动、停止等操作"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        self.paths = paths
        self.logger = logger
    
    def detect_os(self):
        """检测操作系统"""
        if self.paths.os_type == "Darwin":
            macos_version = platform.mac_ver()[0]
            self.logger.info(f"✓ 检测到 macOS {macos_version} ({self.paths.arch})")
            return True
        elif self.paths.os_type == "Linux":
            self.logger.info("✓ 检测到 Linux 系统")
            return True
        else:
            self.logger.error(f"不支持的操作系统: {self.paths.os_type}")
            return False
    
    def check_homebrew(self):
        """检查 Homebrew 安装状态"""
        if self.paths.os_type != "Darwin":
            return True
        
        try:
            subprocess.run(["brew", "--version"], check=True, 
                         capture_output=True, text=True)
            self.logger.info("✓ Homebrew 已安装")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warn("未检测到 Homebrew")
            response = input(f"{Colors.YELLOW}是否安装 Homebrew? (推荐) (Y/n):{Colors.NC} ")
            if not response or response.lower() in ['y', 'yes']:
                return self.install_homebrew()
            else:
                self.logger.error("Homebrew 是 macOS 上推荐的包管理器")
                return False
    
    def install_homebrew(self):
        """安装 Homebrew"""
        self.logger.step("安装 Homebrew...")
        try:
            install_cmd = [
                "/bin/bash", "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            ]
            subprocess.run(install_cmd, check=True)
            self.logger.info("✓ Homebrew 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Homebrew 安装失败: {e}")
            return False
    
    def check_singbox_installed(self):
        """检查 sing-box 是否已安装"""
        try:
            if os.path.exists(self.paths.sing_box_bin):
                return True
            subprocess.run(["sing-box", "version"], check=True, 
                         capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_singbox(self):
        """安装 sing-box"""
        self.logger.step("安装 sing-box...")
        
        if self.paths.os_type == "Darwin":
            # macOS 使用 Homebrew 安装
            if not self.check_homebrew():
                return False
            
            try:
                # 添加第三方仓库
                self.logger.info("添加 sing-box 仓库...")
                subprocess.run(["brew", "tap", "sagernet/sing-box"], check=True, capture_output=True)
                
                # 安装 sing-box
                self.logger.info("通过 Homebrew 安装 sing-box...")
                subprocess.run(["brew", "install", "sing-box"], check=True)
                
                # 验证安装
                result = subprocess.run(["sing-box", "version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.logger.info(f"✓ sing-box 安装成功: {version}")
                    return True
                else:
                    self.logger.error("sing-box 安装验证失败")
                    return False
            except subprocess.CalledProcessError as e:
                self.logger.error(f"sing-box 安装失败: {e}")
                return False
        else:
            # Linux 安装逻辑可以在这里添加
            self.logger.error("Linux 安装功能待实现")
            return False
    
    def create_service(self):
        """创建系统服务"""
        if self.paths.os_type == "Darwin":
            return self._create_macos_service()
        else:
            return self._create_linux_service()
    
    def _create_macos_service(self):
        """创建 macOS 服务"""
        self.logger.step("创建 macOS 服务...")
        
        # 确保目录存在
        self.paths.plist_path.parent.mkdir(parents=True, exist_ok=True)
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{self.paths.service_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.paths.sing_box_bin}</string>
        <string>run</string>
        <string>-c</string>
        <string>{self.paths.main_config}</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ENABLE_DEPRECATED_GEOIP</key>
        <string>true</string>
        <key>ENABLE_DEPRECATED_GEOSITE</key>
        <string>true</string>
        <key>ENABLE_DEPRECATED_TUN_ADDRESS_X</key>
        <string>true</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{self.paths.config_dir}</string>
    <key>StandardOutPath</key>
    <string>{self.paths.log_dir}/sing-box.log</string>
    <key>StandardErrorPath</key>
    <string>{self.paths.log_dir}/sing-box.error.log</string>
</dict>
</plist>"""
        
        with open(self.paths.plist_path, 'w') as f:
            f.write(plist_content)
        
        self.logger.info("✓ macOS 服务配置创建完成")
        return True
    
    def _create_linux_service(self):
        """创建 Linux 服务"""
        self.logger.info("Linux 服务创建功能待实现")
        return False
    
    def check_service_status(self) -> tuple:
        """检查服务状态 (is_running, status_text)"""
        if self.paths.os_type == "Darwin":
            try:
                # 检查服务是否已加载
                result = subprocess.run(["launchctl", "list", self.paths.service_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    output = result.stdout.strip()
                    
                    # 处理macOS launchctl的输出格式（类似JSON但使用等号）
                    if output.startswith('{'):
                        import re
                        
                        # 提取PID
                        pid_match = re.search(r'"PID"\s*=\s*(\d+);', output)
                        # 提取退出状态
                        exit_status_match = re.search(r'"LastExitStatus"\s*=\s*(\d+);', output)
                        
                        if pid_match:
                            pid = int(pid_match.group(1))
                            return True, f"{Colors.GREEN}运行中{Colors.NC}"
                        elif exit_status_match:
                            exit_status = int(exit_status_match.group(1))
                            if exit_status != 0:
                                return False, f"{Colors.RED}启动失败 (退出码: {exit_status}){Colors.NC}"
                            else:
                                return False, f"{Colors.YELLOW}已加载但未运行{Colors.NC}"
                        else:
                            return False, f"{Colors.YELLOW}已加载但未运行{Colors.NC}"
                    
                    # 处理表格格式输出（旧版本或某些情况）
                    lines = output.split('\n')
                    for line in lines:
                        if self.paths.service_name in line:
                            parts = line.strip().split()
                            if len(parts) >= 3:
                                pid = parts[0]
                                status = parts[1]
                                if pid.isdigit():
                                    return True, f"{Colors.GREEN}运行中{Colors.NC}"
                                elif pid == "-":
                                    if status == "0":
                                        return False, f"{Colors.YELLOW}已加载但未运行{Colors.NC}"
                                    else:
                                        return False, f"{Colors.RED}启动失败 (退出码: {status}){Colors.NC}"
                    return False, f"{Colors.YELLOW}未加载{Colors.NC}"
                else:
                    return False, f"{Colors.YELLOW}未加载{Colors.NC}"
            except subprocess.CalledProcessError:
                return False, f"{Colors.RED}检查失败{Colors.NC}"
        else:
            try:
                result = subprocess.run(["systemctl", "is-active", self.paths.service_name], 
                                      capture_output=True, text=True)
                if result.stdout.strip() == "active":
                    return True, f"{Colors.GREEN}运行中{Colors.NC}"
                else:
                    return False, f"{Colors.YELLOW}已停止{Colors.NC}"
            except subprocess.CalledProcessError:
                return False, f"{Colors.RED}未安装{Colors.NC}"
    
    def start_service(self):
        """启动服务"""
        self.logger.step("启动 sing-box 服务...")
        
        # 检查服务是否已经启动
        is_running, status_text = self.check_service_status()
        if is_running:
            self.logger.info("✓ sing-box 服务已经在运行中")
            print(f"服务状态: {status_text}")
            return True
        
        if not self.check_singbox_installed():
            self.logger.error("sing-box 未安装，请先运行安装")
            return False
        
        if self.paths.os_type == "Darwin":
            if not self.paths.plist_path.exists():
                self.logger.error("服务配置文件不存在，请先运行完整安装")
                return False
            
            try:
                subprocess.run(["launchctl", "load", str(self.paths.plist_path)], 
                             check=True, capture_output=True)
                time.sleep(2)
                
                is_running, _ = self.check_service_status()
                if is_running:
                    self.logger.info("✓ sing-box 服务启动成功")
                    return True
                else:
                    self.logger.error(f"服务启动失败，查看日志: tail -f {self.paths.log_dir}/sing-box.log")
                    return False
            except subprocess.CalledProcessError as e:
                self.logger.error(f"启动服务失败: {e}")
                return False
        else:
            try:
                subprocess.run(["systemctl", "start", self.paths.service_name], check=True)
                time.sleep(2)
                
                is_running, _ = self.check_service_status()
                if is_running:
                    self.logger.info("✓ sing-box 服务启动成功")
                    return True
                else:
                    self.logger.error(f"服务启动失败，查看日志: journalctl -u {self.paths.service_name} -f")
                    return False
            except subprocess.CalledProcessError as e:
                self.logger.error(f"启动服务失败: {e}")
                return False
    
    def stop_service(self):
        """停止服务"""
        self.logger.step("停止 sing-box 服务...")
        
        if self.paths.os_type == "Darwin":
            try:
                is_running, _ = self.check_service_status()
                if is_running:
                    subprocess.run(["launchctl", "unload", str(self.paths.plist_path)], 
                                 capture_output=True)
                    self.logger.info("✓ sing-box 服务已停止")
                else:
                    self.logger.warn("sing-box 服务未运行")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"停止服务失败: {e}")
                return False
        else:
            try:
                is_running, _ = self.check_service_status()
                if is_running:
                    subprocess.run(["systemctl", "stop", self.paths.service_name], check=True)
                    self.logger.info("✓ sing-box 服务已停止")
                else:
                    self.logger.warn("sing-box 服务未运行")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"停止服务失败: {e}")
                return False
    
    def restart_service(self):
        """重启服务"""
        self.logger.step("重启 sing-box 服务...")
        self.stop_service()
        time.sleep(1)
        return self.start_service()
    
    def is_port_listening(self, port: int) -> bool:
        """检查端口是否在监听"""
        if self.paths.os_type == "Darwin":
            try:
                result = subprocess.run(["lsof", "-i", f":{port}"], 
                                      capture_output=True, text=True)
                return "LISTEN" in result.stdout
            except:
                return False
        else:
            try:
                result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
                return f":{port} " in result.stdout
            except:
                return False
    
    def view_logs(self):
        """查看日志"""
        self.logger.step("查看 sing-box 日志...")
        print(f"{Colors.YELLOW}按 Ctrl+C 退出日志查看{Colors.NC}")
        print()
        
        log_file = self.paths.log_dir / "sing-box.log"
        if log_file.exists():
            try:
                subprocess.run(["tail", "-f", str(log_file)])
            except KeyboardInterrupt:
                print("\n日志查看已退出")
            except subprocess.CalledProcessError:
                self.logger.error("日志查看失败")
        else:
            self.logger.error(f"日志文件不存在: {log_file}")
    
    def uninstall(self):
        """卸载 sing-box"""
        self.logger.step("卸载 sing-box...")
        
        print(f"{Colors.RED}警告: 这将完全删除 sing-box 及其配置文件{Colors.NC}")
        response = input(f"{Colors.YELLOW}是否确认卸载? (y/N):{Colors.NC} ")
        
        if not response or not response.lower().startswith('y'):
            self.logger.info("取消卸载")
            return False
        
        # 停止服务
        self.stop_service()
        
        # 删除服务文件
        if self.paths.os_type == "Darwin" and self.paths.plist_path.exists():
            self.paths.plist_path.unlink()
            self.logger.info("✓ 删除服务配置")
        
        # 删除配置文件
        import shutil
        if self.paths.config_dir.exists():
            shutil.rmtree(self.paths.config_dir)
            self.logger.info("✓ 删除配置目录")
        
        # 删除日志文件
        if self.paths.log_dir.exists():
            shutil.rmtree(self.paths.log_dir)
            self.logger.info("✓ 删除日志目录")
        
        # 卸载软件包
        if self.paths.os_type == "Darwin":
            try:
                result = subprocess.run(["brew", "list"], capture_output=True, text=True)
                if "sing-box" in result.stdout:
                    subprocess.run(["brew", "uninstall", "sing-box"], check=True)
                    self.logger.info("✓ 通过 Homebrew 卸载 sing-box")
            except subprocess.CalledProcessError:
                self.logger.warn("Homebrew 卸载失败，但配置文件已删除")
        
        self.logger.info("✓ 卸载完成")
        return True 