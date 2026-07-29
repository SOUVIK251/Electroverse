"""
Next Connection & Guided Wiring Assistant Widget
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class WiringPanelWidget(QWidget):
    step_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.guided_connections = []
        self.current_step_idx = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        self.banner_assistant = QFrame()
        self.banner_assistant.setStyleSheet("background-color: #032b45; border: 2px solid #0284c7; border-radius: 6px; padding: 6px;")
        b_lay = QVBoxLayout(self.banner_assistant)
        b_lay.setContentsMargins(6, 4, 6, 4)
        b_lay.setSpacing(3)
        
        b_header = QHBoxLayout()
        self.lbl_assistant_title = QLabel("──────────────  NEXT CONNECTION  ──────────────")
        self.lbl_assistant_title.setStyleSheet("color: #38bdf8; font-weight: 800; font-size: 9pt;")
        b_header.addWidget(self.lbl_assistant_title)
        b_header.addStretch()
        
        self.lbl_conn_counter = QLabel("Connections: 1 / 5 Completed")
        self.lbl_conn_counter.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        b_header.addWidget(self.lbl_conn_counter)
        
        self.progress_guided = QProgressBar()
        self.progress_guided.setRange(0, 100)
        self.progress_guided.setValue(20)
        self.progress_guided.setFixedWidth(80)
        self.progress_guided.setFixedHeight(5)
        self.progress_guided.setTextVisible(False)
        self.progress_guided.setStyleSheet("QProgressBar { background-color: #0369a1; border: none; border-radius: 2px; } QProgressBar::chunk { background-color: #38bdf8; border-radius: 2px; }")
        b_header.addWidget(self.progress_guided)
        
        b_lay.addLayout(b_header)
        
        card_grid = QGridLayout()
        card_grid.setSpacing(2)
        
        card_grid.addWidget(QLabel("FROM:"), 0, 0)
        self.lbl_card_from = QLabel("+5V Power Terminal")
        self.lbl_card_from.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_from, 0, 1)
        
        card_grid.addWidget(QLabel("TO:"), 0, 2)
        self.lbl_card_to = QLabel("Pin 14 (VCC)")
        self.lbl_card_to.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_to, 0, 3)
        
        card_grid.addWidget(QLabel("WIRE COLOR:"), 1, 0)
        self.lbl_card_color = QLabel("Red Wire")
        self.lbl_card_color.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_color, 1, 1)
        
        card_grid.addWidget(QLabel("PURPOSE:"), 1, 2)
        self.lbl_card_purpose = QLabel("IC Power Supply")
        self.lbl_card_purpose.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 8.5pt;")
        card_grid.addWidget(self.lbl_card_purpose, 1, 3)
        
        b_lay.addLayout(card_grid)
        
        self.lbl_card_reason = QLabel("REASON: Powers internal logic gates. Without VCC power the IC cannot operate.")
        self.lbl_card_reason.setStyleSheet("color: #93c5fd; font-size: 8pt; font-style: italic;")
        b_lay.addWidget(self.lbl_card_reason)
        
        act_lay = QHBoxLayout()
        self.btn_center_prev = QPushButton(" ⬅ Previous")
        self.btn_center_prev.setStyleSheet("background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; font-weight: bold; padding: 2px 6px; border-radius: 3px; font-size: 8pt;")
        self.btn_center_prev.clicked.connect(self.prev_guided_step)
        act_lay.addWidget(self.btn_center_prev)
        
        act_lay.addStretch()
        
        self.btn_center_next = QPushButton(" ✓ Verify & Next ➡")
        self.btn_center_next.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_center_next.clicked.connect(self.advance_guided_step)
        act_lay.addWidget(self.btn_center_next)
        
        b_lay.addLayout(act_lay)
        layout.addWidget(self.banner_assistant)

    def load_guided_steps(self, steps):
        self.guided_connections = steps
        self.current_step_idx = 0
        self.update_card_ui()

    def update_card_ui(self):
        if not self.guided_connections:
            return
        self.current_step_idx = max(0, min(self.current_step_idx, len(self.guided_connections) - 1))
        conn = self.guided_connections[self.current_step_idx]
        
        self.lbl_assistant_title.setText(f"──────  NEXT CONNECTION (Card {self.current_step_idx + 1} of {len(self.guided_connections)})  ──────")
        self.lbl_conn_counter.setText(f"Conn: {self.current_step_idx + 1}/{len(self.guided_connections)}")
        
        pct = int(((self.current_step_idx + 1) / len(self.guided_connections)) * 100)
        self.progress_guided.setValue(pct)
        
        self.lbl_card_from.setText(conn.get("from", ""))
        self.lbl_card_to.setText(conn.get("to", ""))
        self.lbl_card_color.setText(conn.get("color", "Red Wire"))
        self.lbl_card_purpose.setText(conn.get("purpose", ""))
        self.lbl_card_reason.setText(conn.get("reason", ""))
        self.step_changed.emit(self.current_step_idx)

    def advance_guided_step(self):
        if self.current_step_idx < len(self.guided_connections) - 1:
            self.current_step_idx += 1
            self.update_card_ui()

    def prev_guided_step(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.update_card_ui()
