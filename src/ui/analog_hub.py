from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QFrame, QLabel
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.ui.learning import LearningView
from src.ui.toolkit import ToolkitView
from src.ui.simulation import SimulationView


class AnalogElectronicsHubView(QWidget):
    """Unified master hub combining Theory & Lessons, Engineering Toolkit,

    and Interactive Simulation Lab into a single Analog Electronics Hub environment.

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing AnalogElectronicsHubView unified workspace")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # 1. Top Sub-Navigation Header Bar (Laboratory Styled)
        # -------------------------------------------------------------
        self.nav_header = QFrame()
        self.nav_header.setFixedHeight(50)
        self.nav_header.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border-bottom: 1px solid #26334D;
            }
        """)

        nav_layout = QHBoxLayout(self.nav_header)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(10)

        # Header Title
        title_lbl = QLabel("ANALOG ELECTRONICS CIRCUIT HUB")
        title_lbl.setStyleSheet("color: #06B6D4; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        nav_layout.addWidget(title_lbl)
        nav_layout.addSpacing(15)

        # Sub-Navigation Buttons
        self.sub_buttons = []
        tab_specs = [
            (" Theory & Lessons", "fa5s.graduation-cap", 0),
            (" Engineering Toolkit", "fa5s.tools", 1),
            (" Interactive Simulation Lab & Oscilloscope", "fa5s.flask", 2)
        ]

        for text, icon_str, idx in tab_specs:
            btn = QPushButton()
            btn.setText(text)
            btn.setIcon(qta.icon(icon_str, color="#94A3B8"))
            btn.setIconSize(QSize(15, 15))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #141B2D;
                    border: 1px solid #26334D;
                    color: #C9D1E3;
                    border-radius: 8px;
                    padding: 0px 14px;
                    font-size: 9.5pt;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1B2740;
                    color: #FFFFFF;
                    border-color: #06B6D4;
                }
                QPushButton:checked {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    border-color: #2563EB;
                }
            """)
            btn.clicked.connect(lambda checked=False, target_idx=idx: self.switch_sub_tab(target_idx))
            nav_layout.addWidget(btn)
            self.sub_buttons.append(btn)

        nav_layout.addStretch()
        main_layout.addWidget(self.nav_header)

        # -------------------------------------------------------------
        # 2. Main Sub-View Stack
        # -------------------------------------------------------------
        self.sub_stack = QStackedWidget()

        self.learning_view = LearningView()
        self.toolkit_view = ToolkitView()
        self.simulation_view = SimulationView()

        self.sub_stack.addWidget(self.learning_view)     # Sub Index 0
        self.sub_stack.addWidget(self.toolkit_view)      # Sub Index 1
        self.sub_stack.addWidget(self.simulation_view)   # Sub Index 2

        main_layout.addWidget(self.sub_stack, 1)

        # Default to Theory & Lessons
        self.switch_sub_tab(0)

    def switch_sub_tab(self, sub_idx: int):
        """Switches between Theory, Toolkit, and Simulation sub-views."""
        if sub_idx < 0 or sub_idx >= self.sub_stack.count():
            return

        self.sub_stack.setCurrentIndex(sub_idx)

        # Update button checked states and icons
        colors = ["#94A3B8", "#94A3B8", "#94A3B8"]
        icons = ["fa5s.graduation-cap", "fa5s.tools", "fa5s.flask"]

        for i, btn in enumerate(self.sub_buttons):
            is_active = (i == sub_idx)
            btn.setChecked(is_active)
            icon_color = "#FFFFFF" if is_active else "#94A3B8"
            btn.setIcon(qta.icon(icons[i], color=icon_color))

    def load_lesson(self, lesson_id: str):
        """Switches to Theory sub-tab and loads the target lesson."""
        self.switch_sub_tab(0)
        if hasattr(self.learning_view, "load_lesson"):
            self.learning_view.load_lesson(lesson_id)

    def select_calculator(self, calc_index: int):
        """Switches to Toolkit sub-tab and selects the target calculator."""
        self.switch_sub_tab(1)
        if hasattr(self.toolkit_view, "list_widget"):
            self.toolkit_view.list_widget.setCurrentRow(calc_index)

    def select_simulation(self, sim_index: int):
        """Switches to Simulation Lab sub-tab and selects the target simulation."""
        self.switch_sub_tab(2)
        if hasattr(self.simulation_view, "list_widget"):
            self.simulation_view.list_widget.setCurrentRow(sim_index)
