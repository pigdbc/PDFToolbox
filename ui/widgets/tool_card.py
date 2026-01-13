#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具卡片组件 - Smallpdf 风格横向卡片
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor


# 工具类别对应的颜色
CATEGORY_COLORS = {
    "压缩": "#e74c3c",  # 红色
    "整理": "#9b59b6",  # 紫色
    "转换": "#3498db",  # 蓝色
    "编辑": "#2ecc71",  # 绿色
    "安全": "#f39c12",  # 橙色
    "OCR": "#1abc9c",   # 青色
}


class ToolCard(QWidget):
    """功能卡片组件 - Smallpdf 风格"""
    
    clicked = pyqtSignal(str)  # 点击信号，传递工具ID
    
    def __init__(self, tool_id: str, icon: str, title: str, description: str = "", 
                 category: str = "", parent=None):
        super().__init__(parent)
        self.tool_id = tool_id
        self.category = category
        self.color = CATEGORY_COLORS.get(category, "#3498db")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(220, 56)
        self.init_ui(icon, title)
        self.apply_style()
    
    def init_ui(self, icon: str, title: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 16, 10)
        layout.setSpacing(12)
        
        # 彩色图标容器
        self.icon_container = QLabel()
        self.icon_container.setObjectName("icon_container")
        self.icon_container.setFixedSize(36, 36)
        self.icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_container.setStyleSheet(f"""
            QLabel {{
                background-color: {self.color};
                border-radius: 8px;
                font-size: 18px;
            }}
        """)
        self.icon_container.setText(icon)
        layout.addWidget(self.icon_container)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("""
            color: #1e2537;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(self.title_label, 1)
    
    def apply_style(self):
        self.setStyleSheet("""
            ToolCard {
                background-color: #ffffff;
                border: 1px solid #e8ecf0;
                border-radius: 10px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.tool_id)
    
    def enterEvent(self, event):
        self.setStyleSheet("""
            ToolCard {
                background-color: #ffffff;
                border: 1px solid #d0d8e0;
                border-radius: 10px;
            }
        """)
        # 增强阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def leaveEvent(self, event):
        self.apply_style()
