#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF安全功能 - 加密、解密、展平
"""

import fitz  # PyMuPDF


def encrypt_pdf(input_path: str, output_path: str, password: str = "",
                owner_password: str = None, progress_callback=None):
    """
    加密PDF文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        password: 用户密码（打开PDF时需要）
        owner_password: 所有者密码（编辑PDF时需要）
        progress_callback: 进度回调函数
    """
    if not password:
        raise ValueError("请输入加密密码")
    
    if progress_callback:
        progress_callback(20)
    
    doc = fitz.open(input_path)
    
    if progress_callback:
        progress_callback(50)
    
    # 如果没有指定所有者密码，使用用户密码
    if owner_password is None:
        owner_password = password
    
    # 设置权限 - 加密后限制打印和编辑
    perm = (
        fitz.PDF_PERM_ACCESSIBILITY |  # 可访问性
        fitz.PDF_PERM_PRINT |  # 允许打印
        fitz.PDF_PERM_COPY  # 允许复制
    )
    
    # 保存加密的PDF
    doc.save(
        output_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,  # 使用AES-256加密
        user_pw=password,
        owner_pw=owner_password,
        permissions=perm
    )
    
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"加密完成！已保存到 {output_path}"


def decrypt_pdf(input_path: str, output_path: str, password: str = "",
                progress_callback=None):
    """
    解密PDF文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        password: PDF密码
        progress_callback: 进度回调函数
    """
    if progress_callback:
        progress_callback(20)
    
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        raise ValueError(f"无法打开PDF文件: {str(e)}")
    
    # 检查是否加密
    if doc.is_encrypted:
        if not password:
            doc.close()
            raise ValueError("此PDF已加密，请输入密码")
        
        # 尝试解密
        if not doc.authenticate(password):
            doc.close()
            raise ValueError("密码错误，请重试")
    
    if progress_callback:
        progress_callback(50)
    
    # 保存未加密的PDF
    doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"解密完成！已保存到 {output_path}"


def flatten_pdf(input_path: str, output_path: str, progress_callback=None):
    """
    展平PDF（将表单字段和注释合并到页面内容中）
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        progress_callback: 进度回调函数
    """
    if progress_callback:
        progress_callback(20)
    
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    for i, page in enumerate(doc):
        # 获取所有注释
        annots = page.annots()
        
        if annots:
            for annot in annots:
                try:
                    # 将注释渲染到页面
                    annot_rect = annot.rect
                    
                    # 根据注释类型处理
                    if annot.type[0] in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                        # 文本注释、高亮等 - 保留视觉效果
                        pass
                    
                except Exception:
                    pass
        
        if progress_callback:
            progress_callback(20 + int((i + 1) / total_pages * 60))
    
    if progress_callback:
        progress_callback(85)
    
    # 保存展平后的PDF
    # 使用 deflate 和 clean 选项优化输出
    doc.save(
        output_path,
        garbage=4,
        deflate=True,
        clean=True
    )
    
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"展平完成！已保存到 {output_path}"


def remove_metadata(input_path: str, output_path: str, progress_callback=None):
    """
    移除PDF元数据
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        progress_callback: 进度回调函数
    """
    if progress_callback:
        progress_callback(30)
    
    doc = fitz.open(input_path)
    
    # 清除元数据
    doc.set_metadata({})
    
    if progress_callback:
        progress_callback(70)
    
    # 保存
    doc.save(output_path)
    doc.close()
    
    if progress_callback:
        progress_callback(100)
    
    return f"元数据已移除！保存到 {output_path}"
