from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog, QLineEdit, QPushButton, QLabel, QMenu
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerJavaScript,
                       QsciLexerHTML, QsciLexerCSS, QsciLexerXML, QsciLexerSQL,
                       QsciLexerJSON, QsciLexerYAML, QsciLexerMarkdown)
try:
    from PyQt6.Qsci import QsciLexerLua
except Exception:
    QsciLexerLua = None
try:
    from PyQt6.Qsci import QsciLexerCPP
except Exception:
    QsciLexerCPP = None
try:
    from PyQt6.Qsci import QsciLexerJava
except Exception:
    QsciLexerJava = None
try:
    from PyQt6.Qsci import QsciLexerBash
except Exception:
    QsciLexerBash = None
from core.autocomplete import AutoCompleter
from types import SimpleNamespace

class EditorWidget(QsciScintilla):
    content_changed = pyqtSignal()
    
    LEXERS = {
        'py': QsciLexerPython,
        'pyw': QsciLexerPython,
        'js': QsciLexerJavaScript,
        'html': QsciLexerHTML,
        'css': QsciLexerCSS,
        'xml': QsciLexerXML,
        'sql': QsciLexerSQL,
        'json': QsciLexerJSON,
        'yaml': QsciLexerYAML,
        'yml': QsciLexerYAML,
        'md': QsciLexerMarkdown
    }

    if QsciLexerLua:
        LEXERS.update({'lua': QsciLexerLua})
    if QsciLexerCPP:
        LEXERS.update({'c': QsciLexerCPP, 'cpp': QsciLexerCPP, 'h': QsciLexerCPP, 'hpp': QsciLexerCPP})
    if QsciLexerJava:
        LEXERS.update({'java': QsciLexerJava})
    if QsciLexerBash:
        LEXERS.update({'sh': QsciLexerBash, 'bash': QsciLexerBash})

    def __init__(self, settings=None):
        super().__init__()
        default = SimpleNamespace(
            editor={
                'font_family': 'Consolas',
                'font_size': 10,
                'tab_size': 4,
                'auto_save': False,
                'show_line_numbers': True
            },
            interface={},
            file_monitor={}
        )
        self.settings = settings or default
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.setup_editor()
        self.setup_autocomplete()
        self.setup_context_menu()
        # apply initial settings
        try:
            self.apply_settings()
        except Exception:
            pass
        
        # Connect signals
        try:
            self.textChanged.connect(self._on_text_changed_debounced)
        except Exception:
            pass

        # syntax checking debounce timer
        self._syntax_timer = QTimer()
        self._syntax_timer.setSingleShot(True)
        self._syntax_timer.timeout.connect(self.check_syntax)
        
        # Initialize theme
        self.update_theme()
        
    def update_theme(self, theme=None):
        """Update editor colors and styles based on theme."""
        try:
            # Get theme manager if not provided
            if theme is None:
                from core.theme_manager import ThemeManager
                theme = ThemeManager().get_current_theme()
            
            colors = theme.colors
            
            # Base colors - set paper (background). Avoid calling setColor which may override lexer-styles.
            bg_color = QColor(colors.get('editor_background', '#151a20'))
            fg_color = QColor(colors.get('editor_foreground', '#e6eef6'))
            try:
                # set the paper/background on the widget; avoid setting global foreground color which can force white text
                self.setPaper(bg_color)
            except Exception:
                pass
            
            # Selection colors
            sel_bg = QColor(colors.get('editor_selection', 'rgba(14, 165, 233, 0.2)'))
            sel_fg = QColor(colors.get('foreground', '#ffffff'))
            self.setSelectionBackgroundColor(sel_bg)
            self.setSelectionForegroundColor(sel_fg)
            
            # Caret and current line
            self.setCaretForegroundColor(QColor(colors.get('foreground', '#ffffff')))
            self.setCaretLineBackgroundColor(QColor(colors.get('editor_line', '#1a1f25')))
            self.setCaretLineVisible(True)
            
            # Margins
            self.setMarginsBackgroundColor(bg_color)
            self.setMarginsForegroundColor(QColor(colors.get('line_number', '#8ba1b5')))
            
            # If we have a lexer, update its colors
            current_lexer = self.lexer()
            if current_lexer:
                try:
                    if hasattr(current_lexer, 'setPaper'):
                        current_lexer.setPaper(bg_color)
                    if hasattr(current_lexer, 'setDefaultPaper'):
                        current_lexer.setDefaultPaper(bg_color)
                    # Update lexer default color only if the lexer supports it; do not call widget-level setColor
                    if hasattr(current_lexer, 'setDefaultColor'):
                        current_lexer.setDefaultColor(fg_color)
                except Exception:
                    pass
            
            # Re-apply syntax highlighting if we have a language set
            if hasattr(self, '_current_language') and self._current_language:
                self.set_lexer(self._current_language)
                
        except Exception as e:
            print(f"Error updating theme: {e}")
            # Set fallback dark colors
            try:
                bg_color = QColor('#151a20')
                fg_color = QColor('#e6eef6')
                try:
                    # set paper only; avoid setting widget-level foreground which can override lexer
                    self.setPaper(bg_color)
                except Exception:
                    pass
                try:
                    if self.lexer():
                        lex = self.lexer()
                        if hasattr(lex, 'setPaper'):
                            lex.setPaper(bg_color)
                        if hasattr(lex, 'setDefaultPaper'):
                            lex.setDefaultPaper(bg_color)
                        if hasattr(lex, 'setDefaultColor'):
                            lex.setDefaultColor(fg_color)
                except Exception:
                    pass
            except Exception:
                pass

    def setup_editor(self):
        """Set up the QScintilla editor with modern features and appearance."""
        try:
            # Basic configuration
            self.setUtf8(True)
            self.setEolMode(QsciScintilla.EolMode.EolUnix)
            
            # Modern editor appearance
            self.setMarginLineNumbers(0, True)
            self.setMarginWidth(0, "00000")
            
            # Initial dark theme colors (will be updated by theme manager)
            self.setMarginsBackgroundColor(QColor("#151a20"))
            self.setMarginsForegroundColor(QColor("#8ba1b5"))
            self.setSelectionBackgroundColor(QColor("#264f78"))
            self.setSelectionForegroundColor(QColor("#ffffff"))
            self.setCaretForegroundColor(QColor("#ffffff"))
            self.setCaretWidth(2)
            
            # Advanced features (with fallbacks)
            self.setup_advanced_features()
            
        except Exception as e:
            print(f"Error setting up editor: {e}")
            
    def setup_advanced_features(self):
        """Set up advanced editor features with proper error handling."""
        # Multiple selection support
        try:
            if hasattr(self, 'setMultipleSelection'):
                self.setMultipleSelection(True)
                if hasattr(self, 'setAdditionalSelectionTyping'):
                    self.setAdditionalSelectionTyping(True)
        except Exception as e:
            print(f"Note: Multiple selection not supported: {e}")

        # Smooth scrolling
        try:
            self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, 1)
            self.SendScintilla(QsciScintilla.SCI_SETMOUSEWHEELCAPTURES, 1)
        except Exception as e:
            print(f"Note: Smooth scrolling not supported: {e}")

        # Modern selection and caret
        try:
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor("#282828"))
            self.setCaretWidth(2)
            self.setCaretForegroundColor(QColor("#FFFFFF"))
        except Exception as e:
            print(f"Error setting caret appearance: {e}")

        # Enable features based on settings
        try:
            self.setup_margins()
            self.setup_folding()
            self.setup_indicators()
        except Exception as e:
            print(f"Error setting up advanced features: {e}")
    
        # Enable brace matching with custom colors
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setMatchedBraceBackgroundColor(QColor("#3a3a3a"))
        self.setMatchedBraceForegroundColor(QColor("#FFFFFF"))
    
        # Modern indentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationGuidesBackgroundColor(QColor("#2d2d2d"))
        self.setIndentationGuidesForegroundColor(QColor("#3a3a3a"))
    
        # Smooth selection
        self.SendScintilla(QsciScintilla.SCI_SETMOUSESELECTIONRECTANGULARSWITCH, 1)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, 1)
    
        # Modern line wrapping
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagNone)
    
        # Enable undo/redo
        self.setReadOnly(False)

        
    def setup_margins(self):
        # Line numbers margin
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#808080"))
        
        # Folding margin
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(2, 15)
        self.setMarginSensitivity(2, True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle, 2)
        
    def setup_folding(self):
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(QColor("#2B2B2B"), QColor("#2B2B2B"))
        
    def setup_indicators(self):
        # Setup search indicator
        self.search_indicator = self.indicatorDefine(
            QsciScintilla.IndicatorStyle.FullBoxIndicator)
        self.setIndicatorForegroundColor(
            QColor("#FFD700"), self.search_indicator)
        self.setIndicatorDrawUnder(True, self.search_indicator)
        
        # Setup error indicator
        self.error_indicator = self.indicatorDefine(
            QsciScintilla.IndicatorStyle.SquiggleIndicator)
        self.setIndicatorForegroundColor(
            QColor("#FF0000"), self.error_indicator)

    def setup_autocomplete(self):
        self.autocompleter = AutoCompleter(self)
        # We call update_completions via a small debounce on text change
        try:
            self.textChanged.connect(lambda: self.autocompleter.update_completions(120))
        except Exception:
            pass

    def _on_text_changed_debounced(self):
        # start syntax check timer and notify content changed
        try:
            self._syntax_timer.start(600)
        except Exception:
            pass
        try:
            self.content_changed.emit()
        except Exception:
            pass

    def on_text_changed(self):
        # kept for compatibility with code calling this directly
        self._on_text_changed_debounced()

    def setup_context_menu(self):
        # basic context menu
        try:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            from PyQt6.QtGui import QAction
            cut = QAction('Cut', self)
            cut.triggered.connect(self.cut)
            copy = QAction('Copy', self)
            copy.triggered.connect(self.copy)
            paste = QAction('Paste', self)
            paste.triggered.connect(self.paste)
            self.addAction(cut)
            self.addAction(copy)
            self.addAction(paste)
        except Exception:
            pass

    def apply_settings(self):
        # apply font and tab settings
        try:
            # prefer a programming font if available
            fam = self.settings.editor.get('font_family', 'Fira Code')
            # fall back to Consolas if Fira Code not present
            try:
                ftest = QFont(fam, int(self.settings.editor.get('font_size', 12)))
                if ftest.family() != fam:
                    fam = 'Consolas'
            except Exception:
                fam = 'Consolas'
            f = QFont(fam, int(self.settings.editor.get('font_size', 12)))
            # enable slight smoothing
            try:
                f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            except Exception:
                pass
            self.setFont(f)
        except Exception:
            pass
        try:
            tab_size = int(self.settings.editor.get('tab_size', 4))
            self.setTabWidth(tab_size)
            self.setIndentationsUseTabs(not self.settings.editor.get('use_spaces', True))
        except Exception:
            pass
        # apply theme colors (if available) to margins and selection
        try:
            from core.theme_manager import ThemeManager
            tm = ThemeManager()
            # try to use theme specified in settings
            theme_name = None
            try:
                theme_name = self.settings.theme.get('name')
            except Exception:
                theme_name = None
            if theme_name:
                try:
                    tm.set_theme(theme_name)
                except Exception:
                    pass
            colors = tm.get_current_theme().colors
            # margins / line numbers
            if 'line_number' in colors:
                try:
                    self.setMarginsForegroundColor(QColor(colors['line_number']))
                except Exception:
                    pass
            # editor paper/foreground
            try:
                if 'editor_background' in colors:
                    self.setPaper(QColor(colors['editor_background']))
                if 'editor_foreground' in colors:
                    # prefer to set lexer default color if a lexer is attached so lexer styles win
                    try:
                        lex = self.lexer()
                        if lex and hasattr(lex, 'setDefaultColor'):
                            lex.setDefaultColor(QColor(colors['editor_foreground']))
                        else:
                            self.setColor(QColor(colors['editor_foreground']))
                    except Exception:
                        try:
                            self.setColor(QColor(colors['editor_foreground']))
                        except Exception:
                            pass
                # selection and caret line
                if 'editor_selection' in colors:
                    try:
                        self.setSelectionBackgroundColor(QColor(colors['editor_selection']))
                    except Exception:
                        pass
                if 'editor_line' in colors:
                    try:
                        self.setCaretLineVisible(True)
                        self.setCaretLineBackgroundColor(QColor(colors['editor_line']))
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass

    def on_text_changed(self):
        try:
            self.content_changed.emit()
        except Exception:
            pass

    def auto_save(self):
        # placeholder for auto-save per-editor
        try:
            if hasattr(self, 'file_path') and self.file_path:
                with open(self.file_path, 'w', encoding='utf-8') as fh:
                    fh.write(self.text())
        except Exception:
            pass

    def check_syntax(self):
        """Quick syntax check using ast.parse. Marks error lines with the error indicator."""
        try:
            import ast
            src = self.text()
            # clear previous error indicators
            try:
                length = len(src)
                self.clearIndicatorRange(0, length, self.error_indicator)
            except Exception:
                pass
            try:
                ast.parse(src)
                return
            except SyntaxError as e:
                try:
                    lineno = getattr(e, 'lineno', None)
                    if lineno is None:
                        return
                    # mark the whole line as error
                    start = self.positionFromLineIndex(lineno - 1, 0)
                    # compute end as start of next line or end of doc
                    try:
                        end = self.positionFromLineIndex(lineno, 0)
                    except Exception:
                        end = len(src)
                    length = max(1, end - start)
                    try:
                        self.fillIndicatorRange(start, length, self.error_indicator)
                    except Exception:
                        # older API may be indicatorFillRange
                        try:
                            self.indicatorFillRange(start, length)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    def set_lexer(self, file_extension):
        """Set up syntax highlighting lexer for given file extension."""
        from core.console import section, info, success, warning, error, debug
        
        try:
            # Store current language for theme updates
            self._current_language = file_extension
            
            # Clean and normalize extension
            ext = (file_extension or '').lower()
            if ext.startswith('.'):
                ext = ext[1:]
            
            section(f"Lexer Setup for .{ext}")
            
            # Get appropriate lexer class
            LexerClass = self.LEXERS.get(ext)
            if not LexerClass:
                warning(f"No lexer available for .{ext} files")
                return
                
            # Create lexer instance and attach immediately so the editor can update UI promptly
            debug(f"Creating {LexerClass.__name__} instance...")
            lexer = LexerClass(self)
            try:
                # Attach basic lexer immediately (minimal work on main path)
                self.setLexer(lexer)
            except Exception:
                # fallback if setLexer signature differs
                try:
                    self.setLexer(lexer)
                except Exception:
                    pass
            
            # Get theme and font settings
            from core.theme_manager import ThemeManager
            theme = ThemeManager().get_current_theme()
            colors = theme.colors
            debug(f"Using theme: {theme.name}")
            
            try:
                font_family = self.settings.editor.get('font_family', 'Consolas')
                font_size = int(self.settings.editor.get('font_size', 12))
                qfont = QFont(font_family, font_size)
                qfont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
                info(f"Using font: {font_family} {font_size}pt")
            except Exception as e:
                warning(f"Using default font due to error: {e}")
                qfont = QFont('Consolas', 10)
            
            # Apply base colors (defer heavier styling so UI can remain responsive)
            bg_color = QColor(colors.get('editor_background', '#1E1E1E'))
            fg_color = QColor(colors.get('editor_foreground', '#D4D4D4'))
            debug(f"Base colors - FG: {colors.get('editor_foreground')} BG: {colors.get('editor_background')}")

            # Quickly set some defaults on the lexer (safe operations)
            try:
                if hasattr(lexer, 'setDefaultColor'):
                    lexer.setDefaultColor(fg_color)
                if hasattr(lexer, 'setDefaultPaper'):
                    lexer.setDefaultPaper(bg_color)
                if hasattr(lexer, 'setDefaultFont'):
                    lexer.setDefaultFont(qfont)
            except Exception:
                pass

            # Defer file-type specific and per-style configuration to let the UI breathe.
            def finish_lexer_config():
                try:
                    if ext in ('py', 'pyw'):
                        info("Configuring Python-specific lexer settings...")
                        from .lexers import python_lexer
                        python_lexer.apply_python_lexer(lexer, colors, qfont)

                    debug("Finalizing lexer application")
                    # Ensure that the editor really has the lexer attached
                    try:
                        self.setLexer(lexer)
                    except Exception:
                        pass
                    success(f"Lexer successfully configured for .{ext} files")
                    # Dump lexer diagnostic info to help debugging color/application issues
                    try:
                        self._dump_lexer_info(lexer)
                    except Exception:
                        pass
                except Exception as e:
                    error(f"Error during deferred lexer config: {e}")

            # schedule deferred configuration a short time in the event loop
            try:
                QTimer.singleShot(30, finish_lexer_config)
            except Exception:
                finish_lexer_config()
            
            # success will be reported by deferred finalizer above; we keep a lightweight immediate check
            if self.lexer() is None:
                error("Lexer not properly set (immediate check)")
                
        except Exception as e:
            error(f"Failed to set up lexer: {str(e)}")
            # Attempt to restore a basic lexer
            try:
                warning("Attempting to restore basic lexer...")
                basic_lexer = LexerClass(self)
                self.setLexer(basic_lexer)
                info("Basic lexer restored")
            except Exception as e:
                error(f"Could not set up basic lexer: {str(e)}")
            
        except Exception as e:
            print(f"Error setting up lexer: {e}")

    def _dump_lexer_info(self, lexer):
        """Dump basic lexer diagnostic info (class and per-style color values) to console."""
        try:
            from core.console import info, debug
            info(f"Lexer diagnostics for: {lexer.__class__.__name__}")
            # common Python style names
            names = [
                'Default', 'Comment', 'Number', 'DoubleQuotedString', 'SingleQuotedString',
                'Keyword', 'TripleSingleQuotedString', 'TripleDoubleQuotedString', 'ClassName',
                'FunctionMethodName', 'Operator', 'Identifier', 'CommentBlock', 'UnclosedString',
                'HighlightedIdentifier', 'Decorator'
            ]
            for n in names:
                try:
                    style_id = getattr(QsciLexerPython, n, None)
                except Exception:
                    style_id = None
                if style_id is None:
                    continue
                color_val = None
                try:
                    # try several getter names depending on Qsci version
                    if hasattr(lexer, 'color'):
                        c = lexer.color(style_id)
                        if c is not None:
                            try:
                                color_val = c.name()
                            except Exception:
                                color_val = str(c)
                    elif hasattr(lexer, 'defaultColor'):
                        c = lexer.defaultColor()
                        try:
                            color_val = c.name()
                        except Exception:
                            color_val = str(c)
                except Exception as e:
                    color_val = f"error:{e}"
                debug(f"Style {n} ({style_id}): {color_val}")
        except Exception:
            pass

    def show_find_dialog(self):
        dialog = FindDialog(self)
        dialog.exec()

    def show_replace_dialog(self):
        dialog = ReplaceDialog(self)
        dialog.exec()

class FindDialog(QDialog):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Find")
        layout = QVBoxLayout()
        
        self.find_input = QLineEdit()
        self.find_button = QPushButton("Find Next")
        self.find_button.clicked.connect(self.find_text)
        
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_input)
        layout.addWidget(self.find_button)
        
        self.setLayout(layout)

    def find_text(self):
        text = self.find_input.text()
        self.editor.findFirst(
            text,        # Text to find
            False,      # Regular expression
            True,       # Case sensitive
            True,       # Whole word only
            True,       # Wrap around document
            True        # Forward search
        )

class ReplaceDialog(QDialog):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Replace")
        layout = QVBoxLayout()
        
        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.find_button = QPushButton("Find Next")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        
        self.find_button.clicked.connect(self.find_text)
        self.replace_button.clicked.connect(self.replace_text)
        self.replace_all_button.clicked.connect(self.replace_all)
        
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_input)
        layout.addWidget(QLabel("Replace with:"))
        layout.addWidget(self.replace_input)
        layout.addWidget(self.find_button)
        layout.addWidget(self.replace_button)
        layout.addWidget(self.replace_all_button)
        
        self.setLayout(layout)

    def find_text(self):
        text = self.find_input.text()
        self.editor.findFirst(
            text,        # Text to find
            False,      # Regular expression
            True,       # Case sensitive
            True,       # Whole word only
            True,       # Wrap around document
            True        # Forward search
        )

    def replace_text(self):
        if self.editor.hasSelectedText():
            self.editor.replaceSelectedText(self.replace_input.text())
            self.find_text()

    def replace_all(self):
        text = self.find_input.text()
        replacement = self.replace_input.text()
        count = 0
        
        # Start from the beginning
        self.editor.setCursorPosition(0, 0)
        
        while self.editor.findFirst(text, False, True, True, True, True):
            self.editor.replaceSelectedText(replacement)
            count += 1
        pass