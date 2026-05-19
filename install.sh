#!/bin/bash
# Termux 一键安装脚本

echo "🚀 Zorix 浏览器 Termux 安装"
echo "============================"

# 更新包管理器
echo "📦 更新包管理器..."
pkg update

# 安装必要的依赖
echo "📥 安装依赖..."
pkg install -y python pip git

# 克隆仓库
echo "⬇️  克隆仓库..."
cd ~
git clone https://github.com/h1collab/Zorix-browser
cd Zorix-browser

# 安装Python依赖
echo "📚 安装Python依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 安装完成!"
echo ""
echo "🚀 启动浏览器:"
echo "   python zorix_browser.py"
echo ""
echo "或使用命令:"
echo "   zorix"
echo ""
