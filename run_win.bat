@echo off
cd /d "%~dp0"
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo ========================================
echo   PDF 工具箱 - 环境检查
echo ========================================
echo.

REM 检查 Python 是否已安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未检测到 Python，正在为您自动安装 Python 3.11.9...
    echo.
    
    REM 下载 Python 3.11.9 安装程序
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe"
    
    echo [下载] 正在下载 Python 3.11.9...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"
    
    if not exist "%PYTHON_INSTALLER%" (
        echo [错误] 下载 Python 失败，请手动下载安装。
        echo 下载地址: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
        pause
        exit /b
    )
    
    echo [安装] 正在静默安装 Python 3.11.9...
    echo        (这可能需要几分钟，请耐心等待)
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
    
    if errorlevel 1 (
        echo [错误] Python 安装失败。
        echo 请手动运行安装程序: %PYTHON_INSTALLER%
        pause
        exit /b
    )
    
    echo [完成] Python 3.11.9 安装成功！
    echo.
    echo [重要] 请关闭此窗口，重新运行 run_win.bat
    pause
    exit /b
)

REM 显示 Python 版本
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [检测] %PYVER%
echo.

REM 检查/创建虚拟环境
if not exist venv (
    echo [配置] 首次运行，正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败。
        pause
        exit /b
    )
    echo [完成] 虚拟环境创建成功！
    echo.
)

REM 激活虚拟环境并检查核心依赖
echo [检查] 正在检查核心依赖...

REM 检查 PyQt6
venv\Scripts\python -c "import PyQt6" > nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 PyQt6...
    venv\Scripts\pip install PyQt6 -i https://pypi.tuna.tsinghua.edu.cn/simple -q
    if errorlevel 1 (
        echo [警告] 镜像源安装失败，尝试官方源...
        venv\Scripts\pip install PyQt6 -q
    )
)

REM 检查 PyMuPDF
venv\Scripts\python -c "import fitz" > nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 PyMuPDF...
    venv\Scripts\pip install PyMuPDF -i https://pypi.tuna.tsinghua.edu.cn/simple -q
    if errorlevel 1 (
        echo [警告] 镜像源安装失败，尝试官方源...
        venv\Scripts\pip install PyMuPDF -q
    )
)

REM 检查其他依赖是否需要安装
venv\Scripts\python -c "import pypdf, pdf2docx, reportlab, docx" > nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装其他依赖包...
    venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
    if errorlevel 1 (
        echo [警告] 镜像源安装失败，尝试官方源...
        venv\Scripts\pip install -r requirements.txt -q
        if errorlevel 1 (
            echo [错误] 依赖安装失败。
            pause
            exit /b
        )
    )
)

echo [完成] 所有依赖已就绪！
echo.
echo ========================================
echo   正在启动 PDF 工具箱...
echo ========================================
start "" venv\Scripts\pythonw.exe main.py
