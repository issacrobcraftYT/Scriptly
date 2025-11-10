from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerSQL
from .base_lexer import BaseLexer


class SQLLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerSQL:
        lexer = QsciLexerSQL()
        
        # VS Code Dark+ inspired colors for SQL
        colors = {
            'keyword': '#569CD6',     # blue for keywords
            'operator': '#D4D4D4',    # light gray for operators
            'function': '#DCDCAA',    # gold for functions
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'identifier': '#9CDCFE',  # light blue for identifiers
            'table': '#4EC9B0',       # turquoise for tables
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerSQL.StyleClass.Keyword)
        lexer.setColor(QColor(colors['operator']), QsciLexerSQL.StyleClass.Operator)
        lexer.setColor(QColor(colors['function']), QsciLexerSQL.StyleClass.KeywordSet5)
        lexer.setColor(QColor(colors['string']), QsciLexerSQL.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerSQL.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerSQL.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerSQL.StyleClass.Comment)
        lexer.setColor(QColor(colors['comment']), QsciLexerSQL.StyleClass.CommentLine)
        lexer.setColor(QColor(colors['comment']), QsciLexerSQL.StyleClass.CommentDoc)
        lexer.setColor(QColor(colors['identifier']), QsciLexerSQL.StyleClass.Identifier)
        lexer.setColor(QColor(colors['table']), QsciLexerSQL.StyleClass.KeywordSet6)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.sql', '.mysql', '.psql', '.plsql', '.tsql']
    
    def name(self) -> str:
        return "SQL"