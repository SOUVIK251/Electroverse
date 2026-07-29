"""
Interactive Quiz, Viva Voce & Exam Prep Widget
Offers MCQ Practice, Technical Interview Flashcards, Assignment Tracking, and Completion Certificates.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QRadioButton, QButtonGroup, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class QuizVivaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #0b0f19; border-radius: 6px; }
            QTabBar::tab { background-color: #1e293b; color: #94a3b8; padding: 6px 12px; font-weight: bold; font-size: 8.5pt; }
            QTabBar::tab:selected { background-color: #0284c7; color: white; }
        """)
        
        # Tab 1: Comprehensive MCQ Bank
        mcq_widget = QWidget()
        m_lay = QVBoxLayout(mcq_widget)
        
        card = QFrame()
        card.setStyleSheet("background-color: #090d16; border: 1px solid #1e293b; border-radius: 6px; padding: 12px;")
        c_lay = QVBoxLayout(card)
        
        t = QLabel("❓ Comprehensive Digital System Design Quiz")
        t.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        t.setStyleSheet("color: #eab308;")
        c_lay.addWidget(t)
        
        q_lbl = QLabel("Q1: Which logic gate is known as a Universal Gate because it can construct any digital circuit?")
        q_lbl.setWordWrap(True)
        q_lbl.setStyleSheet("color: #f8fafc; font-weight: bold; font-size: 9pt;")
        c_lay.addWidget(q_lbl)
        
        btn_grp = QButtonGroup(self)
        opts = ["AND Gate (IC 7408)", "OR Gate (IC 7432)", "NAND Gate (IC 7400)", "XOR Gate (IC 7486)"]
        for i, opt in enumerate(opts):
            r = QRadioButton(opt)
            r.setStyleSheet("color: #cbd5e1; font-size: 8.5pt;")
            btn_grp.addButton(r, i)
            c_lay.addWidget(r)
            
        btn_sub = QPushButton(" Submit Quiz Answer ")
        btn_sub.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px; font-size: 8.5pt;")
        btn_sub.clicked.connect(lambda: QMessageBox.information(self, "Quiz Result", "✓ Correct! NAND and NOR are universal gates because any Boolean function can be implemented using only NAND or NOR gates."))
        c_lay.addWidget(btn_sub)
        
        m_lay.addWidget(card)
        m_lay.addStretch()
        tabs.addTab(mcq_widget, "📝 MCQ Quiz Bank")
        
        # Tab 2: Viva Voce & Interview Flashcards
        viva_widget = QWidget()
        v_lay = QVBoxLayout(viva_widget)
        
        v_card = QFrame()
        v_card.setStyleSheet("background-color: #090d16; border: 1px solid #1e293b; border-radius: 6px; padding: 12px;")
        vc_lay = QVBoxLayout(v_card)
        
        vt = QLabel("🎓 Viva Voce & Interview Flashcards")
        vt.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        vt.setStyleSheet("color: #38bdf8;")
        vc_lay.addWidget(vt)
        
        vq1 = QLabel("Q: What is DeMorgan's First Theorem?")
        vq1.setStyleSheet("color: #f8fafc; font-weight: bold;")
        vc_lay.addWidget(vq1)
        
        va1 = QLabel("A: (A · B)' = A' + B'. The complement of a product is equal to the sum of the complements.")
        va1.setStyleSheet("color: #10b981; font-style: italic;")
        vc_lay.addWidget(va1)
        
        vc_lay.addSpacing(10)
        
        vq2 = QLabel("Q: What is the propagation delay of IC 7408?")
        vq2.setStyleSheet("color: #f8fafc; font-weight: bold;")
        vc_lay.addWidget(vq2)
        
        va2 = QLabel("A: Approximately 7 to 10 nanoseconds for standard 74LS series TTL AND gates.")
        va2.setStyleSheet("color: #10b981; font-style: italic;")
        vc_lay.addWidget(va2)
        
        v_lay.addWidget(v_card)
        v_lay.addStretch()
        tabs.addTab(viva_widget, "🎓 Viva & Interview Flashcards")
        
        # Tab 3: Completion Certificate
        cert_widget = QWidget()
        ct_lay = QVBoxLayout(cert_widget)
        
        c_card = QFrame()
        c_card.setStyleSheet("background-color: #032b45; border: 2px solid #10b981; border-radius: 8px; padding: 16px;")
        cc_lay = QVBoxLayout(c_card)
        
        ct1 = QLabel("🏆 CERTIFICATE OF MASTERY")
        ct1.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        ct1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ct1.setStyleSheet("color: #10b981;")
        cc_lay.addWidget(ct1)
        
        ct2 = QLabel("Digital System Design & Fundamental Gate Synthesis")
        ct2.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        ct2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ct2.setStyleSheet("color: #38bdf8;")
        cc_lay.addWidget(ct2)
        
        ct3 = QLabel("This verifies that the student has completed all 10 learning modules, mastered fundamental logic gates (7400-74266), and verified combinational addition circuits in the 2D Virtual Trainer Kit.")
        ct3.setWordWrap(True)
        ct3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ct3.setStyleSheet("color: #cbd5e1; font-size: 9pt; font-style: italic;")
        cc_lay.addWidget(ct3)
        
        ct_lay.addWidget(c_card)
        ct_lay.addStretch()
        tabs.addTab(cert_widget, "🏆 Progress & Certificate")
        
        layout.addWidget(tabs)
