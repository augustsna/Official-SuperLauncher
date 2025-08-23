import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QSize, QFileInfo, QMimeData
from PySide6.QtGui import QIcon, QPixmap, QKeySequence, QShortcut, QDrag
from PySide6.QtWidgets import (
    QApplication, QFileIconProvider, QGridLayout, QHBoxLayout, QInputDialog,
    QLabel, QLineEdit, QMenu, QMessageBox,
    QPushButton, QToolButton, QVBoxLayout, QWidget,
    QFileDialog, QStyle, QSplitter, QScrollArea
)

from template_app.ui.main_window_base import MainWindowBase
from template_app.config import load_app_settings, project_root
from template_app.styles import apply_app_style

# Icon extraction imports - with fallbacks
try:
    import win32gui
    import win32con
    import win32api
    import win32ui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from PIL import Image
    import tempfile
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


APP_NAME = "SuperLauncher"


class IconExtractor:
    """Extract icons from Windows executables and files using multiple fallback methods."""
    
    @staticmethod
    def extract_icon(file_path: str, size: int = 32) -> QIcon:
        """
        Extract icon from file using best available method.
        Falls back gracefully if advanced methods aren't available.
        """
        file_path = str(Path(file_path).resolve())
        
        # Method 1: Try win32 API (most accurate, like SuperLauncher)
        if HAS_WIN32:
            icon = IconExtractor._extract_with_win32(file_path, size)
            if icon and not icon.isNull():
                return icon
        
        # Method 2: Try system icon association
        icon = IconExtractor._extract_system_icon(file_path)
        if icon and not icon.isNull():
            return icon
        
        # Method 3: Default icon based on file extension
        return IconExtractor._get_default_icon(file_path)
    
    @staticmethod
    def _extract_with_win32(file_path: str, size: int = 32) -> Optional[QIcon]:
        """Extract icon using win32 API (equivalent to C# Icon.ExtractAssociatedIcon)."""
        try:
            # Use SHGetFileInfo to get the icon (simpler and more reliable)
            import struct
            
            # Define constants
            SHGFI_ICON = 0x000000100
            SHGFI_LARGEICON = 0x000000000
            SHGFI_SMALLICON = 0x000000001
            
            # Choose icon size
            flags = SHGFI_ICON | (SHGFI_SMALLICON if size <= 24 else SHGFI_LARGEICON)
            
            # Get file info structure
            ret, info = win32gui.SHGetFileInfo(file_path, 0, flags)
            
            if ret and info[0]:  # info[0] is the icon handle
                # Convert icon handle to QIcon using QPixmap.fromWinHICON if available
                try:
                    pixmap = QPixmap.fromWinHICON(info[0])
                    icon = QIcon(pixmap)
                    win32gui.DestroyIcon(info[0])  # Clean up the icon handle
                    return icon
                except AttributeError:
                    # Fallback: QPixmap.fromWinHICON might not be available
                    win32gui.DestroyIcon(info[0])
                    
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _extract_system_icon(file_path: str) -> QIcon:
        """Use Qt's built-in system icon extraction."""
        try:
            # Try to use system file icon
            file_info = QFileInfo(file_path)
            provider = QFileIconProvider()
            return provider.icon(file_info)
        except Exception:
            return QIcon()
    
    @staticmethod
    def _get_default_icon(file_path: str) -> QIcon:
        """Get default icon based on file extension or type."""
        try:
            app = QApplication.instance()
            if not app:
                return QIcon()
            
            # Check if it's a directory first
            if os.path.isdir(file_path):
                return app.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            
            ext = Path(file_path).suffix.lower()
            
            # Executable files
            if ext in ['.exe', '.msi', '.bat', '.cmd', '.com']:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            
            # Script files
            elif ext in ['.py', '.pyw', '.js', '.vbs', '.ps1']:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            
            # Documents
            elif ext in ['.txt', '.doc', '.docx', '.pdf', '.rtf']:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
            
            # Media files
            elif ext in ['.mp3', '.mp4', '.avi', '.mov', '.wav']:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
            
            # Folders/shortcuts
            elif ext in ['.lnk']:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_FileLinkIcon)
            
            # Default file icon
            else:
                return app.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
                
        except Exception:
            return QIcon()


@dataclass
class AppItem:
    path: str
    title: Optional[str] = None

    def display_name(self) -> str:
        if self.title and self.title.strip():
            return self.title
        
        # Check if it's a directory
        if os.path.isdir(self.path):
            return Path(self.path).name  # Use name() for folders to keep the full folder name
        
        return Path(self.path).stem


class ConfigStore:
    def __init__(self) -> None:
        config_root = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        self.dir = config_root / APP_NAME
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "config.json"
        if not self.path.exists():
            self._write({"apps": []})

    def _read(self) -> dict:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"apps": []}

    def _write(self, data: dict) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_apps(self) -> List[AppItem]:
        data = self._read()
        apps = []
        for item in data.get("apps", []):
            path = item.get("path")
            title = item.get("title")
            if path:
                apps.append(AppItem(path=path, title=title))
        return apps

    def save_apps(self, apps: List[AppItem]) -> None:
        data = {"apps": [{"path": a.path, "title": a.title} for a in apps]}
        self._write(data)


class AppGrid(QWidget):
    """Grid-based app display similar to Windows Start Menu."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apps: List[AppItem] = []
        self.app_widgets: List[QWidget] = []
        self.columns = 5  # Default number of columns
        
        # Create scroll area for the grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget for the grid
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #f5f7fa;")
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        # Ensure items start from top-left corner
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Set the content widget in the scroll area
        self.scroll_area.setWidget(self.content_widget)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        # Ensure the scroll area content starts from top-left
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Connect double-click and context menu
        self.content_widget.mousePressEvent = self._handle_mouse_press
        self.content_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_widget.customContextMenuRequested.connect(self._handle_context_menu)
        
        self._last_clicked_app = None

    def set_columns(self, columns: int) -> None:
        """Set the number of columns in the grid."""
        self.columns = columns
        if self.apps:
            self.populate(self.apps)

    def populate(self, apps: List[AppItem]) -> None:
        """Populate the grid with applications."""
        self.apps = apps
        self._clear_grid()
        self._build_grid()

    def _clear_grid(self) -> None:
        """Clear all app widgets from the grid."""
        for widget in self.app_widgets:
            widget.deleteLater()
        self.app_widgets.clear()
        
        # Clear the grid layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _build_grid(self) -> None:
        """Build the grid layout with app widgets."""
        for i, app in enumerate(self.apps):
            row = i // self.columns
            col = i % self.columns
            
            app_widget = self._create_app_widget(app)
            self.grid_layout.addWidget(app_widget, row, col)
            self.app_widgets.append(app_widget)

    def _create_app_widget(self, app: AppItem) -> QWidget:
        """Create a widget for a single app item."""
        widget = QWidget()
        widget.setFixedSize(100, 100)  # Square size for consistent grid
        widget.setCursor(Qt.PointingHandCursor)
        # Enable drag and drop
        widget.setAcceptDrops(True)
        
        # Store app data
        widget.app_data = app
        
        # Layout for icon and text
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Icon
        icon_label = QLabel()
        icon = IconExtractor.extract_icon(app.path, 48)  # Larger icon for grid
        icon_label.setPixmap(icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        
        # Text label
        text_label = QLabel(app.display_name())
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                background: transparent;
                border: none;
                font-size: 11px;
                font-weight: normal;
                padding: 2px;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        # Connect mouse events
        widget.mousePressEvent = lambda event, w=widget: self._on_app_mouse_press(event, w)
        widget.mouseMoveEvent = lambda event, w=widget: self._on_app_mouse_move(event, w)
        widget.mouseDoubleClickEvent = lambda event, w=widget: self._on_app_double_clicked(event, w)
        widget.enterEvent = lambda event, w=widget: self._on_app_hover_enter(event, w)
        widget.leaveEvent = lambda event, w=widget: self._on_app_hover_leave(event, w)
        # Add drag and drop event handlers
        widget.dragEnterEvent = lambda event, w=widget: self._on_app_drag_enter(event, w)
        widget.dragLeaveEvent = lambda event, w=widget: self._on_app_drag_leave(event, w)
        widget.dropEvent = lambda event, w=widget: self._on_app_drop(event, w)
        
        return widget

    def _on_app_clicked(self, event, widget):
        """Handle single click on app widget."""
        if event.button() == Qt.LeftButton:
            self._last_clicked_app = widget.app_data
            # Highlight the clicked widget
            self._clear_highlights()
            widget._is_clicked = True
            widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(45, 55, 72, 0.1);
                    border-radius: 8px;
                }
            """)

    def _on_app_double_clicked(self, event, widget):
        """Handle double click on app widget."""
        if event.button() == Qt.LeftButton:
            self._run_app(widget.app_data)

    def _on_app_hover_enter(self, event, widget):
        """Handle mouse enter on app widget."""
        if not hasattr(widget, '_is_clicked') or not widget._is_clicked:
            widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(45, 55, 72, 0.05);
                    border-radius: 8px;
                    border: 1px solid rgba(45, 55, 72, 0.2);
                }
            """)

    def _on_app_hover_leave(self, event, widget):
        """Handle mouse leave on app widget."""
        if not hasattr(widget, '_is_clicked') or not widget._is_clicked:
            widget.setStyleSheet("")

    def _on_app_mouse_press(self, event, widget):
        """Handle mouse press on app widget - handles both click and drag start."""
        if event.button() == Qt.LeftButton:
            # Store the widget for potential drag operation
            self._drag_start_widget = widget
            self._drag_start_pos = event.position().toPoint()
            # Handle click
            self._on_app_clicked(event, widget)

    def _on_app_clicked(self, event, widget):
        """Handle single click on app widget."""
        self._last_clicked_app = widget.app_data
        # Highlight the clicked widget
        self._clear_highlights()
        widget._is_clicked = True
        widget.setStyleSheet("""
            QWidget {
                background-color: rgba(45, 55, 72, 0.1);
                border-radius: 8px;
            }
        """)

    def _on_app_mouse_move(self, event, widget):
        """Handle mouse move to start drag operation."""
        if (hasattr(self, '_drag_start_widget') and 
            self._drag_start_widget == widget and
            hasattr(self, '_drag_start_pos') and
            (event.position().toPoint() - self._drag_start_pos).manhattanLength() > 10):
            
            # Start drag operation
            self._start_drag(widget, event)

    def _start_drag(self, widget, event):
        """Start drag operation for the widget."""
        drag = QDrag(widget)
        mime_data = QMimeData()
        mime_data.setText(str(self.app_widgets.index(widget)))
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = widget.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())
        
        # Execute drag
        result = drag.exec(Qt.MoveAction)
        
        # Clean up
        if hasattr(self, '_drag_start_widget'):
            delattr(self, '_drag_start_widget')
        if hasattr(self, '_drag_start_pos'):
            delattr(self, '_drag_start_pos')

    def _on_app_drag_enter(self, event, widget):
        """Handle drag enter event."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Highlight drop target
            widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(45, 55, 72, 0.15);
                    border-radius: 8px;
                    border: 2px dashed rgba(45, 55, 72, 0.4);
                }
            """)

    def _on_app_drag_leave(self, event, widget):
        """Handle drag leave event."""
        # Clear the drop highlight
        if not hasattr(widget, '_is_clicked') or not widget._is_clicked:
            widget.setStyleSheet("")
        else:
            # Restore clicked state styling
            widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(45, 55, 72, 0.1);
                    border-radius: 8px;
                }
            """)

    def _on_app_drop(self, event, widget):
        """Handle drop event to rearrange items."""
        if event.mimeData().hasText():
            try:
                source_index = int(event.mimeData().text())
                target_index = self.app_widgets.index(widget)
                
                if source_index != target_index:
                    # Rearrange the apps list
                    app_item = self.apps.pop(source_index)
                    self.apps.insert(target_index, app_item)
                    
                    # Update the grid
                    self.populate(self.apps)
                    
                    # Save the new order
                    main_window = self._find_main_window()
                    if main_window and hasattr(main_window, 'config'):
                        main_window.config.save_apps(self.apps)
                    
                    # Clear the highlight
                    widget.setStyleSheet("")
                    
            except (ValueError, IndexError):
                pass
            
            event.acceptProposedAction()

    def _handle_mouse_press(self, event):
        """Handle mouse press on the scroll area."""
        if event.button() == Qt.LeftButton:
            # Clear highlights when clicking empty space
            self._clear_highlights()

    def _handle_context_menu(self, pos):
        """Handle context menu request."""
        # Find which app was right-clicked
        child = self.content_widget.childAt(pos)
        while child and not hasattr(child, 'app_data'):
            child = child.parent()
        
        if child and hasattr(child, 'app_data'):
            self._show_context_menu(child.app_data, self.content_widget.mapToGlobal(pos))

    def _show_context_menu(self, app: AppItem, global_pos):
        """Show context menu for an app."""
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d3748;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 0px;
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
        """)
        
        # Check if it's a folder to show appropriate actions
        is_folder = os.path.isdir(app.path)
        
        if is_folder:
            # Folder actions
            open_action = menu.addAction("Open Folder")
            open_loc_action = menu.addAction("Open parent folder")
        else:
            # File actions
            run_action = menu.addAction("Run")
            run_admin_action = menu.addAction("Run as administrator")
            open_loc_action = menu.addAction("Open location")
        
        rename_action = menu.addAction("Rename")
        remove_action = menu.addAction("Unpin")
        
        action = menu.exec(global_pos)
        
        if is_folder:
            if action == open_action:
                self._run_app(app)  # This will open the folder
            elif action == open_loc_action:
                self._open_location(app)
            elif action == rename_action:
                self._rename_app(app)
            elif action == remove_action:
                self._remove_app(app)
        else:
            if action == run_action:
                self._run_app(app)
            elif action == run_admin_action:
                self._run_app_admin(app)
            elif action == open_loc_action:
                self._open_location(app)
            elif action == rename_action:
                self._rename_app(app)
            elif action == remove_action:
                self._remove_app(app)

    def _clear_highlights(self):
        """Clear all widget highlights."""
        for widget in self.app_widgets:
            widget.setStyleSheet("")
            if hasattr(widget, '_is_clicked'):
                widget._is_clicked = False

    def _run_app(self, app: AppItem):
        """Run an application."""
        # Find the main window and call its method
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, 'run_path'):
            main_window.run_path(app.path)

    def _run_app_admin(self, app: AppItem):
        """Run an application as administrator."""
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, 'run_path_admin'):
            main_window.run_path_admin(app.path)

    def _open_location(self, app: AppItem):
        """Open the location of an application or folder."""
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, 'open_location'):
            main_window.open_location(app.path)

    def _rename_app(self, app: AppItem):
        """Rename an application."""
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, 'rename_app'):
            main_window.rename_app(app)

    def _remove_app(self, app: AppItem):
        """Remove an application."""
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, 'remove_app'):
            main_window.remove_app(app)

    def _find_main_window(self):
        """Find the main launcher window by traversing up the widget hierarchy."""
        widget = self
        while widget:
            if hasattr(widget, 'config') and hasattr(widget, 'apps'):
                # This is the main window
                return widget
            widget = widget.parent()
        return None

    def filter(self, text: str) -> None:
        """Filter the grid based on search text."""
        text_lower = text.lower()
        for widget in self.app_widgets:
            app = widget.app_data
            visible = text_lower in app.display_name().lower()
            widget.setVisible(visible)

    def current_app(self) -> Optional[AppItem]:
        """Get the currently selected app."""
        return self._last_clicked_app

    def app_at_pos(self, pos) -> Optional[AppItem]:
        """Get app at a specific position."""
        child = self.content_widget.childAt(pos)
        while child and not hasattr(child, 'app_data'):
            child = child.parent()
        return child.app_data if child else None


class LauncherWindow(MainWindowBase):
    """Enhanced launcher window that extends MainWindowBase with launcher functionality."""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigStore()
        self.apps: List[AppItem] = self.config.load_apps()
        
        # Override window title and size for launcher
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(620, 620)
        self.setMaximumSize(620, 620)
        self.resize(620, 620)
        
        # Clear default UI and build launcher interface
        self._clear_default_ui()
        self._build_launcher_ui()
        
        # Add launcher-specific shortcuts
        self._shortcut_add = QShortcut(QKeySequence("Ctrl+N"), self)
        self._shortcut_add.activated.connect(self.on_add)
        
        self._shortcut_run = QShortcut(QKeySequence("Ctrl+R"), self)
        self._shortcut_run.activated.connect(self.on_run_selected)
        
        self._shortcut_filter = QShortcut(QKeySequence("Ctrl+F"), self)
        self._shortcut_filter.activated.connect(self._focus_filter)

    def _clear_default_ui(self):
        """Clear the default UI elements from MainWindowBase."""
        # Clear header and body layouts
        while self.header_layout.count():
            child = self.header_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        while self.body_layout.count():
            child = self.body_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _build_launcher_ui(self):
        """Build the launcher-specific user interface."""
        # Header: Title and search
        # Create title container with icon and text
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Add rocket icon
        icon_label = QLabel()
        icon = QIcon("template_app/assets/icons/icon.png")
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(32, 32))
        else:
            # Fallback if icon not found
            icon = QIcon("_internal\template_app\assets\icons")
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title text
        title_label = QLabel(APP_NAME)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                font-weight: bold; 
                padding: 10px; 
                color: #333333;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Add icon and title to layout
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setFixedHeight(30)
        self.filter_edit.setFixedWidth(250)
        self.filter_edit.setPlaceholderText("Search...")
        self.filter_edit.textChanged.connect(self.on_filter)
        self.filter_edit.setStyleSheet("""
            QLineEdit {
                padding: 4px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                margin: 0 20px;
            }
        """)
        
        # Create a container widget for the header content
        header_content = QWidget()
        header_content_layout = QVBoxLayout(header_content)
        header_content_layout.setContentsMargins(0, 10, 0, 0)
        header_content_layout.setSpacing(10)
        
        # Add title and search box vertically
        header_content_layout.addWidget(title_container)
        #header_content_layout.addWidget(self.filter_edit, alignment=Qt.AlignCenter)
        
        # Add the header content to the main header layout
        self.header_layout.addWidget(header_content)
        
        # Increase header height to accommodate title and search box
        self.header_widget.setFixedHeight(100)
        

        # Body: App list and controls
        # Create splitter for better layout control
        splitter = QSplitter(Qt.Vertical)
        
        # App grid area
        self.app_grid = AppGrid()
        self.app_grid.populate(self.apps)
        # Don't connect context menu here - AppGrid handles it internally
        
        # Style the scroll area to match the light theme
        self.app_grid.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #f5f7fa;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #e1e5e9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #b8c0c8;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9aa3ad;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Control buttons area
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 10, 0)
        
        self.btn_add = QPushButton("Add")
        self.btn_add.setFixedWidth(80)
        self.btn_add.setFixedHeight(35)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                padding: 4px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
                border-color: #6c757d;
            }
        """)
        
        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(self.on_run_selected)
        self.btn_run.setFixedWidth(80)
        self.btn_run.setFixedHeight(35)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                padding: 4px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
                border-color: #6c757d;
            }
        """)
        
        self.btn_more = QPushButton("More Options")
        self.btn_more.clicked.connect(self.on_more_menu)
        self.btn_more.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_add)
        controls_layout.addSpacing(5)
        controls_layout.addWidget(self.btn_run)
        #controls_layout.addWidget(self.btn_more)
        
        # Add to splitter
        splitter.addWidget(self.app_grid)
        splitter.addWidget(controls_widget)
        splitter.setSizes([400, 50])  # Give more space to app grid
        
        # Add splitter to body layout
        self.body_layout.addWidget(splitter)

    def _focus_filter(self):
        """Focus the filter input field."""
        self.filter_edit.setFocus()
        self.filter_edit.selectAll()

    def on_filter(self, text: str) -> None:
        """Filter the app grid based on search text."""
        self.app_grid.filter(text)

    def on_add(self) -> None:
        """Add new apps to the launcher."""
        # Show menu to choose between files and folders
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
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
        """)
        
        add_files_action = menu.addAction("Add Files...")
        add_folder_action = menu.addAction("Add Folder...")
        
        # Position menu near the add button
        button_pos = self.btn_add.mapToGlobal(self.btn_add.rect().bottomLeft())
        action = menu.exec(button_pos)
        
        if action == add_files_action:
            self.on_add_files()
        elif action == add_folder_action:
            self.on_add_folder()

    def on_add_files(self) -> None:
        """Add new files to the launcher."""
        start_dir = os.path.expandvars(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs")
        if not os.path.exists(start_dir):
            start_dir = os.path.expanduser("~")
            
        paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select files to pin", 
            start_dir,
            "All Files (*.*)"
        )
        
        if not paths:
            return
            
        for path in paths:
            if path not in [app.path for app in self.apps]:
                self.apps.append(AppItem(path=path))
        
        self.config.save_apps(self.apps)
        self.app_grid.populate(self.apps)

    def on_add_folder(self) -> None:
        """Add a folder to the launcher."""
        start_dir = os.path.expandvars(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs")
        if not os.path.exists(start_dir):
            start_dir = os.path.expanduser("~")
            
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select folder to pin",
            start_dir
        )
        
        if not folder_path:
            return
            
        # Debug logging
        print(f"Selected folder: {folder_path}")
        print(f"Folder exists: {os.path.exists(folder_path)}")
        print(f"Is directory: {os.path.isdir(folder_path)}")
        print(f"Absolute path: {os.path.abspath(folder_path)}")
            
        # Check if folder is already added
        if folder_path not in [app.path for app in self.apps]:
            self.apps.append(AppItem(path=folder_path))
            self.config.save_apps(self.apps)
            self.app_grid.populate(self.apps)
            print(f"Folder added successfully: {folder_path}")
        else:
            print(f"Folder already exists in launcher: {folder_path}")

    def on_run_selected(self) -> None:
        """Run the currently selected app."""
        app = self.app_grid.current_app()
        if not app:
            return
        self.run_path(app.path)

    def on_more_menu(self) -> None:
        """Show the more options menu."""
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
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
        """)
        
        add_files_action = menu.addAction("Add Files...")
        add_folder_action = menu.addAction("Add Folder...")
        quit_action = menu.addAction("Exit")
        
        # Position menu near the button
        button_pos = self.btn_more.mapToGlobal(self.btn_more.rect().bottomLeft())
        action = menu.exec(button_pos)
        
        if action == add_files_action:
            self.on_add_files()
        elif action == add_folder_action:
            self.on_add_folder()
        elif action == quit_action:
            QApplication.quit()

    def open_context_menu(self, pos) -> None:
        """Open context menu for right-click on app items."""
        app = self.app_grid.app_at_pos(pos)
        if not app:
            return
            
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
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
        """)
        
        # Check if it's a folder to show appropriate actions
        is_folder = os.path.isdir(app.path)
        
        if is_folder:
            # Folder actions
            open_action = menu.addAction("Open Folder")
            open_loc_action = menu.addAction("Open parent folder")
        else:
            # File actions
            run_action = menu.addAction("Run")
            run_admin_action = menu.addAction("Run as administrator")
            open_loc_action = menu.addAction("Open location")
        
        rename_action = menu.addAction("Rename")
        remove_action = menu.addAction("Unpin")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if is_folder:
            if action == open_action:
                self.run_path(app.path)  # This will open the folder
            elif action == open_loc_action:
                self.open_location(app.path)
            elif action == rename_action:
                self.rename_app(app)
            elif action == remove_action:
                self.remove_app(app)
        else:
            if action == run_action:
                self.run_path(app.path)
            elif action == run_admin_action:
                self.run_path_admin(app.path)
            elif action == open_loc_action:
                self.open_location(app.path)
            elif action == rename_action:
                self.rename_app(app)
            elif action == remove_action:
                self.remove_app(app)

    def rename_app(self, app: AppItem) -> None:
        """Rename an app item."""
        new_title, ok = QInputDialog.getText(
            self, 
            "Rename", 
            "Title:", 
            text=app.display_name()
        )
        if not ok:
            return
            
        app.title = new_title.strip() or None
        self.config.save_apps(self.apps)
        self.app_grid.populate(self.apps)

    def remove_app(self, app: AppItem) -> None:
        """Remove an app from the launcher."""
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to unpin '{app.display_name()}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.apps = [a for a in self.apps if a.path != app.path]
            self.config.save_apps(self.apps)
            self.app_grid.populate(self.apps)

    def open_location(self, path: str) -> None:
        """Open the folder containing the selected item."""
        try:
            if os.path.isdir(path):
                # For folders, open the parent directory
                dir_path = str(Path(path).parent)
            else:
                # For files, open the directory containing the file
                dir_path = str(Path(path).parent)
            
            # Only open if we have a valid parent directory (not root)
            if dir_path and dir_path != path:
                normalized_dir = os.path.normpath(dir_path)
                print(f"Opening parent directory: {normalized_dir}")
                subprocess.Popen(["explorer", normalized_dir])
            else:
                # If no parent directory (root drive), just open the item itself
                normalized_path = os.path.normpath(path)
                print(f"Opening item itself: {normalized_path}")
                subprocess.Popen(["explorer", normalized_path])
        except Exception as e:
            QMessageBox.warning(self, APP_NAME, f"Failed to open location:\n{e}")

    def run_path(self, path: str) -> None:
        """Run a file with proper working directory or open a folder."""
        try:
            # Debug logging
            print(f"run_path called with: {path}")
            print(f"Path exists: {os.path.exists(path)}")
            print(f"Is directory: {os.path.isdir(path)}")
            print(f"Absolute path: {os.path.abspath(path)}")
            
            # Check if the path is a directory
            if os.path.isdir(path):
                # Open folder in Explorer - normalize path to Windows format
                normalized_path = os.path.normpath(path)
                print(f"Normalized path: {normalized_path}")
                print(f"Opening folder in Explorer: {normalized_path}")
                print(f"Explorer command: explorer \"{normalized_path}\"")
                subprocess.Popen(["explorer", normalized_path])
            else:
                # Run file with proper working directory
                target_dir = str(Path(path).parent)
                path_ps = path.replace("'", "''")
                dir_ps = target_dir.replace("'", "''")
                ps_cmd = [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    f"Start-Process -FilePath '{path_ps}' -WorkingDirectory '{dir_ps}'"
                ]
                subprocess.Popen(ps_cmd)
        except Exception as e:
            print(f"Error in run_path: {e}")
            QMessageBox.warning(self, APP_NAME, f"Failed to run:\n{e}")

    def run_path_admin(self, path: str) -> None:
        """Run a file as administrator."""
        ps_path = path.replace("'", "''")
        target_dir = str(Path(path).parent)
        ps_dir = target_dir.replace("'", "''")
        ps_cmd = [
            "powershell",
            "-NoProfile",
            "-WindowStyle",
            "Hidden",
            "-Command",
            f"Start-Process -FilePath '{ps_path}' -WorkingDirectory '{ps_dir}' -Verb RunAs"
        ]
        try:
            subprocess.Popen(ps_cmd)
        except Exception as e:
            QMessageBox.warning(self, APP_NAME, f"Failed to run as admin:\n{e}")


class LauncherApp:
    """Main launcher application."""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.window = LauncherWindow()

    def run(self):
        """Run the application."""
        self.window.show()
        return self.app.exec()


def main():
    """Main entry point."""
    app = LauncherApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()


