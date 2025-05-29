#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rich菜单工具类 - 使用rich库实现自动对齐的菜单系统
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

class RichMenu:
    """基于rich的菜单系统"""
    
    def __init__(self):
        self.console = Console()
    
    def clear(self):
        """清屏"""
        self.console.clear()
    
    def show_banner(self, title="sing-box macOS 管理工具 v2.0", subtitle="Python 模块化版本"):
        """显示程序banner"""
        banner = f"[bold blue]{title}[/bold blue]"
        if subtitle:
            banner += f"\n[italic]{subtitle}[/italic]"
        
        self.console.print(Panel(banner, style="bold", border_style="blue"))
        self.console.print()
    
    def show_status(self, status_data):
        """显示状态信息
        
        Args:
            status_data: dict 状态数据，如 {"服务状态": "运行中", "代理端口": "7890"}
        """
        status_table = Table.grid(padding=1)
        status_table.add_column(style="cyan", no_wrap=True)
        status_table.add_column(style="white")
        
        for key, value in status_data.items():
            status_table.add_row(f"{key}:", value)
        
        status_panel = Panel(
            status_table,
            title="📊 当前状态",
            expand=False,
            border_style="cyan"
        )
        
        self.console.print(status_panel)
        self.console.print()
    
    def show_menu(self, title, items, show_exit=True, exit_text="0. 🚪 退出程序"):
        """显示菜单
        
        Args:
            title: str 菜单标题
            items: list 菜单项列表，格式: [(编号, 图标功能, 描述), ...]
            show_exit: bool 是否显示退出选项
            exit_text: str 退出选项文本
        """
        menu_table = Table.grid(padding=1)
        menu_table.add_column("编号", style="white", no_wrap=True, width=3)
        menu_table.add_column("功能", style="cyan", no_wrap=True, width=18)
        menu_table.add_column("描述", style="white")
        
        for item in items:
            if len(item) == 3:
                num, func, desc = item
                menu_table.add_row(f"{num}.", func, desc)
            elif len(item) == 2:
                num, func = item
                menu_table.add_row(f"{num}.", func, "")
        
        menu_panel = Panel(
            menu_table,
            title=title,
            expand=False,
            border_style="cyan"
        )
        
        self.console.print(menu_panel)
        self.console.print()
        
        if show_exit:
            self.console.print(f"  {exit_text}")
            self.console.print()
    
    def show_table(self, title, headers, rows, styles=None):
        """显示表格
        
        Args:
            title: str 表格标题
            headers: list 表头列表
            rows: list 行数据列表
            styles: dict 列样式，如 {"列名": "cyan"}
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for i, header in enumerate(headers):
            style = styles.get(header, "white") if styles else "white"
            table.add_column(header, style=style)
        
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)
        self.console.print()
    
    def show_info_box(self, title, content, style="blue"):
        """显示信息框"""
        self.console.print(Panel(content, title=title, border_style=style))
        self.console.print()
    
    def prompt_choice(self, prompt_text, choices=None, default=None):
        """提示用户选择
        
        Args:
            prompt_text: str 提示文本
            choices: list 可选项列表，如果为None则接受任何输入
            default: str 默认值，如果为None且提示文本包含[0-则自动设为"0"
            
        Returns:
            str 用户输入
        """
        # 自动检测是否应该设置默认值为"0"
        if default is None and ("[0-" in prompt_text or "[0]" in prompt_text):
            default = "0"
        
        if choices:
            return Prompt.ask(prompt_text, choices=choices, default=default)
        else:
            return Prompt.ask(prompt_text, default=default)
    
    def prompt_confirm(self, prompt_text, default=False):
        """提示用户确认
        
        Args:
            prompt_text: str 提示文本
            default: bool 默认值
            
        Returns:
            bool 用户确认结果
        """
        return Confirm.ask(prompt_text, default=default)
    
    def prompt_input(self, prompt_text, default=None):
        """提示用户输入
        
        Args:
            prompt_text: str 提示文本
            default: str 默认值
            
        Returns:
            str 用户输入
        """
        if default:
            display_text = f"{prompt_text} [{default}]"
        else:
            display_text = prompt_text
        return Prompt.ask(display_text, default=default)
    
    def print_success(self, message):
        """打印成功消息"""
        self.console.print(f"[green]✓[/green] {message}")
    
    def print_error(self, message):
        """打印错误消息"""
        self.console.print(f"[red]✗[/red] {message}")
    
    def print_warning(self, message):
        """打印警告消息"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
    
    def print_info(self, message):
        """打印信息消息"""
        self.console.print(f"[blue]ℹ[/blue] {message}")

# 使用示例
if __name__ == "__main__":
    menu = RichMenu()
    
    # 显示banner
    menu.clear()
    menu.show_banner()
    
    # 显示状态
    status = {
        "服务状态": "[green]运行中[/green]",
        "代理端口": "[green]7890[/green]",
        "当前节点": "[blue]ifx (trojan)[/blue]"
    }
    menu.show_status(status)
    
    # 显示主菜单
    main_items = [
        ("1", "🚀 快速操作", "一键测试、修复、配置向导"),
        ("2", "📡 节点管理", "添加、删除、切换、测速节点"),
        ("3", "🔀 分流管理", "路由规则、自定义规则配置"),
        ("4", "⚙️ 系统管理", "服务控制、配置、日志查看"),
        ("5", "🔧 高级配置", "端口、DNS、TUN、API设置"),
        ("6", "🛠️ 系统工具", "安装、卸载、诊断、帮助")
    ]
    
    menu.show_menu("🎯 主菜单 - 请选择功能分类", main_items)
    
    # 演示表格
    headers = ["节点名称", "类型", "状态", "延迟"]
    rows = [
        ["🇺🇸 美国节点", "Trojan", "[green]✓ 在线[/green]", "[green]45ms[/green]"],
        ["🇯🇵 日本节点", "VLESS", "[red]✗ 离线[/red]", "[red]timeout[/red]"],
        ["🇭🇰 香港节点", "SS", "[green]✓ 在线[/green]", "[yellow]120ms[/yellow]"]
    ]
    styles = {"节点名称": "cyan", "类型": "magenta"}
    
    input("按回车查看表格示例...")
    menu.show_table("节点状态", headers, rows, styles)
    
    # 演示消息
    menu.print_success("操作成功完成")
    menu.print_error("发生错误")
    menu.print_warning("这是一个警告")
    menu.print_info("这是一条信息") 