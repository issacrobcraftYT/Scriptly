from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerHTML
from .base_lexer import BaseLexer


class HTMLLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerHTML:
        lexer = QsciLexerHTML()
        
        # VS Code Dark+ inspired colors for HTML
        colors = {
            'tag': '#569CD6',         # blue for tags
            'attribute': '#9CDCFE',   # light blue for attributes
            'string': '#CE9178',      # coral for strings
            'comment': '#6A9955',     # green for comments
            'entity': '#D4D4D4',      # light gray for entities
            'script': '#DCDCAA',      # gold for script tags
            'style': '#C586C0',       # purple for style tags
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['tag']), QsciLexerHTML.StyleClass.Tag)
        lexer.setColor(QColor(colors['attribute']), QsciLexerHTML.StyleClass.Attribute)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['comment']), QsciLexerHTML.StyleClass.Comment)
        lexer.setColor(QColor(colors['entity']), QsciLexerHTML.StyleClass.Entity)
        lexer.setColor(QColor(colors['script']), QsciLexerHTML.StyleClass.Script)
        lexer.setColor(QColor(colors['style']), QsciLexerHTML.StyleClass.CDATA)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.html', '.htm', '.xhtml', '.vue', '.svelte']
    
    def name(self) -> str:
        return "HTML"