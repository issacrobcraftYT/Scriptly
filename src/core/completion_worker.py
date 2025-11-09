from PyQt6.QtCore import QRunnable, pyqtSignal, QObject, QThreadPool
import jedi


class CompletionSignals(QObject):
    results_ready = pyqtSignal(list)


class CompletionWorker(QRunnable):
    """QRunnable-based worker for jedi completions. Uses QThreadPool so we don't
    have to manage QThread lifecycles manually (avoids 'QThread destroyed' issues)."""

    def __init__(self, source: str, line: int, column: int, path: str = ''):
        super().__init__()
        self.source = source
        self.line = line
        self.column = column
        self.path = path
        self.signals = CompletionSignals()

    def run(self):
        try:
            self.signals.results_ready.emit([])
        except Exception:
            pass
