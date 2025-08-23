#!/usr/bin/env python3
"""
Test script for icon extraction functionality.
This script tests the IconExtractor class with various file types.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import from example_launcher_ui
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

try:
    from example_launcher_ui import IconExtractor
except ImportError as e:
    print(f"Error importing IconExtractor: {e}")
    sys.exit(1)


class IconTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Extraction Test")
        self.setMinimumSize(400, 300)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Test common Windows executables
        test_files = [
            r"C:\Windows\System32\notepad.exe",
            r"C:\Windows\System32\calc.exe", 
            r"C:\Windows\System32\cmd.exe",
            r"C:\Windows\explorer.exe",
            r"C:\Program Files\Internet Explorer\iexplore.exe",
            # Also test with any files in the current directory
            "example_launcher_ui.py",
            "test_icon_extraction.py"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                self.add_icon_test(layout, file_path)
        
        self.setCentralWidget(central)
    
    def add_icon_test(self, layout, file_path):
        """Add an icon test for the given file path."""
        try:
            icon = IconExtractor.extract_icon(file_path, 32)
            
            # Create a label to display the icon and filename
            label = QLabel()
            
            # Convert QIcon to QPixmap for display
            pixmap = icon.pixmap(32, 32)
            label.setPixmap(pixmap)
            label.setText(f"  {Path(file_path).name}")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            layout.addWidget(label)
            print(f"✓ Successfully extracted icon for: {file_path}")
            
        except Exception as e:
            print(f"✗ Failed to extract icon for {file_path}: {e}")


def main():
    app = QApplication(sys.argv)
    
    print("Testing IconExtractor functionality...")
    print(f"Win32 API available: {hasattr(IconExtractor, 'HAS_WIN32') and IconExtractor.__dict__.get('HAS_WIN32', False)}")
    
    window = IconTestWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
