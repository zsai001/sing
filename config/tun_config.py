#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUN模式配置管理模块
TUN Mode Configuration Manager
"""

from typing import Dict, Any
from utils import Colors, Logger
from paths import PathManager
from .base_config import BaseConfigManager


class TUNConfigManager(BaseConfigManager):
    """TUN模式配置管理器"""
    
    def __init__(self, paths: PathManager, logger: Logger):
        super().__init__(paths, logger)
    
    def configure_tun_mode(self):
        """配置TUN模式 - 直接修改sing-box配置"""
        print()
        print(f"{Colors.CYAN}🚇 TUN模式配置{Colors.NC}")
        print("配置虚拟网络接口，实现透明代理")
        print()
        
        # 读取当前sing-box配置
        config = self.load_sing_box_config()
        if not config:
            self.logger.error("未找到 sing-box 配置文件")
            return
        
        # 检查当前TUN配置状态
        inbounds = config.get("inbounds", [])
        tun_inbound = None
        for inbound in inbounds:
            if inbound.get("type") == "tun":
                tun_inbound = inbound
                break
        
        is_enabled = tun_inbound is not None
        
        print(f"{Colors.YELLOW}当前TUN模式状态:{Colors.NC}")
        if is_enabled:
            print(f"  状态: {Colors.GREEN}启用{Colors.NC}")
            print(f"  接口名: {tun_inbound.get('interface_name', 'tun0')}")
            print(f"  MTU: {tun_inbound.get('mtu', 9000)}")
            
            # 处理地址格式兼容性
            address = tun_inbound.get('address')
            inet4_address = tun_inbound.get('inet4_address')
            inet6_address = tun_inbound.get('inet6_address')
            
            if address:
                print(f"  地址: {address}")
            else:
                if inet4_address:
                    print(f"  IPv4地址: {inet4_address}")
                if inet6_address:
                    print(f"  IPv6地址: {inet6_address}")
            
            auto_route = tun_inbound.get('auto_route', True)
            strict_route = tun_inbound.get('strict_route', True)
            print(f"  自动路由: {'开启' if auto_route else '关闭'}")
            print(f"  严格路由: {'开启' if strict_route else '关闭'}")
        else:
            print(f"  状态: {Colors.RED}禁用{Colors.NC}")
        
        print()
        
        while True:
            print("配置选项:")
            print("1. 启用/禁用 TUN模式")
            print("2. 设置接口名称")
            print("3. 设置MTU值")
            print("4. 配置IP地址")
            print("5. 路由设置")
            print("6. 高级设置")
            print("7. 保存并返回")
            print()
            
            choice = input("请选择 [1-7]: ").strip()
            
            if choice == "1":
                self._toggle_tun_mode(config)
            elif choice == "2":
                self._configure_interface_name(config)
            elif choice == "3":
                self._configure_mtu(config)
            elif choice == "4":
                self._configure_addresses(config)
            elif choice == "5":
                self._configure_routing(config)
            elif choice == "6":
                self._configure_advanced_settings(config)
            elif choice == "7":
                self.save_config_and_restart(config, "TUN模式配置已更新")
                return
            else:
                self.logger.error("无效选项")
    
    def _get_or_create_tun_inbound(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取或创建TUN入站配置"""
        inbounds = config.setdefault("inbounds", [])
        
        # 查找现有TUN配置
        for inbound in inbounds:
            if inbound.get("type") == "tun":
                return inbound
        
        # 创建新的TUN配置
        tun_inbound = {
            "type": "tun",
            "tag": "tun-in",
            "interface_name": "tun0",
            "address": ["172.19.0.1/30", "fdfe:dcba:9876::1/126"],
            "mtu": 9000,
            "auto_route": True,
            "strict_route": True,
            "sniff": True,
            "sniff_override_destination": True
        }
        inbounds.append(tun_inbound)
        return tun_inbound
    
    def _toggle_tun_mode(self, config: Dict[str, Any]):
        """启用/禁用TUN模式"""
        inbounds = config.get("inbounds", [])
        tun_index = -1
        
        for i, inbound in enumerate(inbounds):
            if inbound.get("type") == "tun":
                tun_index = i
                break
        
        if tun_index >= 0:
            # 禁用TUN模式
            removed = inbounds.pop(tun_index)
            self.logger.info("✓ TUN模式已禁用")
        else:
            # 启用TUN模式
            self._get_or_create_tun_inbound(config)
            self.logger.info("✓ TUN模式已启用")
    
    def _configure_interface_name(self, config: Dict[str, Any]):
        """配置接口名称"""
        tun_inbound = self._get_or_create_tun_inbound(config)
        current_name = tun_inbound.get("interface_name", "tun0")
        
        new_name = input(f"设置接口名称 (当前: {current_name}): ").strip()
        if new_name:
            tun_inbound["interface_name"] = new_name
            self.logger.info(f"✓ 接口名称设置为: {new_name}")
    
    def _configure_mtu(self, config: Dict[str, Any]):
        """配置MTU值"""
        tun_inbound = self._get_or_create_tun_inbound(config)
        current_mtu = tun_inbound.get("mtu", 9000)
        
        try:
            new_mtu = int(input(f"设置MTU值 (当前: {current_mtu}, 建议: 1500-9000): ").strip())
            if 1280 <= new_mtu <= 9000:
                tun_inbound["mtu"] = new_mtu
                self.logger.info(f"✓ MTU设置为: {new_mtu}")
            else:
                self.logger.error("MTU值应在1280-9000之间")
        except ValueError:
            self.logger.error("MTU必须是数字")
    
    def _configure_addresses(self, config: Dict[str, Any]):
        """配置IP地址"""
        tun_inbound = self._get_or_create_tun_inbound(config)
        
        # 处理地址格式兼容性
        current_address = tun_inbound.get('address')
        current_inet4 = tun_inbound.get('inet4_address')
        current_inet6 = tun_inbound.get('inet6_address')
        
        print()
        print("当前地址配置:")
        if current_address:
            print(f"  统一地址格式: {current_address}")
        else:
            if current_inet4:
                print(f"  IPv4地址: {current_inet4}")
            if current_inet6:
                print(f"  IPv6地址: {current_inet6}")
        
        print()
        print("1. 使用统一地址格式 (推荐)")
        print("2. 使用分离地址格式")
        print("3. 返回上级")
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            # 统一地址格式
            ipv4 = input("IPv4地址 (如 172.19.0.1/30): ").strip()
            ipv6 = input("IPv6地址 (如 fdfe:dcba:9876::1/126): ").strip()
            
            addresses = []
            if ipv4:
                addresses.append(ipv4)
            if ipv6:
                addresses.append(ipv6)
            
            if addresses:
                # 移除旧格式字段
                tun_inbound.pop('inet4_address', None)
                tun_inbound.pop('inet6_address', None)
                tun_inbound['address'] = addresses
                self.logger.info("✓ 地址配置已更新为统一格式")
        
        elif choice == "2":
            # 分离地址格式
            ipv4 = input("IPv4地址 (如 172.19.0.1/30): ").strip()
            ipv6 = input("IPv6地址 (如 fdfe:dcba:9876::1/126): ").strip()
            
            # 移除统一格式字段
            tun_inbound.pop('address', None)
            
            if ipv4:
                tun_inbound['inet4_address'] = ipv4
            if ipv6:
                tun_inbound['inet6_address'] = ipv6
            
            self.logger.info("✓ 地址配置已更新为分离格式")
    
    def _configure_routing(self, config: Dict[str, Any]):
        """配置路由设置"""
        tun_inbound = self._get_or_create_tun_inbound(config)
        
        current_auto = tun_inbound.get("auto_route", True)
        current_strict = tun_inbound.get("strict_route", True)
        
        print()
        print(f"当前路由设置:")
        print(f"  自动路由: {'开启' if current_auto else '关闭'}")
        print(f"  严格路由: {'开启' if current_strict else '关闭'}")
        print()
        
        print("1. 切换自动路由")
        print("2. 切换严格路由")
        print("3. 配置排除路由")
        print("4. 返回上级")
        
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            tun_inbound["auto_route"] = not current_auto
            status = "开启" if not current_auto else "关闭"
            self.logger.info(f"✓ 自动路由已{status}")
        
        elif choice == "2":
            tun_inbound["strict_route"] = not current_strict
            status = "开启" if not current_strict else "关闭"
            self.logger.info(f"✓ 严格路由已{status}")
        
        elif choice == "3":
            self._configure_exclude_routes(tun_inbound)
    
    def _configure_exclude_routes(self, tun_inbound: Dict[str, Any]):
        """配置排除路由"""
        exclude_package = tun_inbound.get("exclude_package", [])
        
        print()
        print("当前排除的应用包名:")
        for i, package in enumerate(exclude_package, 1):
            print(f"  {i}. {package}")
        
        print()
        print("1. 添加排除包名")
        print("2. 删除排除包名")
        print("3. 返回上级")
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            package = input("输入要排除的应用包名: ").strip()
            if package and package not in exclude_package:
                exclude_package.append(package)
                tun_inbound["exclude_package"] = exclude_package
                self.logger.info(f"✓ 已添加排除包名: {package}")
        
        elif choice == "2":
            if exclude_package:
                try:
                    index = int(input("输入要删除的包名编号: ").strip()) - 1
                    if 0 <= index < len(exclude_package):
                        removed = exclude_package.pop(index)
                        tun_inbound["exclude_package"] = exclude_package
                        self.logger.info(f"✓ 已删除排除包名: {removed}")
                    else:
                        self.logger.error("无效编号")
                except ValueError:
                    self.logger.error("请输入有效数字")
    
    def _configure_advanced_settings(self, config: Dict[str, Any]):
        """配置高级设置"""
        tun_inbound = self._get_or_create_tun_inbound(config)
        
        print()
        print("高级设置:")
        print(f"1. 嗅探设置 (当前: {'开启' if tun_inbound.get('sniff', True) else '关闭'})")
        print(f"2. 覆盖目标 (当前: {'开启' if tun_inbound.get('sniff_override_destination', True) else '关闭'})")
        print("3. 返回上级")
        
        choice = input("请选择 [1-3]: ").strip()
        
        if choice == "1":
            current = tun_inbound.get("sniff", True)
            tun_inbound["sniff"] = not current
            status = "开启" if not current else "关闭"
            self.logger.info(f"✓ 嗅探功能已{status}")
        
        elif choice == "2":
            current = tun_inbound.get("sniff_override_destination", True)
            tun_inbound["sniff_override_destination"] = not current
            status = "开启" if not current else "关闭"
            self.logger.info(f"✓ 目标覆盖已{status}") 