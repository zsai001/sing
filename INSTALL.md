# SingTool 安装指南

SingTool 是一个用于管理 sing-box 的命令行工具，支持 macOS 和 Linux 系统。

## 快速安装

### 自动安装（推荐）

1. **下载安装脚本并运行：**
   ```bash
   # 克隆仓库
   git clone <repository-url>
   cd singtool
   
   # 运行安装脚本
   ./install.sh
   ```

2. **或者一键安装：**
   ```bash
   curl -fsSL <install-script-url> | bash
   ```

### 安装过程说明

安装脚本会自动完成以下步骤：

1. ✅ **检测系统环境** - 确认操作系统和架构
2. ✅ **检查Python环境** - 确保Python 3.8+已安装
3. ✅ **安装系统依赖** - 自动安装Homebrew（macOS）和sing-box
4. ✅ **创建虚拟环境** - 在`/usr/local/singtool/venv`创建独立的Python环境
5. ✅ **安装Python依赖** - 安装rich、requests、PyYAML等必要包
6. ✅ **复制程序文件** - 将所有Python模块复制到安装目录
7. ✅ **创建启动脚本** - 在`/usr/local/bin/singtool`创建全局命令

## 手动安装

如果你想手动安装，可以按照以下步骤：

### 1. 环境要求

- **操作系统**: macOS 10.15+ 或 Linux
- **Python**: 3.8 或更高版本
- **权限**: 能够使用sudo（安装到系统目录需要）

### 2. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装sing-box

**macOS (使用Homebrew):**
```bash
brew tap sagernet/sing-box
brew install sing-box
```

**Linux:**
```bash
# 请参考 sing-box 官方文档安装
```

### 4. 运行工具

```bash
# 直接运行
python3 sing.py

# 或者创建符号链接
sudo ln -sf $(pwd)/sing.py /usr/local/bin/singtool
singtool
```

## 使用方法

安装完成后，你可以通过以下方式使用 SingTool：

### 交互式菜单
```bash
singtool
```

### 命令行模式
```bash
singtool install        # 安装和配置sing-box
singtool status         # 查看状态
singtool start          # 启动服务
singtool stop           # 停止服务
singtool restart        # 重启服务
singtool nodes          # 管理节点
singtool logs           # 查看日志
singtool config         # 重新生成配置
singtool test           # 测试节点连通性
singtool uninstall      # 卸载sing-box
singtool help           # 显示帮助
```

## 安装位置

- **程序目录**: `/usr/local/singtool/`
- **虚拟环境**: `/usr/local/singtool/venv/`
- **启动脚本**: `/usr/local/bin/singtool`
- **配置目录**: `~/.config/sing-box/`
- **日志目录**: `~/.local/share/sing-box/logs/`

## 卸载

### 卸载 SingTool
```bash
./install.sh uninstall
```

### 完全清理
```bash
# 卸载工具
./install.sh uninstall

# 手动删除配置（如果需要）
rm -rf ~/.config/sing-box
rm -rf ~/.local/share/sing-box
```

## 故障排除

### 1. Python版本问题
```bash
# 检查Python版本
python3 --version

# 如果版本过低，请升级
brew install python3  # macOS
```

### 2. 权限问题
```bash
# 如果遇到权限问题，检查sudo权限
sudo -v
```

### 3. 依赖包问题
```bash
# 手动安装依赖
pip3 install rich requests PyYAML
```

### 4. sing-box未找到
```bash
# macOS - 重新安装sing-box
brew uninstall sing-box
brew tap sagernet/sing-box
brew install sing-box
```

### 5. 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf /usr/local/singtool/venv
python3 -m venv /usr/local/singtool/venv
source /usr/local/singtool/venv/bin/activate
pip install -r /usr/local/singtool/requirements.txt
```

## 开发模式

如果你想在当前目录运行而不安装到系统：

```bash
# 创建本地虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 直接运行
python3 sing.py
```

## 更新

要更新 SingTool 到最新版本：

```bash
# 方法1: 重新安装
./install.sh

# 方法2: 手动更新
cd singtool
git pull
./install.sh
```

## 支持

- **仓库**: [GitHub Repository URL]
- **文档**: [Documentation URL]
- **问题反馈**: [Issues URL]

---

**注意**: 首次安装后，请运行 `singtool install` 完成 sing-box 的配置和服务设置。 