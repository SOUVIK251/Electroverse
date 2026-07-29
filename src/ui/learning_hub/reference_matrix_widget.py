"""
IC Pinout Matrix, Formula Cheat Sheet & Reference Viewer Widget
Includes Memorization Tricks & Shortcuts for Digital Electronics Formulas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class ReferenceMatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #0b0f19; border-radius: 6px; }
            QTabBar::tab { background-color: #1e293b; color: #94a3b8; padding: 8px 16px; font-weight: bold; font-size: 9pt; }
            QTabBar::tab:selected { background-color: #0284c7; color: white; }
        """)
        
        # Tab 1: Approved Gate IC Reference Matrix
        ic_widget = QWidget()
        i_lay = QVBoxLayout(ic_widget)
        
        title = QLabel("📚 Approved TTL Fundamental Gate IC Reference Matrix")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8;")
        i_lay.addWidget(title)
        
        table = QTableWidget()
        headers = ["IC Part #", "Logic Type", "Gate Count", "VCC Pin", "GND Pin", "Package Pinout Key"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        ic_rows = [
            ["IC 7400", "Quad 2-Input NAND", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2 -> Output 3"],
            ["IC 7402", "Quad 2-Input NOR", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Output 1 <- Inputs: 2,3 (Reversed!)"],
            ["IC 7404", "Hex Inverter (NOT)", "6 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Input 1 -> Output 2"],
            ["IC 7408", "Quad 2-Input AND", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2 -> Output 3"],
            ["IC 7411", "Triple 3-Input AND", "3 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2,13 -> Output 12"],
            ["IC 7432", "Quad 2-Input OR", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2 -> Output 3"],
            ["IC 7486", "Quad 2-Input XOR", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2 -> Output 3"],
            ["IC 74266", "Quad 2-Input XNOR", "4 Gates", "Pin 14 (+5V)", "Pin 7 (0V)", "Inputs: 1,2 -> Output 3 (Open Coll)"]
        ]
        
        table.setRowCount(len(ic_rows))
        table.setStyleSheet("""
            QTableWidget { background-color: #090d16; color: #f8fafc; gridline-color: #1e293b; border: 1px solid #1e293b; border-radius: 4px; font-size: 8.5pt; }
            QHeaderView::section { background-color: #1e293b; color: #38bdf8; font-weight: bold; padding: 4px; font-size: 8.5pt; }
        """)
        
        for r_idx, row in enumerate(ic_rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c_idx == 0:
                    item.setForeground(QColor("#38bdf8"))
                    item.setFont(QFont("Arial", 8.5, QFont.Weight.Bold))
                table.setItem(r_idx, c_idx, item)
                
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        i_lay.addWidget(table)
        tabs.addTab(ic_widget, "📊 IC Pinout Matrix")
        
        # Tab 2: Easy Formula Memorization Shortcuts
        memo_widget = QWidget()
        m_lay = QVBoxLayout(memo_widget)
        
        scroll_m = QScrollArea()
        scroll_m.setWidgetResizable(True)
        scroll_m.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        m_container = QWidget()
        mc_lay = QVBoxLayout(m_container)
        mc_lay.setContentsMargins(10, 10, 10, 10)
        mc_lay.setSpacing(12)
        
        # Section 1: DeMorgan's Rule
        f_card1 = QFrame()
        f_card1.setStyleSheet("background-color: #090d16; border: 1px solid #0284c7; border-radius: 6px; padding: 12px;")
        fc1 = QVBoxLayout(f_card1)
        
        lbl1 = QLabel("🧠 DeMorgan's Rule: 'Break the Bar, Change the Sign!'")
        lbl1.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl1.setStyleSheet("color: #eab308;")
        fc1.addWidget(lbl1)
        
        eq1 = QLabel("1)  (A · B)'  =  A' + B'\n2)  (A + B)'  =  A' · B'")
        eq1.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        eq1.setStyleSheet("color: #38bdf8; padding: 6px; background: #0b1329; border-radius: 4px;")
        fc1.addWidget(eq1)
        
        t1 = QLabel("💡 Memory Trick: Split the top overline bar into two smaller bars, and flip multiplication (·) into addition (+), or vice versa!")
        t1.setWordWrap(True)
        t1.setStyleSheet("color: #cbd5e1; font-size: 9pt; font-style: italic;")
        fc1.addWidget(t1)
        
        mc_lay.addWidget(f_card1)
        
        # Section 2: Gate Logic Memorization
        f_card2 = QFrame()
        f_card2.setStyleSheet("background-color: #090d16; border: 1px solid #10b981; border-radius: 6px; padding: 12px;")
        fc2 = QVBoxLayout(f_card2)
        
        lbl2 = QLabel("🧠 Fundamental Gate Output Rules (How to Remember Instantly)")
        lbl2.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl2.setStyleSheet("color: #10b981;")
        fc2.addWidget(lbl2)
        
        gate_rules = [
            ("AND Gate (Y = A · B)", "AND is ALL", "Output is 1 ONLY when ALL inputs are 1."),
            ("OR Gate (Y = A + B)", "OR is ANY", "Output is 1 if ANY input is 1."),
            ("NOT Gate (Y = A')", "NOT is OPPOSITE", "Flips 0 to 1, and 1 to 0."),
            ("NAND Gate (Y = (A · B)')", "NAND is NOT-AND", "Give AND output, then FLIP it! Output is 0 ONLY when ALL inputs are 1."),
            ("NOR Gate (Y = (A + B)')", "NOR is NOT-OR", "Give OR output, then FLIP it! Output is 1 ONLY when ALL inputs are 0."),
            ("XOR Gate (Y = A ⊕ B)", "XOR is DIFFERENT", "Output is 1 ONLY when inputs are DIFFERENT (01 or 10)."),
            ("XNOR Gate (Y = A ⊙ B)", "XNOR is EQUAL", "Output is 1 ONLY when inputs are EQUAL (00 or 11).")
        ]
        
        for g_title, g_rule, g_desc in gate_rules:
            box = QFrame()
            box.setStyleSheet("background-color: #0b1329; border: 1px solid #1e293b; border-radius: 4px; padding: 6px;")
            b_lay = QHBoxLayout(box)
            
            t = QLabel(f"⚡ {g_title}")
            t.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            t.setStyleSheet("color: #f8fafc;")
            b_lay.addWidget(t, 1)
            
            r = QLabel(f"★ {g_rule}")
            r.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            r.setStyleSheet("color: #eab308; padding: 2px 6px; background: #1e293b; border-radius: 3px;")
            b_lay.addWidget(r)
            
            d = QLabel(g_desc)
            d.setStyleSheet("color: #94a3b8; font-size: 8.5pt;")
            b_lay.addWidget(d, 2)
            
            fc2.addWidget(box)
            
        mc_lay.addWidget(f_card2)
        
        # Section 3: Adders & MUX Tricks
        f_card3 = QFrame()
        f_card3.setStyleSheet("background-color: #090d16; border: 1px solid #a855f7; border-radius: 6px; padding: 12px;")
        fc3 = QVBoxLayout(f_card3)
        
        lbl3 = QLabel("🧠 Adder & MUX Memory Tricks")
        lbl3.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl3.setStyleSheet("color: #a855f7;")
        fc3.addWidget(lbl3)
        
        tricks = [
            "Half Adder Sum = A ⊕ B  (Sum is XOR: Different inputs = 1)",
            "Half Adder Carry = A · B  (Carry is AND: Both inputs = 1)",
            "Full Adder Sum = A ⊕ B ⊕ Cin  (Odd number of 1s = 1)",
            "Full Adder Cout = AB + Cin(A ⊕ B)  (Two or more 1s = 1)",
            "2:1 MUX Y = S'·I0 + S·I1  (Select S=0 picks I0, S=1 picks I1)",
            "N NAND gates for XOR = 4 NAND gates",
            "N NAND gates for Half Adder = 5 NAND gates"
        ]
        
        for tr in tricks:
            lbl = QLabel(f"• {tr}")
            lbl.setStyleSheet("color: #f8fafc; font-size: 9pt;")
            fc3.addWidget(lbl)
            
        mc_lay.addWidget(f_card3)
        
        scroll_m.setWidget(m_container)
        m_lay.addWidget(scroll_m)
        tabs.addTab(memo_widget, "🧠 Formula Memory Shortcuts")
        
        layout.addWidget(tabs)
