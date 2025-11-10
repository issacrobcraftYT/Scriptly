from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerBash
from .base_lexer import BaseLexer


class ShellLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerBash:
        lexer = QsciLexerBash()
        
        # VS Code Dark+ inspired colors for Shell scripts
        colors = {
            'keyword': '#C586C0',     # purple for keywords
            'command': '#DCDCAA',     # gold for commands
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'variable': '#9CDCFE',    # light blue for variables
            'operator': '#D4D4D4',    # light gray for operators
            'parameter': '#569CD6',   # blue for parameters
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerBash.StyleClass.Keyword)
        lexer.setColor(QColor(colors['command']), QsciLexerBash.StyleClass.Word)
        lexer.setColor(QColor(colors['string']), QsciLexerBash.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerBash.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerBash.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerBash.StyleClass.Comment)
        lexer.setColor(QColor(colors['variable']), QsciLexerBash.StyleClass.Scalar)
        lexer.setColor(QColor(colors['operator']), QsciLexerBash.StyleClass.Operator)
        lexer.setColor(QColor(colors['parameter']), QsciLexerBash.StyleClass.Identifier)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.sh', '.bash', '.zsh', '.fish', '.ksh', '.csh', '.bashrc', '.bash_profile', '.profile']
    
    def name(self) -> str:
        return "Shell Script"