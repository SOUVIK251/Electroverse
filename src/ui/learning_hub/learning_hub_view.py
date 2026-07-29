"""
Digital Learning Hub Main Container View
Hosts 4 Integrated Sub-Tabs:
1. 📖 Learn (25% Compact Sidebar | 75% Expandable Textbook Lesson Reader)
2. 🧪 Practice (Pure 2D Breadboard Trainer Kit - Clean Fullscreen Lab)
3. 📝 Test (MCQs, Viva Flashcards & Certificates)
4. 📚 Reference (IC Pinout Matrix, Formulas & Datasheets)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from .learning_path_widget import LearningPathWidget
from .course_tree_widget import CourseTreeWidget
from .lesson_reader_widget import LessonReaderWidget
from .quiz_viva_widget import QuizVivaWidget
from .reference_matrix_widget import ReferenceMatrixWidget
from .deep_search_widget import DeepSearchWidget

from src.ui.dsd_lab import DSDLabView

class LearningHubView(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Primary Top Navigation Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #0b0f19; border-radius: 6px; }
            QTabBar::tab { background-color: #0f172a; color: #94a3b8; padding: 8px 16px; font-weight: bold; font-size: 9pt; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #0284c7; color: #ffffff; }
            QTabBar::tab:hover:!selected { background-color: #1e293b; color: #38bdf8; }
        """)
        
        # TAB 1: 📖 Learn (Left 25% Compact Navigation Sidebar | Right 75% Textbook Lesson Reader)
        learn_widget = QWidget()
        l_lay = QVBoxLayout(learn_widget)
        l_lay.setContentsMargins(2, 2, 2, 2)
        l_lay.setSpacing(2)
        
        # Deep Search Bar
        search_bar = DeepSearchWidget(self)
        search_bar.result_selected.connect(self.on_search_result_selected)
        l_lay.addWidget(search_bar)
        
        learn_splitter = QSplitter(Qt.Orientation.Horizontal)
        learn_splitter.setHandleWidth(4)
        learn_splitter.setStyleSheet("QSplitter::handle { background-color: #1e293b; } QSplitter::handle:hover { background-color: #0284c7; }")
        
        # Left 25% Tabbed Navigation (Path vs Tree)
        left_nav_tabs = QTabWidget()
        left_nav_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #090d16; border-radius: 4px; }
            QTabBar::tab { background-color: #1e293b; color: #94a3b8; padding: 5px 10px; font-size: 8pt; font-weight: bold; }
            QTabBar::tab:selected { background-color: #06b6d4; color: #ffffff; }
        """)
        
        self.learning_path_widget = LearningPathWidget(self)
        self.learning_path_widget.topic_selected.connect(self.on_topic_selected_from_path)
        left_nav_tabs.addTab(self.learning_path_widget, "🗺️ Path")
        
        self.course_tree_widget = CourseTreeWidget(self)
        self.course_tree_widget.topic_selected.connect(self.on_topic_selected_from_path)
        left_nav_tabs.addTab(self.course_tree_widget, "📂 Tree")
        
        learn_splitter.addWidget(left_nav_tabs)
        
        # Right 75% Expandable Lesson Reader
        self.lesson_reader = LessonReaderWidget(self)
        self.lesson_reader.launch_experiment_requested.connect(self.launch_practice_experiment)
        self.lesson_reader.cross_link_clicked.connect(self.on_cross_link_clicked)
        learn_splitter.addWidget(self.lesson_reader)
        
        # 25% Sidebar (~280px) and 75% Reader (~840px)
        learn_splitter.setStretchFactor(0, 1)
        learn_splitter.setStretchFactor(1, 3)
        learn_splitter.setSizes([280, 840])
        
        l_lay.addWidget(learn_splitter, 1)
        
        self.main_tabs.addTab(learn_widget, "📖 Learn")
        
        # TAB 2: 🧪 Practice (Pure Solderless Breadboard Trainer Kit - Clean Fullscreen Lab View)
        self.dsd_breadboard_view = DSDLabView(self.main_window)
        self.main_tabs.addTab(self.dsd_breadboard_view, "🧪 Practice")
        
        # TAB 3: 📝 Test (MCQs, Viva, Certificates)
        self.test_widget = QuizVivaWidget(self)
        self.main_tabs.addTab(self.test_widget, "📝 Test")
        
        # TAB 4: 📚 Reference (IC Matrix & Cheat Sheets)
        self.reference_widget = ReferenceMatrixWidget(self)
        self.main_tabs.addTab(self.reference_widget, "📚 Reference")
        
        main_layout.addWidget(self.main_tabs)
        
        # Default load first topic lesson (Introduction)
        self.lesson_reader.load_topic_json("introduction/intro.json")

    def on_topic_selected_from_path(self, node):
        path_to_data = node.get("path_to_data", "")
        if path_to_data:
            self.lesson_reader.load_topic_json(path_to_data)

    def on_search_result_selected(self, item):
        path = item.get("path", "")
        if path:
            self.lesson_reader.load_topic_json(path)

    def on_cross_link_clicked(self, topic_id):
        mapping = {
            "intro_digital": "introduction/intro.json",
            "number_systems": "number_systems/number_systems.json",
            "boolean_algebra": "boolean_algebra/boolean_algebra.json",
            "gate_and": "logic_gates/and/theory.json",
            "gate_or": "logic_gates/or/theory.json",
            "gate_not": "logic_gates/not/theory.json",
            "gate_nand": "logic_gates/nand/theory.json",
            "gate_nor": "logic_gates/nor/theory.json",
            "gate_xor": "logic_gates/xor/theory.json",
            "gate_xnor": "logic_gates/xnor/theory.json",
            "universal_nand": "universal_gates/nand/theory.json",
            "half_adder": "combinational/half_adder/theory.json",
            "full_adder": "combinational/full_adder/theory.json",
            "mux_2_1": "combinational/mux/theory.json",
            "decoder_2_4": "combinational/decoder/theory.json",
            "bcd_7segment": "combinational/bcd_7segment/theory.json"
        }
        if topic_id in mapping:
            self.lesson_reader.load_topic_json(mapping[topic_id])

    def launch_practice_experiment(self, exp_or_ic_id):
        # Switch tab to TAB 2: 🧪 Practice (Pure Breadboard View)
        self.main_tabs.setCurrentIndex(1)
        if self.dsd_breadboard_view and hasattr(self.dsd_breadboard_view, "ic_selector"):
            ic_map = {
                "half_adder": "7486",
                "full_adder": "7486",
                "mux_2_1": "7408",
                "decoder_2_4": "7408",
                "bcd_7seg": "7408"
            }
            target_ic = ic_map.get(exp_or_ic_id, "7408")
            idx = self.dsd_breadboard_view.ic_selector.findData(target_ic)
            if idx != -1:
                self.dsd_breadboard_view.ic_selector.setCurrentIndex(idx)
