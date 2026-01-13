#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF水印和页码功能
"""

import fitz  # PyMuPDF


def add_watermark(input_path: str, output_path: str, text: str = "WATERMARK",
                  opacity: float = 0.3, angle: float = 45, 
                  progress_callback=None):
    """
    添加文字水印
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        text: 水印文字
        opacity: 透明度 (0-1)
        angle: 旋转角度
        progress_callback: 进度回调函数
    """
    if not text or not text.strip():
        raise ValueError("请输入水印文字")
    
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 水印颜色（灰色带透明度）
    color = (0.5, 0.5, 0.5)
    
    for i, page in enumerate(doc):
        rect = page.rect
        
        # 计算水印位置（页面中心）
        center_x = rect.width / 2
        center_y = rect.height / 2
        
        # 添加水印文字
        # 创建多个水印覆盖整个页面
        positions = [
            (center_x, center_y),
            (center_x, center_y - 200),
            (center_x, center_y + 200),
        ]
        
        for pos_x, pos_y in positions:
            text_point = fitz.Point(pos_x, pos_y)
            
            # 插入文字
            page.insert_text(
                text_point,
                text,
                fontsize=60,
                fontname="helv",
                color=color,
                rotate=angle,
                overlay=True,
                fill_opacity=opacity
            )
        
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 90))
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"水印添加完成！已保存到 {output_path}"


def add_image_watermark(input_path: str, output_path: str, image_path: str,
                        opacity: float = 0.3, position: str = "center",
                        progress_callback=None):
    """
    添加图片水印
    
    Args:
        input_path: 输入PDF路径
        output_path: 输出PDF路径
        image_path: 水印图片路径
        opacity: 透明度 (0-1)
        position: 位置 (center, corner)
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 打开水印图片
    watermark_img = fitz.open(image_path)
    watermark_page = watermark_img[0]
    watermark_rect = watermark_page.rect
    
    for i, page in enumerate(doc):
        rect = page.rect
        
        # 计算水印位置
        if position == "center":
            # 居中放置
            scale = min(rect.width / watermark_rect.width, 
                       rect.height / watermark_rect.height) * 0.5
            w = watermark_rect.width * scale
            h = watermark_rect.height * scale
            x = (rect.width - w) / 2
            y = (rect.height - h) / 2
        else:  # corner - 右下角
            scale = 0.2
            w = watermark_rect.width * scale
            h = watermark_rect.height * scale
            x = rect.width - w - 20
            y = rect.height - h - 20
        
        target_rect = fitz.Rect(x, y, x + w, y + h)
        
        # 插入图片
        page.insert_image(target_rect, filename=image_path, overlay=True)
        
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 90))
    
    watermark_img.close()
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"图片水印添加完成！已保存到 {output_path}"


def add_page_numbers(input_path: str, output_path: str, position: int = 0,
                     start: int = 1, format_str: str = "{page}", 
                     progress_callback=None):
    """
    添加页码
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        position: 位置 (0=底部居中, 1=底部靠右, 2=顶部居中, 3=顶部靠右)
        start: 起始页码
        format_str: 页码格式，{page}表示页码，{total}表示总页数
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    for i, page in enumerate(doc):
        rect = page.rect
        page_num = start + i
        
        # 格式化页码文字
        text = format_str.format(page=page_num, total=total_pages)
        
        # 计算位置
        margin = 30
        fontsize = 12
        
        if position == 0:  # 底部居中
            x = rect.width / 2
            y = rect.height - margin
        elif position == 1:  # 底部靠右
            x = rect.width - margin
            y = rect.height - margin
        elif position == 2:  # 顶部居中
            x = rect.width / 2
            y = margin + fontsize
        else:  # 顶部靠右
            x = rect.width - margin
            y = margin + fontsize
        
        text_point = fitz.Point(x, y)
        
        # 插入页码
        page.insert_text(
            text_point,
            text,
            fontsize=fontsize,
            fontname="helv",
            color=(0, 0, 0),
            overlay=True
        )
        
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 90))
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"页码添加完成！已保存到 {output_path}"
