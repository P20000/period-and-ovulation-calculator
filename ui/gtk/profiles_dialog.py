"""
Profile management dialog for creating, editing, switching, and deleting profiles in GTK4.
"""

from datetime import date, datetime
from typing import Callable, Dict, Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from core.models import Profile


class ProfilesDialog(Adw.Window):
    """Modern modal dialog for managing user profiles."""

    def __init__(
        self,
        parent: Gtk.Window,
        profiles: Dict[str, Profile],
        current_profile: Optional[Profile],
        on_select: Callable[[str], None],
        on_save: Callable[[Profile], None],
        on_delete: Callable[[str], None],
    ):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Manage Profiles")
        self.set_default_size(480, 560)

        self.profiles = profiles
        self.current_profile = current_profile
        self.on_select = on_select
        self.on_save = on_save
        self.on_delete = on_delete

        self._build_ui()

    def _build_ui(self):
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        # Header bar
        header = Adw.HeaderBar()
        content_box.append(header)

        # Scrolled view for form
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        inner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        # Group 1: Profile Selector & Switcher
        grp_select = Adw.PreferencesGroup(title="Active Profile")
        self.combo_row = Adw.ComboRow(title="Select Profile")
        self.string_list = Gtk.StringList()

        names = list(self.profiles.keys())
        for n in names:
            self.string_list.append(n.title())
        self.combo_row.set_model(self.string_list)

        if self.current_profile and self.current_profile.name.lower() in names:
            idx = names.index(self.current_profile.name.lower())
            self.combo_row.set_selected(idx)

        self.combo_row.connect("notify::selected", self._on_profile_dropdown_changed)
        grp_select.add(self.combo_row)
        inner_box.append(grp_select)

        # Group 2: Edit or Create Profile Details
        self.grp_form = Adw.PreferencesGroup(title="Profile Settings")

        self.entry_name = Adw.EntryRow(title="Name")
        self.entry_date = Adw.EntryRow(title="Last Period Start (YYYY-MM-DD or DD-MM-YYYY)")
        self.entry_duration = Adw.SpinRow.new_with_range(1, 20, 1)
        self.entry_duration.set_title("Period Duration (Days)")
        self.entry_cycle = Adw.SpinRow.new_with_range(15, 60, 1)
        self.entry_cycle.set_title("Total Cycle Length (Days)")

        self.grp_form.add(self.entry_name)
        self.grp_form.add(self.entry_date)
        self.grp_form.add(self.entry_duration)
        self.grp_form.add(self.entry_cycle)
        inner_box.append(self.grp_form)

        # Action Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_halign(Gtk.Align.FILL)
        btn_box.set_homogeneous(True)

        self.btn_save = Gtk.Button(label="Save / Update Profile")
        self.btn_save.add_css_class("suggested-action")
        self.btn_save.connect("clicked", self._on_save_clicked)

        self.btn_new = Gtk.Button(label="Clear / New Profile")
        self.btn_new.connect("clicked", self._on_new_clicked)

        self.btn_del = Gtk.Button(label="Delete Profile")
        self.btn_del.add_css_class("destructive-action")
        self.btn_del.connect("clicked", self._on_delete_clicked)

        btn_box.append(self.btn_new)
        btn_box.append(self.btn_save)
        btn_box.append(self.btn_del)
        inner_box.append(btn_box)

        scroll.set_child(inner_box)
        content_box.append(scroll)
        self.set_content(content_box)

        # Pre-fill with current profile
        self._populate_form_with_current()

    def _populate_form_with_current(self):
        if self.current_profile:
            self.entry_name.set_text(self.current_profile.name.title())
            self.entry_date.set_text(self.current_profile.last_period_start_date.strftime("%Y-%m-%d"))
            self.entry_duration.set_value(self.current_profile.period_duration)
            self.entry_cycle.set_value(self.current_profile.cycle_length)
        else:
            self._on_new_clicked(None)

    def _on_profile_dropdown_changed(self, row, param):
        selected_idx = row.get_selected()
        names = list(self.profiles.keys())
        if 0 <= selected_idx < len(names):
            name = names[selected_idx]
            self.current_profile = self.profiles[name]
            self._populate_form_with_current()
            self.on_select(name)

    def _on_new_clicked(self, _):
        self.entry_name.set_text("")
        self.entry_date.set_text(date.today().strftime("%Y-%m-%d"))
        self.entry_duration.set_value(5)
        self.entry_cycle.set_value(28)

    def _on_save_clicked(self, _):
        raw_name = self.entry_name.get_text().strip()
        raw_date = self.entry_date.get_text().strip()
        duration = int(self.entry_duration.get_value())
        cycle = int(self.entry_cycle.get_value())

        if not raw_name:
            self._show_alert("Invalid Input", "Please enter a profile name.")
            return

        parsed_date = None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed_date = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                pass

        if parsed_date is None:
            self._show_alert("Invalid Date", "Please enter a valid date in YYYY-MM-DD or DD-MM-YYYY format.")
            return

        key = raw_name.lower()
        existing = self.profiles.get(key)

        new_profile = Profile(
            name=raw_name,
            last_period_start_date=parsed_date,
            period_duration=duration,
            cycle_length=cycle,
            history=existing.history if existing else [],
            daily_logs=existing.daily_logs if existing else {},
            notes=existing.notes if existing else ""
        )

        self.on_save(new_profile)
        self.close()

    def _on_delete_clicked(self, _):
        raw_name = self.entry_name.get_text().strip().lower()
        if raw_name in self.profiles:
            self.on_delete(raw_name)
            self.close()

    def _show_alert(self, title: str, message: str):
        dialog = Adw.MessageDialog(heading=title, body=message)
        dialog.set_transient_for(self)
        dialog.add_response("ok", "OK")
        dialog.present()
