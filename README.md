<div align="center">

# 🌙 Scriptly  
### A modern, minimal & customizable code editor built with Python + PyQt6  

![Scriptly Logo](https://i.imgur.com/ABCD123.png) 

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg)]()

</div>

---

## Features

- File Operations
  - Open and edit various file types (.txt, .lua, .py, .js, etc.)
  """
  # Scriptly — Lightweight, extensible Python editor

  Welcome to Scriptly. This README is intended to be a complete reference for users and contributors. It explains the architecture, how to run and develop the app, and how the theming system works (including step-by-step instructions for adding new themes). If you plan to publish this project on GitHub, this document will be the canonical entry point for newcomers.

  ---

  ## Table of contents

  - Overview
  - Quick start (run locally)
  - Project structure
  - UI and theming system
    - Where themes live
    - Included theme files: `dark.qss` and `modern_dark.qss`
    - Theme JSON color hints
    - How ThemeManager discovers and applies themes
    - Best practices for theme authors
  - Editor integration and lexers
  - Settings and persistence
  - Development workflow
    - Running the app
    - Formatting and linting
    - Tests
  - Packaging
  - Contributing (high level — see CONTRIBUTING.md for details)
  - License and attribution

  ---

  ## Overview

  Scriptly is a lightweight editor built with PyQt6 and QScintilla. The goals are:

  - Minimal, modern UI with strong dark theme first design
  - Easy theming by community contributors (file-based themes)
  - Maintainable, readable codebase that is easy to extend

  Recent updates focus on consolidating the design to a dark-only experience and providing a simple, file-based theme system so contributors can add or modify themes without touching Python code.

  ---

  ## Quick start (run locally)

  Requirements
  - Python 3.10+ (recommended)
  - PyQt6
  - QScintilla (PyQt6 Qsci)

  Install dependencies (example; adapt to your platform):

  ```powershell
  python -m pip install -r requirements.txt
  ```

  Run the app:

  ```powershell
  python src/main.py
  ```

  If you see import errors, confirm PyQt6 and QScintilla are installed in the same interpreter used to run `python`.

  ---

  ## Project structure

  Key folders and files (short):

  - `src/` — application source code
    - `core/` — core services (settings, theming, file monitor, completion)
      - `themes/` — QSS theme files and optional JSON color hints
        - `dark.qss` — included dark theme (refined)
        - `modern_dark.qss` — included modern dark theme (flat/clean)
        - `dark.json`, `modern_dark.json` — optional color hints for the editor
    - `ui/` — Qt widgets and UI components (main window, editor widget, dialogs)
    - `main.py` — app entry point

  Other top-level files:
  - `README.md` — this file
  - `CONTRIBUTING.md` — contributor guidelines
  - `requirements.txt` — Python package dependencies

  ---

  ## UI and theming system

  Scriptly separates the visual presentation (QSS) from editor token colors (JSON hints). This makes theme files easy to write and preview, and also keeps the program code simple.

  ### Where themes live

  All themes live in: `src/core/themes/`

  Each theme is composed of:

  - A QSS file: `my_theme.qss` — controls Qt widget styling (menus, tabs, buttons, dialogs, scrollbars, etc.).
  - An optional JSON color hint file: `my_theme.json` — provides a `colors` dictionary used by the `EditorWidget` to set QScintilla colors (paper, foreground, selection, caret line, token hints).

  The app ships with two theme QSS files included in that directory: `dark.qss` and `modern_dark.qss`. Companion JSON color hint files (`dark.json`, `modern_dark.json`) are included to provide editor color hints.

  ### How ThemeManager works

  `src/core/theme_manager.py` implements a tiny discovery system:

  - On initialization it scans `src/core/themes/` for `*.qss` files.
  - For each `X.qss`, a `Theme` object is created and registered under the name `X` (the filename stem).
  - If a companion `X.json` exists, it is loaded and attached as `Theme.colors` (a dict). These values are consumed by `EditorWidget` when configuring QScintilla.

  Public API (internal usage):

  - `ThemeManager.get_theme_names()` — returns available theme names (e.g. `['dark', 'modern_dark']`).
  - `ThemeManager.get_current_theme()` — returns the active `Theme` object (call `get_stylesheet()` to get QSS and inspect `Theme.colors` for hints).
  - `ThemeManager.set_theme(name)` — set the active theme.

  This file-based approach allows themes to be added by simply creating files in `src/core/themes`.

  ### Included themes

  - `dark.qss` — a refined dark theme with slightly bluish accents. Suitable as the default.
  - `modern_dark.qss` — a modern flat dark theme that emphasizes clean tab/bar styling.

  Both themes include matching JSON color hint files (`dark.json`, `modern_dark.json`) so the editor widget can use consistent colors for line numbers, caret line, and selection.

  ### Adding a new theme — step-by-step

  1. Create a qss: `src/core/themes/my_theme.qss`.
     - Use only Qt style selectors (QMainWindow, QMenuBar, QTabBar, QDialog, QPushButton, QScrollBar, QsciScintilla, etc.).
     - Keep the rules broad and avoid referencing images or external resources unless they live in the `themes/` directory.

  2. (Optional) Create color hints JSON: `src/core/themes/my_theme.json`.
     - Provide a JSON object with keys the editor expects. Example keys (recommended):

  ```json
  {
    "name": "my_theme",
    "editor_background": "#0f1720",
    "editor_foreground": "#e6eef6",
    "editor_selection": "#0ea5e9",
    "editor_line": "#12202a",
    "line_number": "#858585",
    "keyword": "#61aeee",
    "string": "#ecc48d",
    "comment": "#6aa97b"
  }
  ```

  3. Restart the app. `ThemeManager` will discover the `.qss` file and load the JSON (if present).

  4. If you want to iterate quickly while designing a theme, keep the app running and use a small Python helper (we can add one) to reload and apply a QSS file dynamically.

  ### Theme best practices

  - Keep QSS focused on general widgets and layout. Editor token colorization is controlled by lexers in Python (via `EditorWidget`); use JSON hints to align the editor palette with your QSS.
  - Use semantic JSON keys (editor_background, editor_foreground, etc.).
  - Avoid hard-coded pixel-perfect rules that make a theme brittle across platforms.
  - Check contrast and accessibility (text against background) — aim for good readability.

  ---

  ## Editor integration and lexers

  The editor is a `QsciScintilla` derived widget with per-language lexers. `EditorWidget` consults the current theme's `colors` dictionary (if present) to set:
  - Paper/background color
  - Foreground color
  - Selection background
  - Caret line highlight
  - Line numbers color

  Language token colors (keyword/string/comment) from the JSON are used as hints when configuring lexers, but lexers themselves still control most token styling.

  If a theme JSON is not present, the editor uses sensible defaults.

  ---

  ## Settings and persistence

  App settings are managed via Qt `QSettings` and wrapped in `src/core/settings.py`. Settings persisted include:

  - Editor font family and size
  - Tab width and indentation preferences
  - Auto-save configuration
  - Last open files and workspace layout (where supported)

  The Settings dialog exposes a Reset to Defaults button as well as save/apply behavior.

  ---

  ## Development workflow

  ### Run the app

  ```powershell
  python -m pip install -r requirements.txt
  python src/main.py
  ```

  ### Formatting and linting

  We recommend `black` and `flake8` for consistent style:

  ```powershell
  python -m pip install black flake8
  black .
  flake8 src
  ```

  ### Tests

  There is no test-suite included yet. If you add features, please include unit tests where appropriate and update this README.

  ### Packaging

  You can use PyInstaller to create a bundled executable. Example:

  ```powershell
  pyinstaller --name Scriptly --onefile src/main.py
  ```

  Packaging for each platform (Windows/macOS/Linux) will require platform-specific packaging conventions and testing.

  ---

  ## CONTRIBUTING

  We welcome contributions. Please read `CONTRIBUTING.md` for guidelines on PRs, code style, and theme submissions.

  ---

  ## License

  Add a `LICENSE` file to the repository root (MIT / Apache-2.0 are common choices). If you plan to publish on GitHub, include a license file so contributors know how their contributions will be licensed.

  ---

  If you'd like, I can also:
  - Add a small `scripts/preview_theme.py` helper that loads a theme QSS and shows a preview window for rapid iteration.
  - Add a CLI flag to `src/main.py` to load a specific QSS at startup (useful for theme designers).

  Which of those would you like next?

  """