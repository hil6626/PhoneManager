# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins/platforms', 'PyQt5/Qt5/plugins/platforms'),
        ('venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins/imageformats', 'PyQt5/Qt5/plugins/imageformats'),
        ('venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins/platformthemes', 'PyQt5/Qt5/plugins/platformthemes'),
        ('venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins/iconengines', 'PyQt5/Qt5/plugins/iconengines'),
    ],
    datas=[
        ('resources/', 'resources/'),
        ('config/', 'config/'),
        ('database/', 'database/'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pandas',
        'openpyxl',
        'sqlite3',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

