from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerMarkdown
from .base_lexer import BaseLexer


class MarkdownLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerMarkdown:
        lexer = QsciLexerMarkdown()
        
        # VS Code Dark+ inspired color scheme for Markdown
        colors = {
            'header': '#569CD6',
            'emphasis': '#C586C0',
            'strong': '#4EC9B0',
            'link': '#CE9178',
            'code': '#DCDCAA',
            'list': '#D4D4D4',
            'quote': '#608B4E',
            'background': '#1E1E1E',
            'foreground': '#D4D4D4',
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['header']), QsciLexerMarkdown.StyleClass.Header1)
        lexer.setColor(QColor(colors['header']), QsciLexerMarkdown.StyleClass.Header2)
        lexer.setColor(QColor(colors['header']), QsciLexerMarkdown.StyleClass.Header3)
        lexer.setColor(QColor(colors['emphasis']), QsciLexerMarkdown.StyleClass.Emphasis)
        lexer.setColor(QColor(colors['strong']), QsciLexerMarkdown.StyleClass.StrongEmphasis)
        lexer.setColor(QColor(colors['link']), QsciLexerMarkdown.StyleClass.Link)
        lexer.setColor(QColor(colors['code']), QsciLexerMarkdown.StyleClass.CodeBlock)
        lexer.setColor(QColor(colors['list']), QsciLexerMarkdown.StyleClass.UnorderedList)
        lexer.setColor(QColor(colors['list']), QsciLexerMarkdown.StyleClass.OrderedList)
        lexer.setColor(QColor(colors['quote']), QsciLexerMarkdown.StyleClass.BlockQuote)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.md', '.markdown']
    
    def name(self) -> str:
        return "Markdown"