# Code Standards and Architecture Rules

## 1. File Size Limit (STRICT)
- **Maximum 500 lines of code per file**: No single source code file (`.py`, `.js`, etc.) may exceed 500 lines of code.
- If a file approaches 400 lines, it must be modularized and broken down into smaller, single-responsibility components or helper modules.

## 2. Object-Oriented Programming (OOP) & Encapsulation
- Use domain models (dataclasses/classes) for data representation.
- Encapsulate data access and business logic into dedicated managers and services (e.g. `StorageManager`, `CycleCalculator`, `MoodEngine`).
- Keep UI components separated from business logic through clean view-controller / observer patterns.

## 3. Modular File Organization
- Organize code by domain and responsibility into clear subpackages (e.g., `core/`, `ui/gtk/`, `ui/tk_fallback/`).
- Separate views, custom drawing widgets, dialogs, and platform adaptations into distinct files.

## 4. Cross-Platform Adaptability
- Detect the operating system (Linux, macOS, Windows) and environment at runtime.
- Seamlessly adapt UI backends (Modern GTK4/Libadwaita where available, with graceful fallback to standard Tkinter on systems lacking PyGObject).
- Ensure file paths, data persistence, and date parsing work identically across all operating systems.

## 5. Efficient Data Storage & Safety
- Implement robust, backward-compatible serialization with schema migrations.
- Ensure atomic writes and safe backups to avoid data corruption.
