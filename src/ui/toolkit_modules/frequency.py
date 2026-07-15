import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown
)

class FrequencyCalculator(BaseCalculator):
    """Calculator for Frequency and Time Period (f = 1/T)."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Frequency & Period Calculator",
            formula_str="f = 1 / T   |   T = 1 / f",
            explanation_str=(
                "Frequency (f) is the number of occurrences of a repeating event per unit of time (cycles per second, Hz). "
                "The period (T) is the duration of one complete cycle in a repeating event, and it is the reciprocal of frequency."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Given Variable:"))
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Frequency (f)", "Time Period (T)"])
        self.mode_cb.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_cb)
        layout.addLayout(mode_layout)

        # Input Parameter
        self.param_layout = QHBoxLayout()
        self.param_label = QLabel("Frequency (f):")
        self.param_input = QLineEdit("1000")
        self.param_unit = QComboBox()
        self.param_unit.addItems(["Hz", "kHz", "MHz", "GHz"])
        self.param_layout.addWidget(self.param_label)
        self.param_layout.addWidget(self.param_input)
        self.param_layout.addWidget(self.param_unit)
        layout.addLayout(self.param_layout)

        # Connect listeners
        self.param_input.textChanged.connect(self.trigger_recalc)
        self.param_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Slider for logarithmic sweep (1 Hz to 10 kHz)
        layout.addWidget(QLabel("Frequency Slider (1 Hz - 10 kHz):"))
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setRange(1, 10000)
        self.freq_slider.setValue(1000) # 1 kHz
        self.freq_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.freq_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Waveform Cycles (Amplitude vs Time)")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Amplitude")
        self.plot_canvas.refresh_plot()

    def on_mode_changed(self, idx: int):
        if idx == 0:  # Given f, find T
            self.param_label.setText("Frequency (f):")
            self.param_unit.clear()
            self.param_unit.addItems(["Hz", "kHz", "MHz", "GHz"])
            self.param_input.setText("1000")
        else:  # Given T, find f
            self.param_label.setText("Time Period (T):")
            self.param_unit.clear()
            self.param_unit.addItems(["ms", "s", "μs", "ns"])
            self.param_input.setText("1.0")

        self.trigger_recalc()

    def on_slider_changed(self):
        freq_val = self.freq_slider.value()
        mode = self.mode_cb.currentIndex()

        self.param_input.blockSignals(True)

        if mode == 0:  # Frequency mode
            self.param_input.setText(f"{freq_val}")
            self.param_unit.setCurrentIndex(0)  # Hz
        else:  # Period mode
            period_ms = 1000.0 / freq_val
            self.param_input.setText(f"{period_ms:.4f}")
            self.param_unit.setCurrentIndex(0)  # ms

        self.param_input.blockSignals(False)
        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        mode = self.mode_cb.currentIndex()
        
        try:
            val = float(self.param_input.text())
            if val <= 0:
                raise ValueError("Value must be a positive non-zero number.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        unit = self.param_unit.currentText()
        
        # Base conversion
        f, t = 0.0, 0.0

        if mode == 0:  # Frequency given, solve for T
            mult = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}[unit]
            f = val * mult
            t = 1.0 / f
            
            self.answer_label.setText(f"Time Period (T) = {format_eng(t, 's')}")
            
            breakdown = build_5_step_breakdown(
                formula="T = 1 / f",
                given_dict={"Frequency (f)": f"{val} {unit}"},
                substitution=f"T = 1 / ({format_value_base(val, unit)} Hz)",
                calculation=f"T = 1 / {format_num(f)} = {format_num(t)} seconds",
                final_ans=f"Time Period (T) = {format_eng(t, 's')}"
            )
        else:  # Period given, solve for f
            mult = {"s": 1.0, "ms": 1e-3, "μs": 1e-6, "ns": 1e-9}[unit]
            t = val * mult
            f = 1.0 / t

            self.answer_label.setText(f"Frequency (f) = {format_eng(f, 'Hz')}")
            
            breakdown = build_5_step_breakdown(
                formula="f = 1 / T",
                given_dict={"Time Period (T)": f"{val} {unit}"},
                substitution=f"f = 1 / ({format_value_base(val, unit)} s)",
                calculation=f"f = 1 / {format_num(t)} = {format_num(f)} Hz",
                final_ans=f"Frequency = {format_eng(f, 'Hz')}"
            )

        self.steps_text.setText(breakdown)
        self.current_f = f
        self.current_t = t
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        t = getattr(self, 'current_t', 0.001)

        # Plot 2 full cycles of a sine wave
        t_sweep = np.linspace(0, t * 2, 400)
        amplitude = np.sin(2 * np.pi * (1.0 / t) * t_sweep)

        self.plot_canvas.ax.plot(t_sweep, amplitude, color="#06b6d4", linewidth=2.5, label="Sine Wave (1V peak)")
        
        # Highlight period range
        self.plot_canvas.ax.axvline(t, color="#ef4444", linestyle="--", alpha=0.6, label="First Cycle Limit (T)")
        self.plot_canvas.ax.axvspan(0, t, color=(6/255, 182/255, 212/255, 0.08), label="One Time Period")

        self.plot_canvas.ax.set_title("Visual Waveform Cycles")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Amplitude")
        self.plot_canvas.ax.legend(loc="upper right")
        self.plot_canvas.draw()

    def reset(self):
        self.mode_cb.setCurrentIndex(0)
        self.param_input.setText("1000")
        self.param_unit.setCurrentIndex(0)
        self.freq_slider.setValue(1000)
        self.calculate()
