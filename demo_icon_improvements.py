#!/usr/bin/env python3
"""
Demonstration script showing icon scaling improvements in SuperLauncher.
This script creates a side-by-side comparison of old vs. new icon methods.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QPushButton, QComboBox, QSpinBox, QGroupBox, QTextEdit
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap, QFont
    
    # Import our IconExtractor class
    from main import IconExtractor
    
    class IconImprovementDemo(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Icon Scaling Improvements Demo")
            self.setGeometry(100, 100, 1000, 700)
            
            # Test file path
            self.test_file = self._find_test_file()
            
            self.setup_ui()
            self.update_comparison()
        
        def _find_test_file(self):
            """Find a suitable test file for demonstration."""
            # Try common Windows executables
            test_files = [
                r"C:\Users\Rock\Desktop\Desktop 2\2. MMO Tools\7. SimpleChrome\SimpleChrome.exe",
                r"C:\Windows\System32\calc.exe",
                r"C:\Windows\System32\mspaint.exe",
                r"C:\Windows\System32\cmd.exe"
            ]
            
            for file_path in test_files:
                if os.path.exists(file_path):
                    return file_path
            
            # Fallback to any .exe file in System32
            system32_dir = r"C:\Windows\System32"
            if os.path.exists(system32_dir):
                for file in os.listdir(system32_dir):
                    if file.endswith('.exe'):
                        return os.path.join(system32_dir, file)
            
            return None
        
        def setup_ui(self):
            layout = QVBoxLayout(self)
            
            # Title
            title = QLabel("SuperLauncher Icon Scaling Improvements")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #2c3e50; margin: 10px;")
            layout.addWidget(title)
            
            # File selection
            file_group = QGroupBox("Test File")
            file_layout = QHBoxLayout(file_group)
            
            self.file_label = QLabel(f"Testing: {self.test_file or 'No test file found'}")
            self.file_label.setStyleSheet("padding: 5px; background: #ecf0f1; border-radius: 3px;")
            file_layout.addWidget(self.file_label)
            
            if self.test_file:
                refresh_btn = QPushButton("Refresh")
                refresh_btn.clicked.connect(self.update_comparison)
                file_layout.addWidget(refresh_btn)
            
            layout.addWidget(file_group)
            
            # Comparison area
            comparison_layout = QHBoxLayout()
            
            # Old method (left side)
            old_group = QGroupBox("Old Method (Single Size)")
            old_layout = QVBoxLayout(old_group)
            
            self.old_icon_label = QLabel()
            self.old_icon_label.setAlignment(Qt.AlignCenter)
            self.old_icon_label.setMinimumSize(150, 150)
            self.old_icon_label.setStyleSheet("border: 2px solid #e74c3c; background: #fdf2f2; padding: 10px;")
            old_layout.addWidget(self.old_icon_label)
            
            self.old_info_label = QLabel("Select size to test")
            self.old_info_label.setAlignment(Qt.AlignCenter)
            old_layout.addWidget(self.old_info_label)
            
            old_size_layout = QHBoxLayout()
            old_size_layout.addWidget(QLabel("Size:"))
            self.old_size_spin = QSpinBox()
            self.old_size_spin.setRange(16, 128)
            self.old_size_spin.setValue(48)
            self.old_size_spin.valueChanged.connect(self.update_comparison)
            old_size_layout.addWidget(self.old_size_spin)
            old_layout.addLayout(old_size_layout)
            
            comparison_layout.addWidget(old_group)
            
            # New method (right side)
            new_group = QGroupBox("New Method (Multi-Size + Quality)")
            new_layout = QVBoxLayout(new_group)
            
            self.new_icon_label = QLabel()
            self.new_icon_label.setAlignment(Qt.AlignCenter)
            self.new_icon_label.setMinimumSize(150, 150)
            self.new_icon_label.setStyleSheet("border: 2px solid #27ae60; background: #f0f9f0; padding: 10px;")
            new_layout.addWidget(self.new_icon_label)
            
            self.new_info_label = QLabel("Select method and size")
            self.new_info_label.setAlignment(Qt.AlignCenter)
            new_layout.addWidget(self.new_info_label)
            
            # Method selection
            method_layout = QHBoxLayout()
            method_layout.addWidget(QLabel("Method:"))
            self.method_combo = QComboBox()
            self.method_combo.addItems([
                "Multi-size extraction",
                "High-quality scaling",
                "DPI-aware scaling",
                "Quality-aware extraction"
            ])
            self.method_combo.currentTextChanged.connect(self.update_comparison)
            method_layout.addWidget(self.method_combo)
            new_layout.addLayout(method_layout)
            
            # Size selection
            new_size_layout = QHBoxLayout()
            new_size_layout.addWidget(QLabel("Size:"))
            self.new_size_spin = QSpinBox()
            self.new_size_spin.setRange(16, 128)
            self.new_size_spin.setValue(48)
            self.new_size_spin.valueChanged.connect(self.update_comparison)
            new_size_layout.addWidget(self.new_size_spin)
            new_layout.addLayout(new_size_layout)
            
            comparison_layout.addWidget(new_group)
            
            layout.addLayout(comparison_layout)
            
            # Quality settings
            quality_group = QGroupBox("Quality Settings")
            quality_layout = QVBoxLayout(quality_group)
            
            self.quality_combo = QComboBox()
            self.quality_combo.addItems(['High', 'Medium', 'Low'])
            self.quality_combo.setCurrentText('High')
            self.quality_combo.currentTextChanged.connect(self.update_comparison)
            quality_layout.addWidget(QLabel("Quality Level:"))
            quality_layout.addWidget(self.quality_combo)
            
            layout.addWidget(quality_group)
            
            # Results and analysis
            results_group = QGroupBox("Results & Analysis")
            results_layout = QVBoxLayout(results_group)
            
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setMaximumHeight(150)
            results_layout.addWidget(self.results_text)
            
            layout.addWidget(results_group)
            
            # Action buttons
            button_layout = QHBoxLayout()
            
            clear_cache_btn = QPushButton("Clear Icon Cache")
            clear_cache_btn.clicked.connect(self._clear_cache)
            button_layout.addWidget(clear_cache_btn)
            
            diagnostics_btn = QPushButton("Run Diagnostics")
            diagnostics_btn.clicked.connect(self._run_diagnostics)
            button_layout.addWidget(diagnostics_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
        
        def update_comparison(self):
            """Update the icon comparison display."""
            if not self.test_file or not os.path.exists(self.test_file):
                self._show_error("No test file available")
                return
            
            try:
                # Update old method
                self._update_old_method()
                
                # Update new method
                self._update_new_method()
                
                # Update results analysis
                self._update_results_analysis()
                
            except Exception as e:
                self._show_error(f"Error updating comparison: {str(e)}")
        
        def _update_old_method(self):
            """Update the old method display."""
            try:
                size = self.old_size_spin.value()
                icon = IconExtractor.extract_icon(self.test_file, size)
                
                if icon and not icon.isNull():
                    pixmap = icon.pixmap(size, size)
                    if not pixmap.isNull():
                        self.old_icon_label.setPixmap(pixmap)
                        self.old_info_label.setText(f"Size: {size}x{size}\nMethod: Single size")
                    else:
                        self.old_info_label.setText("Failed to create pixmap")
                else:
                    self.old_info_label.setText("Icon extraction failed")
                    
            except Exception as e:
                self.old_info_label.setText(f"Error: {str(e)}")
        
        def _update_new_method(self):
            """Update the new method display."""
            try:
                method = self.method_combo.currentText()
                size = self.new_size_spin.value()
                quality = self.quality_combo.currentText()
                
                if method == "Multi-size extraction":
                    icon = IconExtractor.extract_icon_multi_size(self.test_file, [16, 24, 32, 48, 64, 128])
                elif method == "High-quality scaling":
                    base_icon = IconExtractor.extract_icon_multi_size(self.test_file, [32, 48, 64, 128])
                    icon = IconExtractor.create_high_quality_icon(base_icon, size)
                elif method == "DPI-aware scaling":
                    base_icon = IconExtractor.extract_icon_multi_size(self.test_file, [32, 48, 64, 128])
                    icon = IconExtractor.create_dpi_aware_icon(base_icon, size, 1.0)
                elif method == "Quality-aware extraction":
                    quality_settings = {
                        'use_high_quality_scaling': quality != 'Low',
                        'use_dpi_aware_scaling': quality == 'High',
                        'preferred_source_sizes': [32, 48, 64, 128] if quality == 'High' else [32, 48, 64],
                        'fallback_scaling_method': 'smooth' if quality == 'High' else 'fast',
                        'cache_enabled': True,
                        'cache_size_limit': 100
                    }
                    icon = IconExtractor.extract_icon_with_quality(self.test_file, size, quality_settings)
                else:
                    icon = IconExtractor.extract_icon(self.test_file, size)
                
                if icon and not icon.isNull():
                    pixmap = icon.pixmap(size, size)
                    if not pixmap.isNull():
                        self.new_icon_label.setPixmap(pixmap)
                        available_sizes = icon.availableSizes()
                        self.new_info_label.setText(f"Size: {size}x{size}\nMethod: {method}\nAvailable: {len(available_sizes)} sizes")
                    else:
                        self.new_info_label.setText("Failed to create pixmap")
                else:
                    self.new_info_label.setText("Icon extraction failed")
                    
            except Exception as e:
                self.new_info_label.setText(f"Error: {str(e)}")
        
        def _update_results_analysis(self):
            """Update the results analysis text."""
            try:
                analysis = []
                analysis.append("=== ICON SCALING ANALYSIS ===\n")
                
                # Compare available sizes
                old_icon = IconExtractor.extract_icon(self.test_file, 48)
                new_icon = IconExtractor.extract_icon_multi_size(self.test_file, [16, 24, 32, 48, 64, 128])
                
                old_sizes = old_icon.availableSizes() if old_icon and not old_icon.isNull() else []
                new_sizes = new_icon.availableSizes() if new_icon and not new_icon.isNull() else []
                
                analysis.append(f"Old method available sizes: {len(old_sizes)}")
                if old_sizes:
                    analysis.append(f"  Sizes: {', '.join([f'{s.width()}x{s.height()}' for s in old_sizes])}")
                
                analysis.append(f"\nNew method available sizes: {len(new_sizes)}")
                if new_sizes:
                    analysis.append(f"  Sizes: {', '.join([f'{s.width()}x{s.height()}' for s in new_sizes])}")
                
                # Quality assessment
                if len(new_sizes) > len(old_sizes):
                    analysis.append("\n✓ IMPROVEMENT: More icon sizes available")
                else:
                    analysis.append("\n⚠ No improvement in available sizes")
                
                if max(new_sizes, key=lambda s: s.width()).width() > max(old_sizes, key=lambda s: s.width()).width() if old_sizes else 0:
                    analysis.append("✓ IMPROVEMENT: Higher resolution icons available")
                else:
                    analysis.append("⚠ No improvement in resolution")
                
                # Performance note
                analysis.append("\n=== PERFORMANCE NOTES ===")
                analysis.append("• First run: Slightly slower due to multi-size extraction")
                analysis.append("• Subsequent runs: Faster due to intelligent caching")
                analysis.append("• Memory usage: Slightly higher but configurable")
                analysis.append("• Quality: Significantly better scaling and appearance")
                
                self.results_text.setPlainText("\n".join(analysis))
                
            except Exception as e:
                self.results_text.setPlainText(f"Error in analysis: {str(e)}")
        
        def _clear_cache(self):
            """Clear the icon cache."""
            try:
                IconExtractor.clear_cache()
                self.results_text.append("\n✓ Icon cache cleared successfully")
                self.update_comparison()
            except Exception as e:
                self.results_text.append(f"\n✗ Error clearing cache: {str(e)}")
        
        def _run_diagnostics(self):
            """Run icon diagnostics on the test file."""
            try:
                diagnostics = IconExtractor.get_icon_diagnostics(self.test_file)
                
                diag_text = "\n=== ICON DIAGNOSTICS ===\n"
                diag_text += f"File: {diagnostics['file_path']}\n"
                diag_text += f"Exists: {diagnostics['file_exists']}\n"
                diag_text += f"Type: {diagnostics['file_type']}\n"
                diag_text += f"Methods: {', '.join(diagnostics['extraction_methods'])}\n"
                diag_text += f"Available sizes: {', '.join(map(str, diagnostics['available_sizes']))}\n"
                
                if diagnostics['errors']:
                    diag_text += f"\nErrors: {', '.join(diagnostics['errors'])}\n"
                
                if diagnostics['recommendations']:
                    diag_text += f"\nRecommendations: {', '.join(diagnostics['recommendations'])}\n"
                
                self.results_text.append(diag_text)
                
            except Exception as e:
                self.results_text.append(f"\n✗ Error running diagnostics: {str(e)}")
        
        def _show_error(self, message):
            """Show an error message."""
            self.results_text.setPlainText(f"ERROR: {message}")
    
    def main():
        app = QApplication(sys.argv)
        window = IconImprovementDemo()
        window.show()
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure PySide6 is installed and main.py is in the same directory")
except Exception as e:
    print(f"Error: {e}")
