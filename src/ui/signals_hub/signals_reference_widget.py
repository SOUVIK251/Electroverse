import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QScrollArea, QLineEdit
)
from PySide6.QtCore import Qt
import qtawesome as qta

class SignalsReferenceWidget(QWidget):
    """Reference & Formula Matrix for Signals & Systems.
    
    Includes:
    - Fourier, Laplace, and Z-Transform Lookup Tables
    - Signal Classification & System Properties Cheat Sheets
    - Key Integral & Differential Formula Matrix
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_dir = os.path.join("src", "data", "signals")
        self.ref_data = self.load_json("reference_tables.json")
        self.formula_data = self.load_json("formula_sheet.json")
        self.init_ui()

    def load_json(self, rel_path):
        p = os.path.join(self.data_dir, rel_path)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(8)

        # Ref Sub-Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #26334D; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab { background-color: #141B2D; color: #94A3B8; padding: 8px 16px; font-weight: bold; font-size: 9pt; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background-color: #06B6D4; color: #FFFFFF; }
        """)

        self.tabs.addTab(self.create_transform_table_view("fourier_transform_table", ["Time Signal x(t)", "Fourier Transform X(w)", "ROC / Frequency Notes"]), "⚡ Fourier Transform Table")
        self.tabs.addTab(self.create_transform_table_view("laplace_transform_table", ["Time Signal x(t)", "Laplace Transform X(s)", "Region of Convergence (ROC)"]), "📐 Laplace Transform Table")
        self.tabs.addTab(self.create_transform_table_view("z_transform_table", ["Discrete Signal x[n]", "Z-Transform X(z)", "Region of Convergence (ROC)"]), "♾️ Z-Transform Table")
        self.tabs.addTab(self.create_formula_sheet_view(), "📋 Formula Cheat Sheet")

        main_layout.addWidget(self.tabs)

    def create_transform_table_view(self, key, headers):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        rows = self.ref_data.get(key, [])
        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #141B2D;
                gridline-color: #26334D;
                color: #F8FAFC;
                border: 1px solid #26334D;
                border-radius: 6px;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #06B6D4;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #26334D;
            }
        """)

        for r, row in enumerate(rows):
            vals = list(row.values())
            for c, val in enumerate(vals[:len(headers)]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(r, c, item)

        layout.addWidget(table)
        return widget

    def create_formula_sheet_view(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        categories = self.formula_data.get("categories", [])
        for cat in categories:
            card = QFrame()
            card.setObjectName("card-panel")
            card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
            c_lay = QVBoxLayout(card)

            hdr = QLabel(cat.get("name", "Formulas"))
            hdr.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06B6D4; padding-bottom: 6px; border-bottom: 1px solid #26334D;")
            c_lay.addWidget(hdr)

            for item in cat.get("formulas", []):
                row = QHBoxLayout()
                lbl1 = QLabel(item.get("name", ""))
                lbl1.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 10pt;")
                lbl2 = QLabel(item.get("formula", ""))
                lbl2.setStyleSheet("color: #F8FAFC; font-weight: bold; font-family: Consolas, monospace; font-size: 10.5pt;")
                row.addWidget(lbl1, 1)
                row.addWidget(lbl2, 2)
                c_lay.addLayout(row)

            layout.addWidget(card)

        scroll.setWidget(container)
        return scroll
