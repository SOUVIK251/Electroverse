"""
Interactive Sequential Learning Path Widget (Compact Sidebar Edition)
Renders a compact visual node-based learning path graph showing progressive unlock status,
completion badges, estimated reading times, and "Start Learning" triggers.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class LearningPathWidget(QWidget):
    topic_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.learning_nodes = []
        self.completed_node_ids = set()
        self.init_ui()
        self.load_learning_path()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Compact Header Banner
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;")
        h_lay = QVBoxLayout(hdr)
        h_lay.setContentsMargins(6, 4, 6, 4)
        h_lay.setSpacing(4)
        
        t1 = QLabel("🗺️ Sequential Learning Path")
        t1.setFont(QFont("Arial", 9.5, QFont.Weight.Bold))
        t1.setStyleSheet("color: #38bdf8;")
        h_lay.addWidget(t1)
        
        v_prog = QHBoxLayout()
        self.lbl_overall_pct = QLabel("Progress: 0%")
        self.lbl_overall_pct.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8.5pt;")
        v_prog.addWidget(self.lbl_overall_pct)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { background-color: #1e293b; border-radius: 3px; } QProgressBar::chunk { background-color: #10b981; border-radius: 3px; }")
        v_prog.addWidget(self.progress_bar, 1)
        h_lay.addLayout(v_prog)
        
        layout.addWidget(hdr)
        
        # Scrollable Node Grid Container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.nodes_container = QWidget()
        self.nodes_grid = QVBoxLayout(self.nodes_container)
        self.nodes_grid.setContentsMargins(4, 4, 4, 4)
        self.nodes_grid.setSpacing(8)
        
        scroll.setWidget(self.nodes_container)
        layout.addWidget(scroll, 1)

    def load_learning_path(self):
        base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "theory")
        path_file = os.path.abspath(os.path.join(base, "learning_path.json"))
        
        if os.path.exists(path_file):
            try:
                with open(path_file, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    self.learning_nodes = data.get("path", [])
            except Exception as e:
                print(f"Error loading learning_path.json: {e}")

        self.render_path_nodes()

    def make_click_callback(self, node_data):
        def callback():
            self.on_node_clicked(node_data)
        return callback

    def on_node_clicked(self, node_data):
        self.completed_node_ids.add(node_data["id"])
        
        # Unlock next node in sequence if any
        current_idx = -1
        for i, n in enumerate(self.learning_nodes):
            if n["id"] == node_data["id"]:
                current_idx = i
                break
        if current_idx != -1 and current_idx + 1 < len(self.learning_nodes):
            self.learning_nodes[current_idx + 1]["unlocked"] = True
            
        pct = int((len(self.completed_node_ids) / max(1, len(self.learning_nodes))) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_overall_pct.setText(f"Progress: {pct}%")
        
        self.render_path_nodes()
        self.topic_selected.emit(node_data)

    def render_path_nodes(self):
        # Clear existing layout
        while self.nodes_grid.count():
            item = self.nodes_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        for idx, node in enumerate(self.learning_nodes):
            is_unlocked = node.get("unlocked", True)
            is_completed = node["id"] in self.completed_node_ids
            
            card = QFrame()
            card.setStyleSheet(
                "background-color: #0b1329; border: 1px solid #0284c7; border-radius: 6px; padding: 6px;" if is_unlocked
                else "background-color: #090d16; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;"
            )
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(6, 6, 6, 6)
            c_lay.setSpacing(4)
            
            # Top row: Badge + Title
            r1 = QHBoxLayout()
            r1.setSpacing(6)
            
            badge = QLabel(f"#{idx+1}")
            badge.setFixedWidth(28)
            badge.setFixedHeight(22)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            badge.setStyleSheet("background-color: #0284c7; color: white; border-radius: 3px;" if is_unlocked else "background-color: #1e293b; color: #64748b; border-radius: 3px;")
            r1.addWidget(badge)
            
            lbl_title = QLabel(node["name"])
            lbl_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            lbl_title.setStyleSheet("color: #f8fafc;" if is_unlocked else "color: #64748b;")
            lbl_title.setWordWrap(True)
            r1.addWidget(lbl_title, 1)
            
            c_lay.addLayout(r1)
            
            # Bottom row: Meta + Action Button
            r2 = QHBoxLayout()
            r2.setSpacing(4)
            
            meta_str = f"⏱ {node.get('est_time', '15m')}"
            lbl_meta = QLabel(meta_str)
            lbl_meta.setStyleSheet("color: #38bdf8; font-size: 7.5pt;" if is_unlocked else "color: #475569; font-size: 7.5pt;")
            r2.addWidget(lbl_meta)
            
            r2.addStretch()
            
            btn = QPushButton("✓ Done" if is_completed else ("📖 Read" if is_unlocked else "🔒 Locked"))
            btn.setEnabled(is_unlocked)
            btn.setFixedHeight(24)
            btn.setStyleSheet(
                "background-color: #10b981; color: white; font-weight: bold; padding: 2px 8px; border-radius: 3px; font-size: 7.5pt;" if is_completed
                else ("background-color: #0284c7; color: white; font-weight: bold; padding: 2px 8px; border-radius: 3px; font-size: 7.5pt;" if is_unlocked
                else "background-color: #1e293b; color: #64748b; padding: 2px 8px; border-radius: 3px; font-size: 7.5pt;")
            )
            btn.clicked.connect(self.make_click_callback(node))
            r2.addWidget(btn)
            
            c_lay.addLayout(r2)
            
            self.nodes_grid.addWidget(card)
            
        self.nodes_grid.addStretch()

    def mark_completed(self, node_id):
        self.completed_node_ids.add(node_id)
        pct = int((len(self.completed_node_ids) / max(1, len(self.learning_nodes))) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_overall_pct.setText(f"Progress: {pct}%")
        self.render_path_nodes()
