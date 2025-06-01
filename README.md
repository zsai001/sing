# SingTool - sing-box 管理工具

一个用于管理 sing-box 的现代化命令行工具，支持 macOS 和 Linux 系统。

## ✨ 特性

- 🎯 **简单易用** - 提供交互式菜单和命令行两种使用方式
- 🔧 **自动化安装** - 一键安装脚本，自动配置环境和依赖
- 📦 **虚拟环境** - 独立的Python环境，不污染系统
- 🚀 **服务管理** - 完整的启动、停止、重启功能
- 📊 **状态监控** - 实时查看服务状态和系统信息
- 🌐 **节点管理** - 支持多种代理协议和节点配置
- 📝 **日志查看** - 便捷的日志管理和查看功能
- 🔄 **配置管理** - 自动生成和管理配置文件

## 🚀 快速安装

### 一键安装（推荐）

```bash
# 方法1: 克隆仓库安装
git clone https://github.com/your-username/singtool.git
cd singtool
./install.sh

# 方法2: 在线安装（即将支持）
curl -fsSL https://raw.githubusercontent.com/your-username/singtool/main/quick-install.sh | bash
```

### 安装过程

安装脚本会自动完成：
- ✅ 检测系统环境（macOS/Linux）
- ✅ 验证Python 3.8+环境
- ✅ 安装系统依赖（Homebrew、sing-box等）
- ✅ 创建独立的Python虚拟环境
- ✅ 安装所需的Python包
- ✅ 复制程序文件到系统目录
- ✅ 创建全局命令`singtool`

## 📖 使用方法

### 交互式菜单
```bash
singtool
```

### 命令行模式
```bash
singtool install        # 安装和配置sing-box
singtool status         # 查看详细状态
singtool start          # 启动服务
singtool stop           # 停止服务
singtool restart        # 重启服务
singtool nodes          # 节点管理
singtool logs           # 查看日志
singtool config         # 重新生成配置
singtool test           # 测试节点连通性
singtool uninstall      # 卸载sing-box
singtool help           # 显示帮助
```

## 📂 安装位置

- **程序目录**: `/usr/local/singtool/`
- **虚拟环境**: `/usr/local/singtool/venv/`
- **启动脚本**: `/usr/local/bin/singtool`
- **配置目录**: `~/.config/sing-box/`
- **日志目录**: `~/.local/share/sing-box/logs/`

## ⚙️ 系统要求

- **操作系统**: macOS 10.15+ 或 Linux
- **Python**: 3.8 或更高版本
- **权限**: 能够使用sudo（安装系统组件需要）
- **网络**: 能够访问GitHub和Homebrew（macOS）

## 🛠️ 手动安装

如果您想手动安装或开发：

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/singtool.git
cd singtool

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 直接运行
python3 sing.py
```

## 🗑️ 卸载

### 卸载工具
```bash
./install.sh uninstall
```

### 完全清理
```bash
# 卸载工具和配置
./install.sh uninstall

# 手动删除配置（可选）
rm -rf ~/.config/sing-box
rm -rf ~/.local/share/sing-box
```

## 🔧 故障排除

### Python版本问题
```bash
python3 --version  # 检查版本
brew install python3  # macOS升级
```

### 依赖包问题
```bash
pip3 install rich requests PyYAML
```

### sing-box未找到
```bash
# macOS
brew tap sagernet/sing-box
brew install sing-box
```

### 权限问题
```bash
sudo -v  # 检查sudo权限
```

详细的故障排除指南请参阅 [INSTALL.md](INSTALL.md)

## 📚 文档

- [安装指南](INSTALL.md) - 详细的安装步骤和故障排除
- [使用手册](#) - 完整的功能说明和使用示例
- [配置指南](#) - 节点配置和高级设置

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [sing-box](https://github.com/SagerNet/sing-box) - 强大的代理工具
- [rich](https://github.com/Textualize/rich) - 美观的终端输出
- 所有贡献者和用户的支持

---

⭐ 如果这个项目对您有帮助，请给它一个星标！ 