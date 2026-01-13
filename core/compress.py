#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF压缩功能
"""

import fitz  # PyMuPDF


def compress_pdf(input_path: str, output_path: str, level: int = 1, progress_callback=None):
    """
    压缩PDF文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        level: 压缩级别 (0=低, 1=中, 2=高)
        progress_callback: 进度回调函数
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 根据压缩级别设置参数
    if level == 0:  # 低压缩
        garbage = 1
        deflate = False
        deflate_images = False
        deflate_fonts = False
    elif level == 1:  # 中压缩
        garbage = 2
        deflate = True
        deflate_images = True
        deflate_fonts = True
    else:  # 高压缩
        garbage = 4
        deflate = True
        deflate_images = True
        deflate_fonts = True
    
    # 处理每一页（用于进度显示）
    for i, page in enumerate(doc):
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 80))
        
        # 高压缩级别时降低图片质量
        if level == 2:
            for img in page.get_images():
                xref = img[0]
                try:
                    # 尝试压缩图片
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n >= 4:  # CMYK或带alpha通道
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    # 降低分辨率
                    if pix.width > 1200 or pix.height > 1200:
                        scale = 1200 / max(pix.width, pix.height)
                        new_width = int(pix.width * scale)
                        new_height = int(pix.height * scale)
                        pix = fitz.Pixmap(pix, new_width, new_height)
                except Exception:
                    pass
    
    if progress_callback:
        progress_callback(90)
    
    # 保存压缩后的PDF
    doc.save(
        output_path,
        garbage=garbage,
        deflate=deflate,
        deflate_images=deflate_images,
        deflate_fonts=deflate_fonts,
        clean=True
    )
    
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"压缩完成！已保存到 {output_path}"
