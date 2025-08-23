import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QSize, QEvent, QFileInfo
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (
	QApplication,
	QFileIconProvider,
	QGridLayout,
	QHBoxLayout,
	QInputDialog,
	QLabel,
	QLineEdit,
	QListWidget,
	QListWidgetItem,
	QMainWindow,
	QMenu,
	QMessageBox,
	QPushButton,
	QSystemTrayIcon,
	QToolButton,
	QVBoxLayout,
	QWidget,
	QFileDialog,
	QStyle,
)

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


APP_NAME = "PySuperLauncher"


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
		"""Get default icon based on file extension."""
		try:
			app = QApplication.instance()
			if not app:
				return QIcon()
			
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


class AppList(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.list = QListWidget()
		self.list.setIconSize(QSize(24, 24))
		layout = QVBoxLayout(self)
		layout.addWidget(self.list)

	def populate(self, apps: List[AppItem]) -> None:
		self.list.clear()
		for app in apps:
			# Extract icon using the new IconExtractor
			icon = IconExtractor.extract_icon(app.path, 24)
			item = QListWidgetItem(icon, app.display_name())
			item.setData(Qt.UserRole, app)
			self.list.addItem(item)

	def filter(self, text: str) -> None:
		text_lower = text.lower()
		for i in range(self.list.count()):
			item = self.list.item(i)
			app: AppItem = item.data(Qt.UserRole)
			visible = text_lower in app.display_name().lower()
			item.setHidden(not visible)

	def current_app(self) -> Optional[AppItem]:
		item = self.list.currentItem()
		return item.data(Qt.UserRole) if item else None

	def app_at_pos(self, pos) -> Optional[AppItem]:
		item = self.list.itemAt(pos)
		return item.data(Qt.UserRole) if item else None


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle(APP_NAME)
		self.setMinimumSize(400, 300)
		self.config = ConfigStore()
		self.apps: List[AppItem] = self.config.load_apps()

		# Center area: app list
		self.app_list = AppList()
		self.app_list.populate(self.apps)
		self.app_list.list.itemDoubleClicked.connect(self.on_run_selected)

		# Bottom bar
		self.filter_edit = QLineEdit(self)
		self.filter_edit.setPlaceholderText("Filter apps…")
		self.filter_edit.textChanged.connect(self.on_filter)

		self.btn_add = QToolButton(self)
		self.btn_add.setText("+")
		self.btn_add.clicked.connect(self.on_add)

		self.btn_run = QToolButton(self)
		self.btn_run.setText("Run")
		self.btn_run.clicked.connect(self.on_run_selected)

		self.btn_more = QToolButton(self)
		self.btn_more.setText("⋯")
		self.btn_more.clicked.connect(self.on_more_menu)

		bottom = QHBoxLayout()
		bottom.addWidget(self.filter_edit, 1)
		bottom.addWidget(self.btn_add)
		bottom.addWidget(self.btn_run)
		bottom.addWidget(self.btn_more)

		central = QWidget(self)
		v = QVBoxLayout(central)
		v.addWidget(self.app_list, 1)
		v.addLayout(bottom)
		self.setCentralWidget(central)

		# Context menu
		self.app_list.list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.app_list.list.customContextMenuRequested.connect(self.open_context_menu)

	def on_filter(self, text: str) -> None:
		self.app_list.filter(text)

	def on_add(self) -> None:
		paths, _ = QFileDialog.getOpenFileNames(self, "Select items to pin", os.path.expandvars(r"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"))
		if not paths:
			return
		for p in paths:
			self.apps.append(AppItem(path=p))
		self.config.save_apps(self.apps)
		self.app_list.populate(self.apps)

	def on_run_selected(self) -> None:
		app = self.app_list.current_app()
		if not app:
			return
		self.run_path(app.path)

	def on_more_menu(self) -> None:
		menu = QMenu(self)
		add_action = menu.addAction("Add items…")
		quit_action = menu.addAction("Exit")
		action = menu.exec(self.mapToGlobal(self.rect().bottomRight()))
		if action == add_action:
			self.on_add()
		elif action == quit_action:
			QApplication.quit()

	def open_context_menu(self, pos) -> None:
		app = self.app_list.app_at_pos(pos)
		if not app:
			return
		menu = QMenu(self)
		run_action = menu.addAction("Run")
		run_admin_action = menu.addAction("Run as administrator")
		open_loc_action = menu.addAction("Open location")
		rename_action = menu.addAction("Rename")
		remove_action = menu.addAction("Unpin")
		action = menu.exec(self.app_list.list.mapToGlobal(pos))
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
		new_title, ok = QInputDialog.getText(self, "Rename", "Title", text=app.display_name())
		if not ok:
			return
		app.title = new_title.strip() or None
		self.config.save_apps(self.apps)
		self.app_list.populate(self.apps)

	def remove_app(self, app: AppItem) -> None:
		self.apps = [a for a in self.apps if a.path != app.path]
		self.config.save_apps(self.apps)
		self.app_list.populate(self.apps)

	def open_location(self, path: str) -> None:
		dir_path = str(Path(path).parent)
		try:
			subprocess.Popen(["explorer", dir_path])
		except Exception as e:
			QMessageBox.warning(self, APP_NAME, f"Failed to open location:\n{e}")

	def run_path(self, path: str) -> None:
		try:
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
			QMessageBox.warning(self, APP_NAME, f"Failed to run:\n{e}")

	def run_path_admin(self, path: str) -> None:
		# Use ShellExecute with 'runas' via PowerShell Start-Process -Verb RunAs
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


class TrayApp:
	def __init__(self):
		self.app = QApplication.instance() or QApplication(sys.argv)
		self.window = MainWindow()
		self.tray = QSystemTrayIcon(self.window)
		self.tray.setIcon(self.window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
		self.tray.setToolTip(APP_NAME)
		menu = QMenu()
		act_toggle = QAction("Open", self.tray)
		act_quit = QAction("Exit", self.tray)
		act_toggle.triggered.connect(self.toggle)
		act_quit.triggered.connect(self.quit)
		menu.addAction(act_toggle)
		menu.addSeparator()
		menu.addAction(act_quit)
		self.tray.setContextMenu(menu)
		self.tray.activated.connect(self.on_tray_activated)
		self.tray.show()

	def toggle(self):
		if self.window.isVisible():
			self.window.hide()
		else:
			self.window.show()
			self.window.raise_()
			self.window.activateWindow()

	def on_tray_activated(self, reason):
		if reason == QSystemTrayIcon.Trigger:
			self.toggle()

	def quit(self):
		QApplication.quit()

	def run(self):
		return self.app.exec()


def main():
	app = TrayApp()
	sys.exit(app.run())
