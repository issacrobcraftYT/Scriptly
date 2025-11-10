from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerYAML
from .base_lexer import BaseLexer


class YAMLLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerYAML:
        lexer = QsciLexerYAML()
        
        # VS Code Dark+ inspired colors for YAML
        colors = {
            'keyword': '#569CD6',     # blue for keywords
            'operator': '#D4D4D4',    # light gray for operators
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'identifier': '#9CDCFE',  # light blue for identifiers
            'document': '#C586C0',    # purple for document markers
            'reference': '#4EC9B0',   # turquoise for references
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerYAML.StyleClass.Keyword)
        lexer.setColor(QColor(colors['operator']), QsciLexerYAML.StyleClass.Operator)
        lexer.setColor(QColor(colors['string']), QsciLexerYAML.StyleClass.TextString)
        lexer.setColor(QColor(colors['number']), QsciLexerYAML.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerYAML.StyleClass.Comment)
        lexer.setColor(QColor(colors['identifier']), QsciLexerYAML.StyleClass.Identifier)
        lexer.setColor(QColor(colors['document']), QsciLexerYAML.StyleClass.DocumentDelimiter)
        lexer.setColor(QColor(colors['reference']), QsciLexerYAML.StyleClass.Reference)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.yml', '.yaml', '.clang-format', '.clang-tidy']
    
    def name(self) -> str:
        return "YAML"