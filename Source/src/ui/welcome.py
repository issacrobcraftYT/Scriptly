from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal




from .utils.modern_widgets import ModernButton
from .utils.ui_effects import apply_shadow, ModernWidget

class WelcomeWidget(ModernWidget):
    """A modern, animated welcome widget with material design elements.

    Signals:
        open_folder() - user clicked Open Folder
        new_file() - user clicked New File
    """
    open_folder = pyqtSignal()
    new_file = pyqtSignal()

    def __init__(self, recent=None, parent=None):
        super().__init__(parent)
        self.recent = recent or []
        self.setObjectName("welcomeWidget")
        
        # Apply clean, integrated styling
        self.setStyleSheet("""
            #welcomeWidget {
                background-color: transparent;
            }
            QLabel {
                color: palette(text);
            }
            QPushButton {
                background-color: palette(button);
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                min-width: 140px;
                color: palette(button-text);
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 2px;
            }
            QListWidget::item:hover {
                background-color: palette(alternate-base);
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            .recent-label {
                color: palette(text);
                font-weight: bold;
                margin-top: 15px;
            }
            .welcome-header {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
            .welcome-subheader {
                color: palette(text);
                margin-bottom: 20px;
            }
            .tip-label {
                color: palette(disabled-text);
                font-size: 11px;
                margin-top: 15px;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 40, 30, 30)

        # Content container for centering
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)
        
        # Welcome header
        header = QLabel("Welcome to Scriptly")
        header.setProperty("class", "welcome-header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)

        # Welcome message
        sub = QLabel("Open a folder to start working, or create a new file.")
        sub.setProperty("class", "welcome-subheader")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(sub)

        # Actions section with modern buttons
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setSpacing(16)
        actions_layout.setContentsMargins(0, 24, 0, 24)
        
        btn_open = ModernButton("Open Folder")
        btn_open.set_accent_color("#2979ff")  # Material Blue
        
        btn_new = ModernButton("New File")
        btn_new.set_accent_color("#00c853")  # Material Green
        
        actions_layout.addStretch(1)
        actions_layout.addWidget(btn_open)
        actions_layout.addWidget(btn_new)
        actions_layout.addStretch(1)
        
        content_layout.addWidget(actions)

        # Recent workspaces section
        if self.recent:
            recent_section = QWidget()
            recent_layout = QVBoxLayout(recent_section)
            recent_layout.setSpacing(8)
            recent_layout.setContentsMargins(0, 10, 0, 0)
            
            recent_header = QLabel("Recent Workspaces")
            recent_header.setProperty("class", "recent-label")
            recent_layout.addWidget(recent_header)
            
            lst = QListWidget()
            lst.setMaximumHeight(200)
            for p in self.recent:
                lst.addItem(p)
            lst.itemDoubleClicked.connect(lambda it: self._open_recent(it.text()))
            recent_layout.addWidget(lst)
            
            content_layout.addWidget(recent_section)

        # Keyboard shortcut tip
        tip = QLabel("Tip: Use File → Open Folder as Workspace or Ctrl+K, Ctrl+O to open a workspace")
        tip.setProperty("class", "tip-label")
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(tip)

        # Add content to main layout with centering
        layout.addStretch(1)
        layout.addWidget(content)
        layout.addStretch(1)
        layout.setAlignment(content, Qt.AlignmentFlag.AlignCenter)

        # Connect signals
        btn_open.clicked.connect(lambda: self.open_folder.emit())
        btn_new.clicked.connect(lambda: self.new_file.emit())

    def _open_recent(self, path):
        # emit open_folder signal; MainWindow will handle recent path selection
        self.open_folder.emit()

