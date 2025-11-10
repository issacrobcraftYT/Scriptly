try:
    import autopep8
    _HAS_AUTOPEP8 = True
except Exception:
    autopep8 = None
    _HAS_AUTOPEP8 = False

from PyQt6.QtCore import QRunnable, pyqtSignal, QObject


class FormatterSignals(QObject):
    format_ready = pyqtSignal(str)


class CodeFormatter(QRunnable):
    """QRunnable-based worker for code formatting."""

    def __init__(self, source: str):
        super().__init__()
        self.source = source
        self.signals = FormatterSignals()

    def run(self):
        try:
            # Format code using autopep8 when available
            if _HAS_AUTOPEP8 and autopep8 is not None:
                try:
                    formatted = autopep8.fix_code(
                        self.source,
                        options={
                            'aggressive': 1,
                            'max_line_length': 100,
                            'indent_size': 4
                        }
                    )
                    self.signals.format_ready.emit(formatted)
                except Exception as e:
                    # Formatting failed (possibly due to underlying parser missing)
                    print(f"Formatting error: {e}")
                    self.signals.format_ready.emit(self.source)
            else:
                # autopep8 not available; return original source
                self.signals.format_ready.emit(self.source)
        except Exception as e:
            # Catch-all fallback
            print(f"Formatting error: {e}")
            self.signals.format_ready.emit(self.source)  # Return original on error