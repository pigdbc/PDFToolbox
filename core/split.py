#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF分割功能
"""

import os
import fitz  # PyMuPDF


def parse_page_range(range_str: str, total_pages: int) -> list:
    """
    解析页面范围字符串
    
    Args:
        range_str: 页面范围字符串，如 "1-3, 5, 7-10"
        total_pages: 总页数
    
    Returns:
        页面索引列表 (0-indexed)
    """
    if not range_str or range_str.strip() == "":
        return list(range(total_pages))
    
    pages = []
    parts = range_str.replace(" ", "").split(",")
    
    for part in parts:
        if "-" in part:
            start_end = part.split("-")
            if len(start_end) == 2:
                try:
                    start = int(start_end[0]) - 1  # 转为0索引
                    end = int(start_end[1])  # 不减1，因为range是半开区间
                    start = max(0, start)
                    end = min(total_pages, end)
                    pages.extend(range(start, end))
                except ValueError:
                    pass
        else:
            try:
                page_num = int(part) - 1  # 转为0索引
                if 0 <= page_num < total_pages:
                    pages.append(page_num)
            except ValueError:
                pass
    
    return sorted(set(pages))


def split_pdf(input_path: str, output_dir: str, mode: int = 0, 
              range: str = "", n_pages: int = 1, progress_callback=None):
    """
    分割PDF文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        mode: 分割模式 (0=每页一个文件, 1=按范围分割, 2=每N页一个文件)
        range: 页面范围 (mode=1时使用)
        n_pages: 每个文件的页数 (mode=2时使用)
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_files = []
    
    if mode == 0:  # 每页一个文件
        for i in range(total_pages):
            output_path = os.path.join(output_dir, f"{base_name}_page{i+1}.pdf")
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)
            
            if progress_callback:
                progress_callback(int((i + 1) / total_pages * 100))
    
    elif mode == 1:  # 按范围分割
        pages = parse_page_range(range, total_pages)
        if not pages:
            raise ValueError("无效的页面范围")
        
        output_path = os.path.join(output_dir, f"{base_name}_extracted.pdf")
        new_doc = fitz.open()
        
        for i, page_idx in enumerate(pages):
            new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
            if progress_callback:
                progress_callback(int((i + 1) / len(pages) * 100))
        
        new_doc.save(output_path)
        new_doc.close()
        output_files.append(output_path)
    
    elif mode == 2:  # 每N页一个文件
        n_pages = max(1, n_pages)
        file_count = 0
        
        for start in range(0, total_pages, n_pages):
            end = min(start + n_pages - 1, total_pages - 1)
            file_count += 1
            output_path = os.path.join(output_dir, f"{base_name}_part{file_count}.pdf")
            
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)
            
            if progress_callback:
                progress_callback(int((start + n_pages) / total_pages * 100))
    
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"分割完成！生成了 {len(output_files)} 个文件到 {output_dir}"
