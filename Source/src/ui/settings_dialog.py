from PyQt6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QSpinBox, QCheckBox, QComboBox, QPushButton,
                             QFontComboBox, QGroupBox, QFormLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()
        self.load_settings()
        
        # Add fade-in animation
        from .utils.animations import fade_in
        fade_in(self, duration=300)
        
    def create_editor_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Editor features group
        features_group = QGroupBox("Editor Features")
        features_layout = QVBoxLayout()
        
        self.minimap_cb = QCheckBox("Show Minimap")
        self.line_numbers_cb = QCheckBox("Show Line Numbers")
        self.highlight_line_cb = QCheckBox("Highlight Current Line")
        self.auto_indent_cb = QCheckBox("Auto Indent")
        self.bracket_matching_cb = QCheckBox("Bracket Matching")
        self.code_folding_cb = QCheckBox("Code Folding")
        self.word_wrap_cb = QCheckBox("Word Wrap")
        self.show_whitespace_cb = QCheckBox("Show Whitespace")
        
        features_layout.addWidget(self.minimap_cb)
        features_layout.addWidget(self.line_numbers_cb)
        features_layout.addWidget(self.highlight_line_cb)
        features_layout.addWidget(self.auto_indent_cb)
        features_layout.addWidget(self.bracket_matching_cb)
        features_layout.addWidget(self.code_folding_cb)
        features_layout.addWidget(self.word_wrap_cb)
        features_layout.addWidget(self.show_whitespace_cb)
        features_group.setLayout(features_layout)
        
        layout.addRow(features_group)
        tab.setLayout(layout)
        return tab
        
    def create_theme_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.color_scheme_combo = QComboBox()
        
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("Color Scheme:", self.color_scheme_combo)
        theme_group.setLayout(theme_layout)
        
        # Custom theme section
        custom_group = QGroupBox("Custom Theme")
        custom_layout = QVBoxLayout()
        
        custom_theme_btn = QPushButton("Create Custom Theme")
        custom_theme_btn.clicked.connect(self.create_custom_theme)
        custom_layout.addWidget(custom_theme_btn)
        
        import_theme_btn = QPushButton("Import Theme")
        import_theme_btn.clicked.connect(self.import_theme)
        custom_layout.addWidget(import_theme_btn)
        
        custom_group.setLayout(custom_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(custom_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_features_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Auto-save group
        autosave_group = QGroupBox("Auto-save")
        autosave_layout = QFormLayout()
        
        self.autosave_cb = QCheckBox("Enable Auto-save")
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setSuffix(" minutes")
        
        autosave_layout.addRow(self.autosave_cb)
        autosave_layout.addRow("Interval:", self.autosave_interval)
        autosave_group.setLayout(autosave_layout)
        
        # Code completion group
        completion_group = QGroupBox("Code Completion")
        completion_layout = QVBoxLayout()
        
        self.autocomplete_cb = QCheckBox("Enable Code Completion")
        self.snippets_cb = QCheckBox("Enable Snippets")
        self.parameter_hints_cb = QCheckBox("Show Parameter Hints")
        
        completion_layout.addWidget(self.autocomplete_cb)
        completion_layout.addWidget(self.snippets_cb)
        completion_layout.addWidget(self.parameter_hints_cb)
        completion_group.setLayout(completion_layout)
        
        layout.addWidget(autosave_group)
        layout.addWidget(completion_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_performance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # File monitoring group
        monitor_group = QGroupBox("File Monitoring")
        monitor_layout = QFormLayout()
        
        self.file_monitor_cb = QCheckBox("Enable File Monitoring")
        self.monitor_interval = QSpinBox()
        self.monitor_interval.setRange(100, 5000)
        self.monitor_interval.setSuffix(" ms")
        
        monitor_layout.addRow(self.file_monitor_cb)
        monitor_layout.addRow("Check Interval:", self.monitor_interval)
        monitor_group.setLayout(monitor_layout)
        
        # Memory usage group
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout()
        
        self.disk_cache_cb = QCheckBox("Enable Disk Cache")
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(128, 4096)
        self.memory_limit.setSuffix(" MB")
        
        memory_layout.addWidget(self.disk_cache_cb)
        memory_layout.addWidget(QLabel("Memory Limit:"))
        memory_layout.addWidget(self.memory_limit)
        memory_group.setLayout(memory_layout)
        
        layout.addWidget(monitor_group)
        layout.addWidget(memory_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def setup_ui(self):
        from .utils.animations import slide_in
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Remove window frame and set modern style
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add custom title bar
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(50)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel("Settings")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        title_bar.setLayout(title_layout)
        layout.addWidget(title_bar)
        
        # Create tab widget with modern style
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setObjectName("settingsTabs")
        
        # Add Editor tab
        editor_tab = self.create_editor_tab()
        tabs.addTab(editor_tab, "Editor")
        
        # Add Theme tab
        theme_tab = self.create_theme_tab()
        tabs.addTab(theme_tab, "Theme")
        
        # Add Features tab
        features_tab = self.create_features_tab()
        tabs.addTab(features_tab, "Features")
        
        # Add Performance tab
        performance_tab = self.create_performance_tab()
        tabs.addTab(performance_tab, "Performance")
        
        # Add tabs with slide animation
        editor_tab = self.create_editor_tab()
        interface_tab = self.create_interface_tab()
        shortcuts_tab = self.create_shortcuts_tab()
        theme_tab = self.create_theme_tab()

        tabs.addTab(editor_tab, "Editor")
        tabs.addTab(interface_tab, "Interface")
        tabs.addTab(shortcuts_tab, "Shortcuts")
        tabs.addTab(theme_tab, "Theme")

        # Animate each tab content
        slide_in(editor_tab, "right", 400)
        slide_in(interface_tab, "right", 400)
        slide_in(shortcuts_tab, "right", 400)
        slide_in(theme_tab, "right", 400)
        
        layout.addWidget(tabs)
        
        # Add modern buttons with hover effects
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        buttons_layout.setSpacing(10)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.setObjectName("resetButton")
        ok_button = QPushButton("Save Changes")
        ok_button.setObjectName("primaryButton")
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("secondaryButton")
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(ok_button)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        reset_button.clicked.connect(self._on_reset_defaults)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def create_editor_tab(self):
        widget = QWidget()
        # Use a form layout for labeled rows
        layout = QFormLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Font settings group
        font_group = QGroupBox("Font Settings")
        font_group.setObjectName("settingsGroup")
        font_layout = QFormLayout()
        font_layout.setContentsMargins(15, 20, 15, 15)
        font_layout.setSpacing(10)
        
        self.font_family = QFontComboBox()
        self.font_family.setObjectName("fontCombo")
        self.font_family.setMinimumWidth(200)
        
        self.font_size = QSpinBox()
        self.font_size.setObjectName("fontSpinBox")
        self.font_size.setRange(6, 72)
        self.font_size.setMinimumWidth(100)
        
        # Editor behavior
        self.tab_size = QSpinBox()
        self.tab_size.setRange(1, 8)
        self.use_spaces = QCheckBox("Use spaces instead of tabs")
        self.auto_indent = QCheckBox("Auto indent")
        self.word_wrap = QCheckBox("Word wrap")
        self.show_line_numbers = QCheckBox("Show line numbers")
        self.highlight_current_line = QCheckBox("Highlight current line")
        self.show_whitespace = QCheckBox("Show whitespace")
        self.show_indentation = QCheckBox("Show indentation guides")
        self.bracket_matching = QCheckBox("Enable bracket matching")
        
        # Auto-save settings
        self.auto_save = QCheckBox("Enable auto-save")
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setSuffix(" minutes")
        
        layout.addRow("Font:", self.font_family)
        layout.addRow("Font size:", self.font_size)
        layout.addRow("Tab size:", self.tab_size)
        layout.addRow("", self.use_spaces)
        layout.addRow("", self.auto_indent)
        layout.addRow("", self.word_wrap)
        layout.addRow("", self.show_line_numbers)
        layout.addRow("", self.highlight_current_line)
        layout.addRow("", self.show_whitespace)
        layout.addRow("", self.show_indentation)
        layout.addRow("", self.bracket_matching)
        layout.addRow("", self.auto_save)
        layout.addRow("Auto-save interval:", self.auto_save_interval)
        
        widget.setLayout(layout)
        return widget
        
    def create_interface_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.show_status_bar = QCheckBox("Show status bar")
        self.show_minimap = QCheckBox("Show minimap")
        self.show_file_browser = QCheckBox("Show file browser")
        self.toolbar_visible = QCheckBox("Show toolbar")
        
        self.tab_position = QComboBox()
        self.tab_position.addItems(["Top", "Bottom", "Left", "Right"])
        
        layout.addRow("", self.show_status_bar)
        layout.addRow("", self.show_minimap)
        layout.addRow("", self.show_file_browser)
        layout.addRow("", self.toolbar_visible)
        layout.addRow("Tab position:", self.tab_position)
        
        widget.setLayout(layout)
        return widget
        
    def create_theme_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_group.setObjectName("settingsGroup")
        theme_layout = QFormLayout()
        theme_layout.setContentsMargins(15, 20, 15, 15)
        theme_layout.setSpacing(10)
        
        # Theme selection
        self.theme_name = QComboBox()
        theme_layout.addRow("Application Theme:", self.theme_name)
        
        # Create user theme button
        import_theme_btn = QPushButton("Import Theme")
        theme_layout.addRow("", import_theme_btn)

        try:
            from core.theme_manager import ThemeManager
            self.theme_manager = ThemeManager()
            names = self.theme_manager.get_theme_names()
            current_theme = self.settings.theme.get('name', 'modern_dark')
            
            # Populate theme dropdown
            for n in names:
                pretty = n.replace('_', ' ').title()
                self.theme_name.addItem(pretty, userData=n)
                
            # Set current theme
            index = self.theme_name.findData(current_theme)
            if index >= 0:
                self.theme_name.setCurrentIndex(index)
                
            # Connect theme change handler
            self.theme_name.currentIndexChanged.connect(self._on_theme_changed)
            import_theme_btn.clicked.connect(self._on_import_theme)
        except Exception as e:
            print(f"Failed to initialize themes: {e}")
            self.theme_name.addItem("Modern Dark", "modern_dark")
            
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Help text
        help_text = QLabel("Themes can be added by placing .qss and .json files in:\n"
                          "- Built-in themes: src/core/themes/\n"
                          "- User themes: ~/.scriptly/themes/\n"
                          "See the themes/README.md for more information.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: gray;")
        layout.addWidget(help_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _on_theme_changed(self, index):
        theme_name = self.theme_name.currentData()
        if theme_name:
            self.settings.theme['name'] = theme_name
            self.settings.save()
            if hasattr(self.parent(), 'apply_theme'):
                self.parent().apply_theme()
                
    def _on_import_theme(self):
        from PyQt6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Theme",
            "",
            "Theme Files (*.qss *.json);;All Files (*.*)"
        )
        if not files:
            return
            
        for file in files:
            try:
                import shutil
                from pathlib import Path
                
                # Create user themes directory if it doesn't exist
                user_themes = Path.home() / ".scriptly" / "themes"
                user_themes.mkdir(parents=True, exist_ok=True)
                
                # Copy theme file to user themes directory
                src = Path(file)
                dst = user_themes / src.name
                shutil.copy2(src, dst)
                
                # If it's a .qss file, try to copy the matching .json if it exists
                if src.suffix == '.qss':
                    json_src = src.with_suffix('.json')
                    if json_src.exists():
                        json_dst = dst.with_suffix('.json')
                        shutil.copy2(json_src, json_dst)
                        
                # Reload themes
                if hasattr(self, 'theme_manager'):
                    self.theme_manager.reload()
                    
                # Update theme dropdown
                self.theme_name.clear()
                for name in self.theme_manager.get_theme_names():
                    pretty = name.replace('_', ' ').title()
                    self.theme_name.addItem(pretty, userData=name)
                    
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Import Error", f"Failed to import theme: {e}")
                
        # Show success message if any files were imported
        if files:
            QMessageBox.information(self, "Success", "Themes imported successfully!")
        # Theme selection - populate from ThemeManager
        # Theme selection
        self.theme_name = QComboBox()
        theme_layout.addRow("Application Theme:", self.theme_name)
        
        # Create user theme button
        import_theme_btn = QPushButton("Import Theme")
        theme_layout.addRow("", import_theme_btn)

        try:
            from core.theme_manager import ThemeManager
            self.theme_manager = ThemeManager()
            names = self.theme_manager.get_theme_names()
            current_theme = self.settings.value('theme/name', 'modern_dark')
            
            # Populate theme dropdown
            for n in names:
                pretty = n.replace('_', ' ').title()
                self.theme_name.addItem(pretty, userData=n)
                
            # Set current theme
            index = self.theme_name.findData(current_theme)
            if index >= 0:
                self.theme_name.setCurrentIndex(index)
                
            # Connect theme change handler
            self.theme_name.currentIndexChanged.connect(self._on_theme_changed)
            import_theme_btn.clicked.connect(self._on_import_theme)
        except Exception as e:
            print(f"Failed to initialize themes: {e}")
            self.theme_name.addItem("Modern Dark", "modern_dark")
            self.theme_name.addItem('Modern Dark', userData='modern_dark')
            self.syntax_theme.addItem('Modern Dark', userData='modern_dark')
        self.syntax_theme.setEnabled(False)  # Locked to modern dark
        
        theme_layout.addRow("Interface theme:", self.theme_name)
        theme_layout.addRow("Code highlighting:", self.syntax_theme)
        
        # Info label
        info = QLabel("Scriptly uses an optimized modern dark theme designed for long coding sessions and optimal readability.")
        info.setWordWrap(True)
        info.setProperty("info", "true")  # For styling
        info.setContentsMargins(0, 10, 0, 0)
        theme_layout.addRow(info)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Preview
        preview_group = QGroupBox("Theme Preview")
        preview_group.setObjectName("settingsGroup")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(15, 20, 15, 15)
        
        preview = QLabel("""
        <pre><code># Example code preview
def greet(name: str) -> str:
    \"\"\"Return a personalized greeting.\"\"\"
    return f'Hello, {name}!'

# Test the function
print(greet('World'))  # Output: Hello, World!</code></pre>
        """)
        preview.setTextFormat(Qt.TextFormat.RichText)
        preview_layout.addWidget(preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_shortcuts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # TODO: Add keyboard shortcut editor
        layout.addWidget(QLabel("Keyboard shortcuts coming soon..."))
        
        widget.setLayout(layout)
        return widget
        
    def load_settings(self):
        # Editor settings
        self.font_family.setCurrentText(self.settings.editor['font_family'])
        self.font_size.setValue(self.settings.editor['font_size'])
        self.tab_size.setValue(self.settings.editor['tab_size'])
        self.use_spaces.setChecked(self.settings.editor['use_spaces'])
        self.auto_indent.setChecked(self.settings.editor['auto_indent'])
        self.word_wrap.setChecked(self.settings.editor['word_wrap'])
        self.show_line_numbers.setChecked(self.settings.editor['show_line_numbers'])
        self.highlight_current_line.setChecked(self.settings.editor['highlight_current_line'])
        self.show_whitespace.setChecked(self.settings.editor['show_whitespace'])
        self.show_indentation.setChecked(self.settings.editor['show_indentation_guides'])
        self.bracket_matching.setChecked(self.settings.editor['bracket_matching'])
        self.auto_save.setChecked(self.settings.editor['auto_save'])
        self.auto_save_interval.setValue(self.settings.editor['auto_save_interval'])
        
        # Interface settings
        self.show_status_bar.setChecked(self.settings.interface['show_status_bar'])
        self.show_minimap.setChecked(self.settings.interface['show_minimap'])
        self.show_file_browser.setChecked(self.settings.interface['show_file_browser'])
        self.toolbar_visible.setChecked(self.settings.interface['toolbar_visible'])
        self.tab_position.setCurrentText(self.settings.interface['tab_position'].capitalize())
        
        # Theme settings
        current_theme = self.settings.theme.get('name', 'modern_dark')
        index = self.theme_name.findData(current_theme)
        if index >= 0:
            self.theme_name.setCurrentIndex(index)
        
    def save_settings(self):
        # Editor settings
        self.settings.editor['font_family'] = self.font_family.currentText()
        self.settings.editor['font_size'] = self.font_size.value()
        self.settings.editor['tab_size'] = self.tab_size.value()
        self.settings.editor['use_spaces'] = self.use_spaces.isChecked()
        self.settings.editor['auto_indent'] = self.auto_indent.isChecked()
        self.settings.editor['word_wrap'] = self.word_wrap.isChecked()
        self.settings.editor['show_line_numbers'] = self.show_line_numbers.isChecked()
        self.settings.editor['highlight_current_line'] = self.highlight_current_line.isChecked()
        self.settings.editor['show_whitespace'] = self.show_whitespace.isChecked()
        self.settings.editor['show_indentation_guides'] = self.show_indentation.isChecked()
        self.settings.editor['bracket_matching'] = self.bracket_matching.isChecked()
        self.settings.editor['auto_save'] = self.auto_save.isChecked()
        self.settings.editor['auto_save_interval'] = self.auto_save_interval.value()
        
        # Interface settings
        self.settings.interface['show_status_bar'] = self.show_status_bar.isChecked()
        self.settings.interface['show_minimap'] = self.show_minimap.isChecked()
        self.settings.interface['show_file_browser'] = self.show_file_browser.isChecked()
        self.settings.interface['toolbar_visible'] = self.toolbar_visible.isChecked()
        self.settings.interface['tab_position'] = self.tab_position.currentText().lower()
        
        # Theme settings
        self.settings.theme['name'] = self.theme_name.currentData()
        
        # Apply theme changes immediately
        if self.parent() and hasattr(self.parent(), 'apply_theme'):
            self.parent().apply_theme()
        
        self.settings.save()

    def _on_reset_defaults(self):
        # ask for confirmation
        try:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, 'Reset Defaults', 'Reset all settings to defaults? This cannot be undone.',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.settings.reset_to_defaults()
                except Exception:
                    pass
                # reload UI with defaults
                try:
                    self.load_settings()
                except Exception:
                    pass
        except Exception:
            try:
                self.settings.reset_to_defaults()
                self.load_settings()
            except Exception:
                pass