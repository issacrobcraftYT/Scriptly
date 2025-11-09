from PyQt6.QtWidgets import (QMainWindow, QWidget, QTabWidget, QMenuBar, QStatusBar, QFileDialog,
                              QMessageBox, QDockWidget, QTreeView, QToolBar, QSplitter,
                              QLabel, QDialog, QMenu)
from PyQt6.QtCore import Qt, QSize, QDir, QTimer, QFileSystemWatcher, QModelIndex
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from .editor_widget import EditorWidget
from .settings_dialog import SettingsDialog
from .terminal_widget import TerminalWidget
from .find_in_files import FindInFilesDialog
from .utils.animations import fade_in, slide_widget
from core.settings import Settings
from core.theme_manager import ThemeManager
from core.file_monitor import FileMonitor
from PyQt6.QtCore import Qt
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.file_monitor = FileMonitor(self.settings)
        self.file_monitor.file_changed.connect(self.handle_external_file_change)
        
        self.setup_ui()
        self.setup_menubar()
        self.setup_shortcuts()
        self.setup_file_browser()
        self.setup_status_bar()
        # Set initial theme before showing window
        self.apply_theme()
        
        # Apply modern window flags
        self.setWindowFlags(self.windowFlags())
        
        # Start auto-save timer if enabled
        if self.settings.editor['auto_save']:
            self.start_auto_save()
        
        # Use a single timer for both operations
        QTimer.singleShot(100, lambda: self.post_show_init())

    def setup_ui(self):
        self.setWindowTitle("Scriptly")
        self.setMinimumSize(QSize(800, 600))
        
        # Create main splitter with animation
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        fade_in(self.main_splitter, duration=500)
        
        # Create tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(True)  # Modern flat look
        self.tab_widget.setMovable(True)  # Allow tab reordering
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_status_bar)
        
        # Customize tab bar
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setExpanding(False)  # Fixed tab width
        tab_bar.setDrawBase(False)  # Remove bottom line
        
        from PyQt6.QtGui import QPainter, QPixmap, QIcon, QColor, QPen
        
        def _make_x_icon(size=12, color=QColor(30, 30, 30)):
            pm = QPixmap(size, size)
            pm.fill(Qt.GlobalColor.transparent)

            # Use QPainter initialized with the pixmap to avoid separate begin()/end() race
            painter = QPainter(pm)
            try:
                if painter.isActive():
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    pen = QPen(color)
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.drawLine(3, 3, size - 4, size - 4)
                    painter.drawLine(size - 4, 3, 3, size - 4)
                else:
                    # painter failed to become active; return an empty icon
                    print("Warning: QPainter failed to initialize for icon drawing")
            finally:
                if painter.isActive():
                    painter.end()

            return QIcon(pm)
            
        try:
            self._close_icon = _make_x_icon(12, QColor(30, 30, 30))
            # apply a lightweight stylesheet so the close button 'lights up' on hover
            self.tab_widget.setStyleSheet("""
                QTabBar::close-button { border: 0px; margin: 2px; padding: 2px; }
                QTabBar::close-button:hover { background: rgba(255, 255, 255, 0.1); }
            """)
            # when tabs are added we'll set a close button widget per-tab that uses this icon
        except Exception:
            self._close_icon = None
        
        # Add splitter as central widget
        self.main_splitter.addWidget(self.tab_widget)
        self.setCentralWidget(self.main_splitter)
        
        # Create first editor tab
        self.new_file()

    def closeEvent(self, event):
        # Prompt to save unsaved changes before quitting
        try:
            unsaved = []
            for i in range(self.tab_widget.count()):
                ed = self.tab_widget.widget(i)
                try:
                    if hasattr(ed, 'isModified') and ed.isModified():
                        name = getattr(ed, 'file_path', None) or f'Untitled-{i+1}'
                        unsaved.append((i, name))
                except Exception:
                    pass

            if unsaved:
                from PyQt6.QtWidgets import QMessageBox
                names = '\n'.join([n for _, n in unsaved[:10]])
                msg = f"You have {len(unsaved)} unsaved file(s):\n{names}\n\nSave all before exiting?"
                resp = QMessageBox.question(
                    self, 'Unsaved Changes', msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes
                )
                if resp == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
                if resp == QMessageBox.StandardButton.Yes:
                    # attempt to save all editors (best-effort)
                    for idx, _ in unsaved:
                        try:
                            ed = self.tab_widget.widget(idx)
                            self.save_file_for_editor(ed)
                        except Exception:
                            pass

        except Exception:
            # if anything goes wrong during prompt, continue to clean up
            pass

        # Ensure any running terminal processes are killed cleanly
        try:
            if hasattr(self, 'terminal_tabs'):
                for i in range(self.terminal_tabs.count()):
                    w = self.terminal_tabs.widget(i)
                    # find TerminalWidget children and kill their processes
                    for t in w.findChildren(TerminalWidget):
                        try:
                            t.kill()
                        except Exception:
                            pass
        except Exception:
            pass

        super().closeEvent(event)

    def setup_menubar(self):
        menubar = self.menuBar()

        # File Menu (trimmed to match requested layout)
        file_menu = menubar.addMenu("&File")
        # Save current file
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")
        # Save all open files
        save_all_action = file_menu.addAction("Save All")
        save_all_action.triggered.connect(lambda: [self.save_file_for_editor(self.tab_widget.widget(i)) for i in range(self.tab_widget.count())])
        save_as_action = file_menu.addAction("Save As")
        save_as_action.triggered.connect(self.save_file_as)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Alt+F4")

        # Edit Menu (kept minimal; removed search options as requested)
        edit_menu = menubar.addMenu("&Edit")
        undo_action = edit_menu.addAction("Undo")
        undo_action.triggered.connect(self.undo)
        undo_action.setShortcut("Ctrl+Z")
        redo_action = edit_menu.addAction("Redo")
        redo_action.triggered.connect(self.redo)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addSeparator()
        cut_action = edit_menu.addAction("Cut")
        cut_action.triggered.connect(self.cut)
        cut_action.setShortcut("Ctrl+X")
        copy_action = edit_menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        copy_action.setShortcut("Ctrl+C")
        paste_action = edit_menu.addAction("Paste")
        paste_action.triggered.connect(self.paste)
        paste_action.setShortcut("Ctrl+V")

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        run_action = tools_menu.addAction("Run/Debug Current File")
        run_action.triggered.connect(self.run_debug_current_file)

        # Terminal Menu
        terminal_menu = menubar.addMenu("&Terminal")
        new_terminal_action = terminal_menu.addAction("New Terminal")
        new_terminal_action.triggered.connect(self.new_terminal)
        split_terminal_action = terminal_menu.addAction("Split Terminal")
        split_terminal_action.triggered.connect(self.split_terminal)
        toggle_terminal_action = terminal_menu.addAction("Toggle Terminal")
        toggle_terminal_action.triggered.connect(self.toggle_terminal)

        # View Menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Toggle File Browser", self.toggle_file_browser)

        # Settings / Preferences (visible and discoverable)
        settings_menu = menubar.addMenu("&Settings")
        settings_action = settings_menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings_dialog)
        # Common shortcut for settings/preferences
        try:
            settings_action.setShortcut("Ctrl+,")
        except Exception:
            pass

    def setup_shortcuts(self):
        # Quick Open (Ctrl+P) and Go To Line (Ctrl+G)
        try:
            from PyQt6.QtGui import QKeySequence
            from PyQt6.QtWidgets import QInputDialog
            self.shortcut_quick_open = QAction(self)
            self.shortcut_quick_open.setShortcut(QKeySequence('Ctrl+P'))
            self.shortcut_quick_open.triggered.connect(self.show_quick_open)
            self.addAction(self.shortcut_quick_open)

            self.shortcut_goto = QAction(self)
            self.shortcut_goto.setShortcut(QKeySequence('Ctrl+G'))
            self.shortcut_goto.triggered.connect(self.goto_line)
            self.addAction(self.shortcut_goto)

            # Toggle file browser (Ctrl+B)
            self.shortcut_toggle_browser = QAction(self)
            self.shortcut_toggle_browser.setShortcut(QKeySequence('Ctrl+B'))
            self.shortcut_toggle_browser.triggered.connect(lambda: self.file_browser.setVisible(not self.file_browser.isVisible()))
            self.addAction(self.shortcut_toggle_browser)

            # Increase/decrease editor font sizes
            self.shortcut_increase_font = QAction(self)
            self.shortcut_increase_font.setShortcut(QKeySequence('Ctrl++'))
            self.shortcut_increase_font.triggered.connect(self.increase_font_size)
            self.addAction(self.shortcut_increase_font)

            self.shortcut_decrease_font = QAction(self)
            self.shortcut_decrease_font.setShortcut(QKeySequence('Ctrl+-'))
            self.shortcut_decrease_font.triggered.connect(self.decrease_font_size)
            self.addAction(self.shortcut_decrease_font)
        except Exception:
            pass

    def post_show_init(self):
        """Handle initialization that should happen after the window is shown."""
        # Update the UI to prevent any paint artifacts
        self.update()
        
        # Make sure all child widgets are properly styled
        self.style().polish(self)
        
        # Fade in the window
        QTimer.singleShot(50, lambda: fade_in(self, duration=300))
        
    def apply_theme(self):
        """Apply the current theme from settings with proper paint handling."""
        theme = self.theme_manager.get_current_theme()
        
        # Block signals during stylesheet application to prevent paint conflicts
        self.blockSignals(True)
        
        # Define additional styling refinements
        extra_styles = """
            QTabBar::close-button { 
                border: 0; 
                margin: 2px; 
                padding: 2px;
            }
            QTabBar::close-button:hover { 
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QToolBar { 
                padding: 4px;
                spacing: 4px;
                border: none;
            }
            QStatusBar { 
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """
        
        try:
            # Get the modern dark theme stylesheet
            stylesheet = theme.get_stylesheet()
            
            # Set stylesheet without triggering immediate repaints
            self.setUpdatesEnabled(False)
            self.setStyleSheet(stylesheet + "\n" + extra_styles)
            
            # Update child widgets
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'update_theme'):
                    widget.update_theme(theme)
                    
        except Exception as e:
            print(f"Error applying theme: {e}")
            self.setStyleSheet(extra_styles)  # Fallback to basic styling
            
        finally:
            # Always re-enable updates and signals
            self.setUpdatesEnabled(True)
            self.blockSignals(False)
            
            # Schedule a proper update
            QTimer.singleShot(0, self.update)

    def new_file(self):
        editor = EditorWidget(self.settings)
        idx = self.tab_widget.addTab(editor, "Untitled")
        # apply custom close button if available
        try:
            if self._close_icon:
                bar = self.tab_widget.tabBar()
                from PyQt6.QtWidgets import QPushButton
                btn = QPushButton()
                btn.setFlat(True)
                btn.setIcon(self._close_icon)
                btn.setCursor(bar.cursor())
                btn.setFixedSize(18, 18)
                # attach the button to the right side of the tab
                bar.setTabButton(idx, bar.ButtonPosition.RightSide, btn)
                # when clicked, find which tab contains this button and close it
                def _on_close():
                    for j in range(self.tab_widget.count()):
                        if bar.tabButton(j, bar.ButtonPosition.RightSide) is btn:
                            self.close_tab(j)
                            return
                btn.clicked.connect(_on_close)
        except Exception:
            pass
        self.tab_widget.setCurrentWidget(editor)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            # If already open, focus the existing tab instead of opening duplicate
            for i in range(self.tab_widget.count()):
                existing = self.tab_widget.widget(i)
                if hasattr(existing, 'file_path') and existing.file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    try:
                        existing.setFocus()
                    except Exception:
                        pass
                    return

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                editor = EditorWidget(self.settings)
                editor.setText(content)
                editor.file_path = file_path
                # set lexer based on extension
                try:
                    ext = os.path.splitext(file_path)[1].lstrip('.')
                    editor.set_lexer(ext)
                except Exception:
                    pass
                # add file to monitor
                try:
                    self.file_monitor.add_file(file_path)
                except Exception:
                    pass
                idx = self.tab_widget.addTab(editor, file_path.split('/')[-1])
                # ensure the newly added tab is selected and focused
                # apply custom close button if available
                try:
                    if self._close_icon:
                        bar = self.tab_widget.tabBar()
                        from PyQt6.QtWidgets import QPushButton
                        btn = QPushButton()
                        btn.setFlat(True)
                        btn.setIcon(self._close_icon)
                        btn.setCursor(bar.cursor())
                        btn.setFixedSize(18, 18)
                        bar.setTabButton(idx, bar.ButtonPosition.RightSide, btn)
                        def _on_close():
                            for j in range(self.tab_widget.count()):
                                if bar.tabButton(j, bar.ButtonPosition.RightSide) is btn:
                                    self.close_tab(j)
                                    return
                        btn.clicked.connect(_on_close)
                except Exception:
                    pass
                self.tab_widget.setCurrentIndex(idx)
                try:
                    editor.setFocus()
                except Exception:
                    pass
                # animate editor appearance
                try:
                    fade_in(editor, duration=260)
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            if not hasattr(editor, 'file_path') or not editor.file_path:
                self.save_file_as()
            else:
                try:
                    with open(editor.file_path, 'w', encoding='utf-8') as file:
                        file.write(editor.text())
                    self.status_bar.showMessage("File saved successfully", 2000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def save_file_as(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", "",
                "All Files (*);;Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js)"
            )
            if file_path:
                editor.file_path = file_path
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])
                self.save_file()

    def close_tab(self, index):
        # Add check for unsaved changes here
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.new_file()

    def show_find_dialog(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.show_find_dialog()

    def show_replace_dialog(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.show_replace_dialog()

    def undo(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.undo()

    def redo(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.redo()

    def cut(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.cut()

    def copy(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.copy()

    def paste(self):
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            editor.paste()

    def change_theme(self, theme_name):
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()
        
    def setup_toolbar(self):
        """Toolbar removed in favor of menu-based actions"""
        pass
        
    def setup_file_browser(self):
        self.file_browser = QDockWidget("Files", self)
        self.file_browser.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        # Create file system model (import lazily because some PyQt6 builds expose it differently)
        try:
            from PyQt6.QtWidgets import QFileSystemModel
        except Exception:
            from PyQt6.QtCore import QFileSystemModel
        self.file_system = QFileSystemModel()
        self.file_system.setRootPath(QDir.currentPath())
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system)
        self.tree_view.setRootIndex(
            self.file_system.index(QDir.currentPath())
        )
        self.tree_view.hideColumn(1)  # Size
        self.tree_view.hideColumn(2)  # Type
        self.tree_view.hideColumn(3)  # Date Modified
        
        # Single-click to open files (more responsive UX)
        try:
            self.tree_view.clicked.connect(self.open_from_browser)
        except Exception:
            self.tree_view.doubleClicked.connect(self.open_from_browser)
        
        self.file_browser.setWidget(self.tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_browser)
        
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.line_col_label = QLabel("Line: 1, Col: 1")
        self.encoding_label = QLabel("UTF-8")
        self.syntax_label = QLabel("Plain Text")
        
        self.status_bar.addPermanentWidget(self.line_col_label)
        self.status_bar.addPermanentWidget(self.encoding_label)
        self.status_bar.addPermanentWidget(self.syntax_label)
        
    def update_status_bar(self):
        # status bar widgets may not be created yet
        if not hasattr(self, 'line_col_label'):
            return
        editor = self.tab_widget.currentWidget()
        if editor and isinstance(editor, EditorWidget):
            # Update line and column
            line, col = editor.getCursorPosition()
            self.line_col_label.setText(f"Line: {line + 1}, Col: {col + 1}")
            
            # Update syntax
            if hasattr(editor, 'lexer') and editor.lexer():
                self.syntax_label.setText(editor.lexer().__class__.__name__[8:])
            else:
                self.syntax_label.setText("Plain Text")
                
    def handle_external_file_change(self, file_path):
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'file_path') and editor.file_path == file_path:
                reply = QMessageBox.question(
                    self,
                    "File Changed",
                    f"The file '{file_path}' has been modified externally.\nDo you want to reload it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.load_file(file_path)

    def toggle_file_browser(self):
        """Toggle the visibility of the file browser dock widget.

        If the file browser hasn't been created yet this will attempt to initialize it.
        """
        if hasattr(self, 'file_browser') and self.file_browser is not None:
            self.file_browser.setVisible(not self.file_browser.isVisible())
            return
        try:
            self.setup_file_browser()
        except Exception:
            pass
    def open_from_browser(self, index):
        # support both native QFileSystemModel and custom model
        if getattr(self, '_fs_model_type', 'native') == 'native':
            file_path = self.file_system.filePath(index)
            if self.file_system.isDir(index):
                return
            self.load_file(file_path)
        else:
            item = self.file_system.itemFromIndex(index)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if os.path.isdir(file_path):
                return
            self.load_file(file_path)
        
    def start_auto_save(self):
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_all)
        interval = self.settings.editor['auto_save_interval'] * 60 * 1000  # Convert minutes to milliseconds
        self.auto_save_timer.start(interval)

    def refresh_browser_path(self, path=None):
        """Refresh the file browser for the given path. Works with native QFileSystemModel or custom model."""
        if not path:
            path = getattr(self, 'workspace_root', QDir.currentPath())
        if getattr(self, '_fs_model_type', 'native') == 'native':
            try:
                idx = self.file_system.index(path)
                self.file_system.refresh(idx)
            except Exception:
                pass
        else:
            # rebuild custom model rooted at workspace or provided path
            try:
                from PyQt6.QtGui import QStandardItemModel, QStandardItem
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Name'])
                root_item = model.invisibleRootItem()
                def add_children(parent_item, p):
                    try:
                        for name in sorted(os.listdir(p)):
                            full = os.path.join(p, name)
                            item = QStandardItem(name)
                            item.setData(full, Qt.ItemDataRole.UserRole)
                            parent_item.appendRow(item)
                            if os.path.isdir(full):
                                add_children(item, full)
                    except Exception:
                        pass
                add_children(root_item, path)
                self.file_system = model
                self.tree_view.setModel(self.file_system)
            except Exception:
                pass
        
    def auto_save_all(self):
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if (hasattr(editor, 'file_path') and 
                editor.file_path and 
                editor.isModified()):
                self.save_file_for_editor(editor)
                
    def show_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.apply_settings()
            
    def apply_settings(self):
        # Apply settings to all editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, EditorWidget):
                editor.apply_settings()
                
        # Apply interface settings (guard toolbar in case it's been removed)
        try:
            if hasattr(self, 'toolbar'):
                self.toolbar.setVisible(self.settings.interface['toolbar_visible'])
        except Exception:
            pass
        try:
            if hasattr(self, 'status_bar'):
                self.status_bar.setVisible(self.settings.interface['show_status_bar'])
        except Exception:
            pass
        try:
            if hasattr(self, 'file_browser'):
                self.file_browser.setVisible(self.settings.interface['show_file_browser'])
        except Exception:
            pass
        
        # Apply tab position
        # QTabWidget exposes TabPosition enum; use that instead of Qt.TabPosition
        positions = {
            'top': QTabWidget.TabPosition.North,
            'bottom': QTabWidget.TabPosition.South,
            'left': QTabWidget.TabPosition.West,
            'right': QTabWidget.TabPosition.East
        }
        # guard against invalid setting value
        pos_key = self.settings.interface.get('tab_position', 'top')
        pos = positions.get(pos_key, QTabWidget.TabPosition.North)
        try:
            self.tab_widget.setTabPosition(pos)
        except Exception:
            # fallback: ignore if the underlying Qt binding expects a different value
            pass
        
        # Update auto-save
        if self.settings.editor['auto_save']:
            self.start_auto_save()
        elif hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()
        
    # ----- Workspace / File Browser helpers -----
    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder as Workspace", QDir.currentPath())
        if not folder:
            return
        self.workspace_root = folder
        # update model depending on type
        if getattr(self, '_fs_model_type', 'native') == 'native':
            try:
                self.file_system.setRootPath(folder)
                self.tree_view.setRootIndex(self.file_system.index(folder))
            except Exception:
                pass
        else:
            # rebuild custom model rooted at folder
            try:
                from PyQt6.QtGui import QStandardItemModel, QStandardItem
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Name'])
                root_item = model.invisibleRootItem()
                def add_children(parent_item, path):
                    try:
                        for name in sorted(os.listdir(path)):
                            full = os.path.join(path, name)
                            item = QStandardItem(name)
                            item.setData(full, Qt.ItemDataRole.UserRole)
                            parent_item.appendRow(item)
                            if os.path.isdir(full):
                                add_children(item, full)
                    except Exception:
                        pass
                add_children(root_item, folder)
                self.file_system = model
                self.tree_view.setModel(self.file_system)
            except Exception:
                pass
        # monitor folder files: add existing open files to monitor
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if hasattr(ed, 'file_path') and ed.file_path:
                try:
                    self.file_monitor.add_file(ed.file_path)
                except Exception:
                    pass

    def setup_file_browser(self):
        # existing setup preserved above; enable context menu
        self.file_browser = QDockWidget("Files", self)
        self.file_browser.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        # Create file system model (import lazily for compatibility)
        try:
            from PyQt6.QtWidgets import QFileSystemModel
            self.file_system = QFileSystemModel()
            self.file_system.setRootPath(QDir.currentPath())
            # Create tree view
            self.tree_view = QTreeView()
            self.tree_view.setModel(self.file_system)
            self.tree_view.setRootIndex(self.file_system.index(QDir.currentPath()))
            self._fs_model_type = 'native'
        except Exception:
            # Fallback: build a simple tree model using QStandardItemModel
            from PyQt6.QtGui import QStandardItemModel, QStandardItem
            self._fs_model_type = 'custom'
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(['Name'])
            root_item = model.invisibleRootItem()
            def add_children(parent_item, path):
                try:
                    for name in sorted(os.listdir(path)):
                        full = os.path.join(path, name)
                        item = QStandardItem(name)
                        item.setData(full, Qt.ItemDataRole.UserRole)
                        parent_item.appendRow(item)
                        if os.path.isdir(full):
                            add_children(item, full)
                except Exception:
                    pass
            add_children(root_item, QDir.currentPath())
            self.tree_view = QTreeView()
            self.tree_view.setModel(model)
            # make items slightly smaller and compact
            try:
                from PyQt6.QtCore import QSize
                self.tree_view.setIconSize(QSize(14, 14))
                self.tree_view.setStyleSheet('QTreeView::item { padding: 4px 6px; }')
            except Exception:
                pass
            self.file_system = model
        self.tree_view.hideColumn(1)  # Size
        self.tree_view.hideColumn(2)  # Type
        self.tree_view.hideColumn(3)  # Date Modified
        
        # connect single-click open for native model too
        try:
            self.tree_view.clicked.connect(self.open_from_browser)
        except Exception:
            self.tree_view.doubleClicked.connect(self.open_from_browser)
        # enable right-click context menu
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_file_tree_context_menu)
        
        self.file_browser.setWidget(self.tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_browser)
        # slightly animate opening/closing via QTimer hooks when toggled
        try:
            self.file_browser.visibilityChanged.connect(lambda visible: None)
        except Exception:
            pass

    def on_file_tree_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return
        # resolve path depending on model type
        if getattr(self, '_fs_model_type', 'native') == 'native':
            path = self.file_system.filePath(index)
        else:
            item = self.file_system.itemFromIndex(index)
            path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        open_act = menu.addAction("Open")
        if os.path.isdir(path):
            new_file_act = menu.addAction("New File")
            new_folder_act = menu.addAction("New Folder")
        else:
            reveal_act = menu.addAction("Reveal in Explorer")
            rename_act = menu.addAction("Rename")
            delete_act = menu.addAction("Delete")

        action = menu.exec(self.tree_view.viewport().mapToGlobal(pos))
        if action is None:
            return
        text = action.text()
        if text == "Open":
            if os.path.isdir(path):
                # expand
                self.tree_view.setExpanded(index, True)
            else:
                self.load_file(path)
        elif text == "New File":
            name, ok = QFileDialog.getSaveFileName(self, "New File", os.path.join(path, "newfile.txt"))
            if ok and name:
                open(name, 'w', encoding='utf-8').close()
                # refresh model or rebuild custom model
                self.refresh_browser_path(path)
        elif text == "New Folder":
            folder_name = os.path.join(path, "new_folder")
            try:
                os.makedirs(folder_name, exist_ok=True)
                self.refresh_browser_path(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        elif text == "Rename":
            new_name, ok = QFileDialog.getSaveFileName(self, "Rename To", path)
            if ok and new_name:
                try:
                    os.rename(path, new_name)
                    parent = os.path.dirname(new_name)
                    self.refresh_browser_path(parent)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
        elif text == "Delete":
            try:
                if os.path.isdir(path):
                    os.rmdir(path)
                else:
                    os.remove(path)
                parent = os.path.dirname(path)
                self.refresh_browser_path(parent)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        elif text == "Reveal in Explorer":
            # open in file explorer
            os.startfile(os.path.dirname(path))

    # ----- Terminal integration -----
    def setup_terminal_dock(self):
        # create terminal dock with tabbed terminals
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        from PyQt6.QtWidgets import QTabWidget
        self.terminal_tabs = QTabWidget()
        # allow closing tabs
        self.terminal_tabs.setTabsClosable(True)
        self.terminal_tabs.tabCloseRequested.connect(self._close_terminal_tab)
        self.terminal_dock.setWidget(self.terminal_tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)
        # show terminal by default (user can toggle)
        self.terminal_dock.setVisible(True)

    def new_terminal(self):
        if not hasattr(self, 'terminal_tabs'):
            self.setup_terminal_dock()
        term = TerminalWidget(shell=self.settings.editor.get('shell', 'powershell'))
        # apply font
        try:
            from PyQt6.QtGui import QFont
            f = QFont(self.settings.editor.get('font_family', 'Consolas'), int(self.settings.editor.get('font_size', 12)))
            term.set_font(f)
        except Exception:
            pass
        # apply theme colors to terminal if available
        try:
            colors = self.theme_manager.get_current_theme().colors
            term.apply_theme(colors)
        except Exception:
            pass
        idx = self.terminal_tabs.addTab(term, "Terminal")
        self.terminal_tabs.setCurrentIndex(idx)
        return term

    def split_terminal(self):
        # replace the current tab content with a splitter containing two terminals
        if not hasattr(self, 'terminal_tabs'):
            self.setup_terminal_dock()
        cur_idx = self.terminal_tabs.currentIndex()
        if cur_idx < 0:
            self.new_terminal()
            return
        cur_widget = self.terminal_tabs.widget(cur_idx)
        from PyQt6.QtWidgets import QSplitter, QWidget, QHBoxLayout
        # create splitter and put existing terminal on left and new on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # reparent existing terminal into splitter
        try:
            self.terminal_tabs.removeTab(cur_idx)
        except Exception:
            pass
        splitter.addWidget(cur_widget)
        new_term = TerminalWidget(shell=self.settings.editor.get('shell', 'powershell'))
        try:
            from PyQt6.QtGui import QFont
            f = QFont(self.settings.editor.get('font_family', 'Consolas'), int(self.settings.editor.get('font_size', 12)))
            new_term.set_font(f)
        except Exception:
            pass
        splitter.addWidget(new_term)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter)
        # add as a tab
        idx = self.terminal_tabs.addTab(container, "Terminal (Split)")
        self.terminal_tabs.setCurrentIndex(idx)

    def toggle_terminal(self):
        if not hasattr(self, 'terminal_dock'):
            self.setup_terminal_dock()
        try:
            vis = not self.terminal_dock.isVisible()
            # animate slide from hidden to visible and vice versa
            if vis:
                self.terminal_dock.setVisible(True)
                try:
                    geom = self.terminal_dock.geometry()
                    start = geom.translated(0, geom.height())
                    slide_widget(self.terminal_dock, start, geom, duration=280)
                except Exception:
                    pass
            else:
                try:
                    geom = self.terminal_dock.geometry()
                    end = geom.translated(0, geom.height())
                    slide_widget(self.terminal_dock, geom, end, duration=220)
                except Exception:
                    pass
                # hide after short delay to allow animation to run
                QTimer.singleShot(240, lambda: self.terminal_dock.setVisible(False))
        except Exception:
            self.terminal_dock.setVisible(not self.terminal_dock.isVisible())

    def _close_terminal_tab(self, index:int):
        # close tab and kill any running processes inside
        widget = self.terminal_tabs.widget(index)
        # try to find TerminalWidget instances inside and kill
        try:
            # if container with splitter
            from PyQt6.QtWidgets import QSplitter
            if isinstance(widget, QSplitter) or widget.findChild(QSplitter) is not None:
                # iterate children
                for child in widget.findChildren(TerminalWidget):
                    try:
                        child.kill()
                    except Exception:
                        pass
            else:
                # single terminal case
                if isinstance(widget, TerminalWidget):
                    try:
                        widget.kill()
                    except Exception:
                        pass
        except Exception:
            # generic kill: find TerminalWidget instances
            for child in widget.findChildren(TerminalWidget):
                try:
                    child.kill()
                except Exception:
                    pass
        try:
            self.terminal_tabs.removeTab(index)
        except Exception:
            pass

    # ----- Run / Debug -----
    def run_debug_current_file(self):
        editor = self.tab_widget.currentWidget()
        if not editor or not isinstance(editor, EditorWidget):
            return
        if not hasattr(editor, 'file_path') or not editor.file_path:
            # prompt to save
            self.save_file()
        file_path = getattr(editor, 'file_path', None)
        if not file_path:
            QMessageBox.warning(self, "No file", "Please save the file before running")
            return
        # make sure terminal exists
        term = self.new_terminal()
        # run python with unbuffered output
        term.run_once(f'python -u "{file_path}"')

    # ----- Find in Files -----
    def show_find_in_files(self):
        root = getattr(self, 'workspace_root', QDir.currentPath())
        dlg = FindInFilesDialog(root, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            path = getattr(dlg, 'selected_path', None)
            lineno = getattr(dlg, 'selected_line', None)
            if path:
                self.load_file(path)
                # navigate to line
                ed = self.tab_widget.currentWidget()
                if hasattr(ed, 'setCursorPosition') and lineno:
                    ed.setCursorPosition(lineno - 1, 0)

    def show_quick_open(self):
        try:
            from .quick_open import QuickOpenDialog
            root = getattr(self, 'workspace_root', QDir.currentPath())
            dlg = QuickOpenDialog(root, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                sel = dlg.get_selected()
                if sel:
                    self.load_file(sel)
        except Exception:
            pass

    def goto_line(self):
        try:
            from PyQt6.QtWidgets import QInputDialog
            editor = self.tab_widget.currentWidget()
            if not editor or not isinstance(editor, EditorWidget):
                return
            num, ok = QInputDialog.getInt(self, 'Go to Line', 'Line number:', 1, 1, 1000000)
            if ok:
                try:
                    editor.setCursorPosition(num - 1, 0)
                except Exception:
                    pass
        except Exception:
            pass

    # ----- Utilities -----
    def save_file_for_editor(self, editor):
        try:
            if hasattr(editor, 'file_path') and editor.file_path:
                with open(editor.file_path, 'w', encoding='utf-8') as fh:
                    fh.write(editor.text())
                # mark not modified
                try:
                    editor.setModified(False)
                except Exception:
                    pass
                return True
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))
        return False

    def increase_font_size(self):
        try:
            cur = int(self.settings.editor.get('font_size', 12))
            cur += 1
            self.settings.editor['font_size'] = cur
            # apply to all editors
            for i in range(self.tab_widget.count()):
                ed = self.tab_widget.widget(i)
                if isinstance(ed, EditorWidget):
                    ed.apply_settings()
        except Exception:
            pass

    def decrease_font_size(self):
        try:
            cur = int(self.settings.editor.get('font_size', 12))
            cur = max(8, cur - 1)
            self.settings.editor['font_size'] = cur
            for i in range(self.tab_widget.count()):
                ed = self.tab_widget.widget(i)
                if isinstance(ed, EditorWidget):
                    ed.apply_settings()
        except Exception:
            pass