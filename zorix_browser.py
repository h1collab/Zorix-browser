#!/usr/bin/env python3
"""
Zorix Browser - A functional web browser application
Main entry point for the browser
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QLineEdit, QPushButton, QLabel, QDialog, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMessageBox
import json
from datetime import datetime


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zorix Browser')
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize browser state
        self.bookmarks = self.load_bookmarks()
        self.history = self.load_history()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        # Back button
        self.back_btn = QPushButton('← Back')
        self.back_btn.clicked.connect(self.go_back)
        toolbar_layout.addWidget(self.back_btn)
        
        # Forward button
        self.forward_btn = QPushButton('Forward →')
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar_layout.addWidget(self.forward_btn)
        
        # Reload button
        self.reload_btn = QPushButton('⟳ Reload')
        self.reload_btn.clicked.connect(self.reload_page)
        toolbar_layout.addWidget(self.reload_btn)
        
        # Stop button
        self.stop_btn = QPushButton('⊗ Stop')
        self.stop_btn.clicked.connect(self.stop_loading)
        toolbar_layout.addWidget(self.stop_btn)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Enter URL or search...')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar_layout.addWidget(self.url_bar)
        
        # Go button
        go_btn = QPushButton('Go')
        go_btn.clicked.connect(self.navigate_to_url)
        toolbar_layout.addWidget(go_btn)
        
        # Bookmark button
        self.bookmark_btn = QPushButton('★ Bookmark')
        self.bookmark_btn.clicked.connect(self.add_bookmark)
        toolbar_layout.addWidget(self.bookmark_btn)
        
        # Show bookmarks
        bookmarks_btn = QPushButton('📑 Bookmarks')
        bookmarks_btn.clicked.connect(self.show_bookmarks)
        toolbar_layout.addWidget(bookmarks_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # Create tab widget for multiple tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tabs)
        
        # Create new tab button
        new_tab_btn = QPushButton('+ New Tab')
        new_tab_btn.clicked.connect(self.new_tab)
        main_layout.addWidget(new_tab_btn)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        main_widget.setLayout(main_layout)
        
        # Create first tab
        self.new_tab()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+T for new tab
        from PyQt5.QtWidgets import QShortcut
        QShortcut(QKeySequence('Ctrl+T'), self).activated.connect(self.new_tab)
        QShortcut(QKeySequence('Ctrl+W'), self).activated.connect(self.close_current_tab)
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(self.reload_page)
        QShortcut(QKeySequence('Ctrl+L'), self).activated.connect(self.focus_url_bar)
    
    def new_tab(self):
        """Create a new browser tab"""
        browser = QWebEngineView()
        browser.loadFinished.connect(lambda: self.on_load_finished())
        browser.urlChanged.connect(lambda url: self.on_url_changed(url))
        browser.titleChanged.connect(lambda title: self.on_title_changed(title))
        
        # Load default home page
        html_content = self.get_home_page()
        browser.setHtml(html_content)
        
        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)
        self.focus_url_bar()
    
    def close_tab(self, index):
        """Close a tab"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def close_current_tab(self):
        """Close current tab"""
        self.close_tab(self.tabs.currentIndex())
    
    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        
        # Handle search queries
        if not url_text.startswith(('http://', 'https://', 'file://')):
            if '.' not in url_text or ' ' in url_text:
                # Search query
                url_text = f'https://www.google.com/search?q={url_text}'
            else:
                url_text = 'https://' + url_text
        
        browser = self.tabs.currentWidget()
        if browser:
            browser.load(QUrl(url_text))
            self.statusBar().showMessage(f'Loading {url_text}...')
            self.add_to_history(url_text)
    
    def focus_url_bar(self):
        """Focus on URL bar"""
        self.url_bar.setFocus()
        self.url_bar.selectAll()
    
    def on_url_changed(self, url):
        """Handle URL changes"""
        self.url_bar.setText(url.toString())
    
    def on_title_changed(self, title):
        """Handle page title changes"""
        if title:
            self.tabs.setTabText(self.tabs.currentIndex(), title[:30])
    
    def on_load_finished(self):
        """Handle page load completion"""
        self.statusBar().showMessage('Page loaded successfully')
    
    def go_back(self):
        """Go back in history"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.back()
    
    def go_forward(self):
        """Go forward in history"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.forward()
    
    def reload_page(self):
        """Reload current page"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()
            self.statusBar().showMessage('Reloading page...')
    
    def stop_loading(self):
        """Stop loading current page"""
        browser = self.tabs.currentWidget()
        if browser:
            browser.stop()
            self.statusBar().showMessage('Loading stopped')
    
    def add_bookmark(self):
        """Add current page to bookmarks"""
        url = self.url_bar.text()
        title = self.tabs.tabText(self.tabs.currentIndex())
        
        if url:
            bookmark = {'url': url, 'title': title, 'date': datetime.now().isoformat()}
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            self.statusBar().showMessage('Bookmarked!')
    
    def show_bookmarks(self):
        """Show bookmarks dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle('Bookmarks')
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        list_widget = QListWidget()
        
        for bookmark in self.bookmarks:
            item_text = f"{bookmark['title']} - {bookmark['url']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, bookmark['url'])
            list_widget.addItem(item)
        
        def open_bookmark():
            item = list_widget.currentItem()
            if item:
                url = item.data(Qt.UserRole)
                self.url_bar.setText(url)
                self.navigate_to_url()
                dialog.close()
        
        def delete_bookmark():
            item = list_widget.currentItem()
            if item:
                index = list_widget.row(item)
                self.bookmarks.pop(index)
                self.save_bookmarks()
                list_widget.takeItem(index)
        
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(open_bookmark)
        
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(delete_bookmark)
        
        layout.addWidget(list_widget)
        layout.addWidget(open_btn)
        layout.addWidget(delete_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def add_to_history(self, url):
        """Add URL to history"""
        self.history.insert(0, {'url': url, 'date': datetime.now().isoformat()})
        if len(self.history) > 100:  # Keep last 100 entries
            self.history = self.history[:100]
        self.save_history()
    
    def load_bookmarks(self):
        """Load bookmarks from file"""
        if os.path.exists('bookmarks.json'):
            try:
                with open('bookmarks.json', 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_bookmarks(self):
        """Save bookmarks to file"""
        with open('bookmarks.json', 'w') as f:
            json.dump(self.bookmarks, f, indent=2)
    
    def load_history(self):
        """Load history from file"""
        if os.path.exists('history.json'):
            try:
                with open('history.json', 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Save history to file"""
        with open('history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_home_page(self):
        """Get home page HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Zorix Browser Home</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .container {
                    background: white;
                    border-radius: 10px;
                    padding: 40px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    max-width: 600px;
                    text-align: center;
                }
                h1 {
                    color: #667eea;
                    margin: 0 0 20px 0;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .features {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-top: 30px;
                    text-align: left;
                }
                .feature {
                    padding: 15px;
                    background: #f5f5f5;
                    border-radius: 5px;
                }
                .feature h3 {
                    color: #667eea;
                    margin-top: 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 Zorix Browser</h1>
                <p>Welcome to your lightweight, functional web browser.</p>
                <div class="features">
                    <div class="feature">
                        <h3>📑 Tabbed Browsing</h3>
                        <p>Open multiple tabs with Ctrl+T</p>
                    </div>
                    <div class="feature">
                        <h3>★ Bookmarks</h3>
                        <p>Save your favorite pages</p>
                    </div>
                    <div class="feature">
                        <h3>⟳ Navigation</h3>
                        <p>Go back and forward easily</p>
                    </div>
                    <div class="feature">
                        <h3>🔍 Search</h3>
                        <p>Built-in Google search</p>
                    </div>
                </div>
                <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #999;">Zorix Browser v1.0</p>
            </div>
        </body>
        </html>
        """


def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
