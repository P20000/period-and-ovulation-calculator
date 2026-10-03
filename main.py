#!/usr/bin/env python3
"""
Cycle & Mood Tracker - Cross-Platform GTK4 / Libadwaita Application with Adaptive Fallback.
Detects operating system environment and dynamically launches the optimal UI architecture.
"""

import argparse
import sys
from core import PlatformDetector, PlatformInfo, StorageManager
from core.platform_detector import BackendType


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cycle & Mood Tracker - Modern Cross-Platform Health & Relationship Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Adaptability:
  Linux (GNOME/Wayland/X11) -> Native GTK4 / Libadwaita UI
  Windows / macOS / Other  -> Cross-Platform Tkinter Fallback UI
        """
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "gtk", "gtk4", "adw", "tk", "tkinter"],
        default="auto",
        help="Force a specific UI backend (default: auto-detect)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print detected platform and toolkit diagnostic info, then exit",
    )
    parser.add_argument(
        "--data-file",
        default="girlfriend_data.json",
        help="Path to JSON data storage file (default: girlfriend_data.json)",
    )

    args = parser.parse_args()

    # 1. Environment & Toolkit Detection
    force_choice = None if args.backend == "auto" else args.backend
    platform_info: PlatformInfo = PlatformDetector.detect(force_backend=force_choice)

    if args.info:
        print("=== System & Toolkit Diagnostics ===")
        print(f"OS:                 {platform_info.os_name} ({platform_info.os_release}) [{platform_info.architecture}]")
        print(f"Desktop/Display:    {platform_info.desktop_env} ({platform_info.display_server})")
        print(f"Python Version:     {platform_info.python_version}")
        print(f"GTK4 / Libadwaita:  {'Available' if platform_info.has_gtk4_adw else 'Not Available'}")
        print(f"GTK3:               {'Available' if platform_info.has_gtk3 else 'Not Available'}")
        print(f"Tkinter:            {'Available' if platform_info.has_tkinter else 'Not Available'}")
        print(f"Selected Backend:   {platform_info.recommended_backend.value}")
        return 0

    print(f"[*] {platform_info.summary()}")

    storage = StorageManager(file_path=args.data_file)

    # 2. Dynamic Backend Architecture Loader
    if platform_info.recommended_backend in (BackendType.GTK4_ADWAITA, BackendType.GTK3):
        try:
            from ui.gtk import GtkApp
            app = GtkApp(storage=storage)
            return app.run(sys.argv)
        except Exception as e:
            print(f"[!] Warning: Failed to launch GTK4 backend: {e}")
            print("[*] Falling back to Cross-Platform Tkinter interface...")
            from ui.tk_fallback import TkApp
            app = TkApp(storage=storage)
            return app.run()

    elif platform_info.recommended_backend in (BackendType.CUSTOM_TKINTER, BackendType.TKINTER):
        from ui.tk_fallback import TkApp
        app = TkApp(storage=storage)
        return app.run()

    else:
        print("[!] Error: No compatible GUI toolkit found on this system.")
        print("    Please install PyGObject (`python3 -m pip install PyGObject`) or standard python3-tk.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
