import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    # Use a neutral system UI font for the application similar to VS Code
    try:
        from PyQt6.QtGui import QFont
        app.setStyle('Fusion')
        ui_font = QFont('Segoe UI', 10)
        app.setFont(ui_font)
    except Exception:
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()