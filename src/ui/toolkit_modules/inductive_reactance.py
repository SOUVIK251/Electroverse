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

class InductiveReactanceCalculator(BaseCalculator):
    """Calculator for Inductive Reactance (Xl = 2pi * f * L)."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Inductive Reactance Calculator",
            formula_str=f"XL = 2{PI} {MULT} f {MULT} L",
            explanation_str=(
                "Inductive reactance (XL) is the opposition to a change of current through "
                "an inductor. Inductive reactance is directly proportional to both the frequency (f) "
                "and the inductance (L). Reactance is measured in Ohms (Ω), but unlike resistance, "
                "it does not dissipate energy as heat (it stores it in the magnetic field)."
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

        # Inductance (L)
        ind_layout = QHBoxLayout()
        ind_layout.addWidget(QLabel("Inductance (L):"))
        self.ind_input = QLineEdit("10.0")
        self.ind_unit = QComboBox()
        self.ind_unit.addItems(["mH", "μH", "H"])
        ind_layout.addWidget(self.ind_input)
        self.ind_unit = self.ind_unit # Wait, self.ind_unit.addItems is correct
        ind_layout.addWidget(self.ind_unit)
        layout.addLayout(ind_layout)

        # Connect listeners
        self.freq_input.textChanged.connect(self.trigger_recalc)
        self.ind_input.textChanged.connect(self.trigger_recalc)
        self.freq_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.ind_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Freq slider
        layout.addWidget(QLabel("Frequency Slider (10 Hz - 10 kHz):"))
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setRange(10, 10000)
        self.freq_slider.setValue(1000)
        self.freq_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.freq_slider)

        # Inductance slider
        layout.addWidget(QLabel("Inductance Slider (1 mH - 1000 mH):"))
        self.ind_slider = QSlider(Qt.Orientation.Horizontal)
        self.ind_slider.setRange(1, 1000)
        self.ind_slider.setValue(10)
        self.ind_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.ind_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Inductive Reactance vs Frequency (Linear slope)")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Reactance XL (Ω)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        freq_val = self.freq_slider.value()
        ind_val = self.ind_slider.value()

        self.freq_input.blockSignals(True)
        self.ind_input.blockSignals(True)

        self.freq_input.setText(f"{freq_val}")
        self.freq_unit.setCurrentIndex(1) # Hz
        
        self.ind_input.setText(f"{ind_val}")
        self.ind_unit.setCurrentIndex(0) # mH

        self.freq_input.blockSignals(False)
        self.ind_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            freq = float(self.freq_input.text())
            ind = float(self.ind_input.text())
            
            if freq <= 0 or ind <= 0:
                raise ValueError("Values must be positive non-zero numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        freq_unit_text = self.freq_unit.currentText()
        ind_unit_text = self.ind_unit.currentText()

        freq_mult = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6}[freq_unit_text]
        ind_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[ind_unit_text]

        base_freq = freq * freq_mult
        base_ind = ind * ind_mult

        # Xl calculation
        xl = 2.0 * np.pi * base_freq * base_ind

        self.answer_label.setText(f"Reactance (XL) = {format_eng(xl, OHM)}")

        breakdown = build_5_step_breakdown(
            formula=f"XL = 2{PI} {MULT} f {MULT} L",
            given_dict={
                "Frequency (f)": f"{freq} {freq_unit_text}",
                "Inductance (L)": f"{ind} {ind_unit_text}"
            },
            substitution=f"XL = 2{PI} {MULT} {format_value_base(freq, freq_unit_text)} Hz {MULT} {format_value_base(ind, ind_unit_text)} H",
            calculation=f"XL = 2{PI} {MULT} {format_num(base_freq)} {MULT} {format_num(base_ind)} = {format_num(xl)} {OHM}",
            final_ans=f"Inductive Reactance = {format_eng(xl, OHM)}"
        )
        self.steps_text.setText(breakdown)

        self.current_freq = base_freq
        self.current_ind = base_ind
        self.current_xl = xl
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        freq = getattr(self, 'current_freq', 1000.0)
        ind = getattr(self, 'current_ind', 0.01)
        xl = getattr(self, 'current_xl', 62.83)

        # Sweep freq from 0 to 3x selected freq
        freq_sweep = np.linspace(0, max(freq * 3, 5000.0), 300)
        xl_sweep = 2.0 * np.pi * freq_sweep * ind

        self.plot_canvas.ax.plot(freq_sweep, xl_sweep, color="#06b6d4", linewidth=2.5, label="XL vs Frequency")
        
        # Highlight active operating point
        self.plot_canvas.ax.scatter([freq], [xl], color="#ef4444", s=80, zorder=5, label="Operating Point")

        self.plot_canvas.ax.set_title("Inductive Reactance vs Frequency Sweep")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Reactance XL (Ω)")
        self.plot_canvas.ax.legend(loc="upper left")
        self.plot_canvas.draw()

    def reset(self):
        self.freq_input.setText("1.0")
        self.freq_unit.setCurrentIndex(0)
        self.ind_input.setText("10.0")
        self.ind_unit.setCurrentIndex(0)
        self.freq_slider.setValue(1000)
        self.ind_slider.setValue(10)
        self.calculate()
