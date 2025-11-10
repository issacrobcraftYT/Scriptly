from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRectF, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from .ui_effects import create_ripple_effect, apply_shadow

class ModernButton(QPushButton):
    """A modern button with material design effects."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Setup appearance
        self.setAutoFillBackground(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Initialize states
        self._pressed = False
        self._hover = False
        self._shadow_enabled = True
        
        # Apply initial shadow
        self._setup_shadow()
        
        # Setup animations
        self._setup_animations()
        
    def _setup_shadow(self):
        """Initialize the shadow effect."""
        if self._shadow_enabled:
            apply_shadow(self, blur_radius=15, y_offset=3)
    
    def _setup_animations(self):
        """Initialize hover and click animations."""
        # Hover animation
        self._hover_anim = QPropertyAnimation(self, b"_hover_value")
        self._hover_anim.setDuration(200)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Click animation
        self._press_anim = QPropertyAnimation(self, b"_press_value")
        self._press_anim.setDuration(100)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self._hover = True
        self._hover_anim.setStartValue(0)
        self._hover_anim.setEndValue(1)
        self._hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self._hover = False
        self._hover_anim.setStartValue(1)
        self._hover_anim.setEndValue(0)
        self._hover_anim.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press with ripple effect."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            pos = event.pos()
            create_ripple_effect(self, pos)
            
            # Start press animation
            self._press_anim.setStartValue(0)
            self._press_anim.setEndValue(1)
            self._press_anim.start()
            
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self._press_anim.setStartValue(1)
            self._press_anim.setEndValue(0)
            self._press_anim.start()
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Custom paint event for rounded corners and effects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 6, 6)
        painter.setClipPath(path)
        
        # Draw background
        super().paintEvent(event)
        
    def set_accent_color(self, color: str):
        """Set the button's accent color."""
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {color};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }}
            ModernButton:hover {{
                background-color: {QColor(color).lighter(110).name()};
            }}
            ModernButton:pressed {{
                background-color: {QColor(color).darker(110).name()};
            }}
        """)

    # Animatable properties for QPropertyAnimation to target
    def get_hover_value(self):
        return getattr(self, "_hover_value_internal", 0.0)

    def set_hover_value(self, v):
        self._hover_value_internal = float(v)
        # Could be used to drive visual state in paintEvent or stylesheet
        self.update()

    _hover_value = pyqtProperty(float, fget=get_hover_value, fset=set_hover_value)

    def get_press_value(self):
        return getattr(self, "_press_value_internal", 0.0)

    def set_press_value(self, v):
        self._press_value_internal = float(v)
        self.update()

    _press_value = pyqtProperty(float, fget=get_press_value, fset=set_press_value)