import os
from typing import Optional, Type
from PyQt6.Qsci import QsciLexer
from .base_lexer import BaseLexer


class LexerManager:
    """Manages lexer loading and creation"""
    
    def __init__(self):
        self._lexers: dict[str, Type[BaseLexer]] = {}
        self._load_lexers()
    
    def _load_lexers(self):
        """Dynamically load all available lexers"""
        from .python import PythonLexer
        from .markdown import MarkdownLexer
        from .javascript import JavaScriptLexer
        from .html import HTMLLexer
        from .css import CSSLexer
        from .java import JavaLexer
        from .cpp import CPPLexer
        from .ruby import RubyLexer
        from .php import PHPLexer
        from .sql import SQLLexer
        from .xml import XMLLexer
        from .shell import ShellLexer
        from .yaml import YAMLLexer
        
        # Register built-in lexers
        self.register_lexer(PythonLexer)
        self.register_lexer(MarkdownLexer)
        self.register_lexer(JavaScriptLexer)
        self.register_lexer(HTMLLexer)
        self.register_lexer(CSSLexer)
        self.register_lexer(JavaLexer)
        self.register_lexer(CPPLexer)
        self.register_lexer(RubyLexer)
        self.register_lexer(PHPLexer)
        self.register_lexer(SQLLexer)
        self.register_lexer(XMLLexer)
        self.register_lexer(ShellLexer)
        self.register_lexer(YAMLLexer)
    
    def register_lexer(self, lexer_class: Type[BaseLexer]):
        """Register a new lexer class"""
        instance = lexer_class()
        for ext in instance.file_extensions():
            self._lexers[ext] = lexer_class
    
    def get_lexer_for_file(self, file_path: str) -> Optional[QsciLexer]:
        """Get an appropriate lexer instance for the given file"""
        _, ext = os.path.splitext(file_path.lower())
        lexer_class = self._lexers.get(ext)
        
        if lexer_class:
            return lexer_class().create_lexer()
        return None