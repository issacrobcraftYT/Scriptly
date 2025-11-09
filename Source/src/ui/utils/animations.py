from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, QPoint, QParallelAnimationGroup
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


def fade_in(widget: QWidget, duration: int = 250):
    """Fade in animation with improved easing and shorter default duration."""
    try:
        # If this is a top-level window, animate windowOpacity instead of applying
        # a QGraphicsOpacityEffect (avoids internal pixmap/painter conflicts).
        if hasattr(widget, 'isWindow') and widget.isWindow():
            anim = QPropertyAnimation(widget, b"windowOpacity")
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            widget._fade_anim = anim
            # ensure starting opacity is 0 to animate from invisible
            try:
                widget.setWindowOpacity(0.0)
            except Exception:
                pass
            anim.start()
            return

        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
            widget.setGraphicsEffect(None)

        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        widget._fade_anim = anim
        anim.start()
    except Exception as e:
        print(f"Animation error: {e}")


def fade_out(widget: QWidget, duration: int = 200):
    """Fade out animation with improved easing and shorter duration."""
    try:
        if hasattr(widget, 'isWindow') and widget.isWindow():
            anim = QPropertyAnimation(widget, b"windowOpacity")
            anim.setDuration(duration)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.Type.InCubic)
            widget._fade_anim = anim
            anim.start()
            return

        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
            widget.setGraphicsEffect(None)

        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)

        widget._fade_anim = anim
        anim.start()
    except Exception as e:
        print(f"Animation error: {e}")


def slide_in(widget: QWidget, direction="right", duration: int = 300):
    """Slide in animation with fade effect."""
    try:
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
    
        anim_group = QParallelAnimationGroup()
    
        pos_anim = QPropertyAnimation(widget, b"pos")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QPoint(start_x, start_y))
        pos_anim.setEndValue(widget.pos())
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
            widget.setGraphicsEffect(None)
        
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(duration)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    
        anim_group.addAnimation(pos_anim)
        anim_group.addAnimation(fade)
    
        widget._anim_group = anim_group
        widget._pos_anim = pos_anim
        widget._fade_anim = fade
        anim_group.start()
    except Exception as e:
        print(f"Animation error: {e}")


def slide_out(widget: QWidget, direction="right", duration: int = 300):
    """Slide out animation with fade effect."""
    try:
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
    
        anim_group = QParallelAnimationGroup()
    
        pos_anim = QPropertyAnimation(widget, b"pos")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(widget.pos())
        pos_anim.setEndValue(QPoint(end_x, end_y))
        pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
    
        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
            widget.setGraphicsEffect(None)
        
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(duration)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.InCubic)
    
        anim_group.addAnimation(pos_anim)
        anim_group.addAnimation(fade)
    
        widget._anim_group = anim_group
        widget._pos_anim = pos_anim
        widget._fade_anim = fade
        anim_group.start()
    except Exception as e:
        print(f"Animation error: {e}")


def slide_widget(widget: QWidget, start_rect: QRect, end_rect: QRect, duration: int = 250):
    """Smooth slide animation with fade effect for geometry changes."""
    try:
        anim_group = QParallelAnimationGroup()
    
        geom_anim = QPropertyAnimation(widget, b"geometry")
        geom_anim.setDuration(duration)
        geom_anim.setStartValue(start_rect)
        geom_anim.setEndValue(end_rect)
        geom_anim.setEasingCurve(QEasingCurve.Type.OutQuint)
    
        if widget.graphicsEffect():
            widget.graphicsEffect().setEnabled(False)
            widget.setGraphicsEffect(None)
        
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(duration)
        fade.setStartValue(0.95)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_group.addAnimation(geom_anim)
        anim_group.addAnimation(fade)
    
        widget._anim_group = anim_group
        widget._geom_anim = geom_anim
        widget._fade_anim = fade
        anim_group.start()
    except Exception as e:
        print(f"Animation error: {e}")
