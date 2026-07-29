"""
Stage-Aware Instructor & Professor Guidance Widget
Renders stage-specific professor notes, circuit objectives, theory, and boolean equations.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class InstructorPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_experiment = None
        self.current_stage = "Foundation"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        card = QFrame()
        card.setStyleSheet("background-color: #0b1329; border: 1px solid #0284c7; border-radius: 6px; padding: 6px;")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(6, 6, 6, 6)
        
        self.lbl_professor_title = QLabel("👨‍🏫 Professor's Guidance Notes")
        self.lbl_professor_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.lbl_professor_title.setStyleSheet("color: #38bdf8;")
        c_lay.addWidget(self.lbl_professor_title)
        
        self.lbl_stage_badge = QLabel("Stage: Foundation (Basic Gates)")
        self.lbl_stage_badge.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8pt;")
        c_lay.addWidget(self.lbl_stage_badge)
        
        self.txt_instructor_notes = QTextEdit()
        self.txt_instructor_notes.setReadOnly(True)
        self.txt_instructor_notes.setStyleSheet("QTextEdit { background-color: #090d16; color: #93c5fd; border: 1px solid #1e293b; border-radius: 4px; font-size: 8pt; line-height: 1.4; }")
        c_lay.addWidget(self.txt_instructor_notes)
        
        layout.addWidget(card)

    def load_experiment_notes(self, exp_data, stage_name="Foundation"):
        self.current_experiment = exp_data
        self.current_stage = stage_name
        
        self.lbl_stage_badge.setText(f"Stage: {stage_name}")
        
        inst_file = os.path.join(exp_data["_path"], "instructor.json")
        note_text = ""
        if os.path.exists(inst_file):
            try:
                with open(inst_file, "r", encoding="utf-8") as fp:
                    inst_data = json.load(fp)
                    stage_key = stage_name.lower().split()[0]
                    note_text = inst_data.get(stage_key, inst_data.get("foundation", ""))
            except Exception as e:
                note_text = f"Instructor note load error: {e}"
        else:
            note_text = exp_data.get("theory", "No instructor notes found.")
            
        full_html = f"""
        <p><b>Objectives:</b></p>
        <ul>
            {"".join(f"<li>{obj}</li>" for obj in exp_data.get("objectives", []))}
        </ul>
        <p><b>Professor Remarks ({stage_name}):</b></p>
        <p><i>{note_text}</i></p>
        <p><b>Boolean Equations:</b></p>
        <ul>
            {"".join(f"<li><b>{k}:</b> {v}</li>" for k, v in exp_data.get("boolean_equations", {}).items())}
        </ul>
        """
        self.txt_instructor_notes.setHtml(full_html)
