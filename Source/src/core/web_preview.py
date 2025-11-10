import os
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pathlib import Path


class WebPreviewManager(QObject):
    preview_updated = pyqtSignal()

    def __init__(self, editor=None):
        super().__init__()
        self.editor = editor
        self.preview_widget = QWebEngineView()
        self._temp_file = None
        self.file_watcher = None

    def set_editor(self, editor):
        """Set the editor to preview."""
        self.editor = editor
        self._setup_preview()

    def _setup_preview(self):
        """Initialize preview based on file type."""
        if not self.editor:
            return

        file_path = getattr(self.editor, 'file_path', '')
        if not file_path:
            return

        ext = Path(file_path).suffix.lower()
        
        if ext == '.html':
            # For HTML files, show direct preview
            self._setup_html_preview()
        elif ext == '.css':
            # For CSS files, create a test HTML page
            self._setup_css_preview()
        elif ext == '.js':
            # For JS files, create a test HTML page
            self._setup_js_preview()

    def _setup_html_preview(self):
        """Set up preview for HTML files."""
        if not self.editor:
            return
            
        content = self.editor.text()
        self.preview_widget.setHtml(content, QUrl.fromLocalFile(str(Path(self.editor.file_path).parent)))

    def _setup_css_preview(self):
        """Set up preview for CSS files."""
        if not self.editor:
            return
            
        css_content = self.editor.text()
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>{css_content}</style>
        </head>
        <body>
            <div class="preview-content">
                <h1>CSS Preview</h1>
                <p>This is a preview of your CSS styles.</p>
                <button>Sample Button</button>
                <input type="text" placeholder="Sample Input">
                <ul>
                    <li>List Item 1</li>
                    <li>List Item 2</li>
                    <li>List Item 3</li>
                </ul>
            </div>
        </body>
        </html>
        """
        self.preview_widget.setHtml(html_content)

    def _setup_js_preview(self):
        """Set up preview for JavaScript files."""
        if not self.editor:
            return
            
        js_content = self.editor.text()
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript Preview</title>
        </head>
        <body>
            <div id="output"></div>
            <script>
                // Redirect console.log to preview
                const output = document.getElementById('output');
                console.log = (...args) => {{
                    const p = document.createElement('p');
                    p.textContent = args.join(' ');
                    output.appendChild(p);
                }};
                
                // Your JavaScript code
                {js_content}
            </script>
        </body>
        </html>
        """
        self.preview_widget.setHtml(html_content)

    def update_preview(self):
        """Update the preview based on current content."""
        self._setup_preview()
        self.preview_updated.emit()

    def get_preview_widget(self):
        """Get the preview widget."""
        return self.preview_widget