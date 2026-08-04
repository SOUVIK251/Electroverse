from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

class NetworkDashboardView(QWidget):
    """Learning Dashboard Landing Screen for Network Theory Hub."""

    tab_jump_requested = Signal(int) # index of target tab (1=Learn, 2=ProblemSolving, 3=Sim, 4=Assessment, 5=Ref)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(15)

        # 1. Header Banner
        hdr_card = QFrame()
        hdr_card.setObjectName("card-panel")
        hdr_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 4px solid #06B6D4; border-radius: 10px; padding: 18px; }")
        h_lay = QVBoxLayout(hdr_card)

        t_lbl = QLabel("⚡ Network Theory Virtual Engineering Laboratory Suite")
        t_lbl.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FFFFFF;")
        
        sub_lbl = QLabel("Welcome back, Engineer! Track your progress, continue interactive simulations, and master network analysis.")
        sub_lbl.setStyleSheet("color: #CBD5E1; font-size: 10pt;")
        
        h_lay.addWidget(t_lbl)
        h_lay.addWidget(sub_lbl)
        lay.addWidget(hdr_card)

        # 2. Metric Cards Row
        metrics_row = QHBoxLayout()
        
        def make_metric(icon_str, title, val_str, sub_text, color):
            card = QFrame()
            card.setStyleSheet(f"background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid {color}; border-radius: 8px; padding: 12px;")
            c_lay = QVBoxLayout(card)
            
            top_row = QHBoxLayout()
            ic = QLabel()
            ic.setPixmap(qta.icon(icon_str, color=color).pixmap(18, 18))
            tl = QLabel(title)
            tl.setStyleSheet("color: #94A3B8; font-size: 8.5pt; font-weight: bold;")
            top_row.addWidget(ic)
            top_row.addWidget(tl)
            top_row.addStretch()
            
            vl = QLabel(val_str)
            vl.setStyleSheet(f"color: #FFFFFF; font-size: 16pt; font-weight: bold; padding: 4px 0px;")
            
            st = QLabel(sub_text)
            st.setStyleSheet("color: #64748B; font-size: 8pt;")

            c_lay.addLayout(top_row)
            c_lay.addWidget(vl)
            c_lay.addWidget(st)
            return card

        metrics_row.addWidget(make_metric("fa5s.book-reader", "MODULES COMPLETED", "18 / 42", "42% Curriculum Finished", "#06B6D4"))
        metrics_row.addWidget(make_metric("fa5s.chart-line", "OVERALL PROGRESS", "48%", "On Track for Mastery", "#10B981"))
        metrics_row.addWidget(make_metric("fa5s.flask", "SIMULATIONS FINISHED", "15 Labs", "Phases 1-4 Complete", "#F59E0B"))
        metrics_row.addWidget(make_metric("fa5s.clipboard-check", "ASSESSMENT AVERAGE", "84%", "Grade: A (Passed)", "#38BDF8"))
        metrics_row.addWidget(make_metric("fa5s.award", "CERTIFICATES", "2 Earned", "Verified Seals", "#EC4899"))

        lay.addLayout(metrics_row)

        # 3. Quick Jumps & Continue Cards
        jump_card = QFrame()
        jump_card.setObjectName("card-panel")
        jump_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
        j_lay = QVBoxLayout(jump_card)

        j_hdr = QLabel("🚀 Continue Learning & Active Sessions")
        j_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 12pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
        j_lay.addWidget(j_hdr)

        btn_row = QHBoxLayout()
        
        btn1 = QPushButton("📖 Continue Theory: Thevenin's Theorem")
        btn1.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 10px 14px; border-radius: 6px; text-align: left;")
        btn1.setIcon(qta.icon("fa5s.book-open", color="#06B6D4"))
        btn1.clicked.connect(lambda: self.tab_jump_requested.emit(1))

        btn2 = QPushButton("🧪 Continue Simulation: Maximum Power Transfer")
        btn2.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 10px 14px; border-radius: 6px; text-align: left;")
        btn2.setIcon(qta.icon("fa5s.flask", color="#F59E0B"))
        btn2.clicked.connect(lambda: self.tab_jump_requested.emit(3))

        btn3 = QPushButton("📝 Continue CBT Assessment: Exam Set 5")
        btn3.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 10px 14px; border-radius: 6px; text-align: left;")
        btn3.setIcon(qta.icon("fa5s.file-signature", color="#10B981"))
        btn3.clicked.connect(lambda: self.tab_jump_requested.emit(4))

        btn_row.addWidget(btn1)
        btn_row.addWidget(btn2)
        btn_row.addWidget(btn3)
        j_lay.addLayout(btn_row)

        lay.addWidget(jump_card)

        # 4. Recent Activity Log
        act_card = QFrame()
        act_card.setObjectName("card-panel")
        act_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
        a_lay = QVBoxLayout(act_card)

        a_hdr = QLabel("🕒 Recent Session Activity Log")
        a_hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11.5pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
        a_lay.addWidget(a_hdr)

        activities = [
            ("• Solved Mesh Analysis Numerical Problem (4 Loops)", "Today at 20:45", "#10B981"),
            ("• Completed Ohm's Law & Power Virtual Lab Experiment", "Yesterday at 18:20", "#06B6D4"),
            ("• Passed KCL & KVL Diagnostic Quiz (Score 90%)", "2 days ago", "#38BDF8"),
            ("• Generated Thevenin Equivalent Circuit Simulation", "3 days ago", "#F59E0B")
        ]

        for act_str, time_str, clr in activities:
            r = QHBoxLayout()
            al = QLabel(act_str)
            al.setStyleSheet(f"color: {clr}; font-size: 9.5pt; font-weight: 600;")
            tl = QLabel(time_str)
            tl.setStyleSheet("color: #64748B; font-size: 8.5pt;")
            r.addWidget(al)
            r.addStretch()
            r.addWidget(tl)
            a_lay.addLayout(r)

        lay.addWidget(act_card)

        scroll.setWidget(container)
        main_lay.addWidget(scroll)
