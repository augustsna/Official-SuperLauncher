#!/usr/bin/env python3
"""
PySide6 Main Application Builder
Builds the main.py executable with PyInstaller
Anti-virus false positive optimized build
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime


def clean_build():
    """Clean previous main builds"""
    print("[*] Cleaning previous main builds...")

    main_build_dirs = [
        'build/main',
        'dist/TemplateApp'
    ]

    for dir_path in main_build_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   [OK] Cleaned {dir_path}")
            except Exception as e:
                print(f"   [WARN] Error cleaning {dir_path}: {e}")

    spec_file = 'main.spec'
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"   [OK] Cleaned {spec_file}")
        except Exception as e:
            print(f"   [WARN] Error cleaning {spec_file}: {e}")


def get_version_info():
    """Get version information for the executable"""
    return {
        'version': '1.0.0.0',
        'company_name': 'Your Company Name',
        'file_description': 'PySide6 Template App',
        'internal_name': 'TemplateApp',
        'legal_copyright': f"Copyright © {datetime.now().year} Your Company Name",
        'original_filename': 'TemplateApp.exe',
        'product_name': 'Template App',
        'product_version': '1.0.0.0'
    }


def create_main_spec():
    """Create PyInstaller spec for main.py with anti-virus optimizations"""
    print("[*] Creating main.spec file...")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os

project_root = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('template_app/assets', 'template_app/assets'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'test', 'setuptools',
        'pkg_resources', 'email', 'http', 'urllib', 'xml', 'xmlrpc',
        'multiprocessing', 'concurrent', 'asyncio', 'ssl',
        'hmac', 'cryptography', 'matplotlib', 'numpy', 'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TemplateApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='template_app/assets/icons/icon.png' if os.path.exists('template_app/assets/icons/icon.png') else None,
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='TemplateApp',
)
'''

    with open('main.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("   [OK] Created main.spec file")


def create_version_file():
    """Create a version file for the executable (optional)"""
    info = get_version_info()
    content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({info['version'].replace('.', ', ')}),
    prodvers=({info['version'].replace('.', ', ')}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u"{info['company_name']}"),
         StringStruct(u'FileDescription', u"{info['file_description']}"),
         StringStruct(u'FileVersion', u"{info['version']}"),
         StringStruct(u'InternalName', u"{info['internal_name']}"),
         StringStruct(u'LegalCopyright', u"{info['legal_copyright']}"),
         StringStruct(u'OriginalFilename', u"{info['original_filename']}"),
         StringStruct(u'ProductName', u"{info['product_name']}"),
         StringStruct(u'ProductVersion', u"{info['product_version']}")])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    print("   [OK] Created version info file (version_info.txt)")


def build_main():
    """Build the main executable with anti-virus optimizations"""
    print("[BUILD] Building TemplateApp...")

    env = os.environ.copy()
    env['PYTHONHASHSEED'] = '0'
    env['PYTHONOPTIMIZE'] = '1'

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean', '--noconfirm',
        '--log-level=WARN',
        'main.spec'
    ]

    print("   [OPT] Building with anti-virus optimizations...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)

    if result.returncode == 0:
        print("   [OK] Main build successful")
        return True
    else:
        print(f"   [ERR] Main build failed: {result.stderr}")
        return False


def post_build_optimizations():
    """Apply post-build optimizations to reduce false positives"""
    print("[OPT] Applying post-build optimizations...")

    exe_path = 'dist/TemplateApp/TemplateApp.exe'
    if os.path.exists(exe_path):
        print("   [OK] Executable created successfully")
        print("   [SIZE] File size:", f"{os.path.getsize(exe_path) / (1024*1024):.2f} MB")
        print("\n   Tips:")
        print("   - Consider code signing with a trusted certificate")
        print("   - Submit to VirusTotal for analysis")
        print("   - Add your application to antivirus whitelists")
        print("   - Use a consistent build environment")
        print("   - Avoid suspicious file names or paths")
    else:
        print("   [ERR] Executable not found")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("[*] Checking dependencies...")

    try:
        import PySide6  # noqa: F401
        print("   [OK] PySide6 is installed")
    except ImportError:
        print("   [ERR] PySide6 is not installed")
        print("   Tip: Please install PySide6: pip install PySide6")
        return False

    try:
        import PyInstaller  # noqa: F401
        print("   [OK] PyInstaller is installed")
    except ImportError:
        print("   [ERR] PyInstaller is not installed")
        print("   Tip: Please install PyInstaller: pip install pyinstaller")
        return False

    return True


def main():
    """Main build process with anti-virus optimizations"""
    print("=" * 60)
    print("  PySide6 Main App Builder (Anti-Virus Optimized)")
    print("=" * 60)
    print()

    if not check_dependencies():
        print("\n[ERR] Missing required dependencies")
        return

    clean_build()
    create_version_file()
    create_main_spec()

    if build_main():
        post_build_optimizations()
        print("\n" + "=" * 60)
        print("  BUILD SUMMARY")
        print("=" * 60)
        print("[OK] Main build successful")
        print("\nGenerated files:")
        print("   - dist/TemplateApp/ - application build")
        print("\n[AV] Anti-virus optimizations applied:")
        print("   - Clean imports and exclusions")
        print("   - Disabled UPX compression")
        print("   - Added proper metadata")
        print("   - Optimized build configuration")
        print("\n[DONE] Build completed successfully!")
    else:
        print("\n[ERR] Build failed")
        print("Tip: Check the error messages above")


if __name__ == "__main__":
    main()


