import pyflakes.api
import ast
from pycodestyle import Checker, StyleGuide
from io import StringIO
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from typing import List, Dict


class AnalyzerSignals(QObject):
    issues_found = pyqtSignal(list)


class Reporter:
    def __init__(self):
        self.errors = []

    def unexpectedError(self, filename, msg):
        self.errors.append({
            'line': 0,
            'col': 0,
            'type': 'error',
            'message': msg
        })

    def syntaxError(self, filename, msg, lineno, offset, text):
        self.errors.append({
            'line': lineno,
            'col': offset,
            'type': 'error',
            'message': msg
        })

    def flake(self, message):
        self.errors.append({
            'line': message.lineno,
            'col': message.col,
            'type': 'warning',
            'message': message.message % message.message_args
        })


class CodeAnalyzer(QRunnable):
    """QRunnable-based worker for code analysis."""

    def __init__(self, source: str, path: str = ''):
        super().__init__()
        self.source = source
        self.path = path
        self.signals = AnalyzerSignals()

    def run(self):
        issues = []

        # Syntax check
        try:
            ast.parse(self.source)
        except SyntaxError as e:
            issues.append({
                'line': e.lineno,
                'col': e.offset,
                'type': 'error',
                'message': str(e)
            })
            self.signals.issues_found.emit(issues)
            return

        # Pyflakes check
        reporter = Reporter()
        pyflakes.api.check(self.source, self.path or '<string>', reporter)
        issues.extend(reporter.errors)

        # PEP 8 style check
        style_guide = StyleGuide(quiet=True)
        checker = Checker(
            lines=self.source.splitlines(True),
            options=style_guide.options
        )
        
        style_errors = checker.check_all()
        for line_number, offset, code, text, doc in checker.errors:
            issues.append({
                'line': line_number,
                'col': offset,
                'type': 'style',
                'message': f'{code}: {text}'
            })

        self.signals.issues_found.emit(issues)