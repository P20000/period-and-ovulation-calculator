"""
Tkinter Canvas-based circular cycle wheel and phase visualizer for cross-platform fallback.
"""

import math
import tkinter as tk
from typing import Tuple
from core.models import PhaseType
from core.calculator import CycleCalculator


class TkCycleCanvas(tk.Canvas):
    """Draws a circular cycle ring widget using standard Tkinter Canvas."""

    def __init__(self, parent, size: int = 260, **kwargs):
        super().__init__(parent, width=size, height=size, bg="white", highlightthickness=0, **kwargs)
        self.size = size
        self.cycle_day = 1
        self.cycle_length = 28
        self.period_duration = 5
        self.phase_color = "#8E54E9"
        self.phase_name = "Follicular"
        self.draw_wheel()

    def update_data(self, cycle_day: int, cycle_length: int, period_duration: int, phase_color: str, phase_name: str):
        self.cycle_day = max(1, min(cycle_day, cycle_length))
        self.cycle_length = max(15, cycle_length)
        self.period_duration = max(1, period_duration)
        self.phase_color = phase_color
        self.phase_name = phase_name
        self.draw_wheel()

    def draw_wheel(self):
        self.delete("all")
        cx = self.size / 2
        cy = self.size / 2
        radius = (self.size / 2) - 25
        line_width = 16

        # Background track
        self.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline="#E8ECF2", width=line_width
        )

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

        # Tkinter angles: 0 is 3 o'clock (East), 90 is 12 o'clock (North)
        # We start at 90 (top) and move counter-clockwise in extent or clockwise by subtracting
        for seg_start, seg_end, color in segments:
            if seg_start > seg_end or seg_start > total_days:
                continue
            seg_end = min(seg_end, total_days)

            # Convert 1-based days to start angle (deg) and extent (deg)
            # Day 1 starts at 90 deg, moving clockwise (- degrees)
            start_deg = 90 - ((seg_start - 1) / total_days) * 360
            extent_deg = - ((seg_end - seg_start + 1) / total_days) * 360

            self.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_deg, extent=extent_deg,
                style=tk.ARC, outline=color, width=line_width
            )

        # Current progress pointer
        curr_angle_rad = (math.pi / 2) - (2 * math.pi * (self.cycle_day / total_days))
        pointer_x = cx + radius * math.cos(curr_angle_rad)
        pointer_y = cy - radius * math.sin(curr_angle_rad)

        # Indicator Dot
        self.create_oval(
            pointer_x - 10, pointer_y - 10, pointer_x + 10, pointer_y + 10,
            fill=self.phase_color, outline="white", width=2
        )

        # Center Text
        self.create_text(
            cx, cy - 12, text=f"Day {self.cycle_day}",
            font=("Helvetica", 18, "bold"), fill="#2D3748"
        )
        self.create_text(
            cx, cy + 10, text=f"of {self.cycle_length} days",
            font=("Helvetica", 10), fill="#718096"
        )
        short_name = self.phase_name.split("(")[0].strip()
        self.create_text(
            cx, cy + 28, text=short_name,
            font=("Helvetica", 10, "bold"), fill=self.phase_color
        )
