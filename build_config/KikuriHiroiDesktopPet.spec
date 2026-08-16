# -*- mode: python ; coding: utf-8 -*-
import os
PROJ_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(PROJ_ROOT, 'desktop_pet.py')],
    pathex=[PROJ_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJ_ROOT, 'pet'), 'pet'),
        (os.path.join(PROJ_ROOT, 'app_icon.ico'), '.'),
    ],
    hiddenimports=[],
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
    name='KikuriHiroiDesktopPet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=os.path.join(PROJ_ROOT, 'build_config', 'version_info.txt'),
    icon=[os.path.join(PROJ_ROOT, 'app_icon.ico')],
)
