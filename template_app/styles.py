"""Centralized application stylesheet(s) for PyQt6 apps."""

# Default light theme stylesheet (inspired by Chrome-like UI)
DEFAULT_STYLE_SHEET = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    color: #333333;
    background-color: #f5f7fa;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #333333;
}

QPushButton {
    background-color: #4a90e2;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #357ABD;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
}

QLineEdit:hover {
    border: 2px solid #4a90e2;
    background-color: #ffffff;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
}

QComboBox:hover {
    border: 2px solid #4687f4;
}

QComboBox::drop-down {
    border: none;
    width: 0px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
    width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    selection-background-color: #3f92e3;
    border: 1px solid #ccc;
    outline: none;
}

/* Dark Context Menu Styles */
QMenu {
    background-color: #2d3748;
    color: #e2e8f0;
    border: 1px solid #4a5568;
    border-radius: 6px;
    padding: 4px 0px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QMenu::item {
    background-color: transparent;
    padding: 8px 16px;
    border: none;
    border-radius: 0px;
}

QMenu::item:selected {
    background-color: #4a5568;
    color: #ffffff;
}

QMenu::item:pressed {
    background-color: #2d3748;
    color: #e2e8f0;
}

QMenu::separator {
    height: 1px;
    background-color: #4a5568;
    margin: 4px 8px;
}

QMenu::indicator {
    width: 16px;
    height: 16px;
}

QMenu::indicator:non-exclusive:unchecked {
    image: none;
    border: 1px solid #718096;
    background-color: #2d3748;
    border-radius: 3px;
}

QMenu::indicator:non-exclusive:checked {
    image: none;
    border: 1px solid #3182ce;
    background-color: #3182ce;
    border-radius: 3px;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #333;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 6px;
    border: 1px solid #ccc;
    background: #ffffff;
}

QCheckBox::indicator:hover {
    background: #f5f9ff;
}

QCheckBox::indicator:unchecked {
    background: #ffffff;
    border: 1px solid #ccc;
}

QCheckBox::indicator:unchecked:hover {
    background: #f5f9ff;
}

QCheckBox::indicator:checked {
    background: #ffffff;
    border: 1px solid #ccc;
}

QScrollBar:vertical {
    background: rgba(240, 240, 240, 0.20);
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(192, 192, 192, 0.20);
    border-radius: 6px;
    min-height: 20px;
    margin: 0px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(160, 160, 160, 0.35);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(240, 240, 240, 0.20);
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: rgba(192, 192, 192, 0.20);
    border-radius: 6px;
    min-width: 20px;
    margin: 0px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(160, 160, 160, 0.35);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

def apply_app_style(widget):
    """Apply the default stylesheet to the given top-level widget."""
    widget.setStyleSheet(DEFAULT_STYLE_SHEET)


def apply_global_dark_theme():
    """Apply dark theme globally to affect all dialogs and message boxes."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPalette, QColor
        
        app = QApplication.instance()
        if app:
            # Apply global dark palette
            palette = app.palette()
            
            # Set dark colors for all widgets
            palette.setColor(QPalette.ColorRole.Window, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#404040"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#4a90e2"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#4a90e2"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            
            app.setPalette(palette)
            
            # Apply global dark stylesheet
            app.setStyleSheet(get_dark_dialog_stylesheet())
            
            print("Global dark theme applied successfully")
            
    except Exception as e:
        print(f"Error applying global dark theme: {e}")


def apply_dark_title_bar_theme(widget):
    """Apply dark title bar theme for Windows dialogs using Win32 API."""
    try:
        # Check if we're on Windows
        import platform
        if platform.system() != 'Windows':
            return
            
        # Try to import win32api
        try:
            import win32gui
            import win32con
            import win32api
            HAS_WIN32 = True
        except ImportError:
            # Fallback to ctypes
            try:
                import ctypes
                from ctypes import wintypes
                HAS_WIN32 = True
            except ImportError:
                HAS_WIN32 = False
        
        if HAS_WIN32:
            # Get the window handle
            hwnd = widget.winId().__int__()
            
            # Set dark title bar using Windows 10+ dark mode API
            # This requires Windows 10 version 1809 or later
            try:
                # Constants for dark mode
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                DWMWA_CAPTION_COLOR = 35
                DWMWA_TEXT_COLOR = 36
                
                # Try to set dark mode for title bar
                try:
                    # Set immersive dark mode (Windows 10 1809+)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 
                        DWMWA_USE_IMMERSIVE_DARK_MODE, 
                        ctypes.byref(wintypes.BOOL(True)), 
                        ctypes.sizeof(wintypes.BOOL)
                    )
                except Exception:
                    pass  # Fallback if not supported
                
                # Set custom caption color (Windows 11 22H2+)
                try:
                    # Dark gray color for caption - matching main window
                    caption_color = 0x002f2f2f  # RGB(47, 47, 47)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 
                        DWMWA_CAPTION_COLOR, 
                        ctypes.byref(wintypes.DWORD(caption_color)), 
                        ctypes.sizeof(wintypes.DWORD)
                    )
                except Exception:
                    pass  # Fallback if not supported
                
                # Set custom text color (Windows 11 22H2+)
                try:
                    # White color for text
                    text_color = 0x00FFFFFF  # RGB(255, 255, 255)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 
                        DWMWA_TEXT_COLOR, 
                        ctypes.byref(wintypes.DWORD(text_color)), 
                        ctypes.sizeof(wintypes.DWORD)
                    )
                except Exception:
                    pass  # Fallback if not supported
                
                print("Dark title bar theme applied to dialog successfully")
                
            except Exception as e:
                print(f"Error applying dark title bar theme to dialog: {e}")
                # Fallback: Use Qt styling for title bar
                _apply_fallback_dialog_styling(widget)
                
        else:
            print("Win32 API not available - using fallback dialog styling")
            _apply_fallback_dialog_styling(widget)
            
    except Exception as e:
        print(f"Error applying dark title bar theme to dialog: {e}")
        # Fallback: Use Qt styling for title bar
        _apply_fallback_dialog_styling(widget)


def _apply_fallback_dialog_styling(widget):
    """Apply fallback title bar styling using Qt for dialogs."""
    try:
        # Set window title with custom styling
        if hasattr(widget, 'setWindowTitle'):
            widget.setWindowTitle(widget.windowTitle())
        
        # Apply custom palette for title bar colors
        from PySide6.QtGui import QPalette, QColor
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            palette = app.palette()
            
            # Set dark colors for title bar
            palette.setColor(QPalette.ColorRole.Window, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2f2f2f"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
            
            # Apply palette to the dialog
            widget.setPalette(palette)
            
            print("Fallback dialog title bar styling applied")
            
    except Exception as e:
        print(f"Error applying fallback dialog styling: {e}")


def get_dark_dialog_stylesheet():
    """Get dark theme stylesheet for dialogs."""
    return """
    QDialog {
        background-color: #2f2f2f;
        color: #ffffff;
        border: none;
    }
    
    QMessageBox {
        background-color: #2f2f2f;
        color: #ffffff;
        border: none;
    }
    
    QMessageBox QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    
    QMessageBox QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: bold;
        min-width: 80px;
    }
    
    QMessageBox QPushButton:hover {
        background-color: #505050;
        border-color: #666666;
    }
    
    QMessageBox QPushButton:pressed {
        background-color: #353535;
        border-color: #444444;
    }
    
    QInputDialog {
        background-color: #2f2f2f;
        color: #ffffff;
        border: none;
    }
    
    QInputDialog QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    
    QInputDialog QLineEdit {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
    
    QInputDialog QLineEdit:focus {
        border-color: #666666;
        background-color: #454545;
    }
    
    QInputDialog QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: bold;
        min-width: 80px;
    }
    
    QInputDialog QPushButton:hover {
        background-color: #505050;
        border-color: #666666;
    }
    
    QInputDialog QPushButton:pressed {
        background-color: #353535;
        border-color: #444444;
    }
    
    QDialog QWidget {
        background-color: #2f2f2f;
        color: #ffffff;
    }
    
    QDialog QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: bold;
    }
    
    QDialog QPushButton:hover {
        background-color: #505050;
        border-color: #666666;
    }
    
    QDialog QPushButton:pressed {
        background-color: #353535;
        border-color: #444444;
    }
    
    QDialog QLineEdit {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
    
    QDialog QLineEdit:focus {
        border-color: #666666;
        background-color: #454545;
    }
    
    QDialog QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    
    QDialog QGroupBox {
        color: #ffffff;
        background-color: #2f2f2f;
        border: 1px solid #555555;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    
    QDialog QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #ffffff;
    }
    
    QDialog QCheckBox {
        color: #ffffff;
        background-color: transparent;
        spacing: 8px;
    }
    
    QDialog QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 6px;
        border: 1px solid #555555;
        background: #404040;
    }
    
    QDialog QCheckBox::indicator:hover {
        background: #505050;
        border-color: #666666;
    }
    
    QDialog QCheckBox::indicator:checked {
        background: #ffffff;
        border-color: #777777;
    }
    
    QDialog QComboBox {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
    
    QDialog QComboBox:hover {
        border-color: #666666;
        background-color: #454545;
    }
    
    QDialog QComboBox QAbstractItemView {
        background-color: #404040;
        selection-background-color: #555555;
        border: 1px solid #555555;
        outline: none;
        color: #ffffff;
    }
    
    QDialog QComboBox QAbstractItemView::item:hover {
        background-color: #505050;
    }
    
    QDialog QComboBox QAbstractItemView::item:selected {
        background-color: #666666;
    }
    
    QDialog QSpinBox {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
    
    QDialog QSpinBox:focus {
        border-color: #666666;
        background-color: #454545;
    }
    
    QDialog QSpinBox::up-button, QDialog QSpinBox::down-button {
        background-color: #505050;
        border: 1px solid #555555;
        border-radius: 3px;
        width: 16px;
    }
    
    QDialog QSpinBox::up-button:hover, QDialog QSpinBox::down-button:hover {
        background-color: #606060;
        border-color: #666666;
    }
    
    QDialog QSlider::groove:horizontal {
        border: 1px solid #555555;
        height: 8px;
        background: #404040;
        border-radius: 4px;
    }
    
    QDialog QSlider::handle:horizontal {
        background: #666666;
        border: 1px solid #777777;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    
    QDialog QSlider::handle:horizontal:hover {
        background: #777777;
        border-color: #888888;
    }
    
    QDialog QSlider::sub-page:horizontal {
        background: #666666;
        border-radius: 4px;
    }
    
    QDialog QSlider::add-page:horizontal {
        background: #404040;
        border-radius: 4px;
    }
    """


