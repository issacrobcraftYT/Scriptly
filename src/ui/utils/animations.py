from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, QPoint, QParallelAnimationGroup
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsOpacityEffect


def fade_in(widget: QWidget, duration: int = 250):
    """Fade in animation with improved easing and shorter default duration."""
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)  # Smooth acceleration
    anim.start()
    widget._fade_anim = anim  # keep reference


def fade_out(widget: QWidget, duration: int = 200):
    """Fade out animation with improved easing and shorter duration."""
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.Type.InCubic)  # Smooth deceleration
    anim.start()
    widget._fade_anim = anim


def slide_in(widget: QWidget, direction="right", duration: int = 300):
    """Slide in animation with fade effect."""
    # Store original geometry
    geo = widget.geometry()
    
    if direction == "right":
        start_x = geo.x() - geo.width()
        start_y = geo.y()
    elif direction == "left":
        start_x = geo.x() + geo.width()
        start_y = geo.y()
    elif direction == "up":
        start_x = geo.x()
        start_y = geo.y() + geo.height()
    else:  # down
        start_x = geo.x()
        start_y = geo.y() - geo.height()
    
    # Create parallel animation group
    anim_group = QParallelAnimationGroup()
    
    # Position animation
    pos_anim = QPropertyAnimation(widget, b"pos")
    pos_anim.setDuration(duration)
    pos_anim.setStartValue(QPoint(start_x, start_y))
    pos_anim.setEndValue(widget.pos())
    pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # Fade animation
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    fade = QPropertyAnimation(effect, b"opacity")
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    anim_group.addAnimation(pos_anim)
    anim_group.addAnimation(fade)
    anim_group.start()
    widget._anim_group = anim_group


def slide_out(widget: QWidget, direction="right", duration: int = 300):
    """Slide out animation with fade effect."""
    # Store original geometry
    geo = widget.geometry()
    
    if direction == "right":
        end_x = geo.x() + geo.width()
        end_y = geo.y()
    elif direction == "left":
        end_x = geo.x() - geo.width()
        end_y = geo.y()
    elif direction == "up":
        end_x = geo.x()
        end_y = geo.y() - geo.height()
    else:  # down
        end_x = geo.x()
        end_y = geo.y() + geo.height()
    
    # Create parallel animation group
    anim_group = QParallelAnimationGroup()
    
    # Position animation
    pos_anim = QPropertyAnimation(widget, b"pos")
    pos_anim.setDuration(duration)
    pos_anim.setStartValue(widget.pos())
    pos_anim.setEndValue(QPoint(end_x, end_y))
    pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
    
    # Fade animation
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    fade = QPropertyAnimation(effect, b"opacity")
    fade.setDuration(duration)
    fade.setStartValue(1.0)
    fade.setEndValue(0.0)
    fade.setEasingCurve(QEasingCurve.Type.InCubic)
    
    anim_group.addAnimation(pos_anim)
    anim_group.addAnimation(fade)
    anim_group.start()
    widget._anim_group = anim_group
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    anim.start()
    widget._fade_anim = anim


def slide_widget(widget: QWidget, start_rect: QRect, end_rect: QRect, duration: int = 250):
    """Smooth slide animation with fade effect for geometry changes."""
    # Create parallel animation group for combined effects
    anim_group = QParallelAnimationGroup()
    
    # Geometry animation
    geom_anim = QPropertyAnimation(widget, b"geometry")
    geom_anim.setDuration(duration)
    geom_anim.setStartValue(start_rect)
    geom_anim.setEndValue(end_rect)
    geom_anim.setEasingCurve(QEasingCurve.Type.OutQuint)  # Very smooth motion
    
    # Subtle fade for smoother transition
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    fade = QPropertyAnimation(effect, b"opacity")
    fade.setDuration(duration)
    fade.setStartValue(0.95)  # Subtle transparency
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    anim_group.addAnimation(geom_anim)
    anim_group.addAnimation(fade)
    anim_group.start()
    widget._anim_group = anim_group
