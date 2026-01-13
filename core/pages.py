#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF页面操作功能
"""

import fitz  # PyMuPDF
from core.split import parse_page_range


def delete_pages(input_path: str, output_path: str, pages: str = "", 
                 progress_callback=None):
    """
    删除PDF页面
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        pages: 要删除的页面范围
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    if not pages or not pages.strip():
        raise ValueError("请指定要删除的页面")
    
    # 解析要删除的页面
    pages_to_delete = parse_page_range(pages, total_pages)
    
    if not pages_to_delete:
        raise ValueError("无效的页面范围")
    
    if len(pages_to_delete) >= total_pages:
        raise ValueError("不能删除所有页面")
    
    if progress_callback:
        progress_callback(30)
    
    # 从后往前删除，避免索引问题
    for page_idx in sorted(pages_to_delete, reverse=True):
        doc.delete_page(page_idx)
    
    if progress_callback:
        progress_callback(80)
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"删除完成！已删除 {len(pages_to_delete)} 页，保存到 {output_path}"


def extract_pages(input_path: str, output_path: str, pages: str = "", 
                  progress_callback=None):
    """
    提取PDF页面
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        pages: 要提取的页面范围
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    if not pages or not pages.strip():
        raise ValueError("请指定要提取的页面")
    
    # 解析要提取的页面
    pages_to_extract = parse_page_range(pages, total_pages)
    
    if not pages_to_extract:
        raise ValueError("无效的页面范围")
    
    if progress_callback:
        progress_callback(20)
    
    # 创建新文档并插入页面
    new_doc = fitz.open()
    
    for i, page_idx in enumerate(pages_to_extract):
        new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
        if progress_callback:
            progress_callback(20 + int((i + 1) / len(pages_to_extract) * 70))
    
    # 保存
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"提取完成！已提取 {len(pages_to_extract)} 页，保存到 {output_path}"


def reorder_pages(input_path: str, output_path: str, order: str = "", 
                  progress_callback=None):
    """
    重新排列PDF页面
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        order: 新的页面顺序，如 "3,1,2,5,4"
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    if not order or not order.strip():
        # 默认反转顺序
        new_order = list(range(total_pages - 1, -1, -1))
    else:
        new_order = parse_page_range(order, total_pages)
    
    if not new_order:
        raise ValueError("无效的页面顺序")
    
    if progress_callback:
        progress_callback(20)
    
    # 创建新文档
    new_doc = fitz.open()
    
    for i, page_idx in enumerate(new_order):
        if 0 <= page_idx < total_pages:
            new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
        
        if progress_callback:
            progress_callback(20 + int((i + 1) / len(new_order) * 70))
    
    # 保存
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"重排完成！保存到 {output_path}"


def crop_pdf(input_path: str, output_path: str, margins: dict = None, 
             progress_callback=None):
    """
    裁剪PDF页面边距
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        margins: 边距字典 {"left": 20, "top": 20, "right": 20, "bottom": 20}
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    if margins is None:
        margins = {"left": 20, "top": 20, "right": 20, "bottom": 20}
    
    for i, page in enumerate(doc):
        rect = page.rect
        # 创建新的裁剪区域
        new_rect = fitz.Rect(
            rect.x0 + margins.get("left", 0),
            rect.y0 + margins.get("top", 0),
            rect.x1 - margins.get("right", 0),
            rect.y1 - margins.get("bottom", 0)
        )
        page.set_cropbox(new_rect)
        
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 90))
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"裁剪完成！保存到 {output_path}"
