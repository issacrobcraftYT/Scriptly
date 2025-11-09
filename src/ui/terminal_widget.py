from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QProcess, Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor

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
        except Exception as e:
            self.output.append(f"Error starting shell: {e}")

    def _on_stdout(self):
        data = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='ignore')
        try:
            self.output.moveCursor(QTextCursor.End)
        except Exception:
            pass
        self.output.insertPlainText(data)
        try:
            self.output.moveCursor(QTextCursor.End)
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
