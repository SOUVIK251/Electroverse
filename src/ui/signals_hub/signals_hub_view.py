from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt

from src.core.logger import log
from .dashboard_view import SignalsDashboardView
from .signals_learn_widget import SignalsLearnWidget
from .signals_simulation_widget import SignalsSimulationWidget
from src.ui.components.cbt_exam_widget import CBTExamWidget
from .signals_reference_widget import SignalsReferenceWidget

class SignalSystemHubView(QWidget):
    """Unified Signal & System Hub Master Learning Platform.
    
    Includes 5 Main Sub-Modules:
    0. 🏠 Dashboard: Subject Banner, Analytics Progress, Quick Access & Widgets
    1. 📖 Learn: Interactive Engineering Textbook Reader (10 Modules & 40+ Topics)
    2. 🧪 Interactive Simulation: Live Matplotlib Signal Generators, Transforms & Convolution
    3. 📝 Assessment: MCQs, Numerical Exercises, Viva & Interview Q&A with Auto-Grader
    4. 📚 Reference: Fourier, Laplace & Z Transform Tables & Formula Cheat Sheets
    """
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        log.info("Initializing SignalSystemHubView unified platform with Subject Dashboard")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # Main Navigation Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #26334D; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab {
                background-color: #141B2D;
                color: #94A3B8;
                padding: 10px 20px;
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
        self.dash_widget = SignalsDashboardView(self)
        self.dash_widget.tab_jump_requested.connect(self.main_tabs.setCurrentIndex)
        self.main_tabs.addTab(self.dash_widget, "🏠 Dashboard")

        # Tab 1: 📖 Learn
        self.learn_widget = SignalsLearnWidget(self)
        self.learn_widget.launch_simulation_requested.connect(self.on_launch_simulation_requested)
        self.main_tabs.addTab(self.learn_widget, "📖 Learn")

        # Tab 2: 🧪 Interactive Simulation
        self.sim_widget = SignalsSimulationWidget(self)
        self.main_tabs.addTab(self.sim_widget, "🧪 Interactive Simulation")

        # Tab 3: 📝 Assessment (Enterprise CBT Engine - 30 Sets)
        self.assessment_widget = CBTExamWidget(subject_id="signal_and_system")
        self.assessment_widget.launch_theory_signal.connect(lambda ref: self.main_tabs.setCurrentIndex(1))
        self.assessment_widget.launch_sim_signal.connect(lambda sim: self.main_tabs.setCurrentIndex(2))
        self.main_tabs.addTab(self.assessment_widget, "📝 Assessment")

        # Tab 4: 📚 Reference
        self.ref_widget = SignalsReferenceWidget(self)
        self.main_tabs.addTab(self.ref_widget, "📚 Reference")

        main_layout.addWidget(self.main_tabs)

    def on_launch_simulation_requested(self, module_idx, params):
        log.info(f"Launch simulation requested for module {module_idx}: {params}")
        # Switch to Tab 2 (Interactive Simulation)
        self.main_tabs.setCurrentIndex(2)
        # Load preset mode and parameters
        self.sim_widget.load_simulation_preset(module_idx, params)
