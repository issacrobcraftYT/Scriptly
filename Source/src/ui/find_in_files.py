from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import re

class FindInFilesDialog(QDialog):
    file_selected = pyqtSignal(str, int)  # file path, line number

    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        self.root_path = root_path or os.getcwd()
        self.setWindowTitle("Find in Files")
        self.resize(800, 600)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        search_layout.addWidget(self.find_input)
        
        # Replace input (initially hidden)
        self.replace_layout = QHBoxLayout()
        self.replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        self.replace_input.setVisible(False)
        self.replace_layout.addWidget(self.replace_input)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case sensitive")
        self.use_regex = QCheckBox("Use regex")
        self.show_replace = QCheckBox("Show replace")
        self.show_replace.toggled.connect(self._toggle_replace)
        
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.use_regex)
        options_layout.addWidget(self.show_replace)
        options_layout.addStretch()
        
        # File filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("File types:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("e.g., *.py, *.js")
        filter_layout.addWidget(self.filter_input)

        # Buttons
        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(self.do_find)
        search_layout.addWidget(self.find_btn)

        self.replace_btn = QPushButton("Replace All")
        self.replace_btn.clicked.connect(self.do_replace)
        self.replace_btn.setVisible(False)
        self.replace_layout.addWidget(self.replace_btn)

        # Results tree
        self.results = QTreeWidget()
        self.results.setHeaderLabels(["File", "Line", "Text"])
        self.results.itemDoubleClicked.connect(self.open_result)

        # Add all layouts to main layout
        layout.addLayout(search_layout)
        layout.addLayout(self.replace_layout)
        layout.addLayout(options_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.results)

        self.setLayout(layout)

    def _toggle_replace(self, checked):
        self.replace_input.setVisible(checked)
        self.replace_btn.setVisible(checked)

    def _matches_filter(self, filename):
        filter_text = self.filter_input.text().strip()
        if not filter_text:
            return True
            
        patterns = [p.strip() for p in filter_text.split(",")]
        return any(self._matches_pattern(filename, pattern) for pattern in patterns)

    def _matches_pattern(self, filename, pattern):
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())

    def do_find(self):
        pattern = self.find_input.text()
        if not pattern:
            QMessageBox.warning(self, "No pattern", "Please enter a search pattern")
            return

        self.results.clear()
        try:
            flags = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
            if self.use_regex.isChecked():
                regex = re.compile(pattern, flags)
            else:
                regex = re.compile(re.escape(pattern), flags)
        except re.error as e:
            QMessageBox.critical(self, "Regex error", str(e))
            return

        for root, _, files in os.walk(self.root_path):
            for f in files:
                if not self._matches_filter(f):
                    continue
                    
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        for i, line in enumerate(fh, start=1):
                            if regex.search(line):
                                item = QTreeWidgetItem([
                                    os.path.relpath(path, self.root_path),
                                    str(i),
                                    line.strip()
                                ])
                                self.results.addTopLevelItem(item)
                except Exception:
                    # skip binary or unreadable files
                    continue

    def do_replace(self):
        if not self.show_replace.isChecked():
            return
            
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text or not replace_text:
            QMessageBox.warning(self, "Missing input", "Please enter both search and replace text")
            return
            
        # Collect all files that need modification
        files_to_modify = set()
        root = self.results.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            file_path = os.path.join(self.root_path, item.text(0))
            files_to_modify.add(file_path)
            
        if not files_to_modify:
            return
            
        # Confirm with user
        reply = QMessageBox.question(self, "Confirm Replace",
                                   f"Replace all occurrences in {len(files_to_modify)} files?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # Perform replacement
        try:
            flags = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
            if self.use_regex.isChecked():
                regex = re.compile(search_text, flags)
            else:
                regex = re.compile(re.escape(search_text), flags)
                
            for file_path in files_to_modify:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                modified = regex.sub(replace_text, content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified)
                    
            QMessageBox.information(self, "Success", 
                                  f"Replaced all occurrences in {len(files_to_modify)} files")
            self.do_find()  # Refresh results
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during replace: {str(e)}")

    def open_result(self, item):
        file_path = os.path.join(self.root_path, item.text(0))
        line_number = int(item.text(1))
        self.file_selected.emit(file_path, line_number)
        self.accept()
