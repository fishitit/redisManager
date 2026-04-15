#!/bin/bash
# macOS 打包脚本

echo "======================================"
echo "  Redis Visual Manager - macOS 打包"
echo "======================================"

# 清理旧的构建文件
echo "[1/4] 清理旧的构建文件..."
rm -rf build dist __pycache__
rm -f *.spec

# 安装依赖
echo "[2/4] 检查依赖..."
pip install redis pyinstaller --break-system-packages -q

# 使用PyInstaller打包
echo "[3/4] 开始打包..."
pyinstaller --name="RedisVisualManager" \
    --onedir \
    --windowed \
    --add-data "models:models" \
    --add-data "views:views" \
    --add-data "controllers:controllers" \
    --add-data "utils:utils" \
    main.py

# 检查结果
echo "[4/4] 检查输出..."
if [ -d "dist/RedisVisualManager" ]; then
    echo ""
    echo "======================================"
    echo "  ✅ 打包成功！"
    echo "  输出目录: dist/RedisVisualManager/"
    echo "  可执行文件: dist/RedisVisualManager/RedisVisualManager"
    echo "======================================"
    du -sh dist/RedisVisualManager
elif [ -f "dist/RedisVisualManager" ]; then
    echo ""
    echo "======================================"
    echo "  ✅ 打包成功！"
    echo "  输出文件: dist/RedisVisualManager"
    echo "======================================"
    ls -lh dist/RedisVisualManager
else
    echo ""
    echo "======================================"
    echo "  ❌ 打包失败！请检查错误信息"
    echo "======================================"
    exit 1
fi
