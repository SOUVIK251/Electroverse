from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QStackedWidget, QSplitter, QComboBox, QProgressBar, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

from src.core.assessment_engine import AssessmentEngine
from src.core.timer_manager import TimerController
from src.core.scoring_engine import ScoringEngine
from .question_card import QuestionCard
from .question_navigation import QuestionNavigation
from .exam_timer import ExamTimerWidget
from .analytics_dashboard import AnalyticsDashboard
from .answer_review import AnswerReviewWidget
from .certificate_dialog import CertificateDialog

class CBTExamWidget(QWidget):
    """Unified Enterprise CBT Examination Engine Widget for All Hubs.
    
    Supports:
    - Digital System Design Hub
    - Signal & System Hub
    - Analog Electronics Hub
    """

    launch_theory_signal = Signal(str)
    launch_sim_signal = Signal(str)

    def __init__(self, subject_id="digital_system_design", parent=None):
        super().__init__(parent)
        self.subject_id = subject_id
        self.engine = AssessmentEngine(subject_id)
        
        self.current_session = None
        self.current_q_idx = 0
        self.user_answers = {}        # q_id -> answer
        self.visited_set = set()      # set of 0-indexed indices
        self.marked_set = set()       # set of 0-indexed indices
        self.eval_results = None

        self.timer_ctrl = TimerController(1800, self)
        self.timer_ctrl.tick.connect(self._on_timer_tick)
        self.timer_ctrl.time_expired.connect(self._on_timer_expired)

        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(4, 4, 4, 4)
        main_lay.setSpacing(6)

        self.stack = QStackedWidget()

        # View 0: Exam Selection Dashboard Grid (30 Sets)
        self.stack.addWidget(self.create_exam_selector_view())
        # View 1: Live CBT Examination Runner
        self.stack.addWidget(self.create_live_exam_runner_view())
        # View 2: Analytics Dashboard & Results
        self.stack.addWidget(self.create_analytics_view())
        # View 3: Answer Key Reviewer
        self.stack.addWidget(self.create_answer_review_view())

        main_lay.addWidget(self.stack)

    # -------------------------------------------------------------
    # View 0: Exam Selection Dashboard (30 Sets)
    # -------------------------------------------------------------
    def create_exam_selector_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(12)

        # Header bar
        hdr = QFrame()
        hdr.setObjectName("card-panel")
        hdr.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 12px; }")
        h_lay = QHBoxLayout(hdr)

        subj_title = "Digital System Design" if self.subject_id == "digital_system_design" else ("Signals & Systems" if self.subject_id == "signal_and_system" else "Analog Electronics")
        title_lbl = QLabel(f"📝 {subj_title} — Enterprise Examination Portal")
        title_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 13pt;")

        m_lbl = QLabel("Exam Mode:")
        m_lbl.setStyleSheet("color: #94A3B8; font-weight: bold;")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Mixed Mode (10 Easy, 10 Med, 10 Hard)", "Adaptive Mode", "Easy Mode", "Medium Mode", "Hard Mode"])
        self.mode_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; padding: 4px 8px; border-radius: 6px;")

        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        h_lay.addWidget(m_lbl)
        h_lay.addWidget(self.mode_combo)
        l.addWidget(hdr)

        # 30-Set Selection Grid Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        grid_container = QWidget()
        g_lay = QGridLayout(grid_container)
        g_lay.setSpacing(12)

        exam_sets = self.engine.get_exam_sets()
        for idx, s_obj in enumerate(exam_sets):
            set_id = s_obj["set_id"]
            set_title = s_obj["set_title"]

            # Calculate actual question count
            raw_q_count = len(s_obj.get("question_ids", []))
            if raw_q_count == 0:
                raw_q_count = len(self.engine.question_bank)

            card = QFrame()
            card.setObjectName("card-panel")
            card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
            c_lay = QVBoxLayout(card)

            t_lbl = QLabel(f"📄 {set_id}")
            t_lbl.setStyleSheet("color: #F8FAFC; font-weight: bold; font-size: 11pt;")
            
            sub_lbl = QLabel(f"{set_title}\n{raw_q_count} Questions | 30 Mins")
            sub_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt;")
            sub_lbl.setWordWrap(True)

            start_btn = QPushButton("🚀 Start Examination")
            start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                }
            """)
            start_btn.clicked.connect(lambda checked=False, s_id=set_id: self.start_exam_session(s_id))

            c_lay.addWidget(t_lbl)
            c_lay.addWidget(sub_lbl)
            c_lay.addWidget(start_btn)

            g_lay.addWidget(card, idx // 3, idx % 3)

        scroll.setWidget(grid_container)
        l.addWidget(scroll, 1)

        return w

    # -------------------------------------------------------------
    # View 1: Live CBT Examination Runner
    # -------------------------------------------------------------
    def create_live_exam_runner_view(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)
        l.setSpacing(6)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("card-panel")
        top_bar.setFixedHeight(48)
        top_bar.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; }")
        tb_lay = QHBoxLayout(top_bar)
        tb_lay.setContentsMargins(10, 4, 10, 4)

        self.exam_title_lbl = QLabel("CBT Exam Set")
        self.exam_title_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 11pt;")

        self.timer_widget = ExamTimerWidget()

        self.exam_prog = QProgressBar()
        self.exam_prog.setRange(0, 30)
        self.exam_prog.setValue(0)
        self.exam_prog.setFixedWidth(140)
        self.exam_prog.setFixedHeight(12)
        self.exam_prog.setTextVisible(False)
        self.exam_prog.setStyleSheet("QProgressBar { background-color: #0F172A; border: 1px solid #26334D; border-radius: 6px; } QProgressBar::chunk { background-color: #10B981; border-radius: 5px; }")

        tb_lay.addWidget(self.exam_title_lbl)
        tb_lay.addStretch()
        tb_lay.addWidget(self.timer_widget)
        tb_lay.addWidget(self.exam_prog)

        l.addWidget(top_bar)

        # Main Splitter (Left Navigator 250px | Right Question Card)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        self.nav_widget = QuestionNavigation(30)
        self.nav_widget.question_selected.connect(self.goto_question)
        splitter.addWidget(self.nav_widget)

        self.q_card_widget = QuestionCard()
        self.q_card_widget.answer_changed.connect(self.on_answer_changed)
        splitter.addWidget(self.q_card_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([260, 840])

        l.addWidget(splitter, 1)

        # Bottom Bar Buttons
        bot_bar = QFrame()
        bot_bar.setFixedHeight(48)
        bot_bar.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px;")
        bb_lay = QHBoxLayout(bot_bar)
        bb_lay.setContentsMargins(10, 4, 10, 4)

        prev_btn = QPushButton("◄ Previous")
        prev_btn.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
        prev_btn.clicked.connect(self.goto_prev_q)

        next_btn = QPushButton("Next ►")
        next_btn.setStyleSheet("background-color: #2563EB; color: #FFF; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
        next_btn.clicked.connect(self.goto_next_q)

        mark_btn = QPushButton("🏷️ Mark for Review")
        mark_btn.setStyleSheet("background-color: #F59E0B; color: #FFF; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
        mark_btn.clicked.connect(self.toggle_mark_review)

        clear_btn = QPushButton("🗑️ Clear Answer")
        clear_btn.setStyleSheet("background-color: #1E293B; color: #EF4444; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
        clear_btn.clicked.connect(self.clear_current_answer)

        sub_btn = QPushButton("🚀 Submit Exam")
        sub_btn.setStyleSheet("background-color: #10B981; color: #FFF; font-weight: bold; padding: 6px 18px; border-radius: 6px;")
        sub_btn.clicked.connect(self.submit_exam)

        bb_lay.addWidget(prev_btn)
        bb_lay.addWidget(next_btn)
        bb_lay.addWidget(mark_btn)
        bb_lay.addWidget(clear_btn)
        bb_lay.addStretch()
        bb_lay.addWidget(sub_btn)

        l.addWidget(bot_bar)

        return w

    # -------------------------------------------------------------
    # View 2 & 3: Analytics & Answer Review
    # -------------------------------------------------------------
    def create_analytics_view(self):
        self.analytics_dash = AnalyticsDashboard()
        self.analytics_dash.claim_certificate_clicked.connect(self.show_certificate_dialog)
        self.analytics_dash.review_answers_clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.analytics_dash.retry_exam_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        return self.analytics_dash

    def create_answer_review_view(self):
        self.answer_review_widget = AnswerReviewWidget()
        self.answer_review_widget.back_to_results_clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.answer_review_widget.launch_theory_clicked.connect(self.launch_theory_signal.emit)
        self.answer_review_widget.launch_sim_clicked.connect(self.launch_sim_signal.emit)
        return self.answer_review_widget

    # -------------------------------------------------------------
    # Session Handlers
    # -------------------------------------------------------------
    def start_exam_session(self, set_id):
        mode_text = self.mode_combo.currentText().split()[0]
        self.current_session = self.engine.prepare_exam_session(set_id, mode=mode_text)
        self.current_q_idx = 0
        self.user_answers.clear()
        self.visited_set.clear()
        self.marked_set.clear()

        total_questions = len(self.current_session["questions"])

        self.exam_title_lbl.setText(f"{self.current_session['set_title']} [{mode_text} Mode]")
        self.exam_prog.setRange(0, max(1, total_questions))
        self.nav_widget.set_total_questions(total_questions)

        # Reset timer
        duration_sec = self.current_session["duration_sec"]
        self.timer_ctrl.reset(duration_sec)
        self.timer_ctrl.start()

        # Reset grid navigator
        for i in range(total_questions):
            self.nav_widget.update_status(i, "NOT_VISITED", i == 0)

        self.goto_question(0)
        self.stack.setCurrentIndex(1)

    def goto_question(self, idx):
        if not self.current_session or idx < 0 or idx >= len(self.current_session["questions"]):
            return

        self.current_q_idx = idx
        self.visited_set.add(idx)

        q_data = self.current_session["questions"][idx]
        q_id = q_data["question_id"]
        curr_ans = self.user_answers.get(q_id, None)

        self.q_card_widget.display_question(q_data, idx + 1, len(self.current_session["questions"]), curr_ans)

        # Update Grid Status
        self.refresh_nav_grid()

    def refresh_nav_grid(self):
        for i in range(len(self.current_session["questions"])):
            q_id = self.current_session["questions"][i]["question_id"]
            has_ans = (q_id in self.user_answers and self.user_answers[q_id] not in [None, [], ""])

            if i in self.marked_set:
                st = "MARKED"
            elif has_ans:
                st = "ANSWERED"
            elif i in self.visited_set:
                st = "VISITED"
            else:
                st = "NOT_VISITED"

            self.nav_widget.update_status(i, st, i == self.current_q_idx)

        ans_count = len([q for q in self.current_session["questions"] if q["question_id"] in self.user_answers and self.user_answers[q["question_id"]] not in [None, [], ""]])
        self.exam_prog.setValue(ans_count)

    def on_answer_changed(self, ans):
        if self.current_session and 0 <= self.current_q_idx < len(self.current_session["questions"]):
            q_id = self.current_session["questions"][self.current_q_idx]["question_id"]
            if ans:
                self.user_answers[q_id] = ans
            else:
                self.user_answers.pop(q_id, None)
            self.refresh_nav_grid()

    def toggle_mark_review(self):
        if self.current_q_idx in self.marked_set:
            self.marked_set.remove(self.current_q_idx)
        else:
            self.marked_set.add(self.current_q_idx)
        self.refresh_nav_grid()

    def clear_current_answer(self):
        self.q_card_widget.clear_selection()

    def goto_prev_q(self):
        if self.current_q_idx > 0:
            self.goto_question(self.current_q_idx - 1)

    def goto_next_q(self):
        if self.current_session and self.current_q_idx < len(self.current_session["questions"]) - 1:
            self.goto_question(self.current_q_idx + 1)

    def _on_timer_tick(self, rem_sec):
        self.timer_widget.update_time(rem_sec)

    def _on_timer_expired(self):
        self.submit_exam()

    def submit_exam(self):
        self.timer_ctrl.stop()

        time_taken = self.current_session["duration_sec"] - self.timer_ctrl.remaining_sec
        scorer = ScoringEngine(correct_marks=1.0, negative_marks=0.25, enable_negative=True, pass_pct=60.0)
        
        self.eval_results = scorer.evaluate_exam(
            self.current_session["questions"],
            self.user_answers,
            time_taken_sec=time_taken
        )

        subj_title = "Digital System Design" if self.subject_id == "digital_system_design" else ("Signals & Systems" if self.subject_id == "signal_and_system" else "Analog Electronics")

        self.analytics_dash.display_results(self.eval_results, subject_title=subj_title)
        self.answer_review_widget.load_review_data(self.eval_results["detailed_eval"])

        self.stack.setCurrentIndex(2)

    def show_certificate_dialog(self):
        if self.eval_results:
            dlg = CertificateDialog(
                student_name="Souvik Kundu",
                subject_title=self.subject_id.replace("_", " ").title(),
                score_pct=self.eval_results["percentage"],
                grade=self.eval_results["grade"],
                parent=self
            )
            dlg.exec()
