"""
Dynamic Experiment Browser Widget
Scans src/data/experiments/ folder for experiment plugins and groups them into categories.
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class ExperimentBrowserWidget(QWidget):
    experiment_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.experiments_cache = {}
        self.init_ui()
        self.load_experiments()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        title = QLabel("📚 Course Experiments")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #06b6d4;")
        layout.addWidget(title)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget { background-color: #090d16; color: #f8fafc; border: 1px solid #1e293b; border-radius: 4px; }
            QTreeWidget::item { padding: 4px; font-size: 8.5pt; }
            QTreeWidget::item:selected { background-color: #0284c7; color: white; }
        """)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

    def load_experiments(self):
        self.tree.clear()
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "experiments")
        base_dir = os.path.abspath(base_dir)
        
        categories = {}
        if os.path.exists(base_dir):
            for folder in os.listdir(base_dir):
                folder_path = os.path.join(base_dir, folder)
                exp_json = os.path.join(folder_path, "experiment.json")
                if os.path.isdir(folder_path) and os.path.exists(exp_json):
                    try:
                        with open(exp_json, "r", encoding="utf-8") as fp:
                            data = json.load(fp)
                            data["_path"] = folder_path
                            cat = data.get("category", "General")
                            if cat not in categories:
                                categories[cat] = []
                            categories[cat].append(data)
                            self.experiments_cache[data["id"]] = data
                    except Exception as e:
                        print(f"Error loading experiment {folder}: {e}")

        for cat_name, exp_list in categories.items():
            cat_item = QTreeWidgetItem(self.tree, [f"📂 {cat_name}"])
            cat_item.setFont(0, QFont("Arial", 8.5, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor("#38bdf8"))
            cat_item.setExpanded(True)
            
            for exp in exp_list:
                item = QTreeWidgetItem(cat_item, [f"  ⚡ {exp['name']}"])
                item.setData(0, Qt.ItemDataRole.UserRole, exp["id"])

    def on_item_clicked(self, item, column):
        exp_id = item.data(0, Qt.ItemDataRole.UserRole)
        if exp_id and exp_id in self.experiments_cache:
            self.experiment_selected.emit(self.experiments_cache[exp_id])
