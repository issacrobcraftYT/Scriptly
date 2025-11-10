import jedi
from PyQt6.QtCore import QTimer, QThreadPool, QObject, pyqtSignal
from core.completion_worker import CompletionWorker
import os
from pathlib import Path


class AutoCompleter:
    def __init__(self, editor):
        self.editor = editor
        # debounce timer for completions
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dispatch_complete)
        self._worker = None
        self._thread_pool = QThreadPool()
        self._thread_pool.setMaxThreadCount(4)  # Limit concurrent completion threads
        
        # Initialize snippets
        self.snippets = {
            'def': 'def ${1:function_name}(${2:parameters}):\n\t${3:pass}',
            'class': 'class ${1:ClassName}:\n\t${2:pass}',
            'if': 'if ${1:condition}:\n\t${2:pass}',
            'for': 'for ${1:item} in ${2:iterable}:\n\t${3:pass}',
            'while': 'while ${1:condition}:\n\t${2:pass}',
            'try': 'try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${4:pass}',
            'with': 'with ${1:expression} as ${2:target}:\n\t${3:pass}',
            'import': 'import ${1:module}',
            'from': 'from ${1:module} import ${2:name}',
            'print': 'print(${1:object})',
            'return': 'return ${1:object}',
        }

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