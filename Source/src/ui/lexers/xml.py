from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciLexerXML
from .base_lexer import BaseLexer


class XMLLexer(BaseLexer):
    def create_lexer(self) -> QsciLexerXML:
        lexer = QsciLexerXML()
        
        # VS Code Dark+ inspired colors for XML
        colors = {
            'tag': '#569CD6',         # blue for tags
            'attribute': '#9CDCFE',   # light blue for attributes
            'string': '#CE9178',      # coral for strings
            'comment': '#6A9955',     # green for comments
            'cdata': '#D7BA7D',       # tan for CDATA
            'entity': '#D4D4D4',      # light gray for entities
            'background': '#1E1E1E',  # dark background
            'foreground': '#D4D4D4',  # light gray text
        }
        
        # Apply colors
        lexer.setColor(QColor(colors['tag']), QsciLexerXML.StyleClass.Tag)
        lexer.setColor(QColor(colors['attribute']), QsciLexerXML.StyleClass.Attribute)
        lexer.setColor(QColor(colors['string']), QsciLexerXML.StyleClass.DoubleQuotedString)
        lexer.setColor(QColor(colors['string']), QsciLexerXML.StyleClass.SingleQuotedString)
        lexer.setColor(QColor(colors['comment']), QsciLexerXML.StyleClass.Comment)
        lexer.setColor(QColor(colors['cdata']), QsciLexerXML.StyleClass.CDATA)
        lexer.setColor(QColor(colors['entity']), QsciLexerXML.StyleClass.Entity)
        
        # Set background and default colors
        lexer.setPaper(QColor(colors['background']))
        lexer.setDefaultColor(QColor(colors['foreground']))
        
        return lexer
    
    def file_extensions(self) -> list[str]:
        return ['.xml', '.svg', '.xaml', '.plist', '.xsd', '.xsl', '.xslt', '.wsdl']
    
    def name(self) -> str:
        return "XML"