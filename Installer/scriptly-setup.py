import sys, os, requests, zipfile, json, shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QProgressBar, QComboBox, QCheckBox, QStackedLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pyshortcuts import make_shortcut
import ctypes

API_URL = "https://scriptlyapp.vercel.app/api"
default_folder = Path(os.environ.get("ProgramFiles", "C:/Program Files"))

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

class InstallerThread(QThread):
    progress = pyqtSignal(int)
    stage = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, url, dest_zip, dest_folder):
        super().__init__()
        self.url = url
        self.dest_zip = dest_zip
        self.dest_folder = dest_folder

    def run(self):
        self.stage.emit("Downloading...")
        r = requests.get(self.url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(self.dest_zip, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = int((downloaded / total_size) * 100) if total_size else 0
                    self.progress.emit(pct)

        self.stage.emit("Extracting...")
        with zipfile.ZipFile(self.dest_zip, "r") as zip_ref:
            zip_ref.extractall(self.dest_folder)

        if os.path.exists(self.dest_zip):
            os.remove(self.dest_zip)

        self.finished.emit()

class Installer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scriptly Installer / Updater")
        self.resize(450, 320)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.stack = QStackedLayout()
        self.layout.addLayout(self.stack)

        self.page_welcome = QWidget()
        w_layout = QVBoxLayout()
        self.welcome_label = QLabel("<h2>Welcome to Scriptly Installer</h2>")
        w_layout.addWidget(self.welcome_label)
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        w_layout.addWidget(self.btn_next)
        self.page_welcome.setLayout(w_layout)
        self.stack.addWidget(self.page_welcome)

        self.page_path = QWidget()
        p_layout = QVBoxLayout()
        p_layout.addWidget(QLabel("Select installation folder:"))
        self.path_label = QLabel(str(default_folder))
        p_layout.addWidget(self.path_label)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_folder)
        p_layout.addWidget(btn_browse)
        btn_next2 = QPushButton("Next")
        btn_next2.clicked.connect(self.fetch_versions)
        p_layout.addWidget(btn_next2)
        self.page_path.setLayout(p_layout)
        self.stack.addWidget(self.page_path)

        self.page_version = QWidget()
        v_layout = QVBoxLayout()
        v_layout.addWidget(QLabel("Select version to install:"))
        self.combo_versions = QComboBox()
        v_layout.addWidget(self.combo_versions)
        self.checkbox_shortcut = QCheckBox("Create desktop shortcut")
        self.checkbox_shortcut.setChecked(True)
        v_layout.addWidget(self.checkbox_shortcut)
        btn_install = QPushButton("Install / Update")
        btn_install.clicked.connect(self.start_install)
        v_layout.addWidget(btn_install)
        self.progress_bar = QProgressBar()
        v_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Progress: waiting...")
        v_layout.addWidget(self.progress_label)
        self.page_version.setLayout(v_layout)
        self.stack.addWidget(self.page_version)

        self.stack.setCurrentIndex(0)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Installation Folder", str(default_folder))
        if folder:
            self.path_label.setText(folder)

    def fetch_versions(self):
        try:
            r = requests.get(f"{API_URL}/versions")
            r.raise_for_status()
            data = r.json()
            self.combo_versions.clear()
            self.combo_versions.addItem("latest")
            for v in data.get("versions", []):
                self.combo_versions.addItem(v)
            self.stack.setCurrentIndex(2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch versions:\n{e}")

    def start_install(self):
        version = self.combo_versions.currentText()
        dest_folder = Path(self.path_label.text())
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_zip = dest_folder / "Scriptly.zip"
        url = f"{API_URL}/download?version={version}"

        scriptly_folder = dest_folder / "Scriptly"
        if scriptly_folder.exists():
            try:
                shutil.rmtree(scriptly_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove old Scriptly folder:\n{e}")
                return

        self.thread = InstallerThread(url, str(dest_zip), str(dest_folder))
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.stage.connect(self.progress_label.setText)
        self.thread.finished.connect(lambda: self.post_install(dest_folder, version))
        self.thread.start()

    def post_install(self, folder: Path, version):
        final_folder = folder / "Scriptly"

        info_file = final_folder / "app_info.json"
        if not info_file.exists():
            with open(info_file, "w") as f:
                json.dump({"version": version}, f)

        if self.checkbox_shortcut.isChecked():
            exe_path = final_folder / "Scriptly.exe"
            if exe_path.exists():
                make_shortcut(str(exe_path), name="Scriptly", desktop=True)

        self.progress_bar.setValue(100)
        self.progress_label.setText("Done!")
        QMessageBox.information(self, "Installation Complete", f"Scriptly {version} installed successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Installer()
    w.show()
    sys.exit(app.exec())
