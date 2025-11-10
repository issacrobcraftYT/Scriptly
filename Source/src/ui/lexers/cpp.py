from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerCPP
from .base_lexer import BaseLexer


class CPPLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerCPP:
        lexer = QsciLexerCPP()
        
        # VS Code Dark+ inspired colors for C/C++
        colors = {
            'keyword': '#569CD6',     # blue for keywords
            'operator': '#D4D4D4',    # light gray for operators
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'class': '#4EC9B0',       # turquoise for classes
            'function': '#DCDCAA',    # gold for functions
            'preprocessor': '#C586C0', # purple for preprocessor
            'identifier': '#9CDCFE',  # light blue for identifiers
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerCPP.StyleClass.Keyword)
        lexer.setColor(QColor(colors['operator']), QsciLexerCPP.StyleClass.Operator)
        lexer.setColor(QColor(colors['string']), QsciLexerCPP.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerCPP.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerCPP.StyleClass.RawString)
        lexer.setColor(QColor(colors['number']), QsciLexerCPP.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerCPP.StyleClass.Comment)
        lexer.setColor(QColor(colors['comment']), QsciLexerCPP.StyleClass.CommentLine)
        lexer.setColor(QColor(colors['comment']), QsciLexerCPP.StyleClass.CommentDoc)
        lexer.setColor(QColor(colors['preprocessor']), QsciLexerCPP.StyleClass.PreProcessor)
        lexer.setColor(QColor(colors['identifier']), QsciLexerCPP.StyleClass.Identifier)
        lexer.setColor(QColor(colors['class']), QsciLexerCPP.StyleClass.GlobalClass)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.c', '.cpp', '.cxx', '.cc', '.h', '.hpp', '.hxx']
    
    def name(self) -> str:
        return "C/C++"