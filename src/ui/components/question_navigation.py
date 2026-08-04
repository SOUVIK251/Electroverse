from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class QuestionNavigation(QWidget):
    """Left Panel Question Navigator Grid (1-30 Status Buttons)."""

    question_selected = Signal(int) # 0-indexed

    def __init__(self, total_questions=30, parent=None):
        super().__init__(parent)
        self.total_questions = total_questions
        self.buttons = []
        self.statuses = ["NOT_VISITED"] * total_questions # NOT_VISITED, VISITED, ANSWERED, MARKED
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(8, 8, 8, 8)
        main_lay.setSpacing(10)

        # Header
        hdr = QLabel("📌 Question Grid (1-30)")
        hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 10.5pt; padding-bottom: 4px;")
        main_lay.addWidget(hdr)

        # Legend
        leg_frame = QFrame()
        leg_frame.setStyleSheet("background-color: #0F172A; border: 1px solid #26334D; border-radius: 6px; padding: 6px;")
        leg_lay = QGridLayout(leg_frame)
        leg_lay.setSpacing(4)

        items = [
            ("⬜ Not Visited", "#475569"),
            ("🟦 Visited", "#2563EB"),
            ("🟩 Answered", "#10B981"),
            ("🟨 Marked", "#F59E0B")
        ]
        for idx, (txt, clr) in enumerate(items):
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color: {clr}; font-weight: bold; font-size: 8.5pt;")
            leg_lay.addWidget(lbl, idx // 2, idx % 2)

        main_lay.addWidget(leg_frame)

        # 5x6 Grid of Buttons
        grid_frame = QFrame()
        grid_frame.setObjectName("card-panel")
        grid_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 8px; }")
        grid_lay = QGridLayout(grid_frame)
        grid_lay.setSpacing(6)

        for i in range(self.total_questions):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(self._get_style("NOT_VISITED", False))
            btn.clicked.connect(lambda checked=False, q_idx=i: self.question_selected.emit(q_idx))
            grid_lay.addWidget(btn, i // 5, i % 5)
            self.buttons.append(btn)

        main_lay.addWidget(grid_frame)
        main_lay.addStretch()

    def update_status(self, q_idx, status, is_current=False):
        if 0 <= q_idx < len(self.statuses):
            self.statuses[q_idx] = status
            self.buttons[q_idx].setStyleSheet(self._get_style(status, is_current))

    def _get_style(self, status, is_current):
        border = "2px solid #38BDF8" if is_current else "1px solid #26334D"
        
        if status == "ANSWERED":
            bg = "#10B981"; color = "#FFFFFF"
        elif status == "MARKED":
            bg = "#F59E0B"; color = "#FFFFFF"
        elif status == "VISITED":
            bg = "#2563EB"; color = "#FFFFFF"
        else: # NOT_VISITED
            bg = "#1E293B"; color = "#94A3B8"

        return f"QPushButton {{ background-color: {bg}; color: {color}; font-weight: bold; border-radius: 6px; border: {border}; font-size: 10pt; }} QPushButton:hover {{ border: 2px solid #06B6D4; }}"
