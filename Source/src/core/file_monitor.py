from PyQt6.QtCore import QFileSystemWatcher, QTimer, pyqtSignal, QObject
import os

class FileMonitor(QObject):
    file_changed = pyqtSignal(str)
    file_created = pyqtSignal(str)
    file_deleted = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.handle_file_change)
        self.watcher.directoryChanged.connect(self.handle_directory_change)
        self.monitored_files = {}
        self.monitored_dirs = set()
        self.change_timestamps = {}
        self.change_buffer = []  # Buffer for batching changes
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self.process_batched_changes)
        self.batch_timer.setInterval(250)  # Process changes every 250ms
        
        # Setup check timer for external changes
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_monitored_files)
        if self.settings.file_monitor['enabled']:
            self.start_monitoring()
            
    def start_monitoring(self):
        interval = self.settings.file_monitor['check_interval']
        self.check_timer.start(interval)
        
    def stop_monitoring(self):
        self.check_timer.stop()
        
    def add_file(self, file_path):
        if os.path.exists(file_path):
            self.watcher.addPath(file_path)
            self.monitored_files[file_path] = os.path.getmtime(file_path)
            
    def remove_file(self, file_path):
        if file_path in self.monitored_files:
            self.watcher.removePath(file_path)
            del self.monitored_files[file_path]
            
    def handle_file_change(self, file_path):
        # Store the timestamp of the change
        self.change_timestamps[file_path] = os.path.getmtime(file_path)
        # Emit the signal after a small delay to prevent multiple updates
        QTimer.singleShot(100, lambda: self.emit_change(file_path))

    def handle_directory_change(self, path):
        """Handle directory changes by checking for added/removed files."""
        if path in self.monitored_dirs:
            self.directory_changed.emit(path)
        
    def emit_change(self, file_path):
        current_time = os.path.getmtime(file_path)
        last_time = self.change_timestamps.get(file_path, 0)
        
        # Only emit if this is the most recent change
        if current_time == last_time:
            self.file_changed.emit(file_path)
            
    def process_batched_changes(self):
        """Process all batched file changes at once."""
        if not self.change_buffer:
            return
            
        # Process all changes in the buffer
        changes = self.change_buffer.copy()
        self.change_buffer.clear()
        
        for change in changes:
            self.file_changed.emit(change)
            
    def check_monitored_files(self):
        for file_path in list(self.monitored_files.keys()):
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)
                if current_mtime != self.monitored_files[file_path]:
                    self.monitored_files[file_path] = current_mtime
                    self.handle_file_change(file_path)
            else:
                # File was deleted
                self.remove_file(file_path)