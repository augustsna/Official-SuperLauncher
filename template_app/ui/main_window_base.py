import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from template_app.config import load_app_settings, project_root
from template_app.styles import apply_app_style


class MainWindowBase(QWidget):
    """Base main window that applies app settings and layout scaffold."""

    def __init__(self):
        super().__init__()
        self.app_settings = load_app_settings()
        self._init_window()
        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(10, 0, 10, 10)
        self.root_layout.setSpacing(0)

        # Header and body containers
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        # Wrap layouts in widgets to control vertical sizing behavior
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(80)
        self.header_widget.setLayout(self.header_layout)

        self.body_widget = QWidget()
        self.body_widget.setLayout(self.body_layout)

        self.root_layout.addWidget(self.header_widget)
        self.root_layout.addWidget(self.body_widget)
        self.setLayout(self.root_layout)

        # Provide a simple default header/body content
        self._build_default_ui()

        # Keyboard shortcut: Ctrl+W closes the window
        self._shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        self._shortcut_close.activated.connect(self.close)

    def _build_default_ui(self):
        title = QLabel(self.app_settings.window_title)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        self.header_layout.addStretch()
        self.header_layout.addWidget(title)
        self.header_layout.addStretch()

        hello_btn = QPushButton("Hello World")
        # Center button horizontally and vertically within body
        self.body_layout.addStretch()
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(hello_btn)
        row.addStretch()
        self.body_layout.addLayout(row)
        self.body_layout.addStretch()

    def _init_window(self):
        self.setWindowTitle(self.app_settings.window_title)
        self.setMinimumSize(200, 300)
        # set a default window size - let the derived class handle it
        #self.resize(*self.app_settings.window_size)
        apply_app_style(self)

        icon_path = os.path.join(project_root(), self.app_settings.icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))


