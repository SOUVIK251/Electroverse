"""
ElectroVerse Microprocessor & Microcontroller Master Assessment View.
Fixes Question Rendering, Data Validation, Matching Interfaces, and Question Session Counts.
"""

import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QGridLayout, QScrollArea, QProgressBar, QRadioButton, QButtonGroup,
    QCheckBox, QComboBox, QLineEdit, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from src.core.logger import log
from src.core.assessment_quality_engine import AssessmentQualityEngine
from src.data.mpmc.assessment_bank import ASSESSMENT_QUESTIONS, ASSESSMENT_MODES


def validate_and_normalize_question(q):
    """
    Validates and normalizes question data structures.
    Returns (is_valid, normalized_q, error_message).
    """
    q_id = q.get("id", "UNKNOWN_ID")
    q_type = str(q.get("type", "")).lower()
    
    if not q.get("question"):
        return False, q, f"Missing 'question' text field in Question {q_id}"
    
    normalized = dict(q)
    
    # --- Matching Question Validation ---
    if q_type in ["matching", "match", "match_the_following"]:
        normalized["type"] = "matching"
        left = q.get("left", [])
        right = q.get("right", [])
        correct_matches = q.get("correct_matches", {})

        # Handle backward compatibility if 'pairs' format was used
        if (not left or not right) and q.get("pairs"):
            pairs = q["pairs"]
            left = [p.get("left", "") for p in pairs]
            right = [p.get("right", "") for p in pairs]
            correct_matches = {p.get("left", ""): p.get("right", "") for p in pairs}
            normalized["left"] = left
            normalized["right"] = right
            normalized["correct_matches"] = correct_matches

        if not left or not right or not correct_matches:
            return False, normalized, f"Matching question {q_id} missing 'left', 'right', or 'correct_matches'"

        return True, normalized, ""

    # --- Fill in the Blank Validation ---
    if q_type in ["fill_blank", "fill_in_the_blank", "numeric"]:
        normalized["type"] = "fill_blank"
        if q.get("correct_answer") is None:
            return False, normalized, f"Fill-in-blank question {q_id} missing 'correct_answer'"
        return True, normalized, ""

    # --- Multi-Select Validation ---
    if q_type == "multi_select":
        if not q.get("options") or not q.get("correct_answers"):
            return False, normalized, f"Multi-select question {q_id} missing 'options' or 'correct_answers'"
        return True, normalized, ""

    # --- Ordering Validation ---
    if q_type in ["ordering", "rearrangement", "sequence"]:
        normalized["type"] = "ordering"
        if not q.get("options") or not q.get("correct_sequence"):
            return False, normalized, f"Ordering question {q_id} missing 'options' or 'correct_sequence'"
        return True, normalized, ""

    # --- Standard MCQ / Register / Machine Code Validation ---
    options = q.get("options", [])
    if not options or q.get("correct_answer") is None:
        return False, normalized, f"Question {q_id} ({q_type}) missing 'options' or 'correct_answer'"

    return True, normalized, ""


class MPMCAssessmentView(QWidget):
    """Master MP&MC Assessment System View."""

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view

        # Assessment State
        self.selected_mode = "quick"
        self.selected_difficulty = "ALL"
        self.active_questions = []
        self.current_q_index = 0
        self.user_answers = {}         # q_id -> user answer
        self.submitted_questions = set()# q_ids submitted
        self.timer_seconds = 0
        self.elapsed_seconds = 0
        self.test_completed = False

        # QTimer for test duration
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_timer_tick)

        log.info("Initializing MPMCAssessmentView master testing platform")
        self.init_ui()
        self.show_home_page()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(6)

        self.content_container = QWidget()
        self.container_layout = QVBoxLayout(self.content_container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_container)

    def clear_container(self):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ==========================================================================
    # 1. ASSESSMENT HOME PAGE
    # ==========================================================================

    def show_home_page(self):
        self.clear_container()
        self.timer.stop()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }
            QScrollBar:vertical { border: none; background: #0F172A; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #F97316; }
        """)

        home_card = QFrame()
        home_card.setStyleSheet("QFrame { background-color: #0B1020; }")
        h_lay = QVBoxLayout(home_card)
        h_lay.setContentsMargins(20, 20, 20, 20)
        h_lay.setSpacing(16)

        # Header Title Card
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 18px;")
        hf_lay = QVBoxLayout(hdr_frame)
        
        t_lbl = QLabel("⚡ MP&MC ASSESSMENT WORKSTATION")
        t_lbl.setStyleSheet("font-size: 16pt; font-weight: 800; color: #F97316; font-family: 'Consolas', 'Segoe UI';")
        hf_lay.addWidget(t_lbl)

        sub_lbl = QLabel("Test your conceptual understanding of Microprocessors, 8085/8051 Architectures, Opcodes, Registers, Timers & Interfacing.")
        sub_lbl.setStyleSheet("font-size: 9.5pt; color: #94A3B8; margin-top: 4px;")
        hf_lay.addWidget(sub_lbl)

        # Difficulty Selection Segmented Control
        diff_box = QHBoxLayout()
        diff_box.setSpacing(8)
        diff_lbl = QLabel("Select Difficulty Level:")
        diff_lbl.setStyleSheet("font-size: 9pt; font-weight: bold; color: #F8FAFC;")
        diff_box.addWidget(diff_lbl)

        self.btn_diff_group = QButtonGroup(hdr_frame)
        difficulties = [("ALL", "All Levels"), ("EASY", "Easy"), ("MEDIUM", "Medium"), ("HARD", "Hard"), ("EXPERT", "Expert")]
        
        for idx, (d_val, d_label) in enumerate(difficulties):
            btn_d = QPushButton(d_label)
            btn_d.setCheckable(True)
            btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_d.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B; color: #94A3B8; border: 1px solid #334155;
                    border-radius: 4px; padding: 4px 12px; font-weight: bold; font-size: 8.5pt;
                }
                QPushButton:checked {
                    background-color: #F97316; color: #FFFFFF; border-color: #F97316;
                }
            """)
            if d_val == self.selected_difficulty:
                btn_d.setChecked(True)
            
            def make_diff_setter(val):
                return lambda: setattr(self, 'selected_difficulty', val)

            btn_d.clicked.connect(make_diff_setter(d_val))
            self.btn_diff_group.addButton(btn_d, idx)
            diff_box.addWidget(btn_d)

        diff_box.addStretch()
        hf_lay.addLayout(diff_box)
        h_lay.addWidget(hdr_frame)

        # Assessment Modes Grid
        modes_title = QLabel("🎯 CHOOSE ASSESSMENT MODE")
        modes_title.setStyleSheet("font-size: 11pt; font-weight: 800; color: #06B6D4; font-family: Consolas;")
        h_lay.addWidget(modes_title)

        grid = QGridLayout()
        grid.setSpacing(14)

        for i, mode in enumerate(ASSESSMENT_MODES):
            m_card = QFrame()
            m_card.setStyleSheet(f"""
                QFrame {{
                    background-color: #0F172A;
                    border: 1px solid #1E293B;
                    border-top: 3px solid {mode['color']};
                    border-radius: 8px;
                    padding: 14px;
                }}
                QFrame:hover {{
                    border-color: {mode['color']};
                }}
            """)
            mc_lay = QVBoxLayout(m_card)
            mc_lay.setSpacing(8)

            m_h = QHBoxLayout()
            m_title = QLabel(f"  {mode['title']}")
            m_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F8FAFC;")
            m_h.addWidget(m_title)
            m_h.addStretch()

            # Calculate actual available candidate count for this mode
            mode_id = mode['id']
            valid_candidates = self.get_candidate_questions(mode_id, self.selected_difficulty)
            actual_q_count = len(valid_candidates)

            cnt_badge = QLabel(f"{actual_q_count} Qs • {mode['time_min']} mins")
            cnt_badge.setStyleSheet(f"background-color: #1E293B; color: {mode['color']}; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 8pt;")
            m_h.addWidget(cnt_badge)
            mc_lay.addLayout(m_h)

            m_desc = QLabel(mode['desc'])
            m_desc.setWordWrap(True)
            m_desc.setStyleSheet("font-size: 8.5pt; color: #94A3B8;")
            mc_lay.addWidget(m_desc)

            btn_start = QPushButton("▶ Start Assessment")
            btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_start.setStyleSheet(f"""
                QPushButton {{
                    background-color: {mode['color']};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 9pt;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            btn_start.clicked.connect(lambda _, m_id=mode['id']: self.start_test(m_id))
            mc_lay.addWidget(btn_start)

            grid.addWidget(m_card, i // 2, i % 2)

        h_lay.addLayout(grid)
        scroll.setWidget(home_card)
        self.container_layout.addWidget(scroll)

    def get_candidate_questions(self, mode_id, difficulty="ALL"):
        """Multi-dimensional diversity sampling with duplicate filtering and answer equalizing."""
        mode_data = next((m for m in ASSESSMENT_MODES if m["id"] == mode_id), ASSESSMENT_MODES[0])
        target_count = mode_data["questions"]

        # Collect all valid questions
        valid_pool = []
        for q in ASSESSMENT_QUESTIONS:
            is_valid, norm_q, err_msg = validate_and_normalize_question(q)
            if is_valid:
                m_match = (mode_id in norm_q.get("target_modes", [])) or (mode_id in ["mock", "quick", "mixed"])
                d_match = (difficulty == "ALL") or (norm_q.get("difficulty") == difficulty)
                if m_match and d_match:
                    valid_pool.append(norm_q)

        # Fallback pool if mode filtering was strict
        if len(valid_pool) < target_count:
            for q in ASSESSMENT_QUESTIONS:
                is_valid, norm_q, _ = validate_and_normalize_question(q)
                if is_valid and norm_q not in valid_pool:
                    valid_pool.append(norm_q)

        # Sample with maximum diversity and duplicate rejection
        diverse_qs = AssessmentQualityEngine.sample_diverse_exam(
            candidate_pool=valid_pool,
            target_count=target_count,
            mode_id=mode_id,
            difficulty_filter=difficulty
        )

        # Pre-flight quality validation & answer position equalization
        _, final_qs, _ = AssessmentQualityEngine.validate_and_finalize_exam(diverse_qs, target_count)
        return final_qs

    # ==========================================================================
    # 2. START TEST & QUESTION SESSION PREPARATION
    # ==========================================================================

    def start_test(self, mode_id):
        self.selected_mode = mode_id
        candidates = self.get_candidate_questions(mode_id, self.selected_difficulty)
        self.active_questions = candidates
        
        mode_data = next((m for m in ASSESSMENT_MODES if m["id"] == mode_id), ASSESSMENT_MODES[0])
        
        self.current_q_index = 0
        self.user_answers = {}
        self.submitted_questions = set()
        self.timer_seconds = mode_data["time_min"] * 60
        self.elapsed_seconds = 0
        self.test_completed = False

        self.timer.start()
        self.show_test_runner()

    # ==========================================================================
    # 3. ACTIVE TEST RUNNER WORKSPACE
    # ==========================================================================

    def show_test_runner(self):
        self.clear_container()

        main_runner = QFrame()
        mr_lay = QVBoxLayout(main_runner)
        mr_lay.setContentsMargins(6, 6, 6, 6)
        mr_lay.setSpacing(8)

        # Header Control & Timer Bar
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 10px;")
        h_lay = QHBoxLayout(hdr)
        h_lay.setContentsMargins(8, 4, 8, 4)

        mode_title = next((m["title"] for m in ASSESSMENT_MODES if m["id"] == self.selected_mode), "TEST")
        t_lbl = QLabel(f"⚡ {mode_title} MODE")
        t_lbl.setStyleSheet("font-size: 10.5pt; font-weight: 800; color: #F97316; font-family: Consolas;")
        h_lay.addWidget(t_lbl)

        h_lay.addStretch()

        self.lbl_timer = QLabel("⏱ Time Remaining: --:--")
        self.lbl_timer.setStyleSheet("font-size: 10pt; font-weight: bold; color: #38BDF8; font-family: Consolas;")
        h_lay.addWidget(self.lbl_timer)

        btn_finish = QPushButton("Submit & Finish Test")
        btn_finish.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finish.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 5px 12px; border-radius: 4px; font-size: 8.5pt;")
        btn_finish.clicked.connect(self.finish_test)
        h_lay.addWidget(btn_finish)

        mr_lay.addWidget(hdr)

        # Progress Bar
        self.test_prog = QProgressBar()
        self.test_prog.setFixedHeight(6)
        self.test_prog.setRange(0, len(self.active_questions) if self.active_questions else 1)
        self.test_prog.setValue(len(self.submitted_questions))
        self.test_prog.setTextVisible(False)
        self.test_prog.setStyleSheet("QProgressBar { background-color: #1E293B; border-radius: 3px; } QProgressBar::chunk { background-color: #10B981; }")
        mr_lay.addWidget(self.test_prog)

        # Splitter: Question Display (Left) + Question Grid Navigator (Right)
        runner_splitter = QSplitter(Qt.Orientation.Horizontal)
        runner_splitter.setStyleSheet("QSplitter::handle { background-color: #1E293B; width: 2px; }")

        # --- Left Question Scroll Workspace ---
        q_scroll = QScrollArea()
        q_scroll.setWidgetResizable(True)
        q_scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }")

        self.q_container = QFrame()
        self.q_container.setStyleSheet("QFrame { background-color: #0B1020; }")
        self.q_layout = QVBoxLayout(self.q_container)
        self.q_layout.setContentsMargins(16, 16, 16, 16)
        self.q_layout.setSpacing(12)
        q_scroll.setWidget(self.q_container)

        # --- Right Question Navigator Grid ---
        nav_panel = QFrame()
        nav_panel.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; }")
        np_lay = QVBoxLayout(nav_panel)

        np_title = QLabel(f"📌 QUESTION NAVIGATOR ({len(self.active_questions)} Qs)")
        np_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #06B6D4; font-family: Consolas;")
        np_lay.addWidget(np_title)

        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        nav_grid_widget = QWidget()
        nav_grid = QGridLayout(nav_grid_widget)
        nav_grid.setSpacing(6)
        
        self.nav_buttons = {}
        for idx, q in enumerate(self.active_questions):
            btn_q = QPushButton(str(idx + 1))
            btn_q.setFixedSize(36, 36)
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_buttons[idx] = btn_q
            btn_q.clicked.connect(lambda _, i=idx: self.jump_to_question(i))
            nav_grid.addWidget(btn_q, idx // 4, idx % 4)

        nav_scroll.setWidget(nav_grid_widget)
        np_lay.addWidget(nav_scroll, 1)

        runner_splitter.addWidget(q_scroll)
        runner_splitter.addWidget(nav_panel)
        runner_splitter.setSizes([730, 270])

        mr_lay.addWidget(runner_splitter, 1)
        self.container_layout.addWidget(main_runner)

        # Refresh all navigator button styles
        self.refresh_all_nav_buttons()
        self.update_timer_display()
        self.render_current_question()

    def refresh_all_nav_buttons(self):
        for idx in range(len(self.active_questions)):
            self.update_nav_button_style(idx)

    def update_nav_button_style(self, idx):
        if not hasattr(self, 'nav_buttons') or idx not in self.nav_buttons:
            return
        btn = self.nav_buttons[idx]
        q = self.active_questions[idx]
        q_id = q["id"]

        is_sub = q_id in self.submitted_questions
        has_ans = (q_id in self.user_answers and self.user_answers[q_id] not in [None, [], "", {}])
        is_curr = (idx == self.current_q_index)

        border = "2.5px solid #38BDF8" if is_curr else "1px solid #334155"

        if is_sub or has_ans:
            bg = "#10B981"
            txt = f"✓ {idx + 1}"
        elif is_curr:
            bg = "#F97316"
            txt = str(idx + 1)
        else:
            bg = "#1E293B"
            txt = str(idx + 1)

        btn.setText(txt)
        btn.setStyleSheet(f"background-color: {bg}; color: white; font-weight: bold; border-radius: 4px; border: {border}; font-size: 8pt;")

    def jump_to_question(self, idx):
        if 0 <= idx < len(self.active_questions):
            self.current_q_index = idx
            self.render_current_question()
            self.refresh_all_nav_buttons()

    # --------------------------------------------------------------------------
    # Render Question Card & Dedicated Question Answer UI Component
    # --------------------------------------------------------------------------

    def render_current_question(self):
        while self.q_layout.count():
            child = self.q_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.active_questions:
            err_card = QFrame()
            err_card.setStyleSheet("background-color: #450A0A; border: 1px solid #EF4444; border-radius: 8px; padding: 14px;")
            e_lay = QVBoxLayout(err_card)
            e_lay.addWidget(QLabel("⚠️ No questions found matching selected mode & difficulty. Please return to Home.", styleSheet="color: #FCA5A5; font-weight: bold;"))
            self.q_layout.addWidget(err_card)
            return

        q = self.active_questions[self.current_q_index]
        q_id = q["id"]
        is_valid, norm_q, err_msg = validate_and_normalize_question(q)

        # Defensive Check: Render Diagnostic Error if question data is malformed
        if not is_valid:
            log.error(f"[ASSESSMENT DATA ERROR] {err_msg}")
            err_card = QFrame()
            err_card.setStyleSheet("background-color: #450A0A; border: 1px solid #EF4444; border-radius: 8px; padding: 14px;")
            e_lay = QVBoxLayout(err_card)
            e_lay.addWidget(QLabel(f"⚠️ [ASSESSMENT DATA ERROR]\nUnable to render this question.\nQuestion ID: {q_id}\nMissing Data: {err_msg}", styleSheet="color: #FCA5A5; font-weight: bold; font-family: Consolas;"))
            self.q_layout.addWidget(err_card)
            return

        is_submitted = q_id in self.submitted_questions

        # --- Question Header Card ---
        q_card = QFrame()
        q_card.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;")
        qc_lay = QVBoxLayout(q_card)
        qc_lay.setSpacing(10)

        # Badges Line
        b_line = QHBoxLayout()
        q_num = QLabel(f"Question {self.current_q_index + 1} of {len(self.active_questions)}")
        q_num.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F97316; font-family: Consolas;")
        b_line.addWidget(q_num)
        b_line.addStretch()

        type_badge = QLabel(f" {norm_q.get('type', 'mcq').upper()} ")
        type_badge.setStyleSheet("background-color: #1E293B; color: #EAB308; font-weight: bold; border-radius: 4px; font-size: 8pt; padding: 2px 6px;")
        b_line.addWidget(type_badge)

        diff_badge = QLabel(f" {norm_q.get('difficulty', 'MEDIUM')} ")
        diff_badge.setStyleSheet("background-color: #1E293B; color: #38BDF8; font-weight: bold; border-radius: 4px; font-size: 8pt; padding: 2px 6px;")
        b_line.addWidget(diff_badge)

        top_badge = QLabel(f" {norm_q.get('topic', 'General')} ")
        top_badge.setStyleSheet("background-color: #1E293B; color: #10B981; font-weight: bold; border-radius: 4px; font-size: 8pt; padding: 2px 6px;")
        b_line.addWidget(top_badge)

        qc_lay.addLayout(b_line)

        # Question Text
        qt = QLabel(norm_q["question"])
        qt.setWordWrap(True)
        qt.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F8FAFC; line-height: 1.4;")
        qc_lay.addWidget(qt)

        self.q_layout.addWidget(q_card)

        # --- Answer Input Component Card ---
        opt_card = QFrame()
        opt_card.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;")
        oc_lay = QVBoxLayout(opt_card)
        oc_lay.setSpacing(10)

        q_type = norm_q["type"]

        # Reset Form Handles
        self.btn_group = None
        self.chk_boxes = []
        self.match_combos = {}
        self.fill_line_edit = None

        radio_style = """
            QRadioButton {
                color: #CBD5E1;
                font-size: 10pt;
                font-weight: 500;
                padding: 10px 14px;
                background-color: #1E293B;
                border: 1.5px solid #334155;
                border-radius: 8px;
                margin-bottom: 4px;
            }
            QRadioButton:hover {
                color: #FFFFFF;
                background-color: #334155;
                border: 1.5px solid #06B6D4;
            }
            QRadioButton:checked {
                color: #FFFFFF;
                font-weight: bold;
                background-color: #0F2942;
                border: 2px solid #06B6D4;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #64748B;
                background-color: #1E293B;
            }
            QRadioButton::indicator:hover {
                border-color: #06B6D4;
            }
            QRadioButton::indicator:checked {
                border-color: #06B6D4;
                background-color: #06B6D4;
            }
        """

        checkbox_style = """
            QCheckBox {
                color: #CBD5E1;
                font-size: 10pt;
                font-weight: 500;
                padding: 10px 14px;
                background-color: #1E293B;
                border: 1.5px solid #334155;
                border-radius: 8px;
                margin-bottom: 4px;
            }
            QCheckBox:hover {
                color: #FFFFFF;
                background-color: #334155;
                border: 1.5px solid #10B981;
            }
            QCheckBox:checked {
                color: #FFFFFF;
                font-weight: bold;
                background-color: #063726;
                border: 2px solid #10B981;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #64748B;
                background-color: #1E293B;
            }
            QCheckBox::indicator:hover {
                border-color: #10B981;
            }
            QCheckBox::indicator:checked {
                border-color: #10B981;
                background-color: #10B981;
            }
        """

        # RENDERER 1: MATCHING / MATCH THE FOLLOWING
        if q_type == "matching":
            oc_lay.addWidget(QLabel("Match each item on the left with the correct option on the right:", styleSheet="color: #06B6D4; font-weight: bold; font-size: 9pt;"))
            
            left_items = norm_q.get("left", [])
            right_items = list(norm_q.get("right", []))
            user_matches = self.user_answers.get(q_id, {})

            for left_str in left_items:
                m_row = QHBoxLayout()
                lbl_left = QLabel(f"• {left_str}")
                lbl_left.setStyleSheet("color: #F8FAFC; font-weight: bold; font-size: 9.5pt;")

                combo = QComboBox()
                combo.addItem("-- Select Match --", "")
                for r_val in right_items:
                    combo.addItem(r_val, r_val)

                if left_str in user_matches:
                    sel_val = user_matches[left_str]
                    idx = combo.findText(sel_val)
                    if idx != -1:
                        combo.setCurrentIndex(idx)

                if is_submitted:
                    combo.setEnabled(False)

                combo.setStyleSheet("background-color: #1E293B; color: #FFFFFF; font-weight: bold; padding: 6px; border-radius: 6px; border: 1px solid #334155;")
                
                def make_matching_handler(curr_left, c_box):
                    def on_change():
                        val = c_box.currentText()
                        if q_id not in self.user_answers:
                            self.user_answers[q_id] = {}
                        if val and val != "-- Select Match --":
                            self.user_answers[q_id][curr_left] = val
                        else:
                            self.user_answers[q_id].pop(curr_left, None)
                        if not self.user_answers[q_id]:
                            self.user_answers.pop(q_id, None)
                        self.update_nav_button_style(self.current_q_index)
                    return on_change

                combo.currentIndexChanged.connect(make_matching_handler(left_str, combo))
                m_row.addWidget(lbl_left, 1)
                m_row.addWidget(combo, 1)
                oc_lay.addLayout(m_row)
                self.match_combos[left_str] = combo

        # RENDERER 2: FILL IN THE BLANK
        elif q_type == "fill_blank":
            oc_lay.addWidget(QLabel("Type your answer in the box below:", styleSheet="color: #06B6D4; font-weight: bold; font-size: 9pt;"))
            self.fill_line_edit = QLineEdit()
            self.fill_line_edit.setPlaceholderText("Type your answer here...")
            if q_id in self.user_answers:
                self.fill_line_edit.setText(str(self.user_answers[q_id]))
            if is_submitted:
                self.fill_line_edit.setEnabled(False)
            self.fill_line_edit.setStyleSheet("QLineEdit { background-color: #1E293B; color: #F8FAFC; border: 1.5px solid #334155; border-radius: 6px; padding: 8px; font-size: 10pt; font-family: Consolas; } QLineEdit:focus { border: 2px solid #06B6D4; background-color: #0B253A; }")
            
            def on_fill_text_changed(txt):
                val = txt.strip()
                if val:
                    self.user_answers[q_id] = val
                else:
                    self.user_answers.pop(q_id, None)
                self.update_nav_button_style(self.current_q_index)

            self.fill_line_edit.textChanged.connect(on_fill_text_changed)
            oc_lay.addWidget(self.fill_line_edit)

        # RENDERER 3: MULTI-SELECT (CHECKBOXES)
        elif q_type == "multi_select":
            oc_lay.addWidget(QLabel("Select ALL options that apply:", styleSheet="color: #06B6D4; font-weight: bold; font-size: 9pt;"))
            selected_opts = self.user_answers.get(q_id, [])
            if not isinstance(selected_opts, list):
                selected_opts = [selected_opts]
            for o_idx, opt in enumerate(norm_q.get("options", [])):
                chk = QCheckBox(opt)
                chk.setStyleSheet(checkbox_style)
                if o_idx in selected_opts:
                    chk.setChecked(True)
                if is_submitted:
                    chk.setEnabled(False)
                self.chk_boxes.append((o_idx, chk))
                
                def make_cb_toggle_handler():
                    def on_toggle():
                        sel = [idx for idx, c in self.chk_boxes if c.isChecked()]
                        if sel:
                            self.user_answers[q_id] = sel
                        else:
                            self.user_answers.pop(q_id, None)
                        self.update_nav_button_style(self.current_q_index)
                    return on_toggle

                chk.toggled.connect(make_cb_toggle_handler())
                oc_lay.addWidget(chk)

        # RENDERER 4: STANDARD MCQ / TRUE-FALSE / REGISTER / MACHINE CODE / ORDERING
        else:
            self.btn_group = QButtonGroup(opt_card)
            curr_val = self.user_answers.get(q_id)
            sel_idx = None
            if curr_val is not None:
                if isinstance(curr_val, list) and len(curr_val) > 0:
                    try:
                        sel_idx = int(curr_val[0])
                    except (ValueError, TypeError):
                        pass
                elif isinstance(curr_val, (int, str)):
                    try:
                        sel_idx = int(curr_val)
                    except (ValueError, TypeError):
                        pass

            for o_idx, opt in enumerate(norm_q.get("options", [])):
                rad = QRadioButton(opt)
                rad.setStyleSheet(radio_style)
                if sel_idx == o_idx:
                    rad.setChecked(True)
                if is_submitted:
                    rad.setEnabled(False)
                self.btn_group.addButton(rad, o_idx)
                oc_lay.addWidget(rad)

            def on_mcq_option_selected(b_id):
                if b_id != -1:
                    self.user_answers[q_id] = b_id
                    self.update_nav_button_style(self.current_q_index)

            self.btn_group.idClicked.connect(on_mcq_option_selected)

        self.q_layout.addWidget(opt_card)

        # --- Submitted Answer Feedback Card ---
        if is_submitted:
            fb_card = QFrame()
            user_ans = self.user_answers.get(q_id)

            is_correct = False
            if q_type == "matching":
                correct_matches = norm_q.get("correct_matches", {})
                is_correct = (user_ans == correct_matches)
            elif q_type == "multi_select":
                correct_set = set(norm_q.get("correct_answers", []))
                is_correct = (set(user_ans or []) == correct_set)
            elif q_type == "fill_blank":
                is_correct = (str(user_ans).strip().lower() == str(norm_q.get("correct_answer")).strip().lower())
            else:
                is_correct = (user_ans == norm_q.get("correct_answer"))

            fb_card.setStyleSheet(f"background-color: {'#061826' if is_correct else '#1E0E17'}; border: 1px solid {'#10B981' if is_correct else '#EF4444'}; border-radius: 8px; padding: 12px;")
            f_lay = QVBoxLayout(fb_card)

            st_lbl = QLabel("✔ CORRECT ANSWER!" if is_correct else "✖ INCORRECT")
            st_lbl.setStyleSheet(f"font-size: 10.5pt; font-weight: bold; color: {'#10B981' if is_correct else '#EF4444'};")
            f_lay.addWidget(st_lbl)

            exp_lbl = QLabel(f"Explanation: {norm_q.get('explanation', '')}")
            exp_lbl.setWordWrap(True)
            exp_lbl.setStyleSheet("font-size: 9pt; color: #E2E8F0; margin-top: 4px;")
            f_lay.addWidget(exp_lbl)

            self.q_layout.addWidget(fb_card)

        # --- Action Buttons (Submit / Next) ---
        act_bar = QHBoxLayout()
        btn_prev = QPushButton("← Previous")
        btn_prev.setEnabled(self.current_q_index > 0)
        btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_prev.setStyleSheet("background-color: #1E293B; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        btn_prev.clicked.connect(lambda: self.jump_to_question(self.current_q_index - 1))
        act_bar.addWidget(btn_prev)

        act_bar.addStretch()

        if not is_submitted:
            btn_sub = QPushButton("Submit Answer")
            btn_sub.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_sub.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
            btn_sub.clicked.connect(self.submit_current_answer)
            act_bar.addWidget(btn_sub)
        else:
            btn_next = QPushButton("Next Question →" if self.current_q_index < len(self.active_questions) - 1 else "View Test Results →")
            btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_next.setStyleSheet("background-color: #F97316; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
            btn_next.clicked.connect(self.next_question_action)
            act_bar.addWidget(btn_next)

        self.q_layout.addLayout(act_bar)

    def submit_current_answer(self):
        q = self.active_questions[self.current_q_index]
        q_id = q["id"]
        q_type = q.get("type", "mcq")

        if q_type == "matching":
            matches = {}
            for left_key, combo in self.match_combos.items():
                val = combo.currentText()
                if val == "-- Select Match --" or not val:
                    QMessageBox.warning(self, "Incomplete Match", f"Please select a match for '{left_key}' before submitting.")
                    return
                matches[left_key] = val
            self.user_answers[q_id] = matches

        elif q_type == "fill_blank":
            val = self.fill_line_edit.text().strip()
            if not val:
                QMessageBox.warning(self, "Input Required", "Please type your answer in the text box before submitting.")
                return
            self.user_answers[q_id] = val

        elif q_type == "multi_select":
            sel_list = [idx for idx, chk in self.chk_boxes if chk.isChecked()]
            if not sel_list:
                QMessageBox.warning(self, "Selection Required", "Please select at least one option before submitting.")
                return
            self.user_answers[q_id] = sel_list

        else:
            if not self.btn_group or self.btn_group.checkedId() == -1:
                QMessageBox.warning(self, "Selection Required", "Please select an answer option before submitting.")
                return
            self.user_answers[q_id] = self.btn_group.checkedId()

        self.submitted_questions.add(q_id)
        self.show_test_runner()

    def next_question_action(self):
        if self.current_q_index < len(self.active_questions) - 1:
            self.current_q_index += 1
            self.show_test_runner()
        else:
            self.finish_test()

    def on_timer_tick(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.elapsed_seconds += 1
            self.update_timer_display()
        else:
            self.timer.stop()
            QMessageBox.information(self, "Time Expired", "Assessment time limit has expired. Submitting test automatically.")
            self.finish_test()

    def update_timer_display(self):
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        if hasattr(self, 'lbl_timer'):
            self.lbl_timer.setText(f"⏱ Time Remaining: {mins:02d}:{secs:02d}")

    def finish_test(self):
        self.timer.stop()
        self.test_completed = True
        self.show_result_page()

    # ==========================================================================
    # 4. RESULT PAGE & PERFORMANCE ANALYTICS
    # ==========================================================================

    def show_result_page(self):
        self.clear_container()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }")

        res_card = QFrame()
        res_card.setStyleSheet("QFrame { background-color: #0B1020; }")
        r_lay = QVBoxLayout(res_card)
        r_lay.setContentsMargins(20, 20, 20, 20)
        r_lay.setSpacing(16)

        total_qs = len(self.active_questions)
        correct_cnt = 0
        incorrect_cnt = 0
        skipped_cnt = 0

        topic_stats = {}

        for q in self.active_questions:
            q_id = q["id"]
            q_type = q.get("type", "mcq")
            top = q.get("topic", "General")

            if top not in topic_stats:
                topic_stats[top] = {"correct": 0, "total": 0}
            topic_stats[top]["total"] += 1

            if q_id not in self.submitted_questions:
                skipped_cnt += 1
            else:
                user_ans = self.user_answers.get(q_id)
                is_correct = False

                if q_type == "matching":
                    is_correct = (user_ans == q.get("correct_matches", {}))
                elif q_type == "multi_select":
                    is_correct = (set(user_ans or []) == set(q.get("correct_answers", [])))
                elif q_type == "fill_blank":
                    is_correct = (str(user_ans).strip().lower() == str(q.get("correct_answer")).strip().lower())
                else:
                    is_correct = (user_ans == q.get("correct_answer"))

                if is_correct:
                    correct_cnt += 1
                    topic_stats[top]["correct"] += 1
                else:
                    incorrect_cnt += 1

        accuracy = int((correct_cnt / total_qs) * 100) if total_qs > 0 else 0

        # Header Title Card
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 18px;")
        h_lay = QVBoxLayout(hdr)
        
        t_lbl = QLabel("🏆 ASSESSMENT COMPLETE")
        t_lbl.setStyleSheet("font-size: 16pt; font-weight: 800; color: #10B981; font-family: Consolas;")
        h_lay.addWidget(t_lbl)

        s_lbl = QLabel(f"Score Summary for {self.selected_mode.upper()} Mode • Accuracy: {accuracy}%")
        s_lbl.setStyleSheet("font-size: 9.5pt; color: #94A3B8;")
        h_lay.addWidget(s_lbl)

        r_lay.addWidget(hdr)

        # Score Summary Cards Grid
        sc_grid = QGridLayout()
        sc_grid.setSpacing(12)

        cards = [
            ("Score", f"{correct_cnt} / {total_qs}", "#F97316"),
            ("Accuracy", f"{accuracy}%", "#10B981"),
            ("Correct", f"{correct_cnt}", "#10B981"),
            ("Incorrect", f"{incorrect_cnt}", "#EF4444"),
            ("Skipped", f"{skipped_cnt}", "#EAB308"),
            ("Time Spent", f"{self.elapsed_seconds // 60:02d}:{self.elapsed_seconds % 60:02d}", "#38BDF8")
        ]

        for i, (title, val, color) in enumerate(cards):
            card = QFrame()
            card.setStyleSheet(f"background-color: #0F172A; border: 1px solid #1E293B; border-top: 3px solid {color}; border-radius: 6px; padding: 10px;")
            c_lay = QVBoxLayout(card)
            c_lbl = QLabel(title)
            c_lbl.setStyleSheet("font-size: 8.5pt; color: #94A3B8; font-weight: bold;")
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(f"font-size: 14pt; font-weight: 800; color: {color}; font-family: Consolas;")
            c_lay.addWidget(c_lbl)
            c_lay.addWidget(v_lbl)
            sc_grid.addWidget(card, i // 3, i % 3)

        r_lay.addLayout(sc_grid)

        # Topic Breakdown
        tb_card = QFrame()
        tb_card.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;")
        tbl_lay = QVBoxLayout(tb_card)

        tb_title = QLabel("📊 TOPIC ACCURACY BREAKDOWN")
        tb_title.setStyleSheet("font-size: 10pt; font-weight: bold; color: #06B6D4; font-family: Consolas;")
        tbl_lay.addWidget(tb_title)

        weak_topics = []
        for top, stats in topic_stats.items():
            top_acc = int((stats["correct"] / stats["total"]) * 100) if stats["total"] > 0 else 0
            if top_acc < 70:
                weak_topics.append(top)

            row = QHBoxLayout()
            t_name = QLabel(top)
            t_name.setStyleSheet("font-size: 9pt; color: #F8FAFC; font-weight: bold;")
            p_bar = QProgressBar()
            p_bar.setRange(0, 100)
            p_bar.setValue(top_acc)
            p_bar.setTextVisible(True)
            p_bar.setStyleSheet("QProgressBar { background-color: #1E293B; color: white; border-radius: 3px; font-weight: bold; } QProgressBar::chunk { background-color: #10B981; }")
            row.addWidget(t_name, 1)
            row.addWidget(p_bar, 2)
            tbl_lay.addLayout(row)

        r_lay.addWidget(tb_card)

        # Study Recommendations Card
        rec_card = QFrame()
        rec_card.setStyleSheet("background-color: #111C35; border: 1px solid #2563EB; border-radius: 8px; padding: 14px;")
        rec_lay = QVBoxLayout(rec_card)

        rec_title = QLabel("💡 AUTOMATED STUDY RECOMMENDATIONS")
        rec_title.setStyleSheet("font-size: 10pt; font-weight: bold; color: #60A5FA; font-family: Consolas;")
        rec_lay.addWidget(rec_title)

        if weak_topics:
            rec_txt = QLabel(f"Your accuracy was lower in: {', '.join(weak_topics)}.\nRecommended Next Steps: Revise MP&MC Learn Module theory -> Practice related instructions in Virtual Trainer.")
        else:
            rec_txt = QLabel("Excellent performance across all topics! You are well-prepared for university and GATE level examinations.")

        rec_txt.setWordWrap(True)
        rec_txt.setStyleSheet("font-size: 9pt; color: #E2E8F0;")
        rec_lay.addWidget(rec_txt)

        r_lay.addWidget(rec_card)

        # Action Buttons (Review / Home)
        act_bar = QHBoxLayout()
        btn_rev = QPushButton("🔍 Review All Answers")
        btn_rev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rev.setStyleSheet("background-color: #06B6D4; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        btn_rev.clicked.connect(self.show_question_review)
        act_bar.addWidget(btn_rev)

        act_bar.addStretch()

        btn_home = QPushButton("🏠 Return to Assessment Home")
        btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_home.setStyleSheet("background-color: #F97316; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        btn_home.clicked.connect(self.show_home_page)
        act_bar.addWidget(btn_home)

        r_lay.addLayout(act_bar)

        scroll.setWidget(res_card)
        self.container_layout.addWidget(scroll)

    # ==========================================================================
    # 5. QUESTION REVIEW MODE
    # ==========================================================================

    def show_question_review(self):
        self.clear_container()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }")

        rev_card = QFrame()
        rev_card.setStyleSheet("QFrame { background-color: #0B1020; }")
        rv_lay = QVBoxLayout(rev_card)
        rv_lay.setContentsMargins(18, 18, 18, 18)
        rv_lay.setSpacing(14)

        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 12px;")
        h_lay = QHBoxLayout(hdr)
        
        t_lbl = QLabel("🔍 QUESTION REVIEW MODE")
        t_lbl.setStyleSheet("font-size: 12pt; font-weight: 800; color: #06B6D4; font-family: Consolas;")
        h_lay.addWidget(t_lbl)
        h_lay.addStretch()

        btn_back = QPushButton("← Back to Results")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("background-color: #1E293B; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px;")
        btn_back.clicked.connect(self.show_result_page)
        h_lay.addWidget(btn_back)

        rv_lay.addWidget(hdr)

        for idx, q in enumerate(self.active_questions):
            q_id = q["id"]
            q_type = q.get("type", "mcq")
            user_ans = self.user_answers.get(q_id)

            is_correct = False
            if q_type == "matching":
                is_correct = (user_ans == q.get("correct_matches", {}))
            elif q_type == "multi_select":
                is_correct = (set(user_ans or []) == set(q.get("correct_answers", [])))
            elif q_type == "fill_blank":
                is_correct = (str(user_ans).strip().lower() == str(q.get("correct_answer")).strip().lower())
            else:
                is_correct = (user_ans == q.get("correct_answer"))

            q_item = QFrame()
            q_item.setStyleSheet(f"background-color: #0F172A; border: 1px solid #1E293B; border-left: 4px solid {'#10B981' if is_correct else '#EF4444'}; border-radius: 6px; padding: 12px;")
            qi_lay = QVBoxLayout(q_item)

            q_hdr = QLabel(f"Q{idx + 1}: {q['question']}")
            q_hdr.setWordWrap(True)
            q_hdr.setStyleSheet("font-weight: bold; font-size: 9.5pt; color: #F8FAFC;")
            qi_lay.addWidget(q_hdr)

            ans_lbl = QLabel(f"Your Answer: {user_ans}  |  Result: {'CORRECT' if is_correct else 'INCORRECT'}")
            ans_lbl.setStyleSheet(f"font-size: 8.5pt; font-weight: bold; color: {'#10B981' if is_correct else '#EF4444'}; margin-top: 4px;")
            qi_lay.addWidget(ans_lbl)

            exp_lbl = QLabel(f"Explanation: {q.get('explanation', '')}")
            exp_lbl.setWordWrap(True)
            exp_lbl.setStyleSheet("font-size: 8.5pt; color: #94A3B8; margin-top: 2px;")
            qi_lay.addWidget(exp_lbl)

            rv_lay.addWidget(q_item)

        scroll.setWidget(rev_card)
        self.container_layout.addWidget(scroll)
