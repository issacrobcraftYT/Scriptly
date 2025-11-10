from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerRuby
from .base_lexer import BaseLexer


class RubyLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerRuby:
        lexer = QsciLexerRuby()
        
        # VS Code Dark+ inspired colors for Ruby
        colors = {
            'keyword': '#C586C0',     # purple for keywords
            'class': '#4EC9B0',       # turquoise for classes
            'function': '#DCDCAA',    # gold for functions/methods
            'symbol': '#569CD6',      # blue for symbols
            'string': '#CE9178',      # coral for strings
            'number': '#B5CEA8',      # sage for numbers
            'comment': '#6A9955',     # green for comments
            'regex': '#D16969',       # red for regex
            'global': '#9CDCFE',      # light blue for global vars
            'instance': '#9CDCFE',    # light blue for instance vars
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['keyword']), QsciLexerRuby.StyleClass.Keyword)
        lexer.setColor(QColor(colors['class']), QsciLexerRuby.StyleClass.ClassName)
        lexer.setColor(QColor(colors['function']), QsciLexerRuby.StyleClass.FunctionMethodName)
        lexer.setColor(QColor(colors['string']), QsciLexerRuby.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerRuby.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['number']), QsciLexerRuby.StyleClass.Number)
        lexer.setColor(QColor(colors['comment']), QsciLexerRuby.StyleClass.Comment)
        lexer.setColor(QColor(colors['comment']), QsciLexerRuby.StyleClass.POD)
        lexer.setColor(QColor(colors['regex']), QsciLexerRuby.StyleClass.Regex)
        lexer.setColor(QColor(colors['global']), QsciLexerRuby.StyleClass.Global)
        lexer.setColor(QColor(colors['instance']), QsciLexerRuby.StyleClass.InstitutionVariable)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.rb', '.rbw', '.rake', '.gemspec', 'Rakefile', 'Gemfile']
    
    def name(self) -> str:
        return "Ruby"