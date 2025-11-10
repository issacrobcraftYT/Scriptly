import os
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / 'assets' / 'images'
DEFAULT_FILE = ASSETS_DIR / 'file.svg'
DEFAULT_FOLDER = ASSETS_DIR / 'folder.svg'
DEFAULT_LANG = ASSETS_DIR / 'language.svg'

# Known extensions mapping to svg names base (without .svg)
EXT_MAP = {
    'py': 'py',
    'js': 'js',
    'html': 'html',
    'css': 'css',
    'md': 'md',
    'txt': 'file',
    'java': 'java',
    'cpp': 'cpp',
    'rb': 'rb',
    'sh': 'sh',
    'sql': 'sql',
    'json': 'json',
    'xml': 'xml',
    'yml': 'yml',
    'yaml': 'yml'
}


def find_icon_for_path(path: str, size: int = 64):
    p = Path(path)
    if p.is_dir():
        # Look for folder.svg with same name
        candidate = ASSETS_DIR / f"{p.name}.svg"
        if candidate.exists():
            return str(candidate)
        return str(DEFAULT_FOLDER)

    # file
    ext = p.suffix.lower().lstrip('.')
    if not ext:
        return str(DEFAULT_FILE)
    # map known ext
    key = EXT_MAP.get(ext, None)
    if key:
        candidate = ASSETS_DIR / f"{key}.svg"
        if candidate.exists():
            return str(candidate)
        else:
            return str(DEFAULT_LANG)
    else:
        # fallback to language.svg
        candidate = ASSETS_DIR / f"{ext}.svg"
        if candidate.exists():
            return str(candidate)
        return str(DEFAULT_LANG)


if __name__ == '__main__':
    test_paths = [
        'README.md',
        'src/main.py',
        'styles/theme.qss',
        'scripts',
        'unknown.xyz'
    ]
    for t in test_paths:
        print(t, '->', find_icon_for_path(t))
