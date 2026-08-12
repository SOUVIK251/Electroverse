"""
ElectroVerse Microprocessor & Microcontroller Master Learning View.
Modern Engineering Learning System with 22 Comprehensive Categories,
Interactive Diagrams, Register State Visualizers, Code Examples, and Quizzes.
"""

import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QSplitter, QPushButton,
    QProgressBar, QRadioButton, QButtonGroup, QMessageBox, QToolTip,
    QGridLayout, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QClipboard
import qtawesome as qta

from src.core.logger import log
from src.data.mpmc.learning_repository import LEARNING_CATEGORIES


class MPMCLearningView(QWidget):
    """Modern Engineering Learning Workstation View for MP&MC Hub."""

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view
        self.completed_topics = set()
        self.bookmarked_topics = set()
        self.show_bookmarks_only = False
        self.flat_topics_list = []
        self.current_topic_idx = 0
        self.current_topic_data = None

        log.info(f"Initializing modern MPMCLearningView with {len(LEARNING_CATEGORIES)} master categories")
        self.build_flat_topic_list()
        self.init_ui()
        self.populate_tree()

    def build_flat_topic_list(self):
        """Flattens categories into an ordered list of topics for easy Next/Prev navigation."""
        self.flat_topics_list = []
        for cat in LEARNING_CATEGORIES:
            for top in cat.get("topics", []):
                top_copy = dict(top)
                top_copy["category_title"] = cat["title"]
                top_copy["category_color"] = cat.get("color", "#F97316")
                top_copy["category_icon"] = cat.get("icon", "fa5s.book")
                self.flat_topics_list.append(top_copy)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # ----------------------------------------------------------------------
        # Top Control Bar & Header
        # ----------------------------------------------------------------------
        top_bar = QFrame()
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 8px;
                padding: 6px 12px;
            }
        """)
        tb_lay = QHBoxLayout(top_bar)
        tb_lay.setContentsMargins(8, 6, 8, 6)
        tb_lay.setSpacing(12)

        # Title & Subtitle
        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        t_lbl = QLabel("⚡ MICROPROCESSOR & MICROCONTROLLER MASTER ENGINEERING SYSTEM")
        t_lbl.setStyleSheet("font-size: 11pt; font-weight: 800; color: #F97316; font-family: 'Consolas', 'Segoe UI';")
        sub_lbl = QLabel(f"{len(LEARNING_CATEGORIES)} Structured Modules • Concept Visualizations • Register State Analysis • Interactive Self-Checks")
        sub_lbl.setStyleSheet("font-size: 8.5pt; color: #94A3B8;")
        t_box.addWidget(t_lbl)
        t_box.addWidget(sub_lbl)
        tb_lay.addLayout(t_box, 1)

        # Progress Indicator
        prog_box = QVBoxLayout()
        prog_box.setSpacing(2)
        tot_q = len(self.flat_topics_list) if self.flat_topics_list else 1
        self.lbl_progress = QLabel(f"Progress: 0 / {tot_q} Topics (0%)")
        self.lbl_progress.setStyleSheet("font-size: 8.5pt; font-weight: bold; color: #10B981;")
        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedWidth(160)
        self.prog_bar.setFixedHeight(8)
        self.prog_bar.setRange(0, tot_q)
        self.prog_bar.setValue(0)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 4px;
            }
        """)
        prog_box.addWidget(self.lbl_progress)
        prog_box.addWidget(self.prog_bar)
        tb_lay.addLayout(prog_box)

        # Bookmark Filter Button
        self.btn_filter_bm = QPushButton(" ★ Bookmarks (0)")
        self.btn_filter_bm.setCheckable(True)
        self.btn_filter_bm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter_bm.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 8.5pt;
            }
            QPushButton:checked {
                background-color: #EAB308;
                color: #000000;
                border-color: #EAB308;
            }
            QPushButton:hover:!checked {
                background-color: #334155;
            }
        """)
        self.btn_filter_bm.toggled.connect(self.toggle_bookmark_filter)
        tb_lay.addWidget(self.btn_filter_bm)

        main_layout.addWidget(top_bar)

        # ----------------------------------------------------------------------
        # Main Splitter: Left Tree Navigation & Right Reader Workspace
        # ----------------------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1E293B; width: 2px; }")

        # --- Left Panel ---
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: #0B1020; border: 1px solid #1E293B; border-radius: 8px; }")
        left_lay = QVBoxLayout(left_panel)
        left_lay.setContentsMargins(8, 8, 8, 8)
        left_lay.setSpacing(8)

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search 22 Modules, Opcodes, Registers...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QLineEdit:focus { border-color: #F97316; }
        """)
        self.search_input.textChanged.connect(self.filter_tree)
        left_lay.addWidget(self.search_input)

        # Tree Widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget { background-color: transparent; border: none; color: #94A3B8; font-size: 9pt; }
            QTreeWidget::item { padding: 5px; margin-bottom: 2px; }
            QTreeWidget::item:hover { background-color: #1E293B; color: #F8FAFC; border-radius: 4px; }
            QTreeWidget::item:selected { background-color: #1E293B; color: #F97316; font-weight: bold; border-radius: 4px; }
        """)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        left_lay.addWidget(self.tree_widget)

        # --- Right Panel ---
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #1E293B; border-radius: 8px; background-color: #0B1020; }
            QScrollBar:vertical {
                border: none; background: #0F172A; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical { background: #334155; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #F97316; }
        """)

        self.right_container = QFrame()
        self.right_container.setStyleSheet("QFrame { background-color: #0B1020; }")
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(18, 18, 18, 18)
        self.right_layout.setSpacing(14)

        right_scroll.setWidget(self.right_container)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_scroll)
        splitter.setSizes([320, 680])

        main_layout.addWidget(splitter, 1)

    # --------------------------------------------------------------------------
    # Tree Population & Filtering
    # --------------------------------------------------------------------------

    def populate_tree(self):
        self.tree_widget.clear()
        self.tree_item_map = {}  # topic_id -> QTreeWidgetItem

        for cat in LEARNING_CATEGORIES:
            cat_item = QTreeWidgetItem(self.tree_widget)
            cat_title = cat["title"]
            cat_item.setText(0, cat_title)
            cat_item.setFont(0, QFont("Consolas", 9.5, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor(cat.get("color", "#F97316")))

            for top in cat.get("topics", []):
                t_id = top["id"]
                t_item = QTreeWidgetItem(cat_item)
                
                # Check mark if completed
                status_icon = "✔ " if t_id in self.completed_topics else "⚡ "
                bm_icon = "★ " if t_id in self.bookmarked_topics else ""
                t_item.setText(0, f"{bm_icon}{status_icon}{top['title']}")
                t_item.setData(0, Qt.ItemDataRole.UserRole, t_id)
                t_item.setForeground(0, QColor("#E2E8F0" if t_id in self.completed_topics else "#94A3B8"))
                
                self.tree_item_map[t_id] = t_item

            cat_item.setExpanded(True)

        if self.flat_topics_list:
            self.load_topic_by_index(0)

    def filter_tree(self, text):
        query = text.lower().strip()
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            match_count = 0
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                t_id = child.data(0, Qt.ItemDataRole.UserRole)
                
                matches_text = (query in child.text(0).lower()) or (query in cat_item.text(0).lower())
                matches_bm = (not self.show_bookmarks_only) or (t_id in self.bookmarked_topics)

                if matches_text and matches_bm:
                    child.setHidden(False)
                    match_count += 1
                else:
                    child.setHidden(True)

            cat_item.setHidden(match_count == 0 and query != "")
            if match_count > 0:
                cat_item.setExpanded(True)

    def toggle_bookmark_filter(self, checked):
        self.show_bookmarks_only = checked
        self.filter_tree(self.search_input.text())

    def on_item_clicked(self, item):
        t_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not t_id:
            return
        for idx, top in enumerate(self.flat_topics_list):
            if top["id"] == t_id:
                self.load_topic_by_index(idx)
                break

    def load_topic_by_index(self, idx):
        if idx < 0 or idx >= len(self.flat_topics_list):
            return
        self.current_topic_idx = idx
        self.current_topic_data = self.flat_topics_list[idx]

        t_id = self.current_topic_data["id"]
        if t_id in self.tree_item_map:
            tree_item = self.tree_item_map[t_id]
            self.tree_widget.setCurrentItem(tree_item)

        self.render_topic_details()

    # --------------------------------------------------------------------------
    # Render Master Topic Workspace
    # --------------------------------------------------------------------------

    def render_topic_details(self):
        topic = self.current_topic_data
        if not topic:
            return

        # Clear existing layout
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # ----------------------------------------------------------------------
        # 1. Header Card (Title, Category Badge, Action Bar)
        # ----------------------------------------------------------------------
        hdr_card = QFrame()
        hdr_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
        h_lay = QVBoxLayout(hdr_card)
        h_lay.setSpacing(8)

        # Top Category Line + Action Buttons
        top_line = QHBoxLayout()
        cat_badge = QLabel(f"  {topic.get('category_title', '')}  ")
        cat_badge.setStyleSheet(f"background-color: #1E293B; color: {topic.get('category_color', '#F97316')}; font-weight: bold; border-radius: 4px; padding: 3px 8px; font-size: 8.5pt;")
        top_line.addWidget(cat_badge)
        top_line.addStretch()

        # Bookmark Button
        t_id = topic["id"]
        is_bm = t_id in self.bookmarked_topics
        btn_bm = QPushButton(" ★ Bookmarked" if is_bm else " ☆ Bookmark")
        btn_bm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_bm.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#EAB308' if is_bm else '#1E293B'};
                color: {'#000000' if is_bm else '#F8FAFC'};
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 8.5pt;
            }}
        """)
        btn_bm.clicked.connect(lambda: self.toggle_bookmark(t_id))
        top_line.addWidget(btn_bm)

        # Mark as Complete Button
        is_comp = t_id in self.completed_topics
        btn_comp = QPushButton(" ✔ Completed" if is_comp else " Mark as Complete")
        btn_comp.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_comp.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#10B981' if is_comp else '#06B6D4'};
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 8.5pt;
            }}
        """)
        btn_comp.clicked.connect(lambda: self.toggle_completion(t_id))
        top_line.addWidget(btn_comp)

        h_lay.addLayout(top_line)

        # Topic Title
        title_lbl = QLabel(topic.get("title", ""))
        title_lbl.setStyleSheet("font-size: 15pt; font-weight: 800; color: #F8FAFC; font-family: 'Segoe UI', Arial;")
        h_lay.addWidget(title_lbl)

        # Short Intuitive Explanation
        sum_lbl = QLabel(topic.get("summary", ""))
        sum_lbl.setWordWrap(True)
        sum_lbl.setStyleSheet("font-size: 9.5pt; color: #38BDF8; font-weight: 600; line-height: 1.4;")
        h_lay.addWidget(sum_lbl)

        self.right_layout.addWidget(hdr_card)

        # ----------------------------------------------------------------------
        # 2. Concept Visualization / Block Diagram
        # ----------------------------------------------------------------------
        if topic.get("diagram"):
            diag_card = QFrame()
            diag_card.setStyleSheet("QFrame { background-color: #060D1A; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; }")
            d_lay = QVBoxLayout(diag_card)
            d_lay.setSpacing(6)

            dh_lay = QHBoxLayout()
            d_title = QLabel("📐 CONCEPT VISUALIZATION & ARCHITECTURE DIAGRAM")
            d_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #F97316; font-family: Consolas;")
            dh_lay.addWidget(d_title)
            dh_lay.addStretch()

            btn_copy = QPushButton("Copy Diagram")
            btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_copy.setStyleSheet("background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 3px; padding: 2px 8px; font-size: 8pt;")
            btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(topic.get("diagram", "")))
            dh_lay.addWidget(btn_copy)
            d_lay.addLayout(dh_lay)

            diag_txt = QLabel(topic.get("diagram", "").strip())
            diag_txt.setFont(QFont("Consolas", 8.5))
            diag_txt.setStyleSheet("color: #10B981; background-color: #030712; padding: 10px; border-radius: 6px; border: 1px solid #1E293B;")
            d_lay.addWidget(diag_txt)

            self.right_layout.addWidget(diag_card)

        # ----------------------------------------------------------------------
        # 3. Important Points
        # ----------------------------------------------------------------------
        if topic.get("important_points"):
            pts_card = QFrame()
            pts_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
            p_lay = QVBoxLayout(pts_card)
            p_lay.setSpacing(6)

            p_title = QLabel("📌 KEY ENGINEERING SPECIFICATIONS & CORE CONCEPTS")
            p_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #06B6D4; font-family: Consolas;")
            p_lay.addWidget(p_title)

            for pt in topic.get("important_points", []):
                pt_row = QHBoxLayout()
                bullet = QLabel("✔")
                bullet.setStyleSheet("color: #10B981; font-weight: bold; font-size: 9pt;")
                pt_txt = QLabel(pt)
                pt_txt.setWordWrap(True)
                pt_txt.setStyleSheet("color: #E2E8F0; font-size: 9.5pt;")
                pt_row.addWidget(bullet)
                pt_row.addWidget(pt_txt, 1)
                p_lay.addLayout(pt_row)

            self.right_layout.addWidget(pts_card)

        # ----------------------------------------------------------------------
        # 4. How It Works
        # ----------------------------------------------------------------------
        if topic.get("how_it_works"):
            how_card = QFrame()
            how_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
            hw_lay = QVBoxLayout(how_card)
            hw_lay.setSpacing(6)

            hw_title = QLabel("⚙ OPERATIONAL MECHANICS & STEP-BY-STEP FLOW")
            hw_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #F59E0B; font-family: Consolas;")
            hw_lay.addWidget(hw_title)

            hw_txt = QLabel(topic.get("how_it_works", ""))
            hw_txt.setWordWrap(True)
            hw_txt.setStyleSheet("color: #CBD5E1; font-size: 9.5pt; line-height: 1.5;")
            hw_lay.addWidget(hw_txt)

            self.right_layout.addWidget(how_card)

        # ----------------------------------------------------------------------
        # 5. Example & Register / Flag State Analysis
        # ----------------------------------------------------------------------
        if topic.get("example") or topic.get("register_state"):
            ex_card = QFrame()
            ex_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
            ex_lay = QVBoxLayout(ex_card)
            ex_lay.setSpacing(10)

            ex_title = QLabel("💻 PRACTICAL EXECUTION EXAMPLE & REGISTER STATE TRACE")
            ex_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #10B981; font-family: Consolas;")
            ex_lay.addWidget(ex_title)

            if topic.get("example"):
                ex_txt = QLabel(topic.get("example", ""))
                ex_txt.setWordWrap(True)
                ex_txt.setFont(QFont("Consolas", 9))
                ex_txt.setStyleSheet("color: #F8FAFC; background-color: #030712; padding: 10px; border-radius: 6px; border: 1px solid #1E293B;")
                ex_lay.addWidget(ex_txt)

            if topic.get("register_state"):
                reg_info = topic.get("register_state")
                reg_frame = QFrame()
                reg_frame.setStyleSheet("background-color: #061826; border: 1px solid #06B6D4; border-radius: 6px; padding: 10px;")
                rf_lay = QGridLayout(reg_frame)

                rf_lay.addWidget(QLabel("BEFORE STATE:", styleSheet="color: #94A3B8; font-weight: bold; font-size: 8.5pt;"), 0, 0)
                rf_lay.addWidget(QLabel(reg_info.get("before", ""), styleSheet="color: #FCA5A5; font-family: Consolas; font-weight: bold; font-size: 9pt;"), 0, 1)

                rf_lay.addWidget(QLabel("OPERATION:", styleSheet="color: #94A3B8; font-weight: bold; font-size: 8.5pt;"), 1, 0)
                rf_lay.addWidget(QLabel(reg_info.get("operation", ""), styleSheet="color: #FDE047; font-family: Consolas; font-weight: bold; font-size: 9pt;"), 1, 1)

                rf_lay.addWidget(QLabel("AFTER STATE:", styleSheet="color: #94A3B8; font-weight: bold; font-size: 8.5pt;"), 2, 0)
                rf_lay.addWidget(QLabel(reg_info.get("after", ""), styleSheet="color: #86EFAC; font-family: Consolas; font-weight: bold; font-size: 9pt;"), 2, 1)

                ex_lay.addWidget(reg_frame)

            self.right_layout.addWidget(ex_card)

        # ----------------------------------------------------------------------
        # 6. Practical Application Card
        # ----------------------------------------------------------------------
        if topic.get("practical_application"):
            app_card = QFrame()
            app_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
            ap_lay = QVBoxLayout(app_card)
            ap_lay.setSpacing(6)

            ap_title = QLabel("🏢 REAL-WORLD INDUSTRIAL & EMBEDDED APPLICATION")
            ap_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #8B5CF6; font-family: Consolas;")
            ap_lay.addWidget(ap_title)

            ap_txt = QLabel(topic.get("practical_application", ""))
            ap_txt.setWordWrap(True)
            ap_txt.setStyleSheet("color: #E2E8F0; font-size: 9.5pt;")
            ap_lay.addWidget(ap_txt)

            self.right_layout.addWidget(app_card)

        # ----------------------------------------------------------------------
        # 7. "Try It" Action Button
        # ----------------------------------------------------------------------
        if topic.get("try_it"):
            try_card = QFrame()
            try_card.setStyleSheet("QFrame { background-color: #111C35; border: 1px solid #2563EB; border-radius: 8px; padding: 12px; }")
            t_lay = QHBoxLayout(try_card)
            
            t_txt = QLabel(f"🚀 {topic.get('try_it', '')}")
            t_txt.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 9pt;")
            t_lay.addWidget(t_txt, 1)

            btn_try = QPushButton("⚡ Launch Simulator")
            btn_try.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_try.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 14px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover { background-color: #1D4ED8; }
            """)
            btn_try.clicked.connect(self.jump_to_simulator)
            t_lay.addWidget(btn_try)

            self.right_layout.addWidget(try_card)

        # ----------------------------------------------------------------------
        # 8. Interactive Quick Quiz / Check Question
        # ----------------------------------------------------------------------
        if topic.get("quiz"):
            quiz_data = topic["quiz"]
            q_card = QFrame()
            q_card.setStyleSheet("QFrame { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; }")
            q_lay = QVBoxLayout(q_card)
            q_lay.setSpacing(10)

            q_title = QLabel("❓ QUICK KNOWLEDGE CHECK")
            q_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #EC4899; font-family: Consolas;")
            q_lay.addWidget(q_title)

            q_txt = QLabel(quiz_data.get("question", ""))
            q_txt.setWordWrap(True)
            q_txt.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #F8FAFC;")
            q_lay.addWidget(q_txt)

            btn_group = QButtonGroup(q_card)
            rad_btns = []
            for o_idx, opt in enumerate(quiz_data.get("options", [])):
                rad = QRadioButton(opt)
                rad.setStyleSheet("QRadioButton { color: #CBD5E1; font-size: 9pt; padding: 2px; } QRadioButton:hover { color: #F8FAFC; }")
                btn_group.addButton(rad, o_idx)
                rad_btns.append(rad)
                q_lay.addWidget(rad)

            lbl_feedback = QLabel("")
            lbl_feedback.setWordWrap(True)
            lbl_feedback.setStyleSheet("font-size: 9pt; font-weight: bold; margin-top: 4px;")
            lbl_feedback.setVisible(False)
            q_lay.addWidget(lbl_feedback)

            btn_check = QPushButton("Check Answer")
            btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_check.setStyleSheet("background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 4px; padding: 5px 12px; font-weight: bold; font-size: 8.5pt;")

            def verify_answer():
                sel_id = btn_group.checkedId()
                if sel_id == -1:
                    lbl_feedback.setText("⚠️ Please select an option first.")
                    lbl_feedback.setStyleSheet("color: #F59E0B; font-weight: bold;")
                    lbl_feedback.setVisible(True)
                    return
                
                correct_idx = quiz_data.get("correct", 0)
                exp = quiz_data.get("explanation", "")
                if sel_id == correct_idx:
                    lbl_feedback.setText(f"✔ CORRECT! {exp}")
                    lbl_feedback.setStyleSheet("color: #10B981; font-weight: bold;")
                else:
                    lbl_feedback.setText(f"✖ INCORRECT. {exp}")
                    lbl_feedback.setStyleSheet("color: #EF4444; font-weight: bold;")
                lbl_feedback.setVisible(True)

            btn_check.clicked.connect(verify_answer)
            q_lay.addWidget(btn_check)

            self.right_layout.addWidget(q_card)

        # ----------------------------------------------------------------------
        # 9. Next / Previous Navigation Bar
        # ----------------------------------------------------------------------
        nav_bar = QHBoxLayout()
        nav_bar.setContentsMargins(0, 10, 0, 0)

        btn_prev = QPushButton("← Previous Topic")
        btn_prev.setEnabled(self.current_topic_idx > 0)
        btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155;
                border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 9pt;
            }
            QPushButton:disabled { opacity: 0.4; }
            QPushButton:hover:!disabled { background-color: #334155; }
        """)
        btn_prev.clicked.connect(lambda: self.load_topic_by_index(self.current_topic_idx - 1))
        nav_bar.addWidget(btn_prev)

        nav_bar.addStretch()

        lbl_idx = QLabel(f"Topic {self.current_topic_idx + 1} of {len(self.flat_topics_list)}")
        lbl_idx.setStyleSheet("color: #94A3B8; font-size: 9pt; font-weight: bold;")
        nav_bar.addWidget(lbl_idx)

        nav_bar.addStretch()

        btn_next = QPushButton("Next Topic →")
        btn_next.setEnabled(self.current_topic_idx < len(self.flat_topics_list) - 1)
        btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_next.setStyleSheet("""
            QPushButton {
                background-color: #F97316; color: #FFFFFF; border: none;
                border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 9pt;
            }
            QPushButton:disabled { opacity: 0.4; }
            QPushButton:hover:!disabled { background-color: #EA580C; }
        """)
        btn_next.clicked.connect(lambda: self.load_topic_by_index(self.current_topic_idx + 1))
        nav_bar.addWidget(btn_next)

        self.right_layout.addLayout(nav_bar)

    # --------------------------------------------------------------------------
    # Helper Actions
    # --------------------------------------------------------------------------

    def toggle_completion(self, t_id):
        if t_id in self.completed_topics:
            self.completed_topics.remove(t_id)
        else:
            self.completed_topics.add(t_id)
        
        self.update_progress()
        self.populate_tree()

    def toggle_bookmark(self, t_id):
        if t_id in self.bookmarked_topics:
            self.bookmarked_topics.remove(t_id)
        else:
            self.bookmarked_topics.add(t_id)

        self.btn_filter_bm.setText(f" ★ Bookmarks ({len(self.bookmarked_topics)})")
        self.populate_tree()

    def update_progress(self):
        tot = len(self.flat_topics_list)
        done = len(self.completed_topics)
        pct = int((done / tot) * 100) if tot > 0 else 0
        self.lbl_progress.setText(f"Progress: {done} / {tot} Topics ({pct}%)")
        self.prog_bar.setValue(done)

    def jump_to_simulator(self):
        if self.hub_view and hasattr(self.hub_view, "main_tabs"):
            # Jump to Tab 2 (Interactive Simulation)
            self.hub_view.main_tabs.setCurrentIndex(2)
