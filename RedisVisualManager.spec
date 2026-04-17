# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('models', 'models'), ('views', 'views'), ('controllers', 'controllers'), ('utils', 'utils')],
    hiddenimports=['redis', 'redis.client', 'redis.connection', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'models.connection_model', 'models.redis_model', 'views.main_view', 'views.connection_dialog', 'views.add_key_dialog', 'views.client_list_dialog', 'controllers.main_controller'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RedisVisualManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
app = BUNDLE(
    coll,
    name='RedisVisualManager.app',
    icon=None,
    bundle_identifier=None,
)
