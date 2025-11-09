import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

APP_NAME = "Scriptly"
AUTHOR = "MoonIsaa"
VERSION = "v0.0.0"

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

    # Setup main window
    window = MainWindow()
    window.setWindowTitle(f"{APP_NAME} - Powered by {AUTHOR}")
    window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
    window.show()

    # Try running app safely
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
