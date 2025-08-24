import json
import os
from dataclasses import dataclass
from typing import Optional, Union, Tuple


@dataclass
class AppSettings:
    window_title: str = "Sample App"
    window_size: Tuple[int, int] = (620, 620)
    icon_path: str = "template_app/assets/icons/icon.png"


def project_root() -> str:
    """Return base directory for locating bundled assets.

    - When running under PyInstaller, prefer the executable directory
      (one-folder) or the temporary extraction dir (one-file via _MEIPASS).
    - When running from source, keep using the current working directory
      so existing relative paths like 'template_app/assets/...' continue to work.
    """
    import sys
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.abspath(os.getcwd())


def load_json(path: str, default: Optional[Union[dict, list]] = None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_app_settings(config_path: str = "config.json") -> AppSettings:
    config = load_json(config_path, {}) or {}
    app_settings = config.get("app_settings", {})
    title = app_settings.get("window_title", "Sample App")
    size = tuple(app_settings.get("window_size", [550, 550]))
    icon = app_settings.get("icon_path", "template_app/assets/icons/icon.png")
    return AppSettings(window_title=title, window_size=size, icon_path=icon)


