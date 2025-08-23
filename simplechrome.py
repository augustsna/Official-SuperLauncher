import os
import sys
import json
import platform
import re
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QGroupBox, QFormLayout, QCheckBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QSettings, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor

# Sample configuration constants
WINDOW_SIZE = (760, 577)
WINDOW_TITLE = "Sample chrome UI"
ICON_PATH = "src/icon.png"
PROJECT_ROOT = "."

# Sample stylesheet with correct colors matching chrome
STYLE_SHEET = """
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
    image: url(src/sources/black_tick.svg);
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

class CustomMessageBox(QDialog):
    """Custom message box dialog with consistent styling"""
    
    def __init__(self, parent=None, title="Message", message="", message_type="info"):
        super().__init__(parent)
        
        # Performance optimizations for smoother dialog
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.setMaximumSize(300, 200)
        self.resize(300, 200)
        self.message_type = message_type
        self.init_ui(title, message)
        
    def init_ui(self, title, message):
        """Initialize the dialog UI"""
        self.setStyleSheet(f"""
            QDialog {{
                background: #f5f7fa;
                border-radius: 10px;
            }}
            QLabel#iconLabel {{
                font-size: 30px;
                color: {self.get_icon_color()};
                margin: 0;
                padding: 0;
            }}
            QLabel#titleLabel {{
                font-size: 15px;
                color: #000000;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            QLabel#messageLabel {{
                font-size: 14px;
                color: #222;
                font-weight: 500;
                margin-top: 4px;
                margin-bottom: 4px;
                line-height: 1.4;
            }}
            QPushButton {{
                background-color: {self.get_button_color()};
                color: {self.get_button_text_color()};
                font-size: 13px;
                padding: 7px 18px;
                border-radius: 6px;
                margin-top: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.get_button_hover_color()};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 25)
        layout.setSpacing(0)

        # Icon
        icon = QLabel(self.get_icon_text())
        icon.setObjectName("iconLabel")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(icon)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Buttons row
        self.btn_row = QHBoxLayout()
        self.btn_row.addStretch()
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedWidth(100)  # Set specific width and height
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        self.btn_row.addWidget(self.ok_button)
        self.btn_row.addStretch()
        layout.addLayout(self.btn_row)

        # Shortcut
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        self.adjustSize()
        
    def get_icon_text(self):
        """Get icon text based on message type"""
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠️", 
            "error": "✕"
        }
        return icons.get(self.message_type, "ℹ")
        
    def get_icon_color(self):
        """Get icon color based on message type"""
        colors = {
            "info": "#4a90e2",
            "success": "#28a745",
            "warning": "#e67e22", 
            "error": "#dc3545"
        }
        return colors.get(self.message_type, "#4a90e2")
        
    def get_button_color(self):
        """Get button color based on message type"""
        colors = {
            "info": "#4a90e2",
            "success": "#28a745",
            "warning": "#ffc107", #e67e22
            "error": "#dc3545"
        }
        return colors.get(self.message_type, "#4a90e2")
        
    def get_button_hover_color(self):
        """Get button hover color based on message type"""
        colors = {
            "info": "#357ABD",
            "success": "#218838", 
            "warning": "#e0a800", #d35400
            "error": "#c82333"
        }
        return colors.get(self.message_type, "#357ABD")
    
    def get_button_text_color(self):
        """Get button text color based on message type"""
        colors = {
            "info": "white",
            "success": "white",
            "warning": "black",
            "error": "white"
        }
        return colors.get(self.message_type, "white")
    
    @staticmethod
    def show_info(parent, title, message):
        """Show info message box"""
        dialog = CustomMessageBox(parent, title, message, "info")
        dialog.exec()
        
    @staticmethod
    def show_success(parent, title, message):
        """Show success message box"""
        dialog = CustomMessageBox(parent, title, message, "success")
        dialog.exec()
        
    @staticmethod
    def show_warning(parent, title, message):
        """Show warning message box"""
        dialog = CustomMessageBox(parent, title, message, "warning")
        dialog.exec()
        
    @staticmethod
    def show_error(parent, title, message):
        """Show error message box"""
        dialog = CustomMessageBox(parent, title, message, "error")
        dialog.exec()
        
    @staticmethod
    def show_confirmation(parent, title, message):
        """Show confirmation dialog with Yes/No buttons"""
        dialog = CustomMessageBox(parent, title, message, "warning")
        
        # Replace the OK button with Yes/No buttons
        ok_button = dialog.ok_button
        ok_button.setText("Yes")
        ok_button.setFixedSize(100, 30)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745 !important;
                color: white !important;
                border-radius: 6px !important;
                padding: 4px 8px !important;
                font-size: normal !important;
                margin-top: 0px !important;
            }
            QPushButton:hover {
                background-color: #218838 !important;
            }
        """)
        
        # Add No button ##1
        no_button = QPushButton("No")
        no_button.setFixedSize(100, 30)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2 !important;
                color: white !important;
                border-radius: 6px !important;
                padding: 4px 8px !important;
                font-size: normal !important;
                margin-top: 0px !important;
            }
            QPushButton:hover {
                background-color: #357ABD !important;
            }
        """)
        no_button.clicked.connect(dialog.reject)
        
        # Update the button layout - clear existing widgets and add in correct order
        # Remove existing widgets from btn_row
        while dialog.btn_row.count():
            child = dialog.btn_row.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Add buttons directly to btn_row in correct order: Yes, then No
        dialog.btn_row.addStretch()
        dialog.btn_row.addWidget(ok_button)  # Yes button
        dialog.btn_row.addSpacing(10)
        dialog.btn_row.addWidget(no_button)  # No button
        dialog.btn_row.addStretch()
        
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted


class EditProfileDialog(QDialog):
    """Dialog for editing profile information"""
    
    def __init__(self, parent=None, profile_data=None):
        super().__init__(parent)
        self.profile_data = profile_data or {}
        self.setWindowTitle("Edit Profile")
        # Calculate dynamic height based on channel types and sub types
        channel_types = self.load_channel_types()
        sub_types = self.load_sub_types()
        
        # Calculate extra height for channel types (2 buttons per row)
        channel_rows_needed = (len(channel_types) + 2) // 2  
        channel_extra_height = max(0, (channel_rows_needed - 2)) * 40
        
        # Calculate extra height for sub types (2 buttons per row)
        sub_rows_needed = (len(sub_types) + 1) // 2  # 2 buttons per row
        sub_extra_height = max(0, (sub_rows_needed - 2)) * 40  # 40px per extra row
        
        # Total extra height needed
        total_extra_height = channel_extra_height + sub_extra_height
        dynamic_height = 610 + total_extra_height
        
        self.setFixedSize(500, dynamic_height)
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("Edit Profile")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        # Profile field (read-only)
        self.profile_edit = QLineEdit()
        self.profile_edit.setText(self.profile_data.get('profile', ''))
        self.profile_edit.setReadOnly(True)  # Make it read-only
        self.profile_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        form_layout.addRow("Profile:", self.profile_edit)
        
        # Profile ID field (read-only for Chrome profiles)
        self.profile_id_edit = QLineEdit()
        self.profile_id_edit.setText(self.profile_data.get('profile_id', ''))
        self.profile_id_edit.setReadOnly(True)  # Make it read-only
        self.profile_id_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        form_layout.addRow("Profile ID:", self.profile_id_edit)
        
        # Email field (read-only)
        self.email_edit = QLineEdit()
        self.email_edit.setText(self.profile_data.get('email', ''))
        self.email_edit.setReadOnly(True)  # Make it read-only
        self.email_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        form_layout.addRow("Email:", self.email_edit)

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.profile_data.get('name', ''))
        self.name_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
        """)
        form_layout.addRow("Name:", self.name_edit)
        
        layout.addLayout(form_layout)
        
        # Total Channel field
        self.total_channel_edit = QLineEdit()
        self.total_channel_edit.setText(self.profile_data.get('total_channel', ''))
        self.total_channel_edit.setPlaceholderText("Enter total number of channels")
        # Add number-only validation
        from PyQt6.QtGui import QIntValidator
        self.total_channel_edit.setValidator(QIntValidator(0, 999999))  # Allow 0 to 999999
        self.total_channel_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
        """)
        form_layout.addRow("Amount:", self.total_channel_edit)
        
        # Notes field
        self.notes_edit = QLineEdit()
        self.notes_edit.setText(self.profile_data.get('notes', ''))
        self.notes_edit.setPlaceholderText("Enter notes about this profile")
        self.notes_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px 4px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
        """)
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Channel Types field (toggle buttons instead of list)
        from PyQt6.QtWidgets import QFrame
        
        # Create a container for channel type buttons
        self.channel_types_container = QFrame()
        self.channel_types_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                min-height: 90px;
            }
        """)
        
        # Create layout for channel type buttons
        self.channel_types_layout = QVBoxLayout(self.channel_types_container)
        self.channel_types_layout.setSpacing(5)
        self.channel_types_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create grid layout for buttons (3 per row)
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(5)
        
        # Load channel types and create toggle buttons
        channel_types = self.load_channel_types()
        self.channel_type_buttons = {}
        
        for i, channel_type in enumerate(channel_types):
            button = QPushButton(channel_type)
            button.setCheckable(True)  # Make it a toggle button
            button.setFixedSize(150, 30)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f0f8ff;
                    border: 1px solid #4a90e2;
                }
                QPushButton:pressed {
                    background-color: #e3f2fd;
                }
                QPushButton:checked {
                    background-color: #4a90e2;
                    color: white;
                    border: 1px solid #4a90e2;
                    font-weight: 600;
                }
                QPushButton:checked:hover {
                    background-color: #357ABD;
                }
                QPushButton:checked:pressed {
                    background-color: #2e6da4;
                }
            """)
            
            # Store button reference
            self.channel_type_buttons[channel_type] = button
            
            # Add button to grid (3 per row)
            row = i // 2
            col = i % 2
            buttons_layout.addWidget(button, row, col)
        
        # Add utility buttons
        utility_layout = QHBoxLayout()
        utility_layout.setSpacing(5)
        
        # Select All button
        select_all_btn = QPushButton("All")
        select_all_btn.setFixedSize(60, 28)
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #47a4ff;
            }
        """)
        select_all_btn.clicked.connect(self.select_all_channel_types)
        
        # Clear All button
        clear_all_btn = QPushButton("Clear")
        clear_all_btn.setFixedSize(60, 28)
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #ff6b6b;
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_channel_types)
        
        utility_layout.addStretch()
        utility_layout.addWidget(select_all_btn)
        utility_layout.addWidget(clear_all_btn)
        
        # Add buttons layout to main layout
        self.channel_types_layout.addLayout(buttons_layout)
        
        # Add utility buttons to the main layout
        self.channel_types_layout.addLayout(utility_layout)
               
        # Set current selections
        current_channel_types = self.profile_data.get('channel_types', [])
        if isinstance(current_channel_types, str):
            # Handle legacy single channel_type
            current_channel_types = [current_channel_types] if current_channel_types else ['user_custom']
        
        for channel_type in current_channel_types:
            if channel_type in self.channel_type_buttons:
                self.channel_type_buttons[channel_type].setChecked(True)
        
        # Ensure at least one channel type is selected (default to user_custom)
        if not any(button.isChecked() for button in self.channel_type_buttons.values()):
            if 'user_custom' in self.channel_type_buttons:
                self.channel_type_buttons['user_custom'].setChecked(True)
        
        form_layout.addRow("Channel type:", self.channel_types_container)
        
        # Sub Types field (toggle buttons like channel types)
        # Create a container for sub type buttons
        self.sub_types_container = QFrame()
        self.sub_types_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                min-height: 90px;
            }
        """)
        
        # Create layout for sub type buttons
        self.sub_types_layout = QVBoxLayout(self.sub_types_container)
        self.sub_types_layout.setSpacing(5)
        self.sub_types_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create grid layout for buttons (2 per row)
        sub_buttons_layout = QGridLayout()
        sub_buttons_layout.setSpacing(5)
        
        # Load sub types and create toggle buttons
        sub_types = self.load_sub_types()
        self.sub_type_buttons = {}
        
        for i, sub_type in enumerate(sub_types):
            button = QPushButton(sub_type)
            button.setCheckable(True)  # Make it a toggle button
            button.setFixedSize(150, 30)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f0f8ff;
                    border: 1px solid #4a90e2;
                }
                QPushButton:pressed {
                    background-color: #e3f2fd;
                }
                QPushButton:checked {
                    background-color: #4a90e2;
                    color: white;
                    border: 1px solid #4a90e2;
                    font-weight: 600;
                }
                QPushButton:checked:hover {
                    background-color: #357ABD;
                }
                QPushButton:checked:pressed {
                    background-color: #2e6da4;
                }
            """)
            
            # Store button reference
            self.sub_type_buttons[sub_type] = button
            
            # Add button to grid (2 per row)
            row = i // 2
            col = i % 2
            sub_buttons_layout.addWidget(button, row, col)
        
        # Add utility buttons for sub types
        sub_utility_layout = QHBoxLayout()
        sub_utility_layout.setSpacing(5)
        
        # Select All button for sub types
        sub_select_all_btn = QPushButton("All")
        sub_select_all_btn.setFixedSize(60, 28)
        sub_select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #47a4ff;
            }
        """)
        sub_select_all_btn.clicked.connect(self.select_all_sub_types)
        
        # Clear All button for sub types
        sub_clear_all_btn = QPushButton("Clear")
        sub_clear_all_btn.setFixedSize(60, 28)
        sub_clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #ff6b6b;
            }
        """)
        sub_clear_all_btn.clicked.connect(self.clear_all_sub_types)
        
        sub_utility_layout.addStretch()
        sub_utility_layout.addWidget(sub_select_all_btn)
        sub_utility_layout.addWidget(sub_clear_all_btn)
        
        # Add sub buttons layout to main layout
        self.sub_types_layout.addLayout(sub_buttons_layout)
        
        # Add utility buttons to the main layout
        self.sub_types_layout.addLayout(sub_utility_layout)
               
        # Set current selections for sub types
        current_sub_types = self.profile_data.get('sub_types', [])
        if isinstance(current_sub_types, str):
            # Handle legacy single sub_type
            current_sub_types = [current_sub_types] if current_sub_types else []
        
        for sub_type in current_sub_types:
            if sub_type in self.sub_type_buttons:
                self.sub_type_buttons[sub_type].setChecked(True)
        
        form_layout.addRow("Sub type:", self.sub_types_container)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 30)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: normal;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(100, 30)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: normal;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Buttons
        layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Add keyboard shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        
    def get_profile_data(self):
        """Get the edited profile data"""
        return {
            'name': self.name_edit.text().strip(),
            'profile': self.profile_edit.text().strip(),
            'channel_types': self.get_selected_channel_types(),
            'sub_types': self.get_selected_sub_types(),
            'profile_id': self.profile_id_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'total_channel': self.total_channel_edit.text().strip(),
            'notes': self.notes_edit.text().strip()
        }
        
    def load_channel_types(self):
        """Load channel types from config.json file"""
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
                return config.get('channel_types', ['user_custom'])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config.json: {e}")
            # Return default channel types if config file is not found or invalid
            return ['user_custom', 'Chrome Profile', 'Standard', 'Premium', 'Basic']
    
    def get_selected_channel_types(self):
        """Get the selected channel types from the toggle buttons"""
        selected_types = []
        for channel_type, button in self.channel_type_buttons.items():
            if button.isChecked():
                selected_types.append(channel_type)
        return selected_types if selected_types else ['user_custom']
    
    def select_all_channel_types(self):
        """Select all channel types"""
        for button in self.channel_type_buttons.values():
            button.setChecked(True)
    
    def clear_all_channel_types(self):
        """Clear all channel types and set default to user_custom"""
        for button in self.channel_type_buttons.values():
            button.setChecked(False)
        # Ensure at least one is selected (user_custom)
        if 'user_custom' in self.channel_type_buttons:
            self.channel_type_buttons['user_custom'].setChecked(True)
    
    def load_sub_types(self):
        """Load sub types from config.json file"""
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
                return config.get('sub_types', ['Personal'])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config.json: {e}")
            # Return default sub types if config file is not found or invalid
            return ['Personal', 'Business', 'Gaming', 'Development', 'Testing', 'Marketing', 'Education']
    
    def get_selected_sub_types(self):
        """Get the selected sub types from the toggle buttons"""
        selected_types = []
        for sub_type, button in self.sub_type_buttons.items():
            if button.isChecked():
                selected_types.append(sub_type)
        return selected_types if selected_types else ['Personal']
    
    def select_all_sub_types(self):
        """Select all sub types"""
        for button in self.sub_type_buttons.values():
            button.setChecked(True)
    
    def clear_all_sub_types(self):
        """Clear all sub types and set default to Personal"""
        for button in self.sub_type_buttons.values():
            button.setChecked(False)
        # Ensure at least one is selected (Personal)
        if 'Personal' in self.sub_type_buttons:
            self.sub_type_buttons['Personal'].setChecked(True)
    


class DeletedProfileDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate to handle styling of deleted profiles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.deleted_rows = set()
    
    def set_deleted_rows(self, deleted_rows):
        """Set which rows contain deleted profiles"""
        self.deleted_rows = deleted_rows
    
    def paint(self, painter, option, index):
        """Custom paint method to style deleted profiles"""
        if index.row() in self.deleted_rows:
            # Fill background with light red color
            painter.fillRect(option.rect, QColor(255, 235, 235))
            
            # Set text color to gray
            painter.setPen(QColor(150, 150, 150))
            
            # Get the text from the item
            text = index.data()
            if text:
                # Draw the text with proper alignment
                alignment = Qt.AlignmentFlag.AlignVCenter
                if index.column() in [0, 4, 7, 8]:  # Number, Sub Type, Amount, Profile ID columns
                    alignment |= Qt.AlignmentFlag.AlignCenter
                    painter.drawText(option.rect, alignment, str(text))
                else:
                    alignment |= Qt.AlignmentFlag.AlignLeft
                    # Add left margin for Name, Profile, Channel Types, Email, and Notes columns
                    rect = option.rect
                    rect.setLeft(rect.left() + 12)  # Add 12px left margin
                    painter.drawText(rect, alignment, str(text))
        else:
            # Use default painting for non-deleted profiles
            super().paint(painter, option, index)


def natural_sort_key(text):
    """
    Generate a key for natural sorting that handles numeric parts correctly.
    This function splits strings into alternating text and number parts,
    converting numeric parts to integers for proper numerical sorting.
    """
    # Split the text into alternating text and number parts
    parts = re.split(r'(\d+)', str(text))
    # Convert numeric parts to integers, keep text parts as strings
    return [int(part) if part.isdigit() else part.lower() for part in parts]


class SamplechromeUI(QWidget):
    """Sample main application window demonstrating chrome UI structure"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Samplechrome', 'SamplechromeUI')
        self.config = self.load_config()
        self.profiles = self.load_profiles()
        self.init_ui()
        self.load_window_position()

    def load_config(self):
        """Load configuration from config.json file"""
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config.json: {e}")
            # Return default config if file is not found or invalid
            return {
                'channel_types': ['user_custom', 'Chrome Profile', 'Standard', 'Premium', 'Basic'],
                'app_settings': {
                    'window_title': 'Sample chrome UI',
                    'window_size': [760, 577],
                    'icon_path': 'src/icon.png'
                }
            }

    def load_profiles(self):
        """Load profiles from profile.json file"""
        try:
            with open('profile.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                profiles = data.get('profiles', [])
                
                # Migrate existing profiles to include email field, notes field, total_channel field, sub_types field, and channel_types if not present
                migrated = False
                for profile in profiles:
                    if 'email' not in profile:
                        profile['email'] = ''
                        migrated = True
                    
                    if 'notes' not in profile:
                        profile['notes'] = ''
                        migrated = True
                    
                    if 'total_channel' not in profile:
                        profile['total_channel'] = ''
                        migrated = True
                    
                    if 'sub_types' not in profile:
                        profile['sub_types'] = ['Personal']
                        migrated = True
                    
                    # Migrate channel_type to channel_types
                    if 'channel_type' in profile and 'channel_types' not in profile:
                        channel_type = profile.get('channel_type', 'user_custom')
                        profile['channel_types'] = [channel_type] if channel_type else ['user_custom']
                        migrated = True
                
                # Save migrated profiles back to file
                if migrated:
                    self.save_profiles(profiles)
                
                # Sort profiles alphabetically by profile name
                profiles.sort(key=lambda profile: profile.get('profile', '').lower())
                
                return profiles
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading profiles: {e}")
            return []

    def get_chrome_profiles(self):
        """Get Chrome profiles from the default Chrome user data directory"""
        chrome_profiles = []
        
        # Determine Chrome user data directory based on OS
        system = platform.system()
        if system == "Windows":
            chrome_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
        elif system == "Darwin":  # macOS
            chrome_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Google', 'Chrome')
        else:  # Linux
            chrome_data_dir = os.path.join(os.path.expanduser('~'), '.config', 'google-chrome')
        
        # Check if Chrome data directory exists
        if not os.path.exists(chrome_data_dir):
            return chrome_profiles
        
        # Look for Local State file to get profile info
        local_state_path = os.path.join(chrome_data_dir, 'Local State')
        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    profile_info = local_state.get('profile', {}).get('info_cache', {})
                    
                    for profile_id, profile_data in profile_info.items():
                        profile_name = profile_data.get('name', f'Profile {profile_id}')
                        
                        # Try to get email from profile preferences
                        email = self.get_profile_email(chrome_data_dir, profile_id)
                        
                        chrome_profiles.append({
                            'name': '',
                            'profile': profile_name,
                            'channel_types': ['user_custom'],
                            'sub_types': ['Personal'],
                            'profile_id': profile_id,
                            'email': email,
                            'total_channel': '',
                            'notes': ''
                        })
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading Chrome profiles: {e}")
        
        return chrome_profiles

    def get_profile_email(self, chrome_data_dir, profile_id):
        """Extract email from Chrome profile using multiple methods"""
        email = ''
        
        # Method 1: Try to get email from Local State file (most reliable)
        try:
            local_state_path = os.path.join(chrome_data_dir, 'Local State')
            if os.path.exists(local_state_path):
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    profile_info = local_state.get('profile', {}).get('info_cache', {})
                    
                    if profile_id in profile_info:
                        profile_data = profile_info[profile_id]
                        
                        # Check user_name field (often contains email)
                        user_name = profile_data.get('user_name', '')
                        if user_name and '@' in user_name:
                            email = user_name
                        
                        # Check gaia_id (Google account ID)
                        gaia_id = profile_data.get('gaia_id', '')
                        if gaia_id and not email:
                            # Try to extract email from gaia_id or related fields
                            pass
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error reading Local State for profile {profile_id}: {e}")
        
        # Method 2: Try to get email from profile preferences file
        if not email:
            try:
                preferences_path = os.path.join(chrome_data_dir, profile_id, 'Preferences')
                
                if os.path.exists(preferences_path):
                    with open(preferences_path, 'r', encoding='utf-8') as f:
                        preferences = json.load(f)
                        
                        # Check account_id_migration_state
                        account_migration = preferences.get('account_id_migration_state', {})
                        if account_migration:
                            email = account_migration.get('email', '')
                        
                        # Check profile content settings
                        if not email:
                            profile = preferences.get('profile', {})
                            if profile:
                                email = profile.get('email_address', '')
                        
                        # Check signin
                        if not email:
                            signin = preferences.get('signin', {})
                            if signin:
                                email = signin.get('email', '')
                        
                        # Check account_tracker_service
                        if not email:
                            account_tracker = preferences.get('account_tracker_service', {})
                            if account_tracker:
                                accounts = account_tracker.get('accounts', {})
                                for account_id, account_data in accounts.items():
                                    if isinstance(account_data, dict) and 'email' in account_data:
                                        email = account_data['email']
                                        break
                        
                        # Check identity
                        if not email:
                            identity = preferences.get('identity', {})
                            if identity:
                                email = identity.get('primary_account_email', '')
                        
                        # Check sync
                        if not email:
                            sync = preferences.get('sync', {})
                            if sync:
                                email = sync.get('requested', {}).get('email', '')
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error reading preferences for profile {profile_id}: {e}")
        
        # Method 3: Try to get email from Secure Preferences file
        if not email:
            try:
                secure_preferences_path = os.path.join(chrome_data_dir, profile_id, 'Secure Preferences')
                
                if os.path.exists(secure_preferences_path):
                    with open(secure_preferences_path, 'r', encoding='utf-8') as f:
                        secure_preferences = json.load(f)
                        
                        # Check account_id_migration_state in secure preferences
                        account_migration = secure_preferences.get('account_id_migration_state', {})
                        if account_migration:
                            email = account_migration.get('email', '')
                        
                        # Check profile in secure preferences
                        if not email:
                            profile = secure_preferences.get('profile', {})
                            if profile:
                                email = profile.get('email_address', '')
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error reading Secure Preferences for profile {profile_id}: {e}")
        
        return email.strip() if email else ''

    def validate_profile_exists(self, profile_id):
        """Check if a Chrome profile actually exists on disk"""
        if not profile_id:
            return False
            
        system = platform.system()
        if system == "Windows":
            chrome_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
        elif system == "Darwin":  # macOS
            chrome_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Google', 'Chrome')
        else:  # Linux
            chrome_data_dir = os.path.join(os.path.expanduser('~'), '.config', 'google-chrome')
        
        # Check if the profile directory exists
        profile_dir = os.path.join(chrome_data_dir, profile_id)
        return os.path.exists(profile_dir)

    def cleanup_deleted_profiles(self):
        """Remove profiles that no longer exist in Chrome"""
        valid_profiles = []
        deleted_profiles = []
        
        for profile in self.profiles:
            if self.validate_profile_exists(profile.get('profile_id', '')):
                valid_profiles.append(profile)
            else:
                deleted_profiles.append(profile)
        
        if deleted_profiles:
            # Show confirmation dialog with list of profiles to be deleted
            profile_names = [p.get('profile', '') for p in deleted_profiles]
            confirmation_message = f"{len(deleted_profiles)} profiles will be removed:\n\n"
            confirmation_message += f"{' , '.join(profile_names)}\n\n"
            confirmation_message += "This action cannot be undone.\n"
            
            # Create custom confirmation dialog
            reply = CustomMessageBox.show_confirmation(self, "Confirm Cleanup", confirmation_message)
            
            if reply:
                # User confirmed, proceed with cleanup
                self.profiles = valid_profiles
                
                # Sort profiles alphabetically by profile name after cleanup
                self.profiles.sort(key=lambda profile: profile.get('profile', '').lower())
                
                self.save_profiles(self.profiles)
                self.populate_profiles_table()
                
                # Show success notification
                CustomMessageBox.show_success(self, "Profiles Cleaned", 
                                           f"Successfully removed {len(deleted_profiles)} deleted profiles:\n{', '.join(profile_names)}")
        else:
            CustomMessageBox.show_info(self, "No Cleanup Needed", 
                                     "All profiles are valid and exist.")

    def check_deleted_profiles_on_startup(self):
        """Check for deleted profiles on startup and show a warning if found"""
        deleted_profiles = []
        
        for profile in self.profiles:
            if not self.validate_profile_exists(profile.get('profile_id', '')):
                deleted_profiles.append(profile)
        
        if deleted_profiles:
            profile_names = [p.get('profile', '') for p in deleted_profiles]
            CustomMessageBox.show_warning(self, "Deleted Profiles Found", 
                                        f"Found {len(deleted_profiles)} deleted Chrome profiles:\n\n"
                                        f"{' , '.join(profile_names)}")


    def save_profiles(self, profiles):
        """Save profiles to profile.json file"""
        try:
            with open('profile.json', 'w', encoding='utf-8') as file:
                json.dump({'profiles': profiles}, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving profiles: {e}")
            return False

    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        app_settings = self.config.get('app_settings', {})
        window_title = app_settings.get('window_title', WINDOW_TITLE)
        window_size = app_settings.get('window_size', WINDOW_SIZE)
        
        self.setWindowTitle(window_title)
        self.setMinimumSize(760, 577)
        self.resize(window_size[0], window_size[1])
        self.setStyleSheet(STYLE_SHEET)
        
        # Set window icon
        icon_path = os.path.join(PROJECT_ROOT, ICON_PATH)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Add keyboard shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)

        # --- TITLE AREA ---
        self.create_title_area(layout)
        
        # --- SCROLLABLE CONTENT AREA ---
        self.create_scrollable_content(layout)
        
        self.setLayout(layout)
        
        # Check for deleted profiles on startup after window is shown
        QTimer.singleShot(2000, self.check_deleted_profiles_on_startup)

    def create_title_area(self, layout):
        """Create the title area with icon and app name"""
        title_widget = QtWidgets.QWidget()
        title_widget.setFixedHeight(100)
        title_widget.setStyleSheet("background-color: transparent;")
        
        # Title icon
        title_icon = QLabel()
        icon_path = os.path.join(PROJECT_ROOT, ICON_PATH)
        if os.path.exists(icon_path):
            title_icon.setPixmap(QPixmap(icon_path).scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Fallback icon if file doesn't exist
            title_icon.setText("")
            title_icon.setStyleSheet("font-size: 45px; background-color: transparent;")
        
        # Title label
        title_label = QLabel("Simple Chrome")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; background-color: transparent; color: #333333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Static icon (placeholder)
        static_icon = QLabel("")
        static_icon.setStyleSheet("font-size: 24px; background-color: transparent;")
        static_icon.setVisible(True)
        
        # Title layout
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.addSpacing(35)
        title_layout.addStretch()
        title_layout.addWidget(title_icon)
        title_layout.addSpacing(10)
        title_layout.addWidget(title_label)
        title_layout.addSpacing(10)
        title_layout.addWidget(static_icon)
        title_layout.addStretch()
        title_widget.setLayout(title_layout)
        
        layout.addWidget(title_widget)



    def create_scrollable_content(self, layout):
        """Create the scrollable content area"""
        # Create scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
                margin-right: 0px;
                padding-right: 0px;
            }
        """)
        
        # Create scrollable content widget
        scroll_content = QtWidgets.QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 0, 20, 0)
        scroll_layout.setSpacing(10)
        
        # Add profiles section
        self.create_profiles_section(scroll_layout)
        
        # Set the scroll content widget
        scroll_area.setWidget(scroll_content)
        
        # Set height constraints for the scroll area
        scroll_area.setMinimumHeight(200)
        # Remove maximum height limit to allow table to resize with window
        
        layout.addWidget(scroll_area)
        
        # Store scroll area reference
        self.scroll_area = scroll_area

    def create_profiles_section(self, layout):
        """Create the profiles display section"""
        # Create search box with two rows
        search_layout = QVBoxLayout()
        search_layout.setSpacing(8)
        
        # First row - Search functionality
        
        
        # Search label
        search_label = QLabel("Search:")
        search_label.setFixedSize(80, 32)
        search_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
                font-size: 13px;
            }
        """)
        
        # Search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search names...")
        self.search_input.setFixedSize(210, 32)
        self.search_input.textChanged.connect(self.filter_profiles_table)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #47a4ff;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """)
        
        # Search scope dropdown
        self.search_scope = QComboBox()
        self.search_scope.addItems([
            "All Fields",
            "Name",
            "Profile", 
            "Email",
            "Notes",
            "Amount",
            "Profile ID"
        ])
        self.search_scope.setCurrentText("All Fields")
        self.search_scope.setFixedSize(120, 32)
        self.search_scope.currentTextChanged.connect(self.filter_profiles_table)
        self.search_scope.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox:focus {
                border: 1px solid #cccccc;
                outline: none;
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
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #ffffff;
                selection-background-color: #47a4ff;
                selection-color: #ffffff;
            }
        """)
        
        # Sort field label
        sort_field_label = QLabel("Sort by:")
        sort_field_label.setFixedSize(80, 32)
        sort_field_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sort_field_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
                font-size: 13px;
            }
        """)
        
        # Sort field dropdown
        self.sort_field_dropdown = QComboBox()
        self.sort_field_dropdown.addItems([
            "Name",
            "Profile",
            "Channel type",
            "Sub type",
            "Email",
            "Notes",
            "Amount",
            "Profile ID"
        ])
        self.sort_field_dropdown.setCurrentText("Profile")
        self.sort_field_dropdown.setFixedSize(120, 32)
        self.sort_field_dropdown.currentTextChanged.connect(self.sort_profiles_table)
        self.sort_field_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox:focus {
                border: 1px solid #cccccc;
                outline: none;
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
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #ffffff;
                selection-background-color: #47a4ff;
                selection-color: #ffffff;
            }
        """)
        
        # Sort order label
        sort_order_label = QLabel("Order:")
        sort_order_label.setFixedSize(80, 32)
        sort_order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sort_order_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
                font-size: 13px;
            }
        """)
        
        # Sort order dropdown
        self.sort_order_dropdown = QComboBox()
        self.sort_order_dropdown.addItems([
            "A-Z",
            "Z-A"
        ])
        self.sort_order_dropdown.setCurrentText("A-Z")
        self.sort_order_dropdown.setFixedSize(120, 32)
        self.sort_order_dropdown.currentTextChanged.connect(self.sort_profiles_table)
        self.sort_order_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox:focus {
                border: 1px solid #cccccc;
                outline: none;
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
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #ffffff;
                selection-background-color: #47a4ff;
                selection-color: #ffffff;
            }
        """)
        
        # Channel type filter label
        channel_filter_label = QLabel("Channel:")
        channel_filter_label.setFixedSize(80, 32)
        channel_filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        channel_filter_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
                font-size: 13px;
            }
        """)
        
        # Channel type filter dropdown
        self.channel_type_filter = QComboBox()
        self.channel_type_filter.addItem("All types")
        self.channel_type_filter.setFixedSize(120, 32)
        self.channel_type_filter.currentTextChanged.connect(self.filter_profiles_table)
        self.channel_type_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox:focus {
                border: 1px solid #cccccc;
                outline: none;
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
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #ffffff;
                selection-background-color: #47a4ff;
                selection-color: #ffffff;
            }
        """)
        
        # Sub type filter label
        sub_type_filter_label = QLabel("Sub type:")
        sub_type_filter_label.setFixedSize(80, 32)
        sub_type_filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_type_filter_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: 500;
                font-size: 13px;
            }
        """)
        
        # Sub type filter dropdown
        self.sub_type_filter = QComboBox()
        self.sub_type_filter.addItem("All Sub types")
        self.sub_type_filter.setFixedSize(120, 32)
        self.sub_type_filter.currentTextChanged.connect(self.filter_profiles_table)
        self.sub_type_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox:focus {
                border: 1px solid #cccccc;
                outline: none;
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
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #ffffff;
                selection-background-color: #47a4ff;
                selection-color: #ffffff;
            }
        """)
        search_row1 = QHBoxLayout()
        search_row1.addStretch()
        search_row1.addWidget(search_label)
        search_row1.addWidget(self.search_scope)
        search_row1.addSpacing(20)
        search_row1.addWidget(self.search_input)
        search_row1.addStretch()
        
        # Second row - Channel Type and Sub Type filters
        search_row2 = QHBoxLayout()
        search_row2.addStretch()
        search_row2.addWidget(channel_filter_label)
        search_row2.addWidget(self.channel_type_filter)
        search_row2.addSpacing(20)
        search_row2.addWidget(sub_type_filter_label)
        search_row2.addWidget(self.sub_type_filter)
        search_row2.addStretch()
        
        # Third row - Sort functionality
        search_row3 = QHBoxLayout()
        search_row3.addStretch()
        search_row3.addWidget(sort_field_label)
        search_row3.addWidget(self.sort_field_dropdown)
        search_row3.addSpacing(20)
        search_row3.addWidget(sort_order_label)
        search_row3.addWidget(self.sort_order_dropdown)
        search_row3.addStretch()
        
        # Add all three rows to the main search layout
        
        search_layout.addLayout(search_row3)
        search_layout.addLayout(search_row2)
        search_layout.addLayout(search_row1)
        
        # Create table widget for profiles
        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(9)
        
        # Set size policy to allow table to expand with window
        from PyQt6.QtWidgets import QSizePolicy
        self.profiles_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.profiles_table.setHorizontalHeaderLabels(["#", "Name", "Profile", "Channel type", "Sub type", "Email", "Amount", "Notes", "Profile ID"])
        
        # Enable header clicking for sorting
        self.profiles_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Set custom delegate for styling deleted profiles
        self.table_delegate = DeletedProfileDelegate(self.profiles_table)
        self.profiles_table.setItemDelegate(self.table_delegate)
        
        # Set table properties
        self.profiles_table.setAlternatingRowColors(False)
        self.profiles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.profiles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Hide the row selection indicator column (first column)
        self.profiles_table.verticalHeader().setVisible(False)
        
        # Make header row fixed (non-scrollable)
        self.profiles_table.horizontalHeader().setStretchLastSection(True)
        self.profiles_table.horizontalHeader().setFixedHeight(35)  # Match the header height we set earlier
        
        # Set scroll mode to ensure header stays fixed
        self.profiles_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        # Set scroll bar policies
        self.profiles_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.profiles_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set header properties
        header = self.profiles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Profile
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Channel Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Sub Type
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Notes
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Profile ID
        
        # Set table style
        self.profiles_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 0px;
                gridline-color: #f0f0f0;
                outline: none;
                selection-background-color: rgba(100, 181, 246, 0.15);
                selection-color: #333333;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f5f5f5;
                color: #333333;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: rgba(100, 181, 246, 0.15);
                color: #333333;
                border-bottom: 1px solid rgba(100, 181, 246, 0.15);
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 4px 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                border-right: 1px solid #e9ecef;
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                position: sticky;
                top: 0;
            }
            QHeaderView::section:first {
                border-top-left-radius: 0px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 0px;
                border-right: 1px solid #e9ecef;
            }
            QTableCornerButton::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #dee2e6;
                border-right: 1px solid #e9ecef;
            }
            QTableWidget::item[column="0"] {
                background-color: #f8f9fa;
                color: #6c757d;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item[column="0"]:selected {
                background-color: rgba(100, 181, 246, 0.15);
                color: #333333;
            }
        """)
        
        # Connect double-click event to launch profile
        self.profiles_table.cellDoubleClicked.connect(self.on_table_double_clicked)
        
        # Populate table with profile data
        self.populate_profiles_table()
        
        # Ensure the table scrolls properly from the first data row
        if self.profiles_table.rowCount() > 0:
            # Set the table to show the first data row at the top
            self.profiles_table.scrollToItem(self.profiles_table.item(0, 0))
            
                        # Set the vertical scroll bar to start from the first data row
            header_height = self.profiles_table.horizontalHeader().height()
            self.profiles_table.verticalScrollBar().setRange(0, self.profiles_table.rowCount() * 50)  # Approximate row height
            
            # Force the table to update its scroll area
            self.profiles_table.updateGeometry()
        
        # Add buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(80, 30)
        refresh_btn.clicked.connect(self.refresh_profiles)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #47a4ff;
            }
        """)
        
        # Add collect Chrome profiles button
        chrome_btn = QPushButton("Collect")
        chrome_btn.setFixedSize(80, 30)
        chrome_btn.clicked.connect(self.collect_chrome_profiles)
        chrome_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #47a4ff;
            }
        """)
        
        # Add launch button
        launch_btn = QPushButton("Launch")
        launch_btn.setFixedSize(100, 30)
        launch_btn.clicked.connect(self.launch_selected_profile)
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        
        # Add edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(80, 30)
        edit_btn.clicked.connect(self.edit_selected_profile)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #47a4ff;
            }
        """)
        
        # Add cleanup button
        cleanup_btn = QPushButton("Clean")
        cleanup_btn.setFixedSize(80, 30)
        cleanup_btn.clicked.connect(self.cleanup_deleted_profiles)
        cleanup_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 2px solid #ff6b6b;
            }
        """)
        
        buttons_layout.addWidget(chrome_btn)
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(cleanup_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(launch_btn)
  
        # Add search layout and table to main layout
        layout.addLayout(search_layout)
        layout.addSpacing(8)  # Add space between search and table
        layout.addWidget(self.profiles_table)
        layout.addSpacing(1)
        layout.addLayout(buttons_layout)
        layout.addSpacing(4)  # Add space between table and buttons

    def populate_profiles_table(self, skip_validation=False):
        """Populate the profiles table with data from profile.json"""
        self.profiles_table.setRowCount(len(self.profiles))
        
        # Initialize the mapping for unsorted state
        self.table_row_to_profile_index = {i: i for i in range(len(self.profiles))}
        
        deleted_rows = set()
        
        for row, profile in enumerate(self.profiles):
            # Check if profile exists (skip validation for faster refresh)
            profile_exists = True if skip_validation else self.validate_profile_exists(profile.get('profile_id', ''))
            
            # Number
            number_item = QTableWidgetItem(str(row + 1))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_table.setItem(row, 0, number_item)
            
            # Name
            name_item = QTableWidgetItem(profile.get('name', ''))
            self.profiles_table.setItem(row, 1, name_item)
            
            # Profile
            profile_name = profile.get('profile', '')
            profile_item = QTableWidgetItem(profile_name)
            self.profiles_table.setItem(row, 2, profile_item)
            
            # Channel Types
            channel_types = profile.get('channel_types', [])
            if isinstance(channel_types, str):
                # Handle legacy single channel_type
                channel_types = [channel_types] if channel_types else []
            
            channel_types_text = ', '.join(channel_types) if channel_types else ''
            channel_type_item = QTableWidgetItem(channel_types_text)
            channel_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_table.setItem(row, 3, channel_type_item)
            
            # Sub Type
            sub_types = profile.get('sub_types', [])
            if isinstance(sub_types, str):
                # Handle legacy single sub_type
                sub_types = [sub_types] if sub_types else []
            
            sub_types_text = ', '.join(sub_types) if sub_types else ''
            sub_type_item = QTableWidgetItem(sub_types_text)
            sub_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_table.setItem(row, 4, sub_type_item)
            
            # Email
            email = profile.get('email', '')
            email_item = QTableWidgetItem(email)
            self.profiles_table.setItem(row, 5, email_item)
            
            # Total Channel
            total_channel = profile.get('total_channel', '')
            total_channel_item = QTableWidgetItem(total_channel)
            total_channel_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_table.setItem(row, 6, total_channel_item)
            
            # Notes
            notes = profile.get('notes', '')
            notes_item = QTableWidgetItem(notes)
            self.profiles_table.setItem(row, 7, notes_item)
            
            # Profile ID
            profile_id = profile.get('profile_id', '')
            profile_id_item = QTableWidgetItem(profile_id)
            profile_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_table.setItem(row, 8, profile_id_item)
            
            # Track deleted profiles for custom delegate
            if not profile_exists:
                deleted_rows.add(row)
        
        # Update the custom delegate with deleted rows
        if hasattr(self, 'table_delegate'):
            self.table_delegate.set_deleted_rows(deleted_rows)
        
        # Force the table to update its styling
        self.profiles_table.viewport().update()
        
        # Update filter options
        self.update_channel_type_filter_options()
        self.update_sub_type_filter_options()
        
        # Select the first row if there are profiles
        if self.profiles_table.rowCount() > 0:
            self.profiles_table.setCurrentCell(0, 0)

    def update_channel_type_filter_options(self):
        """Update the channel type filter dropdown with options from config.json"""
        # Get channel types from config.json
        channel_types = self.config.get('channel_types', [])
        
        # Update the dropdown
        current_selection = self.channel_type_filter.currentText()
        self.channel_type_filter.clear()
        self.channel_type_filter.addItem("All types")
        self.channel_type_filter.addItems(channel_types)
        
        # Restore previous selection if it still exists
        if current_selection in [self.channel_type_filter.itemText(i) for i in range(self.channel_type_filter.count())]:
            self.channel_type_filter.setCurrentText(current_selection)
        else:
            self.channel_type_filter.setCurrentText("All types")

    def update_sub_type_filter_options(self):
        """Update the sub type filter dropdown with options from config.json"""
        # Get sub types from config.json
        sub_types = self.config.get('sub_types', [])
        
        # Update the dropdown
        current_selection = self.sub_type_filter.currentText()
        self.sub_type_filter.clear()
        self.sub_type_filter.addItem("All Sub types")
        self.sub_type_filter.addItems(sub_types)
        
        # Restore previous selection if it still exists
        if current_selection in [self.sub_type_filter.itemText(i) for i in range(self.sub_type_filter.count())]:
            self.sub_type_filter.setCurrentText(current_selection)
        else:
            self.sub_type_filter.setCurrentText("All Sub types")

    def filter_profiles_table(self):
        """Filter the profiles table based on search text, scope, channel type, and sub type"""
        search_text = self.search_input.text().lower().strip()
        search_scope = self.search_scope.currentText()
        channel_type_filter = self.channel_type_filter.currentText()
        sub_type_filter = self.sub_type_filter.currentText()
        
        # If all filters are empty, show all profiles
        if (not search_text and 
            channel_type_filter == "All Channel Types" and 
            sub_type_filter == "All Sub types"):
            for row in range(self.profiles_table.rowCount()):
                self.profiles_table.setRowHidden(row, False)
            return
        
        # Filter profiles based on search text, scope, channel type, and sub type
        for row in range(self.profiles_table.rowCount()):
            # Get text from searchable columns
            name = self.profiles_table.item(row, 1).text().lower() if self.profiles_table.item(row, 1) else ""
            profile = self.profiles_table.item(row, 2).text().lower() if self.profiles_table.item(row, 2) else ""
            email = self.profiles_table.item(row, 5).text().lower() if self.profiles_table.item(row, 5) else ""
            total_channel = self.profiles_table.item(row, 6).text().lower() if self.profiles_table.item(row, 6) else ""
            notes = self.profiles_table.item(row, 7).text().lower() if self.profiles_table.item(row, 7) else ""
            profile_id = self.profiles_table.item(row, 8).text().lower() if self.profiles_table.item(row, 8) else ""
            channel_types = self.profiles_table.item(row, 3).text().lower() if self.profiles_table.item(row, 3) else ""
            sub_types = self.profiles_table.item(row, 4).text().lower() if self.profiles_table.item(row, 4) else ""
            
            # Check channel type filter
            channel_matches = True
            if channel_type_filter != "All types":
                channel_matches = channel_type_filter.lower() in channel_types
            
            # Check sub type filter
            sub_type_matches = True
            if sub_type_filter != "All Sub types":
                sub_type_matches = sub_type_filter.lower() in sub_types
            
            # Check if search text matches based on selected scope
            search_matches = False
            if not search_text:
                search_matches = True
            elif search_scope == "All Fields":
                search_matches = (search_text in name or 
                                search_text in profile or 
                                search_text in email or 
                                search_text in notes or
                                search_text in total_channel or
                                search_text in profile_id)
            elif search_scope == "Name":
                search_matches = search_text in name
            elif search_scope == "Profile":
                search_matches = search_text in profile
            elif search_scope == "Email":
                search_matches = search_text in email
            elif search_scope == "Notes":
                search_matches = search_text in notes
            elif search_scope == "Amount":
                search_matches = search_text in total_channel
            elif search_scope == "Profile ID":
                search_matches = search_text in profile_id
            
            # Show/hide row based on all filters
            self.profiles_table.setRowHidden(row, not (channel_matches and sub_type_matches and search_matches))

    def sort_profiles_table(self):
        """Sort the profiles table based on selected field and order"""
        sort_field = self.sort_field_dropdown.currentText()
        sort_order = self.sort_order_dropdown.currentText()
        
        # Get the column index based on the selected field
        column_index = None
        if sort_field == "Name":
            column_index = 1
        elif sort_field == "Profile":
            column_index = 2
        elif sort_field == "Channel type":
            column_index = 3
        elif sort_field == "Sub type":
            column_index = 4
        elif sort_field == "Email":
            column_index = 5
        elif sort_field == "Amount":
            column_index = 6
        elif sort_field == "Notes":
            column_index = 7
        elif sort_field == "Profile ID":
            column_index = 8
        
        if column_index is not None:
            # Determine sort order (A-Z = ascending, Z-A = descending)
            reverse_order = (sort_order == "Z-A")
            
            # Special handling for Profile ID column to use natural sorting
            if sort_field == "Profile ID":
                self.custom_sort_profile_id_column(reverse_order)
            else:
                # Custom sorting to handle empty values last for all columns
                self.custom_sort_column(column_index, reverse_order)

    def custom_sort_profile_id_column(self, reverse_order=False):
        """Custom sort for Profile ID column using natural sorting"""
        # Get all rows data
        rows_data = []
        for row in range(self.profiles_table.rowCount()):
            row_data = []
            for col in range(self.profiles_table.columnCount()):
                item = self.profiles_table.item(row, col)
                row_data.append(item.text() if item else "")
            rows_data.append(row_data)
        
        # Sort using natural sorting key for Profile ID column (column 8)
        # Empty values will be sorted last
        def sort_key_with_empty_last(row):
            profile_id = row[8].strip()
            if not profile_id:
                return (1, "")  # Empty values get highest sort key
            return (0, natural_sort_key(profile_id))  # Non-empty values get normal sort key
        
        rows_data.sort(key=sort_key_with_empty_last, reverse=reverse_order)
        
        # Clear the table and repopulate with sorted data
        self._repopulate_table_with_sorted_data(rows_data)

    def custom_sort_column(self, column_index, reverse_order=False):
        """Custom sort for any column with empty values last"""
        # Get all rows data
        rows_data = []
        for row in range(self.profiles_table.rowCount()):
            row_data = []
            for col in range(self.profiles_table.columnCount()):
                item = self.profiles_table.item(row, col)
                row_data.append(item.text() if item else "")
            rows_data.append(row_data)
        
        # Sort with empty values last
        def sort_key_with_empty_last(row):
            cell_value = row[column_index].strip()
            if not cell_value:
                return (1, "")  # Empty values get highest sort key
            return (0, cell_value.lower())  # Non-empty values get normal sort key
        
        rows_data.sort(key=sort_key_with_empty_last, reverse=reverse_order)
        
        # Clear the table and repopulate with sorted data
        self._repopulate_table_with_sorted_data(rows_data)

    def _repopulate_table_with_sorted_data(self, rows_data):
        """Helper function to repopulate table with sorted data"""
        self.profiles_table.setRowCount(0)
        self.profiles_table.setRowCount(len(rows_data))
        
        # Store the mapping of table rows to profile indices
        self.table_row_to_profile_index = {}
        
        for row, row_data in enumerate(rows_data):
            # Find the original profile index by matching profile_id
            profile_id = row_data[8]  # Profile ID column
            original_index = None
            for i, profile in enumerate(self.profiles):
                if profile.get('profile_id', '') == profile_id:
                    original_index = i
                    break
            
            if original_index is not None:
                self.table_row_to_profile_index[row] = original_index
            
            for col, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                # Apply center alignment for specific columns
                if col in [0, 3, 4, 7, 8]:  # Number, Channel Types, Sub Type, Amount, Profile ID columns
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.profiles_table.setItem(row, col, item)

    def on_header_clicked(self, logical_index):
        """Handle header clicks for sorting"""
        # Map column index to sort field names
        column_to_field = {
            0: "Name",      # Number column sorts by Name
            1: "Name", 
            2: "Profile",
            3: "Channel type",
            4: "Sub type",
            5: "Email",
            6: "Notes",
            7: "Amount",
            8: "Profile ID"
        }
        
        # Get current sort order from dropdown
        current_order = self.sort_order_dropdown.currentText()
        
        # Toggle sort order if clicking the same column
        if hasattr(self, '_last_sort_column') and self._last_sort_column == logical_index:
            # Toggle order
            new_order = "Z-A" if current_order == "A-Z" else "A-Z"
            self.sort_order_dropdown.setCurrentText(new_order)
        else:
            # Default to ascending for new column
            self.sort_order_dropdown.setCurrentText("A-Z")
        
        # Update sort field dropdown
        if logical_index in column_to_field:
            field_name = column_to_field[logical_index]
            self.sort_field_dropdown.setCurrentText(field_name)
        
        # Store the clicked column
        self._last_sort_column = logical_index
        
        # Trigger sorting
        self.sort_profiles_table()

    def refresh_profiles(self):
        """Refresh the profiles table with updated data from profile.json"""
        self.profiles = self.load_profiles()
        self.populate_profiles_table(skip_validation=True)
        
        # Create custom dialog with auto-close for refresh success
        dialog = CustomMessageBox(self, "Refresh Complete", "Loading from Updated JSON file ", "success")
        
        # Set up auto-close timer
        timer = QTimer(dialog)
        timer.timeout.connect(dialog.accept)
        timer.start(1200)  # Auto-close after 1 second
        
        dialog.exec()

    def collect_chrome_profiles(self):
        """Collect Chrome profiles and add them to the existing profiles"""
        chrome_profiles = self.get_chrome_profiles()
        
        if not chrome_profiles:
            CustomMessageBox.show_info(self, "No Chrome Profiles", 
                                     "No Chrome profiles found. Make sure Chrome is installed and has been used at least once.")
            return
        
        # Check for duplicates (check only profile_id)
        existing_profile_ids = {profile.get('profile_id', '') for profile in self.profiles}
        new_profiles = []
        
        for chrome_profile in chrome_profiles:
            profile_id = chrome_profile.get('profile_id', '')
            if profile_id not in existing_profile_ids:
                new_profiles.append(chrome_profile)
        
        if not new_profiles:
            CustomMessageBox.show_info(self, "No New Profiles", 
                                     "All profiles already added.")
            return
        
        # Add new profiles to existing list
        self.profiles.extend(new_profiles)
        
        # Sort profiles alphabetically by profile name before saving
        self.profiles.sort(key=lambda profile: profile.get('profile', '').lower())
        
        # Save to file
        if self.save_profiles(self.profiles):
            self.populate_profiles_table(skip_validation=True)
            # Show different messages based on number of profiles
            if len(new_profiles) > 5:
                CustomMessageBox.show_success(self, "Success", 
                                            f"Added {len(new_profiles)} Chrome profile(s) to the list.")
            else:
                profile_names = [profile['profile'] for profile in new_profiles]
                CustomMessageBox.show_success(self, "Success", 
                                            f"Added profiles: {', '.join(profile_names)}")
        else:
            CustomMessageBox.show_error(self, "Error", 
                                      "Failed to save profiles to file.")

    def load_window_position(self):
        """Load the last saved window position and size"""
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default position if no saved position exists
            app_settings = self.config.get('app_settings', {})
            window_size = app_settings.get('window_size', WINDOW_SIZE)
            self.resize(window_size[0], window_size[1])
            self.center_window()
    
    def save_window_position(self):
        """Save the current window position and size"""
        self.settings.setValue('geometry', self.saveGeometry())
    
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def closeEvent(self, event):
        """Override close event to save window position"""
        self.save_window_position()
        event.accept()
    
    def resizeEvent(self, event):
        """Override resize event to adjust table height"""
        super().resizeEvent(event)
        # The table will automatically resize due to size policy
        # You can add custom logic here if needed

    def launch_selected_profile(self):
        """Launch the selected Chrome profile"""
        current_row = self.profiles_table.currentRow()
        
        if current_row < 0:
            CustomMessageBox.show_warning(self, "No Selection", 
                                        "Please select a profile to launch.")
            return
        
        # Get the original profile index from the mapping
        if hasattr(self, 'table_row_to_profile_index') and current_row in self.table_row_to_profile_index:
            original_index = self.table_row_to_profile_index[current_row]
        else:
            # Fallback to current_row if no mapping exists (unsorted state)
            original_index = current_row
        
        if original_index >= len(self.profiles):
            CustomMessageBox.show_error(self, "Error", 
                                      "Invalid profile selection.")
            return
        
        selected_profile = self.profiles[original_index]
        profile_id = selected_profile.get('profile_id', '')
        profile_name = selected_profile.get('name', '') or selected_profile.get('profile', '')
        
        if not profile_id:
            CustomMessageBox.show_warning(self, "No Profile ID", 
                                        "Selected profile does not have a valid profile ID.")
            return
        
        # Validate profile exists before launching
        if not self.validate_profile_exists(profile_id):
            CustomMessageBox.show_error(self, "Profile Not Found", 
                                      f"Profile '{profile_name}' no longer exists.\n"
                                      "It may have been deleted from Chrome.\n\n"
                                      "Use the 'Cleanup' button to remove deleted profiles.")
            return
        
        try:
            # Launch Chrome with the selected profile
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if not os.path.exists(chrome_path):
                    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            elif system == "Darwin":  # macOS
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            else:  # Linux
                chrome_path = "google-chrome"
            
            if not os.path.exists(chrome_path) and system != "Linux":
                CustomMessageBox.show_error(self, "Chrome Not Found", 
                                          "Google Chrome is not installed or not found in the default location.")
                return
            
            # Launch Chrome with the profile
            cmd = [chrome_path, f"--profile-directory={profile_id}"]
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # No success dialog needed - profile launches silently
            
        except Exception as e:
            CustomMessageBox.show_error(self, "Launch Error", 
                                      f"Failed to launch Chrome profile: {str(e)}")

    def on_table_double_clicked(self, row, column):
        """Handle double-click events on the profiles table to launch the selected profile"""
        # Set the current row to the clicked row
        self.profiles_table.setCurrentCell(row, 0)
        # Launch the profile
        self.launch_selected_profile()

    def edit_selected_profile(self):
        """Edit the selected profile"""
        current_row = self.profiles_table.currentRow()
        
        if current_row < 0:
            CustomMessageBox.show_warning(self, "No Selection", 
                                        "Please select a profile to edit.")
            return
        
        # Get the original profile index from the mapping
        if hasattr(self, 'table_row_to_profile_index') and current_row in self.table_row_to_profile_index:
            original_index = self.table_row_to_profile_index[current_row]
        else:
            # Fallback to current_row if no mapping exists (unsorted state)
            original_index = current_row
        
        if original_index >= len(self.profiles):
            CustomMessageBox.show_error(self, "Error", 
                                      "Invalid profile selection.")
            return
        
        selected_profile = self.profiles[original_index]
        
        # Show edit dialog
        dialog = EditProfileDialog(self, selected_profile)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get edited data
            edited_data = dialog.get_profile_data()
            
            # Store the profile ID to find it after resorting
            profile_id_to_find = selected_profile.get('profile_id', '')
            
            # Update the profile
            self.profiles[original_index].update(edited_data)
            
            # Sort profiles alphabetically by profile name after editing
            self.profiles.sort(key=lambda profile: profile.get('profile', '').lower())
            
            # Save to file
            if self.save_profiles(self.profiles):
                self.populate_profiles_table(skip_validation=True)
                
                # Find and select the edited profile after resorting
                if profile_id_to_find:
                    for row in range(self.profiles_table.rowCount()):
                        profile_id_item = self.profiles_table.item(row, 8)  # Profile ID column
                        if profile_id_item and profile_id_item.text() == profile_id_to_find:
                            self.profiles_table.setCurrentCell(row, 0)
                            break
                
                # No success dialog needed - profile updates silently
            else:
                CustomMessageBox.show_error(self, "Error", 
                                          "Failed to save profile changes.")

    def create_bottom_action_area(self, layout):
        """Create the bottom action area with buttons"""
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(14, 10, 14, 10)
        action_layout.setSpacing(10)
        
        # Add spacing to push buttons to the left
        action_layout.addStretch()
        
        layout.addLayout(action_layout)

def main():
    """Main function to run the sample application"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = SamplechromeUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
