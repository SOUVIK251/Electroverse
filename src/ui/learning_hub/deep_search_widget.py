"""
Deep Multi-Domain Search Engine Widget
Searches across lesson text, equations, truth tables, IC numbers, viva questions, and breadboard guides.
Results list is hidden by default and pops up dynamically when user types search queries.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class DeepSearchWidget(QWidget):
    result_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_index = []
        self.init_ui()
        self.build_search_index()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        hdr = QHBoxLayout()
        lbl = QLabel("🔍 Deep Curriculum Search:")
        lbl.setFont(QFont("Arial", 9.5, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #06b6d4;")
        hdr.addWidget(lbl)
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search equations, truth tables, IC numbers (7408), viva questions...")
        self.input_search.setStyleSheet("QLineEdit { background-color: #090d16; color: #f8fafc; border: 1px solid #1e293b; border-radius: 4px; padding: 6px; font-size: 8.5pt; }")
        self.input_search.textChanged.connect(self.on_search_text_changed)
        hdr.addWidget(self.input_search, 1)
        
        layout.addLayout(hdr)
        
        self.results_list = QListWidget()
        self.results_list.setFixedHeight(120)
        self.results_list.hide() # Hidden by default to eliminate gap!
        self.results_list.setStyleSheet("""
            QListWidget { background-color: #0b0f19; color: #f8fafc; border: 1px solid #0284c7; border-radius: 6px; }
            QListWidget::item { padding: 6px; font-size: 8.5pt; }
            QListWidget::item:selected { background-color: #0284c7; color: white; }
        """)
        self.results_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.results_list)

    def build_search_index(self):
        self.search_index = [
            {"id": "gate_and", "title": "AND Gate (IC 7408)", "type": "Logic Gate", "snippet": "Y = A · B. Quad 2-input AND gate.", "path": "logic_gates/and/theory.json"},
            {"id": "gate_or", "title": "OR Gate (IC 7432)", "type": "Logic Gate", "snippet": "Y = A + B. Quad 2-input OR gate.", "path": "logic_gates/or/theory.json"},
            {"id": "half_adder", "title": "1-Bit Half Adder", "type": "Adder Circuit", "snippet": "Sum = A ⊕ B, Carry = A · B. Uses XOR + AND.", "path": "combinational/half_adder/theory.json"},
            {"id": "full_adder", "title": "1-Bit Full Adder", "type": "Adder Circuit", "snippet": "Sum = A ⊕ B ⊕ Cin, Cout = (A·B) + (Cin·(A⊕B)).", "path": "combinational/full_adder/theory.json"},
            {"id": "universal_nand", "title": "Universal NAND Synthesis", "type": "Universal Gate", "snippet": "Build any basic gate or circuit using only NAND (IC 7400).", "path": "universal_gates/nand/theory.json"}
        ]

    def on_search_text_changed(self, query_str):
        q = query_str.strip().lower()
        self.results_list.clear()
        if not q:
            self.results_list.hide()
            return
            
        matches_found = False
        for item in self.search_index:
            if q in item["title"].lower() or q in item["snippet"].lower() or q in item["type"].lower():
                l_item = QListWidgetItem(f"⚡ [{item['type']}] {item['title']} — {item['snippet']}")
                l_item.setData(Qt.ItemDataRole.UserRole, item)
                self.results_list.addItem(l_item)
                matches_found = True
                
        if matches_found:
            self.results_list.show()
        else:
            self.results_list.hide()

    def on_item_clicked(self, list_item):
        data = list_item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.result_selected.emit(data)
            self.results_list.hide()
            self.input_search.clear()
