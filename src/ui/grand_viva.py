import os
import json
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QSplitter, QPushButton, QGridLayout, QSizePolicy, QProgressBar,
    QComboBox, QListWidget, QListWidgetItem, QStackedWidget, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QColor, QFont, QCursor
import qtawesome as qta
from src.core.logger import log
from src.core.config import config_manager

SUBJECT_FILES = {
    "basic_electronics": "basic_electronics.json",
    "electronic_devices": "electronic_devices.json",
    "analog_electronics": "analog_electronics.json",
    "digital_electronics": "digital_electronics.json",
    "signals_systems": "signals_systems.json",
    "network_theory": "network_theory.json",
    "electromagnetic_theory": "electromagnetic_theory.json",
    "analog_communication": "analog_communication.json",
    "digital_communication": "digital_communication.json",
    "microprocessors_microcontrollers": "microprocessors_microcontrollers.json",
    "control_systems": "control_systems.json",
    "vlsi": "vlsi.json",
    "embedded_systems": "embedded_systems.json",
    "dsp": "dsp.json",
    "iot": "iot.json",
    "computer_networks": "computer_networks.json",
    "engineering_mathematics": "engineering_mathematics.json",
    "data_structures_algorithms": "data_structures_algorithms.json",
    "design_analysis_algorithms": "design_analysis_algorithms.json",
    "oop": "oop.json",
    "operating_systems": "operating_systems.json",
    "nano_electronics": "nano_electronics.json"
}

SUBJECT_NAMES = {
    "basic_electronics": "Basic Electronics",
    "electronic_devices": "Electronic Devices & Circuits",
    "analog_electronics": "Analog Electronics",
    "digital_electronics": "Digital Electronics",
    "signals_systems": "Signals & Systems",
    "network_theory": "Network Theory",
    "electromagnetic_theory": "Electromagnetic Theory",
    "analog_communication": "Analog Communication",
    "digital_communication": "Digital Communication",
    "microprocessors_microcontrollers": "Microprocessors & Microcontrollers",
    "control_systems": "Control Systems",
    "vlsi": "VLSI",
    "embedded_systems": "Embedded Systems",
    "dsp": "Digital Signal Processing (DSP)",
    "iot": "Internet of Things (IoT)",
    "computer_networks": "Computer Networks",
    "engineering_mathematics": "Engineering Mathematics",
    "data_structures_algorithms": "Data Structures & Algorithms",
    "design_analysis_algorithms": "Design & Analysis of Algorithms",
    "oop": "Object-Oriented Programming",
    "operating_systems": "Operating Systems",
    "nano_electronics": "Nano Electronics"
}

class GrandVivaView(QWidget):
    """Redesigned Professional Grand Viva and Core Technical Interview Preparation View."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing GrandVivaView")
        
        # Load local question database
        self.load_database()
        
        # Load progress state
        self.load_progress()
        
        # Main Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Left Panel (Sidebar Navigation)
        self.setup_left_sidebar()
        
        # Right Panel Stacked Area
        self.setup_right_content_area()
        
        # Splitter wrapper
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_stack)
        self.splitter.setSizes([260, 740])
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #1e293b; }")
        
        self.main_layout.addWidget(self.splitter)
        
        # Show Dashboard Initially
        self.show_dashboard()

    def load_database(self):
        """Loads all subject JSON databases."""
        self.db = {}
        data_dir = r"c:\Users\hp\OneDrive\Desktop\FOSSE\src\data\grand_viva"
        for sub_key, filename in SUBJECT_FILES.items():
            path = os.path.join(data_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        self.db[sub_key] = json.load(f)
                except Exception as e:
                    log.error(f"Error loading {path}: {e}")
                    self.db[sub_key] = []
            else:
                self.db[sub_key] = []

    def load_progress(self):
        """Loads progress variables from configurations."""
        self.progress = config_manager.get("viva_progress") or {
            "attempted_questions": [],
            "correct_questions": [],
            "favorites": [],
            "recently_practiced": [],
            "weak_subjects": []
        }

    def save_progress(self):
        """Saves current progress back to config file."""
        config_manager.set("viva_progress", self.progress)

    def setup_left_sidebar(self):
        """Creates the left panel for trees and shortcuts."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar-panel")
        self.sidebar.setStyleSheet("""
            QFrame#sidebar-panel {
                background-color: #111827;
                border-right: 1px solid #26334D;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(12)
        
        # Search Box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Questions...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                border: 1.5px solid #1e293b;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f8fafc;
                font-size: 9.5pt;
            }
            QLineEdit:focus {
                border-color: #06b6d4;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        sidebar_layout.addWidget(self.search_input)
        
        # Title Label for subjects
        sub_lbl = QLabel("SUBJECTS LIST")
        sub_lbl.setStyleSheet("color: #64748b; font-size: 8pt; font-weight: bold; letter-spacing: 1px;")
        sidebar_layout.addWidget(sub_lbl)
        
        # Subject tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(10)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #e2e8f0;
                font-size: 9.5pt;
            }
            QTreeWidget::item {
                padding: 6px 4px;
            }
            QTreeWidget::item:hover {
                background-color: #1e293b;
                color: #06b6d4;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #1e293b;
                color: #06b6d4;
                font-weight: bold;
            }
        """)
        
        # Build tree items
        self.tree_items = {}
        for sub_key, sub_name in SUBJECT_NAMES.items():
            item = QTreeWidgetItem([sub_name])
            item.setData(0, Qt.ItemDataRole.UserRole, sub_key)
            self.tree_widget.addTopLevelItem(item)
            self.tree_items[sub_key] = item
            
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        sidebar_layout.addWidget(self.tree_widget)
        
        # Navigation Shortcut Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(6)
        
        # Dashboard Button
        self.dash_btn = QPushButton("  Dashboard Workspace")
        self.dash_btn.setIcon(qta.icon("fa5s.th-large", color="#06b6d4"))
        self.dash_btn.setStyleSheet(self.get_sidebar_btn_style())
        self.dash_btn.clicked.connect(self.show_dashboard)
        btn_layout.addWidget(self.dash_btn)
        
        # Mock Grand Viva Button
        self.mock_btn = QPushButton("  Mock Grand Viva")
        self.mock_btn.setIcon(qta.icon("fa5s.clipboard-check", color="#ffffff"))
        self.mock_btn.setStyleSheet(self.get_sidebar_btn_style())
        self.mock_btn.clicked.connect(lambda: self.show_mock_config())
        btn_layout.addWidget(self.mock_btn)
        
        # Rapid Fire Button
        self.rapid_btn = QPushButton("  Rapid Fire Revision")
        self.rapid_btn.setIcon(qta.icon("fa5s.bolt", color="#ffffff"))
        self.rapid_btn.setStyleSheet(self.get_sidebar_btn_style())
        self.rapid_btn.clicked.connect(self.start_rapid_fire)
        btn_layout.addWidget(self.rapid_btn)
        
        # Favorites List Button
        self.favs_btn = QPushButton("  Favorite Bookmarks")
        self.favs_btn.setIcon(qta.icon("fa5s.star", color="#f59e0b"))
        self.favs_btn.setStyleSheet(self.get_sidebar_btn_style())
        self.favs_btn.clicked.connect(self.show_favorites)
        btn_layout.addWidget(self.favs_btn)
        
        sidebar_layout.addLayout(btn_layout)

    def get_sidebar_btn_style(self):
        return """
            QPushButton {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 9px 12px;
                font-weight: bold;
                font-size: 9.5pt;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1e293b;
                border-color: #06b6d4;
            }
        """

    def setup_right_content_area(self):
        """Sets up the stacked widget space on the right panel."""
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #0f172a;")
        
        # 1. Dashboard View
        self.setup_dashboard_ui()
        
        # 2. Practice/Question List View
        self.setup_practice_ui()
        
        # 3. Question Detail Viewer View
        self.setup_viewer_ui()
        
        # 4. Mock Viva View
        self.setup_mock_ui()
        
        # 5. Rapid Fire View
        self.setup_rapid_ui()
        
        # 6. Favorites List View
        self.setup_favorites_ui()
        
        # Add Views to stack
        self.content_stack.addWidget(self.dash_scroll)      # 0
        self.content_stack.addWidget(self.practice_panel)  # 1
        self.content_stack.addWidget(self.viewer_panel)    # 2
        self.content_stack.addWidget(self.mock_panel)      # 3
        self.content_stack.addWidget(self.rapid_panel)     # 4
        self.content_stack.addWidget(self.favorites_panel) # 5

    def setup_dashboard_ui(self):
        """Creates the Dashboard UI Workspace panel."""
        self.dash_scroll = QScrollArea()
        self.dash_scroll.setWidgetResizable(True)
        self.dash_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        dash_widget = QWidget()
        dash_widget.setStyleSheet("background-color: #0b0f19;")
        dash_layout = QVBoxLayout(dash_widget)
        dash_layout.setContentsMargins(20, 20, 20, 20)
        dash_layout.setSpacing(15)
        
        # Banner Header
        banner = QFrame()
        banner.setObjectName("viva-banner")
        banner.setStyleSheet("""
            QFrame#viva-banner {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-left: 5px solid #06b6d4;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        banner_lay = QHBoxLayout(banner)
        logo_lbl = QLabel("🎓")
        logo_lbl.setStyleSheet("font-size: 24pt;")
        banner_lay.addWidget(logo_lbl)
        
        text_lay = QVBoxLayout()
        title = QLabel("Grand Viva & Core Technical Interview Prep")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f8fafc;")
        desc = QLabel("Comprehensive oral examination simulator, rapid-fire reviewer, and core engineering interview hub.")
        desc.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
        text_lay.addWidget(title)
        text_lay.addWidget(desc)
        banner_lay.addLayout(text_lay)
        banner_lay.addStretch()
        
        dash_layout.addWidget(banner)
        
        # Stats Cards Grid
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(12)
        dash_layout.addLayout(self.stats_layout)
        
        # Quick Buttons Grid Section
        qb_lbl = QLabel("EXAMINATION WORKSPACES")
        qb_lbl.setStyleSheet("color: #06b6d4; font-size: 9pt; font-weight: bold; letter-spacing: 0.5px; margin-top: 10px;")
        dash_layout.addWidget(qb_lbl)
        
        qb_grid = QGridLayout()
        qb_grid.setSpacing(15)
        
        launchers = [
            ("Subject-wise Practice", "Browse questions sorted by ECE engineering topics.", "fa5s.book-open", lambda: self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0)) or self.on_tree_item_clicked(self.tree_widget.topLevelItem(0))),
            ("Random Grand Viva", "Generate a random mix of questions across all subjects.", "fa5s.random", lambda: self.start_mock_viva(30)),
            ("Core Technical Interview", "Prepare with top conceptual questions asked in ISRO, DRDO, BEL, etc.", "fa5s.briefcase", self.show_core_interview_panel),
            ("Rapid Fire Revision", "30 random fast-paced conceptual flashcard questions.", "fa5s.bolt", self.start_rapid_fire),
            ("Mock Grand Viva Simulator", "Interactive oral board exam simulator with score metrics.", "fa5s.clipboard-list", self.show_mock_config),
            ("Favorite Questions", "Revise and practice bookmarked questions.", "fa5s.star", self.show_favorites)
        ]
        
        for i, (name, d, icon, slot) in enumerate(launchers):
            card = QFrame()
            card.setObjectName("qb-card")
            card.setStyleSheet("""
                QFrame#qb-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
                QFrame#qb-card:hover {
                    border-color: #06b6d4;
                    background-color: #1e293b;
                }
            """)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Simple custom click connector
            def make_click(callback):
                return lambda event: callback()
            card.mousePressEvent = make_click(slot)
            
            c_lay = QHBoxLayout(card)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon, color="#06b6d4").pixmap(24, 24))
            c_lay.addWidget(icon_lbl)
            
            txt_lay = QVBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10.5pt;")
            d_lbl = QLabel(d)
            d_lbl.setStyleSheet("color: #94a3b8; font-size: 8.5pt;")
            d_lbl.setWordWrap(True)
            txt_lay.addWidget(n_lbl)
            txt_lay.addWidget(d_lbl)
            c_lay.addLayout(txt_lay)
            
            qb_grid.addWidget(card, i // 2, i % 2)
            
        dash_layout.addLayout(qb_grid)
        
        # Local Module Progress Section
        prg_lbl = QLabel("YOUR PROGRESS METRICS")
        prg_lbl.setStyleSheet("color: #06b6d4; font-size: 9pt; font-weight: bold; letter-spacing: 0.5px; margin-top: 10px;")
        dash_layout.addWidget(prg_lbl)
        
        self.progress_panel = QFrame()
        self.progress_panel.setObjectName("progress-panel")
        self.progress_panel.setStyleSheet("""
            QFrame#progress-panel {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.prg_layout = QGridLayout(self.progress_panel)
        self.prg_layout.setSpacing(15)
        
        dash_layout.addWidget(self.progress_panel)
        dash_layout.addStretch()
        
        self.dash_scroll.setWidget(dash_widget)

    def refresh_dashboard(self):
        """Calculates stats metrics and updates the Dashboard Workspace."""
        # Calculate statistics
        tot_subjects = len(self.db.keys())
        tot_questions = sum(len(q) for q in self.db.values())
        
        beg_count = 0
        int_count = 0
        adv_count = 0
        for sub_qs in self.db.values():
            for q in sub_qs:
                diff = q.get("difficulty", "Beginner")
                if diff == "Beginner":
                    beg_count += 1
                elif diff == "Intermediate":
                    int_count += 1
                else:
                    adv_count += 1
                    
        fav_count = len(self.progress["favorites"])
        attempted = len(self.progress["attempted_questions"])
        correct = len(self.progress["correct_questions"])
        
        # Update Stats layouts
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        stats = [
            ("Total Subjects", f"{tot_subjects} Subjects", "fa5s.university", "#06b6d4"),
            ("Total Questions", f"{tot_questions} Questions", "fa5s.database", "#3b82f6"),
            ("Beginner Level", f"{beg_count} Qs (40%)", "fa5s.smile", "#10b981"),
            ("Intermediate Level", f"{int_count} Qs (35%)", "fa5s.meh", "#f59e0b"),
            ("Advanced Level", f"{adv_count} Qs (25%)", "fa5s.frown", "#ef4444"),
            ("Starred Questions", f"{fav_count} Saved", "fa5s.star", "#eab308")
        ]
        
        for index, (k, v, icon, col) in enumerate(stats):
            col_idx = index % 3
            row_idx = index // 3
            
            card = QFrame()
            card.setStyleSheet(f"background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px;")
            lay = QHBoxLayout(card)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon, color=col).pixmap(20, 20))
            lay.addWidget(icon_lbl)
            
            txt_lay = QVBoxLayout()
            k_lbl = QLabel(k)
            k_lbl.setStyleSheet("color: #64748b; font-size: 7.5pt; text-transform: uppercase; font-weight: bold;")
            v_lbl = QLabel(v)
            v_lbl.setStyleSheet("color: #f8fafc; font-size: 11pt; font-weight: bold;")
            txt_lay.addWidget(k_lbl)
            txt_lay.addWidget(v_lbl)
            lay.addLayout(txt_lay)
            
            self.stats_layout.addWidget(card, row_idx, col_idx)
            
        # Update Progress Tracker layout
        while self.prg_layout.count():
            child = self.prg_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Subjects completed count
        completed_subs = 0
        weak_subs = []
        
        for sub_key, sub_qs in self.db.items():
            if not sub_qs:
                continue
            attempted_sub_qs = [q["id"] for q in sub_qs if q["id"] in self.progress["attempted_questions"]]
            if len(attempted_sub_qs) >= len(sub_qs):
                completed_subs += 1
                
            # If attempted > 10 and correct answer rate < 60%, mark as weak
            sub_correct = [q["id"] for q in sub_qs if q["id"] in self.progress["correct_questions"]]
            if len(attempted_sub_qs) >= 5:
                rate = len(sub_correct) / len(attempted_sub_qs)
                if rate < 0.6:
                    weak_subs.append(SUBJECT_NAMES[sub_key])
                    
        # Update weak subjects list in progress
        self.progress["weak_subjects"] = weak_subs
        self.save_progress()
        
        # Display progress info
        att_bar = QProgressBar()
        att_bar.setValue(min(100, int((attempted / max(1, tot_questions)) * 100)))
        att_bar.setStyleSheet("QProgressBar { background-color: #1e293b; border-radius: 3px; text-align: center; color: white; } QProgressBar::chunk { background-color: #06b6d4; }")
        
        succ_rate = 0
        if attempted > 0:
            succ_rate = int((correct / attempted) * 100)
            
        rate_bar = QProgressBar()
        rate_bar.setValue(succ_rate)
        rate_bar.setStyleSheet("QProgressBar { background-color: #1e293b; border-radius: 3px; text-align: center; color: white; } QProgressBar::chunk { background-color: #10b981; }")
        
        self.prg_layout.addWidget(QLabel("Viva Questions Attempted:"), 0, 0)
        self.prg_layout.addWidget(att_bar, 0, 1)
        self.prg_layout.addWidget(QLabel(f"{attempted} / {tot_questions}"), 0, 2)
        
        self.prg_layout.addWidget(QLabel("Correct Answers Rate:"), 1, 0)
        self.prg_layout.addWidget(rate_bar, 1, 1)
        self.prg_layout.addWidget(QLabel(f"{succ_rate}% Accuracy"), 1, 2)
        
        weak_str = ", ".join(weak_subs[:3]) if weak_subs else "None! Excellent performance."
        weak_lbl = QLabel(f"Weak Subjects: {weak_str}")
        weak_lbl.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 9.5pt;")
        self.prg_layout.addWidget(weak_lbl, 2, 0, 1, 3)
        
        comp_lbl = QLabel(f"Subjects Fully Practiced: {completed_subs} / {tot_subjects}")
        comp_lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 9.5pt;")
        self.prg_layout.addWidget(comp_lbl, 3, 0, 1, 3)

    def setup_practice_ui(self):
        """Creates the Subject Practice QList panel."""
        self.practice_panel = QFrame()
        layout = QVBoxLayout(self.practice_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.sub_title_lbl = QLabel("Subject Practice Workspace")
        self.sub_title_lbl.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f8fafc;")
        layout.addWidget(self.sub_title_lbl)
        
        self.practice_list = QListWidget()
        self.practice_list.setStyleSheet("""
            QListWidget {
                background-color: #0b0f19;
                border: 1px solid #1e293b;
                border-radius: 6px;
                color: #e2e8f0;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:hover {
                background-color: #1e293b;
                color: #06b6d4;
            }
        """)
        self.practice_list.itemClicked.connect(self.on_practice_item_clicked)
        layout.addWidget(self.practice_list)
        
        # Back to Dashboard button
        back_btn = QPushButton(" Back to Dashboard")
        back_btn.setIcon(qta.icon("fa5s.arrow-left", color="#ffffff"))
        back_btn.setStyleSheet(self.get_sidebar_btn_style())
        back_btn.clicked.connect(self.show_dashboard)
        layout.addWidget(back_btn)

    def setup_viewer_ui(self):
        """Creates the Question Detail Viewer layout panel."""
        self.viewer_panel = QFrame()
        self.viewer_scroll = QScrollArea(self.viewer_panel)
        self.viewer_scroll.setWidgetResizable(True)
        self.viewer_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        v_widget = QWidget()
        v_widget.setStyleSheet("background-color: #0f172a;")
        v_layout = QVBoxLayout(v_widget)
        v_layout.setContentsMargins(20, 20, 20, 20)
        v_layout.setSpacing(12)
        
        # Header Row (Question ID, Difficulty, Company Tag, Favorite Star)
        hdr_lay = QHBoxLayout()
        
        self.v_diff_lbl = QLabel("Difficulty")
        self.v_diff_lbl.setStyleSheet("border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 8pt;")
        hdr_lay.addWidget(self.v_diff_lbl)
        
        self.v_comp_lbl = QLabel("Company Tag")
        self.v_comp_lbl.setStyleSheet("background-color: #3b82f622; color: #3b82f6; border: 1px solid #3b82f6; border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 8pt;")
        hdr_lay.addWidget(self.v_comp_lbl)
        
        hdr_lay.addStretch()
        
        # Favorite Toggle Button
        self.v_fav_btn = QPushButton()
        self.v_fav_btn.setFixedSize(30, 30)
        self.v_fav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.v_fav_btn.setStyleSheet("border: none; background: transparent;")
        self.v_fav_btn.clicked.connect(lambda: self.toggle_favorite_question(getattr(self, "current_question", None)))
        hdr_lay.addWidget(self.v_fav_btn)
        
        v_layout.addLayout(hdr_lay)
        
        # Question Text Card
        q_card = QFrame()
        q_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px;")
        q_lay = QVBoxLayout(q_card)
        self.v_question_lbl = QLabel("Question")
        self.v_question_lbl.setStyleSheet("font-size: 13pt; font-weight: bold; color: #FFFFFF;")
        self.v_question_lbl.setWordWrap(True)
        self.v_question_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        q_lay.addWidget(self.v_question_lbl)
        v_layout.addWidget(q_card)
        
        # Expected Answer Panel (Hidden initially)
        self.ans_card = QFrame()
        self.ans_card.setStyleSheet("background-color: #141B2D; border: 1px solid #22C55E; border-radius: 10px; padding: 15px;")
        ans_lay = QVBoxLayout(self.ans_card)
        ans_hdr = QLabel("EXPECTED ANSWER")
        ans_hdr.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 8pt; text-transform: uppercase;")
        self.v_expected_lbl = QLabel("Answer content goes here.")
        self.v_expected_lbl.setStyleSheet("color: #C9D1E3; font-size: 10.5pt; font-weight: 500;")
        self.v_expected_lbl.setWordWrap(True)
        self.v_expected_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        ans_lay.addWidget(ans_hdr)
        ans_lay.addWidget(self.v_expected_lbl)
        v_layout.addWidget(self.ans_card)
        
        # Detailed Explanation Panel
        exp_card = QFrame()
        exp_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px;")
        exp_lay = QVBoxLayout(exp_card)
        exp_hdr = QLabel("DETAILED ENGINEERING EXPLANATION")
        exp_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 8pt; text-transform: uppercase;")
        self.v_explanation_lbl = QLabel("Explanation goes here.")
        self.v_explanation_lbl.setStyleSheet("color: #C9D1E3; font-size: 10pt; line-height: 1.45;")
        self.v_explanation_lbl.setWordWrap(True)
        self.v_explanation_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        exp_lay.addWidget(exp_hdr)
        exp_lay.addWidget(self.v_explanation_lbl)
        v_layout.addWidget(exp_card)
        
        # Formula Card (if applicable)
        self.formula_card = QFrame()
        self.formula_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px;")
        form_lay = QVBoxLayout(self.formula_card)
        form_hdr = QLabel("GOVERNING EQUATIONS & VARIABLES")
        form_hdr.setStyleSheet("color: #C9D1E3; font-weight: bold; font-size: 8pt;")
        self.v_formula_lbl = QLabel("Formula")
        self.v_formula_lbl.setStyleSheet("color: #06B6D4; font-size: 11pt; font-weight: bold; margin-top: 5px;")
        self.v_formula_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        self.v_vars_lbl = QLabel("Variables")
        self.v_vars_lbl.setStyleSheet("color: #94A3B8; font-size: 9pt;")
        self.v_vars_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        form_lay.addWidget(form_hdr)
        form_lay.addWidget(self.v_formula_lbl)
        form_lay.addWidget(self.v_vars_lbl)
        v_layout.addWidget(self.formula_card)
        
        # Memorization Shortcut Card (How to Remember)
        self.memo_card = QFrame()
        self.memo_card.setStyleSheet("background-color: #141B2D; border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px;")
        m_lay = QVBoxLayout(self.memo_card)
        m_hdr = QLabel("🧠 INSTANT MEMORIZATION TRICK (HOW TO REMEMBER)")
        m_hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 8.5pt;")
        self.v_memo_lbl = QLabel("Memory Shortcut")
        self.v_memo_lbl.setStyleSheet("color: #FFFFFF; font-size: 10.5pt; font-weight: bold;")
        self.v_memo_lbl.setWordWrap(True)
        self.v_memo_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        m_lay.addWidget(m_hdr)
        m_lay.addWidget(self.v_memo_lbl)
        v_layout.addWidget(self.memo_card)
        
        # Interview Tip & Estimation Box
        tip_card = QFrame()
        tip_card.setStyleSheet("background-color: #0b0f19; border: 1px solid #eab308; border-radius: 6px; padding: 12px;")
        t_lay = QVBoxLayout(tip_card)
        t_hdr = QLabel("💡 ORAL BOARD INTERVIEW TIP")
        t_hdr.setStyleSheet("color: #eab308; font-weight: bold; font-size: 8pt;")
        self.v_tip_lbl = QLabel("Tip")
        self.v_tip_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt;")
        self.v_tip_lbl.setWordWrap(True)
        self.v_tip_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        t_lay.addWidget(t_hdr)
        t_lay.addWidget(self.v_tip_lbl)
        v_layout.addWidget(tip_card)
        
        # Evaluation Actions (Mark Correct/Incorrect, Reveal expected answer)
        self.eval_panel = QFrame()
        self.eval_panel.setStyleSheet("background-color: transparent;")
        eval_lay = QHBoxLayout(self.eval_panel)
        eval_lay.setContentsMargins(0, 0, 0, 0)
        
        self.reveal_btn = QPushButton("Reveal Expected Answer")
        self.reveal_btn.setStyleSheet("""
            QPushButton {
                background-color: #06b6d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #0891b2;
            }
        """)
        self.reveal_btn.clicked.connect(self.reveal_expected_answer)
        eval_lay.addWidget(self.reveal_btn)
        
        self.correct_btn = QPushButton("✓ Answered Correctly")
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.correct_btn.clicked.connect(lambda: self.evaluate_practice_question(True))
        
        self.wrong_btn = QPushButton("✗ Answered Incorrectly")
        self.wrong_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.wrong_btn.clicked.connect(lambda: self.evaluate_practice_question(False))
        
        eval_lay.addWidget(self.correct_btn)
        eval_lay.addWidget(self.wrong_btn)
        v_layout.addWidget(self.eval_panel)
        
        # Cross Links panel
        self.links_panel = QFrame()
        self.links_panel.setStyleSheet("background-color: transparent;")
        self.links_lay = QHBoxLayout(self.links_panel)
        self.links_lay.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(self.links_panel)
        
        v_scroll_lay = QVBoxLayout(self.viewer_panel)
        v_scroll_lay.setContentsMargins(0, 0, 0, 0)
        v_scroll_lay.addWidget(self.viewer_scroll)
        self.viewer_scroll.setWidget(v_widget)
        
        # Navigation bar
        self.nav_bar = QHBoxLayout()
        self.prev_q_btn = QPushButton("Previous Question")
        self.prev_q_btn.clicked.connect(self.load_prev_question)
        self.next_q_btn = QPushButton("Next Question")
        self.next_q_btn.clicked.connect(self.load_next_question)
        self.nav_bar.addWidget(self.prev_q_btn)
        self.nav_bar.addStretch()
        self.nav_bar.addWidget(self.next_q_btn)
        v_layout.addLayout(self.nav_bar)

    def setup_mock_ui(self):
        """Creates the Mock Grand Viva workspace simulator."""
        self.mock_panel = QFrame()
        layout = QVBoxLayout(self.mock_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.mock_title = QLabel("Mock Grand Viva Board Simulator")
        self.mock_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f8fafc;")
        layout.addWidget(self.mock_title)
        
        # Config state vs Running state
        self.mock_stack = QStackedWidget()
        
        # Config Screen
        self.config_widget = QWidget()
        cw_lay = QVBoxLayout(self.config_widget)
        cw_lay.setSpacing(12)
        
        info = QLabel("Simulate a professional academic oral board examination. Select the count of viva questions to draw randomly from all subjects:")
        info.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        info.setWordWrap(True)
        cw_lay.addWidget(info)
        
        self.mock_size_cmb = QComboBox()
        self.mock_size_cmb.addItems(["10 Questions", "20 Questions", "30 Questions", "50 Questions", "100 Questions"])
        self.mock_size_cmb.setStyleSheet("""
            QComboBox {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 6px;
                color: #e2e8f0;
                font-size: 10pt;
            }
        """)
        cw_lay.addWidget(self.mock_size_cmb)
        
        start_btn = QPushButton("Start Mock Viva Board")
        start_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        start_btn.clicked.connect(self.initiate_mock_session)
        cw_lay.addWidget(start_btn)
        cw_lay.addStretch()
        
        # Running Screen
        self.running_widget = QWidget()
        rw_lay = QVBoxLayout(self.running_widget)
        rw_lay.setSpacing(12)
        
        self.mock_progress = QProgressBar()
        self.mock_progress.setStyleSheet("QProgressBar { background-color: #1e293b; border-radius: 3px; text-align: center; color: white; } QProgressBar::chunk { background-color: #06b6d4; }")
        rw_lay.addWidget(self.mock_progress)
        
        # Embed similar structures as the viewer UI inside the runner
        self.mock_question_box = QLabel("Question content goes here.")
        self.mock_question_box.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; background-color: #111827; padding: 15px; border-radius: 6px;")
        self.mock_question_box.setWordWrap(True)
        self.mock_question_box.setTextFormat(Qt.TextFormat.MarkdownText)
        rw_lay.addWidget(self.mock_question_box)
        
        self.mock_reveal_btn = QPushButton("Reveal Expected Answer")
        self.mock_reveal_btn.clicked.connect(self.reveal_mock_answer)
        rw_lay.addWidget(self.mock_reveal_btn)
        
        self.mock_answer_box = QLabel("Answer goes here.")
        self.mock_answer_box.setStyleSheet("font-size: 10.5pt; color: #e2e8f0; background-color: #0b0f19; border: 1px solid #10b981; padding: 15px; border-radius: 6px;")
        self.mock_answer_box.setWordWrap(True)
        self.mock_answer_box.setTextFormat(Qt.TextFormat.MarkdownText)
        rw_lay.addWidget(self.mock_answer_box)
        
        # Mark Buttons
        self.mock_eval_widget = QWidget()
        me_lay = QHBoxLayout(self.mock_eval_widget)
        me_lay.setContentsMargins(0, 0, 0, 0)
        
        self.mock_correct_btn = QPushButton("✓ Answered Correctly")
        self.mock_correct_btn.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.mock_correct_btn.clicked.connect(lambda: self.evaluate_mock_question(True))
        
        self.mock_wrong_btn = QPushButton("✗ Answered Incorrectly")
        self.mock_wrong_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.mock_wrong_btn.clicked.connect(lambda: self.evaluate_mock_question(False))
        
        me_lay.addWidget(self.mock_correct_btn)
        me_lay.addWidget(self.mock_wrong_btn)
        rw_lay.addWidget(self.mock_eval_widget)
        
        # Next/Prev buttons
        np_lay = QHBoxLayout()
        self.mock_prev_btn = QPushButton("Back")
        self.mock_prev_btn.clicked.connect(self.prev_mock_question)
        self.mock_next_btn = QPushButton("Next")
        self.mock_next_btn.clicked.connect(self.next_mock_question)
        np_lay.addWidget(self.mock_prev_btn)
        np_lay.addStretch()
        np_lay.addWidget(self.mock_next_btn)
        rw_lay.addLayout(np_lay)
        rw_lay.addStretch()
        
        # Results Screen
        self.results_widget = QWidget()
        res_lay = QVBoxLayout(self.results_widget)
        res_lay.setSpacing(15)
        
        self.results_score_lbl = QLabel("Score: N/A")
        self.results_score_lbl.setStyleSheet("font-size: 16pt; font-weight: bold; color: #10b981; text-align: center;")
        self.results_score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_lay.addWidget(self.results_score_lbl)
        
        self.results_summary_lbl = QLabel("")
        self.results_summary_lbl.setStyleSheet("font-size: 10.5pt; color: #94a3b8;")
        self.results_summary_lbl.setWordWrap(True)
        res_lay.addWidget(self.results_summary_lbl)
        
        finish_btn = QPushButton("Complete Simulation & Save Progress")
        finish_btn.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        finish_btn.clicked.connect(self.show_dashboard)
        res_lay.addWidget(finish_btn)
        res_lay.addStretch()
        
        # Add to local mock stack
        self.mock_stack.addWidget(self.config_widget)  # 0
        self.mock_stack.addWidget(self.running_widget) # 1
        self.mock_stack.addWidget(self.results_widget) # 2
        
        layout.addWidget(self.mock_stack)
        
        # Back to Dashboard button
        back_btn = QPushButton(" Exit Board Simulator")
        back_btn.setStyleSheet(self.get_sidebar_btn_style())
        back_btn.clicked.connect(self.show_dashboard)
        layout.addWidget(back_btn)

    def setup_rapid_ui(self):
        """Creates the Rapid Fire Revision panel."""
        self.rapid_panel = QFrame()
        layout = QVBoxLayout(self.rapid_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_hdr = QLabel("⚡ Rapid Fire Flashcard Review")
        title_hdr.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f8fafc;")
        layout.addWidget(title_hdr)
        
        self.rf_progress = QLabel("Question 1 of 30")
        self.rf_progress.setStyleSheet("color: #06b6d4; font-weight: bold;")
        layout.addWidget(self.rf_progress)
        
        self.rf_question_lbl = QLabel("Question text goes here.")
        self.rf_question_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; background-color: #111827; padding: 15px; border-radius: 6px;")
        self.rf_question_lbl.setWordWrap(True)
        self.rf_question_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        layout.addWidget(self.rf_question_lbl)
        
        self.rf_reveal_btn = QPushButton("Reveal Answer")
        self.rf_reveal_btn.clicked.connect(self.reveal_rapid_answer)
        layout.addWidget(self.rf_reveal_btn)
        
        self.rf_answer_lbl = QLabel("Expected Answer goes here.")
        self.rf_answer_lbl.setStyleSheet("font-size: 10.5pt; color: #e2e8f0; background-color: #0b0f19; border: 1px solid #10b981; padding: 15px; border-radius: 6px;")
        self.rf_answer_lbl.setWordWrap(True)
        self.rf_answer_lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        layout.addWidget(self.rf_answer_lbl)
        
        # Control Buttons
        ctrl_lay = QHBoxLayout()
        self.rf_prev_btn = QPushButton("Previous")
        self.rf_prev_btn.clicked.connect(self.prev_rapid_question)
        self.rf_next_btn = QPushButton("Next")
        self.rf_next_btn.clicked.connect(self.next_rapid_question)
        ctrl_lay.addWidget(self.rf_prev_btn)
        ctrl_lay.addStretch()
        ctrl_lay.addWidget(self.rf_next_btn)
        layout.addLayout(ctrl_lay)
        layout.addStretch()
        
        exit_btn = QPushButton(" Exit Rapid Fire")
        exit_btn.setStyleSheet(self.get_sidebar_btn_style())
        exit_btn.clicked.connect(self.show_dashboard)
        layout.addWidget(exit_btn)

    def setup_favorites_ui(self):
        """Creates the Bookmarked Favorites view panel."""
        self.favorites_panel = QFrame()
        layout = QVBoxLayout(self.favorites_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_lbl = QLabel("★ Starred Questions Library")
        title_lbl.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f8fafc;")
        layout.addWidget(title_lbl)
        
        self.fav_list_widget = QListWidget()
        self.fav_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #0b0f19;
                border: 1px solid #1e293b;
                border-radius: 6px;
                color: #e2e8f0;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:hover {
                background-color: #1e293b;
                color: #eab308;
            }
        """)
        self.fav_list_widget.itemClicked.connect(self.on_fav_item_clicked)
        layout.addWidget(self.fav_list_widget)
        
        back_btn = QPushButton(" Back to Dashboard")
        back_btn.setStyleSheet(self.get_sidebar_btn_style())
        back_btn.clicked.connect(self.show_dashboard)
        layout.addWidget(back_btn)

    def show_dashboard(self):
        self.refresh_dashboard()
        self.content_stack.setCurrentIndex(0)

    def on_tree_item_clicked(self, item):
        sub_key = item.data(0, Qt.ItemDataRole.UserRole)
        if sub_key and sub_key in self.db:
            self.current_subject = sub_key
            self.sub_title_lbl.setText(f"{SUBJECT_NAMES[sub_key]} — Question Practice")
            self.practice_list.clear()
            for index, q in enumerate(self.db[sub_key], 1):
                item_widget = QListWidgetItem(f"Q{index}: {q['question']}")
                item_widget.setData(Qt.ItemDataRole.UserRole, q)
                self.practice_list.addItem(item_widget)
            self.content_stack.setCurrentIndex(1)

    def on_practice_item_clicked(self, item_widget):
        q = item_widget.data(Qt.ItemDataRole.UserRole)
        if q:
            self.load_question_detail(q, self.db[self.current_subject])

    def get_formula_and_mnemonic(self, q):
        q_text = (q.get("question", "") + " " + q.get("reference_topic", "")).lower()
        
        # Digital Electronics & Logic
        if "demorgan" in q_text or "de morgan" in q_text:
            return (
                "$$\\overline{A \\cdot B} = \\bar{A} + \\bar{B}, \\quad \\overline{A + B} = \\bar{A} \\cdot \\bar{B}$$",
                "Where: $A, B$ are binary logic inputs.",
                "🧠 DeMorgan's Rule: 'Break the Bar, Change the Sign!' Split the top overline bar into two, and change AND (·) into OR (+), or OR (+) into AND (·)."
            )
        elif "and gate" in q_text or "7408" in q_text:
            return (
                "$$Y = A \\cdot B$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 AND is ALL! Output is 1 ONLY when ALL inputs are 1. If any input is 0, the output is ZERO."
            )
        elif "or gate" in q_text or "7432" in q_text:
            return (
                "$$Y = A + B$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 OR is ANY! Output is 1 if ANY input is 1. Output is ZERO ONLY when ALL inputs are 0."
            )
        elif "nand gate" in q_text or "7400" in q_text:
            return (
                "$$Y = \\overline{A \\cdot B}$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 NAND is NOT-AND! Calculate AND, then FLIP it! Output is 0 ONLY when ALL inputs are 1."
            )
        elif "nor gate" in q_text or "7402" in q_text:
            return (
                "$$Y = \\overline{A + B}$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 NOR is NOT-OR! Calculate OR, then FLIP it! Output is 1 ONLY when ALL inputs are 0."
            )
        elif "xor gate" in q_text or "7486" in q_text:
            return (
                "$$Y = A \\oplus B = A\\bar{B} + \\bar{A}B$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 XOR is DIFFERENT! Output is 1 ONLY when inputs are DIFFERENT (01 or 10)."
            )
        elif "xnor gate" in q_text or "74266" in q_text:
            return (
                "$$Y = A \\odot B = AB + \\bar{A}\\bar{B}$$",
                "Where: $A, B$ are inputs, $Y$ is output.",
                "🧠 XNOR is EQUAL! Output is 1 ONLY when inputs are EQUAL (00 or 11)."
            )
        elif "half adder" in q_text:
            return (
                "$$Sum = A \\oplus B, \\quad Carry = A \\cdot B$$",
                "Where: $A, B$ are 1-bit inputs.",
                "🧠 Half Adder Rule: Sum is XOR (Different = 1), Carry is AND (Both = 1)!"
            )
        elif "full adder" in q_text:
            return (
                "$$Sum = A \\oplus B \\oplus C_{in}, \\quad C_{out} = AB + C_{in}(A \\oplus B)$$",
                "Where: $A, B, C_{in}$ are inputs.",
                "🧠 Full Adder Rule: Odd number of 1s gives Sum = 1. Two or more 1s gives Carry-Out = 1!"
            )
        elif "multiplexer" in q_text or "mux" in q_text:
            return (
                "$$Y = \\bar{S} I_0 + S I_1$$",
                "Where: $S$ is Select line, $I_0, I_1$ are Data inputs.",
                "🧠 MUX Rule: Select line S acts like a track switch! S=0 picks Data line I0, S=1 picks Data line I1."
            )
        elif "decoder" in q_text:
            return (
                "$$Y_0 = \\bar{A}_1 \\bar{A}_0, \\; Y_1 = \\bar{A}_1 A_0, \\; Y_2 = A_1 \\bar{A}_0, \\; Y_3 = A_1 A_0$$",
                "Where: $A_1, A_0$ are 2-bit binary address inputs.",
                "🧠 Decoder Rule: N binary input lines activate 1 out of 2^N unique output lines!"
            )
        elif "ohm" in q_text:
            return (
                "$$V = I \\cdot R, \\quad I = \\frac{V}{R}, \\quad R = \\frac{V}{I}$$",
                "Where: $V$ = Voltage (Volts), $I$ = Current (Amperes), $R$ = Resistance (Ohms).",
                "🧠 Ohm's Law Pyramid: V is at the top! To find V, multiply I×R. To find I or R, divide V by the other variable!"
            )
        elif "kirchhoff" in q_text or "kvl" in q_text or "kcl" in q_text:
            return (
                "$$KVL: \\sum V_{loop} = 0, \\quad KCL: \\sum I_{in} = \\sum I_{out}$$",
                "Where: $V$ = Potential drops/sources, $I$ = Node currents.",
                "🧠 Kirchhoff Rules: KVL = Energy Conservation (Voltage gains equal voltage drops around a loop). KCL = Charge Conservation (What flows IN must flow OUT)!"
            )
        elif "resonance" in q_text:
            return (
                "$$f_0 = \\frac{1}{2\\pi\\sqrt{LC}}, \\quad X_L = X_C = 2\\pi f L = \\frac{1}{2\\pi f C}$$",
                "Where: $f_0$ = Resonant frequency (Hz), $L$ = Inductance (H), $C$ = Capacitance (F).",
                "🧠 Resonance Rule: At resonance, inductive reactance cancels capacitive reactance ($X_L = X_C$), leaving MINIMUM impedance ($Z = R$)!"
            )
        elif "op-amp" in q_text or "operational amplifier" in q_text:
            return (
                "$$V_{out} = A_{OL}(V_+ - V_-), \\quad V_+ = V_- \\; (Virtual \\; Ground)$$",
                "Where: $A_{OL}$ = Open-loop gain, $V_+, V_-$ = Input terminals.",
                "🧠 Op-Amp Golden Rules: 1) NO current enters inputs ($I_+ = I_- = 0$). 2) Negative feedback forces non-inverting and inverting input voltages to be EQUAL ($V_+ = V_-$)!"
            )
        else:
            formula = q.get("formula", "$$y = f(x)$$")
            vars_text = q.get("variables", "Where: $y$ = Output, $x$ = Input")
            trick = q.get("mnemonic_trick", "🧠 Exam Tip: Write the governing formula clearly before starting any numerical derivation.")
            return (formula, vars_text, trick)

    def load_question_detail(self, q, parent_list):
        self.current_question = q
        self.current_parent_list = parent_list
        
        # Set titles
        self.v_question_lbl.setText(q["question"])
        self.v_expected_lbl.setText(q["expected_answer"])
        self.v_explanation_lbl.setText(q["explanation"])
        
        # Difficulty color styling
        diff = q.get("difficulty", "Beginner")
        color = "#10b981" if diff == "Beginner" else "#f59e0b" if diff == "Intermediate" else "#ef4444"
        self.v_diff_lbl.setText(diff)
        self.v_diff_lbl.setStyleSheet(f"background-color: {color}22; color: {color}; border: 1px solid {color}; border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 8pt;")
        
        # Company
        self.v_comp_lbl.setText(q.get("company", "ISRO"))
        
        # Reset visibility
        self.ans_card.setVisible(False)
        self.correct_btn.setVisible(False)
        self.wrong_btn.setVisible(False)
        self.reveal_btn.setVisible(True)
        
        # Formula & Memorization Resolution
        formula, vars_text, mnemonic = self.get_formula_and_mnemonic(q)
        if formula:
            self.formula_card.setVisible(True)
            self.v_formula_lbl.setText(formula)
            self.v_vars_lbl.setText(vars_text)
        else:
            self.formula_card.setVisible(False)
            
        if mnemonic:
            self.memo_card.setVisible(True)
            self.v_memo_lbl.setText(mnemonic)
        else:
            self.memo_card.setVisible(False)
            
        # Tip
        self.v_tip_lbl.setText(q.get("interview_tip", ""))
        
        is_fav = q["id"] in self.progress["favorites"]
        self.v_fav_btn.setIcon(qta.icon("fa5s.star", color="#f59e0b" if is_fav else "#475569"))
        
        # Icon loaded dynamically based on favorites state
        
        # Build intelligent cross-links buttons
        while self.links_lay.count():
            child = self.links_lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Related component link
        rel_c = q.get("related_component")
        if rel_c:
            btn = QPushButton(" View Component Explorer")
            btn.setIcon(qta.icon("fa5s.book-open", color="#ffffff"))
            btn.clicked.connect(lambda: self.window().navigate_to_component(rel_c))
            self.links_lay.addWidget(btn)
            
        # Related simulation link
        rel_s = q.get("related_simulation")
        if rel_s:
            sim_idx = self.get_simulation_index(rel_s)
            if sim_idx is not None:
                btn = QPushButton(" Launch Real-time Simulation")
                btn.setIcon(qta.icon("fa5s.flask", color="#ffffff"))
                btn.clicked.connect(lambda: self.window().navigate_to_simulation(sim_idx))
                self.links_lay.addWidget(btn)
                
        # Related lesson link
        rel_l = q.get("related_lesson")
        if rel_l:
            btn = QPushButton(" Read Syllabus Lesson")
            btn.setIcon(qta.icon("fa5s.graduation-cap", color="#ffffff"))
            btn.clicked.connect(lambda: self.window().navigate_to_lesson(rel_l))
            self.links_lay.addWidget(btn)
            
        self.content_stack.setCurrentIndex(2)
        
        # Log recently practiced
        if q["id"] not in self.progress["recently_practiced"]:
            self.progress["recently_practiced"].insert(0, q["id"])
            if len(self.progress["recently_practiced"]) > 10:
                self.progress["recently_practiced"] = self.progress["recently_practiced"][:10]
            self.save_progress()

    def get_simulation_index(self, sim_name):
        exp_to_row = {
            "RC Charging": 0, "RC Discharging": 0, "RL Transient": 1,
            "Series RLC Resonance": 2, "Low Pass Filter": 3, "High Pass Filter": 4,
            "Half Wave Rectifier": 5, "Full Wave Rectifier": 6, "Signal Attenuation": 7,
            "Voltage Divider": 8
        }
        return exp_to_row.get(sim_name)

    def reveal_expected_answer(self):
        self.ans_card.setVisible(True)
        self.reveal_btn.setVisible(False)
        self.correct_btn.setVisible(True)
        self.wrong_btn.setVisible(True)
        
        # Add to attempted progress
        q_id = self.current_question["id"]
        if q_id not in self.progress["attempted_questions"]:
            self.progress["attempted_questions"].append(q_id)
            self.save_progress()

    def evaluate_practice_question(self, correct):
        q_id = self.current_question["id"]
        if correct:
            if q_id not in self.progress["correct_questions"]:
                self.progress["correct_questions"].append(q_id)
        else:
            if q_id in self.progress["correct_questions"]:
                self.progress["correct_questions"].remove(q_id)
                
        self.save_progress()
        self.load_next_question()

    def load_next_question(self):
        if hasattr(self, "current_question") and hasattr(self, "current_parent_list"):
            idx = self.current_parent_list.index(self.current_question)
            if idx < len(self.current_parent_list) - 1:
                self.load_question_detail(self.current_parent_list[idx + 1], self.current_parent_list)
            else:
                self.show_dashboard()

    def load_prev_question(self):
        if hasattr(self, "current_question") and hasattr(self, "current_parent_list"):
            idx = self.current_parent_list.index(self.current_question)
            if idx > 0:
                self.load_question_detail(self.current_parent_list[idx - 1], self.current_parent_list)

    def toggle_favorite_question(self, q):
        q_id = q["id"]
        if q_id in self.progress["favorites"]:
            self.progress["favorites"].remove(q_id)
            self.show_toast_message(f"Removed question from Starred Library.")
        else:
            self.progress["favorites"].append(q_id)
            self.show_toast_message(f"Saved question to Starred Library.")
            
        self.save_progress()
        is_fav = q_id in self.progress["favorites"]
        self.v_fav_btn.setIcon(qta.icon("fa5s.star", color="#f59e0b" if is_fav else "#475569"))

    def show_toast_message(self, text):
        win = self.window()
        if win and hasattr(win, "show_toast"):
            win.show_toast(text)

    # 4. Mock Viva Board Simulation Logics
    def show_mock_config(self):
        self.mock_stack.setCurrentIndex(0)
        self.content_stack.setCurrentIndex(3)

    def initiate_mock_session(self):
        size_str = self.mock_size_cmb.currentText()
        count = int(size_str.split(" ")[0])
        self.start_mock_viva(count)

    def start_mock_viva(self, count):
        # Draw random questions from every subject
        all_qs = []
        for sub_qs in self.db.values():
            all_qs.extend(sub_qs)
            
        if not all_qs:
            self.show_dashboard()
            return
            
        # Draw evenly or randomly
        self.mock_session_qs = random.sample(all_qs, min(count, len(all_qs)))
        self.mock_index = 0
        self.mock_score = 0
        self.mock_evals = {}
        
        self.mock_stack.setCurrentIndex(1)
        self.content_stack.setCurrentIndex(3)
        self.load_mock_question()

    def load_mock_question(self):
        q = self.mock_session_qs[self.mock_index]
        self.mock_question_box.setText(f"Question {self.mock_index + 1} of {len(self.mock_session_qs)}:\n\n{q['question']}")
        
        self.mock_answer_box.setText(q["expected_answer"])
        self.mock_answer_box.setVisible(False)
        self.mock_reveal_btn.setVisible(True)
        self.mock_eval_widget.setVisible(False)
        
        # Progress
        self.mock_progress.setValue(int(((self.mock_index) / len(self.mock_session_qs)) * 100))

    def reveal_mock_answer(self):
        self.mock_answer_box.setVisible(True)
        self.mock_reveal_btn.setVisible(False)
        self.mock_eval_widget.setVisible(True)

    def evaluate_mock_question(self, correct):
        self.mock_evals[self.mock_index] = correct
        
        # Track attempted progress
        q_id = self.mock_session_qs[self.mock_index]["id"]
        if q_id not in self.progress["attempted_questions"]:
            self.progress["attempted_questions"].append(q_id)
        if correct:
            if q_id not in self.progress["correct_questions"]:
                self.progress["correct_questions"].append(q_id)
        self.save_progress()
        
        self.next_mock_question()

    def next_mock_question(self):
        if self.mock_index < len(self.mock_session_qs) - 1:
            self.mock_index += 1
            self.load_mock_question()
        else:
            self.calculate_mock_results()

    def prev_mock_question(self):
        if self.mock_index > 0:
            self.mock_index -= 1
            self.load_mock_question()

    def calculate_mock_results(self):
        correct_count = sum(1 for v in self.mock_evals.values() if v)
        total = len(self.mock_session_qs)
        pct = int((correct_count / total) * 100) if total > 0 else 0
        
        self.results_score_lbl.setText(f"Mock Viva Score: {correct_count} / {total} ({pct}%)")
        
        verdict = "Excellent board evaluation! You show high mastery of core electronics engineering concepts." if pct >= 80 else "Good attempt. Revise weak topics and try again to improve your score."
        self.results_summary_lbl.setText(
            f"Evaluations complete.\n\n"
            f"Verdict: {verdict}\n\n"
            f"Attempted: {total}\n"
            f"Correct: {correct_count}\n"
            f"Incorrect: {total - correct_count}"
        )
        
        self.mock_stack.setCurrentIndex(2)

    # 5. Rapid Fire Revision Session
    def start_rapid_fire(self):
        all_qs = []
        for sub_qs in self.db.values():
            all_qs.extend(sub_qs)
            
        if not all_qs:
            self.show_dashboard()
            return
            
        self.rapid_qs = random.sample(all_qs, min(30, len(all_qs)))
        self.rapid_idx = 0
        
        self.content_stack.setCurrentIndex(4)
        self.load_rapid_question()

    def load_rapid_question(self):
        q = self.rapid_qs[self.rapid_idx]
        self.rf_progress.setText(f"Flashcard {self.rapid_idx + 1} of {len(self.rapid_qs)}")
        self.rf_question_lbl.setText(q["question"])
        self.rf_answer_lbl.setText(q["expected_answer"])
        
        self.rf_answer_lbl.setVisible(False)
        self.rf_reveal_btn.setVisible(True)

    def reveal_rapid_answer(self):
        self.rf_answer_lbl.setVisible(True)
        self.rf_reveal_btn.setVisible(False)
        
        # Track attempted progress
        q_id = self.rapid_qs[self.rapid_idx]["id"]
        if q_id not in self.progress["attempted_questions"]:
            self.progress["attempted_questions"].append(q_id)
            self.save_progress()

    def next_rapid_question(self):
        if self.rapid_idx < len(self.rapid_qs) - 1:
            self.rapid_idx += 1
            self.load_rapid_question()
        else:
            self.show_dashboard()

    def prev_rapid_question(self):
        if self.rapid_idx > 0:
            self.rapid_idx -= 1
            self.load_rapid_question()

    # 6. Favorite Bookmarks List
    def show_favorites(self):
        self.fav_list_widget.clear()
        
        fav_ids = self.progress["favorites"]
        all_qs = {}
        for sub_qs in self.db.values():
            for q in sub_qs:
                all_qs[q["id"]] = q
                
        for q_id in fav_ids:
            if q_id in all_qs:
                q = all_qs[q_id]
                item = QListWidgetItem(f"★ {q['question']}")
                item.setData(Qt.ItemDataRole.UserRole, q)
                self.fav_list_widget.addItem(item)
                
        if not fav_ids:
            self.fav_list_widget.addItem("No starred questions yet. Bookmark questions while practicing to save them here.")
            
        self.content_stack.setCurrentIndex(5)

    def on_fav_item_clicked(self, item_widget):
        q = item_widget.data(Qt.ItemDataRole.UserRole)
        if q:
            # Rebuild a parent list containing just the favs to allow next/prev switches
            fav_ids = self.progress["favorites"]
            all_qs = []
            for sub_qs in self.db.values():
                for q_obj in sub_qs:
                    if q_obj["id"] in fav_ids:
                        all_qs.append(q_obj)
            self.load_question_detail(q, all_qs)

    # 7. Core Company-style Technical Interviews Filter
    def show_core_interview_panel(self):
        # We can construct a filter layout using the favorites panel or custom popups
        # To keep it extremely simple and clean, let's load all company questions in the practice panel list!
        self.sub_title_lbl.setText("Core Technical Interview Practice (DRDO, ISRO, BEL, Intel, TI)")
        self.practice_list.clear()
        
        all_qs = []
        for sub_qs in self.db.values():
            for q in sub_qs:
                if q.get("company"):
                    all_qs.append(q)
                    
        # Show a random selection of 50 top company questions
        company_selection = random.sample(all_qs, min(50, len(all_qs)))
        for index, q in enumerate(company_selection, 1):
            item = QListWidgetItem(f"[{q.get('company', 'CORE')}] Q{index}: {q['question']}")
            item.setData(Qt.ItemDataRole.UserRole, q)
            self.practice_list.addItem(item)
            
        self.current_parent_list = company_selection
        self.content_stack.setCurrentIndex(1)

    # 8. Intelligent Search
    def on_search_changed(self, text):
        if not text.strip():
            # Reset tree view
            for i in range(self.tree_widget.topLevelItemCount()):
                self.tree_widget.topLevelItem(i).setHidden(False)
            return
            
        text = text.lower().strip()
        
        # Display matches in the practice list view directly
        self.sub_title_lbl.setText(f"Search Results for: '{text}'")
        self.practice_list.clear()
        
        matches = []
        for sub_qs in self.db.values():
            for q in sub_qs:
                if (text in q["question"].lower() or 
                    text in q["expected_answer"].lower() or 
                    text in q.get("explanation", "").lower() or 
                    text in q.get("reference_topic", "").lower()):
                    matches.append(q)
                    
        for index, q in enumerate(matches[:100], 1): # Cap at 100 search matches
            item = QListWidgetItem(f"Q{index}: {q['question']}")
            item.setData(Qt.ItemDataRole.UserRole, q)
            self.practice_list.addItem(item)
            
        self.current_parent_list = matches[:100]
        self.content_stack.setCurrentIndex(1)
        
        # Filter tree items matching key
        for sub_key, item in self.tree_items.items():
            hide = True
            for q in self.db[sub_key]:
                if text in q["question"].lower():
                    hide = False
                    break
            item.setHidden(hide)
