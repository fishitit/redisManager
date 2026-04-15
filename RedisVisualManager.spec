# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 规格文件
用于打包Redis可视化管理工具
支持Windows和macOS
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 分析主程序
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),
        ('views', 'views'),
        ('controllers', 'controllers'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'redis',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 创建PYZ归档
pyz = PYZ(a.pure)

# 根据平台选择EXE类型
if sys.platform == 'win32':
    # Windows
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='RedisVisualManager',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # 无控制台窗口
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='RedisVisualManager',
    )
else:
    # macOS / Linux
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='RedisVisualManager',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # 无控制台窗口
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='RedisVisualManager',
    )
