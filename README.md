# PDF Toolbox / PDF工具箱

每个功能都精心设计，简单易用。

![主界面预览](assets/preview.png)

一个功能强大的跨平台PDF工具箱，支持Windows和macOS。

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

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR（可选，用于OCR功能）

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

## 运行

```bash
python main.py
```

## 打包为可执行文件

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --name "PDF工具箱" main.py
```

## 技术栈

- Python 3.9+
- PyQt6 - GUI框架
- PyMuPDF - PDF处理
- pdf2docx - PDF转Word
- 其他依赖见 requirements.txt

## 许可证

MIT License
