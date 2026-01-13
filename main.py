#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF工具箱 - 跨平台PDF处理应用
"""

import sys
import os

# 确保能够找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow

def setup_exception_logging():
    """设置异常日志记录 (可选: 如果本地运行不需要也可以删掉，但保留也不坏处)"""
    pass 
    # 本地开发直接在控制台看 traceback 更好，所以我把它置空了，或者你可以完全移除这个函数。
    # 为了保持简洁，我将移除 global exception hook 的覆盖，让它默认输出到控制台。

def main():
    # 启用高DPI支持
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("PDF工具箱")
    app.setApplicationVersion("1.0.0")
    
    # 设置默认字体
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    font.setPointSize(10)
    app.setFont(font)
    
    # 加载样式表
    # 直接使用相对路径，适合开发环境
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "styles.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Style file not found at {style_path}")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
