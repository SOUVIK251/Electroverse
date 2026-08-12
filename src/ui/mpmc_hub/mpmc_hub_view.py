"""
ElectroVerse Master Microprocessor & Microcontroller Hub Platform.
Unified Engineering Hub for 8085, 8086, 8051, ARM Cortex, Embedded Systems & RTOS.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.core.logger import log
from .dashboard_view import MPMCDashboardView
from .learning_view import MPMCLearningView
from .simulation_view import MPMCSimulationView
from .assessment_view import MPMCAssessmentView
from .reference_view import MPMCReferenceView


class MPMCHubView(QWidget):
    """Unified Master Microprocessor & Microcontroller Hub Engineering Platform."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        log.info("Initializing MPMCHubView master engineering platform")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # Header Bar
        hdr_bar = QFrame()
        hdr_bar.setFixedHeight(45)
        hdr_bar.setStyleSheet("background-color: #101827; border-bottom: 1px solid #1E293B;")
        hb_lay = QHBoxLayout(hdr_bar)
        hb_lay.setContentsMargins(12, 0, 12, 0)

        t_lbl = QLabel("MICROPROCESSOR & MICROCONTROLLER VIRTUAL LABORATORY")
        t_lbl.setStyleSheet("color: #F97316; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        hb_lay.addWidget(t_lbl)
        hb_lay.addStretch()

        ws_btn = QPushButton("💼 Engineering Workspace")
        ws_btn.setIcon(qta.icon("fa5s.briefcase", color="#FFFFFF"))
        ws_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                border: 1px solid #334155;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 5px 12px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #F97316;
                border-color: #F97316;
            }
        """)
        hb_lay.addWidget(ws_btn)
        main_layout.addWidget(hdr_bar)

        # Main Navigation Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1E293B; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab {
                background-color: #141B2D;
                color: #94A3B8;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 9.5pt;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #1E293B;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #F97316;
                color: #FFFFFF;
                border-color: #F97316;
            }
            QTabBar::tab:hover:!selected {
                background-color: #1B2740;
                color: #FFFFFF;
            }
        """)

        # Tab 0: 🏠 Dashboard
        self.dash_widget = MPMCDashboardView(self)
        self.dash_widget.tab_jump_requested.connect(self.main_tabs.setCurrentIndex)
        self.main_tabs.addTab(self.dash_widget, "🏠 Dashboard")

        # Tab 1: 📖 Learn
        self.learn_widget = MPMCLearningView(self)
        self.main_tabs.addTab(self.learn_widget, "📖 Learn")

        # Tab 2: 🔬 Interactive Simulation
        self.sim_widget = MPMCSimulationView(self)
        self.main_tabs.addTab(self.sim_widget, "🔬 Interactive Simulation")

        # Tab 3: 📝 Assessment
        self.exam_widget = MPMCAssessmentView(hub_view=self, parent=self)
        self.main_tabs.addTab(self.exam_widget, "📝 Assessment")

        # Tab 4: 📚 Reference
        self.ref_widget = MPMCReferenceView(self)
        self.main_tabs.addTab(self.ref_widget, "📚 Reference")

        main_layout.addWidget(self.main_tabs)
