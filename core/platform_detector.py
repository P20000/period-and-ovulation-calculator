"""
Platform and environment detector for cross-platform GUI adaptation.
Inspects operating system, desktop environment, and available GUI toolkits.
"""

import importlib.util
import os
import platform
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BackendType(str, Enum):
    GTK4_ADWAITA = "gtk4_adwaita"
    GTK3 = "gtk3"
    CUSTOM_TKINTER = "custom_tkinter"
    TKINTER = "tkinter"
    HEADLESS = "headless"


@dataclass
class PlatformInfo:
    """Encapsulates system platform diagnostics and selected GUI backend."""
    os_name: str          # "Linux", "Darwin", "Windows"
    os_release: str
    architecture: str
    desktop_env: str      # "GNOME", "KDE", "Windows Shell", "Aqua", etc.
    display_server: str   # "wayland", "x11", "win32", "quartz", etc.
    python_version: str
    has_gtk4_adw: bool
    has_gtk3: bool
    has_customtkinter: bool
    has_tkinter: bool
    recommended_backend: BackendType

    def summary(self) -> str:
        return (
            f"Platform: {self.os_name} ({self.architecture}) | "
            f"Env: {self.desktop_env} ({self.display_server}) | "
            f"Backend Selected: {self.recommended_backend.value}"
        )


class PlatformDetector:
    """Detects running environment and selects the best native UI architecture."""

    @classmethod
    def detect(cls, force_backend: Optional[str] = None) -> PlatformInfo:
        os_name = platform.system()
        os_release = platform.release()
        arch = platform.machine()
        python_ver = sys.version.split()[0]

        # Detect desktop environment and display server
        desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
        display_server = "unknown"

        if os_name == "Linux" or "BSD" in os_name:
            if os.environ.get("WAYLAND_DISPLAY"):
                display_server = "wayland"
            elif os.environ.get("DISPLAY"):
                display_server = "x11"
        elif os_name == "Darwin":
            desktop_env = "Aqua (macOS)"
            display_server = "quartz"
        elif os_name == "Windows":
            desktop_env = "Windows Shell"
            display_server = "win32"

        # Check toolkit availability
        has_gtk4_adw = cls._check_gtk4_adwaita()
        has_gtk3 = cls._check_gtk3() if not has_gtk4_adw else False
        has_ctk = cls._check_customtkinter()
        has_tk = cls._check_tkinter()

        # Decide recommended backend
        selected_backend: BackendType
        if force_backend:
            backend_str = force_backend.lower().strip()
            if backend_str in ["gtk", "gtk4", "adw", "libadwaita"] and has_gtk4_adw:
                selected_backend = BackendType.GTK4_ADWAITA
            elif backend_str == "gtk3" and has_gtk3:
                selected_backend = BackendType.GTK3
            elif backend_str in ["ctk", "customtkinter"] and has_ctk:
                selected_backend = BackendType.CUSTOM_TKINTER
            elif backend_str in ["tk", "tkinter"] and has_tk:
                selected_backend = BackendType.TKINTER
            else:
                selected_backend = cls._choose_default_backend(has_gtk4_adw, has_gtk3, has_ctk, has_tk)
        else:
            selected_backend = cls._choose_default_backend(has_gtk4_adw, has_gtk3, has_ctk, has_tk)

        return PlatformInfo(
            os_name=os_name,
            os_release=os_release,
            architecture=arch,
            desktop_env=desktop_env,
            display_server=display_server,
            python_version=python_ver,
            has_gtk4_adw=has_gtk4_adw,
            has_gtk3=has_gtk3,
            has_customtkinter=has_ctk,
            has_tkinter=has_tk,
            recommended_backend=selected_backend,
        )

    @staticmethod
    def _choose_default_backend(has_gtk4_adw: bool, has_gtk3: bool, has_ctk: bool, has_tk: bool) -> BackendType:
        if has_gtk4_adw:
            return BackendType.GTK4_ADWAITA
        elif has_gtk3:
            return BackendType.GTK3
        elif has_ctk:
            return BackendType.CUSTOM_TKINTER
        elif has_tk:
            return BackendType.TKINTER
        else:
            return BackendType.HEADLESS

    @staticmethod
    def _check_gtk4_adwaita() -> bool:
        try:
            import gi
            gi.require_version("Gtk", "4.0")
            gi.require_version("Adw", "1")
            from gi.repository import Gtk, Adw
            return True
        except (ImportError, ValueError):
            return False

    @staticmethod
    def _check_gtk3() -> bool:
        try:
            import gi
            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk
            return True
        except (ImportError, ValueError):
            return False

    @staticmethod
    def _check_customtkinter() -> bool:
        return importlib.util.find_spec("customtkinter") is not None

    @staticmethod
    def _check_tkinter() -> bool:
        return importlib.util.find_spec("tkinter") is not None
