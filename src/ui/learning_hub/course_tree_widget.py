"""
Collapsible Syllabus Course Tree Navigation Panel
Renders a hierarchical syllabus tree for Digital Electronics (Introduction, Number Systems, Boolean Algebra, Logic Gates, Universal Gates, Combinational Circuits, Sequential Circuits, Digital ICs, Breadboard, Applications).
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class CourseTreeWidget(QWidget):
    topic_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_syllabus_tree()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        title = QLabel("📚 Course Syllabus Tree")
        title.setFont(QFont("Arial", 9.5, QFont.Weight.Bold))
        title.setStyleSheet("color: #06b6d4;")
        layout.addWidget(title)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget { background-color: #090d16; color: #f8fafc; border: 1px solid #1e293b; border-radius: 6px; }
            QTreeWidget::item { padding: 4px; font-size: 8.5pt; }
            QTreeWidget::item:selected { background-color: #0284c7; color: white; }
        """)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

    def load_syllabus_tree(self):
        self.tree.clear()
        
        categories = [
            {
                "name": "📂 1. Introduction",
                "topics": [
                    {"name": "⚡ Intro to Digital Electronics", "path": "introduction/intro.json"}
                ]
            },
            {
                "name": "📂 2. Number Systems",
                "topics": [
                    {"name": "🔢 Binary, Hex & Conversions", "path": "number_systems/number_systems.json"}
                ]
            },
            {
                "name": "📂 3. Boolean Algebra",
                "topics": [
                    {"name": "🧮 Laws & K-Map Minimization", "path": "boolean_algebra/boolean_algebra.json"}
                ]
            },
            {
                "name": "📂 4. Fundamental Logic Gates",
                "topics": [
                    {"name": "⚡ AND Gate (IC 7408)", "path": "logic_gates/and/theory.json"},
                    {"name": "⚡ OR Gate (IC 7432)", "path": "logic_gates/or/theory.json"},
                    {"name": "⚡ NOT Inverter (IC 7404)", "path": "logic_gates/not/theory.json"},
                    {"name": "⚡ NAND Gate (IC 7400)", "path": "logic_gates/nand/theory.json"},
                    {"name": "⚡ NOR Gate (IC 7402)", "path": "logic_gates/nor/theory.json"},
                    {"name": "⚡ XOR Gate (IC 7486)", "path": "logic_gates/xor/theory.json"},
                    {"name": "⚡ XNOR Gate (IC 74266)", "path": "logic_gates/xnor/theory.json"}
                ]
            },
            {
                "name": "📂 5. Universal Gates",
                "topics": [
                    {"name": "🔄 Universal NAND Synthesis", "path": "universal_gates/nand/theory.json"}
                ]
            },
            {
                "name": "📂 6. Combinational Circuits",
                "topics": [
                    {"name": "➕ 1-Bit Half Adder", "path": "combinational/half_adder/theory.json"},
                    {"name": "➕ 1-Bit Full Adder", "path": "combinational/full_adder/theory.json"},
                    {"name": "🔀 2:1 Multiplexer (MUX)", "path": "combinational/mux/theory.json"},
                    {"name": "🔍 2-to-4 Line Decoder", "path": "combinational/decoder/theory.json"},
                    {"name": "💡 BCD to 7-Segment Display", "path": "combinational/bcd_7segment/theory.json"}
                ]
            }
        ]
        
        for cat in categories:
            cat_item = QTreeWidgetItem(self.tree, [cat["name"]])
            cat_item.setFont(0, QFont("Arial", 8.5, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor("#38bdf8"))
            cat_item.setExpanded(True)
            
            for t in cat["topics"]:
                item = QTreeWidgetItem(cat_item, [f"  {t['name']}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {"path_to_data": t["path"], "name": t["name"]})

    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.topic_selected.emit(data)
