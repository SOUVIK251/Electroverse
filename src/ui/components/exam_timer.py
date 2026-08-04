from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class ExamTimerWidget(QWidget):
    """Timer Widget with 5m Orange Warning and 1m Red Alert States."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame()
        self.card.setStyleSheet("background-color: #0F172A; border: 1px solid #26334D; border-radius: 6px; padding: 4px 12px;")
        c_lay = QHBoxLayout(self.card)

        icon_lbl = QLabel("⏱️")
        icon_lbl.setStyleSheet("font-size: 11pt;")
        
        self.t_lbl = QLabel("30:00")
        self.t_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12pt; font-family: Consolas, monospace;")

        c_lay.addWidget(icon_lbl)
        c_lay.addWidget(self.t_lbl)

        layout.addWidget(self.card)

    def update_time(self, remaining_sec):
        mins = remaining_sec // 60
        secs = remaining_sec % 60
        t_str = f"{mins:02d}:{secs:02d}"
        self.t_lbl.setText(t_str)

        if remaining_sec <= 60:
            self.card.setStyleSheet("background-color: #450A0A; border: 2px solid #EF4444; border-radius: 6px; padding: 4px 12px;")
            self.t_lbl.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 12pt; font-family: Consolas, monospace;")
        elif remaining_sec <= 300:
            self.card.setStyleSheet("background-color: #451A03; border: 1px solid #F59E0B; border-radius: 6px; padding: 4px 12px;")
            self.t_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 12pt; font-family: Consolas, monospace;")
        else:
            self.card.setStyleSheet("background-color: #0F172A; border: 1px solid #26334D; border-radius: 6px; padding: 4px 12px;")
            self.t_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12pt; font-family: Consolas, monospace;")
