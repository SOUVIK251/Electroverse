import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown,
    MULT, OHM, PI
)

class CapacitiveReactanceCalculator(BaseCalculator):
    """Calculator for Capacitive Reactance (Xc = 1 / (2pi * f * C))."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Capacitive Reactance Calculator",
            formula_str=f"XC = 1 / (2{PI} {MULT} f {MULT} C)",
            explanation_str=(
                "Capacitive reactance (XC) is an opposition to the change of voltage across "
                "an element. Capacitive reactance is inversely proportional to both the signal "
                "frequency (f) and the capacitance (C). Reactance is measured in Ohms (Ω), but "
                "unlike resistance, it does not dissipate energy as heat (it stores it in the electric field)."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Frequency (f)
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency (f):"))
        self.freq_input = QLineEdit("1.0")
        self.freq_unit = QComboBox()
        self.freq_unit.addItems(["kHz", "Hz", "MHz"])
        freq_layout.addWidget(self.freq_input)
        freq_layout.addWidget(self.freq_unit)
        layout.addLayout(freq_layout)

        # Capacitance (C)
        cap_layout = QHBoxLayout()
        cap_layout.addWidget(QLabel("Capacitance (C):"))
        self.cap_input = QLineEdit("10.0")
        self.cap_unit = QComboBox()
        self.cap_unit.addItems(["nF", "μF", "pF", "mF"])
        cap_layout.addWidget(self.cap_input)
        cap_layout.addWidget(self.cap_unit)
        layout.addLayout(cap_layout)

        # Connect listeners
        self.freq_input.textChanged.connect(self.trigger_recalc)
        self.cap_input.textChanged.connect(self.trigger_recalc)
        self.freq_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.cap_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Freq slider
        layout.addWidget(QLabel("Frequency Slider (10 Hz - 10 kHz):"))
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setRange(10, 10000)
        self.freq_slider.setValue(1000)
        self.freq_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.freq_slider)

        # Cap slider
        layout.addWidget(QLabel("Capacitance Slider (1 nF - 1000 nF):"))
        self.cap_slider = QSlider(Qt.Orientation.Horizontal)
        self.cap_slider.setRange(1, 1000)
        self.cap_slider.setValue(10)
        self.cap_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.cap_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Capacitive Reactance vs Frequency (Decaying curve)")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Reactance XC (Ω)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        freq_val = self.freq_slider.value()
        cap_val = self.cap_slider.value()

        self.freq_input.blockSignals(True)
        self.cap_input.blockSignals(True)

        self.freq_input.setText(f"{freq_val}")
        self.freq_unit.setCurrentIndex(1) # Hz
        
        self.cap_input.setText(f"{cap_val}")
        self.cap_unit.setCurrentIndex(0) # nF

        self.freq_input.blockSignals(False)
        self.cap_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            freq = float(self.freq_input.text())
            cap = float(self.cap_input.text())
            
            if freq <= 0 or cap <= 0:
                raise ValueError("Values must be positive non-zero numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        freq_unit_text = self.freq_unit.currentText()
        cap_unit_text = self.cap_unit.currentText()

        freq_mult = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6}[freq_unit_text]
        cap_mult = {"nF": 1e-9, "μF": 1e-6, "pF": 1e-12, "mF": 1e-3}[cap_unit_text]

        base_freq = freq * freq_mult
        base_cap = cap * cap_mult

        # Xc calculation
        xc = 1.0 / (2.0 * np.pi * base_freq * base_cap)

        self.answer_label.setText(f"Reactance (XC) = {format_eng(xc, OHM)}")

        breakdown = build_5_step_breakdown(
            formula=f"XC = 1 / (2{PI} {MULT} f {MULT} C)",
            given_dict={
                "Frequency (f)": f"{freq} {freq_unit_text}",
                "Capacitance (C)": f"{cap} {cap_unit_text}"
            },
            substitution=f"XC = 1 / (2{PI} {MULT} {format_value_base(freq, freq_unit_text)} Hz {MULT} {format_value_base(cap, cap_unit_text)} F)",
            calculation=f"XC = 1 / (2{PI} {MULT} {format_num(base_freq)} {MULT} {format_num(base_cap)}) = {format_num(xc)} {OHM}",
            final_ans=f"Capacitive Reactance = {format_eng(xc, OHM)}"
        )
        self.steps_text.setText(breakdown)

        self.current_freq = base_freq
        self.current_cap = base_cap
        self.current_xc = xc
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.ax.set_yscale("log") # Log scale fits reactance decay nicely
        self.plot_canvas.apply_theme_colors()

        freq = getattr(self, 'current_freq', 1000.0)
        cap = getattr(self, 'current_cap', 1e-8)
        xc = getattr(self, 'current_xc', 15915.0)

        # Sweep freq from 10Hz to 10x selected freq
        freq_sweep = np.linspace(10, max(freq * 3, 20000.0), 300)
        xc_sweep = 1.0 / (2.0 * np.pi * freq_sweep * cap)

        self.plot_canvas.ax.plot(freq_sweep, xc_sweep, color="#06b6d4", linewidth=2.5, label="XC vs Frequency")
        
        # Highlight active operating point
        self.plot_canvas.ax.scatter([freq], [xc], color="#ef4444", s=80, zorder=5, label="Operating Point")

        self.plot_canvas.ax.set_title("Capacitive Reactance vs Frequency Sweep")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Reactance XC (Ω) [Log Scale]")
        self.plot_canvas.ax.legend(loc="upper right")
        self.plot_canvas.draw()

    def reset(self):
        self.freq_input.setText("1.0")
        self.freq_unit.setCurrentIndex(0)
        self.cap_input.setText("10.0")
        self.cap_unit.setCurrentIndex(0)
        self.freq_slider.setValue(1000)
        self.cap_slider.setValue(10)
        self.calculate()
