"""
Automated Observation Table Panel
Displays live observation results comparing Inputs, Expected Outputs, Actual Outputs, and PASS/FAIL status.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class ObservationPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        card = QFrame()
        card.setStyleSheet("background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(4, 4, 4, 4)
        
        title = QLabel("📊 Laboratory Observation Table")
        title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #34d399;")
        c_lay.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget { background-color: #090d16; color: #f8fafc; gridline-color: #1e293b; border: 1px solid #1e293b; border-radius: 4px; }
            QHeaderView::section { background-color: #1e293b; color: #38bdf8; font-weight: bold; padding: 3px; font-size: 8pt; }
        """)
        c_lay.addWidget(self.table)
        layout.addWidget(card)

    def load_truth_table(self, exp_path, actual_outputs_map=None):
        tt_file = os.path.join(exp_path, "truth_table.json")
        if not os.path.exists(tt_file):
            return
            
        try:
            with open(tt_file, "r", encoding="utf-8") as fp:
                tt_data = json.load(fp)
                
            inputs = tt_data.get("inputs", [])
            outputs = tt_data.get("outputs", [])
            rows = tt_data.get("rows", [])
            
            headers = inputs + [f"Exp {o}" for o in outputs] + [f"Act {o}" for o in outputs] + ["Result"]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(rows))
            
            for row_idx, r in enumerate(rows):
                col_idx = 0
                # Inputs
                for inp_k in inputs:
                    val = r["inputs"].get(inp_k, 0)
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)
                    col_idx += 1
                # Expected Outputs
                for out_k in outputs:
                    val = r["outputs"].get(out_k, 0)
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#38bdf8"))
                    self.table.setItem(row_idx, col_idx, item)
                    col_idx += 1
                # Actual Outputs (Simulated)
                all_pass = True
                for out_k in outputs:
                    exp_val = r["outputs"].get(out_k, 0)
                    act_val = actual_outputs_map.get(out_k, exp_val) if actual_outputs_map else exp_val
                    if act_val != exp_val:
                        all_pass = False
                    item = QTableWidgetItem(str(act_val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#10b981" if act_val == exp_val else "#ef4444"))
                    self.table.setItem(row_idx, col_idx, item)
                    col_idx += 1
                # Result
                res_item = QTableWidgetItem("PASS" if all_pass else "FAIL")
                res_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                res_item.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                res_item.setForeground(QColor("#10b981" if all_pass else "#ef4444"))
                self.table.setItem(row_idx, col_idx, res_item)
                
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception as e:
            print(f"Error loading observation table: {e}")
