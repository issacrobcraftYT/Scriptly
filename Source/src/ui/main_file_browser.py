import os
from PyQt6.QtWidgets import QDockWidget, QTreeView, QApplication
from PyQt6.QtCore import QDir, Qt, QSize
from PyQt6.QtGui import QIcon
from pathlib import Path

def _get_icon_for_path(path: str, size=16):
    try:
        import sys
        import os
        
        # Get the absolute path to the assets directory
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images'))
        
        # Default icons
        if os.path.isdir(path):
            icon_path = os.path.join(assets_dir, 'folder.svg')
        else:
            # Get extension without the dot
            ext = os.path.splitext(path)[1].lower().lstrip('.')
            
            # Try extension-specific icon first
            custom_icon = os.path.join(assets_dir, f'{ext}.svg')
            if os.path.exists(custom_icon):
                icon_path = custom_icon
            # Special case for multiple extensions mapping to same icon (e.g., py and pyw)
            elif ext == 'pyw':
                python_icon = os.path.join(assets_dir, 'python.svg')
                if os.path.exists(python_icon):
                    icon_path = python_icon
                else:
                    icon_path = os.path.join(assets_dir, 'file.svg')
            # Special case for markdown extensions
            elif ext in ['markdown']:
                md_icon = os.path.join(assets_dir, 'md.svg')
                if os.path.exists(md_icon):
                    icon_path = md_icon
                else:
                    icon_path = os.path.join(assets_dir, 'file.svg')
            else:
                icon_path = os.path.join(assets_dir, 'file.svg')
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                return icon
            else:
                print(f"Failed to load icon: {icon_path}")
    except Exception as e:
        print(f"Icon load error: {e}")
    return QIcon()

def create_file_browser(window):
    """Create and attach a file browser dock to the given MainWindow instance.

    This function mirrors the previous inline implementation in main_window but
    lives in its own module so it can be tested and maintained separately.
    """
    window.file_browser = QDockWidget("Files", window)
    window.file_browser.setAllowedAreas(
        Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
    )

    # Create file system model (import lazily because some PyQt6 builds expose it differently)
    try:
        from PyQt6.QtWidgets import QFileSystemModel
        from PyQt6.QtGui import QFileIconProvider
        
        class CustomIconProvider(QFileIconProvider):
            def icon(self, v):
                # v may be a QFileInfo or QUrl or type; try to get absolute file path
                try:
                    # QFileInfo
                    fp = v.absoluteFilePath()
                except Exception:
                    try:
                        fp = str(v.toLocalFile())
                    except Exception:
                        fp = None
                if fp:
                    return _get_icon_for_path(fp, size=16)
                return super().icon(v)

        window.file_system = QFileSystemModel()
        window.file_system.setIconProvider(CustomIconProvider())
        window.file_system.setRootPath(QDir.currentPath())
        window.tree_view = QTreeView()
        window.tree_view.setModel(window.file_system)
        window.tree_view.setRootIndex(window.file_system.index(QDir.currentPath()))
        # Set consistent icon size
        window.tree_view.setIconSize(QSize(16, 16))
        # Add some padding for better visual appearance
        window.tree_view.setStyleSheet('QTreeView::item { padding: 2px; }')
        window._fs_model_type = 'native'

    except Exception:
        # Fallback: build a simple tree model using QStandardItemModel
        from PyQt6.QtGui import QStandardItemModel, QStandardItem
        window._fs_model_type = 'custom'
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Name'])
        root_item = model.invisibleRootItem()

        def add_children(parent_item, path):
            try:
                for name in sorted(os.listdir(path)):
                    full = os.path.join(path, name)
                    item = QStandardItem(name)
                    # Set icon using our icon manager
                    try:
                        icon = _get_icon_for_path(full, size=16)
                        if not icon.isNull():
                            item.setIcon(icon)
                    except Exception:
                        pass
                    item.setData(full, Qt.ItemDataRole.UserRole)
                    parent_item.appendRow(item)
                    if os.path.isdir(full):
                        add_children(item, full)
            except Exception:
                pass

        add_children(root_item, QDir.currentPath())
        window.tree_view = QTreeView()
        window.tree_view.setModel(model)
        try:
            window.tree_view.setIconSize(QSize(16, 16))
            window.tree_view.setStyleSheet('QTreeView::item { padding: 2px; }')
        except Exception:
            pass
        window.file_system = model

    # Hide unneeded columns for native model
    try:
        window.tree_view.hideColumn(1)
        window.tree_view.hideColumn(2)
        window.tree_view.hideColumn(3)
    except Exception:
        pass

    # Connect clicks
    try:
        window.tree_view.clicked.connect(window.open_from_browser)
    except Exception:
        try:
            window.tree_view.doubleClicked.connect(window.open_from_browser)
        except Exception:
            pass

    # Context menu
    window.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    window.tree_view.customContextMenuRequested.connect(window.on_file_tree_context_menu)

    window.file_browser.setWidget(window.tree_view)
    window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, window.file_browser)

    try:
        window.file_browser.visibilityChanged.connect(lambda visible: None)
    except Exception:
        pass

    return window.file_browser