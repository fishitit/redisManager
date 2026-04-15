@echo off
chcp 65001 >nul
REM ======================================
REM Redis Visual Manager - Windows 打包脚本
REM ======================================

echo.
echo ======================================
echo   Redis Visual Manager - Windows 打包
echo ======================================
echo.

REM 检查Python是否安装
echo [0/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查PyInstaller是否安装
echo [1/5] 检查PyInstaller...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装PyInstaller...
    pip install pyinstaller -q
    if %errorlevel% neq 0 (
        echo ❌ 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)

REM 检查redis库
echo 检查redis库...
python -c "import redis" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装redis库...
    pip install redis -q
)

REM 清理旧的构建文件
echo [2/5] 清理旧的构建文件...
if exist build (
    echo 删除 build 目录...
    rmdir /s /q build
)
if exist dist (
    echo 删除 dist 目录...
    rmdir /s /q dist
)
if exist *.spec (
    echo 删除旧的spec文件...
    del /q *.spec
)
if exist __pycache__ (
    echo 删除缓存...
    rmdir /s /q __pycache__
)

REM 检查必要的目录和文件
echo [3/5] 检查项目文件...
if not exist models (
    echo ❌ 错误: 缺少 models 目录
    pause
    exit /b 1
)
if not exist views (
    echo ❌ 错误: 缺少 views 目录
    pause
    exit /b 1
)
if not exist controllers (
    echo ❌ 错误: 缺少 controllers 目录
    pause
    exit /b 1
)
if not exist main.py (
    echo ❌ 错误: 缺少 main.py 文件
    pause
    exit /b 1
)

REM 使用PyInstaller打包
echo [4/5] 开始打包（这可能需要几分钟）...
echo.

pyinstaller --name="RedisVisualManager" ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    --add-data "models;models" ^
    --add-data "views;views" ^
    --add-data "controllers;controllers" ^
    --add-data "utils;utils" ^
    --hidden-import=redis ^
    --hidden-import=redis.client ^
    --hidden-import=redis.connection ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=models.connection_model ^
    --hidden-import=models.redis_model ^
    --hidden-import=views.main_view ^
    --hidden-import=views.connection_dialog ^
    --hidden-import=views.add_key_dialog ^
    --hidden-import=views.client_list_dialog ^
    --hidden-import=controllers.main_controller ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 错误: 打包过程失败
    echo 请检查上方的错误信息
    pause
    exit /b 1
)

REM 检查结果
echo [5/5] 检查输出...
echo.

if exist "dist\RedisVisualManager\RedisVisualManager.exe" (
    echo ======================================
    echo   ✅ 打包成功！
    echo ======================================
    echo.
    echo 输出目录: dist\RedisVisualManager\
    echo 可执行文件: dist\RedisVisualManager\RedisVisualManager.exe
    echo.
    echo 文件大小:
    dir "dist\RedisVisualManager\RedisVisualManager.exe" | find "RedisVisualManager.exe"
    echo.
    echo ======================================
    echo 如何运行:
    echo   1. 打开 dist\RedisVisualManager\ 目录
    echo   2. 双击 RedisVisualManager.exe
    echo.
    echo 如何分发:
    echo   1. 压缩整个 dist\RedisVisualManager\ 目录
    echo   2. 使用压缩软件创建zip文件
    echo   3. 将zip文件发送给用户
    echo ======================================
    echo.
    
    REM 询问是否打开输出目录
    set /p open_dir="是否打开输出目录? (Y/N): "
    if /i "%open_dir%"=="Y" (
        explorer "dist\RedisVisualManager"
    )
    
) else if exist "dist\RedisVisualManager.exe" (
    echo ======================================
    echo   ✅ 打包成功（单文件模式）
    echo ======================================
    echo.
    echo 输出文件: dist\RedisVisualManager.exe
    echo.
    dir "dist\RedisVisualManager.exe" | find "RedisVisualManager.exe"
    echo.
    
) else (
    echo ======================================
    echo   ❌ 打包失败
    echo ======================================
    echo.
    echo 未找到预期的输出文件
    echo 请检查上方的错误日志
    echo.
    echo 常见问题:
    echo   1. 确保所有Python文件都存在
    echo   2. 确保依赖已安装（redis, pyinstaller）
    echo   3. 确保有写入权限
    echo.
    pause
    exit /b 1
)

pause
