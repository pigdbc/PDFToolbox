#!/usr/bin/env python3
"""
PyInstaller Runtime Hook for PyQt6 on macOS
在 Qt 库加载之前设置必要的环境变量
"""
import os
import sys

# 确保在 Qt 加载前设置这些环境变量
if sys.platform == 'darwin':
    # 禁用 Qt 的位置服务初始化（导致崩溃的根源）
    os.environ['QT_MAC_DISABLE_FOREGROUND_APPLICATION_TRANSFORM'] = '1'
    
    # 如果是打包后的应用
    if hasattr(sys, '_MEIPASS'):
        # 设置 Qt 插件路径
        qt_plugins = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins')
        if os.path.exists(qt_plugins):
            os.environ['QT_PLUGIN_PATH'] = qt_plugins
        
        # 设置 Qt QPA 平台插件路径
        qpa_path = os.path.join(qt_plugins, 'platforms')
        if os.path.exists(qpa_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qpa_path
