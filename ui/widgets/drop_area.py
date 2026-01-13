#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拖拽区域组件 - 支持拖放PDF文件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropArea(QWidget):
    """拖拽上传区域"""
    
    files_dropped = pyqtSignal(list)  # 文件拖放信号
    
    def __init__(self, accept_extensions=None, multiple=True, parent=None):
        super().__init__(parent)
        self.accept_extensions = accept_extensions or ['.pdf']
        self.multiple = multiple
        self.setAcceptDrops(True)
        self.setObjectName("drop_area")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        
        # 图标
        self.icon_label = QLabel("📄")
        self.icon_label.setObjectName("icon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.icon_label)
        
        # 提示文字
        self.hint_label = QLabel("将PDF文件拖拽到此处")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("color: #6b7280; font-size: 16px;")
        layout.addWidget(self.hint_label)
        
        self.setMinimumHeight(200)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile().lower()
                    if any(file_path.endswith(ext) for ext in self.accept_extensions):
                        event.acceptProposedAction()
                        self.setStyleSheet("""
                            #drop_area {
                                background-color: #e8f4fc;
                                border: 2px dashed #3b82f6;
                            }
                        """)
                        return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("")
    
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if any(file_path.lower().endswith(ext) for ext in self.accept_extensions):
                    files.append(file_path)
                    if not self.multiple:
                        break
        
        if files:
            event.acceptProposedAction()
            self.files_dropped.emit(files)
    
    def open_file_dialog(self):
        ext_filter = "PDF文件 (*.pdf)" if '.pdf' in self.accept_extensions else "所有文件 (*.*)"
        
        if self.multiple:
            files, _ = QFileDialog.getOpenFileNames(
                self, "选择文件", "", ext_filter
            )
        else:
            file, _ = QFileDialog.getOpenFileName(
                self, "选择文件", "", ext_filter
            )
            files = [file] if file else []
        
        if files:
            self.files_dropped.emit(files)
    
    def set_hint(self, text: str):
        """设置提示文字"""
        self.hint_label.setText(text)
    
    def set_extensions(self, extensions: list):
        """设置接受的文件扩展名"""
        self.accept_extensions = extensions
