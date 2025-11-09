import jedi
from PyQt6.QtCore import QTimer
from core.completion_worker import CompletionWorker


class AutoCompleter:
    def __init__(self, editor):
        self.editor = editor
        # debounce timer for completions
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dispatch_complete)
        self._worker = None

    def update_completions(self, delay=150):
        # schedule completion after a short debounce interval
        try:
            self._timer.start(delay)
        except Exception:
            # fallback: dispatch immediately
            self._dispatch_complete()

    def _dispatch_complete(self):
        try:
            editor = self.editor
            line, column = editor.getCursorPosition()
            src = editor.text()
            ln = line + 1
            col = column
            path = getattr(editor, 'file_path', '') or ''
            # if a previous worker is running, ignore it
            try:
                if self._worker is not None and self._worker.isRunning():
                    # let it finish; start a new one
                    pass
            except Exception:
                pass
            worker = CompletionWorker(src, ln, col, path)
            # connect results via signals object
            try:
                worker.signals.results_ready.connect(self._on_results)
            except Exception:
                try:
                    worker.results_ready.connect(self._on_results)
                except Exception:
                    pass
            # keep reference briefly
            self._worker = worker
            # submit to global thread pool
            try:
                QThreadPool.globalInstance().start(worker)
            except Exception:
                # fallback to starting in the main thread
                worker.run()
        except Exception:
            pass

    def _on_results(self, names):
        try:
            if not names:
                return
            try:
                self.editor.showUserList(1, names)
            except Exception:
                try:
                    self.editor.showUserList(1, '\n'.join(names))
                except Exception:
                    pass
        except Exception:
            pass