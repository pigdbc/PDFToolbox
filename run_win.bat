@echo off
cd /d "%~dp0"
chcp 65001 > nul
setlocal

echo 正在检查运行环境...

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python。
    echo 请访问 https://www.python.org/downloads/windows/ 下载安装。
    echo 注意：安装时请勾选 "Add Python to PATH"。
    pause
    exit /b
)

if not exist venv (
    echo [配置] 首次运行，正在为您配置环境（可能需要几分钟）...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败。
        pause
        exit /b
    )
    
    echo [下载] 正在安装依赖包...
    venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [警告] 镜像源安装失败，尝试官方源...
        venv\Scripts\pip install -r requirements.txt
        if errorlevel 1 (
            echo [错误] 依赖安装失败。
            pause
            exit /b
        )
    )
    echo [完成] 环境配置完成！
)

echo [启动] 正在启动 PDF 工具箱...
start venv\Scripts\pythonw.exe main.py
