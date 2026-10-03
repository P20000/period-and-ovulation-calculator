"""
Daily symptom, mood, and note tracker view for GTK4.
"""

from datetime import date
from typing import Callable, List, Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from core.models import Profile, DailyLog


COMMON_SYMPTOMS = [
    "Cramps", "Headache", "Bloating", "Tender Breasts",
    "Fatigue", "Backache", "Sugar Cravings", "Mood Swings",
    "Clear Skin", "High Energy", "Insomnia", "Anxiety"
]


class TrackerView(Gtk.ScrolledWindow):
    """View to log daily moods, physical symptoms, and custom notes."""

    def __init__(self, on_save_log: Optional[Callable[[DailyLog], None]] = None):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.on_save_log = on_save_log
        self.current_profile: Optional[Profile] = None
        self.selected_mood_score: int = 3
        self.symptom_checkboxes: dict = {}

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.container.set_margin_top(20)
        self.container.set_margin_bottom(24)
        self.container.set_margin_start(24)
        self.container.set_margin_end(24)
        self.set_child(self.container)

        self._build_header()
        self._build_mood_picker()
        self._build_sliders()
        self._build_symptoms_grid()
        self._build_notes_section()
        self._build_save_button()

    def _build_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.title_lbl = Gtk.Label(label="Daily Symptom & Mood Log", xalign=0)
        self.title_lbl.add_css_class("title-hero")

        today_str = date.today().strftime("%A, %B %d, %Y")
        self.sub_lbl = Gtk.Label(label=f"Recording for today: {today_str}", xalign=0)
        self.sub_lbl.add_css_class("subtitle-text")

        header_box.append(self.title_lbl)
        header_box.append(self.sub_lbl)
        self.container.append(header_box)

    def _build_mood_picker(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        lbl = Gtk.Label(label="<b>How is she feeling overall?</b>", xalign=0, use_markup=True)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_homogeneous(True)

        moods = [
            (1, "😢", "Very Low"),
            (2, "😕", "Low"),
            (3, "😐", "Neutral"),
            (4, "🙂", "Good"),
            (5, "🤩", "Radiant")
        ]

        self.mood_buttons = []
        for score, emoji, title in moods:
            btn = Gtk.Button(label=f"{emoji} {title}")
            btn.connect("clicked", self._make_mood_handler(score, btn))
            btn_box.append(btn)
            self.mood_buttons.append((score, btn))

        box.append(lbl)
        box.append(btn_box)
        frame.set_child(box)
        self.container.append(frame)

    def _make_mood_handler(self, score: int, clicked_btn: Gtk.Button):
        def handler(_):
            self.selected_mood_score = score
            for s, b in self.mood_buttons:
                if s == score:
                    b.add_css_class("suggested-action")
                else:
                    b.remove_css_class("suggested-action")
        return handler

    def _build_sliders(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Energy Slider
        lbl_energy = Gtk.Label(label="<b>Energy Level (1 - 5)</b>", xalign=0, use_markup=True)
        self.adj_energy = Gtk.Adjustment(value=3, lower=1, upper=5, step_increment=1, page_increment=1)
        self.scale_energy = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adj_energy)
        self.scale_energy.set_digits(0)
        self.scale_energy.set_draw_value(True)

        # Pain / Cramps Slider
        lbl_pain = Gtk.Label(label="<b>Cramps / Physical Discomfort Level (0 - 5)</b>", xalign=0, use_markup=True)
        self.adj_pain = Gtk.Adjustment(value=0, lower=0, upper=5, step_increment=1, page_increment=1)
        self.scale_pain = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adj_pain)
        self.scale_pain.set_digits(0)
        self.scale_pain.set_draw_value(True)

        box.append(lbl_energy)
        box.append(self.scale_energy)
        box.append(lbl_pain)
        box.append(self.scale_pain)
        frame.set_child(box)
        self.container.append(frame)

    def _build_symptoms_grid(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        lbl = Gtk.Label(label="<b>Active Symptoms &amp; Body Notes</b>", xalign=0, use_markup=True)
        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(8)
        grid.set_column_homogeneous(True)

        cols = 3
        for idx, symptom in enumerate(COMMON_SYMPTOMS):
            chk = Gtk.CheckButton(label=symptom)
            r = idx // cols
            c = idx % cols
            grid.attach(chk, c, r, 1, 1)
            self.symptom_checkboxes[symptom] = chk

        box.append(lbl)
        box.append(grid)
        frame.set_child(box)
        self.container.append(frame)

    def _build_notes_section(self):
        frame = Gtk.Frame()
        frame.add_css_class("stat-card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        lbl = Gtk.Label(label="<b>Personal Notes &amp; Observations</b>", xalign=0, use_markup=True)
        self.notes_buffer = Gtk.TextBuffer()
        self.notes_view = Gtk.TextView(buffer=self.notes_buffer)
        self.notes_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.notes_view.set_size_request(-1, 80)

        box.append(lbl)
        box.append(self.notes_view)
        frame.set_child(box)
        self.container.append(frame)

    def _build_save_button(self):
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_halign(Gtk.Align.END)

        self.btn_save = Gtk.Button(label="💾 Save Today's Log Entry")
        self.btn_save.add_css_class("btn-primary-accent")
        self.btn_save.connect("clicked", self._on_save_clicked)

        btn_box.append(self.btn_save)
        self.container.append(btn_box)

    def _on_save_clicked(self, _):
        selected_symptoms = [s for s, chk in self.symptom_checkboxes.items() if chk.get_active()]
        start_iter = self.notes_buffer.get_start_iter()
        end_iter = self.notes_buffer.get_end_iter()
        notes_text = self.notes_buffer.get_text(start_iter, end_iter, True)

        log = DailyLog(
            log_date=date.today(),
            mood_score=self.selected_mood_score,
            energy_score=int(self.adj_energy.get_value()),
            pain_level=int(self.adj_pain.get_value()),
            symptoms=selected_symptoms,
            notes=notes_text.strip(),
        )

        if self.on_save_log:
            self.on_save_log(log)

    def update_profile(self, profile: Optional[Profile]):
        """Preloads today's existing log entry if present."""
        self.current_profile = profile
        if not profile:
            return

        today_key = date.today().isoformat()
        if today_key in profile.daily_logs:
            log = profile.daily_logs[today_key]
            self.selected_mood_score = log.mood_score
            for s, b in self.mood_buttons:
                if s == log.mood_score:
                    b.add_css_class("suggested-action")
                else:
                    b.remove_css_class("suggested-action")

            self.adj_energy.set_value(log.energy_score)
            self.adj_pain.set_value(log.pain_level)

            for sym, chk in self.symptom_checkboxes.items():
                chk.set_active(sym in log.symptoms)

            self.notes_buffer.set_text(log.notes)
        else:
            # Reset defaults
            self.selected_mood_score = 3
            for s, b in self.mood_buttons:
                if s == 3:
                    b.add_css_class("suggested-action")
                else:
                    b.remove_css_class("suggested-action")
            self.adj_energy.set_value(3)
            self.adj_pain.set_value(0)
            for chk in self.symptom_checkboxes.values():
                chk.set_active(False)
            self.notes_buffer.set_text("")
