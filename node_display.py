"""
节点显示模块
Node Display Module
"""

import time
import json
from typing import Dict
from pathlib import Path
from utils import Logger
from rich_menu import RichMenu


class NodeDisplay:
    """节点显示器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.rich_menu = RichMenu()
    
    def show_nodes_table(self, nodes: Dict, current_node: str, cache_data: Dict, refreshing_node: str = None):
        """显示节点表格"""
        # 准备表格数据
        headers = ["状态", "节点ID", "节点名称", "协议", "国别", "延迟", "配置状态"]
        rows = []
        
        for node_id, node_info in nodes.items():
            name = node_info.get('name', node_id)
            node_type = node_info.get('type', 'unknown')
            
            # 状态标识
            if node_id == current_node:
                status_style = "[green]●[/green]"  # 当前活动节点 - 绿点
            elif node_id == refreshing_node:
                status_style = "[yellow]●[/yellow]"  # 正在刷新的节点 - 黄点
            else:
                status_style = "[white]○[/white]"  # 其他节点 - 白圈
            
            # 从缓存获取或设置默认值
            cache_key = self._get_cache_key(node_info)
            cached_info = cache_data.get(cache_key, {})
            cache_expired = self._is_cache_expired(cached_info.get('timestamp'))
            
            if not cache_expired and cached_info:
                # 使用缓存数据
                country = cached_info.get('country', '未知')
                latency = cached_info.get('latency', 'N/A')
                country_emoji = self._get_country_flag(country)
                
                if isinstance(latency, (int, float)):
                    if latency < 100:
                        latency_str = f"[green]{latency}ms[/green]"
                    elif latency < 300:
                        latency_str = f"[yellow]{latency}ms[/yellow]"
                    else:
                        latency_str = f"[red]{latency}ms[/red]"
                else:
                    latency_str = f"[red]{latency}[/red]"
            else:
                # 显示待测试状态
                country_emoji = "🔍testing"
                latency_str = "[yellow]待测试[/yellow]"
            
            # 检查单个节点配置状态
            config_status = self._get_node_config_status(node_info)
            if config_status['valid']:
                config_status_str = "[green]✓ 有效[/green]"
            else:
                config_status_str = "[red]✗ 错误[/red]"
            
            rows.append([
                status_style,
                node_id,
                name,
                node_type,
                country_emoji,
                latency_str,
                config_status_str
            ])
        
        # 显示表格
        print()
        self.rich_menu.show_table("📡 节点列表", headers, rows, styles={
            "节点ID": "cyan",
            "节点名称": "blue",
            "协议": "magenta"
        })
        
        print()
        if refreshing_node:
            self.rich_menu.print_info("● = 当前节点  ● = 正在刷新  ○ = 其他节点")
        else:
            self.rich_menu.print_info("● = 当前节点  ○ = 其他节点")
        if current_node:
            self.rich_menu.print_success(f"当前活动节点: {current_node}")
        else:
            self.rich_menu.print_warning("当前活动节点: 无节点")
    
    def show_node_details(self, node_info: Dict, node_id: str):
        """显示单个节点的详细信息"""
        name = node_info.get('name', node_id)
        node_type = node_info.get('type', 'unknown')
        config = node_info.get('config', {})
        
        print()
        self.rich_menu.print_info(f"📋 节点详情: {name}")
        print()
        
        # 基本信息
        basic_info = [
            ["节点ID", node_id],
            ["节点名称", name],
            ["协议类型", node_type],
            ["创建时间", config.get('created_at', '未知')]
        ]
        
        self.rich_menu.show_table("基本信息", ["属性", "值"], basic_info)
        
        # 连接信息
        if node_type in ['trojan', 'vless', 'vmess', 'shadowsocks', 'hysteria2', 'tuic', 'reality', 'shadowtls', 'wireguard', 'hysteria']:
            server = config.get('server', 'N/A')
            port = config.get('port', 'N/A')
            
            connection_info = [
                ["服务器地址", server],
                ["端口", str(port)]
            ]
            
            # 根据协议类型添加特定信息
            if node_type == 'trojan':
                connection_info.extend([
                    ["密码", "●●●●●●" if config.get('password') else 'N/A'],
                    ["TLS", "是" if config.get('tls', {}).get('enabled') else "否"],
                    ["SNI", config.get('tls', {}).get('server_name', 'N/A')]
                ])
            elif node_type in ['vless', 'vmess']:
                connection_info.extend([
                    ["UUID", config.get('uuid', 'N/A')],
                    ["TLS", "是" if config.get('tls', {}).get('enabled') else "否"]
                ])
            elif node_type == 'shadowsocks':
                connection_info.extend([
                    ["密码", "●●●●●●" if config.get('password') else 'N/A'],
                    ["加密方式", config.get('method', 'N/A')]
                ])
            
            self.rich_menu.show_table("连接信息", ["属性", "值"], connection_info)
        
        # 传输信息
        transport = config.get('transport')
        if transport:
            transport_info = [
                ["传输类型", transport.get('type', 'N/A')]
            ]
            
            if transport.get('type') == 'ws':
                transport_info.extend([
                    ["WebSocket路径", transport.get('path', 'N/A')],
                    ["Host头", transport.get('headers', {}).get('Host', 'N/A')]
                ])
            
            self.rich_menu.show_table("传输信息", ["属性", "值"], transport_info)
    
    def _get_cache_key(self, node_info: dict) -> str:
        """生成缓存键"""
        config = node_info.get('config', {})
        server = config.get('server', config.get('address', 'localhost'))
        port = config.get('port', config.get('listen_port', 0))
        return f"{server}:{port}"
    
    def _is_cache_expired(self, timestamp: float, expiry_hours: int = 6) -> bool:
        """检查缓存是否过期"""
        if not timestamp:
            return True
        return time.time() - timestamp > expiry_hours * 3600
    
    def _get_country_flag(self, country: str) -> str:
        """获取国家对应的代码+emoji标志"""
        country_map = {
            # 中文国家名称
            '中国': ('cn', '🇨🇳'),
            '香港': ('hk', '🇭🇰'), 
            '台湾': ('tw', '🇹🇼'), 
            '澳门': ('mo', '🇲🇴'),
            '日本': ('jp', '🇯🇵'), 
            '韩国': ('kr', '🇰🇷'), 
            '新加坡': ('sg', '🇸🇬'), 
            '马来西亚': ('my', '🇲🇾'),
            '美国': ('us', '🇺🇸'), 
            '加拿大': ('ca', '🇨🇦'), 
            '英国': ('uk', '🇬🇧'), 
            '德国': ('de', '🇩🇪'),
            '法国': ('fr', '🇫🇷'), 
            '荷兰': ('nl', '🇳🇱'), 
            '俄罗斯': ('ru', '🇷🇺'), 
            '澳大利亚': ('au', '🇦🇺'),
            '印度': ('in', '🇮🇳'),
            '巴西': ('br', '🇧🇷'),
            '意大利': ('it', '🇮🇹'),
            '西班牙': ('es', '🇪🇸'),
            '瑞士': ('ch', '🇨🇭'),
            '瑞典': ('se', '🇸🇪'),
            '挪威': ('no', '🇳🇴'),
            '芬兰': ('fi', '🇫🇮'),
            '丹麦': ('dk', '🇩🇰'),
            '波兰': ('pl', '🇵🇱'),
            '捷克': ('cz', '🇨🇿'),
            '奥地利': ('at', '🇦🇹'),
            '比利时': ('be', '🇧🇪'),
            '爱尔兰': ('ie', '🇮🇪'),
            '葡萄牙': ('pt', '🇵🇹'),
            '希腊': ('gr', '🇬🇷'),
            '土耳其': ('tr', '🇹🇷'),
            '以色列': ('il', '🇮🇱'),
            '阿联酋': ('ae', '🇦🇪'),
            '沙特阿拉伯': ('sa', '🇸🇦'),
            '南非': ('za', '🇿🇦'),
            '埃及': ('eg', '🇪🇬'),
            '泰国': ('th', '🇹🇭'),
            '印度尼西亚': ('id', '🇮🇩'),
            '菲律宾': ('ph', '🇵🇭'),
            '越南': ('vn', '🇻🇳'),
            
            # 英文国家名称（API返回的格式）
            'China': ('cn', '🇨🇳'),
            'Hong Kong': ('hk', '🇭🇰'),
            'Taiwan': ('tw', '🇹🇼'),
            'Macau': ('mo', '🇲🇴'),
            'Japan': ('jp', '🇯🇵'),
            'South Korea': ('kr', '🇰🇷'),
            'Singapore': ('sg', '🇸🇬'),
            'Malaysia': ('my', '🇲🇾'),
            'United States': ('us', '🇺🇸'),
            'Canada': ('ca', '🇨🇦'),
            'United Kingdom': ('uk', '🇬🇧'),
            'Germany': ('de', '🇩🇪'),
            'France': ('fr', '🇫🇷'),
            'Netherlands': ('nl', '🇳🇱'),
            'Russia': ('ru', '🇷🇺'),
            'Australia': ('au', '🇦🇺'),
            'India': ('in', '🇮🇳'),
            'Brazil': ('br', '🇧🇷'),
            'Italy': ('it', '🇮🇹'),
            'Spain': ('es', '🇪🇸'),
            'Switzerland': ('ch', '🇨🇭'),
            'Sweden': ('se', '🇸🇪'),
            'Norway': ('no', '🇳🇴'),
            'Finland': ('fi', '🇫🇮'),
            'Denmark': ('dk', '🇩🇰'),
            'Poland': ('pl', '🇵🇱'),
            'Czech Republic': ('cz', '🇨🇿'),
            'Austria': ('at', '🇦🇹'),
            'Belgium': ('be', '🇧🇪'),
            'Ireland': ('ie', '🇮🇪'),
            'Portugal': ('pt', '🇵🇹'),
            'Greece': ('gr', '🇬🇷'),
            'Turkey': ('tr', '🇹🇷'),
            'Israel': ('il', '🇮🇱'),
            'United Arab Emirates': ('ae', '🇦🇪'),
            'Saudi Arabia': ('sa', '🇸🇦'),
            'South Africa': ('za', '🇿🇦'),
            'Egypt': ('eg', '🇪🇬'),
            'Thailand': ('th', '🇹🇭'),
            'Indonesia': ('id', '🇮🇩'),
            'Philippines': ('ph', '🇵🇭'),
            'Vietnam': ('vn', '🇻🇳'),
            
            # 特殊状态
            '本地': ('local', '🏠'),
            '未知': ('na', '🌐')
        }
        
        code, emoji = country_map.get(country, ('na', '🌐'))
        return f"{code}{emoji}"
    
    def _get_node_config_status(self, node_info: Dict) -> Dict:
        """获取节点配置状态 (简化版本)"""
        try:
            node_type = node_info.get('type', '')
            config = node_info.get('config', {})
            
            if not node_type or not config:
                return {'valid': False, 'error': '配置不完整'}
            
            # 基本检查
            if node_type in ['trojan', 'vless', 'vmess', 'shadowsocks']:
                if not config.get('server') or not config.get('port'):
                    return {'valid': False, 'error': '缺少服务器或端口'}
            
            return {'valid': True, 'error': None}
        except:
            return {'valid': False, 'error': '配置解析错误'} 