# PDF 工具箱 (macOS)

一个功能强大的 macOS PDF 工具箱，界面简洁，功能齐全。

![主界面预览](assets/preview.png)

## 功能特性

- 📦 **PDF压缩** - 减小PDF文件大小
- 📑 **合并PDF** - 将多个PDF合并为一个
- ✂️ **分割PDF** - 按页面范围分割PDF
- 🔄 **旋转PDF** - 旋转PDF页面
- 📄 **页面操作** - 删除、提取、重排页面
- 🔄 **格式转换** - PDF与Word/Excel/PPT/JPG互转
- 💧 **水印** - 添加文字或图片水印
- 🔒 **安全** - PDF加密、解密、展平
- 📝 **OCR** - 识别扫描PDF中的文字

## 安装与运行

### 快速启动
双击 `run_mac.command` 即可运行，首次运行会自动安装依赖。

### 手动安装
```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行
python3 main.py
```

### OCR功能（可选）
```bash
brew install tesseract tesseract-lang
```

## 系统要求

- macOS 10.15+
- Python 3.9+

## 技术栈

- PyQt6 - GUI框架
- PyMuPDF - PDF处理
- pdf2docx - PDF转Word

## 许可证

MIT License
