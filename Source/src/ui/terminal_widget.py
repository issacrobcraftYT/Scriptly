from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QProcess, Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtGui import QTextCharFormat
from PyQt6.QtCore import QTimer
import re

class TerminalWidget(QWidget):
    closed = pyqtSignal()

    def __init__(self, shell=None, parent=None):
        super().__init__(parent)
        self.shell = shell or "powershell"
        self.process = QProcess(self)
        try:
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        except Exception:
            # some PyQt6 versions expose enums differently
            try:
                self.process.setProcessChannelMode(QProcess.MergedChannels)
            except Exception:
                pass
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.finished.connect(self._on_finished)

        self._setup_ui()
        self.start_shell()

    def set_font(self, qfont):
        try:
            self.output.setFont(qfont)
            self.input.setFont(qfont)
        except Exception:
            pass

    def apply_theme(self, colors: dict):
        try:
            # apply background/foreground to output and input
            bg = colors.get('background')
            fg = colors.get('foreground')
            if bg:
                self.output.setStyleSheet(f"background-color: {bg}; color: {fg};")
                self.input.setStyleSheet(f"background-color: {bg}; color: {fg};")
        except Exception:
            pass

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        # Track whether the user has manually scrolled away from the bottom
        self._user_scrolled_up = False
        sb = self.output.verticalScrollBar()
        sb.valueChanged.connect(self._on_scrollbar_value_changed)
        self.input = QLineEdit()
        self.input.returnPressed.connect(self._send_command)

        bottom = QHBoxLayout()
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self._send_command)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.output.clear())
        bottom.addWidget(QLabel("Command:"))
        bottom.addWidget(self.input)
        bottom.addWidget(run_btn)
        bottom.addWidget(clear_btn)

        layout.addWidget(self.output)
        layout.addLayout(bottom)
        self.setLayout(layout)

    def start_shell(self):
        try:
            self.process.start(self.shell)
            if not self.process.waitForStarted(2000):
                self.output.append("Failed to start shell: %s" % self.shell)
            else:
                # On initial start, show the beginning of the stream (scroll to top) unless the user has scrolled
                try:
                    # PyQt6 QTextCursor uses MoveOperation enums
                    QTimer.singleShot(50, lambda: self.output.moveCursor(QTextCursor.MoveOperation.Start))
                    # assume user hasn't scrolled yet
                    self._user_scrolled_up = False
                except Exception:
                    pass
        except Exception as e:
            self.output.append(f"Error starting shell: {e}")

    def _on_stdout(self):
        data = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='ignore')
        # Convert ANSI sequences to HTML and append so colors are preserved in the widget
        html = self._ansi_to_html(data)
        try:
            # If user has scrolled up, do not force scroll; otherwise append and scroll to bottom
            at_bottom = not self._user_scrolled_up
            if at_bottom:
                self.output.moveCursor(QTextCursor.End)
            # Use insertHtml to preserve simple styling
            self.output.insertHtml(html.replace('\n', '<br/>'))
            if at_bottom:
                QTimer.singleShot(0, lambda: self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum()))
        except Exception:
            # fallback to plain text insert
            try:
                if not getattr(self, '_user_scrolled_up', False):
                    self.output.moveCursor(QTextCursor.End)
                self.output.insertPlainText(data)
            except Exception:
                pass

    def _send_command(self):
        cmd = self.input.text()
        if not cmd:
            return
        try:
            # Write command to process
            if self.process.state() == QProcess.ProcessState.Running:
                # Ensure newline is sent
                self.process.write((cmd + "\n").encode('utf-8'))
                self.process.waitForBytesWritten(1000)
            else:
                self.output.append("Process not running")
        except Exception as e:
            self.output.append(f"Error sending command: {e}")
        self.input.clear()
        # user initiated a command; ensure view scrolls to the bottom so typed command and output are visible
        try:
            QTimer.singleShot(50, lambda: self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum()))
            # reset the user-scrolled flag because user intends to see the latest output
            self._user_scrolled_up = False
        except Exception:
            pass

    def _on_scrollbar_value_changed(self, value):
        try:
            sb = self.output.verticalScrollBar()
            # if user moves the scrollbar to a position lower than max - threshold, consider them scrolled up
            threshold = 20
            if sb.maximum() - value > threshold:
                self._user_scrolled_up = True
            else:
                self._user_scrolled_up = False
        except Exception:
            pass

    _ANSI_RE = re.compile(r"\x1b\[(?P<code>[0-9;]+)m")

    def _ansi_to_html(self, text: str) -> str:
        """Very small ANSI -> HTML converter for common foreground colors used by console module.
        Supports basic colors and reset sequences. Returns HTML-safe string with <span style=\"color:...\"> wrappers.
        """
        if not text:
            return ""

        # map ANSI codes to CSS colors
        code_map = {
            '30': '#000000', '31': '#AA0000', '32': '#00AA00', '33': '#AA5500',
            '34': '#0000AA', '35': '#AA00AA', '36': '#00AAAA', '37': '#AAAAAA',
            '90': '#555555', '91': '#FF5555', '92': '#55FF55', '93': '#FFFF55',
            '94': '#5555FF', '95': '#FF55FF', '96': '#55FFFF', '97': '#FFFFFF'
        }

        parts = []
        last_end = 0
        current_style = None

        for m in self._ANSI_RE.finditer(text):
            start, end = m.span()
            if start > last_end:
                chunk = text[last_end:start]
                if current_style:
                    parts.append(f"<span style='color:{current_style}'>" + self._escape_html(chunk) + "</span>")
                else:
                    parts.append(self._escape_html(chunk))
            codes = m.group('code').split(';')
            # reset
            if '0' in codes:
                current_style = None
            else:
                # take last color code present that maps
                color = None
                for c in reversed(codes):
                    if c in code_map:
                        color = code_map[c]
                        break
                current_style = color
            last_end = end

        # append remainder
        if last_end < len(text):
            tail = text[last_end:]
            if current_style:
                parts.append(f"<span style='color:{current_style}'>" + self._escape_html(tail) + "</span>")
            else:
                parts.append(self._escape_html(tail))

        out = ''.join(parts)

        # If no ANSI sequences were present and we still have tagged log lines like [ERROR], [DEBUG],
        # apply simple tag-based coloring so users still get visual hints in the terminal widget.
        if '\x1b[' not in text:
            # simple mapping for bracket tags
            tag_map = {
                'ERROR': '#AA0000',
                'WARNING': '#CCA700',
                'INFO': '#00AAAA',
                'DEBUG': '#5555FF',
                'SUCCESS': '#00AA00',
            }
            # replace occurrences of [TAG] at start or inline
            def _replace_tag(m):
                tag = m.group(1)
                color = tag_map.get(tag.upper())
                if color:
                    return f"<span style='color:{color}'>[{tag}]</span>"
                return f"[{tag}]"

            import re
            out = re.sub(r"\[(ERROR|WARNING|INFO|DEBUG|SUCCESS)\]", _replace_tag, out)

        return out

    def _escape_html(self, s: str) -> str:
        return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))

    def kill(self):
        try:
            if not self.process:
                return
            # attempt graceful terminate first
            try:
                if self.process.state() == QProcess.ProcessState.Running:
                    self.process.terminate()
                    # wait briefly for it to finish
                    self.process.waitForFinished(1000)
            except Exception:
                pass
            # ensure process is killed
            try:
                if self.process.state() == QProcess.ProcessState.Running:
                    self.process.kill()
                    self.process.waitForFinished(1000)
            except Exception:
                pass
        except Exception:
            pass

    def _on_finished(self, exit_code, status):
        self.output.append(f"Process finished with exit code {exit_code}")

    def run_once(self, command):
        # Convenience to run a single command and show output
        proc = QProcess(self)
        try:
            proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        except Exception:
            try:
                proc.setProcessChannelMode(QProcess.MergedChannels)
            except Exception:
                pass
        proc.start(self.shell, ["-Command", command])
        proc.waitForFinished(10000)
        out = bytes(proc.readAllStandardOutput()).decode('utf-8', errors='ignore')
        self.output.append(out)
        proc.deleteLater()

    def closeEvent(self, event):
        try:
            if self.process and self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
        except Exception:
            pass
        super().closeEvent(event)
