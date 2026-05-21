#!/usr/bin/env python3
"""
Zorix Browser - 真实的终端网络浏览器
在 Termux、Linux 和 Mac 上运行
支持 Web API 服务
"""

import sys
import os
import json
import requests
from urllib.parse import urljoin, urlparse, unquote
from datetime import datetime
from bs4 import BeautifulSoup
import re
from collections import deque
from threading import Thread
import time

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class Fore:
        CYAN = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        WHITE = ''
    class Back:
        BLACK = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


class ZorixBrowser:
    def __init__(self):
        self.history = deque(maxlen=100)
        self.bookmarks = self.load_bookmarks()
        self.current_url = None
        self.current_content = None
        self.current_links = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache = {}  # 缓存获取的内容
        self.api_server = None
    
    def fetch_page(self, url):
        """获取网页内容"""
        try:
            # 确保URL有protocol
            if not url.startswith(('http://', 'https://', 'ftp://')):
                url = 'https://' + url
            
            print(f"{Fore.CYAN}⏳ 正在加载: {url}{Style.RESET_ALL}")
            response = self.session.get(url, timeout=10)
            response.encoding = response.apparent_encoding or 'utf-8'
            
            self.current_url = url
            self.history.append(url)
            self.cache[url] = response.text  # 缓存内容
            return response.text
        except requests.exceptions.MissingSchema:
            print(f"{Fore.RED}✖ 无效的URL��式{Style.RESET_ALL}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}✖ 连接失败 - 请检查网络{Style.RESET_ALL}")
            return None
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}✖ 连接超时{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}✖ 错误: {str(e)}{Style.RESET_ALL}")
            return None
    
    def parse_html(self, html_content):
        """解析HTML并提取内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(['script', 'style', 'meta', 'link']):
                script.decompose()
            
            # 提取文本
            text = soup.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            return lines
        except Exception as e:
            print(f"{Fore.RED}✖ 解析错误: {str(e)}{Style.RESET_ALL}")
            return []
    
    def extract_links(self, html_content):
        """从HTML提取所有链接"""
        links = {}
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            link_index = 1
            
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                text = a.get_text(strip=True)[:50]  # 限制文本长度
                
                if href and text:
                    full_url = urljoin(self.current_url, href)
                    if full_url.startswith(('http://', 'https://')):
                        links[link_index] = {
                            'url': full_url,
                            'text': text
                        }
                        link_index += 1
            
            self.current_links = links
        except:
            pass
        
        return links
    
    def display_page(self, html_content):
        """在终端显示网页"""
        self.current_content = html_content
        lines = self.parse_html(html_content)
        links = self.extract_links(html_content)
        
        # 显示页面信息
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📄 URL: {self.current_url}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
        
        # 显示内容（前50行）
        for i, line in enumerate(lines[:50]):
            if i > 0 and i % 20 == 0:
                print(f"{Fore.YELLOW}--- 继续滚动 ---{Style.RESET_ALL}")
            print(line[:70])  # 限制每行长度
        
        if len(lines) > 50:
            print(f"\n{Fore.YELLOW}... 还有 {len(lines)-50} 行内容 ...{Style.RESET_ALL}")
        
        # 显示链接
        if links:
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔗 可用链接:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            for idx, link_info in sorted(links.items()):
                print(f"  {Fore.YELLOW}[{idx}]{Style.RESET_ALL} {link_info['text']}")
                print(f"       {Fore.CYAN}{link_info['url']}{Style.RESET_ALL}")
    
    def open_url(self, url):
        """打开URL"""
        html = self.fetch_page(url)
        if html:
            self.display_page(html)
            return True
        return False
    
    def search(self, query):
        """搜索"""
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        self.open_url(search_url)
    
    def click_link(self, link_id):
        """点击链接"""
        try:
            link_id = int(link_id)
            if link_id in self.current_links:
                url = self.current_links[link_id]['url']
                self.open_url(url)
            else:
                print(f"{Fore.RED}✖ 链接不存在{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}✖ 请输入有效的链接编号{Style.RESET_ALL}")
    
    def load_bookmarks(self):
        """加载书签"""
        if os.path.exists('bookmarks.json'):
            try:
                with open('bookmarks.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_bookmarks(self):
        """保存书签"""
        with open('bookmarks.json', 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
    
    def add_bookmark(self):
        """添加书签"""
        if self.current_url:
            bookmark = {
                'url': self.current_url,
                'title': input(f"{Fore.GREEN}输入书签标题: {Style.RESET_ALL}").strip(),
                'date': datetime.now().isoformat()
            }
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            print(f"{Fore.GREEN}✅ 书签已保存{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✖ 没有当前页面{Style.RESET_ALL}")
    
    def show_bookmarks(self):
        """显示书签"""
        if not self.bookmarks:
            print(f"{Fore.YELLOW}📚 没有书签{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📚 我的书签:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        for i, bookmark in enumerate(self.bookmarks, 1):
            print(f"  {Fore.YELLOW}[{i}]{Style.RESET_ALL} {bookmark['title']}")
            print(f"       {Fore.CYAN}{bookmark['url']}{Style.RESET_ALL}")
        
        try:
            choice = input(f"\n{Fore.GREEN}选择书签打开 (输入编号) 或 Enter 跳过: {Style.RESET_ALL}")
            if choice.isdigit() and 1 <= int(choice) <= len(self.bookmarks):
                self.open_url(self.bookmarks[int(choice)-1]['url'])
        except KeyboardInterrupt:
            pass
    
    def show_history(self):
        """显示历史记录"""
        if not self.history:
            print(f"{Fore.YELLOW}📋 没有历史记录{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📋 浏览历史:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        for i, url in enumerate(reversed(list(self.history)), 1):
            print(f"  {Fore.YELLOW}[{i}]{Style.RESET_ALL} {Fore.CYAN}{url}{Style.RESET_ALL}")
    
    def show_help(self):
        """显示帮助"""
        help_text = f"""
{Fore.GREEN}{'='*60}{Style.RESET_ALL}
{Fore.CYAN}🌐 Zorix 浏览器 - 命令帮助{Style.RESET_ALL}
{Fore.GREEN}{'='*60}{Style.RESET_ALL}

{Fore.YELLOW}导航命令:{Style.RESET_ALL}
  open <url>          - 打开网址 (例: open https://example.com)
  search <keyword>    - 搜索 (例: search python tutorial)
  <链接编号>          - 点击链接 (例: 1)

{Fore.YELLOW}浏览命令:{Style.RESET_ALL}
  refresh             - 刷新当前页面
  bookmarks           - 显示书签列表
  add-bookmark        - 保存当前页面为书签
  history             - 显示浏览历史

{Fore.YELLOW}系统命令:{Style.RESET_ALL}
  clear               - 清屏
  help                - 显示此帮助
  api-start           - 启动 Web API 服务
  quit / exit         - 退出浏览器

{Fore.GREEN}{'='*60}{Style.RESET_ALL}
"""
        print(help_text)
    
    def create_api_server(self, host='0.0.0.0', port=5000):
        """创建 Flask API 服务器"""
        if not HAS_FLASK:
            print(f"{Fore.RED}✖ Flask 未安装，请运行: pip install flask{Style.RESET_ALL}")
            return False
        
        app = Flask(__name__)
        browser_instance = self
        
        @app.route('/search--usercontent/', methods=['GET'])
        def search_user_content():
            """获取用户请求的内容
            使用方式: GET /search--usercontent/?url=https://example.com
            或: GET /search--usercontent/?url=example.com
            返回: JSON 格式的 HTML 内容和链接信息
            """
            url = request.args.get('url', '').strip()
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': '缺少 url 参数',
                    'usage': '/search--usercontent/?url=https://example.com'
                }), 400
            
            try:
                # 确保URL有protocol
                if not url.startswith(('http://', 'https://', 'ftp://')):
                    url = 'https://' + url
                
                # 尝试从缓存获取
                if url in browser_instance.cache:
                    html_content = browser_instance.cache[url]
                else:
                    # 获取新的内容
                    response = browser_instance.session.get(url, timeout=10)
                    response.encoding = response.apparent_encoding or 'utf-8'
                    html_content = response.text
                    browser_instance.cache[url] = html_content
                
                # 解析 HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 移除脚本和样式
                for script in soup(['script', 'style', 'meta', 'link']):
                    script.decompose()
                
                # 提取文本内容
                text = soup.get_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # 提取链接
                links = {}
                link_index = 1
                for a in soup.find_all('a', href=True):
                    href = a.get('href')
                    text_content = a.get_text(strip=True)[:100]
                    
                    if href and text_content:
                        full_url = urljoin(url, href)
                        if full_url.startswith(('http://', 'https://')):
                            links[link_index] = {
                                'url': full_url,
                                'text': text_content
                            }
                            link_index += 1
                
                return jsonify({
                    'success': True,
                    'url': url,
                    'status_code': 200,
                    'content': lines[:100],  # 前100行
                    'content_length': len(lines),
                    'links': links,
                    'links_count': len(links),
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except requests.exceptions.Timeout:
                return jsonify({
                    'success': False,
                    'error': '连接超时'
                }), 504
            except requests.exceptions.ConnectionError:
                return jsonify({
                    'success': False,
                    'error': '连接失败'
                }), 503
            except requests.exceptions.MissingSchema:
                return jsonify({
                    'success': False,
                    'error': '无效的URL格式'
                }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @app.route('/search--usercontent/html', methods=['GET'])
        def get_raw_html():
            """获取原始 HTML 内容
            使用方式: GET /search--usercontent/html?url=https://example.com
            返回: 原始 HTML 文本
            """
            url = request.args.get('url', '').strip()
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': '缺少 url 参数'
                }), 400
            
            try:
                if not url.startswith(('http://', 'https://', 'ftp://')):
                    url = 'https://' + url
                
                if url in browser_instance.cache:
                    html_content = browser_instance.cache[url]
                else:
                    response = browser_instance.session.get(url, timeout=10)
                    response.encoding = response.apparent_encoding or 'utf-8'
                    html_content = response.text
                    browser_instance.cache[url] = html_content
                
                return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
            
            except Exception as e:
                return f"Error: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}
        
        @app.route('/search--usercontent/status', methods=['GET'])
        def api_status():
            """API 状态检查"""
            return jsonify({
                'status': 'online',
                'version': '1.0',
                'endpoints': {
                    '/search--usercontent/': '获取解析后的页面内容（JSON）',
                    '/search--usercontent/html': '获取原始 HTML 内容',
                    '/search--usercontent/status': '获取 API 状态'
                }
            }), 200
        
        # 在后台线程启动服务器
        def run_server():
            app.run(host=host, port=port, debug=False, use_reloader=False)
        
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        
        self.api_server = True
        print(f"{Fore.GREEN}��� Web API 已启动{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 服务地址: http://{host}:{port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📡 可用端点:{Style.RESET_ALL}")
        print(f"   - GET /search--usercontent/?url=<url>")
        print(f"   - GET /search--usercontent/html?url=<url>")
        print(f"   - GET /search--usercontent/status\n")
        
        return True
    
    def run(self):
        """主循环"""
        print(f"{Fore.CYAN}")
        print(r"""
  _____ _____   ___ __  __ 
 |__  / /  __ \/   \  \/  /
  /_ / /  /__/  /\ \  \ / 
|___/  \____/\_/__\ \/  
                    
        """)
        print(f"{Fore.GREEN}欢迎使用 Zorix 浏览器")
        print(f"真实的终端网络浏览器 v1.1{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}输入 'help' 获取帮助{Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # 解析命令
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else None
                
                if command == 'open':
                    if args:
                        self.open_url(args)
                    else:
                        print(f"{Fore.RED}✖ 请提供URL{Style.RESET_ALL}")
                
                elif command == 'search':
                    if args:
                        self.search(args)
                    else:
                        print(f"{Fore.RED}✖ 请提供搜索关键词{Style.RESET_ALL}")
                
                elif command == 'refresh':
                    if self.current_url:
                        self.open_url(self.current_url)
                    else:
                        print(f"{Fore.RED}✖ 没有当前页面{Style.RESET_ALL}")
                
                elif command == 'bookmarks':
                    self.show_bookmarks()
                
                elif command == 'add-bookmark':
                    self.add_bookmark()
                
                elif command == 'history':
                    self.show_history()
                
                elif command == 'clear':
                    os.system('clear' if os.name != 'nt' else 'cls')
                
                elif command == 'help':
                    self.show_help()
                
                elif command == 'api-start':
                    if not self.api_server:
                        port = int(args) if args and args.isdigit() else 5000
                        self.create_api_server(port=port)
                    else:
                        print(f"{Fore.YELLOW}⚠ Web API 已在运行{Style.RESET_ALL}")
                
                elif command in ['quit', 'exit', 'q']:
                    print(f"{Fore.GREEN}👋 感谢使用 Zorix 浏览器!{Style.RESET_ALL}")
                    break
                
                elif command.isdigit():
                    self.click_link(command)
                
                else:
                    print(f"{Fore.RED}✖ 未知命令: {command}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}输入 'help' 获取帮助{Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}中断 (按 Ctrl+C 再次退出){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✖ 错误: {str(e)}{Style.RESET_ALL}")


def main():
    browser = ZorixBrowser()
    browser.run()


if __name__ == '__main__':
    main()
