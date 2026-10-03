"""
Deep Mood and Care Insights view detailing hormonal, emotional, and physical guidance.
"""

from typing import Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from core.models import Profile, PhaseInfo
from core.calculator import CycleCalculator


class InsightsView(Gtk.ScrolledWindow):
    """Presents in-depth scientific, emotional, and relationship care advice for the current phase."""

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
        self._build_groups()

    def _build_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.title_lbl = Gtk.Label(label="Cycle Insights & Mood Forecast", xalign=0)
        self.title_lbl.add_css_class("title-hero")

        self.phase_subtitle_lbl = Gtk.Label(label="Phase analysis", xalign=0)
        self.phase_subtitle_lbl.add_css_class("subtitle-text")

        header_box.append(self.title_lbl)
        header_box.append(self.phase_subtitle_lbl)
        self.container.append(header_box)

    def _build_groups(self):
        # Section 1: Emotional Landscape
        self.grp_mood = self._create_section_card(
            "🧠 Emotional Landscape & Mood",
            "What she is likely experiencing mentally and emotionally."
        )
        self.lbl_mood_content = Gtk.Label(label="", xalign=0)
        self.lbl_mood_content.set_wrap(True)
        self.grp_mood["box"].append(self.lbl_mood_content)
        self.container.append(self.grp_mood["frame"])

        # Section 2: Partner Care Strategy
        self.grp_partner = self._create_section_card(
            "💖 How You Can Best Support Her",
            "Actionable ways to make her feel loved, comfortable, and understood today."
        )
        self.lbl_partner_content = Gtk.Label(label="", xalign=0)
        self.lbl_partner_content.set_wrap(True)
        self.grp_partner["box"].append(self.lbl_partner_content)
        self.container.append(self.grp_partner["frame"])

        # Section 3: Hormonal Dynamics
        self.grp_hormones = self._create_section_card(
            "🔬 Hormonal Activity & Biological State",
            "Endocrine shifts taking place inside her body."
        )
        self.lbl_hormones_content = Gtk.Label(label="", xalign=0)
        self.lbl_hormones_content.set_wrap(True)
        self.grp_hormones["box"].append(self.lbl_hormones_content)
        self.container.append(self.grp_hormones["frame"])

        # Section 4: Physical Sensations
        self.grp_physical = self._create_section_card(
            "🌿 Physical Sensations & Energy",
            "Body signals, stamina, and symptoms."
        )
        self.lbl_physical_content = Gtk.Label(label="", xalign=0)
        self.lbl_physical_content.set_wrap(True)
        self.grp_physical["box"].append(self.lbl_physical_content)
        self.container.append(self.grp_physical["frame"])

        # Section 5: Nutrition & Healing Foods
        self.grp_nutrition = self._create_section_card(
            "🥑 Nourishing Foods & Nutrition Tips",
            "Nutrients that replenish energy and stabilize moods."
        )
        self.lbl_nutrition_content = Gtk.Label(label="", xalign=0)
        self.lbl_nutrition_content.set_wrap(True)
        self.grp_nutrition["box"].append(self.lbl_nutrition_content)
        self.container.append(self.grp_nutrition["frame"])

        # Section 6: Recommended Activities
        self.grp_activities = self._create_section_card(
            "✨ Recommended Activities Today",
            "Workouts, hobbies, and social pacing matching her current energy."
        )
        self.activities_flow = Gtk.FlowBox()
        self.activities_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.activities_flow.set_max_children_per_line(4)
        self.activities_flow.set_row_spacing(8)
        self.activities_flow.set_column_spacing(8)
        self.grp_activities["box"].append(self.activities_flow)
        self.container.append(self.grp_activities["frame"])

    def _create_section_card(self, title: str, subtitle: str) -> dict:
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        lbl_title = Gtk.Label(label=title, xalign=0)
        lbl_title.add_css_class("card-title")
        escaped_title = title.replace("&", "&amp;")
        lbl_title.set_markup(f"<b>{escaped_title}</b>")

        lbl_sub = Gtk.Label(label=subtitle, xalign=0)
        lbl_sub.add_css_class("subtitle-text")

        box.append(lbl_title)
        box.append(lbl_sub)
        frame.set_child(box)

        return {"frame": frame, "box": box, "title": lbl_title, "sub": lbl_sub}

    def update_profile(self, profile: Optional[Profile]):
        """Populates insight cards based on the calculated phase."""
        if not profile:
            self.phase_subtitle_lbl.set_text("No profile active.")
            return

        phase: PhaseInfo = CycleCalculator.calculate_phase(
            profile.last_period_start_date, profile.period_duration, profile.cycle_length
        )

        self.title_lbl.set_text(f"{profile.name.title()}'s Insights")
        self.phase_subtitle_lbl.set_text(
            f"Day {phase.day_in_cycle} of {phase.cycle_length} • {phase.phase_name} ({phase.energy_level})"
        )

        self.lbl_mood_content.set_text(phase.mood_summary)
        self.lbl_partner_content.set_text(phase.care_tip_for_partner)
        self.lbl_hormones_content.set_text(phase.hormone_status)
        self.lbl_physical_content.set_text(phase.physical_summary)
        self.lbl_nutrition_content.set_text(phase.nutrition_tip)

        # Clear and repopulate activities flow box
        while child := self.activities_flow.get_first_child():
            self.activities_flow.remove(child)

        for act in phase.recommended_activities:
            lbl = Gtk.Label(label=f"• {act}")
            lbl.add_css_class("tag-chip")
            self.activities_flow.append(lbl)
