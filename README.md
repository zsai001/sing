# SingTool - sing-box 管理工具

专为 macOS 优化的 sing-box 管理脚本，Python版本提供更好的跨平台兼容性和模块化设计。

## ✨ 功能特色

- 🎯 **Python实现**: 跨平台兼容性
- 🔧 **模块化设计**: 清晰的代码结构  
- 🧙‍♂️ **友好界面**: 直观的菜单系统
- 📡 **多节点支持**: 本地服务器/客户端节点
- 🌐 **多协议支持**: Trojan, VLESS, Shadowsocks
- 🍎 **macOS优化**: 原生集成

## 🚀 快速开始

### 系统要求

- macOS 10.15+ 或 Linux
- Python 3.7+

### 安装运行

```bash
# 克隆项目
git clone git@github.com:zsai001/sing.git
cd sing

# 运行
python3 sing.py
```

## 📖 基本用法

```bash
# 交互式菜单
python3 sing.py

# 命令行模式
python3 sing.py status    # 查看状态
python3 sing.py nodes     # 节点管理
python3 sing.py install   # 完整安装
python3 sing.py help      # 显示帮助
```

## 📂 项目结构

```
sing/
├── sing.py           # 主程序入口
├── core.py           # 核心管理模块
├── nodes.py          # 节点管理模块
├── menu.py           # 菜单系统模块
├── service.py        # 服务管理模块
├── config.py         # 配置管理模块
├── paths.py          # 路径管理模块
├── utils.py          # 工具模块
└── README.md         # 项目说明
```

## 🌐 支持的协议

- **Trojan**: 高性能代理协议
- **VLESS**: V2Ray 新协议  
- **Shadowsocks**: 经典代理协议

## 📡 节点类型

### 远程节点
连接到远程代理服务器

### 本地节点 ⭐
- **本地服务器**: 在本机启动代理服务器，供其他设备连接
- **本地客户端**: 连接到本机其他端口的服务

## 🔧 配置文件

配置文件位置：`~/.config/sing-box/`

```
~/.config/sing-box/
├── nodes.json          # 节点配置
├── config.json         # sing-box主配置
└── backup/            # 自动备份目录
```

## 🛠️ 开发

项目采用模块化设计，可以轻松扩展功能。

## 📄 许可证

MIT License

## 💬 支持

如有问题或建议，请在GitHub创建Issue。 