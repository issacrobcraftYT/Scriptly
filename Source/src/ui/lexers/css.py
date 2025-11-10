from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerCSS
from .base_lexer import BaseLexer


class CSSLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerCSS:
        lexer = QsciLexerCSS()
        
        # VS Code Dark+ inspired colors for CSS
        colors = {
            'tag': '#D7BA7D',        # tan for selectors
            'class': '#4EC9B0',      # turquoise for classes
            'id': '#569CD6',         # blue for IDs
            'property': '#9CDCFE',   # light blue for properties
            'value': '#CE9178',      # coral for values
            'number': '#B5CEA8',     # sage for numbers
            'unit': '#B5CEA8',       # sage for units
            'comment': '#6A9955',    # green for comments
            'important': '#569CD6',  # blue for !important
            'background': '#1E1E1E', # dark background
            'foreground': '#D4D4D4', # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['tag']), QsciLexerCSS.StyleClass.Tag)
        lexer.setColor(QColor(colors['class']), QsciLexerCSS.StyleClass.ClassSelector)
        lexer.setColor(QColor(colors['id']), QsciLexerCSS.StyleClass.IDSelector)
        lexer.setColor(QColor(colors['property']), QsciLexerCSS.StyleClass.Property)
        lexer.setColor(QColor(colors['value']), QsciLexerCSS.StyleClass.Value)
        lexer.setColor(QColor(colors['number']), QsciLexerCSS.StyleClass.CSS1Property)
        lexer.setColor(QColor(colors['unit']), QsciLexerCSS.StyleClass.CSS2Property)
        lexer.setColor(QColor(colors['comment']), QsciLexerCSS.StyleClass.Comment)
        lexer.setColor(QColor(colors['important']), QsciLexerCSS.StyleClass.Important)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.css', '.scss', '.sass', '.less']
    
    def name(self) -> str:
        return "CSS"