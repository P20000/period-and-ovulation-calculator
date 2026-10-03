# 🌸 Cycle & Mood Tracker (Cross-Platform)

An intelligent, scientific cycle and mood tracker with relationship care guidance, built with a modern **GTK4 / Libadwaita** native interface and adaptive **cross-platform fallback** (Windows, macOS, Linux).

---

## ✨ Features

- **🎨 Modern Visual Cycle Wheel**: Interactive circular dial (rendered with Cairo / Canvas) displaying cycle progress, phase boundaries, and a live day pointer.
- **🧠 Deep Mood & Emotional Forecasting**: Scientific insights into hormonal fluctuations (Estrogen, Progesterone, LH) and emotional states across all 5 cycle phases.
- **💖 Partner Care Protocols**: Actionable guidance for partners on how to best support, nourish, and care for her each day.
- **📝 Daily Symptom & Mood Logger**: Track mood ratings (1–5), energy levels, cramps/pain intensity, common symptoms, and personal journal notes.
- **📅 6-Month Cycle & Ovulation Forecast**: Detailed projections of future periods, fertile windows, and estimated ovulation dates.
- **👤 Multi-Profile Management**: Seamlessly add, edit, switch, or delete profiles.
- **💾 Safe & Atomic Storage**: Backward-compatible JSON storage with atomic writes, automated `.bak` backups, and schema evolution.
- **🌍 Adaptive Cross-Platform Architecture**: Detects runtime OS and toolkits:
  - **Linux (GNOME / Wayland / X11)**: Native GTK4 + Libadwaita UI with dark/light mode toggle and Adwaita styling.
  - **Windows / macOS / Systems without GTK**: Automated fallback to clean Tkinter / ttk notebook UI with full feature parity.

---

## 🏛️ Modular OOP Architecture

All files are strictly kept under **500 lines of code** with clean separation of concerns:

```
├── main.py                     # Entry point & dynamic backend selector
├── app.py                      # Backwards-compatible alias launcher
├── core/
│   ├── models.py               # Profile, CycleRecord, DailyLog, PhaseInfo dataclasses
│   ├── calculator.py           # Scientific phase math & mood generation algorithms
│   ├── storage.py              # Safe atomic JSON repository & automated backup
│   └── platform_detector.py    # Runtime OS, desktop, and GUI toolkit detector
├── ui/
│   ├── base.py                 # Abstract base application interface
│   ├── gtk/                    # Native GTK4 & Libadwaita UI
│   │   ├── app.py              # Adw.Application lifecycle & CSS provider
│   │   ├── window.py           # MainWindow with ViewStack & ViewSwitcher
│   │   ├── dashboard_view.py   # Overview, stat cards, & quick actions
│   │   ├── cycle_canvas.py     # Cairo anti-aliased circular cycle dial
│   │   ├── insights_view.py    # Hormones, emotions, nutrition & care tips
│   │   ├── tracker_view.py     # Daily symptom & mood log form
│   │   ├── history_view.py     # 6-month projections & log timeline
│   │   ├── profiles_dialog.py  # Profile CRUD modal dialog
│   │   └── style.css           # Custom CSS theme accents
│   └── tk_fallback/            # Universal Tkinter fallback backend
│       ├── app.py              # Cross-platform Tkinter/ttk application
│       └── cycle_canvas.py     # Tkinter Canvas circular wheel
```

---

## 🚀 Quick Start

### 1. Requirements

Install required dependencies:

```bash
pip install -r requirements.txt
```

- **Linux**: Standard system PyGObject (`sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1`)
- **Windows / macOS**: Built-in standard `tkinter` works out-of-the-box!

### 2. Running the Application

```bash
# Auto-detect and launch the best UI for your system:
python3 main.py

# Or inspect your system diagnostics:
python3 main.py --info

# Or explicitly choose a backend:
python3 main.py --backend gtk      # GTK4 / Libadwaita
python3 main.py --backend tkinter  # Tkinter Cross-Platform Fallback
```

---

## 📋 Architectural Guidelines & Rules

- **Code Limit**: Strict maximum of 500 lines per file (enforced in `AGENTS.md` and `.agents/rules/code_limits.md`).
- **Encapsulation**: Domain models, storage operations, and calculation math are fully decoupled from UI widgets.
