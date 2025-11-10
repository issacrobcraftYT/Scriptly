from abc import ABC, abstractmethod
from PyQt6.Qsci import QsciLexer
from PyQt6.QtGui import QFont


class BaseLexer(ABC):
    """Base class for all lexers"""
    
    @abstractmethod
    def create_lexer(self) -> QsciLexer:
        """Create and return a configured lexer instance"""
        pass
        
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Return list of file extensions this lexer supports"""
        pass
        
    @abstractmethod
    def name(self) -> str:
        """Return the name of this lexer"""
        pass
        
    def configure_lexer(self, lexer: QsciLexer, font: QFont = None):
        """Configure common lexer properties"""
        if font:
            lexer.setFont(font)