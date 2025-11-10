from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerJava
from .base_lexer import BaseLexer


class JavaLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerJava:
        lexer = QsciLexerJava()
        
        # VS Code Dark+ inspired colors for Java
        colors = {
            'keyword': '#569CD6',     # blue for keywords
            'operator': '#D4D4D4',    # light gray for operators
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'class': '#4EC9B0',       # turquoise for classes
            'interface': '#4EC9B0',   # turquoise for interfaces
            'method': '#DCDCAA',      # gold for methods
            'annotation': '#C586C0',  # purple for annotations
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerJava.StyleClass.Keyword)
        lexer.setColor(QColor(colors['operator']), QsciLexerJava.StyleClass.Operator)
        lexer.setColor(QColor(colors['string']), QsciLexerJava.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerJava.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerJava.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerJava.StyleClass.Comment)
        lexer.setColor(QColor(colors['comment']), QsciLexerJava.StyleClass.CommentLine)
        lexer.setColor(QColor(colors['comment']), QsciLexerJava.StyleClass.CommentDoc)
        lexer.setColor(QColor(colors['class']), QsciLexerJava.StyleClass.GlobalClass)
        lexer.setColor(QColor(colors['method']), QsciLexerJava.StyleClass.CommentDocKeyword)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.java', '.jav']
    
    def name(self) -> str:
        return "Java"