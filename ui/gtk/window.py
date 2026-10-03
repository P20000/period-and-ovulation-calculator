"""
Main application window for GTK4 / Libadwaita interface.
Coordinates view switching, toast feedback, and profile updates.
"""

from typing import Dict, Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio
from core.models import Profile, DailyLog
from core.storage import StorageManager
from .dashboard_view import DashboardView
from .insights_view import InsightsView
from .tracker_view import TrackerView
from .history_view import HistoryView
from .profiles_dialog import ProfilesDialog


class MainWindow(Adw.ApplicationWindow):
    """Main window with Adwaita styling, ViewStack navigation, and Toast feedback."""

    def __init__(self, app: Adw.Application, storage: StorageManager):
        super().__init__(application=app)
        self.storage = storage
        self.profiles = self.storage.load_profiles()
        self.current_profile: Optional[Profile] = None

        if self.profiles:
            self.current_profile = next(iter(self.profiles.values()))

        self.set_title("Cycle & Mood Tracker")
        self.set_default_size(880, 780)

        self._build_ui()
        self._refresh_all_views()

    def _build_ui(self):
        self.toast_overlay = Adw.ToastOverlay()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(self.main_box)
        self.set_content(self.toast_overlay)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        self.view_switcher_title = Adw.ViewSwitcherTitle()
        self.view_switcher_title.set_title("Cycle & Mood")
        self.view_switcher_title.set_subtitle(self.current_profile.name.title() if self.current_profile else "No Profile")
        self.header_bar.set_title_widget(self.view_switcher_title)

        # Profile Switcher Button in Header
        self.btn_profile = Gtk.Button(label="👤 Profiles")
        self.btn_profile.connect("clicked", self._on_manage_profiles_clicked)
        self.header_bar.pack_start(self.btn_profile)

        # Color Theme Toggle Button
        self.btn_theme = Gtk.Button(icon_name="weather-clear-night-symbolic")
        self.btn_theme.set_tooltip_text("Toggle Dark / Light Theme")
        self.btn_theme.connect("clicked", self._on_toggle_theme)
        self.header_bar.pack_end(self.btn_theme)

        self.main_box.append(self.header_bar)

        # View Stack
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)
        self.view_switcher_title.set_stack(self.view_stack)

        # Views
        self.dashboard_view = DashboardView(on_switch_tab=self.switch_to_tab)
        self.insights_view = InsightsView()
        self.tracker_view = TrackerView(on_save_log=self._on_save_daily_log)
        self.history_view = HistoryView()

        self.view_stack.add_titled_with_icon(
            self.dashboard_view, "dashboard", "Dashboard", "emblem-favorite-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.insights_view, "insights", "Care Insights", "dialog-information-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.tracker_view, "tracker", "Tracker", "document-edit-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.history_view, "history", "Forecast", "x-office-calendar-symbolic"
        )

        self.main_box.append(self.view_stack)

        # Bottom ViewSwitcherBar for narrow screen widths
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.view_stack)
        self.view_switcher_title.bind_property(
            "title-visible", self.view_switcher_bar, "reveal", 0
        )
        self.main_box.append(self.view_switcher_bar)

    def switch_to_tab(self, tab_id: str):
        """Switches the view stack to the specified child name."""
        self.view_stack.set_visible_child_name(tab_id)

    def _on_manage_profiles_clicked(self, _):
        dialog = ProfilesDialog(
            parent=self,
            profiles=self.profiles,
            current_profile=self.current_profile,
            on_select=self._on_select_profile,
            on_save=self._on_save_profile,
            on_delete=self._on_delete_profile,
        )
        dialog.present()

    def _on_select_profile(self, profile_name: str):
        key = profile_name.lower()
        if key in self.profiles:
            self.current_profile = self.profiles[key]
            self._refresh_all_views()
            self.show_toast(f"Switched to {self.current_profile.name.title()}")

    def _on_save_profile(self, profile: Profile):
        key = profile.name.lower()
        self.profiles[key] = profile
        self.storage.save_profiles(self.profiles)
        self.current_profile = profile
        self._refresh_all_views()
        self.show_toast(f"Profile '{profile.name.title()}' saved!")

    def _on_delete_profile(self, profile_name: str):
        key = profile_name.lower()
        if key in self.profiles:
            del self.profiles[key]
            self.storage.save_profiles(self.profiles)
            self.current_profile = next(iter(self.profiles.values())) if self.profiles else None
            self._refresh_all_views()
            self.show_toast(f"Deleted profile '{profile_name.title()}'")

    def _on_save_daily_log(self, log: DailyLog):
        if not self.current_profile:
            self.show_toast("Please select a profile first.")
            return

        date_key = log.log_date.isoformat()
        self.current_profile.daily_logs[date_key] = log
        self.profiles[self.current_profile.name.lower()] = self.current_profile
        self.storage.save_profiles(self.profiles)
        self._refresh_all_views()
        self.show_toast("✨ Today's symptoms & mood saved successfully!")

    def _on_toggle_theme(self, _):
        manager = Adw.StyleManager.get_default()
        if manager.get_dark():
            manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            self.btn_theme.set_icon_name("weather-clear-night-symbolic")
        else:
            manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            self.btn_theme.set_icon_name("weather-clear-symbolic")

    def show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _refresh_all_views(self):
        sub = self.current_profile.name.title() if self.current_profile else "No Profile"
        self.view_switcher_title.set_subtitle(sub)
        self.dashboard_view.update_profile(self.current_profile)
        self.insights_view.update_profile(self.current_profile)
        self.tracker_view.update_profile(self.current_profile)
        self.history_view.update_profile(self.current_profile)
