#!/usr/bin/env python3
"""
SuperLauncher Builder
Builds the SuperLauncher executable with PyInstaller
"""

import os
import sys
import subprocess
import shutil

def clean_build():
    """Clean previous SuperLauncher builds"""
    print("🧹 Cleaning previous SuperLauncher builds...")
    
    # Clean only SuperLauncher-specific build files
    launcher_build_dirs = [
        'build/main',
        'dist/SuperLauncher'
    ]
    
    for dir_path in launcher_build_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Cleaned {dir_path}")
            except Exception as e:
                print(f"   ⚠️ Error cleaning {dir_path}: {e}")
    
    # Clean main spec file if it exists
    spec_file = 'main.spec'
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"   ✅ Cleaned {spec_file}")
        except Exception as e:
            print(f"   ⚠️ Error cleaning {spec_file}: {e}")

def create_main_spec():
    """Create PyInstaller spec for SuperLauncher"""
    print("📝 Creating SuperLauncher spec file...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get project paths
project_root = os.path.dirname(os.path.abspath(SPECPATH))

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('template_app/assets', 'template_app/assets'),
        ('launcher_config.json', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets.QApplication',
        'PySide6.QtWidgets.QMainWindow',
        'PySide6.QtWidgets.QWidget',
        'PySide6.QtWidgets.QVBoxLayout',
        'PySide6.QtWidgets.QHBoxLayout',
        'PySide6.QtWidgets.QGridLayout',
        'PySide6.QtWidgets.QLabel',
        'PySide6.QtWidgets.QLineEdit',
        'PySide6.QtWidgets.QPushButton',
        'PySide6.QtWidgets.QFrame',
        'PySide6.QtWidgets.QTextEdit',
        'PySide6.QtWidgets.QScrollArea',
        'PySide6.QtWidgets.QSizePolicy',
        'PySide6.QtWidgets.QFileDialog',
        'PySide6.QtWidgets.QMessageBox',
        'PySide6.QtWidgets.QMenu',
        'PySide6.QtWidgets.QMenuBar',
        'PySide6.QtWidgets.QStatusBar',
        'PySide6.QtWidgets.QToolBar',
        'PySide6.QtWidgets.QSplitter',
        'PySide6.QtWidgets.QTabWidget',
        'PySide6.QtWidgets.QComboBox',
        'PySide6.QtWidgets.QCheckBox',
        'PySide6.QtWidgets.QRadioButton',
        'PySide6.QtWidgets.QSlider',
        'PySide6.QtWidgets.QProgressBar',
        'PySide6.QtWidgets.QSpinBox',
        'PySide6.QtWidgets.QDoubleSpinBox',
        'PySide6.QtWidgets.QDateEdit',
        'PySide6.QtWidgets.QTimeEdit',
        'PySide6.QtWidgets.QDateTimeEdit',
        'PySide6.QtWidgets.QCalendarWidget',
        'PySide6.QtWidgets.QListWidget',
        'PySide6.QtWidgets.QTreeWidget',
        'PySide6.QtWidgets.QTableWidget',
        'PySide6.QtWidgets.QGroupBox',
        'PySide6.QtWidgets.QStackedWidget',
        'PySide6.QtCore.Qt',
        'PySide6.QtCore.QTimer',
        'PySide6.QtCore.QPropertyAnimation',
        'PySide6.QtCore.QEasingCurve',
        'PySide6.QtCore.QRect',
        'PySide6.QtCore.QSize',
        'PySide6.QtCore.QPoint',
        'PySide6.QtCore.QThread',
        'PySide6.QtCore.QSignal',
        'PySide6.QtCore.QSlot',
        'PySide6.QtCore.QObject',
        'PySide6.QtCore.QEvent',
        'PySide6.QtCore.QFileInfo',
        'PySide6.QtCore.QMimeData',
        'PySide6.QtGui.QFont',
        'PySide6.QtGui.QPalette',
        'PySide6.QtGui.QColor',
        'PySide6.QtGui.QPixmap',
        'PySide6.QtGui.QPainter',
        'PySide6.QtGui.QLinearGradient',
        'PySide6.QtGui.QIcon',
        'PySide6.QtGui.QKeySequence',
        'PySide6.QtGui.QShortcut',
        'PySide6.QtGui.QDrag',
        'PySide6.QtGui.QAction',
        'win32gui',
        'win32api',
        'win32con',
        'win32process',
        'win32file',
        'win32security',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'json',
        'pathlib',
        'subprocess',
        'dataclasses',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'test', 'distutils', 'setuptools',
        'pkg_resources', 'email', 'http', 'urllib', 'xml', 'xmlrpc',
        'multiprocessing', 'concurrent', 'asyncio', 'ssl',
        'hmac', 'cryptography', 'matplotlib', 'numpy', 'scipy',
        'pandas', 'sklearn', 'tensorflow', 'torch', 'jupyter',
        'notebook', 'ipython', 'sympy', 'requests', 'aiohttp',
        'flask', 'django', 'fastapi', 'sqlalchemy', 'psycopg2',
        'mysql', 'sqlite3', 'redis', 'celery', 'gunicorn',
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
    name='SuperLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,  # No compression for better compatibility
    console=False,  # GUI application
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
    name='SuperLauncher',
)
'''
    
    with open('main.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   ✅ Created SuperLauncher spec file")

def build_launcher():
    """Build the SuperLauncher executable"""
    print("🔨 Building SuperLauncher...")
    
    # Build command
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'main.spec']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # Longer timeout for main app
    
    if result.returncode == 0:
        print("   ✅ SuperLauncher build successful")
        return True
    else:
        print(f"   ❌ SuperLauncher build failed: {result.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PySide6
        print("   ✅ PySide6 is installed")
    except ImportError:
        print("   ❌ PySide6 is not installed")
        print("   💡 Please install PySide6: pip install PySide6")
        return False
    
    try:
        import PyInstaller
        print("   ✅ PyInstaller is installed")
    except ImportError:
        print("   ❌ PyInstaller is not installed")
        print("   💡 Please install PyInstaller: pip install pyinstaller")
        return False
    
    try:
        import win32gui
        print("   ✅ pywin32 is installed")
    except ImportError:
        print("   ❌ pywin32 is not installed")
        print("   💡 Please install pywin32: pip install pywin32")
        return False
    
    try:
        import PIL
        print("   ✅ Pillow is installed")
    except ImportError:
        print("   ❌ Pillow is not installed")
        print("   💡 Please install Pillow: pip install pillow")
        return False
    
    return True

def check_required_files():
    """Check if required files exist"""
    print("📋 Checking required files...")
    
    required_files = [
        'main.py',
        'launcher_config.json',
        'template_app/assets/icons/icon.png',
        'template_app/ui/main_window_base.py',
        'template_app/config.py',
        'template_app/styles.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ Found {file_path}")
        else:
            print(f"   ❌ Missing {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True

def create_version_info():
    """Create version info file for Windows executable"""
    print("📄 Creating version info...")
    
    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'SuperLauncher'),
        StringStruct(u'FileDescription', u'SuperLauncher - Advanced Application Launcher'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'SuperLauncher'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'SuperLauncher.exe'),
        StringStruct(u'ProductName', u'SuperLauncher'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("   ✅ Created version info file")

def main():
    """Main build process"""
    print("=" * 60)
    print("  SuperLauncher Builder")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required dependencies")
        print("💡 Install missing dependencies and try again")
        return
    
    # Check required files
    if not check_required_files():
        print("\n❌ Missing required files")
        print("💡 Ensure all required files are present and try again")
        return
    
    # Clean previous builds
    clean_build()
    
    # Create version info
    create_version_info()
    
    # Create spec file
    create_main_spec()
    
    # Build launcher
    if build_launcher():
        print("\n" + "=" * 60)
        print("  BUILD SUMMARY")
        print("=" * 60)
        print("✅ SuperLauncher build successful")
        print("\n📁 Generated files:")
        print("   • dist/SuperLauncher/ - SuperLauncher build")
        print("   • dist/SuperLauncher/SuperLauncher.exe - Main executable")
        print("\n🎉 SuperLauncher build completed successfully!")
        print("\n💡 You can now run the executable from:")
        print("   dist/SuperLauncher/SuperLauncher.exe")
    else:
        print("\n❌ SuperLauncher build failed")
        print("💡 Check the error messages above")
        print("💡 Ensure all dependencies are installed correctly")

if __name__ == "__main__":
    main()
