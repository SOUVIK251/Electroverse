"""
Interactive Experiment Quiz Widget
Renders multiple choice questions and provides feedback.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QRadioButton, QPushButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class QuizPanelWidget(QWidget):
    quiz_completed = Signal(int, int) # score, total
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.current_q_idx = 0
        self.score = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 8px;")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(6, 6, 6, 6)
        c_lay.setSpacing(6)
        
        title = QLabel("❓ Knowledge Verification Quiz")
        title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #eab308;")
        c_lay.addWidget(title)
        
        self.lbl_question = QLabel("Select an experiment to begin quiz.")
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setStyleSheet("color: #f8fafc; font-size: 8.5pt; font-weight: bold;")
        c_lay.addWidget(self.lbl_question)
        
        self.btn_group = QButtonGroup(self)
        self.radio_options = []
        for i in range(4):
            r = QRadioButton(f"Option {i+1}")
            r.setStyleSheet("color: #94a3b8; font-size: 8pt;")
            c_lay.addWidget(r)
            self.btn_group.addButton(r, i)
            self.radio_options.append(r)
            
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.setStyleSheet("font-size: 8pt; font-style: italic;")
        c_lay.addWidget(self.lbl_feedback)
        
        self.btn_submit = QPushButton(" Submit Answer ")
        self.btn_submit.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 8.5pt;")
        self.btn_submit.clicked.connect(self.submit_answer)
        c_lay.addWidget(self.btn_submit)
        
        layout.addWidget(card)

    def load_quiz(self, exp_path):
        quiz_file = os.path.join(exp_path, "quiz.json")
        self.questions = []
        self.current_q_idx = 0
        self.score = 0
        self.lbl_feedback.setText("")
        
        if os.path.exists(quiz_file):
            try:
                with open(quiz_file, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    self.questions = data.get("questions", [])
            except Exception as e:
                print(f"Quiz load error: {e}")
                
        if self.questions:
            self.show_question(0)
        else:
            self.lbl_question.setText("No quiz available for this experiment.")
            for r in self.radio_options:
                r.setVisible(False)
            self.btn_submit.setEnabled(False)

    def show_question(self, idx):
        if 0 <= idx < len(self.questions):
            q = self.questions[idx]
            self.lbl_question.setText(f"Q{idx+1}: {q['question']}")
            options = q.get("options", [])
            self.btn_group.setExclusive(False)
            for i, r in enumerate(self.radio_options):
                if i < len(options):
                    r.setText(options[i])
                    r.setChecked(False)
                    r.setVisible(True)
                else:
                    r.setVisible(False)
            self.btn_group.setExclusive(True)
            self.btn_submit.setEnabled(True)
            self.lbl_feedback.setText("")

    def submit_answer(self):
        if not self.questions or self.current_q_idx >= len(self.questions):
            return
            
        selected_id = self.btn_group.checkedId()
        if selected_id == -1:
            QMessageBox.information(self, "Quiz", "Please select an answer.")
            return
            
        q = self.questions[self.current_q_idx]
        correct_idx = q.get("answer_idx", 0)
        explanation = q.get("explanation", "")
        
        if selected_id == correct_idx:
            self.score += 1
            self.lbl_feedback.setText(f"✓ Correct! {explanation}")
            self.lbl_feedback.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8pt;")
        else:
            self.lbl_feedback.setText(f"❌ Incorrect. {explanation}")
            self.lbl_feedback.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8pt;")
            
        self.current_q_idx += 1
        if self.current_q_idx < len(self.questions):
            self.btn_submit.setText(" Next Question ➡ ")
        else:
            self.btn_submit.setText(" Quiz Completed ")
            self.btn_submit.setEnabled(False)
            self.quiz_completed.emit(self.score, len(self.questions))
