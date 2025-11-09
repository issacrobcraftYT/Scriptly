import sys, os, shutil, ctypes
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

default_folder = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Scriptly"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

class Uninstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scriptly Uninstaller")
        self.resize(400, 200)
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("<h2>Scriptly Uninstaller</h2>"))
        self.label = QLabel(f"This will remove Scriptly from:\n{default_folder}")
        layout.addWidget(self.label)

        btn_uninstall = QPushButton("Uninstall")
        btn_uninstall.clicked.connect(self.uninstall)
        layout.addWidget(btn_uninstall)

    def uninstall(self):
        try:
            if default_folder.exists():
                for item in default_folder.iterdir():
                    if item.name == os.path.basename(sys.argv[0]):
                        continue
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                remaining = list(default_folder.iterdir())
                if len(remaining) == 1 and remaining[0].name == os.path.basename(sys.argv[0]):
                    pass
                else:
                    shutil.rmtree(default_folder)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove Scriptly folder:\n{e}")
            return

        desktop = Path.home() / "Desktop" / "Scriptly.lnk"
        if desktop.exists():
            try:
                desktop.unlink()
            except:
                pass

        QMessageBox.information(self, "Done", "Scriptly has been uninstalled!")

        exe_path = sys.argv[0]
        try:
            os.remove(exe_path)
        except:
            import subprocess
            subprocess.Popen(f'cmd /c "ping 127.0.0.1 -n 2 > nul & del "{exe_path}""', shell=True)
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Uninstaller()
    w.show()
    sys.exit(app.exec())
