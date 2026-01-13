#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR功能 - 识别扫描PDF中的文字
"""

import os
import fitz  # PyMuPDF


def ocr_pdf(input_path: str, output_path: str, language: str = "chi_sim+eng",
            progress_callback=None):
    """
    对扫描PDF进行OCR识别，生成可搜索的PDF
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        language: OCR语言 (chi_sim=简体中文, eng=英文, jpn=日文)
        progress_callback: 进度回调函数
    
    Note:
        需要安装 Tesseract OCR:
        - macOS: brew install tesseract tesseract-lang
        - Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError("请安装 pytesseract 和 Pillow: pip install pytesseract Pillow")
    
    # 检查 Tesseract 是否已安装
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        raise RuntimeError(
            "未检测到 Tesseract OCR。请先安装：\n"
            "macOS: brew install tesseract tesseract-lang\n"
            "Windows: 下载 https://github.com/UB-Mannheim/tesseract/wiki"
        )
    
    if progress_callback:
        progress_callback(5)
    
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 创建新的PDF用于存储OCR结果
    output_doc = fitz.open()
    
    for i, page in enumerate(doc):
        if progress_callback:
            progress_callback(5 + int((i / total_pages) * 90))
        
        # 渲染页面为高分辨率图片
        zoom = 2.0  # 提高分辨率以获得更好的OCR效果
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # 保存临时图片
        temp_img_path = f"/tmp/ocr_page_{i}.png"
        pix.save(temp_img_path)
        
        # 使用 Tesseract 进行 OCR
        try:
            img = Image.open(temp_img_path)
            
            # 获取OCR结果（包含位置信息）
            ocr_data = pytesseract.image_to_data(
                img, 
                lang=language, 
                output_type=pytesseract.Output.DICT
            )
            
            # 同时获取纯文本用于创建可搜索层
            text = pytesseract.image_to_string(img, lang=language)
            
        except Exception as e:
            # OCR失败时继续处理下一页
            os.remove(temp_img_path)
            # 直接复制原页面
            output_doc.insert_pdf(doc, from_page=i, to_page=i)
            continue
        
        # 创建新页面，保持原始尺寸
        new_page = output_doc.new_page(
            width=page.rect.width,
            height=page.rect.height
        )
        
        # 插入原始页面图像
        img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        new_page.insert_image(img_rect, filename=temp_img_path)
        
        # 添加隐藏的文字层（使PDF可搜索）
        scale = 1 / zoom
        
        n_boxes = len(ocr_data['level'])
        for j in range(n_boxes):
            if ocr_data['text'][j].strip():
                # 获取文字位置
                x = ocr_data['left'][j] * scale
                y = ocr_data['top'][j] * scale
                w = ocr_data['width'][j] * scale
                h = ocr_data['height'][j] * scale
                
                word = ocr_data['text'][j]
                
                # 在对应位置添加透明文字
                try:
                    # 计算合适的字体大小
                    fontsize = max(6, min(h * 0.8, 72))
                    
                    # 添加透明文字（透明度设为0使其不可见但可搜索）
                    new_page.insert_text(
                        fitz.Point(x, y + h * 0.8),
                        word,
                        fontsize=fontsize,
                        fontname="helv",
                        color=(1, 1, 1),  # 白色
                        fill_opacity=0,  # 完全透明
                        overlay=True
                    )
                except Exception:
                    # 忽略插入失败的文字
                    pass
        
        # 清理临时文件
        os.remove(temp_img_path)
    
    doc.close()
    
    if progress_callback:
        progress_callback(95)
    
    # 保存输出PDF
    output_doc.save(output_path, garbage=4, deflate=True)
    output_doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"OCR完成！已保存到 {output_path}"


def extract_text_ocr(input_path: str, output_path: str = None, 
                     language: str = "chi_sim+eng", progress_callback=None):
    """
    使用OCR提取PDF中的文字
    
    Args:
        input_path: 输入PDF路径
        output_path: 输出文本文件路径（可选）
        language: OCR语言
        progress_callback: 进度回调函数
    
    Returns:
        提取的文字内容
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError("请安装 pytesseract 和 Pillow")
    
    doc = fitz.open(input_path)
    total_pages = len(doc)
    all_text = []
    
    for i, page in enumerate(doc):
        # 渲染页面
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # 保存临时图片
        temp_img = f"/tmp/extract_page_{i}.png"
        pix.save(temp_img)
        
        # OCR识别
        img = Image.open(temp_img)
        text = pytesseract.image_to_string(img, lang=language)
        all_text.append(f"--- 第 {i+1} 页 ---\n{text}")
        
        os.remove(temp_img)
        
        if progress_callback:
            progress_callback(int((i + 1) / total_pages * 100))
    
    doc.close()
    
    result = "\n\n".join(all_text)
    
    # 如果指定了输出文件，保存文本
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return f"文字已提取并保存到 {output_path}"
    
    return result
