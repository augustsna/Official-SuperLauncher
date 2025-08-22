from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QShortcut, QKeySequence


class MessageBox(QDialog):
    """Reusable message box with minimal styling options."""

    def __init__(self, parent=None, title="Message", message="", kind="info"):
        super().__init__(parent)
        self.kind = kind
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.setMaximumSize(300, 200)
        self._init_ui(title, message)

    def _init_ui(self, title, message):
        self.setStyleSheet(f"""
            QDialog {{
                background: #f5f7fa;
                border-radius: 10px;
            }}
            QLabel#iconLabel {{
                font-size: 30px;
                color: {self._icon_color()};
            }}
            QLabel#titleLabel {{
                font-size: 15px;
                color: #000000;
                font-weight: 700;
            }}
            QLabel#messageLabel {{
                font-size: 14px;
                color: #222;
                font-weight: 500;
            }}
            QPushButton {{
                background-color: {self._button_color()};
                color: {self._button_text_color()};
                font-size: 13px;
                padding: 7px 18px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {self._button_hover_color()};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 25)
        layout.setSpacing(0)

        icon = QLabel(self._icon_text())
        icon.setObjectName("iconLabel")
        icon.setAlignment(Qt.AlignHCenter)
        layout.addWidget(icon)

        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setAlignment(Qt.AlignHCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        btn_row.addWidget(ok_button)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _icon_text(self):
        return {"info": "ℹ", "success": "✓", "warning": "⚠️", "error": "✕"}.get(self.kind, "ℹ")

    def _icon_color(self):
        return {"info": "#4a90e2", "success": "#28a745", "warning": "#e67e22", "error": "#dc3545"}.get(self.kind, "#4a90e2")

    def _button_color(self):
        return {"info": "#4a90e2", "success": "#28a745", "warning": "#ffc107", "error": "#dc3545"}.get(self.kind, "#4a90e2")

    def _button_hover_color(self):
        return {"info": "#357ABD", "success": "#218838", "warning": "#e0a800", "error": "#c82333"}.get(self.kind, "#357ABD")

    def _button_text_color(self):
        return {"warning": "black"}.get(self.kind, "white")


def info(parent, title, message):
    MessageBox(parent, title, message, "info").exec()


def success(parent, title, message):
    MessageBox(parent, title, message, "success").exec()


def warning(parent, title, message):
    MessageBox(parent, title, message, "warning").exec()


def error(parent, title, message):
    MessageBox(parent, title, message, "error").exec()

class CustomWDialog(QDialog):
    """Custom warning dialog with consistent styling"""
    def __init__(self, parent=None, title="⚠️ Warning", message=""):
        super().__init__(parent)

        icon_path = icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.setMaximumSize(300, 200)
        self.resize(300, 200)
        self.setStyleSheet(
            """
            QDialog {
                background: #f5f7fa;
                border-radius: 10px;
            }
            QLabel#iconLabel {
                font-size: 30px;
                color: #e67e22;
                margin: 0;
                padding: 0;
            }
            QLabel#titleLabel {
                font-size: 15px;
                color: #000000;
                font-weight: 700;
                margin-bottom: 8px;
            }
            QLabel#messageLabel {
                font-size: 14px;
                color: #222;
                font-weight: 500;
                margin-top: 4px;
                margin-bottom: 4px;
                line-height: 1.4;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-size: 13px;
                padding: 7px 18px;
                border-radius: 6px;
                min-width: 90px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        icon = QLabel("⚠️")
        icon.setObjectName("iconLabel")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(icon)

        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        self.adjustSize()

    def _close_dialog(self):
        self.close()
        return None