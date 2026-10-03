"""
Cairo-rendered circular cycle dial and phase visualization widget for GTK4.
"""

import math
from typing import Tuple
import cairo
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from core.models import PhaseType
from core.calculator import CycleCalculator


def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
    """Converts a hex color string to Cairo float RGB (0.0 - 1.0)."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 6:
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return r / 255.0, g / 255.0, b / 255.0
    return 0.5, 0.5, 0.5


class CycleCanvas(Gtk.DrawingArea):
    """Draws an interactive circular gauge showing cycle progress and phases."""

    def __init__(self, cycle_day: int = 1, cycle_length: int = 28, period_duration: int = 5):
        super().__init__()
        self.cycle_day = cycle_day
        self.cycle_length = max(15, cycle_length)
        self.period_duration = max(1, period_duration)
        self.phase_color = "#8E54E9"
        self.phase_name = "Follicular"

        self.set_content_width(280)
        self.set_content_height(280)
        self.set_draw_func(self._on_draw)

    def update_data(self, cycle_day: int, cycle_length: int, period_duration: int, phase_color: str, phase_name: str):
        """Updates cycle parameters and requests a canvas repaint."""
        self.cycle_day = max(1, min(cycle_day, cycle_length))
        self.cycle_length = max(15, cycle_length)
        self.period_duration = max(1, period_duration)
        self.phase_color = phase_color
        self.phase_name = phase_name
        self.queue_draw()

    def _on_draw(self, area, cr, width: int, height: int):
        cx = width / 2.0
        cy = height / 2.0
        radius = min(cx, cy) - 25.0
        line_width = 18.0

        if radius <= 10:
            return

        # 1. Background Track
        cr.set_line_width(line_width)
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.12)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()

        # 2. Phase Segments
        # Calculate angle ranges for each phase
        total_days = self.cycle_length
        ovulation_day = max(self.period_duration + 2, total_days - 14)
        fertile_start = max(self.period_duration + 1, ovulation_day - 4)
        fertile_end = ovulation_day + 1
        early_luteal_end = total_days - 5

        segments = [
            (1, self.period_duration, CycleCalculator.PHASE_COLORS[PhaseType.MENSTRUAL]),
            (self.period_duration + 1, fertile_start - 1, CycleCalculator.PHASE_COLORS[PhaseType.FOLLICULAR]),
            (fertile_start, fertile_end, CycleCalculator.PHASE_COLORS[PhaseType.OVULATION]),
            (fertile_end + 1, early_luteal_end, CycleCalculator.PHASE_COLORS[PhaseType.LUTEAL_EARLY]),
            (early_luteal_end + 1, total_days, CycleCalculator.PHASE_COLORS[PhaseType.LUTEAL_LATE_PMS]),
        ]

        start_base_angle = -math.pi / 2  # 12 o'clock

        for seg_start, seg_end, color in segments:
            if seg_start > seg_end or seg_start > total_days:
                continue
            seg_end = min(seg_end, total_days)

            a_start = start_base_angle + 2 * math.pi * ((seg_start - 1) / total_days)
            a_end = start_base_angle + 2 * math.pi * (seg_end / total_days)

            # Small gap between segments for clean modern UI look
            gap = 0.03
            if (a_end - a_start) > gap:
                r, g, b = hex_to_rgb(color)
                cr.set_source_rgba(r, g, b, 0.75)
                cr.set_line_width(line_width)
                cr.arc(cx, cy, radius, a_start + gap/2, a_end - gap/2)
                cr.stroke()

        # 3. Active Progress Arc
        current_progress_angle = start_base_angle + 2 * math.pi * (self.cycle_day / total_days)
        pr_r, pr_g, pr_b = hex_to_rgb(self.phase_color)

        # 4. Current Day Indicator Pointer
        indicator_x = cx + radius * math.cos(current_progress_angle)
        indicator_y = cy + radius * math.sin(current_progress_angle)

        # Outer glowing halo
        cr.set_source_rgba(pr_r, pr_g, pr_b, 0.35)
        cr.arc(indicator_x, indicator_y, 14, 0, 2 * math.pi)
        cr.fill()

        # Inner solid dot
        cr.set_source_rgba(pr_r, pr_g, pr_b, 1.0)
        cr.arc(indicator_x, indicator_y, 8, 0, 2 * math.pi)
        cr.fill()

        # White center pip
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.9)
        cr.arc(indicator_x, indicator_y, 4, 0, 2 * math.pi)
        cr.fill()

        # 5. Center Text Readout
        cr.select_font_face("Sans", 0, 1)  # Bold
        cr.set_font_size(28.0)
        day_text = f"Day {self.cycle_day}"
        extents = cr.text_extents(day_text)
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.95)
        cr.move_to(cx - (extents.width / 2), cy - 6)
        cr.show_text(day_text)

        # Subtitle: of Total Days
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(13.0)
        sub_text = f"of {self.cycle_length} days"
        ext_sub = cr.text_extents(sub_text)
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.85)
        cr.move_to(cx - (ext_sub.width / 2), cy + 16)
        cr.show_text(sub_text)

        # Phase pill label in center
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(11.0)
        phase_short = self.phase_name.split("(")[0].strip()
        ext_ph = cr.text_extents(phase_short)
        cr.set_source_rgba(pr_r, pr_g, pr_b, 1.0)
        cr.move_to(cx - (ext_ph.width / 2), cy + 36)
        cr.show_text(phase_short)
