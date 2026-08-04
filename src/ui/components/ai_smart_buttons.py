"""
ElectroVerse Context-Aware Smart AI Buttons Component
Creates reusable action buttons for Lessons, Simulations, Assessments, and Formulas.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
import qtawesome as qta


class AISmartButtonsWidget(QFrame):
    """Context-aware Smart AI Button Bar."""

    def __init__(self, target_type: str = "lesson", context_data: dict = None, on_action_cb=None, parent=None):
        super().__init__(parent)
        self.target_type = target_type  # 'lesson' or 'simulation'
        self.context_data = context_data or {}
        self.on_action_cb = on_action_cb

        self.setStyleSheet("""
            QFrame {
                background-color: #0b1020;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)

        tag = QLabel("🤖 AI SMART ASSIST:")
        tag.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 8pt;")
        lay.addWidget(tag)

        if self.target_type == "lesson":
            btns_config = [
                ("Ask AI", "fa5s.comments", "Engineering Tutor"),
                ("Explain Again", "fa5s.redo", "Engineering Tutor"),
                ("Generate Notes", "fa5s.sticky-note", "Report Generator"),
                ("Generate Viva", "fa5s.user-graduate", "Viva Examiner"),
                ("Generate MCQs", "fa5s.tasks", "Viva Examiner"),
                ("Solve Example", "fa5s.calculator", "Problem Solver"),
            ]
        else:  # simulation
            btns_config = [
                ("Explain Output", "fa5s.wave-square", "Simulation Explainer"),
                ("Why?", "fa5s.question-circle", "Simulation Explainer"),
                ("Predict Changes", "fa5s.chart-line", "Simulation Explainer"),
                ("Common Errors", "fa5s.exclamation-triangle", "Simulation Explainer"),
            ]

        for label, icon_name, mode in btns_config:
            btn = QPushButton(f" {label}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 8pt;
                    padding: 4px 8px;
                    border: 1px solid #334155;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0369a1;
                    border-color: #38bdf8;
                }
            """)
            btn.setIcon(qta.icon(icon_name, color="#06b6d4"))
            btn.clicked.connect(lambda _, l=label, m=mode: self.trigger_action(l, m))
            lay.addWidget(btn)

        lay.addStretch()

    def trigger_action(self, action_label: str, mode: str):
        if self.on_action_cb:
            self.on_action_cb(action_label, mode, self.context_data)
