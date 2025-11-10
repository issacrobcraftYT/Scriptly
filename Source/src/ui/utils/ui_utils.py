from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QIcon
from PyQt6.QtCore import Qt


def make_close_icon(size=12, color=None):
    """Create a small 'X' icon used for tab close buttons.

    Returns a QIcon. Safe to call from UI code; wraps QPainter usage.
    """
    if color is None:
        color = QColor(30, 30, 30)

    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pm)
    try:
        if painter.isActive():
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(3, 3, size - 4, size - 4)
            painter.drawLine(size - 4, 3, 3, size - 4)
    finally:
        if painter.isActive():
            painter.end()

    return QIcon(pm)


def format_line_col(line, col):
    """Return formatted line/column text for status bar."""
    try:
        return f"Line: {line + 1}, Col: {col + 1}"
    except Exception:
        return "Line: 1, Col: 1"
