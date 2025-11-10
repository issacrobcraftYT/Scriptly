from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerJavaScript
from .base_lexer import BaseLexer


class JavaScriptLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerJavaScript:
        lexer = QsciLexerJavaScript()
        
        # VS Code Dark+ inspired colors for JavaScript
        colors = {
            'keyword': '#C586C0',      # purple for keywords
            'operator': '#D4D4D4',     # light gray for operators
            'function': '#DCDCAA',     # gold for functions
            'string': '#CE9178',       # coral for strings
            'number': '#B5CEA8',       # sage for numbers
            'comment': '#6A9955',      # green for comments
            'regex': '#D16969',        # red for regex
            'identifier': '#9CDCFE',   # light blue for variables
            'property': '#9CDCFE',     # light blue for properties
            'background': '#1E1E1E',   # dark background
            'foreground': '#D4D4D4',   # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerJavaScript.StyleClass.Keyword)
        lexer.setColor(QColor(colors['operator']), QsciLexerJavaScript.StyleClass.Operator)
        lexer.setColor(QColor(colors['function']), QsciLexerJavaScript.StyleClass.GlobalClass)
        lexer.setColor(QColor(colors['string']), QsciLexerJavaScript.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerJavaScript.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerJavaScript.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerJavaScript.StyleClass.Comment)
        lexer.setColor(QColor(colors['comment']), QsciLexerJavaScript.StyleClass.CommentLine)
        lexer.setColor(QColor(colors['regex']), QsciLexerJavaScript.StyleClass.RegEx)
        lexer.setColor(QColor(colors['identifier']), QsciLexerJavaScript.StyleClass.Identifier)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs']
    
    def name(self) -> str:
        return "JavaScript/TypeScript"