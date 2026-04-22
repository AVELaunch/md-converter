"""
Shared path resolution for MD Converter.

This is the single source of truth for app paths. Both converter_app.py
and converters.py import from here — do not duplicate path logic elsewhere.
"""

import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent


def user_data_dir() -> Path:
    """Return a writable per-user data directory, creating it if needed.

    When frozen (PyInstaller .app):
        macOS:  ~/Library/Application Support/MD Converter
        Other:  $XDG_DATA_HOME/md-converter or ~/.local/share/md-converter

    When running from source:
        The repo root (parent of src/).
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "MD Converter"
        else:
            xdg = os.environ.get("XDG_DATA_HOME")
            base = Path(xdg) / "md-converter" if xdg else Path.home() / ".local" / "share" / "md-converter"
        base.mkdir(parents=True, exist_ok=True)
        return base
    return APP_DIR


def config_path() -> Path:
    """Return the path to config.json."""
    return user_data_dir() / "config.json"
