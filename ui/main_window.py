#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - PDF工具箱主界面
"""

import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QMessageBox, QFileDialog,
    QSpinBox, QComboBox, QLineEdit, QListWidget, QListWidgetItem,
    QProgressBar, QCheckBox, QSplitter, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QImage, QDrag

from ui.widgets.drop_area import DropArea
from ui.widgets.tool_card import ToolCard


# 工具定义
TOOLS = {
    "compress": {"icon": "📦", "title": "压缩PDF", "category": "压缩"},
    "merge": {"icon": "📑", "title": "合并PDF", "category": "整理"},
    "split": {"icon": "✂️", "title": "分割PDF", "category": "整理"},
    "rotate": {"icon": "🔄", "title": "旋转PDF", "category": "整理"},
    "delete_pages": {"icon": "🗑️", "title": "删除页面", "category": "整理"},
    "extract_pages": {"icon": "📤", "title": "提取页面", "category": "整理"},
    "reorder": {"icon": "📋", "title": "重排页面", "category": "整理"},
    "pdf_to_word": {"icon": "📝", "title": "PDF转Word", "category": "转换"},
    "pdf_to_excel": {"icon": "📊", "title": "PDF转Excel", "category": "转换"},
    "pdf_to_ppt": {"icon": "📽️", "title": "PDF转PPT", "category": "转换"},
    "pdf_to_jpg": {"icon": "🖼️", "title": "PDF转图片", "category": "转换"},
    "word_to_pdf": {"icon": "📄", "title": "Word转PDF", "category": "转换"},
    "jpg_to_pdf": {"icon": "🖼️", "title": "图片转PDF", "category": "转换"},
    "watermark": {"icon": "💧", "title": "添加水印", "category": "编辑"},
    "page_number": {"icon": "🔢", "title": "添加页码", "category": "编辑"},
    "crop": {"icon": "✂️", "title": "裁剪PDF", "category": "编辑"},
    "encrypt": {"icon": "🔒", "title": "加密PDF", "category": "安全"},
    "decrypt": {"icon": "🔓", "title": "解密PDF", "category": "安全"},
    "flatten": {"icon": "📃", "title": "展平PDF", "category": "安全"},
    "ocr": {"icon": "🔍", "title": "OCR识别", "category": "OCR"},
}

CATEGORIES = ["全部", "压缩", "整理", "转换", "编辑", "安全", "OCR"]


from PyQt6.QtGui import QTransform

class SelectablePageItem(QFrame):
    """可选择的页面缩略图（支持多选和预览旋转）"""
    
    toggled = pyqtSignal(int, bool)  # 页面选中状态改变信号
    
    def __init__(self, page_num, pixmap, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.selected = False
        self.current_rotation = 0  # 当前预览旋转角度
        self.base_pixmap = pixmap  # 原始缩略图
        
        self.setFixedSize(100, 130)
        self.update_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # 缩略图
        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.thumb_label)
        
        self.update_preview()
        
        # 页码
        self.page_label = QLabel(f"{page_num + 1}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("color: #1e2537; font-size: 11px; font-weight: bold; background: transparent;")
        layout.addWidget(self.page_label)
    
    def update_preview(self):
        """更新预览图（应用旋转）"""
        if self.current_rotation == 0:
            pix = self.base_pixmap
        else:
            transform = QTransform().rotate(self.current_rotation)
            pix = self.base_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            
        scaled = pix.scaled(85, 95, Qt.AspectRatioMode.KeepAspectRatio, 
                           Qt.TransformationMode.SmoothTransformation)
        self.thumb_label.setPixmap(scaled)
    
    def set_rotation(self, angle):
        """设置预览旋转角度 (0, 90, 180, 270)"""
        self.current_rotation = angle % 360
        self.update_preview()
    
    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #dbeafe;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #e8ecf0;
                    border-radius: 8px;
                }
                QFrame:hover { border-color: #93c5fd; }
            """)
    
    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected = not self.selected
            self.update_style()
            self.toggled.emit(self.page_num, self.selected)
        super().mousePressEvent(event)


class PageSelectorWidget(QWidget):
    """通用页面选择组件 - 用于旋转、删除、提取等操作"""
    
    selection_changed = pyqtSignal(list)  # 选中页面列表改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_items = []
        self.selected_pages = set()
        self.total_pages = 0
        self.preview_angle = 0  # 当前设定的预览角度
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        
        self.hint_label = QLabel("点击选择页面")
        self.hint_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        top_layout.addWidget(self.hint_label)
        
        top_layout.addStretch()
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #3b82f6;
                border: 1px solid #3b82f6;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #eff6ff; }
        """)
        self.select_all_btn.clicked.connect(self.select_all)
        top_layout.addWidget(self.select_all_btn)
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #6b7280;
                border: 1px solid #d0d8e0;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
        """)
        self.clear_btn.clicked.connect(self.clear_selection)
        top_layout.addWidget(self.clear_btn)
        
        layout.addLayout(top_layout)
        
        # 选中计数
        self.count_label = QLabel("已选择: 0 页")
        self.count_label.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.count_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setMinimumHeight(160)
        scroll.setMaximumHeight(220)
        
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.setVisible(False)
    
    def load_pdf(self, pdf_path):
        """加载PDF并显示页面缩略图"""
        self.clear()
        
        try:
            doc = fitz.open(pdf_path)
            self.total_pages = len(doc)
            
            cols = 6
            for i, page in enumerate(doc):
                mat = fitz.Matrix(0.2, 0.2)
                pix = page.get_pixmap(matrix=mat)
                img = QImage(pix.samples, pix.width, pix.height, 
                           pix.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                item = SelectablePageItem(i, pixmap)
                item.toggled.connect(self.on_page_toggled)
                self.page_items.append(item)
                
                row = i // cols
                col = i % cols
                self.grid_layout.addWidget(item, row, col)
            
            doc.close()
            self.hint_label.setText(f"共 {self.total_pages} 页，点击选择")
            self.setVisible(True)
            
        except Exception as e:
            print(f"加载PDF失败: {e}")
    
    def on_page_toggled(self, page_num, selected):
        """页面选中状态改变"""
        if selected:
            self.selected_pages.add(page_num)
        else:
            self.selected_pages.discard(page_num)
        
        # 应用当前预览角度
        self.update_visual_rotation()
        
        self.update_count()
        self.selection_changed.emit(sorted(list(self.selected_pages)))
    
    def set_preview_rotation(self, angle):
        """设置选中页面的预览旋转角度"""
        self.preview_angle = angle
        self.update_visual_rotation()
        
    def update_visual_rotation(self):
        """更新所有页面的视觉旋转状态"""
        for i, item in enumerate(self.page_items):
            if i in self.selected_pages:
                item.set_rotation(self.preview_angle)
            else:
                item.set_rotation(0)
    
    def update_count(self):
        """更新选中计数"""
        count = len(self.selected_pages)
        self.count_label.setText(f"已选择: {count} 页")
    
    def select_all(self):
        """全选"""
        self.selected_pages = set(range(self.total_pages))
        for item in self.page_items:
            item.set_selected(True)
        self.update_visual_rotation()
        self.update_count()
        self.selection_changed.emit(sorted(list(self.selected_pages)))
    
    def clear_selection(self):
        """清除选择"""
        self.selected_pages.clear()
        for item in self.page_items:
            item.set_selected(False)
        self.update_visual_rotation()
        self.update_count()
        self.selection_changed.emit([])
    
    def clear(self):
        """清空组件"""
        for item in self.page_items:
            item.deleteLater()
        self.page_items = []
        self.selected_pages.clear()
        self.total_pages = 0
        self.preview_angle = 0
    
    def get_selected_pages(self):
        """获取选中的页面列表（1-indexed）"""
        return sorted([p + 1 for p in self.selected_pages])
    
    def get_selected_pages_0indexed(self):
        """获取选中的页面列表（0-indexed）"""
        return sorted(list(self.selected_pages))


class DraggablePageItem(QFrame):
    """可选择的页面缩略图 - 支持动态尺寸"""
    
    clicked = pyqtSignal(int)  # 点击信号
    
    def __init__(self, page_num, pixmap, width=120, height=160, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.selected = False
        self.item_width = width
        self.item_height = height
        self.setFixedSize(width, height)
        self.update_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        
        # 缩略图 (留出边距和页码空间)
        thumb_width = width - 10
        thumb_height = height - 25
        thumb_label = QLabel()
        scaled = pixmap.scaled(thumb_width, thumb_height, Qt.AspectRatioMode.KeepAspectRatio, 
                               Qt.TransformationMode.SmoothTransformation)
        thumb_label.setPixmap(scaled)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setStyleSheet("background: transparent;")
        layout.addWidget(thumb_label)
        
        # 页码 (根据尺寸调整字体)
        font_size = max(9, min(11, width // 12))
        self.page_label = QLabel(f"第 {page_num + 1} 页")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet(f"color: #1e2537; font-size: {font_size}px; background: transparent;")
        layout.addWidget(self.page_label)
    
    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e0f2fe;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #e8ecf0;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #3b82f6;
                }
            """)
    
    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.page_num)
        super().mousePressEvent(event)


class PageReorderWidget(QWidget):
    """页面重排组件 - 点击选择+按钮移动"""
    
    order_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_items = []
        self.page_order = []
        self.selected_index = -1  # 当前选中的页面索引
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # 提示文字
        hint = QLabel("点击选择页面，使用按钮调整顺序")
        hint.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(hint)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.move_left_btn = QPushButton("◀ 左移")
        self.move_left_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; }
        """)
        self.move_left_btn.clicked.connect(self.move_left)
        self.move_left_btn.setEnabled(False)
        btn_layout.addWidget(self.move_left_btn)
        
        self.move_right_btn = QPushButton("右移 ▶")
        self.move_right_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; }
        """)
        self.move_right_btn.clicked.connect(self.move_right)
        self.move_right_btn.setEnabled(False)
        btn_layout.addWidget(self.move_right_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 滚动区域 - 允许更大的显示区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll.setMinimumHeight(200)
        self.scroll.setMaximumHeight(500)  # 增加最大高度以显示更多页面
        
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.setVisible(False)
    
    def calculate_thumbnail_size(self, page_count):
        """根据页面数量计算合适的缩略图尺寸和列数"""
        # 页面越多，缩略图越小，每行显示更多
        if page_count <= 5:
            return 120, 160, 5   # 大尺寸，5列
        elif page_count <= 10:
            return 100, 135, 6   # 中等尺寸，6列
        elif page_count <= 20:
            return 85, 115, 7    # 较小尺寸，7列
        elif page_count <= 40:
            return 70, 95, 8     # 小尺寸，8列
        else:
            return 60, 82, 10    # 最小尺寸，10列
    
    def load_pdf(self, pdf_path):
        """加载PDF并显示页面缩略图"""
        # 清空现有页面
        self.clear()
        
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            self.page_order = list(range(page_count))
            
            # 根据页面数量动态计算尺寸
            item_width, item_height, cols = self.calculate_thumbnail_size(page_count)
            self.current_cols = cols
            
            # 根据尺寸调整渲染比例
            scale = 0.2 if page_count > 20 else 0.3
            
            for i, page in enumerate(doc):
                # 渲染缩略图
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为QPixmap
                img = QImage(pix.samples, pix.width, pix.height, 
                           pix.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                # 创建可选择项 (传入动态尺寸)
                item = DraggablePageItem(i, pixmap, item_width, item_height)
                item.clicked.connect(self.on_page_clicked)
                self.page_items.append(item)
                
                row = i // cols
                col = i % cols
                self.grid_layout.addWidget(item, row, col)
            
            doc.close()
            self.setVisible(True)
            
        except Exception as e:
            print(f"加载PDF失败: {e}")
    
    def clear(self):
        """清空页面"""
        for item in self.page_items:
            item.deleteLater()
        self.page_items = []
        self.page_order = []
        self.selected_index = -1
    
    def on_page_clicked(self, page_num):
        """页面被点击"""
        # 找到该页面在当前顺序中的位置
        try:
            new_index = self.page_order.index(page_num)
        except ValueError:
            return
        
        # 取消之前的选择
        if self.selected_index >= 0 and self.selected_index < len(self.page_items):
            old_page = self.page_order[self.selected_index]
            self.page_items[old_page].set_selected(False)
        
        # 选择新页面
        self.selected_index = new_index
        self.page_items[page_num].set_selected(True)
        
        # 更新按钮状态
        self.update_buttons()
    
    def update_buttons(self):
        """更新按钮状态"""
        self.move_left_btn.setEnabled(self.selected_index > 0)
        self.move_right_btn.setEnabled(self.selected_index >= 0 and 
                                        self.selected_index < len(self.page_order) - 1)
    
    def move_left(self):
        """向左移动选中页面"""
        if self.selected_index > 0:
            self.swap_pages(self.selected_index, self.selected_index - 1)
            self.selected_index -= 1
            self.update_buttons()
    
    def move_right(self):
        """向右移动选中页面"""
        if self.selected_index < len(self.page_order) - 1:
            self.swap_pages(self.selected_index, self.selected_index + 1)
            self.selected_index += 1
            self.update_buttons()
    
    def swap_pages(self, from_idx, to_idx):
        """交换两个页面的位置"""
        if from_idx != to_idx:
            self.page_order[from_idx], self.page_order[to_idx] = \
                self.page_order[to_idx], self.page_order[from_idx]
            self.refresh_grid()
            self.order_changed.emit(self.page_order)
    
    def refresh_grid(self):
        """刷新网格布局"""
        # 移除所有项
        for item in self.page_items:
            self.grid_layout.removeWidget(item)
        
        # 按新顺序添加 (使用动态列数)
        cols = getattr(self, 'current_cols', 5)
        for i, page_idx in enumerate(self.page_order):
            item = self.page_items[page_idx]
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(item, row, col)
    
    def get_order(self):
        """获取当前页面顺序"""
        return self.page_order


class MultiFilePreviewWidget(QWidget):
    """多文件预览组件 - 用于合并功能"""
    
    files_reordered = pyqtSignal(list)  # 文件重排信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_paths = []
        self.thumbnails = []
        self.selected_index = -1
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # 提示文字
        hint = QLabel("点击选择文件，使用按钮调整合并顺序")
        hint.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(hint)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.move_up_btn = QPushButton("◀ 上移")
        self.move_up_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; }
        """)
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_up_btn.setEnabled(False)
        btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("下移 ▶")
        self.move_down_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; }
        """)
        self.move_down_btn.clicked.connect(self.move_down)
        self.move_down_btn.setEnabled(False)
        btn_layout.addWidget(self.move_down_btn)
        
        self.remove_btn = QPushButton("✕ 移除")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #ef4444;
                border: 1px solid #fca5a5;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #fef2f2; }
            QPushButton:disabled { color: #9ca3af; background-color: #f3f4f6; border-color: #d0d8e0; }
        """)
        self.remove_btn.clicked.connect(self.remove_file)
        self.remove_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setMinimumHeight(180)
        scroll.setMaximumHeight(250)
        
        self.container = QWidget()
        self.grid_layout = QHBoxLayout(self.container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.setVisible(False)
    
    def load_files(self, file_paths):
        """加载多个PDF文件并显示缩略图"""
        self.clear()
        self.file_paths = list(file_paths)
        
        for i, path in enumerate(self.file_paths):
            try:
                doc = fitz.open(path)
                if len(doc) > 0:
                    page = doc[0]
                    mat = fitz.Matrix(0.25, 0.25)
                    pix = page.get_pixmap(matrix=mat)
                    img = QImage(pix.samples, pix.width, pix.height, 
                               pix.stride, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(img)
                    
                    # 创建缩略图项
                    item = self.create_thumbnail_item(i, pixmap, os.path.basename(path))
                    self.thumbnails.append(item)
                    self.grid_layout.addWidget(item)
                doc.close()
            except Exception as e:
                print(f"加载文件失败: {path}, {e}")
        
        if self.file_paths:
            self.setVisible(True)
    
    def create_thumbnail_item(self, index, pixmap, filename):
        """创建缩略图项"""
        frame = QFrame()
        frame.setFixedSize(130, 160)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e8ecf0;
                border-radius: 8px;
            }
            QFrame:hover { border-color: #3b82f6; }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        # 缩略图
        thumb = QLabel()
        scaled = pixmap.scaled(110, 100, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        thumb.setPixmap(scaled)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("background: transparent;")
        layout.addWidget(thumb)
        
        # 文件名
        name_label = QLabel(filename[:15] + "..." if len(filename) > 15 else filename)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #1e2537; font-size: 10px; background: transparent;")
        name_label.setToolTip(filename)
        layout.addWidget(name_label)
        
        # 点击事件
        frame.mousePressEvent = lambda e, idx=index: self.on_item_clicked(idx)
        
        return frame
    
    def on_item_clicked(self, index):
        """项被点击"""
        # 取消之前的选择
        if self.selected_index >= 0 and self.selected_index < len(self.thumbnails):
            self.thumbnails[self.selected_index].setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #e8ecf0;
                    border-radius: 8px;
                }
                QFrame:hover { border-color: #3b82f6; }
            """)
        
        # 选择新项
        self.selected_index = index
        if index < len(self.thumbnails):
            self.thumbnails[index].setStyleSheet("""
                QFrame {
                    background-color: #e0f2fe;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                }
            """)
        
        self.update_buttons()
    
    def update_buttons(self):
        """更新按钮状态"""
        has_selection = self.selected_index >= 0
        self.move_up_btn.setEnabled(has_selection and self.selected_index > 0)
        self.move_down_btn.setEnabled(has_selection and self.selected_index < len(self.file_paths) - 1)
        self.remove_btn.setEnabled(has_selection)
    
    def move_up(self):
        """向前移动"""
        if self.selected_index > 0:
            self.swap(self.selected_index, self.selected_index - 1)
            self.selected_index -= 1
            self.update_buttons()
    
    def move_down(self):
        """向后移动"""
        if self.selected_index < len(self.file_paths) - 1:
            self.swap(self.selected_index, self.selected_index + 1)
            self.selected_index += 1
            self.update_buttons()
    
    def swap(self, i, j):
        """交换两个文件"""
        self.file_paths[i], self.file_paths[j] = self.file_paths[j], self.file_paths[i]
        self.thumbnails[i], self.thumbnails[j] = self.thumbnails[j], self.thumbnails[i]
        self.refresh_layout()
        self.files_reordered.emit(self.file_paths)
    
    def remove_file(self):
        """移除选中的文件"""
        if self.selected_index >= 0 and self.selected_index < len(self.file_paths):
            self.file_paths.pop(self.selected_index)
            old_thumb = self.thumbnails.pop(self.selected_index)
            old_thumb.deleteLater()
            
            self.selected_index = -1
            self.update_buttons()
            self.files_reordered.emit(self.file_paths)
            
            if not self.file_paths:
                self.setVisible(False)
    
    def refresh_layout(self):
        """刷新布局"""
        for thumb in self.thumbnails:
            self.grid_layout.removeWidget(thumb)
        for thumb in self.thumbnails:
            self.grid_layout.addWidget(thumb)
    
    def clear(self):
        """清空"""
        for thumb in self.thumbnails:
            thumb.deleteLater()
        self.thumbnails = []
        self.file_paths = []
        self.selected_index = -1
    
    def get_files(self):
        """获取当前文件列表"""
        return self.file_paths


class PagePreviewWidget(QWidget):
    """PDF页面预览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # 预览区域
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #ffffff; border: 1px solid #e8ecf0; border-radius: 8px;")
        self.preview_label.setMinimumHeight(300)
        layout.addWidget(self.preview_label)
        
        # 导航栏
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; }
        """)
        self.prev_btn.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("0 / 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("color: #1e2537; font-size: 14px;")
        nav_layout.addWidget(self.page_label, 1)
        
        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { color: #9ca3af; }
        """)
        self.next_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        self.setVisible(False)
    
    def load_pdf(self, pdf_path):
        """加载PDF"""
        try:
            if self.doc:
                self.doc.close()
            self.doc = fitz.open(pdf_path)
            self.total_pages = len(self.doc)
            self.current_page = 0
            self.render_page()
            self.setVisible(True)
        except Exception as e:
            print(f"加载PDF失败: {e}")
    
    def render_page(self):
        """渲染当前页面"""
        if not self.doc or self.total_pages == 0:
            return
        
        page = self.doc[self.current_page]
        
        # 计算缩放比例以适应预览区域
        rect = page.rect
        max_width = self.preview_label.width() - 20 if self.preview_label.width() > 100 else 400
        max_height = self.preview_label.height() - 20 if self.preview_label.height() > 100 else 350
        
        scale = min(max_width / rect.width, max_height / rect.height, 1.5)
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为QPixmap
        img = QImage(pix.samples, pix.width, pix.height, 
                   pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        self.preview_label.setPixmap(pixmap)
        self.page_label.setText(f"第 {self.current_page + 1} 页 / 共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page()
    
    def close_pdf(self):
        """关闭PDF"""
        if self.doc:
            self.doc.close()
            self.doc = None
        self.setVisible(False)


class WorkerThread(QThread):
    """后台工作线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            print(f"[DEBUG] func: {self.func.__name__}")
            print(f"[DEBUG] args: {self.args}")
            print(f"[DEBUG] kwargs: {self.kwargs}")
            result = self.func(*self.args, progress_callback=self.progress.emit, **self.kwargs)
            self.finished.emit(True, result if isinstance(result, str) else "处理完成！")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF工具箱")
        self.setMinimumSize(1200, 800)
        self.current_files = []
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 侧边栏
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # 内容区域
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content")
        main_layout.addWidget(self.content_stack, 1)
        
        # 创建首页
        self.home_page = self.create_home_page()
        self.content_stack.addWidget(self.home_page)
        
        # 创建各功能页面
        self.tool_pages = {}
        for tool_id in TOOLS:
            page = self.create_tool_page(tool_id)
            self.tool_pages[tool_id] = page
            self.content_stack.addWidget(page)
    
    def create_sidebar(self):
        """创建侧边栏"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Logo
        logo = QLabel("📄 PDF工具箱")
        logo.setObjectName("logo")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937; padding: 16px 8px;")
        layout.addWidget(logo)
        
        # 分类按钮
        self.category_buttons = {}
        for category in CATEGORIES:
            btn = QPushButton(f"  {category}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=category: self.filter_category(c))
            self.category_buttons[category] = btn
            layout.addWidget(btn)
        
        self.category_buttons["全部"].setChecked(True)
        
        layout.addStretch()
        
        # 版本信息
        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #606060; font-size: 11px; padding: 8px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        return sidebar
    
    def create_home_page(self):
        """创建首页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # 标题
        header = QLabel("欢迎使用 PDF 工具箱")
        header.setObjectName("content_header")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e2537; margin-bottom: 10px;")
        layout.addWidget(header)
        
        subtitle = QLabel("选择一个工具开始处理您的PDF文件")
        subtitle.setStyleSheet("color: #6b7280; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # 工具网格（包装在滚动区域中）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.tools_container = QWidget()
        self.tools_grid = QGridLayout(self.tools_container)
        self.tools_grid.setSpacing(16)
        self.tools_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.populate_tools_grid()
        
        scroll.setWidget(self.tools_container)
        layout.addWidget(scroll, 1)
        
        return page
    
    def populate_tools_grid(self, category="全部"):
        """填充工具网格"""
        # 清空现有卡片
        while self.tools_grid.count():
            item = self.tools_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加卡片
        row, col = 0, 0
        max_cols = 3
        
        for tool_id, tool_info in TOOLS.items():
            if category != "全部" and tool_info["category"] != category:
                continue
            
            card = ToolCard(tool_id, tool_info["icon"], tool_info["title"], 
                          category=tool_info["category"])
            card.clicked.connect(self.open_tool)
            self.tools_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def filter_category(self, category):
        """按分类筛选工具"""
        # 更新按钮状态
        for cat, btn in self.category_buttons.items():
            btn.setChecked(cat == category)
        
        # 重新填充网格
        self.populate_tools_grid(category)
        
        # 显示首页
        self.content_stack.setCurrentWidget(self.home_page)
    
    def create_tool_page(self, tool_id):
        """创建工具页面"""
        tool_info = TOOLS[tool_id]
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)
        
        # 返回按钮和标题 - 修复样式
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        back_btn = QPushButton("← 返回")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 1px solid #d0d8e0;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                color: #1e2537;
                border-color: #3b82f6;
            }
        """)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.go_back(tool_id))
        back_btn.setFixedWidth(80)
        header_layout.addWidget(back_btn)
        
        title = QLabel(f"{tool_info['icon']} {tool_info['title']}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e2537;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 拖拽区域
        drop_area = DropArea(
            accept_extensions=self.get_accept_extensions(tool_id),
            multiple=self.is_multi_file_tool(tool_id)
        )
        drop_area.files_dropped.connect(lambda files: self.handle_files_dropped(tool_id, files))
        layout.addWidget(drop_area)
        
        # 页面选择组件（旋转、删除、提取）
        page_select_tools = ["rotate", "delete_pages", "extract_pages"]
        if tool_id in page_select_tools:
            page_selector = PageSelectorWidget()
            page_selector.setObjectName(f"page_selector_{tool_id}")
            layout.addWidget(page_selector)
            page.page_selector = page_selector
        
        # PDF预览区域（非重排、非页面选择工具）
        if tool_id != "reorder" and tool_id not in page_select_tools:
            preview_widget = PagePreviewWidget()
            preview_widget.setObjectName(f"preview_{tool_id}")
            layout.addWidget(preview_widget)
            page.preview_widget = preview_widget
        
        # 重排页面专用组件
        if tool_id == "reorder":
            reorder_widget = PageReorderWidget()
            reorder_widget.setObjectName("reorder_widget")
            layout.addWidget(reorder_widget)
            page.reorder_widget = reorder_widget
        
        # 选项区域（根据工具类型不同）
        options_widget = self.create_options_widget(tool_id)
        if options_widget:
            layout.addWidget(options_widget)
        
        # 文件列表（多文件工具，非合并）
        if self.is_multi_file_tool(tool_id) and tool_id != "merge":
            file_list = QListWidget()
            file_list.setObjectName(f"file_list_{tool_id}")
            file_list.setMaximumHeight(150)
            file_list.setVisible(False)
            layout.addWidget(file_list)
        
        # 合并专用多文件预览
        if tool_id == "merge":
            merge_preview = MultiFilePreviewWidget()
            merge_preview.setObjectName("merge_preview")
            merge_preview.files_reordered.connect(lambda files: self.on_merge_files_reordered(files))
            layout.addWidget(merge_preview)
            page.merge_preview = merge_preview
        
        # 进度条
        progress = QProgressBar()
        progress.setObjectName(f"progress_{tool_id}")
        progress.setVisible(False)
        progress.setMaximumHeight(10)
        layout.addWidget(progress)
        
        # 按钮区域 - 居中显示
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_layout.addStretch()
        
        # 选择文件按钮
        select_btn = QPushButton("选择文件")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e2537;
                border: 1px solid #d0d8e0;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #3b82f6;
            }
        """)
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_btn.setFixedWidth(120)
        select_btn.clicked.connect(lambda: drop_area.open_file_dialog())
        btn_layout.addWidget(select_btn)
        
        # 开始处理按钮（默认禁用灰色）
        process_btn = QPushButton("开始处理")
        process_btn.setObjectName("process_btn")
        process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        process_btn.setEnabled(False)
        process_btn.setFixedWidth(140)
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }
        """)
        process_btn.clicked.connect(lambda: self.process_tool(tool_id))
        btn_layout.addWidget(process_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        # 保存组件引用
        page.drop_area = drop_area
        page.process_btn = process_btn
        page.progress = progress
        
        return page
    
    def go_back(self, tool_id):
        """返回首页并清理预览"""
        page = self.tool_pages[tool_id]
        
        # 关闭预览
        if hasattr(page, 'preview_widget'):
            page.preview_widget.close_pdf()
        if hasattr(page, 'reorder_widget'):
            page.reorder_widget.clear()
            page.reorder_widget.setVisible(False)
        if hasattr(page, 'merge_preview'):
            page.merge_preview.clear()
            page.merge_preview.setVisible(False)
        if hasattr(page, 'page_selector'):
            page.page_selector.clear()
            page.page_selector.setVisible(False)
        
        # 重置状态
        page.drop_area.set_hint("将PDF文件拖拽到此处")
        page.process_btn.setEnabled(False)
        self.current_files = []
        
        self.content_stack.setCurrentWidget(self.home_page)
    
    def get_accept_extensions(self, tool_id):
        """获取工具接受的文件扩展名"""
        if tool_id in ["word_to_pdf"]:
            return [".docx", ".doc"]
        elif tool_id in ["jpg_to_pdf"]:
            return [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
        else:
            return [".pdf"]
    
    def is_multi_file_tool(self, tool_id):
        """判断是否为多文件工具"""
        return tool_id in ["merge", "jpg_to_pdf"]
    
    def create_options_widget(self, tool_id):
        """创建工具选项区域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 10)
        
        if tool_id == "compress":
            label = QLabel("压缩级别：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            combo = QComboBox()
            combo.addItems(["低（较大文件）", "中（推荐）", "高（较小文件）"])
            combo.setCurrentIndex(1)
            combo.setObjectName("compress_level")
            combo.setFixedWidth(200)
            layout.addWidget(combo)
            
        elif tool_id == "split":
            label = QLabel("分割方式：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            combo = QComboBox()
            combo.addItems(["每页一个文件", "按范围分割", "每N页一个文件"])
            combo.setObjectName("split_mode")
            combo.setFixedWidth(180)
            layout.addWidget(combo)
            
            range_label = QLabel("范围：")
            range_label.setStyleSheet("color: #1e2537; margin-left: 20px;")
            layout.addWidget(range_label)
            
            range_input = QLineEdit()
            range_input.setPlaceholderText("例如: 1-3, 5, 7-10")
            range_input.setObjectName("split_range")
            range_input.setFixedWidth(200)
            layout.addWidget(range_input)
            
        elif tool_id == "rotate":
            label = QLabel("旋转角度：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            combo = QComboBox()
            combo.addItems(["顺时针90°", "180°", "逆时针90°"])
            combo.setObjectName("rotate_angle")
            combo.setFixedWidth(150)
            
            # 连接信号更新预览
            def update_preview(index):
                page = self.tool_pages.get(tool_id)
                if page and hasattr(page, 'page_selector'):
                    angles = [90, 180, 270]
                    page.page_selector.set_preview_rotation(angles[index])
            
            combo.currentIndexChanged.connect(update_preview)
            layout.addWidget(combo)
            

        elif tool_id == "watermark":
            label = QLabel("水印文字：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            text_input = QLineEdit()
            text_input.setPlaceholderText("输入水印文字...")
            text_input.setObjectName("watermark_text")
            text_input.setFixedWidth(200)
            layout.addWidget(text_input)
            
            opacity_label = QLabel("透明度：")
            opacity_label.setStyleSheet("color: #1e2537; margin-left: 20px;")
            layout.addWidget(opacity_label)
            
            opacity = QSpinBox()
            opacity.setRange(10, 100)
            opacity.setValue(30)
            opacity.setSuffix("%")
            opacity.setObjectName("watermark_opacity")
            layout.addWidget(opacity)
            
        elif tool_id == "page_number":
            label = QLabel("位置：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            combo = QComboBox()
            combo.addItems(["底部居中", "底部靠右", "顶部居中", "顶部靠右"])
            combo.setObjectName("page_number_position")
            combo.setFixedWidth(150)
            layout.addWidget(combo)
            
            start_label = QLabel("起始编号：")
            start_label.setStyleSheet("color: #1e2537; margin-left: 20px;")
            layout.addWidget(start_label)
            
            start_num = QSpinBox()
            start_num.setRange(1, 9999)
            start_num.setValue(1)
            start_num.setObjectName("page_number_start")
            layout.addWidget(start_num)
            
        elif tool_id == "encrypt":
            label = QLabel("密码：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            pwd_input = QLineEdit()
            pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            pwd_input.setPlaceholderText("输入加密密码...")
            pwd_input.setObjectName("encrypt_password")
            pwd_input.setFixedWidth(200)
            layout.addWidget(pwd_input)
            
        elif tool_id == "decrypt":
            label = QLabel("密码：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            pwd_input = QLineEdit()
            pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            pwd_input.setPlaceholderText("输入PDF密码...")
            pwd_input.setObjectName("decrypt_password")
            pwd_input.setFixedWidth(200)
            layout.addWidget(pwd_input)
            
        elif tool_id == "pdf_to_jpg":
            label = QLabel("DPI：")
            label.setStyleSheet("color: #1e2537;")
            layout.addWidget(label)
            
            dpi = QSpinBox()
            dpi.setRange(72, 600)
            dpi.setValue(150)
            dpi.setObjectName("image_dpi")
            layout.addWidget(dpi)
            
            format_label = QLabel("格式：")
            format_label.setStyleSheet("color: #1e2537; margin-left: 20px;")
            layout.addWidget(format_label)
            
            format_combo = QComboBox()
            format_combo.addItems(["PNG", "JPEG"])
            format_combo.setObjectName("image_format")
            format_combo.setFixedWidth(100)
            layout.addWidget(format_combo)
        
        layout.addStretch()
        
        # 如果没有选项则返回None（重排页面不需要额外选项）
        if layout.count() <= 1 or tool_id == "reorder":
            widget.deleteLater()
            return None
        
        return widget
    
    def open_tool(self, tool_id):
        """打开工具页面"""
        if tool_id in self.tool_pages:
            self.current_files = []
            page = self.tool_pages[tool_id]
            page.process_btn.setEnabled(False)
            self.content_stack.setCurrentWidget(page)
    
    def handle_files_dropped(self, tool_id, files):
        """处理文件拖放"""
        self.current_files = files
        page = self.tool_pages[tool_id]
        
        # 合并工具使用多文件预览
        if tool_id == "merge" and hasattr(page, 'merge_preview'):
            page.merge_preview.load_files(files)
        # 其他多文件工具使用列表
        elif self.is_multi_file_tool(tool_id):
            file_list = page.findChild(QListWidget, f"file_list_{tool_id}")
            if file_list:
                file_list.clear()
                for f in files:
                    file_list.addItem(os.path.basename(f))
                file_list.setVisible(True)
        
        # 启用处理按钮（合并需要至少2个文件）
        if tool_id == "merge":
            page.process_btn.setEnabled(len(files) >= 2)
        else:
            page.process_btn.setEnabled(len(files) > 0)
        
        # 更新拖拽区域提示
        if len(files) == 1:
            page.drop_area.set_hint(f"已选择: {os.path.basename(files[0])}")
        else:
            page.drop_area.set_hint(f"已选择 {len(files)} 个文件")
        
        # 页面选择工具使用 PageSelectorWidget
        page_select_tools = ["rotate", "delete_pages", "extract_pages"]
        if tool_id in page_select_tools and len(files) == 1 and files[0].lower().endswith('.pdf'):
            if hasattr(page, 'page_selector'):
                page.page_selector.load_pdf(files[0])
                # 如果是旋转工具，初始化预览角度
                if tool_id == "rotate":
                    combo = page.findChild(QComboBox, "rotate_angle")
                    if combo:
                        angles = [90, 180, 270]
                        page.page_selector.set_preview_rotation(angles[combo.currentIndex()])
        # 加载PDF预览（单文件非合并非页面选择工具）
        elif len(files) == 1 and files[0].lower().endswith('.pdf') and tool_id != "merge":
            # 重排页面使用特殊组件
            if tool_id == "reorder" and hasattr(page, 'reorder_widget'):
                page.reorder_widget.load_pdf(files[0])
            # 其他工具显示普通预览
            elif hasattr(page, 'preview_widget'):
                page.preview_widget.load_pdf(files[0])
    
    def on_merge_files_reordered(self, files):
        """合并文件顺序改变回调"""
        self.current_files = files
        # 更新按钮状态
        page = self.tool_pages.get("merge")
        if page:
            page.process_btn.setEnabled(len(files) >= 2)
            if len(files) == 0:
                page.drop_area.set_hint("将PDF文件拖拽到此处")
            else:
                page.drop_area.set_hint(f"已选择 {len(files)} 个文件")

    
    def process_tool(self, tool_id):
        """处理工具操作"""
        if not self.current_files:
            return
        
        page = self.tool_pages[tool_id]
        
        # 选择保存位置
        if tool_id in ["pdf_to_jpg", "split"]:
            output_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
            if not output_path:
                return
        else:
            default_name = self.get_default_output_name(tool_id)
            output_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", default_name, 
                self.get_save_filter(tool_id)
            )
            if not output_path:
                return
        
        # 获取选项
        options = self.get_tool_options(tool_id, page)
        
        # 显示进度
        page.progress.setValue(0)
        page.progress.setVisible(True)
        page.process_btn.setEnabled(False)
        
        # 执行处理
        try:
            self.execute_tool(tool_id, self.current_files, output_path, options, page)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败：{str(e)}")
            page.progress.setVisible(False)
            page.process_btn.setEnabled(True)
    
    def get_default_output_name(self, tool_id):
        """获取默认输出文件名"""
        if not self.current_files:
            return "output"
        
        base_name = os.path.splitext(os.path.basename(self.current_files[0]))[0]
        
        suffix_map = {
            "compress": "_compressed.pdf",
            "merge": "_merged.pdf",
            "rotate": "_rotated.pdf",
            "delete_pages": "_deleted.pdf",
            "extract_pages": "_extracted.pdf",
            "reorder": "_reordered.pdf",
            "pdf_to_word": ".docx",
            "pdf_to_excel": ".xlsx",
            "pdf_to_ppt": ".pptx",
            "word_to_pdf": ".pdf",
            "jpg_to_pdf": ".pdf",
            "watermark": "_watermarked.pdf",
            "page_number": "_numbered.pdf",
            "crop": "_cropped.pdf",
            "encrypt": "_encrypted.pdf",
            "decrypt": "_decrypted.pdf",
            "flatten": "_flattened.pdf",
            "ocr": "_ocr.pdf",
        }
        
        return base_name + suffix_map.get(tool_id, "_output.pdf")
    
    def get_save_filter(self, tool_id):
        """获取保存文件过滤器"""
        filters = {
            "pdf_to_word": "Word文档 (*.docx)",
            "pdf_to_excel": "Excel表格 (*.xlsx)",
            "pdf_to_ppt": "PowerPoint演示文稿 (*.pptx)",
        }
        return filters.get(tool_id, "PDF文件 (*.pdf)")
    
    def get_tool_options(self, tool_id, page):
        """获取工具选项"""
        options = {}
        
        if tool_id == "compress":
            combo = page.findChild(QComboBox, "compress_level")
            if combo:
                options["level"] = combo.currentIndex()
        
        elif tool_id == "split":
            combo = page.findChild(QComboBox, "split_mode")
            range_input = page.findChild(QLineEdit, "split_range")
            if combo:
                options["mode"] = combo.currentIndex()
            if range_input:
                options["range"] = range_input.text()
        
        elif tool_id == "rotate":
            combo = page.findChild(QComboBox, "rotate_angle")
            if combo:
                angles = [90, 180, 270]
                options["angle"] = angles[combo.currentIndex()]
            # 从页面选择器获取选中页面
            if hasattr(page, 'page_selector'):
                selected = page.page_selector.get_selected_pages()
                if selected:
                    options["pages"] = ",".join(str(p) for p in selected)
        
        elif tool_id in ["delete_pages", "extract_pages"]:
            # 从页面选择器获取选中页面
            if hasattr(page, 'page_selector'):
                selected = page.page_selector.get_selected_pages()
                if selected:
                    options["pages"] = ",".join(str(p) for p in selected)
        
        elif tool_id == "reorder":
            # 获取重排后的顺序
            if hasattr(page, 'reorder_widget'):
                order = page.reorder_widget.get_order()
                if order:
                    # 转换为1-indexed的字符串
                    options["order"] = ",".join(str(i + 1) for i in order)
        
        elif tool_id == "watermark":
            text_input = page.findChild(QLineEdit, "watermark_text")
            opacity = page.findChild(QSpinBox, "watermark_opacity")
            if text_input:
                options["text"] = text_input.text()
            if opacity:
                options["opacity"] = opacity.value() / 100
        
        elif tool_id == "page_number":
            combo = page.findChild(QComboBox, "page_number_position")
            start = page.findChild(QSpinBox, "page_number_start")
            if combo:
                options["position"] = combo.currentIndex()
            if start:
                options["start"] = start.value()
        
        elif tool_id == "encrypt":
            pwd_input = page.findChild(QLineEdit, "encrypt_password")
            if pwd_input:
                options["password"] = pwd_input.text()
        
        elif tool_id == "decrypt":
            pwd_input = page.findChild(QLineEdit, "decrypt_password")
            if pwd_input:
                options["password"] = pwd_input.text()
        
        elif tool_id == "pdf_to_jpg":
            dpi = page.findChild(QSpinBox, "image_dpi")
            format_combo = page.findChild(QComboBox, "image_format")
            if dpi:
                options["dpi"] = dpi.value()
            if format_combo:
                options["format"] = format_combo.currentText().lower()
        
        return options
    
    def execute_tool(self, tool_id, files, output_path, options, page):
        """执行工具操作"""
        from core import compress, merge, split, rotate, pages, convert, watermark, security, ocr
        
        func_map = {
            "compress": compress.compress_pdf,
            "merge": merge.merge_pdfs,
            "split": split.split_pdf,
            "rotate": rotate.rotate_pdf,
            "delete_pages": pages.delete_pages,
            "extract_pages": pages.extract_pages,
            "reorder": pages.reorder_pages,
            "pdf_to_word": convert.pdf_to_word,
            "pdf_to_excel": convert.pdf_to_excel,
            "pdf_to_ppt": convert.pdf_to_ppt,
            "pdf_to_jpg": convert.pdf_to_images,
            "word_to_pdf": convert.word_to_pdf,
            "jpg_to_pdf": convert.images_to_pdf,
            "watermark": watermark.add_watermark,
            "page_number": watermark.add_page_numbers,
            "crop": pages.crop_pdf,
            "encrypt": security.encrypt_pdf,
            "decrypt": security.decrypt_pdf,
            "flatten": security.flatten_pdf,
            "ocr": ocr.ocr_pdf,
        }
        
        func = func_map.get(tool_id)
        if not func:
            raise ValueError(f"未知工具: {tool_id}")
        
        # 在后台线程执行
        self.worker = WorkerThread(func, files[0] if len(files) == 1 else files, output_path, **options)
        self.worker.progress.connect(lambda v: page.progress.setValue(v))
        self.worker.finished.connect(lambda ok, msg: self.on_process_finished(ok, msg, page))
        self.worker.start()
    
    def on_process_finished(self, success, message, page):
        """处理完成回调"""
        page.progress.setVisible(False)
        page.process_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.critical(self, "错误", f"处理失败：{message}")
