#!/bin/bash
# PDF工具箱 DMG 打包脚本
# 用法: ./build_dmg.sh

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="PDF工具箱"
VERSION="1.1.1"
DMG_NAME="${APP_NAME}-v${VERSION}-macOS"

echo "=========================================="
echo "  PDF工具箱 DMG 打包脚本"
echo "  版本: $VERSION"
echo "=========================================="
echo ""

# 检查依赖
echo "📦 检查依赖..."

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行一次应用以创建环境"
    exit 1
fi

source venv/bin/activate

# 安装 PyInstaller
if ! python -c "import PyInstaller" &> /dev/null; then
    echo "⚠️  PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

if ! command -v create-dmg &> /dev/null; then
    echo "⚠️  create-dmg 未安装，正在通过 Homebrew 安装..."
    if ! command -v brew &> /dev/null; then
        echo "❌ 需要先安装 Homebrew: https://brew.sh"
        exit 1
    fi
    brew install create-dmg
fi

echo "✅ 依赖检查完成"
echo ""

# 清理旧的构建
echo "🧹 清理旧的构建产物..."
rm -rf build dist "${DMG_NAME}.dmg"
echo "✅ 清理完成"
echo ""

# 使用 PyInstaller 打包
echo "🔨 开始打包应用程序..."
echo "   这可能需要几分钟，请耐心等待..."
pyinstaller PDFToolbox.spec --noconfirm

if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 打包失败：未找到 .app 文件"
    exit 1
fi

echo "✅ 应用程序打包完成"
echo ""

# 创建 DMG
echo "💿 创建 DMG 安装包..."

# 创建临时目录用于 DMG 内容
DMG_TEMP="dist/dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# 复制 app 到临时目录
cp -R "dist/${APP_NAME}.app" "$DMG_TEMP/"

# 创建 Applications 链接
ln -s /Applications "$DMG_TEMP/Applications"

# 使用 create-dmg 创建漂亮的 DMG
create-dmg \
    --volname "${APP_NAME}" \
    --volicon "assets/preview.png" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 150 185 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 450 185 \
    "dist/${DMG_NAME}.dmg" \
    "$DMG_TEMP" \
    || {
        # create-dmg 可能因为缺少某些选项而失败，使用简单方式创建
        echo "⚠️  使用简化方式创建 DMG..."
        hdiutil create -volname "${APP_NAME}" \
            -srcfolder "$DMG_TEMP" \
            -ov -format UDZO \
            "dist/${DMG_NAME}.dmg"
    }

# 清理临时目录
rm -rf "$DMG_TEMP"

echo ""
echo "=========================================="
echo "  ✅ 打包完成！"
echo "=========================================="
echo ""
echo "📍 产物位置:"
echo "   应用程序: dist/${APP_NAME}.app"
echo "   DMG安装包: dist/${DMG_NAME}.dmg"
echo ""
echo "📦 DMG 大小: $(du -h "dist/${DMG_NAME}.dmg" | cut -f1)"
echo ""
echo "🎉 可以分发给其他用户使用了！"
