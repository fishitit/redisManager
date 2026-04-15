#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis可视化管理工具
===================
功能特性:
- 多Redis连接管理（添加/保存/删除/切换）
- Key-Value管理（支持string/hash/list/set/zset五种类型）
- Redis服务状态查看
- 数据库操作（切换/清空）
- 本地连接配置持久化

依赖安装:
pip install redis

运行:
python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controllers import Controller


def main():
    """主程序入口"""
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口大小和位置
    root.geometry("1200x700+100+100")
    root.minsize(900, 600)
    
    # 设置样式
    style = ttk.Style()
    # 使用现代主题
    try:
        style.theme_use('clam')
    except:
        pass  # 如果主题不可用则使用默认
    
    # 创建控制器
    try:
        app = Controller(root)
    except Exception as e:
        messagebox.showerror("错误", f"程序初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 显示窗口
    root.mainloop()


if __name__ == "__main__":
    main()
