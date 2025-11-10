import sys
import os
from pathlib import Path
import json
from typing import Dict, Optional

def resource_path(relative_path: str) -> str:
    """Devuelve ruta válida tanto en ejecución normal como compilada."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Theme:
    """Represents a theme discovered on disk.

    Attributes:
        name: canonical theme name (filename stem)
        path: Path to the QSS file
        colors: optional dict loaded from a companion JSON file (if present)
    """

    def __init__(self, name: str, path: Path, colors: Optional[Dict] = None):
        self.name = name
        self.path = Path(path)
        self._stylesheet: Optional[str] = None
        self.colors: Dict = colors or {}

    def get_stylesheet(self) -> str:
        if self._stylesheet is None:
            if not self.path.exists():
                raise FileNotFoundError(f"Theme file not found: {self.path}")
            with open(self.path, "r", encoding="utf-8") as f:
                self._stylesheet = f.read()
        return self._stylesheet


class ThemeManager:
    """Loads themes from `src/core/themes/` and exposes them.

    Behavior:
    - Scans the `themes` directory for `*.qss` files.
    - For each `X.qss` it will look for an optional `X.json` to load a `colors` dict.
    - Prefers `modern_dark` as the default if present, otherwise picks the first discovered.
    """

    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[str] = None
        self.active_color_scheme = None
        self._load_themes()
        self._init_color_schemes()

    def _init_color_schemes(self):
        """Initialize predefined color schemes for syntax highlighting."""
        self.color_schemes = {
            'default': {
                'background': '#2b2b2b',
                'foreground': '#a9b7c6',
                'keywords': '#cc7832',
                'strings': '#6a8759',
                'comments': '#808080',
                'numbers': '#6897bb',
                'functions': '#ffc66d',
                'classes': '#a9b7c6',
                'operators': '#cc7832',
                'brackets': '#a9b7c6',
                'selection_bg': '#214283',
                'current_line': '#323232'
            },
            'light': {
                'background': '#ffffff',
                'foreground': '#000000',
                'keywords': '#0033b3',
                'strings': '#067d17',
                'comments': '#8c8c8c',
                'numbers': '#1750eb',
                'functions': '#00627a',
                'classes': '#000000',
                'operators': '#0033b3',
                'brackets': '#000000',
                'selection_bg': '#add6ff',
                'current_line': '#f5f5f5'
            }
        }
        self.active_color_scheme = 'default'

    def _load_themes(self):
        """Discover and load all available .qss themes, prefer modern_dark as default."""
        # Look for themes in multiple locations
        theme_paths = [
            Path(__file__).parent / "themes",  # Built-in themes
            Path("themes"),  # Themes in application directory
            Path.home() / ".scriptly" / "themes",  # User custom themes
            Path.home() / ".scriptly" / "themes"  # User themes
        ]
        
        for base in theme_paths:
            if not base.exists():
                continue

        # Discover all .qss files
        for qss in sorted(base.glob("*.qss")):
            name = qss.stem
            json_path = qss.with_suffix(".json")
            colors = None
            if json_path.exists():
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        colors = json.load(jf)
                except Exception as e:
                    # non-fatal; continue without colors
                    print(f"Warning: failed to load colors for theme {name}: {e}")
                    colors = None
            self.themes[name] = Theme(name, qss, colors)

        # Prefer modern_dark if present, otherwise first theme
        if "modern_dark" in self.themes:
            self.current_theme = "modern_dark"
        elif self.themes:
            self.current_theme = next(iter(self.themes))

    def reload(self):
        """Reload themes from disk (useful during development/design)."""
        self.themes.clear()
        self.current_theme = None
        self._load_themes()

    def get_current_theme(self) -> Theme:
        if not self.current_theme:
            raise RuntimeError("No theme loaded")
        return self.themes[self.current_theme]

    def set_theme(self, theme_name: str):
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            raise KeyError(f"Unknown theme: {theme_name}")

    def get_theme_names(self) -> list[str]:
        return list(self.themes.keys())

    def write_theme(self, name: str, qss: str, colors: Optional[Dict] = None) -> Theme:
        """Create or overwrite a theme files (qss + optional json) in the themes folder.

        Returns the created Theme object.
        """
        base = Path(resource_path("src/core/themes"))
        base.mkdir(parents=True, exist_ok=True)
        safe_name = name.strip().replace(" ", "_")
        qss_path = base / f"{safe_name}.qss"
        json_path = base / f"{safe_name}.json"
        with open(qss_path, "w", encoding="utf-8") as f:
            f.write(qss)
        if colors is not None:
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(colors, jf, indent=2)
        # reload themes and return the Theme
        self.reload()
        return self.themes[safe_name]


class DesignManager:
    """High-level helper for theme authors to scaffold and preview themes.

    This manager is intentionally small and file-based: it creates a QSS template and
    a JSON color hints file that authors can edit. It uses ThemeManager internally.
    """

    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        self.tm = theme_manager or ThemeManager()

    def scaffold_theme(self, name: str) -> Theme:
        """Create a new theme scaffold (qss + json) if it doesn't exist and return it."""
        if name in self.tm.themes:
            return self.tm.themes[name]

        qss_template = (
            "/* New Scriptly theme: %s */\n"
            "QMainWindow { background-color: #1a1f25; }\n"
            "QMenuBar { color: #e6eef6; }\n"
            "QsciScintilla { background-color: #151a20; }\n"
        ) % name

        colors_template = {
            "name": name,
            "editor_background": "#151a20",
            "editor_foreground": "#e6eef6",
            "editor_selection": "#264F78",
            "editor_line": "#2A2A2A",
            "line_number": "#8ba1b5",
            "keyword": "#C586C0",
            "string": "#CE9178",
            "comment": "#6A9955",
        }

        return self.tm.write_theme(name, qss_template, colors_template)

import os
import json
from pathlib import Path


class Theme:
    """Represents a theme discovered on disk.

    Attributes:
        name: canonical theme name (filename stem)
        path: Path to the QSS file
        colors: optional dict loaded from a companion JSON file (if present)
    """
    def __init__(self, name: str, path: Path, colors: dict | None = None):
        self.name = name
        self.path = Path(path)
        self._stylesheet: str | None = None
        self.colors = colors or {}

    def get_stylesheet(self) -> str:
        if self._stylesheet is None:
            if not self.path.exists():
                raise FileNotFoundError(f"Theme file not found: {self.path}")
            with open(self.path, 'r', encoding='utf-8') as f:
                self._stylesheet = f.read()
        return self._stylesheet


class ThemeManager:
    """Loads themes from `src/core/themes/` and exposes them.

    Behavior:
    - Scans the `themes` directory for `*.qss` files.
    - For each `X.qss` it will look for an optional `X.json` to load a `colors` dict.
    - Prefers `modern_dark` as the default if present, otherwise picks the first discovered.
    """
    def __init__(self):
        self.themes: dict[str, Theme] = {}
        self.current_theme: str | None = None
        self._load_themes()

    def _load_themes(self):
        """Discover and load all available .qss themes, prefer modern_dark as default."""
    
        # función que resuelve la ruta compatible con PyInstaller
        def resource_path(relative_path: str) -> str:
            import sys, os
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        # detecta todas las posibles ubicaciones
        possible_dirs = [
            Path(resource_path("src/core/themes")), 
            Path(resource_path("core/themes")),   
            Path(resource_path("themes")),      
        ]

        base = None
        for d in possible_dirs:
            if d.exists():
                base = d
                break

        if base is None:
            return

        # carga los temas
        for qss in sorted(base.glob("*.qss")):
            name = qss.stem
            json_path = qss.with_suffix(".json")
            colors = None
            if json_path.exists():
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        colors = json.load(jf)
                except Exception as e:
                    print(f"Warning: failed to load colors for theme {name}: {e}")
            self.themes[name] = Theme(name, qss, colors)

        # establece el tema actual
        if "modern_dark" in self.themes:
            self.current_theme = "modern_dark"
        elif self.themes:
            self.current_theme = next(iter(self.themes))
        else:+
            print("⚠️ No themes found at runtime.")

    def get_current_theme(self) -> Theme:
        if not self.current_theme:
            raise RuntimeError('No theme loaded')
        return self.themes[self.current_theme]

    def set_theme(self, theme_name: str):
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            raise KeyError(f"Unknown theme: {theme_name}")

    def get_theme_names(self) -> list[str]:
        return list(self.themes.keys())
