#!/bin/bash
# Redis可视化管理工具启动脚本

echo "正在启动Redis可视化管理工具..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查redis库是否安装
python3 -c "import redis" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装redis库..."
    pip3 install redis --break-system-packages -q
fi

# 启动程序
echo "启动程序..."
cd "$(dirname "$0")"
python3 main.py
