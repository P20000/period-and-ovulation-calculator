"""
History and Future Projections view for GTK4.
Displays upcoming 6-month cycle forecast and past daily symptom logs.
"""

from typing import Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from core.models import Profile
from core.calculator import CycleCalculator


class HistoryView(Gtk.ScrolledWindow):
    """Shows upcoming cycle projections and historical logged entries."""

    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.container.set_margin_top(20)
        self.container.set_margin_bottom(24)
        self.container.set_margin_start(24)
        self.container.set_margin_end(24)
        self.set_child(self.container)

        self._build_header()
        self._build_projections_section()
        self._build_logs_section()

    def _build_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.title_lbl = Gtk.Label(label="Cycle Forecast & Log History", xalign=0)
        self.title_lbl.add_css_class("title-hero")

        self.sub_lbl = Gtk.Label(label="Projected upcoming cycles and past logged entries", xalign=0)
        self.sub_lbl.add_css_class("subtitle-text")

        header_box.append(self.title_lbl)
        header_box.append(self.sub_lbl)
        self.container.append(header_box)

    def _build_projections_section(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        lbl = Gtk.Label(label="<b>📅 6-Month Cycle Forecast</b>", xalign=0, use_markup=True)
        box.append(lbl)

        self.projections_list = Gtk.ListBox()
        self.projections_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.projections_list.add_css_class("boxed-list")
        box.append(self.projections_list)

        frame.set_child(box)
        self.container.append(frame)

    def _build_logs_section(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        lbl = Gtk.Label(label="<b>📝 Recorded Symptom Logs</b>", xalign=0, use_markup=True)
        box.append(lbl)

        self.logs_list = Gtk.ListBox()
        self.logs_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.logs_list.add_css_class("boxed-list")
        box.append(self.logs_list)

        frame.set_child(box)
        self.container.append(frame)

    def update_profile(self, profile: Optional[Profile]):
        """Populates future projection rows and past logged days."""
        if not profile:
            return

        # 1. Populate Future Projections
        while child := self.projections_list.get_first_child():
            self.projections_list.remove(child)

        projections = CycleCalculator.get_future_projections(
            profile.last_period_start_date, profile.period_duration, profile.cycle_length, months_ahead=6
        )

        for proj in projections:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            hbox.set_margin_top(8)
            hbox.set_margin_bottom(8)
            hbox.set_margin_start(12)
            hbox.set_margin_end(12)

            # Cycle number pill
            pill = Gtk.Label(label=f"Cycle #{proj['cycle_index']}")
            pill.add_css_class("tag-chip")

            # Period dates
            period_str = f"Period: {proj['period_start'].strftime('%b %d')} - {proj['period_end'].strftime('%b %d, %Y')}"
            lbl_period = Gtk.Label(label=f"<b>{period_str}</b>", xalign=0, use_markup=True)
            lbl_period.set_hexpand(True)

            # Ovulation
            ov_str = f"Ovulation: ~{proj['ovulation_date'].strftime('%b %d')}"
            lbl_ov = Gtk.Label(label=ov_str, xalign=1)
            lbl_ov.add_css_class("subtitle-text")

            hbox.append(pill)
            hbox.append(lbl_period)
            hbox.append(lbl_ov)
            row.set_child(hbox)
            self.projections_list.append(row)

        # 2. Populate Past Logs
        while child := self.logs_list.get_first_child():
            self.logs_list.remove(child)

        if not profile.daily_logs:
            empty_row = Gtk.ListBoxRow()
            empty_lbl = Gtk.Label(label="No logs recorded yet. Use the Tracker tab to add one!", xalign=0)
            empty_lbl.set_margin_top(12)
            empty_lbl.set_margin_bottom(12)
            empty_lbl.set_margin_start(12)
            empty_lbl.add_css_class("subtitle-text")
            empty_row.set_child(empty_lbl)
            self.logs_list.append(empty_row)
        else:
            sorted_dates = sorted(profile.daily_logs.keys(), reverse=True)
            mood_emojis = {1: "😢 Low", 2: "😕 Sensitive", 3: "😐 Neutral", 4: "🙂 Good", 5: "🤩 Radiant"}

            for date_key in sorted_dates:
                log = profile.daily_logs[date_key]
                row = Gtk.ListBoxRow()
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                vbox.set_margin_top(8)
                vbox.set_margin_bottom(8)
                vbox.set_margin_start(12)
                vbox.set_margin_end(12)

                top_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                lbl_d = Gtk.Label(label=f"<b>{log.log_date.strftime('%a, %b %d, %Y')}</b>", xalign=0, use_markup=True)
                lbl_d.set_hexpand(True)

                mood_str = mood_emojis.get(log.mood_score, "😐")
                lbl_m = Gtk.Label(label=f"Mood: {mood_str}")
                lbl_m.add_css_class("tag-chip")

                top_h.append(lbl_d)
                top_h.append(lbl_m)
                vbox.append(top_h)

                # Symptoms
                if log.symptoms:
                    sym_str = "Symptoms: " + ", ".join(log.symptoms)
                    lbl_s = Gtk.Label(label=sym_str, xalign=0)
                    lbl_s.add_css_class("subtitle-text")
                    vbox.append(lbl_s)

                if log.notes:
                    lbl_n = Gtk.Label(label=f'"{log.notes}"', xalign=0)
                    vbox.append(lbl_n)

                row.set_child(vbox)
                self.logs_list.append(row)
