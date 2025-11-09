from PyQt6.QtGui import QColor, QFont

def apply_python_lexer(lexer, colors: dict = None, font: QFont = None):
    """
    Apply a Visual Studio Code Dark+ style to a QsciLexerPython instance.
    """
    if colors is None:
        colors = {}

    defaults = {
        'keyword': '#0ea5e9',     # Bright blue for keywords
        'builtin': '#38bdf8',     # Sky blue for builtins
        'string': '#ecc48d',      # Warm orange for strings
        'number': '#94e2d5',      # Cyan for numbers
        'comment': '#6aa97b',     # Muted green for comments
        'decorator': '#f0c4a9',   # Soft orange for decorators
        'operator': '#e6eef6',    # Light blue-grey for operators
        'class': '#38bdf8',       # Sky blue for classes
        'function': '#93c5fd',    # Light blue for functions
        'identifier': '#e6eef6',  # Light blue-grey for identifiers
        'background': '#151a20',  # Dark blue-grey background
        'foreground': '#e6eef6',  # Light blue-grey foreground
        'caret': '#ffffff',       # White caret
        'selection_bg': 'rgba(14, 165, 233, 0.2)'  # Transparent blue selection
    }

    cfg = defaults.copy()
    cfg.update({k: v for k, v in (colors or {}).items() if v})

    # Apply base foreground/background colors
    try:
        lexer.setDefaultColor(QColor(cfg['foreground']))
        lexer.setPaper(QColor(cfg['background']))
        lexer.setColor(QColor(cfg['foreground']))
    except Exception:
        pass

    # Apply syntax-specific colors dynamically
    try:
        cls = lexer.__class__
        for name in dir(cls):
            if not name[0].isupper():
                continue
            try:
                style_id = getattr(cls, name)
                if not isinstance(style_id, int):
                    continue
            except Exception:
                continue

            n = name.lower()
            color = None
            if 'keyword' in n or n == 'word':
                color = cfg['keyword']
            elif 'string' in n:
                color = cfg['string']
            elif 'comment' in n:
                color = cfg['comment']
            elif 'number' in n:
                color = cfg['number']
            elif 'decorator' in n:
                color = cfg['decorator']
            elif 'class' in n:
                color = cfg['class']
            elif 'function' in n or 'method' in n:
                color = cfg['function']
            elif 'identifier' in n or 'builtin' in n:
                color = cfg['builtin']
            elif 'operator' in n or 'punctuation' in n:
                color = cfg['operator']

            if color:
                try:
                    lexer.setColor(QColor(color), style_id)
                    if font:
                        lexer.setFont(font, style_id)
                except Exception:
                    pass
    except Exception:
        pass

    # Apply global font if provided
    try:
        if font:
            lexer.setFont(font)
    except Exception:
        pass

    # Final background adjustments
    try:
        lexer.setDefaultPaper(QColor(cfg['background']))
        lexer.setColor(QColor(cfg['caret']))
        lexer.setPaper(QColor(cfg['background']))
    except Exception:
        pass

    return lexer
