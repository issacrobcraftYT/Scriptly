from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
from PyQt6.QtCore import Qt
import os, re

class FindInFilesDialog(QDialog):
    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        self.root_path = root_path or os.getcwd()
        self.setWindowTitle("Find in Files")
        self.resize(700, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        hl.addWidget(self.find_input)
        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(self.do_find)
        hl.addWidget(self.find_btn)
        layout.addLayout(hl)

        self.results = QListWidget()
        self.results.itemDoubleClicked.connect(self.open_result)
        layout.addWidget(self.results)

        self.setLayout(layout)

    def do_find(self):
        pattern = self.find_input.text()
        if not pattern:
            QMessageBox.warning(self, "No pattern", "Please enter a search pattern")
            return
        self.results.clear()
        try:
            regex = re.compile(pattern)
        except re.error as e:
            QMessageBox.critical(self, "Regex error", str(e))
            return
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        for i, line in enumerate(fh, start=1):
                            if regex.search(line):
                                self.results.addItem(f"{path}:{i}: {line.strip()}")
                except Exception:
                    # skip binary or unreadable files
                    continue

    def open_result(self, item):
        text = item.text()
        parts = text.split(':', 2)
        if len(parts) >= 2:
            path = parts[0]
            lineno = int(parts[1])
            # Emit data back to main window by setting attributes; caller should read them
            self.selected_path = path
            self.selected_line = lineno
            self.accept()
