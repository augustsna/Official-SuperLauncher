"""Centralized application stylesheet(s) for PyQt6 apps."""

# Default light theme stylesheet (inspired by Chrome-like UI)
DEFAULT_STYLE_SHEET = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    color: #333333;
    background-color: #202020;
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


