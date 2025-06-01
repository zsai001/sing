#!/bin/bash

# SingTool 安装脚本
# macOS/Linux 自动化安装脚本

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/singtool"
BIN_DIR="/usr/local/bin"
VENV_DIR="$INSTALL_DIR/venv"
PYTHON_FILES=("sing.py" "core.py" "service.py" "config_manager.py" "nodes.py" "menu.py" "rich_menu.py" "paths.py" "utils.py" "advanced_config.py" "requirements.txt" "LICENSE")

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要以root权限运行此脚本"
        log_info "脚本会在需要时自动请求sudo权限"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    log_step "检测操作系统..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        ARCH=$(uname -m)
        if [[ "$ARCH" == "x86_64" ]]; then
            BREW_PREFIX="/usr/local"
        else
            BREW_PREFIX="/opt/homebrew"
        fi
        log_info "检测到 macOS ($ARCH)"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        log_info "检测到 Linux"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查Python环境
check_python() {
    log_step "检查Python环境..."
    
    # 检查Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            log_info "Python版本: $PYTHON_VERSION ✓"
            PYTHON_CMD="python3"
        else
            log_error "需要Python 3.8+，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "未找到Python 3，请先安装Python 3.8+"
        if [[ "$OS" == "macOS" ]]; then
            log_info "可通过以下方式安装:"
            log_info "  brew install python3"
            log_info "  或访问 https://python.org 下载安装"
        fi
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到pip3，请安装pip"
        exit 1
    fi
    
    log_info "pip3版本: $(pip3 --version | cut -d' ' -f2) ✓"
}

# 检查依赖
check_dependencies() {
    log_step "检查系统依赖..."
    
    if [[ "$OS" == "macOS" ]]; then
        # 检查Homebrew
        if command -v brew &> /dev/null; then
            log_info "Homebrew已安装 ✓"
        else
            log_warn "未检测到Homebrew"
            read -p "是否安装Homebrew? (推荐) [Y/n]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                log_step "安装Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                
                # 添加到PATH
                if [[ "$ARCH" == "arm64" ]]; then
                    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                log_info "Homebrew安装完成 ✓"
            fi
        fi
        
        # 检查sing-box
        if command -v sing-box &> /dev/null; then
            SINGBOX_VERSION=$(sing-box version | head -n1)
            log_info "sing-box已安装: $SINGBOX_VERSION ✓"
        else
            log_warn "sing-box未安装"
            read -p "是否通过Homebrew安装sing-box? [Y/n]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                log_step "安装sing-box..."
                brew tap sagernet/sing-box
                brew install sing-box
                log_info "sing-box安装完成 ✓"
            fi
        fi
    fi
}

# 创建安装目录
create_install_dir() {
    log_step "创建安装目录..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        log_warn "安装目录已存在: $INSTALL_DIR"
        read -p "是否覆盖安装? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo rm -rf "$INSTALL_DIR"
        else
            log_info "取消安装"
            exit 0
        fi
    fi
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $(whoami):$(id -gn) "$INSTALL_DIR"
    log_info "安装目录创建完成: $INSTALL_DIR"
}

# 创建虚拟环境
create_venv() {
    log_step "创建Python虚拟环境..."
    
    if [[ -d "$VENV_DIR" ]]; then
        log_warn "虚拟环境已存在，重新创建..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    pip install --upgrade pip
    
    log_info "虚拟环境创建完成: $VENV_DIR"
}

# 安装Python依赖
install_dependencies() {
    log_step "安装Python依赖..."
    
    source "$VENV_DIR/bin/activate"
    
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        pip install -r "$SCRIPT_DIR/requirements.txt"
        log_info "依赖安装完成 ✓"
    else
        log_warn "未找到requirements.txt，手动安装基础依赖..."
        pip install rich requests PyYAML
    fi
}

# 复制文件
copy_files() {
    log_step "复制程序文件..."
    
    for file in "${PYTHON_FILES[@]}"; do
        if [[ -f "$SCRIPT_DIR/$file" ]]; then
            cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
            log_info "复制: $file ✓"
        else
            log_warn "文件不存在，跳过: $file"
        fi
    done
    
    # 复制配置目录
    if [[ -d "$SCRIPT_DIR/config" ]]; then
        cp -r "$SCRIPT_DIR/config" "$INSTALL_DIR/"
        log_info "复制配置目录 ✓"
    fi
    
    # 复制UI目录
    if [[ -d "$SCRIPT_DIR/ui" ]]; then
        cp -r "$SCRIPT_DIR/ui" "$INSTALL_DIR/"
        log_info "复制UI目录 ✓"
    fi
}

# 创建启动脚本
create_launcher() {
    log_step "创建启动脚本..."
    
    cat > "$INSTALL_DIR/singtool" << EOF
#!/bin/bash
# SingTool 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
source "\$SCRIPT_DIR/venv/bin/activate"

# 切换到安装目录
cd "\$SCRIPT_DIR"

# 运行主程序
python3 sing.py "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/singtool"
    
    # 创建系统级别的符号链接
    sudo ln -sf "$INSTALL_DIR/singtool" "$BIN_DIR/singtool"
    
    log_info "启动脚本创建完成 ✓"
}

# 设置权限
set_permissions() {
    log_step "设置文件权限..."
    
    # 设置目录权限
    chmod 755 "$INSTALL_DIR"
    chmod 755 "$VENV_DIR"
    
    # 设置Python文件权限
    find "$INSTALL_DIR" -name "*.py" -exec chmod 644 {} \;
    
    # 设置可执行文件权限
    chmod +x "$INSTALL_DIR/sing.py"
    chmod +x "$INSTALL_DIR/singtool"
    
    log_info "权限设置完成 ✓"
}

# 创建配置目录
create_config_dirs() {
    log_step "创建配置目录..."
    
    CONFIG_DIR="$HOME/.config/sing-box"
    LOG_DIR="$HOME/.local/share/sing-box/logs"
    
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    
    log_info "配置目录: $CONFIG_DIR"
    log_info "日志目录: $LOG_DIR"
}

# 显示安装完成信息
show_completion() {
    echo
    echo -e "${GREEN}🎉 SingTool 安装完成！${NC}"
    echo
    echo -e "${CYAN}使用方法:${NC}"
    echo "  singtool                # 启动交互式菜单"
    echo "  singtool install        # 安装和配置sing-box"
    echo "  singtool status         # 查看状态"
    echo "  singtool start          # 启动服务"
    echo "  singtool stop           # 停止服务"
    echo "  singtool nodes          # 管理节点"
    echo "  singtool help           # 显示帮助"
    echo
    echo -e "${CYAN}安装位置:${NC}"
    echo "  程序目录: $INSTALL_DIR"
    echo "  虚拟环境: $VENV_DIR"
    echo "  启动脚本: $BIN_DIR/singtool"
    echo
    echo -e "${YELLOW}下一步:${NC}"
    echo "  1. 运行 'singtool install' 完成sing-box安装"
    echo "  2. 添加节点配置"
    echo "  3. 启动服务"
    echo
}

# 卸载函数
uninstall() {
    log_step "卸载SingTool..."
    
    echo -e "${RED}警告: 这将完全删除SingTool及其所有数据${NC}"
    read -p "是否确认卸载? [y/N]: " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "取消卸载"
        exit 0
    fi
    
    # 停止服务（如果在运行）
    if command -v singtool &> /dev/null; then
        singtool stop 2>/dev/null || true
    fi
    
    # 删除安装目录
    if [[ -d "$INSTALL_DIR" ]]; then
        sudo rm -rf "$INSTALL_DIR"
        log_info "删除安装目录: $INSTALL_DIR"
    fi
    
    # 删除符号链接
    if [[ -L "$BIN_DIR/singtool" ]]; then
        sudo rm -f "$BIN_DIR/singtool"
        log_info "删除启动脚本: $BIN_DIR/singtool"
    fi
    
    # 询问是否删除配置和日志
    read -p "是否同时删除配置文件和日志? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/.config/sing-box" 2>/dev/null || true
        rm -rf "$HOME/.local/share/sing-box" 2>/dev/null || true
        log_info "删除配置和日志目录"
    fi
    
    log_info "SingTool卸载完成"
}

# 显示帮助
show_help() {
    echo "SingTool 安装脚本"
    echo
    echo "用法:"
    echo "  $0 [选项]"
    echo
    echo "选项:"
    echo "  install     # 安装SingTool (默认)"
    echo "  uninstall   # 卸载SingTool"
    echo "  help        # 显示此帮助"
    echo
    echo "安装过程包括:"
    echo "  1. 检测系统环境"
    echo "  2. 检查Python环境"
    echo "  3. 安装系统依赖"
    echo "  4. 创建虚拟环境"
    echo "  5. 安装Python依赖"
    echo "  6. 复制程序文件"
    echo "  7. 创建启动脚本"
    echo
}

# 主函数
main() {
    case "${1:-install}" in
        "install")
            check_root
            detect_os
            check_python
            check_dependencies
            create_install_dir
            create_venv
            install_dependencies
            copy_files
            create_launcher
            set_permissions
            create_config_dirs
            show_completion
            ;;
        "uninstall")
            uninstall
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 