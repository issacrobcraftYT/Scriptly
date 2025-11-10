import os
try:
    # import from centralized metadata
    from app_metadata import get_version
except Exception:
    # fallback
    def get_version(prepend_v=False):
        return "0.0.0"


def get_app_version(prepend_v=False):
    """Return the app version from centralized metadata."""
    return get_version(prepend_v=prepend_v)


def read_text_file(path):
    """Read text file contents (utf-8). Returns None on error."""
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return fh.read()
    except Exception:
        return None


def write_text_file(path, content):
    """Write text file contents (utf-8). Returns True on success."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    try:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
        return True
    except Exception:
        return False
