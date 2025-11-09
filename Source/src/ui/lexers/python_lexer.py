from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython


def apply_python_lexer(lexer: QsciLexerPython, colors: dict = None, font: QFont = None):
    """Apply VS Code Dark+ style to a QsciLexerPython instance."""
    from core.console import section, info, success, warning, error, debug

    section("Python Lexer Configuration")

    # Validate inputs
    if not isinstance(lexer, QsciLexerPython):
        error(f"Invalid lexer type {type(lexer)}")
        return

    debug("Initializing lexer configuration...")
    # Initialize colors dict
    colors = colors or {}

    # VS Code Dark+ color scheme
    defaults = {
        'keyword': '#C586C0',
        'builtin': '#DCDCAA',
        'string': '#CE9178',
        'number': '#B5CEA8',
        'comment': '#6A9955',
        'decorator': '#C586C0',
        'operator': '#D4D4D4',
        'class': '#4EC9B0',
        'function': '#DCDCAA',
        'identifier': '#9CDCFE',
        'background': '#1E1E1E',
        'foreground': '#D4D4D4',
        'caret': '#AEAFAD',
        'selection_bg': '#264F78',
        'line_highlight': '#2A2A2A',
        'error': '#F44747',
        'warning': '#CCA700',
    }

    cfg = defaults.copy()
    cfg.update({k: v for k, v in (colors or {}).items() if v})

    # Apply base foreground/background colors
    try:
        lexer.setDefaultColor(QColor(cfg['foreground']))
        lexer.setPaper(QColor(cfg['background']))
    except Exception:
        pass

    # Set default colors and font
    try:
        lexer.setDefaultColor(QColor(cfg['foreground']))
        lexer.setDefaultPaper(QColor(cfg['background']))
        lexer.setDefaultFont(font or QFont('Consolas', 10))
    except Exception:
        pass

    # Map style constants to colors
    style_colors = {
        QsciLexerPython.Default: cfg['foreground'],
        QsciLexerPython.Comment: cfg['comment'],
        QsciLexerPython.Number: cfg['number'],
        QsciLexerPython.DoubleQuotedString: cfg['string'],
        QsciLexerPython.SingleQuotedString: cfg['string'],
        QsciLexerPython.Keyword: cfg['keyword'],
        QsciLexerPython.TripleSingleQuotedString: cfg['string'],
        QsciLexerPython.TripleDoubleQuotedString: cfg['string'],
        QsciLexerPython.ClassName: cfg['class'],
        QsciLexerPython.FunctionMethodName: cfg['function'],
        QsciLexerPython.Operator: cfg['operator'],
        QsciLexerPython.Identifier: cfg['identifier'],
        QsciLexerPython.CommentBlock: cfg['comment'],
        QsciLexerPython.UnclosedString: cfg['string'],
        QsciLexerPython.HighlightedIdentifier: cfg['builtin'],
        QsciLexerPython.Decorator: cfg['decorator']
    }

    # Apply style colors
    for style_id, color in style_colors.items():
        try:
            fg_color = QColor(color)
            bg_color = QColor(cfg['background'])
            if not fg_color.isValid():
                debug(f"Invalid color {color} for style {style_id}")
                continue
            lexer.setColor(fg_color, style_id)
            lexer.setPaper(bg_color, style_id)
            if font:
                lexer.setFont(font, style_id)
        except Exception as e:
            debug(f"Error setting style {style_id}: {e}")

    # Apply global font if provided
    try:
        if font:
            lexer.setFont(font)
    except Exception:
        pass

    # Final background adjustments - ensure default colors are set
    try:
        lexer.setDefaultPaper(QColor(cfg['background']))
        lexer.setDefaultColor(QColor(cfg['foreground']))
        # Make sure caret and selection colors are set where supported
        try:
            # avoid calling setColor without a style id which can overwrite per-style colors
            # lexer implementations may support caret color separately; skip global setColor here
            lexer.setPaper(QColor(cfg['background']))
        except Exception:
            pass
    except Exception:
        pass

    return lexer
