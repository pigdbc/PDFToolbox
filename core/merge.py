#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF合并功能
"""

import fitz  # PyMuPDF


def merge_pdfs(input_paths, output_path: str, progress_callback=None):
    """
    合并多个PDF文件
    
    Args:
        input_paths: 输入文件路径列表
        output_path: 输出文件路径
        progress_callback: 进度回调函数
    """
    if isinstance(input_paths, str):
        input_paths = [input_paths]
    
    if len(input_paths) < 2:
        raise ValueError("至少需要2个PDF文件进行合并")
    
    # 创建新的PDF文档
    output_doc = fitz.open()
    total_files = len(input_paths)
    
    for i, path in enumerate(input_paths):
        try:
            doc = fitz.open(path)
            output_doc.insert_pdf(doc)
            doc.close()
        except Exception as e:
            raise ValueError(f"无法打开文件 {path}: {str(e)}")
        
        if progress_callback:
            progress_callback(int((i + 1) / total_files * 90))
    
    # 保存
    output_doc.save(output_path)
    output_doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"合并完成！已将 {total_files} 个文件合并为 {output_path}"
