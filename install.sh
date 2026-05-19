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
rm -rf Zorix-browser
git clone https://github.com/h1collab/Zorix-browser
cd Zorix-browser

# 安装Python依赖 (不包括Pillow - Termux中难以编译)
echo "📚 安装Python依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 安装完成!"
echo ""
echo "🚀 启动浏览器:"
echo "   cd ~/Zorix-browser"
echo "   python zorix_browser.py"
echo ""
echo "📍 或创建快捷命令:"
echo "   echo 'cd ~/Zorix-browser && python zorix_browser.py' > ~/.zorix"
echo "   chmod +x ~/.zorix"
echo "   ~/.zorix"
echo ""
