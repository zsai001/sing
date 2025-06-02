"""
节点测试模块
Node Testing Module
"""

import socket
import time
import requests
import subprocess
import concurrent.futures
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from utils import Colors, Logger


class NodeTester:
    """节点测试器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def test_node_connectivity(self, nodes: Dict, node_id: str = None) -> bool:
        """测试节点连通性"""
        if not nodes:
            self.logger.error("暂无节点可测试")
            return False
        
        if node_id:
            nodes_to_test = {node_id: nodes.get(node_id)} if node_id in nodes else {}
        else:
            nodes_to_test = nodes
        
        if not nodes_to_test:
            self.logger.error(f"节点 '{node_id}' 不存在")
            return False
        
        self.logger.step("测试节点连通性...")
        print()
        
        results = []
        for test_node_id, node_info in nodes_to_test.items():
            name = node_info.get('name', test_node_id)
            node_type = node_info.get('type', 'unknown')
            config_data = node_info.get('config', {})
            
            print(f"测试节点: {name} ({test_node_id})")
            
            if node_type in ['local_server', 'local_client']:
                print("  本地节点 - 跳过网络测试")
            elif node_type in ['trojan', 'vless', 'shadowsocks', 'vmess', 'hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
                # 远程节点
                server = config_data.get('server', '')
                port = config_data.get('port', 443)
                
                if not server:
                    status = f"{Colors.RED}错误{Colors.NC}"
                    latency = f"{Colors.RED}N/A{Colors.NC}"
                    note = "配置错误"
                else:
                    success, latency_ms = self._test_tcp_connection(server, port, timeout=10)
                    
                    if success:
                        if latency_ms < 100:
                            status = f"{Colors.GREEN}优秀{Colors.NC}"
                            latency = f"{Colors.GREEN}{latency_ms}ms{Colors.NC}"
                        elif latency_ms < 300:
                            status = f"{Colors.YELLOW}良好{Colors.NC}"
                            latency = f"{Colors.YELLOW}{latency_ms}ms{Colors.NC}"
                        else:
                            status = f"{Colors.RED}较慢{Colors.NC}"
                            latency = f"{Colors.RED}{latency_ms}ms{Colors.NC}"
                        note = f"{server}:{port}"
                    else:
                        status = f"{Colors.RED}离线{Colors.NC}"
                        latency = f"{Colors.RED}超时{Colors.NC}"
                        note = "连接失败"
                        
                # 记录结果用于排序
                results.append((latency_ms if success else 9999, test_node_id, name, node_type))
            else:
                status = f"{Colors.YELLOW}未知{Colors.NC}"
                latency = f"{Colors.YELLOW}N/A{Colors.NC}"
                note = "未知类型"
            
            print(f"{name:<25} {node_type:<12} {status:<15} {latency:<15} {note}")
        
        print("-" * 80)
        
        # 显示最快的节点推荐
        if results:
            # 按延迟排序
            results.sort(key=lambda x: x[0])
            fastest = results[0]
            if fastest[0] < 9999:  # 有成功的连接
                print(f"{Colors.GREEN}🏆 推荐最快节点: {fastest[2]} ({fastest[0]}ms){Colors.NC}")
                return fastest[1]  # 返回最快节点ID
        
        return None
    
    def speed_test_single_node(self, node_info: Dict, node_id: str) -> Dict:
        """测试单个节点的速度"""
        name = node_info.get('name', node_id)
        node_type = node_info.get('type', 'unknown')
        config_data = node_info.get('config', {})
        
        result = {
            'node_id': node_id,
            'name': name,
            'type': node_type,
            'status': 'unknown',
            'latency': None,
            'country': '未知'
        }
        
        if node_type in ['local_server', 'local_client']:
            if node_type == 'local_server':
                port = config_data.get('listen_port', 5566)
                if self._is_port_in_use(port):
                    result['status'] = 'online'
                    result['latency'] = 1  # 本地连接延迟
                    result['country'] = '本地'
                else:
                    result['status'] = 'offline'
            else:
                server = config_data.get('server', '127.0.0.1')
                port = config_data.get('port', 5566)
                success, latency = self._test_tcp_connection(server, port)
                if success:
                    result['status'] = 'online'
                    result['latency'] = latency
                    result['country'] = '本地'
                else:
                    result['status'] = 'offline'
                    
        elif node_type in ['trojan', 'vless', 'shadowsocks', 'vmess', 'hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
            server = config_data.get('server', '')
            port = config_data.get('port', 443)
            
            if not server:
                result['status'] = 'error'
                return result
            
            # 测试连接
            success, latency = self._test_tcp_connection(server, port, timeout=10)
            if success:
                result['status'] = 'online'
                result['latency'] = latency
                result['country'] = self._get_server_country(server)
            else:
                result['status'] = 'offline'
        
        return result
    
    def test_node_speed_and_country(self, node_info: dict) -> tuple:
        """测试节点速度和国别"""
        config = node_info.get('config', {})
        server = config.get('server', config.get('address'))
        port = config.get('port', config.get('listen_port'))
        
        if not server or not port:
            return '本地', 'N/A'
        
        # 测试延迟
        try:
            latency = self._ping_test(server, timeout=5)
            if latency is None:
                latency = 'timeout'
        except Exception:
            latency = '待测试'
        
        # 获取国别信息
        country = self._get_server_country(server)
        
        return country, latency
    
    def _test_tcp_connection(self, server: str, port: int, timeout: int = 5) -> tuple:
        """测试TCP连接"""
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((server, port))
            
            end_time = time.time()
            latency = int((end_time - start_time) * 1000)  # 转换为毫秒
            
            sock.close()
            
            if result == 0:
                return True, latency
            else:
                return False, latency
                
        except socket.timeout:
            return False, timeout * 1000
        except socket.gaierror:
            # DNS解析失败
            return False, None
        except Exception:
            return False, None
    
    def _test_https_connection(self, server: str, port: int, timeout: int = 5) -> tuple:
        """测试HTTPS连接（用于WebSocket节点）"""
        try:
            import ssl
            
            start_time = time.time()
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 创建socket并连接
            sock = socket.create_connection((server, port), timeout=timeout)
            
            # 包装为SSL socket
            ssock = context.wrap_socket(sock, server_hostname=server)
            
            # 发送简单的HTTP请求
            request = f"GET / HTTP/1.1\r\nHost: {server}\r\nConnection: close\r\n\r\n"
            ssock.send(request.encode())
            
            # 读取响应头（只读前几个字节即可）
            response = ssock.recv(1024)
            
            end_time = time.time()
            latency = int((end_time - start_time) * 1000)  # 转换为毫秒
            
            ssock.close()
            
            # 检查是否收到有效的HTTP响应
            if response and (b'HTTP/' in response or b'404' in response or b'200' in response):
                return True, latency
            else:
                return False, latency
                
        except socket.timeout:
            return False, timeout * 1000
        except socket.gaierror:
            # DNS解析失败
            return False, None
        except Exception:
            return False, None
    
    def _ping_test(self, server: str, timeout: int = 5) -> int:
        """使用ping命令测试服务器延迟"""
        try:
            import platform
            import re
            
            # 根据操作系统选择ping命令参数
            os_type = platform.system()
            if os_type == "Windows":
                # Windows: ping -n 1 -w 超时时间(毫秒)
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), server]
            else:
                # macOS/Linux: ping -c 1 -W 超时时间(秒)
                cmd = ["ping", "-c", "1", "-W", str(timeout), server]
            
            # 执行ping命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 2  # 给subprocess额外的超时时间
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # 解析ping输出获取延迟时间
                if os_type == "Windows":
                    # Windows输出格式: "时间=XXXms" 或 "time=XXXms"
                    match = re.search(r'[时间|time]=(\d+)ms', output, re.IGNORECASE)
                    if match:
                        latency = float(match.group(1))
                        return int(latency)
                else:
                    # macOS/Linux输出格式: "time=XX.X ms" 或 "round-trip min/avg/max = XX/XX/XX"
                    match = re.search(r'time=(\d+\.?\d*)\s*ms', output, re.IGNORECASE)
                    if match:
                        latency = float(match.group(1))
                        return int(latency)
                    
                    # 尝试解析round-trip格式
                    match = re.search(r'round-trip.*?=\s*(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)', output, re.IGNORECASE)
                    if match:
                        # 使用平均值（第二个数值）
                        latency = float(match.group(2))
                        return int(latency)
                
                # 如果无法解析延迟，但ping成功，返回一个估计值
                return 100  # 默认100ms
            else:
                # ping失败
                return None
                
        except subprocess.TimeoutExpired:
            # ping超时
            return None
        except Exception:
            # 其他错误
            return None
    
    def _get_server_country(self, server: str) -> str:
        """获取服务器国别信息"""
        try:
            # 简单的国家判断逻辑，基于域名或IP
            if not server:
                return '本地'
            
            # 本地地址
            if server in ['localhost', '127.0.0.1', '::1'] or server.startswith('192.168.') or server.startswith('10.'):
                return '本地'
            
            # 使用IP地理位置查询API
            try:
                # 使用ip-api.com (免费且可靠)
                response = requests.get(f"http://ip-api.com/json/{server}?fields=country,status", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        country = data.get('country', '')
                        if country and country.strip():
                            return country.strip()
            except Exception:
                pass
            
            # 如果API失败，根据域名后缀简单判断
            if '.' in server:
                tld = server.split('.')[-1].lower()
                tld_map = {
                    'cn': '中国', 'jp': '日本', 'kr': '韩国', 'sg': '新加坡',
                    'hk': '香港', 'tw': '台湾', 'us': '美国', 'uk': '英国',
                    'de': '德国', 'fr': '法国', 'ca': '加拿大', 'au': '澳大利亚',
                    'nl': '荷兰', 'ru': '俄罗斯', 'br': '巴西', 'in': '印度'
                }
                country = tld_map.get(tld)
                if country:
                    return country
            
            return '未知'
        except Exception:
            return '未知'
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def batch_test_nodes(self, nodes: Dict, max_workers: int = 5) -> Dict[str, Dict]:
        """批量测试节点"""
        results = {}
        
        def test_single(node_item):
            node_id, node_info = node_item
            return node_id, self.speed_test_single_node(node_info, node_id)
        
        # 使用线程池并发测试
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {
                executor.submit(test_single, item): item[0] 
                for item in nodes.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_node):
                try:
                    node_id, result = future.result()
                    results[node_id] = result
                except Exception as e:
                    node_id = future_to_node[future]
                    results[node_id] = {
                        'node_id': node_id,
                        'status': 'error',
                        'error': str(e)
                    }
        
        return results 