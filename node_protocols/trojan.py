"""
Trojan协议节点处理器
Trojan Protocol Node Handler
"""

from typing import Dict, Optional
from .base import BaseNodeHandler
from utils import Colors


class TrojanNodeHandler(BaseNodeHandler):
    """Trojan节点处理器"""
    
    def add_node(self, node_id: str, node_name: str) -> bool:
        """添加Trojan节点"""
        print()
        print(f"{Colors.BLUE}🔐 配置 Trojan 节点:{Colors.NC}")
        print(f"{Colors.YELLOW}Trojan 是一个高性能的代理协议，使用 TLS 加密{Colors.NC}")
        print()
        
        # 服务器地址
        while True:
            server = input("服务器地址 (例: example.com): ").strip()
            if not server:
                print(f"{Colors.YELLOW}提示: 服务器地址不能为空{Colors.NC}")
                continue
            # 简单验证域名/IP格式
            if '.' not in server:
                confirm = input(f"{Colors.YELLOW}'{server}' 看起来不像一个有效的域名或IP，是否继续? (y/N): {Colors.NC}").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        
        # 端口
        while True:
            port_str = input("端口 (默认 443): ").strip() or "443"
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    print(f"{Colors.YELLOW}提示: 端口范围应在 1-65535 之间{Colors.NC}")
                    continue
                break
            except ValueError:
                print(f"{Colors.YELLOW}提示: 端口必须是数字{Colors.NC}")
        
        # 密码
        while True:
            password = input("密码: ").strip()
            if not password:
                print(f"{Colors.YELLOW}提示: 密码不能为空{Colors.NC}")
                continue
            if len(password) < 6:
                confirm = input(f"{Colors.YELLOW}密码较短，建议使用更长的密码，是否继续? (y/N): {Colors.NC}").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        
        # SNI/服务器名称设置
        print()
        print(f"{Colors.CYAN}🌐 TLS 服务器名称 (SNI):{Colors.NC}")
        print("SNI (Server Name Indication) 用于指定TLS握手时的服务器名称")
        sni = input(f"SNI/服务器名称 (默认 {server}): ").strip() or server
        
        # 证书验证
        print()
        print(f"{Colors.CYAN}🔒 证书验证配置:{Colors.NC}")
        print(f"{Colors.GREEN}选项说明:{Colors.NC}")
        print("  1. 严格验证 (推荐) - 验证服务器证书，确保连接安全")
        print("     ✓ 更安全，防止中间人攻击")
        print("     ✗ 需要服务器有有效的SSL证书")
        print()
        print("  2. 跳过验证 - 不验证证书，允许自签名证书")
        print("     ✓ 兼容性好，适用于自建服务器")
        print("     ✗ 安全性较低，可能受到中间人攻击")
        print()
        
        while True:
            verify_choice = input("请选择证书验证方式 [1=严格验证/2=跳过验证] (默认 1): ").strip() or "1"
            if verify_choice in ["1", "2"]:
                insecure = (verify_choice == "2")
                break
            else:
                print(f"{Colors.YELLOW}请输入 1 或 2{Colors.NC}")
        
        if insecure:
            print(f"{Colors.YELLOW}⚠️  已选择跳过证书验证，请确保服务器可信{Colors.NC}")
        else:
            print(f"{Colors.GREEN}✓ 已选择严格验证，将验证服务器证书{Colors.NC}")
        
        # 传输协议
        print()
        print(f"{Colors.CYAN}传输协议选项:{Colors.NC}")
        print("  1) TCP - 直接TCP连接 (默认)")
        print("  2) WebSocket - 通过WebSocket传输，可伪装成网页流量")
        transport_choice = input("请选择传输协议 [1-2]: ").strip() or "1"
        
        transport = "tcp"
        ws_config = None
        
        if transport_choice == "2":
            transport = "ws"
            print()
            print(f"{Colors.CYAN}WebSocket 配置:{Colors.NC}")
            ws_path = input("WebSocket 路径 (默认 /): ").strip() or "/"
            ws_host = input(f"WebSocket Host (默认 {sni}): ").strip() or sni
            ws_config = {
                "type": "ws",
                "path": ws_path,
                "headers": {"Host": ws_host}
            }
        
        # 构建节点配置
        node_config = self.get_base_config(node_name, "trojan")
        node_config["config"].update({
            "server": server,
            "port": port,
            "password": password,
            "tls": {
                "enabled": True,
                "server_name": sni,
                "insecure": insecure
            }
        })
        
        if ws_config:
            node_config["config"]["transport"] = ws_config
        
        # 显示配置摘要
        print()
        print(f"{Colors.GREEN}📋 配置摘要:{Colors.NC}")
        print(f"  节点名称: {Colors.CYAN}{node_name}{Colors.NC}")
        print(f"  服务器: {Colors.CYAN}{server}:{port}{Colors.NC}")
        print(f"  SNI: {Colors.CYAN}{sni}{Colors.NC}")
        print(f"  证书验证: {Colors.CYAN}{'跳过' if insecure else '严格'}{Colors.NC}")
        print(f"  传输: {Colors.CYAN}{transport.upper()}{Colors.NC}")
        if ws_config:
            print(f"  WS路径: {Colors.CYAN}{ws_config['path']}{Colors.NC}")
            print(f"  WS Host: {Colors.CYAN}{ws_config['headers']['Host']}{Colors.NC}")
        
        # 确认保存
        print()
        confirm = input(f"{Colors.YELLOW}确认添加此节点? (Y/n): {Colors.NC}").strip().lower()
        if confirm and not confirm.startswith('y'):
            self.logger.info("取消添加节点")
            return False
        
        self.logger.info(f"✓ Trojan 节点添加成功: {node_name}")
        return node_config
    
    def validate_config(self, config: dict) -> dict:
        """校验Trojan配置"""
        required_fields = ['server', 'port', 'password']
        for field in required_fields:
            if not config.get(field):
                return {'valid': False, 'error': f'缺少必需字段: {field}'}
        
        # 检查端口范围
        port = config.get('port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            return {'valid': False, 'error': f'端口号无效: {port}'}
        
        return {'valid': True, 'error': None}
    
    def convert_from_clash(self, clash_node: dict) -> Optional[dict]:
        """从Clash格式转换Trojan节点"""
        config = {
            "type": "trojan",
            "tag": "proxy",
            "server": clash_node.get('server'),
            "port": clash_node.get('port', 443),
            "password": clash_node.get('password'),
            "tls": {
                "enabled": True,
                "insecure": clash_node.get('skip-cert-verify', False),
                "server_name": clash_node.get('sni', clash_node.get('servername', ''))
            }
        }
        
        # 处理WebSocket传输
        network = clash_node.get('network')
        if network == 'ws':
            ws_opts = clash_node.get('ws-opts', {})
            config["transport"] = {
                "type": "ws",
                "path": ws_opts.get('path', '/'),
                "headers": ws_opts.get('headers', {})
            }
        
        return config 