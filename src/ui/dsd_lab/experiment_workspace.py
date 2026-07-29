"""
Experiment Workspace Container Widget
Assembles Experiment Browser, Instructor Panel, Observation Panel, Quiz Panel, Wiring Assistant, Assessment, and 2D Breadboard View into a cohesive engineering laboratory.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSplitter, QTabWidget, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from .stage_manager import StageManager, StageLevel, ExperimentStatus
from .experiment_browser import ExperimentBrowserWidget
from .instructor_panel import InstructorPanelWidget
from .observation_panel import ObservationPanelWidget
from .quiz_panel import QuizPanelWidget
from .wiring_panel import WiringPanelWidget
from .assessment_panel import AssessmentPanelWidget

class ExperimentWorkspace(QWidget):
    def __init__(self, dsd_lab_view, parent=None):
        super().__init__(parent)
        self.dsd_lab_view = dsd_lab_view
        self.stage_manager = StageManager()
        self.current_exp_data = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # 1. Left Experiment Browser Accordion
        self.browser_widget = ExperimentBrowserWidget(self)
        self.browser_widget.experiment_selected.connect(self.on_experiment_selected)
        main_layout.addWidget(self.browser_widget, 1)
        
        # 2. Right Modular Workspace Splitter
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(3)
        
        # Top Stage Navigation Header
        stage_bar = QFrame()
        stage_bar.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 4px;")
        s_lay = QHBoxLayout(stage_bar)
        s_lay.setContentsMargins(6, 2, 6, 2)
        s_lay.setSpacing(10)
        
        self.lbl_exp_title = QLabel("Select an Experiment from the Left Browser")
        self.lbl_exp_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_exp_title.setStyleSheet("color: #06b6d4;")
        s_lay.addWidget(self.lbl_exp_title)
        
        s_lay.addStretch()
        
        self.btn_stage_1 = QPushButton("1. Foundation")
        self.btn_stage_1.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_stage_1.clicked.connect(lambda: self.switch_stage(StageLevel.FOUNDATION))
        s_lay.addWidget(self.btn_stage_1)
        
        self.btn_stage_2 = QPushButton("2. Optimization")
        self.btn_stage_2.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_stage_2.clicked.connect(lambda: self.switch_stage(StageLevel.OPTIMIZATION))
        s_lay.addWidget(self.btn_stage_2)
        
        self.btn_stage_3 = QPushButton("3. Industrial Practice")
        self.btn_stage_3.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        self.btn_stage_3.clicked.connect(lambda: self.switch_stage(StageLevel.INDUSTRIAL))
        s_lay.addWidget(self.btn_stage_3)
        
        right_splitter.addWidget(stage_bar)
        
        # Center Workbench Tabs (2D Breadboard | Observation Sheet | Quiz | Assessment)
        center_tabs = QTabWidget()
        center_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #0b0f19; border-radius: 4px; }
            QTabBar::tab { background-color: #1e293b; color: #94a3b8; padding: 4px 8px; font-size: 8.5pt; font-weight: bold; }
            QTabBar::tab:selected { background-color: #06b6d4; color: #ffffff; }
        """)
        
        if self.dsd_lab_view:
            center_tabs.addTab(self.dsd_lab_view, "🔌 Workbench & Breadboard")
            
        self.instructor_widget = InstructorPanelWidget(self)
        center_tabs.addTab(self.instructor_widget, "👨‍🏫 Instructor Guidance")
        
        self.observation_widget = ObservationPanelWidget(self)
        center_tabs.addTab(self.observation_widget, "📊 Observation Table")
        
        self.quiz_widget = QuizPanelWidget(self)
        center_tabs.addTab(self.quiz_widget, "❓ Knowledge Check Quiz")
        
        self.assessment_widget = AssessmentPanelWidget(self)
        center_tabs.addTab(self.assessment_widget, "🏆 Grade & Assessment")
        
        right_splitter.addWidget(center_tabs)
        right_splitter.setSizes([45, 600])
        
        main_layout.addWidget(right_splitter, 4)

    def on_experiment_selected(self, exp_data):
        self.current_exp_data = exp_data
        exp_id = exp_data["id"]
        exp_name = exp_data["name"]
        
        self.lbl_exp_title.setText(f"Experiment: {exp_name}")
        
        # Load Instructor Notes, Observation Table, Quiz
        self.instructor_widget.load_experiment_notes(exp_data, "Foundation")
        self.observation_widget.load_truth_table(exp_data["_path"])
        self.quiz_widget.load_quiz(exp_data["_path"])
        
        # Reset stage to Foundation
        self.stage_manager.set_stage(exp_id, StageLevel.FOUNDATION)
        self.update_stage_buttons(exp_id)

    def switch_stage(self, stage: StageLevel):
        if not self.current_exp_data:
            return
        exp_id = self.current_exp_data["id"]
        if self.stage_manager.is_stage_unlocked(exp_id, stage):
            self.stage_manager.set_stage(exp_id, stage)
            self.update_stage_buttons(exp_id)
            self.instructor_widget.load_experiment_notes(self.current_exp_data, stage.value)

    def update_stage_buttons(self, exp_id):
        cur_stage = self.stage_manager.get_current_stage(exp_id)
        
        # Button 1
        self.btn_stage_1.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;" if cur_stage == StageLevel.FOUNDATION else "background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        
        # Button 2
        u2 = self.stage_manager.is_stage_unlocked(exp_id, StageLevel.OPTIMIZATION)
        self.btn_stage_2.setEnabled(u2)
        if cur_stage == StageLevel.OPTIMIZATION:
            self.btn_stage_2.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        else:
            self.btn_stage_2.setStyleSheet("background-color: #1e293b; color: " + ("#38bdf8" if u2 else "#475569") + "; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
            
        # Button 3
        u3 = self.stage_manager.is_stage_unlocked(exp_id, StageLevel.INDUSTRIAL)
        self.btn_stage_3.setEnabled(u3)
        if cur_stage == StageLevel.INDUSTRIAL:
            self.btn_stage_3.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
        else:
            self.btn_stage_3.setStyleSheet("background-color: #1e293b; color: " + ("#38bdf8" if u3 else "#475569") + "; font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 8pt;")
