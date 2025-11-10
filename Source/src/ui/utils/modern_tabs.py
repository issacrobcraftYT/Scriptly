from PyQt6.QtWidgets import QTabWidget, QWidget, QStackedWidget, QTabBar
from PyQt6.QtCore import QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, Qt
from .ui_effects import apply_shadow, apply_rounded_corners

class ModernTabWidget(QTabWidget):
    """A modern tab widget with smooth transitions and visual effects."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Setup appearance
        self.setDocumentMode(True)
        self.setTabPosition(QTabWidget.TabPosition.North)
        
        # Custom stack (solo para control interno)
        self._stack = QStackedWidget()
        
        # Animaciones
        self._current_index = 0
        self._animations = {}
        
        # Modern styling
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin: 0px 2px;
                border: none;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

    def addTab(self, widget: QWidget, label: str):
        """Add a tab with smooth transition animations."""
        if widget is None:
            return
        
        index = self.count()
        
        # Guardar geometría inicial (solo si existe)
        original_geometry = widget.geometry()
        if original_geometry.isNull():
            original_geometry.setWidth(200)
            original_geometry.setHeight(150)
        
        # Crear animaciones
        show_anim = QPropertyAnimation(widget, b"geometry")
        show_anim.setDuration(300)
        show_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        hide_anim = QPropertyAnimation(widget, b"geometry")
        hide_anim.setDuration(300)
        hide_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Guardar anims
        self._animations[index] = {
            'show': show_anim,
            'hide': hide_anim,
            'original_geometry': original_geometry
        }
        
        super().addTab(widget, label)

    def setCurrentIndex(self, index: int):
        """Change tab with smooth transition."""
        # Verifica que index sea válido
        if index is None or index < 0 or index >= self.count():
            return
        
        if index == self._current_index:
            return

        # Obtén los widgets
        old_widget = self.widget(self._current_index)
        new_widget = self.widget(index)
        
        if not old_widget or not new_widget:
            super().setCurrentIndex(index)
            self._current_index = index
            return

        # Si no hay animaciones guardadas para alguno, cambia directo
        if index not in self._animations or self._current_index not in self._animations:
            super().setCurrentIndex(index)
            self._current_index = index
            return

        # Animaciones grupales
        group = QParallelAnimationGroup()

        hide_anim = self._animations[self._current_index]['hide']
        hide_geo = self._animations[self._current_index]['original_geometry']
        hide_anim.setStartValue(hide_geo)
        hide_anim.setEndValue(hide_geo.translated(hide_geo.width(), 0))
        group.addAnimation(hide_anim)

        show_anim = self._animations[index]['show']
        show_geo = self._animations[index]['original_geometry']
        show_anim.setStartValue(show_geo.translated(-show_geo.width(), 0))
        show_anim.setEndValue(show_geo)
        group.addAnimation(show_anim)

        # Arranca animaciones
        group.start()
        
        # Cambia el índice real
        super().setCurrentIndex(index)
        self._current_index = index

    def setTabEnabled(self, index: int, enabled: bool):
        """Enable/disable tab with visual feedback."""
        super().setTabEnabled(index, enabled)
        tabbar = self.tabBar()
        if not tabbar:
            return
        btn = tabbar.tabButton(index, QTabBar.ButtonPosition.LeftSide)
        if btn:
            btn.setEnabled(enabled)
