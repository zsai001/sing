#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich_menu import RichMenu

def test_menu():
    menu = RichMenu()
    
    # 清屏并显示banner
    menu.clear()
    menu.show_banner("测试菜单", "验证默认回车选择0功能")
    
    # 显示测试菜单
    test_items = [
        ("1", "选项1", "这是选项1"),
        ("2", "选项2", "这是选项2"),
        ("3", "选项3", "这是选项3")
    ]
    
    menu.show_menu("测试菜单", test_items, exit_text="0. 🔙 退出测试")
    
    # 测试提示
    print("现在直接按回车应该会选择0（退出）")
    choice = menu.prompt_choice("请选择 [0-3]")
    
    print(f"您选择了: '{choice}'")
    
    if choice == "0":
        print("✓ 默认回车选择0功能正常工作！")
    else:
        print(f"您选择了选项 {choice}")

if __name__ == "__main__":
    test_menu() 