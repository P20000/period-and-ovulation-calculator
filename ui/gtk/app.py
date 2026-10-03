"""
GTK4 and Libadwaita Application entry point and lifecycle manager.
"""

import os
import sys
from typing import Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Gio
from core.storage import StorageManager
from ui.base import BaseApp
from .window import MainWindow


class GtkApp(Adw.Application, BaseApp):
    """Native GTK4/Libadwaita application for modern Linux desktop environments."""

    def __init__(self, storage: Optional[StorageManager] = None):
        Adw.Application.__init__(
            self,
            application_id="org.antigravity.cycleandmood",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        BaseApp.__init__(self, storage_manager=storage)
        self.win: Optional[MainWindow] = None

    def do_activate(self):
        """Lifecycle hook triggered on application activation."""
        self._load_custom_css()
        if not self.win:
            self.win = MainWindow(self, self.storage)
        self.win.present()

    def _load_custom_css(self):
        """Loads and applies custom styling sheets for modern visual polish."""
        css_file = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_file):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_file)
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

    def run(self, args: Optional[list] = None) -> int:
        """Executes the GTK main loop."""
        return Adw.Application.run(self, args or sys.argv)
