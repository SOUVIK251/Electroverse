"""
Student Performance Assessment & Certificate Grade Panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class AssessmentPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 8px;")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(6, 6, 6, 6)
        
        title = QLabel("🏆 Performance Assessment & Certificate")
        title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8;")
        c_lay.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(4)
        
        grid.addWidget(QLabel("Connection Accuracy:"), 0, 0)
        self.lbl_accuracy = QLabel("100%")
        self.lbl_accuracy.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        grid.addWidget(self.lbl_accuracy, 0, 1)
        
        grid.addWidget(QLabel("Simulation Runs:"), 1, 0)
        self.lbl_sim_runs = QLabel("1")
        self.lbl_sim_runs.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 8.5pt;")
        grid.addWidget(self.lbl_sim_runs, 1, 1)
        
        grid.addWidget(QLabel("Quiz Score:"), 2, 0)
        self.lbl_quiz_score = QLabel("2 / 2 (100%)")
        self.lbl_quiz_score.setStyleSheet("color: #eab308; font-weight: bold; font-size: 8.5pt;")
        grid.addWidget(self.lbl_quiz_score, 2, 1)
        
        grid.addWidget(QLabel("Final Grade:"), 3, 0)
        self.lbl_final_grade = QLabel("A+ (Mastered)")
        self.lbl_final_grade.setStyleSheet("color: #10b981; font-weight: bold; font-size: 9.5pt;")
        grid.addWidget(self.lbl_final_grade, 3, 1)
        
        c_lay.addLayout(grid)
        layout.addWidget(card)

    def update_assessment(self, accuracy=100, sim_runs=1, quiz_score=2, quiz_total=2):
        self.lbl_accuracy.setText(f"{accuracy}%")
        self.lbl_sim_runs.setText(str(sim_runs))
        pct = int((quiz_score / max(1, quiz_total)) * 100)
        self.lbl_quiz_score.setText(f"{quiz_score} / {quiz_total} ({pct}%)")
        
        if accuracy >= 90 and pct >= 80:
            self.lbl_final_grade.setText("A+ (Mastered)")
            self.lbl_final_grade.setStyleSheet("color: #10b981; font-weight: bold; font-size: 9.5pt;")
        elif accuracy >= 75:
            self.lbl_final_grade.setText("B (Completed)")
            self.lbl_final_grade.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 9.5pt;")
        else:
            self.lbl_final_grade.setText("C (In Progress)")
            self.lbl_final_grade.setStyleSheet("color: #eab308; font-weight: bold; font-size: 9.5pt;")
