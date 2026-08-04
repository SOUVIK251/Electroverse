from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, Signal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from src.core.analytics_engine import AnalyticsEngine

class AnalyticsDashboard(QWidget):
    """Result & Detailed Analytics Dashboard."""

    claim_certificate_clicked = Signal()
    review_answers_clicked = Signal()
    retry_exam_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.container = QWidget()
        self.lay = QVBoxLayout(self.container)
        self.lay.setSpacing(15)

        scroll.setWidget(self.container)
        main_lay.addWidget(scroll)

    def display_results(self, eval_res, subject_title="Engineering Assessment"):
        while self.lay.count():
            item = self.lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Top Banner Card (Pass/Fail)
        is_pass = eval_res.get("is_passed", False)
        score_pct = eval_res.get("percentage", 0.0)
        grade = eval_res.get("grade", "F")
        raw_score = eval_res.get("raw_score", 0.0)
        max_score = eval_res.get("max_score", 30.0)

        banner = QFrame()
        b_bg = "#064E3B" if is_pass else "#450A0A"
        b_border = "#10B981" if is_pass else "#EF4444"
        banner.setStyleSheet(f"background-color: {b_bg}; border: 2px solid {b_border}; border-radius: 10px; padding: 20px;")
        b_lay = QHBoxLayout(banner)

        b_info = QVBoxLayout()
        st_title = QLabel("🎉 EXAMINATION PASSED!" if is_pass else "⚠️ EXAMINATION NOT PASSED")
        st_title.setStyleSheet(f"color: {'#34D399' if is_pass else '#FCA5A5'}; font-size: 16pt; font-weight: bold;")
        
        st_sub = QLabel(f"Subject: {subject_title}  |  Grade: {grade}  |  Score: {raw_score:.1f} / {max_score:.1f} ({score_pct:.1f}%)")
        st_sub.setStyleSheet("color: #FFFFFF; font-size: 11pt;")
        b_info.addWidget(st_title)
        b_info.addWidget(st_sub)

        b_lay.addLayout(b_info, 1)

        if score_pct >= 80.0:
            cert_btn = QPushButton("🎓 Claim Certificate")
            cert_btn.setStyleSheet("background-color: #F59E0B; color: #FFF; font-weight: bold; font-size: 10.5pt; padding: 10px 16px; border-radius: 8px;")
            cert_btn.clicked.connect(self.claim_certificate_clicked.emit)
            b_lay.addWidget(cert_btn)

        self.lay.addWidget(banner)

        # 2. Action Buttons Row
        act_row = QHBoxLayout()
        rev_btn = QPushButton("📖 Review Answers & Explanations")
        rev_btn.setStyleSheet("background-color: #2563EB; color: #FFF; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        rev_btn.clicked.connect(self.review_answers_clicked.emit)

        retry_btn = QPushButton("🔄 Retry Exam")
        retry_btn.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        retry_btn.clicked.connect(self.retry_exam_clicked.emit)

        act_row.addWidget(rev_btn)
        act_row.addWidget(retry_btn)
        act_row.addStretch()
        self.lay.addLayout(act_row)

        # 3. Matplotlib Charts Row
        charts_row = QHBoxLayout()
        
        pie_fig = AnalyticsEngine.create_score_pie_chart(
            eval_res.get("correct_count", 0),
            eval_res.get("wrong_count", 0),
            eval_res.get("skipped_count", 0)
        )
        pie_canvas = FigureCanvas(pie_fig)

        bar_fig = AnalyticsEngine.create_topic_bar_chart(eval_res.get("topic_analysis", {}))
        bar_canvas = FigureCanvas(bar_fig)

        charts_row.addWidget(pie_canvas, 1)
        charts_row.addWidget(bar_canvas, 2)
        self.lay.addLayout(charts_row)

        # 4. Learning Recommendations (If weak topics exist)
        weak = eval_res.get("weak_topics", [])
        if weak:
            recs, total_min = AnalyticsEngine.calculate_recovery_plan(weak)
            
            rec_card = QFrame()
            rec_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px;")
            r_lay = QVBoxLayout(rec_card)

            r_hdr = QLabel(f"🧠 Personalized Learning Recommendations (Est. Recovery Time: {total_min} mins)")
            r_hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
            r_lay.addWidget(r_hdr)

            for item in recs:
                lbl = QLabel(f"• **{item['module']}** (Accuracy: {item['accuracy']}%): {item['theory_lesson']} | {item['simulation']} (~{item['estimated_time_min']} mins)")
                lbl.setStyleSheet("color: #E2E8F0; font-size: 9.5pt; padding: 3px 0px;")
                lbl.setWordWrap(True)
                r_lay.addWidget(lbl)

            self.lay.addWidget(rec_card)
