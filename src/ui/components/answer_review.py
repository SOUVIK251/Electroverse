from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal

class AnswerReviewWidget(QWidget):
    """Question Answer Key Reviewer with Explanations & Theory/Simulation Links."""

    launch_theory_clicked = Signal(str)      # Emits topic reference
    launch_sim_clicked = Signal(str)         # Emits simulation link
    back_to_results_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        # Header bar
        hdr_card = QFrame()
        hdr_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px;")
        h_lay = QHBoxLayout(hdr_card)

        title = QLabel("📖 Examination Answer Key & Explanations Review")
        title.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 12pt;")
        
        back_btn = QPushButton("◄ Back to Analytics")
        back_btn.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
        back_btn.clicked.connect(self.back_to_results_clicked.emit)

        h_lay.addWidget(title)
        h_lay.addStretch()
        h_lay.addWidget(back_btn)

        main_lay.addWidget(hdr_card)

        # Scrollable Questions Review List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.container = QWidget()
        self.lay = QVBoxLayout(self.container)
        self.lay.setSpacing(12)

        scroll.setWidget(self.container)
        main_lay.addWidget(scroll, 1)

    def load_review_data(self, detailed_eval):
        while self.lay.count():
            item = self.lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, item in enumerate(detailed_eval):
            status = item["status"]
            b_color = "#10B981" if status == "CORRECT" else ("#EF4444" if status == "WRONG" else "#64748B")
            
            card = QFrame()
            card.setObjectName("card-panel")
            card.setStyleSheet(f"QFrame#card-panel {{ background-color: #141B2D; border: 1px solid #26334D; border-left: 4px solid {b_color}; border-radius: 8px; padding: 12px; }}")
            c_lay = QVBoxLayout(card)

            top_row = QHBoxLayout()
            q_num = QLabel(f"Q{idx + 1}. [{item['module']}] {item['question']}")
            q_num.setStyleSheet("color: #F8FAFC; font-weight: bold; font-size: 10.5pt;")
            q_num.setWordWrap(True)

            st_lbl = QLabel(status)
            st_lbl.setStyleSheet(f"background-color: {b_color}; color: #FFF; font-weight: bold; font-size: 8pt; padding: 2px 8px; border-radius: 4px;")

            top_row.addWidget(q_num, 1)
            top_row.addWidget(st_lbl)
            c_lay.addLayout(top_row)

            # Answers comparison
            ans_lbl = QLabel(f"Your Answer: {item['user_answer']}   |   Correct Answer: {item['correct_answer']}")
            ans_lbl.setStyleSheet("color: #CBD5E1; font-size: 9.5pt; font-weight: 600; padding-top: 4px;")
            c_lay.addWidget(ans_lbl)

            # Explanation
            exp_lbl = QLabel(f"💡 Explanation: {item['explanation']}")
            exp_lbl.setStyleSheet("color: #34D399; font-size: 9.5pt; background-color: #09121E; padding: 8px; border-radius: 6px; margin-top: 4px;")
            exp_lbl.setWordWrap(True)
            c_lay.addWidget(exp_lbl)

            # Action links
            act_row = QHBoxLayout()
            if item.get("reference_topic"):
                t_btn = QPushButton("📖 Launch Theory Lesson")
                t_btn.setStyleSheet("background-color: #1E293B; color: #38BDF8; border: 1px solid #26334D; font-size: 8.5pt; padding: 4px 10px; border-radius: 4px;")
                t_btn.clicked.connect(lambda checked=False, ref=item["reference_topic"]: self.launch_theory_clicked.emit(ref))
                act_row.addWidget(t_btn)

            if item.get("simulation_link"):
                s_btn = QPushButton("🧪 Launch Interactive Simulation")
                s_btn.setStyleSheet("background-color: #1E293B; color: #06B6D4; border: 1px solid #26334D; font-size: 8.5pt; padding: 4px 10px; border-radius: 4px;")
                s_btn.clicked.connect(lambda checked=False, sim=item["simulation_link"]: self.launch_sim_clicked.emit(sim))
                act_row.addWidget(s_btn)

            act_row.addStretch()
            c_lay.addLayout(act_row)

            self.lay.addWidget(card)
