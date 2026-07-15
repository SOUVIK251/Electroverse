from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
import qtawesome as qta

class ToastNotification(QWidget):
    """A premium, self-dismissing overlay toast notification."""
    
    def __init__(self, parent, message: str, is_success: bool = True):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Transparent background, borderless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        
        # Styling
        border_color = "#10b981" if is_success else "#ef4444"
        bg_color = "rgba(17, 24, 39, 0.95)" # Premium dark glass
        
        # Main container layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Icon
        icon_str = "fa5s.check-circle" if is_success else "fa5s.exclamation-circle"
        icon_color = "#10b981" if is_success else "#ef4444"
        self.icon_label = QLabel()
        self.icon_label.setPixmap(qta.icon(icon_str, color=icon_color).pixmap(18, 18))
        
        # Text Message
        self.msg_label = QLabel(message)
        self.msg_label.setStyleSheet("color: #f8fafc; font-size: 10pt; font-weight: 500;")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.msg_label)
        
        # Overlay style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.adjustSize()
        
        # Animation parameters
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Timer to auto-close
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)
        
        # Positioning relative to parent
        self.parent = parent
        self.parent.installEventFilter(self)
        self.reposition()
        
        # Start show
        self.setWindowOpacity(0.0)
        self.show()
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()
        
        self.timer.start(3000) # Show for 3 seconds

    def reposition(self):
        """Positions toast at the top-center of the parent window."""
        if not self.parent:
            return
        parent_rect = self.parent.rect()
        # Top center offset by 80px
        x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
        y = parent_rect.y() + 80
        # Convert to global coordinate if parent has global map
        global_pos = self.parent.mapToGlobal(QPoint(x, y))
        self.move(global_pos)

    def fade_out(self):
        """Smoothly fade out and delete widget."""
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.windowOpacity())
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.finished.connect(self.close)
        self.opacity_anim.start()
        
    def eventFilter(self, watched, event):
        """Ensures toast repositions itself if parent window is resized or moved."""
        if watched == self.parent and event.type() in [event.Type.Resize, event.Type.Move]:
            self.reposition()
        return super().eventFilter(watched, event)
