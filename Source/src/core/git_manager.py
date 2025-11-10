import os
from git import Repo, GitCommandError
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path


class GitManager(QObject):
    status_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, workspace_path: str):
        super().__init__()
        self.workspace_path = workspace_path
        try:
            self.repo = Repo(workspace_path)
        except:
            self.repo = None

    def is_git_repo(self) -> bool:
        """Check if the workspace is a git repository."""
        return self.repo is not None and not self.repo.bare

    def init_repo(self) -> bool:
        """Initialize a new git repository."""
        try:
            self.repo = Repo.init(self.workspace_path)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize repository: {str(e)}")
            return False

    def get_status(self) -> dict:
        """Get the current git status."""
        if not self.is_git_repo():
            return {}

        try:
            status = {
                'branch': self.repo.active_branch.name,
                'modified': [],
                'untracked': [],
                'staged': []
            }

            # Get file statuses
            for item in self.repo.index.diff(None):
                status['modified'].append(item.a_path)

            for item in self.repo.index.diff('HEAD'):
                status['staged'].append(item.a_path)

            status['untracked'] = self.repo.untracked_files

            self.status_changed.emit(status)
            return status
        except Exception as e:
            self.error_occurred.emit(f"Failed to get status: {str(e)}")
            return {}

    def stage_file(self, file_path: str) -> bool:
        """Stage a file for commit."""
        if not self.is_git_repo():
            return False

        try:
            rel_path = os.path.relpath(file_path, self.workspace_path)
            self.repo.index.add([rel_path])
            self.get_status()  # Update status
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to stage file: {str(e)}")
            return False

    def unstage_file(self, file_path: str) -> bool:
        """Unstage a file."""
        if not self.is_git_repo():
            return False

        try:
            rel_path = os.path.relpath(file_path, self.workspace_path)
            self.repo.index.remove([rel_path])
            self.get_status()  # Update status
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to unstage file: {str(e)}")
            return False

    def commit(self, message: str) -> bool:
        """Commit staged changes."""
        if not self.is_git_repo():
            return False

        try:
            self.repo.index.commit(message)
            self.get_status()  # Update status
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to commit: {str(e)}")
            return False

    def push(self, remote: str = 'origin', branch: str = None) -> bool:
        """Push commits to remote."""
        if not self.is_git_repo():
            return False

        try:
            if branch is None:
                branch = self.repo.active_branch.name
            self.repo.remotes[remote].push(branch)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to push: {str(e)}")
            return False

    def pull(self, remote: str = 'origin', branch: str = None) -> bool:
        """Pull changes from remote."""
        if not self.is_git_repo():
            return False

        try:
            if branch is None:
                branch = self.repo.active_branch.name
            self.repo.remotes[remote].pull(branch)
            self.get_status()  # Update status
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to pull: {str(e)}")
            return False