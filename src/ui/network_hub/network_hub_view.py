from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.core.logger import log
from .dashboard_view import NetworkDashboardView
from .learning_view import NetworkLearningView
from .problem_solving_view import NetworkProblemSolvingView
from .simulation_view import NetworkSimulationView
from src.ui.components.cbt_exam_widget import CBTExamWidget
from .reference_view import NetworkReferenceView
from .workspace_dialog import EngineeringWorkspaceDialog

class NetworkHubView(QWidget):
    """Unified Master Network Theory Hub Learning Platform.
    
    Dynamically adjusts tab visibility (Problem Solving Lab) based on topic metadata.
    """

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        log.info("Initializing NetworkHubView unified master platform")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # Header Bar
        hdr_bar = QFrame()
        hdr_bar.setFixedHeight(45)
        hdr_bar.setStyleSheet("background-color: #101827; border-bottom: 1px solid #26334D;")
        hb_lay = QHBoxLayout(hdr_bar)
        hb_lay.setContentsMargins(12, 0, 12, 0)

        t_lbl = QLabel("NETWORK THEORY VIRTUAL ENGINEERING LABORATORY")
        t_lbl.setStyleSheet("color: #06B6D4; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        hb_lay.addWidget(t_lbl)
        hb_lay.addStretch()

        ws_btn = QPushButton("💼 Engineering Workspace")
        ws_btn.setIcon(qta.icon("fa5s.briefcase", color="#FFFFFF"))
        ws_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                border: 1px solid #26334D;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 5px 12px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        ws_btn.clicked.connect(self.open_workspace)
        hb_lay.addWidget(ws_btn)

        main_layout.addWidget(hdr_bar)

        # Main Navigation Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #26334D; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab {
                background-color: #141B2D;
                color: #94A3B8;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 9.5pt;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #26334D;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #06B6D4;
                color: #FFFFFF;
                border-color: #06B6D4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #1B2740;
                color: #FFFFFF;
            }
        """)

        # Tab 0: 🏠 Dashboard
        self.dash_widget = NetworkDashboardView(self)
        self.dash_widget.tab_jump_requested.connect(self.main_tabs.setCurrentIndex)
        self.main_tabs.addTab(self.dash_widget, "🏠 Dashboard")

        # Tab 1: 📖 Learn
        self.learn_widget = NetworkLearningView(self)
        self.learn_widget.open_problem_solving_signal.connect(lambda topic: self.main_tabs.setCurrentIndex(2))
        self.learn_widget.launch_simulation_signal.connect(lambda topic: self.main_tabs.setCurrentIndex(3))
        self.learn_widget.topic_selected_signal.connect(self.on_topic_selected)
        self.main_tabs.addTab(self.learn_widget, "📖 Learn")

        # Tab 2: 🧠 Problem Solving Lab
        self.ps_widget = NetworkProblemSolvingView(self)
        self.main_tabs.addTab(self.ps_widget, "🧠 Problem Solving Lab")

        # Tab 3: 🧪 Interactive Simulation
        self.sim_widget = NetworkSimulationView(self)
        self.main_tabs.addTab(self.sim_widget, "🧪 Interactive Simulation")

        # Tab 4: 📝 Assessment (Enterprise CBT Engine - 30 Sets)
        self.assessment_widget = CBTExamWidget(subject_id="network_theory")
        self.assessment_widget.launch_theory_signal.connect(lambda ref: self.main_tabs.setCurrentIndex(1))
        self.assessment_widget.launch_sim_signal.connect(lambda sim: self.main_tabs.setCurrentIndex(3))
        self.main_tabs.addTab(self.assessment_widget, "📝 Assessment")

        # Tab 5: 📚 Reference
        self.ref_widget = NetworkReferenceView(self)
        self.main_tabs.addTab(self.ref_widget, "📚 Reference")

        main_layout.addWidget(self.main_tabs)

    def on_topic_selected(self, topic_meta):
        has_ps = topic_meta.get("has_problem_solving", False)
        # Tab index 2 is Problem Solving Lab
        self.main_tabs.setTabVisible(2, has_ps)

        # If user is currently on Problem Solving tab and it becomes hidden, switch back to Learn (Tab 1)
        if not has_ps and self.main_tabs.currentIndex() == 2:
            self.main_tabs.setCurrentIndex(1)

    def open_workspace(self):
        dlg = EngineeringWorkspaceDialog(self)
        dlg.exec()
