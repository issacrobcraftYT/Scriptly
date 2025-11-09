import sys
from pathlib import Path

# Ensure we can import the application modules
repo_root = Path(__file__).resolve().parents[1]
src_path = repo_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.theme_manager import ThemeManager

try:
    from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow, QVBoxLayout, QWidget, QTextEdit
    from PyQt6.QtGui import QFont
    HAVE_QT = True
except Exception:
    HAVE_QT = False


def preview_theme(theme_name: str | None = None, qss_path: Path | None = None):
    if not HAVE_QT:
        print('PyQt6 is not available in this environment. Install PyQt6 to preview themes.')
        return

    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))

    tm = ThemeManager()
    if theme_name:
        if theme_name not in tm.get_theme_names():
            print(f"Theme '{theme_name}' not found. Available: {tm.get_theme_names()}")
            return
        tm.set_theme(theme_name)
        theme = tm.get_current_theme()
    elif qss_path:
        # load raw qss from path
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss = f.read()
        theme = None
    else:
        theme = tm.get_current_theme()

    # Build a simple UI to preview common widgets
    win = QMainWindow()
    win.setWindowTitle('Scriptly Theme Preview')

    central = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QLabel('Heading — Theme Preview'))
    layout.addWidget(QPushButton('Primary Button'))
    layout.addWidget(QTextEdit('Sample text area to preview background and selection.'))

    central.setLayout(layout)
    win.setCentralWidget(central)

    if theme is not None:
        try:
            app.setStyleSheet(theme.get_stylesheet())
        except Exception as e:
            print('Failed to apply theme stylesheet:', e)
    else:
        app.setStyleSheet(qss)

    win.resize(600, 400)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Preview a Scriptly QSS theme')
    p.add_argument('--theme', help='Theme name to preview (use ThemeManager to list available)')
    p.add_argument('--qss', help='Path to a .qss file to load directly')
    args = p.parse_args()

    qss_path = Path(args.qss) if args.qss else None
    preview_theme(theme_name=args.theme, qss_path=qss_path)
