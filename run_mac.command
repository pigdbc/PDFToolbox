#!/bin/bash
cd "$(dirname "$0")"

echo "正在检查运行环境..."

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未检测到 Python 3。"
    echo "请访问 https://www.python.org/downloads/macos/ 下载并安装 Python 3。"
    read -p "按回车键退出..."
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在为您配置环境（可能需要几分钟）..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败。"
        read -p "按回车键退出..."
        exit 1
    fi
    
    echo "⬇️  正在安装依赖包..."
    # 使用清华源加速
    ./venv/bin/pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "⚠️  镜像源安装失败，尝试官方源..."
        ./venv/bin/pip install -r requirements.txt
        if [ $? -ne 0 ]; then
             echo "❌ 依赖安装失败，请检查网络连接。"
             read -p "按回车键退出..."
             exit 1
        fi
    fi
    echo "✅ 环境配置完成！"
fi

echo "🚀 正在启动 PDF 工具箱..."
# 使用 nohup 后台运行，或者直接运行。直接运行即关闭终端会退出，nohup 可以独立。
# 这里直接运行，方便看日志
./venv/bin/python3 main.py
