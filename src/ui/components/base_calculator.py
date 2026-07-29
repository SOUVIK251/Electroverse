from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QScrollArea, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

from src.ui.components.math_plot import MathPlotCanvas
from src.core.logger import log

class BaseCalculator(QWidget):
    """Base class for all Engineering Toolkit calculators.
    
    Provides a standardized professional IDE interface with:
    - Reusable collapsible cards.
    - Mini plot navigation toolbar (Zoom In, Zoom Out, Reset, Save).
    - Toast notifications and validation handlers.
    """
    
    def __init__(self, title: str, formula_str: str, explanation_str: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.formula_str = formula_str
        self.explanation_str = explanation_str
        
        # Central Main Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)

        # -------------------------------------------------------------
        # Left Panel (Inputs, Formula, Calculation Outputs)
        # -------------------------------------------------------------
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.left_scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(5, 5, 5, 5)
        self.left_layout.setSpacing(15)
        
        # Title Card
        self.setup_title_card()
        
        # Formula Card (Collapsible)
        self.setup_formula_card()
        
        # Inputs Form Card
        self.inputs_card = QFrame()
        self.inputs_card.setObjectName("card-panel")
        self.inputs_layout = QVBoxLayout(self.inputs_card)
        self.inputs_layout.setContentsMargins(15, 15, 15, 15)
        self.inputs_layout.setSpacing(12)
        
        inputs_header = QLabel("Parameters")
        inputs_header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #10b981;")
        self.inputs_layout.addWidget(inputs_header)
        
        self.setup_inputs(self.inputs_layout)
        
        # Action Buttons Layout (Calculate, Reset)
        self.setup_action_buttons()
        self.inputs_layout.addLayout(self.actions_layout)
        self.left_layout.addWidget(self.inputs_card)

        # Calculation Steps Card
        self.setup_steps_card()
        
        # Explanation Card (Collapsible)
        self.setup_explanation_card()
        
        self.left_scroll.setWidget(self.left_container)
        self.main_layout.addWidget(self.left_scroll, stretch=1)

        # -------------------------------------------------------------
        # Right Panel (Interactive Graph & Real-time Sliders)
        # -------------------------------------------------------------
        self.right_container = QFrame()
        self.right_container.setObjectName("card-panel")
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(15)

        right_header_layout = QHBoxLayout()
        right_header = QLabel("Visualization Chart")
        right_header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06b6d4;")
        
        # Hover coordinate display in header
        self.coord_label = QLabel("")
        self.coord_label.setStyleSheet("font-size: 10pt; color: #94a3b8; font-weight: 500;")
        
        right_header_layout.addWidget(right_header)
        right_header_layout.addStretch()
        right_header_layout.addWidget(self.coord_label)
        self.right_layout.addLayout(right_header_layout)

        # Matplotlib Plot
        self.plot_canvas = MathPlotCanvas()
        self.plot_canvas.setMaximumHeight(280)
        self.plot_canvas.coordinates_updated.connect(self.coord_label.setText)
        self.right_layout.addWidget(self.plot_canvas, stretch=0)

        # Plot Controls Toolbar
        self.setup_chart_controls()

        # Sliders Container
        self.sliders_frame = QFrame()
        self.sliders_layout = QVBoxLayout(self.sliders_frame)
        self.sliders_layout.setContentsMargins(0, 5, 0, 5)
        self.sliders_layout.setSpacing(10)
        self.setup_sliders(self.sliders_layout)
        self.right_layout.addWidget(self.sliders_frame)

        self.main_layout.addWidget(self.right_container, stretch=1)

        # Initialize Plot default state
        self.orig_limits_saved = False
        self.init_plot()

    def setup_title_card(self):
        """Sets up the calculator title header."""
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #06b6d4;")
        self.left_layout.addWidget(self.title_label)

    def setup_formula_card(self):
        """Sets up the collapsible mathematical formula card."""
        content = QLabel(self.formula_str)
        content.setStyleSheet("font-size: 13pt; font-weight: bold; color: #f8fafc; padding: 5px;")
        content.setWordWrap(True)
        
        card = self.make_card_collapsible("Mathematical Formula", content)
        self.left_layout.addWidget(card)

    def setup_explanation_card(self):
        """Sets up the collapsible concept explanation card."""
        content = QLabel(self.explanation_str)
        content.setStyleSheet("font-size: 10pt; color: #94a3b8; line-height: 1.45;")
        content.setWordWrap(True)
        
        card = self.make_card_collapsible("Engineering Concept", content)
        self.left_layout.addWidget(card)

    def make_card_collapsible(self, title_text: str, content_widget: QWidget) -> QFrame:
        """Utility to wrap a widget inside a collapsible panel frame."""
        card = QFrame()
        card.setObjectName("card-panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        # Header bar
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_title = QLabel(title_text)
        header_title.setStyleSheet("font-size: 11pt; font-weight: 600; color: #94a3b8;")
        header_title.setCursor(Qt.CursorShape.PointingHandCursor)

        toggle_btn = QPushButton()
        toggle_btn.setFixedSize(24, 24)
        toggle_btn.setStyleSheet("border: none; background: transparent; padding: 0px;")
        toggle_btn.setIcon(qta.icon("fa5s.chevron-down", color="#94a3b8"))

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(toggle_btn)
        layout.addWidget(header_widget)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.05); height: 1px; border: none;")
        layout.addWidget(sep)

        # Add content body
        layout.addWidget(content_widget)

        def toggle():
            is_visible = content_widget.isVisible()
            content_widget.setVisible(not is_visible)
            sep.setVisible(not is_visible)
            icon_str = "fa5s.chevron-right" if is_visible else "fa5s.chevron-down"
            toggle_btn.setIcon(qta.icon(icon_str, color="#94a3b8"))

        toggle_btn.clicked.connect(toggle)
        
        # Make title label clickable
        # Re-route mouse release
        class ClickableLabel(QLabel):
            clicked = Signal()
            def mouseReleaseEvent(self, event):
                self.clicked.emit()
                
        header_title.mouseReleaseEvent = lambda e: toggle()

        return card

    def setup_action_buttons(self):
        """Creates calculate and reset buttons."""
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(10)
        
        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.setProperty("primary", "true")
        self.calc_btn.clicked.connect(self.calculate)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        
        self.actions_layout.addWidget(self.calc_btn)
        self.actions_layout.addWidget(self.reset_btn)

    def setup_steps_card(self):
        """Sets up the mathematical steps and final answer panel."""
        self.steps_card = QFrame()
        self.steps_card.setObjectName("card-panel")
        layout = QVBoxLayout(self.steps_card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header = QLabel("Calculation Breakdown")
        header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #10b981;")
        
        # Step-by-step substituted formula text label
        self.steps_text = QLabel("Enter parameters above and click 'Calculate'.")
        self.steps_text.setStyleSheet("font-size: 10.5pt; color: #f8fafc;")
        self.steps_text.setWordWrap(True)
        self.steps_text.setTextFormat(Qt.TextFormat.MarkdownText)

        # Final Answer label
        self.answer_box = QFrame()
        self.answer_box.setStyleSheet("background-color: rgba(6, 182, 212, 0.1); border: 1px solid #06b6d4; border-radius: 6px;")
        ab_layout = QVBoxLayout(self.answer_box)
        ab_layout.setContentsMargins(12, 12, 12, 12)
        
        self.answer_label = QLabel("Answer: Pending")
        self.answer_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #06b6d4;")
        ab_layout.addWidget(self.answer_label)

        # Error notification label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 10pt; font-weight: 500;")
        self.error_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self.steps_text)
        layout.addWidget(self.answer_box)
        layout.addWidget(self.error_label)
        
        self.left_layout.addWidget(self.steps_card)

    def setup_chart_controls(self):
        """Appends interactive controls directly under the Matplotlib canvas."""
        tb = QHBoxLayout()
        tb.setContentsMargins(0, 0, 0, 0)
        tb.setSpacing(8)
        
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(qta.icon("fa5s.search-plus", color="#94a3b8"))
        self.zoom_in_btn.setFixedSize(32, 32)
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self.plot_canvas.zoom_in)
        
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(qta.icon("fa5s.search-minus", color="#94a3b8"))
        self.zoom_out_btn.setFixedSize(32, 32)
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.plot_canvas.zoom_out)
        
        self.reset_zoom_btn = QPushButton()
        self.reset_zoom_btn.setIcon(qta.icon("fa5s.compress", color="#94a3b8"))
        self.reset_zoom_btn.setFixedSize(32, 32)
        self.reset_zoom_btn.setToolTip("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.plot_canvas.reset_zoom)
        
        self.save_png_btn = QPushButton()
        self.save_png_btn.setIcon(qta.icon("fa5s.camera", color="#94a3b8"))
        self.save_png_btn.setFixedSize(32, 32)
        self.save_png_btn.setToolTip("Save Graph as Image (PNG)")
        self.save_png_btn.clicked.connect(self.plot_canvas.save_graph)
        
        tb.addWidget(self.zoom_in_btn)
        tb.addWidget(self.zoom_out_btn)
        tb.addWidget(self.reset_zoom_btn)
        tb.addWidget(self.save_png_btn)
        tb.addStretch()
        
        self.right_layout.addLayout(tb)

    def register_input_validator(self, line_edit: QLineEdit, bounds_check_fn=None):
        """Monitors and styles QLineEdit based on valid input text dynamically."""
        line_edit.setClearButtonEnabled(True)
        line_edit.setPlaceholderText("Enter number...")
        
        def validate(text):
            if not text:
                line_edit.setStyleSheet("border: 1px solid #ef4444; background-color: rgba(239, 68, 68, 0.05);")
                return
            try:
                val = float(text)
                if bounds_check_fn and not bounds_check_fn(val):
                    raise ValueError()
                # Clear validation style override
                line_edit.setStyleSheet("")
            except ValueError:
                # Turn border red
                line_edit.setStyleSheet("border: 1px solid #ef4444; background-color: rgba(239, 68, 68, 0.05);")
                
        line_edit.textChanged.connect(validate)

    def show_toast(self, message: str, is_success: bool = True):
        """Triggers a self-dismissing overlay toast notification."""
        from src.ui.components.toast import ToastNotification
        top_window = self.window()
        if top_window:
            ToastNotification(top_window, message, is_success)

    def trigger_recalc(self):
        """Callback to execute calculation automatically on slider shifts."""
        self.calculate()

    # --- Virtual Methods to Override ---
    def setup_inputs(self, layout: QVBoxLayout):
        pass

    def setup_sliders(self, layout: QVBoxLayout):
        pass

    def init_plot(self):
        pass

    def update_plot(self):
        pass

    def calculate(self):
        pass

    def reset(self):
        pass

    def update_theme(self):
        self.plot_canvas.refresh_plot()
        self.update_plot()
