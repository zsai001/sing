#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统代理配置管理模块
System Proxy Configuration Manager
"""

import json
import subprocess
import platform
from typing import Dict, Any
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager


class SystemProxyManager(BaseConfigManager):
    """系统代理配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
        self.advanced_config_file = self.paths.config_dir / "advanced.json"
        self.system_type = platform.system().lower()
    
    def load_system_proxy_config(self) -> Dict[str, Any]:
        """加载系统代理配置"""
        default_config = {
            "enabled": False,
            "auto_set": True,
            "proxy_type": "http",
            "proxy_host": "127.0.0.1",
            "proxy_port": 7890,
            "bypass_domains": [
                "localhost", "127.0.0.1", "::1", "10.*", "172.16.*", "172.17.*", 
                "172.18.*", "172.19.*", "172.20.*", "172.21.*", "172.22.*", "172.23.*",
                "172.24.*", "172.25.*", "172.26.*", "172.27.*", "172.28.*", "172.29.*",
                "172.30.*", "172.31.*", "192.168.*", "*.local", "*.cn"
            ],
            "pac_enabled": False,
            "pac_url": ""
        }
        
        if not self.advanced_config_file.exists():
            return default_config
        
        try:
            with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                system_proxy = config.get("system_proxy", {})
                # 合并默认配置
                default_config.update(system_proxy)
                return default_config
        except (FileNotFoundError, json.JSONDecodeError):
            return default_config
    
    def save_system_proxy_config(self, proxy_config: Dict[str, Any]):
        """保存系统代理配置"""
        if self.advanced_config_file.exists():
            try:
                with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
        else:
            config = {}
        
        config["system_proxy"] = proxy_config
        
        try:
            self.advanced_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存系统代理配置失败: {e}")
    
    def configure_system_proxy(self):
        """配置系统代理"""
        print()
        print(f"{Colors.CYAN}🌍 系统代理配置{Colors.NC}")
        print("管理系统级代理设置，自动配置操作系统代理")
        print()
        
        proxy_config = self.load_system_proxy_config()
        
        print(f"{Colors.YELLOW}当前系统代理配置:{Colors.NC}")
        print(f"  状态: {'启用' if proxy_config.get('enabled', False) else '禁用'}")
        print(f"  自动设置: {'是' if proxy_config.get('auto_set', True) else '否'}")
        print(f"  代理类型: {proxy_config.get('proxy_type', 'http').upper()}")
        print(f"  代理地址: {proxy_config.get('proxy_host', '127.0.0.1')}:{proxy_config.get('proxy_port', 7890)}")
        print(f"  绕过域名数量: {len(proxy_config.get('bypass_domains', []))}")
        print(f"  PAC模式: {'启用' if proxy_config.get('pac_enabled', False) else '禁用'}")
        print()
        
        while True:
            print("配置选项:")
            print("1. 启用/禁用系统代理")
            print("2. 配置代理设置")
            print("3. 管理绕过域名")
            print("4. PAC配置")
            print("5. 应用代理设置")
            print("6. 清除代理设置")
            print("7. 检查代理状态")
            print("8. 保存并返回")
            print()
            
            choice = input("请选择 [1-8]: ").strip()
            
            if choice == "1":
                current = proxy_config.get('enabled', False)
                toggle = input(f"系统代理当前{'启用' if current else '禁用'}，是否切换? (y/N): ").strip().lower()
                if toggle in ['y', 'yes']:
                    proxy_config['enabled'] = not current
                    status = '启用' if not current else '禁用'
                    self.logger.info(f"✓ 系统代理已{status}")
                    
            elif choice == "2":
                self._configure_proxy_settings(proxy_config)
            elif choice == "3":
                self._configure_bypass_domains(proxy_config)
            elif choice == "4":
                self._configure_pac_settings(proxy_config)
            elif choice == "5":
                self._apply_system_proxy(proxy_config)
            elif choice == "6":
                self._clear_system_proxy()
            elif choice == "7":
                self._check_system_proxy_status()
            elif choice == "8":
                self.save_system_proxy_config(proxy_config)
                self.logger.info("✓ 系统代理配置已保存")
                return
            else:
                self.logger.error("无效选项")
    
    def _configure_proxy_settings(self, proxy_config: Dict[str, Any]):
        """配置代理设置"""
        print()
        print("代理设置:")
        print("1. 设置代理类型")
        print("2. 设置代理地址")
        print("3. 设置代理端口")
        print("4. 切换自动设置")
        print("5. 返回上级")
        
        choice = input("请选择 [1-5]: ").strip()
        
        if choice == "1":
            print("代理类型: 1-HTTP, 2-SOCKS5")
            type_choice = input("选择代理类型 [1-2]: ").strip()
            if type_choice == "1":
                proxy_config['proxy_type'] = 'http'
                self.logger.info("✓ 代理类型设置为: HTTP")
            elif type_choice == "2":
                proxy_config['proxy_type'] = 'socks5'
                self.logger.info("✓ 代理类型设置为: SOCKS5")
                
        elif choice == "2":
            current_host = proxy_config.get('proxy_host', '127.0.0.1')
            new_host = input(f"设置代理地址 (当前: {current_host}): ").strip()
            if new_host:
                proxy_config['proxy_host'] = new_host
                self.logger.info(f"✓ 代理地址设置为: {new_host}")
                
        elif choice == "3":
            current_port = proxy_config.get('proxy_port', 7890)
            try:
                new_port = int(input(f"设置代理端口 (当前: {current_port}): ").strip())
                proxy_config['proxy_port'] = new_port
                self.logger.info(f"✓ 代理端口设置为: {new_port}")
            except ValueError:
                self.logger.error("端口必须是数字")
                
        elif choice == "4":
            current_auto = proxy_config.get('auto_set', True)
            proxy_config['auto_set'] = not current_auto
            status = "启用" if not current_auto else "禁用"
            self.logger.info(f"✓ 自动设置已{status}")
    
    def _configure_bypass_domains(self, proxy_config: Dict[str, Any]):
        """配置绕过域名"""
        print()
        print("绕过域名管理:")
        print("1. 查看绕过域名")
        print("2. 添加绕过域名")
        print("3. 删除绕过域名")
        print("4. 重置默认域名")
        print("5. 返回上级")
        
        choice = input("请选择 [1-5]: ").strip()
        
        if choice == "1":
            bypass_domains = proxy_config.get('bypass_domains', [])
            print(f"\n当前绕过域名 (共{len(bypass_domains)}个):")
            for i, domain in enumerate(bypass_domains, 1):
                print(f"  {i}. {domain}")
                
        elif choice == "2":
            domain = input("输入要添加的绕过域名: ").strip()
            bypass_domains = proxy_config.get('bypass_domains', [])
            if domain and domain not in bypass_domains:
                bypass_domains.append(domain)
                self.logger.info(f"✓ 已添加绕过域名: {domain}")
                
        elif choice == "3":
            bypass_domains = proxy_config.get('bypass_domains', [])
            if bypass_domains:
                print("当前绕过域名:")
                for i, domain in enumerate(bypass_domains, 1):
                    print(f"  {i}. {domain}")
                try:
                    index = int(input("输入要删除的域名编号: ").strip()) - 1
                    if 0 <= index < len(bypass_domains):
                        removed = bypass_domains.pop(index)
                        self.logger.info(f"✓ 已删除域名: {removed}")
                    else:
                        self.logger.error("无效编号")
                except ValueError:
                    self.logger.error("请输入有效数字")
                    
        elif choice == "4":
            confirm = input("确定要重置为默认绕过域名吗? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                proxy_config['bypass_domains'] = [
                    "localhost", "127.0.0.1", "::1", "10.*", "172.16.*", "172.17.*", 
                    "172.18.*", "172.19.*", "172.20.*", "172.21.*", "172.22.*", "172.23.*",
                    "172.24.*", "172.25.*", "172.26.*", "172.27.*", "172.28.*", "172.29.*",
                    "172.30.*", "172.31.*", "192.168.*", "*.local", "*.cn"
                ]
                self.logger.info("✓ 已重置为默认绕过域名")
    
    def _configure_pac_settings(self, proxy_config: Dict[str, Any]):
        """配置PAC设置"""
        print()
        print("PAC配置:")
        print(f"1. 启用/禁用PAC (当前: {'启用' if proxy_config.get('pac_enabled', False) else '禁用'})")
        print("2. 设置PAC URL")
        print("3. 生成PAC文件")
        print("4. 返回上级")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            current_pac = proxy_config.get('pac_enabled', False)
            toggle = input(f"PAC当前{'启用' if current_pac else '禁用'}，是否切换? (y/N): ").strip().lower()
            if toggle in ['y', 'yes']:
                proxy_config['pac_enabled'] = not current_pac
                status = '启用' if not current_pac else '禁用'
                self.logger.info(f"✓ PAC已{status}")
                
        elif choice == "2":
            current_url = proxy_config.get('pac_url', '')
            new_url = input(f"设置PAC URL (当前: {current_url or '未设置'}): ").strip()
            if new_url:
                proxy_config['pac_url'] = new_url
                self.logger.info(f"✓ PAC地址设置为: {new_url}")
                
        elif choice == "3":
            self._generate_pac_file(proxy_config)
    
    def _generate_pac_file(self, proxy_config: Dict[str, Any]):
        """生成PAC文件"""
        pac_file = self.paths.config_dir / "proxy.pac"
        pac_content = self._create_pac_content(proxy_config)
        
        try:
            with open(pac_file, 'w', encoding='utf-8') as f:
                f.write(pac_content)
            
            pac_url = f"file://{pac_file.absolute()}"
            proxy_config['pac_url'] = pac_url
            proxy_config['pac_enabled'] = True
            
            self.logger.info(f"✓ PAC文件已生成: {pac_file}")
            self.logger.info(f"✓ PAC URL: {pac_url}")
        except Exception as e:
            self.logger.error(f"生成PAC文件失败: {e}")
    
    def _create_pac_content(self, proxy_config: Dict[str, Any]) -> str:
        """创建PAC文件内容"""
        proxy_type = proxy_config.get('proxy_type', 'http').upper()
        proxy_host = proxy_config.get('proxy_host', '127.0.0.1')
        proxy_port = proxy_config.get('proxy_port', 7890)
        bypass_domains = proxy_config.get('bypass_domains', [])
        
        proxy_string = f"{proxy_type} {proxy_host}:{proxy_port}"
        
        pac_content = f"""function FindProxyForURL(url, host) {{
    // 绕过本地地址
    if (isPlainHostName(host) ||
        shExpMatch(host, "localhost") ||
        isInNet(dnsResolve(host), "127.0.0.0", "255.0.0.0") ||
        isInNet(dnsResolve(host), "10.0.0.0", "255.0.0.0") ||
        isInNet(dnsResolve(host), "172.16.0.0", "255.240.0.0") ||
        isInNet(dnsResolve(host), "192.168.0.0", "255.255.0.0")) {{
        return "DIRECT";
    }}
    
    // 绕过自定义域名
"""
        
        for domain in bypass_domains:
            if domain.startswith("*."):
                domain_pattern = domain[2:]
                pac_content += f'    if (shExpMatch(host, "*{domain_pattern}")) {{ return "DIRECT"; }}\n'
            elif "*" in domain:
                pac_content += f'    if (shExpMatch(host, "{domain}")) {{ return "DIRECT"; }}\n'
            else:
                pac_content += f'    if (host == "{domain}") {{ return "DIRECT"; }}\n'
        
        pac_content += f"""
    // 其他流量使用代理
    return "{proxy_string}";
}}"""
        
        return pac_content
    
    def _apply_system_proxy(self, proxy_config: Dict[str, Any]):
        """应用系统代理设置"""
        if not proxy_config.get('auto_set', True):
            proxy_config['auto_set'] = False
        
        proxy_type = proxy_config.get('proxy_type', 'http')
        proxy_host = proxy_config.get('proxy_host', '127.0.0.1')
        proxy_port = proxy_config.get('proxy_port', 7890)
        pac_enabled = proxy_config.get('pac_enabled', False)
        pac_url = proxy_config.get('pac_url', '')
        
        self.logger.info(f"正在设置系统代理: {proxy_type.upper()} {proxy_host}:{proxy_port}")
        
        try:
            if self.system_type == "darwin":
                self._set_macos_proxy(proxy_host, proxy_port, proxy_type, pac_enabled, pac_url, proxy_config)
            elif self.system_type == "linux":
                self._set_linux_proxy(proxy_host, proxy_port, proxy_type, pac_enabled, pac_url, proxy_config)
            elif self.system_type == "windows":
                self._set_windows_proxy(proxy_host, proxy_port, proxy_type, pac_enabled, pac_url, proxy_config)
            else:
                self.logger.error(f"不支持的操作系统: {self.system_type}")
        except Exception as e:
            self.logger.error(f"设置系统代理失败: {e}")
    
    def _clear_system_proxy(self):
        """清除系统代理设置"""
        self.logger.info("正在清除系统代理设置...")
        
        try:
            if self.system_type == "darwin":
                self._clear_macos_proxy()
            elif self.system_type == "linux":
                self._clear_linux_proxy()
            elif self.system_type == "windows":
                self._clear_windows_proxy()
            
            self.logger.info("✓ 系统代理已清除")
        except Exception as e:
            self.logger.error(f"清除系统代理失败: {e}")
    
    def _check_system_proxy_status(self):
        """检查系统代理状态"""
        try:
            if self.system_type == "darwin":
                self._check_macos_proxy_status()
            elif self.system_type == "linux":
                self._check_linux_proxy_status()
            elif self.system_type == "windows":
                self._check_windows_proxy_status()
        except Exception as e:
            self.logger.error(f"检查代理状态失败: {e}")
    
    def _set_macos_proxy(self, host: str, port: int, proxy_type: str, pac_enabled: bool, pac_url: str, proxy_config: Dict[str, Any]):
        """设置macOS系统代理"""
        # 获取网络服务名称
        result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                              capture_output=True, text=True)
        services = [line.strip() for line in result.stdout.split('\n')[1:] if line.strip() and not line.startswith('*')]
        
        for service in services:
            if not service:
                continue
                
            try:
                if pac_enabled and pac_url:
                    # 设置PAC代理
                    subprocess.run(['networksetup', '-setautoproxyurl', service, pac_url], check=True)
                    subprocess.run(['networksetup', '-setautoproxystate', service, 'on'], check=True)
                else:
                    # 设置HTTP/HTTPS代理
                    if proxy_type in ['http', 'https']:
                        subprocess.run(['networksetup', '-setwebproxy', service, host, str(port)], check=True)
                        subprocess.run(['networksetup', '-setwebproxystate', service, 'on'], check=True)
                        subprocess.run(['networksetup', '-setsecurewebproxy', service, host, str(port)], check=True)
                        subprocess.run(['networksetup', '-setsecurewebproxystate', service, 'on'], check=True)
                    
                    # 设置SOCKS代理
                    if proxy_type == 'socks5':
                        subprocess.run(['networksetup', '-setsocksfirewallproxy', service, host, str(port)], check=True)
                        subprocess.run(['networksetup', '-setsocksfirewallproxystate', service, 'on'], check=True)
                
                # 设置绕过域名
                bypass_domains = proxy_config.get('bypass_domains', [])
                if bypass_domains:
                    subprocess.run(['networksetup', '-setproxybypassdomains', service] + bypass_domains, check=True)
                
            except subprocess.CalledProcessError as e:
                self.logger.warn(f"设置 {service} 代理失败: {e}")
                continue
        
        self.logger.info("✓ macOS系统代理设置完成")
    
    def _clear_macos_proxy(self):
        """清除macOS系统代理"""
        result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                              capture_output=True, text=True)
        services = [line.strip() for line in result.stdout.split('\n')[1:] if line.strip() and not line.startswith('*')]
        
        for service in services:
            if not service:
                continue
                
            try:
                # 禁用所有代理
                subprocess.run(['networksetup', '-setwebproxystate', service, 'off'], check=True)
                subprocess.run(['networksetup', '-setsecurewebproxystate', service, 'off'], check=True)
                subprocess.run(['networksetup', '-setsocksfirewallproxystate', service, 'off'], check=True)
                subprocess.run(['networksetup', '-setautoproxystate', service, 'off'], check=True)
                
            except subprocess.CalledProcessError as e:
                self.logger.warn(f"清除 {service} 代理失败: {e}")
                continue
    
    def _check_macos_proxy_status(self):
        """检查macOS代理状态"""
        result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                              capture_output=True, text=True)
        services = [line.strip() for line in result.stdout.split('\n')[1:] if line.strip() and not line.startswith('*')]
        
        print()
        print(f"{Colors.YELLOW}macOS 系统代理状态:{Colors.NC}")
        
        for service in services[:3]:  # 只检查前3个网络服务
            if not service:
                continue
                
            print(f"\n网络服务: {service}")
            
            # 检查HTTP代理
            result = subprocess.run(['networksetup', '-getwebproxy', service], 
                                  capture_output=True, text=True)
            if 'Enabled: Yes' in result.stdout:
                print("  HTTP代理: 启用")
                for line in result.stdout.split('\n'):
                    if 'Server:' in line or 'Port:' in line:
                        print(f"    {line.strip()}")
            else:
                print("  HTTP代理: 禁用")
            
            # 检查SOCKS代理
            result = subprocess.run(['networksetup', '-getsocksfirewallproxy', service], 
                                  capture_output=True, text=True)
            if 'Enabled: Yes' in result.stdout:
                print("  SOCKS代理: 启用")
                for line in result.stdout.split('\n'):
                    if 'Server:' in line or 'Port:' in line:
                        print(f"    {line.strip()}")
            else:
                print("  SOCKS代理: 禁用")
            
            # 检查PAC代理
            result = subprocess.run(['networksetup', '-getautoproxyurl', service], 
                                  capture_output=True, text=True)
            if 'Enabled: Yes' in result.stdout:
                print("  PAC代理: 启用")
                for line in result.stdout.split('\n'):
                    if 'URL:' in line:
                        print(f"    {line.strip()}")
            else:
                print("  PAC代理: 禁用")
    
    def _set_linux_proxy(self, host: str, port: int, proxy_type: str, pac_enabled: bool, pac_url: str, proxy_config: Dict[str, Any]):
        """设置Linux系统代理"""
        # Linux通过环境变量设置代理
        if proxy_type == 'http':
            proxy_url = f"http://{host}:{port}"
        elif proxy_type == 'socks5':
            proxy_url = f"socks5://{host}:{port}"
        else:
            proxy_url = f"http://{host}:{port}"
        
        # 设置环境变量（临时）
        import os
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        
        # 设置绕过
        bypass_domains = proxy_config.get('bypass_domains', [])
        if bypass_domains:
            no_proxy = ','.join(bypass_domains)
            os.environ['no_proxy'] = no_proxy
            os.environ['NO_PROXY'] = no_proxy
        
        self.logger.info("✓ Linux环境变量代理已设置（临时）")
        self.logger.warn("注意: 这只是临时设置，重启后失效")
        self.logger.info("如需永久设置，请手动配置 ~/.bashrc 或 ~/.zshrc")
    
    def _clear_linux_proxy(self):
        """清除Linux系统代理"""
        import os
        proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'no_proxy', 'NO_PROXY']
        
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
        
        self.logger.info("✓ Linux环境变量代理已清除")
    
    def _check_linux_proxy_status(self):
        """检查Linux代理状态"""
        import os
        
        print()
        print(f"{Colors.YELLOW}Linux 系统代理状态:{Colors.NC}")
        
        proxy_vars = {
            'http_proxy': 'HTTP代理',
            'https_proxy': 'HTTPS代理', 
            'HTTP_PROXY': 'HTTP代理(大写)',
            'HTTPS_PROXY': 'HTTPS代理(大写)',
            'no_proxy': '绕过列表',
            'NO_PROXY': '绕过列表(大写)'
        }
        
        for var, desc in proxy_vars.items():
            value = os.environ.get(var)
            if value:
                print(f"  {desc}: {value}")
            else:
                print(f"  {desc}: 未设置")
    
    def _set_windows_proxy(self, host: str, port: int, proxy_type: str, pac_enabled: bool, pac_url: str, proxy_config: Dict[str, Any]):
        """设置Windows系统代理"""
        try:
            import winreg
            
            # 打开注册表项
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                   0, winreg.KEY_WRITE)
            
            if pac_enabled and pac_url:
                # 设置PAC
                winreg.SetValueEx(reg_key, "AutoConfigURL", 0, winreg.REG_SZ, pac_url)
                winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            else:
                # 设置HTTP代理
                proxy_server = f"{host}:{port}"
                winreg.SetValueEx(reg_key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
                winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                
                # 设置绕过列表
                bypass_domains = proxy_config.get('bypass_domains', [])
                if bypass_domains:
                    bypass_list = ';'.join(bypass_domains)
                    winreg.SetValueEx(reg_key, "ProxyOverride", 0, winreg.REG_SZ, bypass_list)
            
            winreg.CloseKey(reg_key)
            
            # 刷新系统设置
            import ctypes
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)  # INTERNET_OPTION_REFRESH
            
            self.logger.info("✓ Windows系统代理设置完成")
            
        except ImportError:
            self.logger.error("Windows系统代理设置需要winreg模块支持")
        except Exception as e:
            self.logger.error(f"设置Windows代理失败: {e}")
    
    def _clear_windows_proxy(self):
        """清除Windows系统代理"""
        try:
            import winreg
            
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                   0, winreg.KEY_WRITE)
            
            # 禁用代理
            winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            
            # 清除PAC
            try:
                winreg.DeleteValue(reg_key, "AutoConfigURL")
            except:
                pass
            
            winreg.CloseKey(reg_key)
            
            # 刷新系统设置
            import ctypes
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
            
        except ImportError:
            self.logger.error("Windows系统代理设置需要winreg模块支持")
        except Exception as e:
            self.logger.error(f"清除Windows代理失败: {e}")
    
    def _check_windows_proxy_status(self):
        """检查Windows代理状态"""
        try:
            import winreg
            
            print()
            print(f"{Colors.YELLOW}Windows 系统代理状态:{Colors.NC}")
            
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
            
            try:
                proxy_enable = winreg.QueryValueEx(reg_key, "ProxyEnable")[0]
                print(f"  代理状态: {'启用' if proxy_enable else '禁用'}")
                
                if proxy_enable:
                    try:
                        proxy_server = winreg.QueryValueEx(reg_key, "ProxyServer")[0]
                        print(f"  代理服务器: {proxy_server}")
                    except:
                        pass
                    
                    try:
                        proxy_override = winreg.QueryValueEx(reg_key, "ProxyOverride")[0]
                        print(f"  绕过列表: {proxy_override}")
                    except:
                        pass
                
                try:
                    auto_config_url = winreg.QueryValueEx(reg_key, "AutoConfigURL")[0]
                    print(f"  PAC地址: {auto_config_url}")
                except:
                    print("  PAC: 未设置")
                
            except Exception as e:
                print(f"  读取代理设置失败: {e}")
            
            winreg.CloseKey(reg_key)
            
        except ImportError:
            self.logger.error("Windows系统代理检查需要winreg模块支持")
        except Exception as e:
            self.logger.error(f"检查Windows代理状态失败: {e}") 