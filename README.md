# Zorix Browser

一个真实的、可在Termux中运行的轻量级网络浏览器。

## 特性

- ✅ 真实HTTP/HTTPS请求
- ✅ HTML渲染为终端界面
- ✅ CSS基础支持
- ✅ 链接导航
- ✅ 浏览历史
- ✅ 书签功能
- ✅ 支持Markdown渲染
- ✅ 终端图像显示

## 安装

### 在Termux中安装

```bash
pkg install python pip git
git clone https://github.com/h1collab/Zorix-browser
cd Zorix-browser
pip install -r requirements.txt
```

### 在Linux/Mac中安装

```bash
pip install -r requirements.txt
```

## 使用

### 启动浏览器

```bash
python zorix_browser.py
```

### 基本命令

```
open <url>        - 打开网址
search <keyword>  - 搜索
back              - 返回上一页
forward           - 前进下一页
refresh           - 刷新当前页
bookmarks         - 显示书签
add-bookmark      - 保存书签
history           - 显示历史
clear             - 清屏
help              - 显示帮助
quit/exit         - 退出浏览器
```

### 例子

```
> open https://example.com
> search python tutorial
> bookmarks
> add-bookmark
```

## 系统要求

- Python 3.8+
- requests
- beautifulsoup4
- lxml
- pillow (可选，用于图像显示)

## 在Termux中测试

直接在Termux中运行：

```bash
python zorix_browser.py
```

然后输入：

```
open https://www.example.com
```
