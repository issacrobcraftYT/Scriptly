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
            # Create Jedi Script object
            script = jedi.Script(code=self.source, path=self.path)
            
            # Get completions
            completions = script.complete(line=self.line, column=self.column)
            
            # Convert to simplified format
            results = []
            for c in completions:
                result = {
                    'name': c.name,
                    'type': c.type,
                    'module': c.module_name,
                    'description': c.description,
                    'docstring': c.docstring(),
                    'complete': c.complete
                }
                results.append(result)
                
            # Emit results
            self.signals.results_ready.emit(results)
        except Exception as e:
            print(f"Completion error: {e}")
            self.signals.results_ready.emit([])
