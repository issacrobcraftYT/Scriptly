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
    - Registered theme name is the file stem (e.g. `dark`, `modern_dark`).
    """
    def __init__(self):
        self.themes: dict[str, Theme] = {}
        self.current_theme: str | None = None
        self._load_themes()

    def _load_themes(self):
        """Load themes from disk, enforcing modern_dark as the only theme."""
        base = Path(__file__).parent / 'themes'
        if not base.exists():
            return
        
        # Only load modern_dark theme
        qss_path = base / 'modern_dark.qss'
        if not qss_path.exists():
            raise FileNotFoundError("Required theme file modern_dark.qss not found")
            
        # Load required modern dark theme
        json_path = qss_path.with_suffix('.json')
        colors = None

        # Try to load color hints from JSON
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as jf:
                    colors = json.load(jf)
            except Exception as e:
                print(f"Error loading theme colors: {e}")
                colors = None
                
        # Register the modern dark theme
        self.themes['modern_dark'] = Theme('modern_dark', qss_path, colors)
        self.current_theme = 'modern_dark'  # Always use modern_dark

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