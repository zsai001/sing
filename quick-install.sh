#!/bin/bash

# SingTool 一键安装脚本
# 适用于 macOS 和 Linux

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
REPO_URL="https://github.com/your-username/singtool.git"  # 请替换为实际的仓库地址
TEMP_DIR="/tmp/singtool-install"

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

# 检查系统
check_system() {
    log_step "检查系统环境..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "检测到 macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_step "检查依赖工具..."
    
    if ! command -v git &> /dev/null; then
        log_error "未找到 git，请先安装 git"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python 3，请先安装 Python 3.8+"
        exit 1
    fi
    
    log_info "依赖检查通过 ✓"
}

# 下载源码
download_source() {
    log_step "下载 SingTool 源码..."
    
    # 清理临时目录
    rm -rf "$TEMP_DIR"
    
    # 克隆仓库
    git clone "$REPO_URL" "$TEMP_DIR" || {
        log_error "源码下载失败"
        exit 1
    }
    
    log_info "源码下载完成 ✓"
}

# 运行安装
run_install() {
    log_step "运行安装脚本..."
    
    cd "$TEMP_DIR"
    chmod +x install.sh
    ./install.sh
}

# 清理临时文件
cleanup() {
    log_step "清理临时文件..."
    rm -rf "$TEMP_DIR"
    log_info "清理完成 ✓"
}

# 显示横幅
show_banner() {
    echo
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           SingTool 一键安装            ║${NC}"
    echo -e "${CYAN}║      sing-box 管理工具 v2.0            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo
}

# 显示完成信息
show_completion() {
    echo
    echo -e "${GREEN}🎉 SingTool 安装完成！${NC}"
    echo
    echo -e "${CYAN}快速开始:${NC}"
    echo "  1. 运行: singtool"
    echo "  2. 选择: 完整安装"
    echo "  3. 添加节点配置"
    echo "  4. 启动服务"
    echo
    echo -e "${YELLOW}更多命令:${NC}"
    echo "  singtool help       # 查看帮助"
    echo "  singtool status     # 查看状态"
    echo "  singtool nodes      # 管理节点"
    echo
}

# 主函数
main() {
    show_banner
    
    # 检查是否以root运行
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要以root权限运行此脚本"
        exit 1
    fi
    
    check_system
    check_dependencies
    download_source
    run_install
    cleanup
    show_completion
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}安装已中断${NC}"; cleanup; exit 1' INT TERM

# 运行主函数
main "$@" 