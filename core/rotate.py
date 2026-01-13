#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF旋转功能
"""

import fitz  # PyMuPDF
from core.split import parse_page_range


def rotate_pdf(input_path: str, output_path: str, angle: int = 90, 
               pages: str = "", progress_callback=None):
    """
    旋转PDF页面
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        angle: 旋转角度 (90, 180, 270)
        pages: 要旋转的页面范围，空则旋转所有页面
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 解析要旋转的页面
    if pages and pages.strip():
        page_list = parse_page_range(pages, total_pages)
    else:
        page_list = list(range(total_pages))
    
    # 旋转页面
    for i, page_idx in enumerate(page_list):
        page = doc[page_idx]
        page.set_rotation(page.rotation + angle)
        
        if progress_callback:
            progress_callback(int((i + 1) / len(page_list) * 90))
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"旋转完成！已旋转 {len(page_list)} 页，保存到 {output_path}"
