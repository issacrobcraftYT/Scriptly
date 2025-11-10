import sys
import os
from datetime import datetime
from PyQt6.QtWebEngineWidgets import QWebEngineView  
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

# === Ajuste para PyInstaller ===
def fix_imports():
    """
    Asegura que las rutas de los módulos funcionen tanto en dev como en .exe
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folders = ["ui", "core", "utils", "resources"]
    for folder in folders:
        path = os.path.join(base_dir, folder)
        if path not in sys.path:
            sys.path.append(path)

fix_imports()

import core 
import ui

from ui.main_window import MainWindow
from app_metadata import APP_NAME, AUTHOR, get_version

VERSION = get_version(prepend_v=True)

def resource_path(relative_path: str):
    """
    Devuelve la ruta válida para archivos dentro del .exe o en dev
    """
    try:
        base_path = sys._MEIPASS  # carpeta temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def display_banner():
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "╔" + "═"*70 + "╗")
    print("║" + " " * 70 + "║")
    print("║" + f"   {APP_NAME} {VERSION} ".center(70) + "║")
    print("║" + f"  Developed by {AUTHOR}".center(70) + "║")
    print("║" + "  Public use without credit may lead to legal issues!".center(70) + "║")
    print("║" + " " * 70 + "║")
    print("║" + f"  Current session started at: {date_time}".center(70) + "║")
    print("║" + "  Enjoy coding and stay epic! :3".center(70) + "║")
    print("║" + " " * 70 + "║")
    print("╚" + "═"*70 + "╝\n")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont('Segoe UI', 10))

    display_banner()

    icon_path = resource_path("ico.ico")
    window = MainWindow()
    window.setWindowTitle(f"{APP_NAME} - Powered by {AUTHOR}")
    window.setWindowIcon(QIcon(icon_path))
    window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
    window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
