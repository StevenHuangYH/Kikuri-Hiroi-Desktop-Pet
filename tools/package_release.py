import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RELEASE_DIR = BASE_DIR / 'release'
RELEASE_PKG_DIR = RELEASE_DIR / 'KikuriHiroiDesktopPet_v1.0'

if RELEASE_DIR.exists():
    shutil.rmtree(RELEASE_DIR)
RELEASE_PKG_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy standalone exe
src_exe = BASE_DIR / 'dist' / 'KikuriHiroiDesktopPet.exe'
dst_exe = RELEASE_PKG_DIR / 'KikuriHiroiDesktopPet.exe'
if src_exe.is_file():
    shutil.copy2(src_exe, dst_exe)
    shutil.copy2(src_exe, RELEASE_DIR / 'KikuriHiroiDesktopPet.exe')

# 2. Copy pet assets directory
shutil.copytree(BASE_DIR / 'pet', RELEASE_PKG_DIR / 'pet')

# 3. Create convenient batch launcher
bat_lines = [
    '@echo off',
    'title Kikuri Hiroi Desktop Pet',
    'cd /d "%~dp0"',
    'start "" "%~dp0KikuriHiroiDesktopPet.exe"',
    'exit'
]
with open(RELEASE_PKG_DIR / '启动桌宠.bat', 'w', encoding='ansi') as f:
    f.write('\n'.join(bat_lines))

# 4. Copy README.md
shutil.copy2(BASE_DIR / 'README.md', RELEASE_PKG_DIR / 'README.md')
shutil.copy2(BASE_DIR / 'README.md', RELEASE_DIR / 'README.md')

# 5. Create ZIP archive
zip_path = RELEASE_DIR / 'KikuriHiroiDesktopPet_v1.0.zip'
print('Creating release ZIP archive at:', zip_path)
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(RELEASE_PKG_DIR):
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(RELEASE_PKG_DIR.parent)
            zf.write(full_path, arcname=rel_path)

print('Release packaging complete!')
for item in RELEASE_DIR.iterdir():
    size_str = f'{item.stat().st_size / (1024*1024):.2f} MB' if item.is_file() else '[DIR]'
    print(f' - {item.name:35} : {size_str}')
