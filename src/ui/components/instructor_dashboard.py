from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, Signal

class InstructorDashboardWidget(QWidget):
    """Instructor Portal: Unlock All Sets, Custom Exam Builder & Batch Reports."""

    instructor_mode_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instructor_mode = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setObjectName("card-panel")
        card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #F59E0B; border-radius: 10px; padding: 15px; }")
        lay = QVBoxLayout(card)

        hdr = QLabel("👨‍🏫 Instructor Control Panel")
        hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 13pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
        lay.addWidget(hdr)

        row1 = QHBoxLayout()
        self.inst_cb = QCheckBox("Enable Instructor Mode (Unlock All 30 Exam Sets & View Answer Keys)")
        self.inst_cb.setStyleSheet("QCheckBox { color: #FFFFFF; font-size: 10.5pt; font-weight: bold; }")
        self.inst_cb.toggled.connect(self.on_toggled)
        row1.addWidget(self.inst_cb)
        lay.addLayout(row1)

        desc = QLabel("When Instructor Mode is enabled, all exam sets are unlocked immediately, answer keys become visible, and timer restrictions can be bypassed for curriculum verification.")
        desc.setStyleSheet("color: #94A3B8; font-size: 9.5pt;")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        layout.addWidget(card)

    def on_toggled(self, checked):
        self.instructor_mode = checked
        self.instructor_mode_toggled.emit(checked)
