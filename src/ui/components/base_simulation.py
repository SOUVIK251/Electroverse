from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QScrollArea, QSizePolicy, QLineEdit, QSlider, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal
import qtawesome as qta
import numpy as np

from src.ui.components.math_plot import MathPlotCanvas
from src.core.logger import log
from src.core.config import config_manager

class BaseSimulation(QWidget):
    """Base class for all Simulation Lab modules.
    
    Provides:
    - Resizable QSplitter split-pane panel layout.
    - Left Scrollable Parameter Input & Breakdown Panel.
    - Right Plotting and Visualizer Animation Area.
    - Standard Play/Pause/Reset simulation clock loop.
    """
    
    def __init__(self, title: str, formula_str: str, explanation_str: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.formula_str = formula_str
        self.explanation_str = explanation_str
        
        # Simulation clock state
        self.sim_time = 0.0
        self.is_running = False
        self.sim_speed = 1.0  # speed factor
        self.orig_limits_saved = False
        
        # Simulation Clock Timer (30 FPS)
        self.timer = QTimer(self)
        self.timer.setInterval(33)  # ~30ms per tick
        self.timer.timeout.connect(self.on_timer_tick)
        
        # Central Splitter Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("sim-splitter")
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1e293b;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #06b6d4;
            }
        """)
        main_layout.addWidget(self.splitter)

        # -------------------------------------------------------------
        # Left Panel (Scrollable Details / Formulas / Inputs)
        # -------------------------------------------------------------
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(5, 5, 15, 5)
        self.left_layout.setSpacing(15)
        
        # Title Header
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #06b6d4;")
        self.left_layout.addWidget(self.title_label)
        
        # Formula Card (Collapsible)
        self.setup_formula_card()
        
        # Simulation Parameters Card
        self.inputs_card = QFrame()
        self.inputs_card.setObjectName("card-panel")
        self.inputs_layout = QVBoxLayout(self.inputs_card)
        self.inputs_layout.setContentsMargins(15, 15, 15, 15)
        self.inputs_layout.setSpacing(12)
        
        inputs_header = QLabel("Simulation Controls")
        inputs_header.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10b981;")
        self.inputs_layout.addWidget(inputs_header)
        
        self.setup_inputs(self.inputs_layout)
        self.left_layout.addWidget(self.inputs_card)

        # Calculations Steps Card
        self.setup_steps_card()
        
        # Concept Explanation Card (Collapsible)
        self.setup_explanation_card()
        
        self.left_scroll.setWidget(self.left_container)
        self.splitter.addWidget(self.left_scroll)

        # -------------------------------------------------------------
        # Right Panel (Interactive Plot, Clock Controls, Animated Visualizer)
        # -------------------------------------------------------------
        self.right_container = QFrame()
        self.right_container.setObjectName("card-panel")
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(12)

        # Right Header Layout
        right_header_layout = QHBoxLayout()
        right_header = QLabel("Real-Time Waveform Visualization")
        right_header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06b6d4;")
        
        self.coord_label = QLabel("")
        self.coord_label.setStyleSheet("font-size: 10pt; color: #94a3b8; font-weight: 500;")
        
        right_header_layout.addWidget(right_header)
        right_header_layout.addStretch()
        right_header_layout.addWidget(self.coord_label)
        self.right_layout.addLayout(right_header_layout)

        # Math Plot Canvas
        self.plot_canvas = MathPlotCanvas(self)
        self.plot_canvas.coordinates_updated.connect(self.coord_label.setText)
        self.right_layout.addWidget(self.plot_canvas, stretch=1)

        # Plot Controls Toolbar
        self.setup_chart_controls()

        # Simulation Clock Panel
        self.setup_clock_panel()

        # Custom Interactive Animation Visualizer Placement
        self.visualizer_container = QWidget()
        self.visualizer_layout = QVBoxLayout(self.visualizer_container)
        self.visualizer_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_visualizer(self.visualizer_layout)
        self.right_layout.addWidget(self.visualizer_container)

        self.splitter.addWidget(self.right_container)
        
        # Default split sizing
        self.splitter.setSizes([450, 650])
        
        # Load initialization parameters
        self.init_simulation()

    def setup_formula_card(self):
        content = QLabel(self.formula_str)
        content.setStyleSheet("font-size: 12pt; font-weight: bold; color: #f8fafc; padding: 5px;")
        content.setWordWrap(True)
        card = self.make_card_collapsible("Mathematical Formula", content)
        self.left_layout.addWidget(card)

    def setup_explanation_card(self):
        content = QLabel(self.explanation_str)
        content.setStyleSheet("font-size: 9.5pt; color: #94a3b8; line-height: 1.4;")
        content.setWordWrap(True)
        card = self.make_card_collapsible("Practical Engineering Notes", content)
        self.left_layout.addWidget(card)

    def make_card_collapsible(self, title_text: str, content_widget: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("card-panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

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

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.05); height: 1px; border: none;")
        layout.addWidget(sep)

        layout.addWidget(content_widget)

        def toggle():
            is_visible = content_widget.isVisible()
            content_widget.setVisible(not is_visible)
            sep.setVisible(not is_visible)
            icon_str = "fa5s.chevron-right" if is_visible else "fa5s.chevron-down"
            toggle_btn.setIcon(icon_str)

        toggle_btn.clicked.connect(toggle)
        header_title.mouseReleaseEvent = lambda e: toggle()

        return card

    def setup_steps_card(self):
        self.steps_card = QFrame()
        self.steps_card.setObjectName("card-panel")
        layout = QVBoxLayout(self.steps_card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header = QLabel("Simulation Results Summary")
        header.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10b981;")
        
        self.steps_text = QLabel("Start the simulation to display results.")
        self.steps_text.setStyleSheet("font-size: 10pt; color: #f8fafc;")
        self.steps_text.setWordWrap(True)
        self.steps_text.setTextFormat(Qt.TextFormat.MarkdownText)

        self.answer_box = QFrame()
        self.answer_box.setStyleSheet("background-color: rgba(6, 182, 212, 0.08); border: 1px solid #06b6d4; border-radius: 6px;")
        ab_layout = QVBoxLayout(self.answer_box)
        ab_layout.setContentsMargins(10, 10, 10, 10)
        
        self.answer_label = QLabel("State: Ready")
        self.answer_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06b6d4;")
        ab_layout.addWidget(self.answer_label)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 9.5pt; font-weight: 500;")
        self.error_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self.steps_text)
        layout.addWidget(self.answer_box)
        layout.addWidget(self.error_label)
        self.left_layout.addWidget(self.steps_card)

    def setup_chart_controls(self):
        tb = QHBoxLayout()
        tb.setContentsMargins(0, 0, 0, 0)
        tb.setSpacing(8)
        
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(qta.icon("fa5s.search-plus", color="#94a3b8"))
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self.plot_canvas.zoom_in)
        
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(qta.icon("fa5s.search-minus", color="#94a3b8"))
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.plot_canvas.zoom_out)
        
        self.reset_zoom_btn = QPushButton()
        self.reset_zoom_btn.setIcon(qta.icon("fa5s.compress", color="#94a3b8"))
        self.reset_zoom_btn.setFixedSize(30, 30)
        self.reset_zoom_btn.setToolTip("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.plot_canvas.reset_zoom)
        
        self.save_png_btn = QPushButton()
        self.save_png_btn.setIcon(qta.icon("fa5s.camera", color="#94a3b8"))
        self.save_png_btn.setFixedSize(30, 30)
        self.save_png_btn.setToolTip("Save Graph as Image (PNG)")
        self.save_png_btn.clicked.connect(self.plot_canvas.save_graph)
        
        tb.addWidget(self.zoom_in_btn)
        tb.addWidget(self.zoom_out_btn)
        tb.addWidget(self.reset_zoom_btn)
        tb.addWidget(self.save_png_btn)
        tb.addStretch()
        self.right_layout.addLayout(tb)

    def setup_clock_panel(self):
        """Creates standard playback controls (Play, Pause, Reset, Speed Slider)."""
        panel = QFrame()
        panel.setStyleSheet("background-color: rgba(30, 41, 59, 0.4); border-radius: 8px; border: 1px solid #1e293b;")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Play/Pause Action Button
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
        self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)

        # Reset button
        self.reset_btn = QPushButton()
        self.reset_btn.setFixedSize(36, 36)
        self.reset_btn.setIcon(qta.icon("fa5s.redo", color="#ffffff"))
        self.reset_btn.setStyleSheet("background-color: #3b82f6; border: none; border-radius: 18px;")
        self.reset_btn.clicked.connect(self.reset_simulation)
        layout.addWidget(self.reset_btn)

        # Speed Controls Slider
        layout.addWidget(QLabel("Simulation Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 20)  # 0.1x to 2.0x
        self.speed_slider.setValue(10)    # 1.0x
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        layout.addWidget(self.speed_slider)

        self.speed_lbl = QLabel("1.0x")
        self.speed_lbl.setStyleSheet("font-weight: bold; color: #06b6d4;")
        layout.addWidget(self.speed_lbl)

        layout.addStretch()
        
        # Active Time Step tracker label
        self.time_lbl = QLabel("Sim Time: 0.00s")
        self.time_lbl.setStyleSheet("font-family: Consolas; font-weight: bold; color: #f8fafc;")
        layout.addWidget(self.time_lbl)

        self.right_layout.addWidget(panel)

    def register_input_validator(self, line_edit: QLineEdit, bounds_check_fn=None):
        line_edit.setClearButtonEnabled(True)
        line_edit.setPlaceholderText("Enter value...")
        
        def validate(text):
            if not text:
                line_edit.setStyleSheet("border: 1px solid #ef4444; background-color: rgba(239, 68, 68, 0.05);")
                return
            try:
                val = float(text)
                if bounds_check_fn and not bounds_check_fn(val):
                    raise ValueError()
                line_edit.setStyleSheet("")
            except ValueError:
                line_edit.setStyleSheet("border: 1px solid #ef4444; background-color: rgba(239, 68, 68, 0.05);")
                
        line_edit.textChanged.connect(validate)

    def show_toast(self, message: str, is_success: bool = True):
        from src.ui.components.toast import ToastNotification
        top_window = self.window()
        if top_window and hasattr(top_window, "show_toast"):
            top_window.show_toast(message, is_success)

    def toggle_play(self):
        """Toggles clock looping on click."""
        if self.is_running:
            self.timer.stop()
            self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
            self.is_running = False
            self.answer_label.setText("State: Paused")
            self.show_toast("Simulation Paused.")
        else:
            self.timer.start()
            self.play_btn.setIcon(qta.icon("fa5s.pause", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #f59e0b; border: none; border-radius: 18px;")
            self.is_running = True
            self.answer_label.setText("State: Simulating...")
            self.show_toast("Simulation Started.")

    def reset_simulation(self):
        """Resets clock cycle back to 0."""
        self.timer.stop()
        self.is_running = False
        self.sim_time = 0.0
        self.time_lbl.setText("Sim Time: 0.00s")
        self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
        self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
        self.answer_label.setText("State: Ready")
        self.reset_data()
        self.show_toast("Simulation Reset.")

    def on_speed_changed(self, val):
        self.sim_speed = val / 10.0
        self.speed_lbl.setText(f"{self.sim_speed:.1f}x")

    def on_timer_tick(self):
        """Triggers updates on every interval timer cycle."""
        # Increment time step by speed factor
        dt = 0.033 * self.sim_speed
        self.sim_time += dt
        self.time_lbl.setText(f"Sim Time: {self.sim_time:.2f}s")
        self.update_simulation_step(dt)

    # --- Virtual interface methods ---
    def setup_inputs(self, layout: QVBoxLayout):
        pass

    def setup_sliders(self, layout: QVBoxLayout):
        pass

    def setup_visualizer(self, layout: QVBoxLayout):
        pass

    def init_simulation(self):
        pass

    def reset_data(self):
        pass

    def update_simulation_step(self, dt: float):
        pass

    def update_theme(self):
        self.plot_canvas.refresh_plot()
        self.update_simulation_step(0.0)
