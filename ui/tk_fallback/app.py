"""
Tkinter/ttk cross-platform fallback application.
Provides complete feature parity across Windows, macOS, and Linux without GTK requirements.
"""

from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from core.models import Profile, DailyLog, PhaseInfo
from core.calculator import CycleCalculator
from core.storage import StorageManager
from ui.base import BaseApp
from .cycle_canvas import TkCycleCanvas


class TkApp(BaseApp):
    """Tkinter-based GUI fallback ensuring 100% cross-platform compatibility."""

    def __init__(self, storage: Optional[StorageManager] = None):
        super().__init__(storage_manager=storage)
        self.root = tk.Tk()
        self.root.title("Cycle & Mood Tracker (Cross-Platform Edition)")
        self.root.geometry("860x760")
        self.root.minsize(720, 600)
        self.root.configure(bg="#F7FAFC")

        self._setup_styles()
        self._build_ui()
        self._refresh_ui()

    def _setup_styles(self):
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure("TNotebook", background="#F7FAFC", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[16, 8])
        self.style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")])
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        self.style.configure("Primary.TButton", font=("Helvetica", 10, "bold"), background="#8E54E9", foreground="white")

    def _build_ui(self):
        # Top Profile Bar
        top_bar = tk.Frame(self.root, bg="#FFFFFF", padx=16, pady=12, highlightthickness=1, highlightbackground="#E2E8F0")
        top_bar.pack(fill="x", side="top")

        lbl_app = tk.Label(top_bar, text="🌸 Cycle & Mood Tracker", font=("Helvetica", 13, "bold"), bg="#FFFFFF", fg="#2D3748")
        lbl_app.pack(side="left")

        self.profile_var = tk.StringVar()
        self.combo_profile = ttk.Combobox(top_bar, textvariable=self.profile_var, state="readonly", width=22)
        self.combo_profile.pack(side="right", padx=6)
        self.combo_profile.bind("<<ComboboxSelected>>", self._on_profile_selected)

        lbl_prof = tk.Label(top_bar, text="Active Profile:", font=("Helvetica", 10), bg="#FFFFFF", fg="#718096")
        lbl_prof.pack(side="right")

        # Tab Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        # Tab 1: Dashboard
        self.tab_dash = tk.Frame(self.notebook, bg="#F7FAFC", padx=12, pady=12)
        self.notebook.add(self.tab_dash, text="📊 Dashboard")
        self._build_dashboard_tab()

        # Tab 2: Insights
        self.tab_insights = tk.Frame(self.notebook, bg="#F7FAFC", padx=12, pady=12)
        self.notebook.add(self.tab_insights, text="💡 Mood & Care Insights")
        self._build_insights_tab()

        # Tab 3: Tracker
        self.tab_tracker = tk.Frame(self.notebook, bg="#F7FAFC", padx=12, pady=12)
        self.notebook.add(self.tab_tracker, text="📝 Daily Tracker")
        self._build_tracker_tab()

        # Tab 4: Forecast
        self.tab_forecast = tk.Frame(self.notebook, bg="#F7FAFC", padx=12, pady=12)
        self.notebook.add(self.tab_forecast, text="📅 6-Month Forecast")
        self._build_forecast_tab()

        # Tab 5: Manage Profiles
        self.tab_profiles = tk.Frame(self.notebook, bg="#F7FAFC", padx=12, pady=12)
        self.notebook.add(self.tab_profiles, text="⚙️ Manage Profiles")
        self._build_profiles_tab()

    def _build_dashboard_tab(self):
        # Stats top row
        stats_frame = tk.Frame(self.tab_dash, bg="#F7FAFC")
        stats_frame.pack(fill="x", pady=(0, 12))

        self.dash_card_phase = self._create_stat_card(stats_frame, "CURRENT PHASE", "Follicular", "4 days remaining")
        self.dash_card_period = self._create_stat_card(stats_frame, "NEXT PERIOD", "In 14 Days", "Expected on --")
        self.dash_card_ov = self._create_stat_card(stats_frame, "OVULATION", "In 4 Days", "Fertile Window")

        self.dash_card_phase.pack(side="left", fill="x", expand=True, padx=4)
        self.dash_card_period.pack(side="left", fill="x", expand=True, padx=4)
        self.dash_card_ov.pack(side="left", fill="x", expand=True, padx=4)

        # Center Wheel
        center_frame = tk.Frame(self.tab_dash, bg="#FFFFFF", padx=16, pady=16, highlightthickness=1, highlightbackground="#E2E8F0")
        center_frame.pack(fill="x", pady=6)

        self.wheel_canvas = TkCycleCanvas(center_frame, size=240)
        self.wheel_canvas.pack(pady=4)

        # Care Banner
        self.care_banner = tk.Label(
            center_frame, text="Loading insights...", font=("Helvetica", 10),
            bg="#FAF5FF", fg="#6B46C1", padx=12, pady=10, wraplength=700, justify="left"
        )
        self.care_banner.pack(fill="x", pady=8)

    def _create_stat_card(self, parent, title: str, val: str, sub: str) -> tk.Frame:
        card = tk.Frame(parent, bg="#FFFFFF", padx=14, pady=10, highlightthickness=1, highlightbackground="#E2E8F0")
        lbl_t = tk.Label(card, text=title, font=("Helvetica", 8, "bold"), fg="#A0AEC0", bg="#FFFFFF")
        lbl_t.pack(anchor="w")
        lbl_v = tk.Label(card, text=val, font=("Helvetica", 14, "bold"), fg="#2D3748", bg="#FFFFFF")
        lbl_v.pack(anchor="w", pady=2)
        lbl_s = tk.Label(card, text=sub, font=("Helvetica", 9), fg="#718096", bg="#FFFFFF")
        lbl_s.pack(anchor="w")
        card.lbl_val = lbl_v
        card.lbl_sub = lbl_s
        return card

    def _build_insights_tab(self):
        scroll = tk.Canvas(self.tab_insights, bg="#F7FAFC", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_insights, orient="vertical", command=scroll.yview)
        inner = tk.Frame(scroll, bg="#F7FAFC")

        inner.bind("<Configure>", lambda e: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.create_window((0, 0), window=inner, anchor="nw", width=800)
        scroll.configure(yscrollcommand=scrollbar.set)

        scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.ins_partner = self._create_insight_block(inner, "💖 Partner Support Protocol", "")
        self.ins_mood = self._create_insight_block(inner, "🧠 Emotional & Psychological Landscape", "")
        self.ins_hormones = self._create_insight_block(inner, "🔬 Hormonal Activity", "")
        self.ins_physical = self._create_insight_block(inner, "🌿 Physical Sensations & Energy", "")
        self.ins_nutrition = self._create_insight_block(inner, "🥑 Nourishing Nutrition", "")

    def _create_insight_block(self, parent, title: str, text: str) -> tk.Label:
        card = tk.Frame(parent, bg="#FFFFFF", padx=16, pady=12, highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="x", pady=6)
        lbl_t = tk.Label(card, text=title, font=("Helvetica", 11, "bold"), fg="#8E54E9", bg="#FFFFFF")
        lbl_t.pack(anchor="w")
        lbl_b = tk.Label(card, text=text, font=("Helvetica", 10), fg="#2D3748", bg="#FFFFFF", wraplength=740, justify="left")
        lbl_b.pack(anchor="w", pady=(4, 0))
        return lbl_b

    def _build_tracker_tab(self):
        card = tk.Frame(self.tab_tracker, bg="#FFFFFF", padx=20, pady=16, highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Log Today's Mood & Symptoms", font=("Helvetica", 13, "bold"), bg="#FFFFFF", fg="#2D3748").pack(anchor="w")

        # Mood Score
        m_frame = tk.Frame(card, bg="#FFFFFF", pady=8)
        m_frame.pack(fill="x")
        tk.Label(m_frame, text="Mood (1-5):", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(side="left")
        self.var_mood = tk.IntVar(value=3)
        for val, em in [(1, "😢 1"), (2, "😕 2"), (3, "😐 3"), (4, "🙂 4"), (5, "🤩 5")]:
            tk.Radiobutton(m_frame, text=em, variable=self.var_mood, value=val, bg="#FFFFFF").pack(side="left", padx=6)

        # Sliders
        s_frame = tk.Frame(card, bg="#FFFFFF", pady=8)
        s_frame.pack(fill="x")
        tk.Label(s_frame, text="Energy (1-5):", bg="#FFFFFF").pack(side="left")
        self.tk_energy = ttk.Scale(s_frame, from_=1, to=5, orient="horizontal")
        self.tk_energy.set(3)
        self.tk_energy.pack(side="left", padx=10)

        tk.Label(s_frame, text="Cramps/Pain (0-5):", bg="#FFFFFF").pack(side="left", padx=(20, 0))
        self.tk_pain = ttk.Scale(s_frame, from_=0, to=5, orient="horizontal")
        self.tk_pain.set(0)
        self.tk_pain.pack(side="left", padx=10)

        # Symptoms
        tk.Label(card, text="Symptoms:", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(10, 4))
        sym_frame = tk.Frame(card, bg="#FFFFFF")
        sym_frame.pack(fill="x")
        self.tk_sym_vars = {}
        symptoms = ["Cramps", "Headache", "Bloating", "Tender Breasts", "Fatigue", "Sugar Cravings", "Mood Swings", "Clear Skin"]
        for idx, s in enumerate(symptoms):
            v = tk.BooleanVar()
            self.tk_sym_vars[s] = v
            tk.Checkbutton(sym_frame, text=s, variable=v, bg="#FFFFFF").grid(row=idx // 4, column=idx % 4, sticky="w", padx=8, pady=4)

        # Notes
        tk.Label(card, text="Notes:", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(10, 4))
        self.tk_notes = tk.Text(card, height=4, width=60, font=("Helvetica", 10))
        self.tk_notes.pack(fill="x", pady=4)

        # Save Button
        btn = tk.Button(card, text="💾 Save Today's Log", font=("Helvetica", 10, "bold"), bg="#8E54E9", fg="white", padx=14, pady=6, command=self._on_save_log_clicked)
        btn.pack(anchor="e", pady=10)

    def _build_forecast_tab(self):
        card = tk.Frame(self.tab_forecast, bg="#FFFFFF", padx=16, pady=16, highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="both", expand=True)

        tk.Label(card, text="📅 Upcoming 6-Month Projections", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#2D3748").pack(anchor="w", pady=(0, 10))
        self.txt_forecast = tk.Text(card, height=18, font=("Courier", 10), bg="#F8FAFC", relief="flat")
        self.txt_forecast.pack(fill="both", expand=True)

    def _build_profiles_tab(self):
        card = tk.Frame(self.tab_profiles, bg="#FFFFFF", padx=20, pady=20, highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Profile Configuration", font=("Helvetica", 13, "bold"), bg="#FFFFFF", fg="#2D3748").pack(anchor="w", pady=(0, 12))

        tk.Label(card, text="Profile Name:", bg="#FFFFFF").pack(anchor="w")
        self.entry_name = ttk.Entry(card, width=30)
        self.entry_name.pack(anchor="w", pady=4)

        tk.Label(card, text="Last Period Start Date (YYYY-MM-DD):", bg="#FFFFFF").pack(anchor="w", pady=(8, 0))
        self.entry_date = ttk.Entry(card, width=30)
        self.entry_date.pack(anchor="w", pady=4)

        tk.Label(card, text="Period Duration (days):", bg="#FFFFFF").pack(anchor="w", pady=(8, 0))
        self.entry_dur = ttk.Entry(card, width=30)
        self.entry_dur.pack(anchor="w", pady=4)

        tk.Label(card, text="Cycle Length (days):", bg="#FFFFFF").pack(anchor="w", pady=(8, 0))
        self.entry_cyc = ttk.Entry(card, width=30)
        self.entry_cyc.pack(anchor="w", pady=4)

        btn_box = tk.Frame(card, bg="#FFFFFF", pady=16)
        btn_box.pack(anchor="w")

        tk.Button(btn_box, text="Save / Update", bg="#8E54E9", fg="white", font=("Helvetica", 10, "bold"), command=self._on_save_profile_clicked).pack(side="left", padx=4)
        tk.Button(btn_box, text="New Blank Profile", bg="#EDF2F7", fg="#2D3748", command=self._on_new_profile_clicked).pack(side="left", padx=4)
        tk.Button(btn_box, text="Delete Profile", bg="#E53E3E", fg="white", command=self._on_delete_profile_clicked).pack(side="left", padx=4)

    def _on_profile_selected(self, _):
        selected = self.profile_var.get().lower()
        if selected in self.profiles:
            self.current_profile = self.profiles[selected]
            self._refresh_ui()

    def _on_save_log_clicked(self):
        if not self.current_profile:
            messagebox.showwarning("Warning", "Select a profile first.")
            return
        selected_symptoms = [s for s, var in self.tk_sym_vars.items() if var.get()]
        notes = self.tk_notes.get("1.0", "end-1c").strip()
        log = DailyLog(
            log_date=date.today(),
            mood_score=self.var_mood.get(),
            energy_score=int(self.tk_energy.get()),
            pain_level=int(self.tk_pain.get()),
            symptoms=selected_symptoms,
            notes=notes
        )
        self.storage.log_daily_entry(self.current_profile.name, log)
        self.profiles = self.storage.load_profiles()
        self.current_profile = self.profiles[self.current_profile.name.lower()]
        messagebox.showinfo("Saved", "Today's mood and symptoms saved successfully!")

    def _on_save_profile_clicked(self):
        name = self.entry_name.get().strip()
        date_str = self.entry_date.get().strip()
        if not name or not date_str:
            messagebox.showerror("Error", "Name and Start Date are required.")
            return
        try:
            p_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            dur = int(self.entry_dur.get().strip())
            cyc = int(self.entry_cyc.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid date (YYYY-MM-DD) or duration numbers.")
            return

        key = name.lower()
        existing = self.profiles.get(key)
        prof = Profile(
            name=name,
            last_period_start_date=p_date,
            period_duration=dur,
            cycle_length=cyc,
            history=existing.history if existing else [],
            daily_logs=existing.daily_logs if existing else {}
        )
        self.storage.save_profile(prof)
        self.profiles = self.storage.load_profiles()
        self.current_profile = self.profiles[key]
        self._refresh_ui()
        messagebox.showinfo("Success", f"Profile '{name}' saved!")

    def _on_new_profile_clicked(self):
        self.entry_name.delete(0, "end")
        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_dur.delete(0, "end")
        self.entry_dur.insert(0, "5")
        self.entry_cyc.delete(0, "end")
        self.entry_cyc.insert(0, "28")

    def _on_delete_profile_clicked(self):
        name = self.entry_name.get().strip().lower()
        if name in self.profiles:
            if messagebox.askyesno("Confirm", f"Delete profile '{name}'?"):
                self.storage.delete_profile(name)
                self.profiles = self.storage.load_profiles()
                self.current_profile = next(iter(self.profiles.values())) if self.profiles else None
                self._refresh_ui()

    def _refresh_ui(self):
        names = list(self.profiles.keys())
        self.combo_profile["values"] = [n.title() for n in names]
        if self.current_profile:
            self.profile_var.set(self.current_profile.name.title())
            p = self.current_profile

            # Form fields
            self.entry_name.delete(0, "end")
            self.entry_name.insert(0, p.name.title())
            self.entry_date.delete(0, "end")
            self.entry_date.insert(0, p.last_period_start_date.strftime("%Y-%m-%d"))
            self.entry_dur.delete(0, "end")
            self.entry_dur.insert(0, str(p.period_duration))
            self.entry_cyc.delete(0, "end")
            self.entry_cyc.insert(0, str(p.cycle_length))

            phase = CycleCalculator.calculate_phase(p.last_period_start_date, p.period_duration, p.cycle_length)
            milestones = CycleCalculator.get_cycle_milestones(p.last_period_start_date, p.period_duration, p.cycle_length)

            # Dashboard
            self.dash_card_phase.lbl_val.config(text=phase.phase_name.split("(")[0].strip())
            self.dash_card_phase.lbl_sub.config(text=f"{phase.days_remaining_in_phase} days remaining")
            days_p = milestones["days_until_next_period"]
            self.dash_card_period.lbl_val.config(text=f"In {days_p} Days")
            self.dash_card_period.lbl_sub.config(text=f"Due {milestones['next_period_date'].strftime('%b %d')}")
            days_ov = milestones["days_until_ovulation"]
            self.dash_card_ov.lbl_val.config(text=f"In {days_ov} Days" if days_ov > 0 else "Luteal Phase")

            self.wheel_canvas.update_data(phase.day_in_cycle, phase.cycle_length, p.period_duration, phase.phase_color, phase.phase_name)
            self.care_banner.config(text=f"💡 How to support {p.name.title()} today:\n{phase.care_tip_for_partner}")

            # Insights
            self.ins_partner.config(text=phase.care_tip_for_partner)
            self.ins_mood.config(text=phase.mood_summary)
            self.ins_hormones.config(text=phase.hormone_status)
            self.ins_physical.config(text=phase.physical_summary)
            self.ins_nutrition.config(text=phase.nutrition_tip)

            # Forecast
            projs = CycleCalculator.get_future_projections(p.last_period_start_date, p.period_duration, p.cycle_length)
            f_text = f"{'Cycle':<8}{'Period Start':<16}{'Period End':<16}{'Ovulation Date':<16}\n" + "-" * 56 + "\n"
            for pr in projs:
                f_text += f"#{pr['cycle_index']:<7}{str(pr['period_start']):<16}{str(pr['period_end']):<16}{str(pr['ovulation_date']):<16}\n"
            self.txt_forecast.delete("1.0", "end")
            self.txt_forecast.insert("1.0", f_text)

    def run(self) -> int:
        self.root.mainloop()
        return 0
