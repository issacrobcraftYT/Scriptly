from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciLexerPython
from .base_lexer import BaseLexer


class PythonLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerPython:
        lexer = QsciLexerPython()
        
        # VS Code Dark+ color scheme
        colors = {
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
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerPython.StyleClass.Keyword)
        lexer.setColor(QColor(colors['builtin']), QsciLexerPython.StyleClass.ClassName)
        lexer.setColor(QColor(colors['string']), QsciLexerPython.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerPython.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerPython.StyleClass.TripleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerPython.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerPython.StyleClass.Comment)
        lexer.setColor(QColor(colors['decorator']), QsciLexerPython.StyleClass.Decorator)
        lexer.setColor(QColor(colors['operator']), QsciLexerPython.StyleClass.Operator)
        lexer.setColor(QColor(colors['function']), QsciLexerPython.StyleClass.FunctionMethodName)
        lexer.setColor(QColor(colors['identifier']), QsciLexerPython.StyleClass.Identifier)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.py', '.pyw', '.pyi']
    
    def name(self) -> str:
        return "Python"