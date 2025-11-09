"""Utility functions for console output with colors.

This module uses colorama when available to print colored messages. If
colorama is not installed or cannot be initialized, the functions fall back
to plain text output so the app still logs useful messages.
"""

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    _HAS_COLORAMA = True
except Exception:
    # colorama not available; provide ANSI escape sequences as a fallback
    _HAS_COLORAMA = False
    ANSI_RESET = "\x1b[0m"
    class _AnsiFore:
        CYAN = "\x1b[36m"
        GREEN = "\x1b[32m"
        YELLOW = "\x1b[33m"
        RED = "\x1b[31m"
        BLUE = "\x1b[34m"
        MAGENTA = "\x1b[35m"
        LIGHTCYAN_EX = "\x1b[96m"
        WHITE = "\x1b[37m"
    class _AnsiBack:
        BLUE = "\x1b[44m"
    class _AnsiStyle:
        RESET_ALL = ANSI_RESET

    Fore = _AnsiFore()
    Back = _AnsiBack()
    Style = _AnsiStyle()
import sys


def _supports_color() -> bool:
    """Return True if the current stdout is likely to support ANSI colors.
    We prefer colorama when available, otherwise fall back to isatty detection.
    """
    try:
        if _HAS_COLORAMA:
            return True
        # if stdout is a tty, many modern terminals support ANSI
        return sys.stdout.isatty()
    except Exception:
        return False


def _fmt(tag: str, color: str, msg: str) -> str:
    # If colors are not supported in this environment, return a plain tagged message
    if not _supports_color():
        return f"[{tag}] {msg}"
    return f"{color}[{tag}] {msg}{Style.RESET_ALL}"


def info(msg: str):
    print(_fmt('INFO', Fore.CYAN, msg))


def success(msg: str):
    print(_fmt('SUCCESS', Fore.GREEN, msg))


def warning(msg: str):
    print(_fmt('WARNING', Fore.YELLOW, msg))


def error(msg: str):
    print(_fmt('ERROR', Fore.RED, msg))


def debug(msg: str):
    print(_fmt('DEBUG', Fore.BLUE, msg))


def status(msg: str):
    print(_fmt('STATUS', Fore.MAGENTA, msg))


def highlight_code(msg: str):
    print(_fmt('CODE', Fore.LIGHTCYAN_EX, msg))


def section(name: str):
    header = f"=== {name} ==="
    if _HAS_COLORAMA:
        print(f"\n{Back.BLUE}{Fore.WHITE}{header}{Style.RESET_ALL}\n")
    else:
        print(f"\n{header}\n")