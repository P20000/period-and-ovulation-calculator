"""
Dashboard view displaying current cycle status, visual dial, and quick insights.
"""

from typing import Callable, Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from core.models import Profile, PhaseInfo
from core.calculator import CycleCalculator
from .cycle_canvas import CycleCanvas


class DashboardView(Gtk.ScrolledWindow):
    """Main dashboard showing cycle dial, milestones, and daily highlights."""

    def __init__(self, on_switch_tab: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.on_switch_tab = on_switch_tab

        # Main vertical container with standard Adwaita padding
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.container.set_margin_top(20)
        self.container.set_margin_bottom(24)
        self.container.set_margin_start(24)
        self.container.set_margin_end(24)
        self.set_child(self.container)

        self._build_header_section()
        self._build_stat_cards()
        self._build_wheel_section()
        self._build_quick_insights_card()

    def _build_header_section(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.greeting_label = Gtk.Label(label="Cycle Overview", xalign=0)
        self.greeting_label.add_css_class("title-hero")

        self.date_label = Gtk.Label(label="Loading cycle status...", xalign=0)
        self.date_label.add_css_class("subtitle-text")

        header_box.append(self.greeting_label)
        header_box.append(self.date_label)
        self.container.append(header_box)

    def _build_stat_cards(self):
        self.stats_grid = Gtk.Grid()
        self.stats_grid.set_column_spacing(14)
        self.stats_grid.set_row_spacing(10)
        self.stats_grid.set_column_homogeneous(True)

        # Card 1: Phase
        self.card_phase = self._create_card("CURRENT PHASE", "Follicular", "4 days remaining", "#4E9FDF")
        # Card 2: Next Period
        self.card_period = self._create_card("NEXT PERIOD", "In 14 Days", "Expected on --", "#E05375")
        # Card 3: Ovulation
        self.card_ovulation = self._create_card("OVULATION", "In 4 Days", "Fertile window open", "#38B278")

        self.stats_grid.attach(self.card_phase["box"], 0, 0, 1, 1)
        self.stats_grid.attach(self.card_period["box"], 1, 0, 1, 1)
        self.stats_grid.attach(self.card_ovulation["box"], 2, 0, 1, 1)

        self.container.append(self.stats_grid)

    def _create_card(self, title: str, main_val: str, sub_val: str, accent_color: str) -> dict:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add_css_class("stat-card")

        lbl_title = Gtk.Label(label=title, xalign=0)
        lbl_title.add_css_class("stat-label")

        lbl_val = Gtk.Label(label=main_val, xalign=0)
        lbl_val.add_css_class("stat-value")

        lbl_sub = Gtk.Label(label=sub_val, xalign=0)
        lbl_sub.add_css_class("subtitle-text")

        box.append(lbl_title)
        box.append(lbl_val)
        box.append(lbl_sub)

        return {"box": box, "title": lbl_title, "value": lbl_val, "sub": lbl_sub}

    def _build_wheel_section(self):
        wheel_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        wheel_container.set_halign(Gtk.Align.CENTER)
        wheel_container.add_css_class("cycle-canvas-container")

        self.cycle_canvas = CycleCanvas()
        wheel_container.append(self.cycle_canvas)

        self.container.append(wheel_container)

    def _build_quick_insights_card(self):
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card_box.add_css_class("care-card")

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.mood_badge = Gtk.Label(label="✨ High Energy & Optimistic")
        self.mood_badge.add_css_class("tag-chip")
        
        lbl_care_title = Gtk.Label(label="Partner Care Guidance", xalign=0)
        lbl_care_title.add_css_class("care-card-title")
        lbl_care_title.set_hexpand(True)

        top_row.append(lbl_care_title)
        top_row.append(self.mood_badge)

        self.care_text_label = Gtk.Label(label="", xalign=0)
        self.care_text_label.set_wrap(True)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_halign(Gtk.Align.END)

        self.btn_more_insights = Gtk.Button(label="Explore Deep Insights →")
        self.btn_more_insights.connect("clicked", lambda _: self._navigate_to("insights"))

        self.btn_quick_log = Gtk.Button(label="Log Symptoms")
        self.btn_quick_log.add_css_class("btn-primary-accent")
        self.btn_quick_log.connect("clicked", lambda _: self._navigate_to("tracker"))

        btn_row.append(self.btn_more_insights)
        btn_row.append(self.btn_quick_log)

        card_box.append(top_row)
        card_box.append(self.care_text_label)
        card_box.append(btn_row)

        self.container.append(card_box)

    def _navigate_to(self, tab_id: str):
        if self.on_switch_tab:
            self.on_switch_tab(tab_id)

    def update_profile(self, profile: Optional[Profile]):
        """Updates all dashboard elements with current profile calculations."""
        if not profile:
            self.greeting_label.set_text("No Profile Selected")
            self.date_label.set_text("Please create or choose a profile.")
            return

        self.greeting_label.set_text(f"{profile.name.title()}'s Cycle")
        phase: PhaseInfo = CycleCalculator.calculate_phase(
            profile.last_period_start_date, profile.period_duration, profile.cycle_length
        )
        milestones = CycleCalculator.get_cycle_milestones(
            profile.last_period_start_date, profile.period_duration, profile.cycle_length
        )

        # Update Stat Cards
        self.card_phase["value"].set_text(phase.phase_name.split("(")[0].strip())
        self.card_phase["sub"].set_text(f"{phase.days_remaining_in_phase} days remaining in phase")

        days_period = milestones["days_until_next_period"]
        p_text = f"In {days_period} Day{'s' if days_period != 1 else ''}" if days_period >= 0 else "Due now"
        self.card_period["value"].set_text(p_text)
        self.card_period["sub"].set_text(f"Expected {milestones['next_period_date'].strftime('%b %d')}")

        days_ov = milestones["days_until_ovulation"]
        if milestones["is_in_fertile_window"]:
            self.card_ovulation["value"].set_text("Fertile Window")
            self.card_ovulation["sub"].set_text("High chance of conception")
        elif days_ov > 0:
            self.card_ovulation["value"].set_text(f"In {days_ov} Day{'s' if days_ov != 1 else ''}")
            self.card_ovulation["sub"].set_text(f"Ovulation ~{milestones['ovulation_date'].strftime('%b %d')}")
        else:
            self.card_ovulation["value"].set_text("Luteal Phase")
            self.card_ovulation["sub"].set_text("Ovulation completed")

        # Update Cycle Canvas
        self.cycle_canvas.update_data(
            phase.day_in_cycle,
            phase.cycle_length,
            profile.period_duration,
            phase.phase_color,
            phase.phase_name
        )

        # Update Care Box
        self.mood_badge.set_text(f"⚡ {phase.energy_level}")
        self.care_text_label.set_text(
            f"💡 How to support {profile.name.title()} today:\n{phase.care_tip_for_partner}\n\n"
            f"Mood Forecast: {phase.mood_summary}"
        )
