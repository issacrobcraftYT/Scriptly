from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
import os

class QuickOpenDialog(QDialog):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.setWindowTitle('Quick Open')
        self.resize(700, 400)
        self._build_ui()
        self.files = []
        self._index_files()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText('Type to filter files...')
        self.input.textChanged.connect(self._filter)
        self.listw = QListWidget()
        self.listw.itemActivated.connect(self._accept)
        layout.addWidget(self.input)
        layout.addWidget(self.listw)

    def _index_files(self):
        # simple file index; avoid hidden dirs
        for dirpath, dirnames, filenames in os.walk(self.root):
            # skip .git and node_modules by default
            dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__')]
            for f in filenames:
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, self.root)
                self.files.append((rel, full))
        self._populate_list(self.files)

    def _populate_list(self, items):
        self.listw.clear()
        for rel, full in items:
            it = QListWidgetItem(rel)
            it.setData(Qt.ItemDataRole.UserRole, full)
            self.listw.addItem(it)

    def _filter(self, text):
        txt = text.lower()
        if not txt:
            self._populate_list(self.files[:200])
            return
        out = [t for t in self.files if txt in t[0].lower()]
        self._populate_list(out[:200])

    def _accept(self, item: QListWidgetItem):
        self.selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def get_selected(self):
        return getattr(self, 'selected', None)
