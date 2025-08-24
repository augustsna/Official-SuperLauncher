import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QSize, QFileInfo, QMimeData, QTimer
from PySide6.QtGui import QIcon, QPixmap, QKeySequence, QShortcut, QDrag, QColor
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
    
    # Class-level cache for icons to improve performance
    _icon_cache = {}
    _cache_size_limit = 100  # Maximum number of cached icons
    
    @staticmethod
    def _get_cache_key(file_path: str, sizes: List[int] = None) -> str:
        """Generate a cache key for the icon request."""
        if sizes is None:
            sizes = [32]  # Default size
        return f"{file_path}:{','.join(map(str, sorted(sizes)))}"
    
    @staticmethod
    def _add_to_cache(file_path: str, sizes: List[int], icon: QIcon) -> None:
        """Add an icon to the cache."""
        cache_key = IconExtractor._get_cache_key(file_path, sizes)
        
        # Implement simple LRU cache
        if len(IconExtractor._icon_cache) >= IconExtractor._cache_size_limit:
            # Remove oldest entry (simple approach - remove first item)
            oldest_key = next(iter(IconExtractor._icon_cache))
            del IconExtractor._icon_cache[oldest_key]
        
        IconExtractor._icon_cache[cache_key] = icon
    
    @staticmethod
    def _get_from_cache(file_path: str, sizes: List[int] = None) -> Optional[QIcon]:
        """Get an icon from the cache if available."""
        cache_key = IconExtractor._get_cache_key(file_path, sizes)
        return IconExtractor._icon_cache.get(cache_key)
    
    @staticmethod
    def clear_cache() -> None:
        """Clear the icon cache."""
        IconExtractor._icon_cache.clear()
    
    @staticmethod
    def extract_icon(file_path: str, size: int = 32) -> QIcon:
        """
        Extract icon from file using best available method.
        Falls back gracefully if advanced methods aren't available.
        """
        file_path = str(Path(file_path).resolve())
        
        # Check cache first
        cached_icon = IconExtractor._get_from_cache(file_path, [size])
        if cached_icon:
            return cached_icon
        
        # Method 1: Try win32 API (most accurate, like SuperLauncher)
        if HAS_WIN32:
            icon = IconExtractor._extract_with_win32(file_path, size)
            if icon and not icon.isNull():
                IconExtractor._add_to_cache(file_path, [size], icon)
                return icon
        
        # Method 2: Try system icon association
        icon = IconExtractor._extract_system_icon(file_path)
        if icon and not icon.isNull():
            IconExtractor._add_to_cache(file_path, [size], icon)
            return icon
        
        # Method 3: Default icon based on file extension
        icon = IconExtractor._get_default_icon(file_path)
        IconExtractor._add_to_cache(file_path, [size], icon)
        return icon
    
    @staticmethod
    def extract_icon_multi_size(file_path: str, sizes: List[int] = None) -> QIcon:
        """
        Extract icon at multiple sizes for better scaling quality.
        This method provides the best visual results by extracting icons
        at multiple resolutions and letting Qt choose the best one.
        """
        try:
            if sizes is None:
                sizes = [16, 24, 32, 48, 64, 128, 256]  # Common icon sizes
            
            file_path = str(Path(file_path).resolve())
            
            # Check cache first
            cached_icon = IconExtractor._get_from_cache(file_path, sizes)
            if cached_icon:
                return cached_icon
            
            icon = QIcon()
            
            # Method 1: Try win32 API with multiple sizes
            if HAS_WIN32:
                for size in sizes:
                    try:
                        single_icon = IconExtractor._extract_with_win32(file_path, size)
                        if single_icon and not single_icon.isNull():
                            pixmap = single_icon.pixmap(size, size)
                            if not pixmap.isNull():
                                icon.addPixmap(pixmap)
                    except Exception:
                        continue
                
                # If we got any icons, return the multi-size icon
                if not icon.isNull():
                    IconExtractor._add_to_cache(file_path, sizes, icon)
                    return icon
            
            # Method 2: Try system icon association (also supports multiple sizes)
            try:
                file_info = QFileInfo(file_path)
                provider = QFileIconProvider()
                system_icon = provider.icon(file_info)
                
                # Extract multiple sizes from system icon
                for size in sizes:
                    pixmap = system_icon.pixmap(size, size)
                    if not pixmap.isNull():
                        icon.addPixmap(pixmap)
                
                if not icon.isNull():
                    IconExtractor._add_to_cache(file_path, sizes, icon)
                    return icon
            except Exception:
                pass
            
            # Method 3: Default icon with multiple sizes
            icon = IconExtractor._get_default_icon_multi_size(file_path, sizes)
            IconExtractor._add_to_cache(file_path, sizes, icon)
            return icon
        except Exception:
            # If multi-size extraction fails, fall back to basic method
            return IconExtractor.extract_icon(file_path, sizes[0] if sizes else 32)
    
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
    
    @staticmethod
    def _get_default_icon_multi_size(file_path: str, sizes: List[int]) -> QIcon:
        """Get default icon at multiple sizes for better scaling."""
        try:
            app = QApplication.instance()
            if not app:
                return QIcon()
            
            icon = QIcon()
            
            # Check if it's a directory first
            if os.path.isdir(file_path):
                base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            else:
                ext = Path(file_path).suffix.lower()
                
                # Executable files
                if ext in ['.exe', '.msi', '.bat', '.cmd', '.com']:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
                
                # Script files
                elif ext in ['.py', '.pyw', '.js', '.vbs', '.ps1']:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
                
                # Documents
                elif ext in ['.txt', '.doc', '.docx', '.pdf', '.rtf']:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
                
                # Media files
                elif ext in ['.mp3', '.mp4', '.avi', '.mov', '.wav']:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
                
                # Folders/shortcuts
                elif ext in ['.lnk']:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_FileLinkIcon)
                
                # Default file icon
                else:
                    base_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            
            # Add multiple sizes to the icon
            for size in sizes:
                pixmap = base_icon.pixmap(size, size)
                if not pixmap.isNull():
                    icon.addPixmap(pixmap)
            
            return icon
                
        except Exception:
            return QIcon()

    @staticmethod
    def create_high_quality_icon(base_icon: QIcon, target_size: int) -> QIcon:
        """
        Create a high-quality icon by scaling with better interpolation.
        This method provides smoother scaling for icons that need to be resized.
        """
        if base_icon.isNull():
            return base_icon
        
        # Try to get the largest available size first
        available_sizes = base_icon.availableSizes()
        if not available_sizes:
            return base_icon
        
        # Find the best source size (closest to target but not smaller)
        best_size = None
        for size in sorted(available_sizes, key=lambda s: s.width(), reverse=True):
            if size.width() >= target_size:
                best_size = size
                break
        
        # If no larger size found, use the largest available
        if not best_size:
            best_size = max(available_sizes, key=lambda s: s.width())
        
        # Extract the pixmap at the best size
        source_pixmap = base_icon.pixmap(best_size)
        if source_pixmap.isNull():
            return base_icon
        
        # Create a new icon with the scaled pixmap
        scaled_icon = QIcon()
        
        # Add the target size with high-quality scaling
        if best_size.width() == target_size:
            # No scaling needed
            scaled_icon.addPixmap(source_pixmap)
        else:
            # Scale with high quality
            scaled_pixmap = source_pixmap.scaled(
                target_size, target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled_icon.addPixmap(scaled_pixmap)
        
        # Also add the original sizes for better quality
        for size in available_sizes:
            if size.width() != target_size:
                pixmap = base_icon.pixmap(size)
                if not pixmap.isNull():
                    scaled_icon.addPixmap(pixmap)
        
        return scaled_icon
    
    @staticmethod
    def create_dpi_aware_icon(base_icon: QIcon, target_size: int, device_pixel_ratio: float = 1.0) -> QIcon:
        """
        Create a DPI-aware icon that looks crisp on high-DPI displays.
        This method accounts for the device pixel ratio to ensure icons
        are rendered at the appropriate resolution.
        """
        if base_icon.isNull():
            return base_icon
        
        # Calculate the actual pixel size needed for the target logical size
        actual_pixel_size = int(target_size * device_pixel_ratio)
        
        # Get available sizes
        available_sizes = base_icon.availableSizes()
        if not available_sizes:
            return base_icon
        
        # Find the best source size for the actual pixel size
        best_size = None
        for size in sorted(available_sizes, key=lambda s: s.width(), reverse=True):
            if size.width() >= actual_pixel_size:
                best_size = size
                break
        
        # If no larger size found, use the largest available
        if not best_size:
            best_size = max(available_sizes, key=lambda s: s.width())
        
        # Extract the pixmap at the best size
        source_pixmap = base_icon.pixmap(best_size)
        if source_pixmap.isNull():
            return base_icon
        
        # Create a new icon
        dpi_icon = QIcon()
        
        # Add the target logical size
        if best_size.width() == actual_pixel_size:
            # No scaling needed, but we need to set the device pixel ratio
            dpi_icon.addPixmap(source_pixmap)
        else:
            # Scale to the actual pixel size with high quality
            scaled_pixmap = source_pixmap.scaled(
                actual_pixel_size, actual_pixel_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            dpi_icon.addPixmap(scaled_pixmap)
        
        # Add other available sizes for fallback
        for size in available_sizes:
            if size.width() != actual_pixel_size:
                pixmap = base_icon.pixmap(size)
                if not pixmap.isNull():
                    dpi_icon.addPixmap(pixmap)
        
        return dpi_icon
    
    @staticmethod
    def get_icon_quality_settings() -> dict:
        """
        Get the current icon quality settings.
        Returns a dictionary with quality configuration options.
        """
        return {
            'use_high_quality_scaling': True,
            'use_dpi_aware_scaling': True,
            'preferred_source_sizes': [32, 48, 64, 128, 256],
            'fallback_scaling_method': 'smooth',  # 'smooth', 'fast', 'best'
            'cache_enabled': True,
            'cache_size_limit': 100
        }
    
    @staticmethod
    def set_icon_quality_settings(settings: dict) -> None:
        """
        Update icon quality settings.
        This allows users to customize the icon scaling behavior.
        """
        if 'cache_size_limit' in settings:
            IconExtractor._cache_size_limit = settings['cache_size_limit']
        
        if 'cache_enabled' in settings and not settings['cache_enabled']:
            IconExtractor.clear_cache()
    
    @staticmethod
    def extract_icon_with_quality(file_path: str, target_size: int, quality_settings: dict = None) -> QIcon:
        """
        Extract icon with customizable quality settings.
        This is the main method that users should call for best results.
        """
        try:
            if quality_settings is None:
                quality_settings = IconExtractor.get_icon_quality_settings()
            
            # Extract base icon with multiple sizes
            base_icon = IconExtractor.extract_icon_multi_size(
                file_path, 
                quality_settings.get('preferred_source_sizes', [32, 48, 64, 128])
            )
            
            if base_icon.isNull():
                return base_icon
            
            # Apply quality settings
            if quality_settings.get('use_dpi_aware_scaling', True):
                # Get device pixel ratio
                device_pixel_ratio = 1.0
                try:
                    screen = QApplication.primaryScreen()
                    if screen:
                        device_pixel_ratio = screen.devicePixelRatio()
                except Exception:
                    pass
                
                return IconExtractor.create_dpi_aware_icon(base_icon, target_size, device_pixel_ratio)
            elif quality_settings.get('use_high_quality_scaling', True):
                return IconExtractor.create_high_quality_icon(base_icon, target_size)
            else:
                # Return base icon without additional processing
                return base_icon
        except Exception:
            # If quality extraction fails, fall back to basic method
            return IconExtractor.extract_icon(file_path, target_size)

    @staticmethod
    def get_icon_diagnostics(file_path: str) -> dict:
        """
        Get diagnostic information about icon extraction for a file.
        This helps users understand what's happening with their icons.
        """
        diagnostics = {
            'file_path': file_path,
            'file_exists': False,
            'file_type': 'unknown',
            'extraction_methods': [],
            'available_sizes': [],
            'errors': [],
            'recommendations': []
        }
        
        try:
            file_path = str(Path(file_path).resolve())
            diagnostics['file_path'] = file_path
            diagnostics['file_exists'] = os.path.exists(file_path)
            
            if not diagnostics['file_exists']:
                diagnostics['errors'].append("File does not exist")
                return diagnostics
            
            # Determine file type
            if os.path.isdir(file_path):
                diagnostics['file_type'] = 'directory'
            else:
                ext = Path(file_path).suffix.lower()
                if ext in ['.exe', '.msi', '.bat', '.cmd', '.com']:
                    diagnostics['file_type'] = 'executable'
                elif ext in ['.py', '.pyw', '.js', '.vbs', '.ps1']:
                    diagnostics['file_type'] = 'script'
                elif ext in ['.txt', '.doc', '.docx', '.pdf', '.rtf']:
                    diagnostics['file_type'] = 'document'
                elif ext in ['.mp3', '.mp4', '.avi', '.mov', '.wav']:
                    diagnostics['file_type'] = 'media'
                elif ext in ['.lnk']:
                    diagnostics['file_type'] = 'shortcut'
                else:
                    diagnostics['file_type'] = 'file'
            
            # Test different extraction methods
            if HAS_WIN32:
                try:
                    win32_icon = IconExtractor._extract_with_win32(file_path, 32)
                    if win32_icon and not win32_icon.isNull():
                        diagnostics['extraction_methods'].append('win32_api')
                        diagnostics['available_sizes'].extend([s.width() for s in win32_icon.availableSizes()])
                    else:
                        diagnostics['errors'].append("Win32 API extraction failed")
                except Exception as e:
                    diagnostics['errors'].append(f"Win32 API error: {str(e)}")
            else:
                diagnostics['recommendations'].append("Install pywin32 for better icon extraction")
            
            # Test system icon extraction
            try:
                system_icon = IconExtractor._extract_system_icon(file_path)
                if system_icon and not system_icon.isNull():
                    diagnostics['extraction_methods'].append('system_icon')
                    diagnostics['available_sizes'].extend([s.width() for s in system_icon.availableSizes()])
                else:
                    diagnostics['errors'].append("System icon extraction failed")
            except Exception as e:
                diagnostics['errors'].append(f"System icon error: {str(e)}")
            
            # Test default icon
            try:
                default_icon = IconExtractor._get_default_icon(file_path)
                if default_icon and not default_icon.isNull():
                    diagnostics['extraction_methods'].append('default_icon')
                    diagnostics['available_sizes'].extend([s.width() for s in default_icon.availableSizes()])
                else:
                    diagnostics['errors'].append("Default icon extraction failed")
            except Exception as e:
                diagnostics['errors'].append(f"Default icon error: {str(e)}")
            
            # Remove duplicates and sort sizes
            diagnostics['available_sizes'] = sorted(list(set(diagnostics['available_sizes'])))
            
            # Generate recommendations
            if not diagnostics['extraction_methods']:
                diagnostics['recommendations'].append("No icon extraction methods succeeded")
            elif len(diagnostics['extraction_methods']) == 1:
                diagnostics['recommendations'].append("Only one extraction method working - consider fallbacks")
            
            if not diagnostics['available_sizes']:
                diagnostics['recommendations'].append("No icon sizes available - check file format")
            elif max(diagnostics['available_sizes']) < 48:
                diagnostics['recommendations'].append("Icons may appear small - enable high-quality scaling")
            
            if diagnostics['file_type'] == 'executable' and 'win32_api' not in diagnostics['extraction_methods']:
                diagnostics['recommendations'].append("For executables, install pywin32 for best results")
            
        except Exception as e:
            diagnostics['errors'].append(f"General error: {str(e)}")
        
        return diagnostics


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
        self.content_widget.setStyleSheet("background-color: #333333;")
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
        # Ensure no widgets appear focused on startup
        self._clear_highlights()

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
        
        # Apply dark theme styling to app widget
        widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 8px;
                border: 1px solid #404040;
            }
        """)
        
        # Store app data
        widget.app_data = app
        
        # Layout for icon and text
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Icon
        icon_label = QLabel()
        try:
            # Use the new quality-aware icon extraction method
            icon = IconExtractor.extract_icon_with_quality(app.path, 48)
            if icon and not icon.isNull():
                pixmap = icon.pixmap(48, 48)
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap)
                else:
                    # Fallback to basic icon extraction
                    fallback_icon = IconExtractor.extract_icon(app.path, 48)
                    if fallback_icon and not fallback_icon.isNull():
                        icon_label.setPixmap(fallback_icon.pixmap(48, 48))
            else:
                # Fallback to basic icon extraction
                fallback_icon = IconExtractor.extract_icon(app.path, 48)
                if fallback_icon and not fallback_icon.isNull():
                    icon_label.setPixmap(fallback_icon.pixmap(48, 48))
        except Exception as e:
            # If all else fails, try basic icon extraction
            try:
                fallback_icon = IconExtractor.extract_icon(app.path, 48)
                if fallback_icon and not fallback_icon.isNull():
                    icon_label.setPixmap(fallback_icon.pixmap(48, 48))
            except Exception:
                # Last resort: leave icon label empty
                pass
        
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
                color: #ffffff;
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
            # Clear highlights after 1 second delay
            QTimer.singleShot(2500, self._clear_highlights)

    def _on_app_hover_enter(self, event, widget):
        """Handle mouse enter on app widget."""
        if not hasattr(widget, '_is_clicked') or not widget._is_clicked:
            widget.setStyleSheet("""
                QWidget {
                    background-color: #353535;
                    border-radius: 8px;
                    border: 1px solid #606060;
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
                background-color: #383838;
                border-radius: 8px;
                border: 1px solid #606060;
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
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    border: 2px dashed #404040;
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
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    border: 1px solid #404040;
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
            # Select the item that was right-clicked
            self._last_clicked_app = child.app_data
            self._clear_highlights()
            child._is_clicked = True
            child.setStyleSheet("""
                QWidget {
                    background-color: #383838;
                    border-radius: 8px;
                    border: 1px solid #606060;
                }
            """)
            
            self._show_context_menu(child.app_data, self.content_widget.mapToGlobal(pos))

    def _show_context_menu(self, app: AppItem, global_pos):
        """Show context menu for an app."""
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #404040;
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
                background-color: #404040;
                color: #ffffff;
            }
            QMenu::item:pressed {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
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
        menu.addSeparator()
        icon_diagnostics_action = menu.addAction("Icon Diagnostics...")
        remove_action = menu.addAction("Unpin")
        
        action = menu.exec(global_pos)
        
        if is_folder:
            if action == open_action:
                self._run_app(app)  # This will open the folder
            elif action == open_loc_action:
                self._open_location(app)
            elif action == rename_action:
                self._rename_app(app)
            elif action == icon_diagnostics_action:
                self._show_icon_diagnostics()
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
            elif action == icon_diagnostics_action:
                self._show_icon_diagnostics()
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
    
    def _show_item_missing_error(self, app: AppItem):
        """Show error when trying to run a missing item."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.warning(
            self,
            "Item Not Found",
            f"The item '{app.display_name()}' no longer exists at:\n{app.path}\n\nPlease Unpin it from the launcher or update the path.",
            QMessageBox.Ok
        )

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
        
        # Icon quality settings
        self.icon_quality_settings = {
            'use_high_quality_scaling': True,
            'use_dpi_aware_scaling': True,
            'preferred_source_sizes': [32, 48, 64, 128, 256],
            'fallback_scaling_method': 'smooth',
            'cache_enabled': True,
            'cache_size_limit': 100
        }
        
        # Apply icon quality settings
        self._apply_icon_quality_settings()
        
        # Override window title and size for launcher
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(620, 620)
        self.setMaximumSize(620, 620)
        self.resize(620, 620)
        
        # Remove default window frame and create custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set window icon for taskbar (different from UI icons) - after setting window flags
        window_icon = QIcon("template_app/assets/icons/icon2.png")
        if not window_icon.isNull():
            self.setWindowIcon(window_icon)
            print(f"Window icon set successfully: {window_icon.availableSizes()}")
        else:
            print("Failed to load window icon from template_app/assets/icons/icon2.png")
        
        # Enable high-quality rendering attributes
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        
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
        
        self._shortcut_icon_settings = QShortcut(QKeySequence("Ctrl+I"), self)
        self._shortcut_icon_settings.activated.connect(self._show_icon_quality_settings)
        
        self._shortcut_icon_diagnostics = QShortcut(QKeySequence("Ctrl+D"), self)
        self._shortcut_icon_diagnostics.activated.connect(self._show_icon_diagnostics)
        
        # Apply dark theme to main window with transparent background for rounded corners
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: #ffffff;
            }
        """)
    
    def _apply_icon_quality_settings(self):
        """Apply the current icon quality settings to the IconExtractor."""
        IconExtractor.set_icon_quality_settings(self.icon_quality_settings)
    
    def _show_icon_quality_settings(self):
        """Show a dialog to configure icon quality settings."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox, QComboBox, QLabel, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Icon Quality Settings")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        # Apply dark theme styling to match the UI
        dialog.setStyleSheet("""
            QDialog {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QCheckBox {
                color: #ffffff;
                background-color: transparent;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #606060;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #ffffff;
                border-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #808080;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 4px;
            }
            QSpinBox:hover {
                border-color: #808080;
            }
            QSpinBox:focus {
                border-color: #ffffff;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 4px;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #808080;
            }
            QComboBox:focus {
                border-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #808080;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #363636;
                border-color: #808080;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # High quality scaling checkbox
        high_quality_cb = QCheckBox("Use high-quality scaling")
        high_quality_cb.setChecked(self.icon_quality_settings['use_high_quality_scaling'])
        layout.addWidget(high_quality_cb)
        
        # DPI-aware scaling checkbox
        dpi_aware_cb = QCheckBox("Use DPI-aware scaling")
        dpi_aware_cb.setChecked(self.icon_quality_settings['use_dpi_aware_scaling'])
        layout.addWidget(dpi_aware_cb)
        
        # Cache enabled checkbox
        cache_cb = QCheckBox("Enable icon caching")
        cache_cb.setChecked(self.icon_quality_settings['cache_enabled'])
        layout.addWidget(cache_cb)
        
        # Cache size limit
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("Cache size limit:"))
        cache_spin = QSpinBox()
        cache_spin.setRange(50, 500)
        cache_spin.setValue(self.icon_quality_settings['cache_size_limit'])
        cache_layout.addWidget(cache_spin)
        layout.addLayout(cache_layout)
        
        # Scaling method
        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(QLabel("Scaling method:"))
        scaling_combo = QComboBox()
        scaling_combo.addItems(['smooth', 'fast', 'best'])
        scaling_combo.setCurrentText(self.icon_quality_settings['fallback_scaling_method'])
        scaling_layout.addWidget(scaling_combo)
        layout.addLayout(scaling_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        apply_btn.clicked.connect(lambda: self._apply_icon_settings_dialog(
            dialog, high_quality_cb.isChecked(), dpi_aware_cb.isChecked(),
            cache_cb.isChecked(), cache_spin.value(), scaling_combo.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _show_icon_diagnostics(self):
        """Show a dialog to diagnose icon issues for the selected app."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea
        
        # Get the currently selected app
        selected_app = self.app_grid.current_app()
        if not selected_app:
            QMessageBox.information(self, "Icon Diagnostics", "Please select an app first to diagnose its icons.")
            return
        
        # Get diagnostics
        diagnostics = IconExtractor.get_icon_diagnostics(selected_app.path)
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Icon Diagnostics - {selected_app.display_name()}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        # Apply dark theme styling to match the UI
        dialog.setStyleSheet("""
            QDialog {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #363636;
                border-color: #808080;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # App info
        app_info = QLabel(f"App: {selected_app.display_name()}\nPath: {selected_app.path}")
        app_info.setStyleSheet("""
            font-weight: bold; 
            padding: 10px; 
            background: #2d2d2d; 
            border: 1px solid #404040;
            border-radius: 5px;
            color: #ffffff;
        """)
        layout.addWidget(app_info)
        
        # File status
        status_text = f"File exists: {'✓' if diagnostics['file_exists'] else '✗'}\n"
        status_text += f"File type: {diagnostics['file_type']}"
        status_label = QLabel(status_text)
        status_label.setStyleSheet("""
            padding: 5px; 
            background: #2d2d2d; 
            border: 1px solid #404040;
            border-radius: 4px;
            color: #ffffff;
        """)
        layout.addWidget(status_label)
        
        # Extraction methods
        methods_text = "Extraction methods:\n"
        if diagnostics['extraction_methods']:
            for method in diagnostics['extraction_methods']:
                methods_text += f"  ✓ {method}\n"
        else:
            methods_text += "  ✗ None working\n"
        
        methods_label = QLabel(methods_text)
        methods_label.setStyleSheet("""
            padding: 5px; 
            background: #2d2d2d; 
            border: 1px solid #404040;
            border-radius: 4px;
            color: #ffffff;
        """)
        layout.addWidget(methods_label)
        
        # Available sizes
        sizes_text = "Available icon sizes:\n"
        if diagnostics['available_sizes']:
            sizes_text += f"  {', '.join(map(str, diagnostics['available_sizes']))}\n"
        else:
            sizes_text += "  None\n"
        
        sizes_label = QLabel(sizes_text)
        sizes_label.setStyleSheet("""
            padding: 5px; 
            background: #2d2d2d; 
            border: 1px solid #404040;
            border-radius: 4px;
            color: #ffffff;
        """)
        layout.addWidget(sizes_label)
        
        # Errors and recommendations
        if diagnostics['errors'] or diagnostics['recommendations']:
            issues_text = ""
            if diagnostics['errors']:
                issues_text += "Errors:\n"
                for error in diagnostics['errors']:
                    issues_text += f"  ✗ {error}\n"
            
            if diagnostics['recommendations']:
                issues_text += "\nRecommendations:\n"
                for rec in diagnostics['recommendations']:
                    issues_text += f"  💡 {rec}\n"
            
            issues_textedit = QTextEdit()
            issues_textedit.setPlainText(issues_text)
            issues_textedit.setReadOnly(True)
            issues_textedit.setMaximumHeight(150)
            layout.addWidget(QLabel("Issues and Recommendations:"))
            layout.addWidget(issues_textedit)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Test icon button
        test_btn = QPushButton("Test Icon Extraction")
        test_btn.clicked.connect(lambda: self._test_icon_extraction(selected_app.path))
        button_layout.addWidget(test_btn)
        
        # Clear cache button
        clear_cache_btn = QPushButton("Clear Icon Cache")
        clear_cache_btn.clicked.connect(self._clear_icon_cache)
        button_layout.addWidget(clear_cache_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh App Grid")
        refresh_btn.clicked.connect(lambda: self._refresh_app_grid())
        button_layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _test_icon_extraction(self, file_path: str):
        """Test icon extraction for a specific file."""
        try:
            # Test different methods
            methods = [
                ("Basic extraction", lambda: IconExtractor.extract_icon(file_path, 48)),
                ("Multi-size extraction", lambda: IconExtractor.extract_icon_multi_size(file_path, [32, 48, 64])),
                ("High-quality scaling", lambda: IconExtractor.create_high_quality_icon(
                    IconExtractor.extract_icon_multi_size(file_path, [32, 48, 64]), 48)),
                ("Quality-aware extraction", lambda: IconExtractor.extract_icon_with_quality(file_path, 48))
            ]
            
            results = []
            for method_name, method_func in methods:
                try:
                    icon = method_func()
                    if icon and not icon.isNull():
                        sizes = icon.availableSizes()
                        results.append(f"✓ {method_name}: {len(sizes)} sizes available")
                    else:
                        results.append(f"✗ {method_name}: Failed")
                except Exception as e:
                    results.append(f"✗ {method_name}: Error - {str(e)}")
            
            # Show results
            result_text = "Icon extraction test results:\n\n" + "\n".join(results)
            QMessageBox.information(self, "Icon Test Results", result_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Test Error", f"Error testing icon extraction:\n{str(e)}")
    
    def _clear_icon_cache(self):
        """Clear the icon cache."""
        try:
            IconExtractor.clear_cache()
            QMessageBox.information(self, "Cache Cleared", "Icon cache has been cleared successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Cache Error", f"Error clearing cache:\n{str(e)}")
    
    def _refresh_app_grid(self):
        """Refresh the app grid to show updated icons."""
        try:
            self.app_grid.populate(self.apps)
            QMessageBox.information(self, "Refresh Complete", "App grid has been refreshed with updated icons.")
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing app grid:\n{str(e)}")
    
    def _title_bar_mouse_press(self, event):
        """Handle mouse press on title bar for window dragging."""
        if event.button() == Qt.LeftButton:
            # Store the initial mouse position relative to the window
            self._drag_start_pos = event.globalPosition().toPoint()
            self._window_start_pos = self.pos()
            self._dragging = True
    
    def _title_bar_mouse_move(self, event):
        """Handle mouse move on title bar for window dragging."""
        if hasattr(self, '_dragging') and self._dragging:
            # Calculate the new position based on the initial window position and mouse delta
            current_mouse_pos = event.globalPosition().toPoint()
            mouse_delta = current_mouse_pos - self._drag_start_pos
            new_window_pos = self._window_start_pos + mouse_delta
            
            # Move the window to the new position
            self.move(new_window_pos)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging."""
        if hasattr(self, '_dragging'):
            self._dragging = False
    
    def paintEvent(self, event):
        """Custom paint event to draw rounded corners with enhanced anti-aliasing."""
        from PySide6.QtGui import QPainter, QPainterPath, QBrush, QColor, QPen
        from PySide6.QtCore import Qt
        
        painter = QPainter(self)
        
        # Enhanced anti-aliasing and rendering quality (PySide6 compatible)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # Create rounded rectangle path with 10px radius
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        
        # Fill with dark background using high-quality brush
        brush = QBrush(QColor("#333333"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.fillPath(path, brush)
        
        # Draw subtle border with anti-aliased pen
        pen = QPen(QColor("#404040"))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

    def _apply_icon_settings_dialog(self, dialog, high_quality, dpi_aware, cache_enabled, cache_size, scaling_method):
        """Apply the icon quality settings from the dialog."""
        self.icon_quality_settings.update({
            'use_high_quality_scaling': high_quality,
            'use_dpi_aware_scaling': dpi_aware,
            'cache_enabled': cache_enabled,
            'cache_size_limit': cache_size,
            'fallback_scaling_method': scaling_method
        })
        
        # Apply the new settings
        self._apply_icon_quality_settings()
        
        # Clear the icon cache to force regeneration with new settings
        IconExtractor.clear_cache()
        
        # Refresh the app grid to show icons with new quality settings
        self.app_grid.populate(self.apps)
        
        dialog.accept()

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
        
        # Custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 0, 0)
        title_bar_layout.setSpacing(0)
        
        # App icon and title on the left
        title_info = QWidget()
        title_info_layout = QHBoxLayout(title_info)
        title_info_layout.setContentsMargins(0, 0, 0, 0)
        title_info_layout.setSpacing(8)
        
        # App icon
        app_icon = QLabel()
        icon = QIcon("template_app/assets/icons/icon.png")
        if not icon.isNull():
            app_icon.setPixmap(icon.pixmap(20, 20))
        app_icon.setStyleSheet("background: transparent; border: none;")
        
        # App title
        app_title = QLabel(APP_NAME)
        app_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        
        title_info_layout.addWidget(app_icon)
        title_info_layout.addWidget(app_title)
        title_info_layout.addStretch()
        
        # Window control buttons on the right
        controls_container = QWidget()
        controls_container.setStyleSheet("background: transparent; border: none;")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)
        
        # Minimize button
        btn_minimize = QPushButton("─")
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #404040;
                border-radius: 4px;
            }
        """)
        btn_minimize.clicked.connect(self.showMinimized)
        
        # Close button
        btn_close_title = QPushButton("×")
        btn_close_title.setFixedSize(30, 30)
        btn_close_title.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e81123;
                border-radius: 4px;
            }
        """)
        btn_close_title.clicked.connect(self.close)
        
        controls_layout.addWidget(btn_minimize)
        controls_layout.addWidget(btn_close_title)
        
        # Add widgets to title bar
        title_bar_layout.addWidget(title_info)
        title_bar_layout.addWidget(controls_container)
        
        # Header: Title and search
        # Create title container with icon and text
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        
        # Add rocket icon
        icon_label = QLabel()
        icon = QIcon("template_app/assets/icons/icon.png")
        if not icon.isNull():
            # Use high-quality scaling for the header icon
            icon_label.setPixmap(icon.pixmap(32, 32, QIcon.Mode.Normal, QIcon.State.Off))
        else:
            # Fallback if icon not found - try alternative paths
            fallback_paths = [
                "template_app/assets/icons/icon.png",
                "template_app/assets/icon.png",
                "assets/icons/icon.png"
            ]
            
            icon = QIcon()
            for path in fallback_paths:
                icon = QIcon(path)
                if not icon.isNull():
                    break
            
            # If still no icon found, create a default placeholder
            if icon.isNull():
                # Create a simple colored square as placeholder
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(100, 150, 200))  # Nice blue color
                icon = QIcon(pixmap)
        
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title text
        title_label = QLabel(APP_NAME)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                font-weight: bold; 
                padding: 10px; 
                color: #ffffff;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Add icon and title to layout
        #title_layout = QHBoxLayout(title_container)
        #title_layout.setContentsMargins(0, 0, 0, 0)
        #title_layout.setSpacing(0)
        #title_layout.setAlignment(Qt.AlignCenter)
        #title_layout.addWidget(icon_label)
        #title_layout.addWidget(title_label)
        
        # Add search box below title
        self.filter_edit = QLineEdit()
        self.filter_edit.setFixedHeight(30)
        self.filter_edit.setFixedWidth(250)
        self.filter_edit.setPlaceholderText("Search...")
        self.filter_edit.textChanged.connect(self.on_filter)
        self.filter_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                margin: 0 20px;
            }
            QLineEdit:focus {
                border-color: #404040;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        
        # Create a container widget for the header content
        header_content = QWidget()
        header_content.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        header_content_layout = QVBoxLayout(header_content)
        header_content_layout.setContentsMargins(0, 10, 0, 0)
        header_content_layout.setSpacing(10)
        
        # Add title and search box vertically
        #header_content_layout.addWidget(title_container)
        header_content_layout.addWidget(self.filter_edit, alignment=Qt.AlignCenter)
        
        # Add the header content to the main header layout
        self.header_layout.addWidget(header_content)
        
        # Increase header height to accommodate title and search box
        self.header_widget.setFixedHeight(100)
        
        # Add title bar to the very top of the main layout
        self.layout().insertWidget(0, title_bar)
        
        # Enable window dragging from title bar
        title_bar.mousePressEvent = self._title_bar_mouse_press
        title_bar.mouseMoveEvent = self._title_bar_mouse_move
        

        # Body: App list and controls
        # Create splitter for better layout control
        splitter = QSplitter(Qt.Vertical)
        
        # App grid area
        self.app_grid = AppGrid()
        self.app_grid.populate(self.apps)
        # Don't connect context menu here - AppGrid handles it internally
        
        # Style the scroll area to match the dark theme
        self.app_grid.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #333333;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Control buttons area
        controls_widget = QWidget()
        controls_widget.setStyleSheet("""
            QWidget {
                background-color: #2F2F2F;
                border: none;
                border-radius: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(10, 0, 10, 0)
        
        self.btn_add = QPushButton("Add")
        self.btn_add.setFixedWidth(80)
        self.btn_add.setFixedHeight(35)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #363636;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        
        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(self.on_run_selected)
        self.btn_run.setFixedWidth(80)
        self.btn_run.setFixedHeight(35)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #363636;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        
        self.btn_more = QPushButton("Options")
        self.btn_more.setFixedWidth(80)
        self.btn_more.setFixedHeight(35)
        self.btn_more.clicked.connect(self.on_more_menu)
        self.btn_more.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #363636;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)

        # Add close button
        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedWidth(80)
        self.btn_close.setFixedHeight(35)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #383838;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)

        controls_layout.addWidget(self.btn_more)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_add)
        controls_layout.addSpacing(5)
        controls_layout.addWidget(self.btn_run)
        controls_layout.addSpacing(5)
        controls_layout.addWidget(self.btn_close)
        
        
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
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #404040;
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
                background-color: #404040;
                color: #ffffff;
            }
            QMenu::item:pressed {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
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
        # Use Desktop as default location instead of Start Menu Programs
        desktop_dir = os.path.expandvars(r"%USERPROFILE%\Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.expanduser("~")
            
        paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select files to pin", 
            desktop_dir,
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
        # Use Desktop as default location instead of Start Menu Programs
        desktop_dir = os.path.expandvars(r"%USERPROFILE%\Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.expanduser("~")
            
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select folder to pin",
            desktop_dir
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
        # Clear highlights after 1 second delay
        QTimer.singleShot(2500, self.app_grid._clear_highlights)

    def on_more_menu(self) -> None:
        """Show the more options menu."""
        menu = QMenu(self)
        
        # Apply dark context menu styling
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #404040;
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
                background-color: #404040;
                color: #ffffff;
            }
            QMenu::item:pressed {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
                margin: 4px 8px;
            }
        """)
        
        add_files_action = menu.addAction("Add Files...")
        add_folder_action = menu.addAction("Add Folder...")
        menu.addSeparator()
        icon_settings_action = menu.addAction("Icon Quality Settings...")
        icon_diagnostics_action = menu.addAction("Icon Diagnostics...")
        menu.addSeparator()
        quit_action = menu.addAction("Exit")
        
        # Position menu near the button
        button_pos = self.btn_more.mapToGlobal(self.btn_more.rect().bottomLeft())
        action = menu.exec(button_pos)
        
        if action == add_files_action:
            self.on_add_files()
        elif action == add_folder_action:
            self.on_add_folder()
        elif action == icon_settings_action:
            self._show_icon_quality_settings()
        elif action == icon_diagnostics_action:
            self._show_icon_diagnostics()
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
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #404040;
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
                background-color: #404040;
                color: #ffffff;
            }
            QMenu::item:pressed {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
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
        menu.addSeparator()
        icon_diagnostics_action = menu.addAction("Icon Diagnostics...")
        remove_action = menu.addAction("Unpin")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if is_folder:
            if action == open_action:
                self.run_path(app.path)  # This will open the folder
            elif action == open_loc_action:
                self.open_location(app.path)
            elif action == rename_action:
                self.rename_app(app)
            elif action == icon_diagnostics_action:
                self._show_icon_diagnostics()
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
                subprocess.Popen(["explorer", normalized_dir], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # If no parent directory (root drive), just open the item itself
                normalized_path = os.path.normpath(path)
                print(f"Opening item itself: {normalized_path}")
                subprocess.Popen(["explorer", normalized_path], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            QMessageBox.warning(self, APP_NAME, f"Failed to open location:\n{e}")

    def run_path(self, path: str) -> None:
        """Run a file with proper working directory or open a folder."""
        try:
            # Check if the path exists before trying to run it
            if not os.path.exists(path):
                QMessageBox.warning(
                    self, 
                    "Item Not Found", 
                    f"The item no longer exists at:\n{path}\n\nPlease Unpin it from the launcher or update the path.",
                    QMessageBox.Ok
                )
                return
            
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
                subprocess.Popen(["explorer", normalized_path], creationflags=subprocess.CREATE_NO_WINDOW)
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
                subprocess.Popen(ps_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
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
            subprocess.Popen(ps_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            QMessageBox.warning(self, APP_NAME, f"Failed to run as admin:\n{e}")


class LauncherApp:
    """Main launcher application."""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Set application icon globally (affects taskbar)
        app_icon = QIcon("template_app/assets/icons/icon2.png")
        if not app_icon.isNull():
            self.app.setWindowIcon(app_icon)
            print(f"Application icon set successfully: {app_icon.availableSizes()}")
        else:
            print("Failed to load application icon from template_app/assets/icons/icon2.png")
        
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


