from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerHTML
from .base_lexer import BaseLexer


class PHPLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerHTML:
        lexer = QsciLexerHTML()  # PHP uses HTML lexer with PHP support
        
        # VS Code Dark+ inspired colors for PHP
        colors = {
            'keyword': '#569CD6',     # blue for keywords
            'variable': '#9CDCFE',    # light blue for variables
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'function': '#DCDCAA',    # gold for functions
            'class': '#4EC9B0',       # turquoise for classes
            'operator': '#D4D4D4',    # light gray for operators
            'html': '#808080',        # gray for HTML
            'tag': '#569CD6',         # blue for HTML tags
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors for PHP sections
        lexer.setColor(QColor(colors['keyword']), QsciLexerHTML.StyleClass.PHPKeyword)
        lexer.setColor(QColor(colors['variable']), QsciLexerHTML.StyleClass.PHPVariable)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.PHPDoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.PHPSingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerHTML.StyleClass.PHPNumber)
        lexer.setColor(QColor(colors['comment']), QsciLexerHTML.StyleClass.PHPComment)
        lexer.setColor(QColor(colors['comment']), QsciLexerHTML.StyleClass.PHPCommentLine)
        lexer.setColor(QColor(colors['operator']), QsciLexerHTML.StyleClass.PHPOperator)
        
        # Apply colors for HTML sections
        lexer.setColor(QColor(colors['html']), QsciLexerHTML.StyleClass.Default)
        lexer.setColor(QColor(colors['tag']), QsciLexerHTML.StyleClass.Tag)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.HTMLDoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerHTML.StyleClass.HTMLSingleQuotedString)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.php', '.phtml', '.php3', '.php4', '.php5', '.php7', '.phps']
    
    def name(self) -> str:
        return "PHP"