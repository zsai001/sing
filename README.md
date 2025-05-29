# SingTool - sing-box 管理工具 Python版

专为 macOS 优化的 sing-box 管理脚本，Python版本提供更好的跨平台兼容性和代码结构。

## ✨ 功能特色

- 🎯 **Python实现**: 更好的跨平台兼容性
- 🔧 **模块化设计**: 清晰的OOP代码结构  
- 🧙‍♂️ **友好界面**: 直观的菜单系统
- 📡 **多节点支持**: 本地服务器/客户端节点
- 🌐 **多协议支持**: Trojan, VLESS, VMess, Shadowsocks
- 🍎 **macOS优化**: 原生集成Homebrew和launchctl
- 📊 **智能管理**: 自动备份、配置验证

## 🚀 快速开始

### 系统要求

- macOS 10.15+ 或 Linux
- Python 3.7+
- 管理员权限（部分功能需要）

### 安装运行

```bash
# 克隆或下载项目
git clone <repository-url>
cd singtool

# 给脚本添加执行权限
chmod +x singtool.py

# 运行主菜单
python3 singtool.py
```

### 基本用法

```bash
# 显示交互式菜单
python3 singtool.py

# 查看节点列表
python3 singtool.py nodes

# 显示帮助
python3 singtool.py help
```

## 📡 节点管理

### 支持的节点类型

#### 远程节点
- **Trojan**: 高性能代理协议
- **VLESS**: V2Ray 新协议  
- **VMess**: V2Ray 经典协议
- **Shadowsocks**: 经典代理协议

#### 本地节点 ⭐ 新功能
- **本地服务器**: 在本机启动代理服务器，供其他设备连接
- **本地客户端**: 连接到本机其他端口的服务

### 本地节点使用场景

#### 🌐 本地服务器节点
```
用途: 为其他设备提供代理服务
配置: 可设置不同端口，互不冲突
协议: 支持 Trojan/VLESS
传输: 支持 TCP/WebSocket
示例: 端口5566供手机连接，端口5567供平板连接
```

#### 🔗 本地客户端节点  
```
用途: 连接到本机运行的其他代理服务
场景: 代理链、中转、本地服务整合
协议: 支持多种协议
示例: 连接本机1080端口的其他SOCKS5服务
```

## 🎯 使用示例

### 创建本地服务器节点
```bash
python3 singtool.py
# 选择: 6 → 6 → 输入节点信息
# 结果: 创建Trojan服务器供其他设备连接
```

### 创建本地客户端节点
```bash
python3 singtool.py  
# 选择: 6 → 7 → 输入服务器信息
# 结果: 连接到本机其他代理服务
```

### 混合使用方案
```
场景: 同时运行多个节点
- 服务器节点: 端口5566 (供手机用)
- 客户端节点: 连接VPS (供电脑用)  
- 优势: 互不冲突，灵活配置
```

## 📂 项目结构

```
singtool/
├── singtool.py          # 主程序入口
├── README.md           # 项目说明
├── demo.sh            # 功能演示脚本
└── sing.sh            # Bash版本(兼容)
```

## 🏗️ 代码架构

### 核心类

- **`SingToolManager`**: 主管理类，负责系统检测和初始化
- **`NodeManager`**: 节点管理类，处理节点CRUD操作
- **`PathManager`**: 路径管理类，跨平台路径处理
- **`MenuSystem`**: 菜单系统类，用户交互界面
- **`Logger`**: 日志类，统一日志输出

### 设计优势

- **类型提示**: 使用Python类型注解提高代码质量
- **异常处理**: 完善的错误处理机制
- **配置管理**: JSON配置文件自动备份
- **模块分离**: 清晰的模块职责分工

## 🔧 配置文件

### 文件位置
```
~/.config/sing-box/
├── nodes.json          # 节点配置
├── local_proxy.json    # 本地代理配置  
├── dns_rules.json      # DNS规则配置
├── config.json         # sing-box主配置
└── backup/            # 自动备份目录
```

### 节点配置格式
```json
{
  "version": "1.0",
  "current_node": null,
  "nodes": {
    "node_id": {
      "name": "节点名称",
      "type": "local_server|local_client|trojan|vless|vmess|shadowsocks",
      "protocol": "trojan|vless|shadowsocks",
      "enabled": true,
      "config": {
        "listen_port": 5566,
        "password": "密码",
        "created_at": "2024-01-01T00:00:00"
      }
    }
  }
}
```

## 🛠️ 开发

### 扩展功能
项目采用模块化设计，可以轻松扩展：

```python
# 添加新的节点类型
class NodeManager:
    def add_custom_node(self, node_id: str, node_name: str) -> bool:
        # 实现自定义节点逻辑
        pass

# 添加新的菜单选项  
class MenuSystem:
    def show_custom_menu(self):
        # 实现自定义菜单
        pass
```

### 贡献代码
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📋 待办事项

- [ ] 远程节点配置功能
- [ ] 订阅链接导入
- [ ] 服务管理功能
- [ ] 配置文件生成
- [ ] 连接测试功能
- [ ] 性能监控
- [ ] GUI界面

## 🆚 版本对比

| 功能 | Bash版本 | Python版本 |
|------|----------|------------|
| 跨平台兼容性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 代码可维护性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| JSON处理 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 错误处理 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 功能完整性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 启动速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 💬 支持

如有问题或建议，请创建 Issue 或联系维护者。 

# SingTool 模块化重构总结

## 📁 文件结构概览

重构后的项目将原来的 2400+ 行单文件拆分为 7 个模块化文件：

```
singtool/
├── utils.py           # 通用工具模块
├── paths.py           # 路径管理模块  
├── service.py         # 服务管理模块
├── config.py          # 配置管理模块
├── nodes.py           # 节点管理模块
├── menu.py            # 菜单系统模块
├── core.py            # 核心管理模块
├── singtool_new.py    # 新的主入口文件
└── README.md          # 项目文档
```

## 📋 各文件功能详细说明

### 🔧 `utils.py` - 通用工具模块 (35 行)

**功能**: 提供基础工具类和颜色定义

**包含的类和函数**:
- `Colors` 类: 终端颜色常量定义
  - `RED`, `GREEN`, `YELLOW`, `BLUE`, `PURPLE`, `CYAN`, `NC`
- `Logger` 类: 日志输出管理
  - `info(message)`: 显示信息日志
  - `warn(message)`: 显示警告日志
  - `error(message)`: 显示错误日志
  - `step(message)`: 显示步骤日志

### 🗂️ `paths.py` - 路径管理模块 (47 行)

**功能**: 处理跨平台路径配置和文件路径管理

**包含的类和函数**:
- `PathManager` 类: 路径管理器
  - `__init__()`: 初始化路径配置
  - `_setup_paths()`: 设置平台特定路径
  - 属性: `config_dir`, `log_dir`, `nodes_dir`, `main_config`, `nodes_config` 等

### ⚙️ `service.py` - 服务管理模块 (310 行)

**功能**: 负责 sing-box 服务的安装、启动、停止、日志查看等操作

**包含的类和函数**:
- `ServiceManager` 类: 服务管理器
  - `detect_os()`: 检测操作系统
  - `check_homebrew()`: 检查 Homebrew 安装状态
  - `install_homebrew()`: 安装 Homebrew
  - `check_singbox_installed()`: 检查 sing-box 安装状态
  - `install_singbox()`: 安装 sing-box
  - `create_service()`: 创建系统服务
  - `_create_macos_service()`: 创建 macOS 服务
  - `_create_linux_service()`: 创建 Linux 服务
  - `check_service_status()`: 检查服务状态
  - `start_service()`: 启动服务
  - `stop_service()`: 停止服务
  - `restart_service()`: 重启服务
  - `is_port_listening(port)`: 检查端口监听状态
  - `view_logs()`: 查看日志
  - `uninstall()`: 卸载系统

### 📝 `config.py` - 配置管理模块 (350 行)

**功能**: 负责 sing-box 配置文件的生成、管理和验证

**包含的类和函数**:
- `ConfigManager` 类: 配置管理器
  - `ensure_config_directories()`: 确保配置目录存在
  - `generate_local_proxy_config(selected_nodes)`: 生成本地代理配置
  - `generate_local_server_config(server_type, config_data)`: 生成本地服务器配置
  - `_generate_trojan_server_config(config_data)`: 生成 Trojan 服务器配置
  - `_generate_shadowsocks_server_config(config_data)`: 生成 Shadowsocks 服务器配置
  - `_generate_vless_server_config(config_data)`: 生成 VLESS 服务器配置
  - `save_config(config, config_path)`: 保存配置文件
  - `backup_config(config_path)`: 备份配置文件
  - `load_config(config_path)`: 加载配置文件
  - `validate_config(config)`: 验证配置文件格式
  - `get_local_ip()`: 获取本机 IP 地址

### 📡 `nodes.py` - 节点管理模块 (550 行)

**功能**: 负责节点的增删改查、连接测试和节点类型管理

**包含的类和函数**:
- `NodeManager` 类: 节点管理器
  - `init_nodes_config()`: 初始化节点配置
  - `load_nodes_config()`: 加载节点配置
  - `save_nodes_config(config)`: 保存节点配置
  - `show_nodes()`: 显示节点列表
  - `add_local_server_node(node_id, node_name)`: 添加本地服务器节点
  - `add_local_client_node(node_id, node_name)`: 添加本地客户端节点
  - `_is_port_in_use(port)`: 检查端口占用
  - `switch_node(target_node_id)`: 切换节点
  - `delete_node(node_id)`: 删除节点
  - `add_trojan_node(node_id, node_name)`: 添加 Trojan 节点
  - `add_vless_node(node_id, node_name)`: 添加 VLESS 节点
  - `add_shadowsocks_node(node_id, node_name)`: 添加 Shadowsocks 节点
  - `test_node_connectivity(node_id)`: 测试节点连通性
  - `_test_tcp_connection(host, port, timeout)`: 测试 TCP 连接

### 🖥️ `menu.py` - 菜单系统模块 (420 行)

**功能**: 提供交互式用户界面和菜单操作

**包含的类和函数**:
- `MenuSystem` 类: 菜单系统
  - `show_main_menu()`: 显示主菜单
  - `_show_status_overview()`: 显示状态概览
  - `_quick_test()`: 快速测试连接
  - `_quick_fix()`: 一键修复问题
  - `_config_wizard()`: 配置向导
  - `_add_remote_node_menu()`: 添加远程节点菜单
  - `_add_local_node_menu()`: 添加本地节点菜单
  - `_show_local_server_usage_info(node_id)`: 显示本地服务器使用说明
  - `_switch_node_menu()`: 切换节点菜单
  - `_delete_node_menu()`: 删除节点菜单
  - `_start_restart_service()`: 启动/重启服务
  - `_advanced_config_menu()`: 高级配置菜单
  - `_install_menu()`: 安装菜单
  - `_diagnostic_menu()`: 诊断菜单
  - `show_help()`: 显示帮助信息

### 🎯 `core.py` - 核心管理模块 (420 行)

**功能**: 协调各个子模块，提供统一的管理接口

**包含的类和函数**:
- `SingToolManager` 类: 核心管理器
  - `__init__()`: 初始化所有子模块
  - `_ensure_directories()`: 确保目录存在
  - `show_banner()`: 显示横幅
  - `detect_os()`: 系统检测（委托给 ServiceManager）
  - `check_homebrew()`: Homebrew 检查（委托给 ServiceManager）
  - `install_singbox()`: 安装 sing-box（委托给 ServiceManager）
  - `create_service()`: 创建服务（委托给 ServiceManager）
  - `start_service()`, `stop_service()`, `restart_service()`: 服务控制
  - `show_status()`: 显示详细状态信息
  - `_check_port_status()`: 检查端口状态
  - `_show_system_info()`: 显示系统信息
  - `create_main_config()`: 创建主配置文件
  - `_generate_basic_config()`: 生成基础配置
  - `_generate_local_client_config(node_info)`: 生成本地客户端配置
  - `init_local_config()`: 初始化本地配置
  - `full_install()`: 完整安装流程
  - `_show_connection_info()`: 显示连接信息

### 🚀 `singtool_new.py` - 主入口文件 (85 行)

**功能**: 程序入口点，协调所有模块工作

**包含的函数**:
- `main()`: 主函数
  - 初始化核心管理器
  - 处理命令行参数
  - 启动交互式菜单
  - 异常处理

## 🔄 模块间依赖关系

```
singtool_new.py (主入口)
    │
    ├── core.py (核心管理)
    │   ├── utils.py (工具类)
    │   ├── paths.py (路径管理)
    │   ├── config.py (配置管理)
    │   └── service.py (服务管理)
    │
    ├── nodes.py (节点管理)
    │   ├── utils.py
    │   └── paths.py
    │
    └── menu.py (菜单系统)
        └── utils.py
```

## ✨ 重构优势

1. **🎯 单一职责**: 每个模块只负责特定功能
2. **🔧 易于维护**: 代码分离，便于定位和修改
3. **📈 可扩展性**: 新功能可以独立添加到相应模块
4. **🧪 便于测试**: 每个模块可以独立测试
5. **📚 代码重用**: 模块可以在其他项目中重用
6. **👥 团队协作**: 不同开发者可以并行开发不同模块

## 🛠️ 使用方法

```bash
# 使用新的模块化版本
python singtool_new.py

# 命令行模式
python singtool_new.py status    # 查看状态
python singtool_new.py nodes     # 节点管理
python singtool_new.py install   # 完整安装
```

## 📊 重构数据对比

| 指标 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| 单文件行数 | 2,469 行 | 最大 550 行 | ✓ 可读性大幅提升 |
| 文件数量 | 1 个 | 8 个 | ✓ 功能模块化 |
| 类的职责 | 混合 | 单一 | ✓ 符合设计原则 |
| 代码重用性 | 低 | 高 | ✓ 模块独立 |
| 维护难度 | 高 | 低 | ✓ 问题定位容易 |

这种模块化设计使得代码更加清晰、易维护，并且为未来的功能扩展奠定了良好的基础。 