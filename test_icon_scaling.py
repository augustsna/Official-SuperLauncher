#!/usr/bin/env python3
"""
Test script to demonstrate improved icon scaling methods.
This script shows the difference between old and new icon extraction methods.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap
    
    # Import our IconExtractor class
    from main import IconExtractor
    
    class IconScalingTest(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Icon Scaling Test")
            self.setGeometry(100, 100, 800, 600)
            
            # Test file path (use a common executable)
            self.test_file = r"C:\Windows\System32\notepad.exe"
            if not os.path.exists(self.test_file):
                # Fallback to any .exe file in System32
                system32_dir = r"C:\Windows\System32"
                for file in os.listdir(system32_dir):
                    if file.endswith('.exe'):
                        self.test_file = os.path.join(system32_dir, file)
                        break
            
            self.setup_ui()
            self.test_icon_methods()
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            
            # File path display
            file_label = QLabel(f"Testing file: {self.test_file}")
            file_label.setWordWrap(True)
            layout.addWidget(file_label)
            
            # Method selection
            method_layout = QHBoxLayout()
            method_layout.addWidget(QLabel("Icon Method:"))
            self.method_combo = QComboBox()
            self.method_combo.addItems([
                "Old method (single size)",
                "Multi-size extraction",
                "High-quality scaling",
                "DPI-aware scaling",
                "Quality-aware extraction"
            ])
            self.method_combo.currentTextChanged.connect(self.on_method_changed)
            method_layout.addWidget(self.method_combo)
            layout.addLayout(method_layout)
            
            # Icon display
            self.icon_label = QLabel()
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.icon_label.setMinimumSize(200, 200)
            self.icon_label.setStyleSheet("border: 2px solid #ccc; background: #f0f0f0;")
            layout.addWidget(self.icon_label)
            
            # Size selection
            size_layout = QHBoxLayout()
            size_layout.addWidget(QLabel("Display Size:"))
            self.size_combo = QComboBox()
            self.size_combo.addItems(['16', '24', '32', '48', '64', '128'])
            self.size_combo.setCurrentText('48')
            self.size_combo.currentTextChanged.connect(self.on_size_changed)
            size_layout.addWidget(self.size_combo)
            layout.addLayout(size_layout)
            
            # Quality settings
            settings_layout = QHBoxLayout()
            settings_layout.addWidget(QLabel("Quality Settings:"))
            self.quality_combo = QComboBox()
            self.quality_combo.addItems(['High', 'Medium', 'Low'])
            self.quality_combo.setCurrentText('High')
            self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
            settings_layout.addWidget(self.quality_combo)
            layout.addLayout(settings_layout)
            
            # Refresh button
            refresh_btn = QPushButton("Refresh Icons")
            refresh_btn.clicked.connect(self.test_icon_methods)
            layout.addWidget(refresh_btn)
            
            # Info display
            self.info_label = QLabel("Select a method to see icon details")
            self.info_label.setWordWrap(True)
            layout.addWidget(self.info_label)
        
        def on_method_changed(self):
            self.test_icon_methods()
        
        def on_size_changed(self):
            self.test_icon_methods()
        
        def on_quality_changed(self):
            self.test_icon_methods()
        
        def test_icon_methods(self):
            if not os.path.exists(self.test_file):
                self.info_label.setText(f"Test file not found: {self.test_file}")
                return
            
            method = self.method_combo.currentText()
            size = int(self.size_combo.currentText())
            quality = self.quality_combo.currentText()
            
            try:
                if method == "Old method (single size)":
                    icon = IconExtractor.extract_icon(self.test_file, size)
                    info = f"Old method: Single size {size}x{size}"
                
                elif method == "Multi-size extraction":
                    icon = IconExtractor.extract_icon_multi_size(self.test_file, [16, 24, 32, 48, 64, 128])
                    info = f"Multi-size: Available sizes: {icon.availableSizes()}"
                
                elif method == "High-quality scaling":
                    base_icon = IconExtractor.extract_icon_multi_size(self.test_file, [32, 48, 64, 128])
                    icon = IconExtractor.create_high_quality_icon(base_icon, size)
                    info = f"High-quality: Scaled from {base_icon.availableSizes()}"
                
                elif method == "DPI-aware scaling":
                    base_icon = IconExtractor.extract_icon_multi_size(self.test_file, [32, 48, 64, 128])
                    icon = IconExtractor.create_dpi_aware_icon(base_icon, size, 1.0)
                    info = f"DPI-aware: Scaled from {base_icon.availableSizes()}"
                
                elif method == "Quality-aware extraction":
                    # Configure quality settings based on selection
                    quality_settings = {
                        'use_high_quality_scaling': quality != 'Low',
                        'use_dpi_aware_scaling': quality == 'High',
                        'preferred_source_sizes': [32, 48, 64, 128, 256] if quality == 'High' else [32, 48, 64],
                        'fallback_scaling_method': 'smooth' if quality == 'High' else 'fast',
                        'cache_enabled': True,
                        'cache_size_limit': 100
                    }
                    icon = IconExtractor.extract_icon_with_quality(self.test_file, size, quality_settings)
                    info = f"Quality-aware ({quality}): {icon.availableSizes()}"
                
                else:
                    icon = IconExtractor.extract_icon(self.test_file, size)
                    info = "Default method"
                
                if icon and not icon.isNull():
                    # Display the icon
                    pixmap = icon.pixmap(size, size)
                    if not pixmap.isNull():
                        self.icon_label.setPixmap(pixmap)
                        self.info_label.setText(f"{info}\nIcon size: {pixmap.size()}")
                    else:
                        self.info_label.setText(f"{info}\nFailed to create pixmap")
                else:
                    self.info_label.setText(f"{info}\nIcon is null or empty")
                
            except Exception as e:
                self.info_label.setText(f"Error: {str(e)}")
    
    def main():
        app = QApplication(sys.argv)
        window = IconScalingTest()
        window.show()
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure PySide6 is installed and main.py is in the same directory")
except Exception as e:
    print(f"Error: {e}")
