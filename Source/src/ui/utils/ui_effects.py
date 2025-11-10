from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath

def apply_shadow(widget: QWidget, color: str = "#000000", blur_radius: int = 20, 
                x_offset: int = 0, y_offset: int = 4, opacity: float = 0.2):
    """Apply a modern shadow effect to a widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(color).darker(200))
    shadow.setColor(QColor(color))
    shadow_color = QColor(color)
    shadow_color.setAlphaF(opacity)
    shadow.setColor(shadow_color)
    widget.setGraphicsEffect(shadow)

def apply_rounded_corners(widget: QWidget, radius: int = 8):
    """Apply rounded corners to a widget."""
    path = QPainterPath()
    # QPainterPath.addRoundedRect expects a QRectF or numeric coords
    rectf = QRectF(widget.rect())
    path.addRoundedRect(rectf, radius, radius)
    widget.setMask(path.toFillPolygon().toPolygon())

class ModernWidget(QWidget):
    """A modern widget base class with enhanced visual effects."""
    
    def __init__(self, parent=None, shadow=True, corners=True):
        super().__init__(parent)
        
        if shadow:
            apply_shadow(self)
        if corners:
            self.corner_radius = 8
        else:
            self.corner_radius = 0
            
        self.setAutoFillBackground(True)
        
    def paintEvent(self, event):
        """Override paint event for rounded corners."""
        if self.corner_radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            # Use QRectF when adding rounded rect to QPainterPath
            path.addRoundedRect(QRectF(self.rect()), self.corner_radius, self.corner_radius)
            
            painter.setClipPath(path)
            super().paintEvent(event)
        else:
            super().paintEvent(event)

def create_ripple_effect(widget: QWidget, pos: QPoint, color: str = "#ffffff"):
    """Create a material design ripple effect at the specified position."""
    from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
    
    # Create ripple widget
    ripple = QWidget(widget)
    ripple.setGeometry(0, 0, 0, 0)
    ripple.setStyleSheet(f"""
        background-color: {color};
        border-radius: 0px;
        opacity: 0.3;
    """)
    ripple.show()
    
    # Calculate final size (diagonal of the widget)
    size = max(widget.width(), widget.height()) * 2
    
    # Center ripple on click position
    final_x = pos.x() - size/2
    final_y = pos.y() - size/2
    
    # Create and configure animation
    from PyQt6.QtCore import QRect
    anim = QPropertyAnimation(ripple, b"geometry")
    anim.setDuration(400)
    anim.setStartValue(QRect(pos.x(), pos.y(), 0, 0))
    anim.setEndValue(QRect(int(final_x), int(final_y), int(size), int(size)))
    anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    
    # Connect animation finished to cleanup
    anim.finished.connect(lambda: ripple.deleteLater())
    
    # Start animation
    anim.start()