#!/usr/bin/env python3
"""
SuperCut Keygen Builder
Builds the keygen executable with PyInstaller
"""

import os
import sys
import subprocess
import shutil

def clean_build():
    """Clean previous keygen builds"""
    print("🧹 Cleaning previous keygen builds...")
    
    # Clean only keygen-specific build files
    keygen_build_dirs = [
        'build/supercut_keygen',
        'dist/SuperCut_Keygen'
    ]
    
    for dir_path in keygen_build_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Cleaned {dir_path}")
            except Exception as e:
                print(f"   ⚠️ Error cleaning {dir_path}: {e}")
    
    # Clean keygen spec file if it exists
    spec_file = 'supercut_keygen.spec'
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"   ✅ Cleaned {spec_file}")
        except Exception as e:
            print(f"   ⚠️ Error cleaning {spec_file}: {e}")

def create_keygen_spec():
    """Create PyInstaller spec for keygen"""
    print("📝 Creating keygen spec file...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get project paths
project_root = os.path.dirname(os.path.abspath(SPECPATH))

# Analysis
a = Analysis(
    ['supercut_keygen.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('src/sources/keygen.png', 'src/sources'),
    ],
    hiddenimports=[
        'hashlib',
        'base64',
        'platform',
        'subprocess',
        'json',
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets.QApplication',
        'PyQt6.QtWidgets.QMainWindow',
        'PyQt6.QtWidgets.QWidget',
        'PyQt6.QtWidgets.QVBoxLayout',
        'PyQt6.QtWidgets.QHBoxLayout',
        'PyQt6.QtWidgets.QLabel',
        'PyQt6.QtWidgets.QLineEdit',
        'PyQt6.QtWidgets.QPushButton',
        'PyQt6.QtWidgets.QFrame',
        'PyQt6.QtWidgets.QTextEdit',
        'PyQt6.QtWidgets.QScrollArea',
        'PyQt6.QtWidgets.QSizePolicy',
        'PyQt6.QtCore.Qt',
        'PyQt6.QtCore.QTimer',
        'PyQt6.QtCore.QPropertyAnimation',
        'PyQt6.QtCore.QEasingCurve',
        'PyQt6.QtCore.QRect',
        'PyQt6.QtGui.QFont',
        'PyQt6.QtGui.QPalette',
        'PyQt6.QtGui.QColor',
        'PyQt6.QtGui.QPixmap',
        'PyQt6.QtGui.QPainter',
        'PyQt6.QtGui.QLinearGradient',
        'PyQt6.QtGui.QIcon',
        'PyQt6.QtGui.QKeySequence',
        'PyQt6.QtGui.QShortcut',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'test', 'distutils', 'setuptools',
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
    name='SuperCut_Keygen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,  # No compression
    console=False,  # GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/sources/keygen.png' if os.path.exists('src/sources/keygen.png') else ('src/sources/icon.ico' if os.path.exists('src/sources/icon.ico') else None),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='SuperCut_Keygen',
)
'''
    
    with open('supercut_keygen.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   ✅ Created keygen spec file")

def build_keygen():
    """Build the keygen executable"""
    print("🔨 Building SuperCut Keygen...")
    
    # Build command
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'supercut_keygen.spec']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        print("   ✅ Keygen build successful")
        return True
    else:
        print(f"   ❌ Keygen build failed: {result.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PyQt6
        print("   ✅ PyQt6 is installed")
    except ImportError:
        print("   ❌ PyQt6 is not installed")
        print("   💡 Please install PyQt6: pip install PyQt6")
        return False
    
    try:
        import PyInstaller
        print("   ✅ PyInstaller is installed")
    except ImportError:
        print("   ❌ PyInstaller is not installed")
        print("   💡 Please install PyInstaller: pip install pyinstaller")
        return False
    
    return True

def main():
    """Main build process"""
    print("=" * 60)
    print("  SuperCut Keygen Builder")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required dependencies")
        return
    
    # Clean previous builds
    clean_build()
    
    # Create spec file
    create_keygen_spec()
    
    # Build keygen
    if build_keygen():
        print("\n" + "=" * 60)
        print("  BUILD SUMMARY")
        print("=" * 60)
        print("✅ Keygen build successful")
        print("\n📁 Generated files:")
        print("   • dist/SuperCut_Keygen/ - Keygen build")
        print("\n🎉 Keygen build completed successfully!")
    else:
        print("\n❌ Keygen build failed")
        print("💡 Check the error messages above")

if __name__ == "__main__":
    main()
