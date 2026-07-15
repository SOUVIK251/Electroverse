import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown,
    MULT, OHM, SQRT, PI
)

class RLCResonanceCalculator(BaseCalculator):
    """Calculator for Series RLC Resonance Frequency, Q-Factor, and Bandwidth."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RLC Resonance Calculator (Series)",
            formula_str=f"f0 = 1 / (2{PI} {MULT} {SQRT}(L {MULT} C))   |   Q = (1/R) {MULT} {SQRT}(L/C)   |   BW = f0 / Q = R / (2{PI} {MULT} L)",
            explanation_str=(
                "Resonance in a series RLC circuit occurs when the capacitive reactance (Xc) "
                "equals the inductive reactance (Xl). At this frequency, the reactances cancel each other out, "
                "the total impedance is at its minimum (equal to R), and current is at its maximum. "
                "The Quality Factor (Q) dictates the sharpness/selectivity of the resonance peak."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Input Voltage (V_in) to calculate actual current peak
        vin_layout = QHBoxLayout()
        vin_layout.addWidget(QLabel("Applied Voltage (Vin):"))
        self.vin_input = QLineEdit("5.0")
        self.vin_unit = QComboBox()
        self.vin_unit.addItems(["V", "mV"])
        vin_layout.addWidget(self.vin_input)
        vin_layout.addWidget(self.vin_unit)
        layout.addLayout(vin_layout)

        # Resistor R
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("10.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["Ω", "kΩ"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Inductor L
        l_layout = QHBoxLayout()
        l_layout.addWidget(QLabel("Inductance (L):"))
        self.l_input = QLineEdit("10.0")
        self.l_unit = QComboBox()
        self.l_unit.addItems(["mH", "μH", "H"])
        l_layout.addWidget(self.l_input)
        l_layout.addWidget(self.l_unit)
        layout.addLayout(l_layout)

        # Capacitor C
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Capacitance (C):"))
        self.c_input = QLineEdit("100")
        self.c_unit = QComboBox()
        self.c_unit.addItems(["nF", "μF", "pF"])
        c_layout.addWidget(self.c_input)
        c_layout.addWidget(self.c_unit)
        layout.addLayout(c_layout)

        # Connect listeners
        self.vin_input.textChanged.connect(self.trigger_recalc)
        self.r_input.textChanged.connect(self.trigger_recalc)
        self.l_input.textChanged.connect(self.trigger_recalc)
        self.c_input.textChanged.connect(self.trigger_recalc)
        self.vin_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.l_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.c_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # R slider
        layout.addWidget(QLabel("Resistance Slider (1 Ω - 200 Ω):"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(1, 200)
        self.r_slider.setValue(10)
        self.r_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r_slider)

        # L slider
        layout.addWidget(QLabel("Inductance Slider (1 mH - 50 mH):"))
        self.l_slider = QSlider(Qt.Orientation.Horizontal)
        self.l_slider.setRange(1, 50)
        self.l_slider.setValue(10)
        self.l_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.l_slider)

        # C slider
        layout.addWidget(QLabel("Capacitance Slider (10 nF - 1000 nF):"))
        self.c_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_slider.setRange(10, 1000)
        self.c_slider.setValue(100)
        self.c_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.c_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("RLC Bandwidth Current Response Sweep")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Current I (A)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        r_val = self.r_slider.value()
        l_val = self.l_slider.value()
        c_val = self.c_slider.value()

        self.r_input.blockSignals(True)
        self.l_input.blockSignals(True)
        self.c_input.blockSignals(True)

        self.r_input.setText(f"{r_val}")
        self.r_unit.setCurrentIndex(0) # Ω
        
        self.l_input.setText(f"{l_val}")
        self.l_unit.setCurrentIndex(0) # mH
        
        self.c_input.setText(f"{c_val}")
        self.c_unit.setCurrentIndex(0) # nF

        self.r_input.blockSignals(False)
        self.l_input.blockSignals(False)
        self.c_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            vin = float(self.vin_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            
            if vin <= 0 or r <= 0 or l <= 0 or c <= 0:
                raise ValueError("Values must be positive non-zero numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        vin_unit_text = self.vin_unit.currentText()
        r_unit_text = self.r_unit.currentText()
        l_unit_text = self.l_unit.currentText()
        c_unit_text = self.c_unit.currentText()

        vin_mult = {"V": 1.0, "mV": 1e-3}[vin_unit_text]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[r_unit_text]
        l_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[l_unit_text]
        c_mult = {"nF": 1e-9, "μF": 1e-6, "pF": 1e-12}[c_unit_text]

        base_vin = vin * vin_mult
        base_r = r * r_mult
        base_l = l * l_mult
        base_c = c * c_mult

        # Resonance formulas
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
        q = (1.0 / base_r) * np.sqrt(base_l / base_c)
        bw = f0 / q
        imax = base_vin / base_r

        self.answer_label.setText(f"Resonant Freq (f0) = {format_eng(f0, 'Hz')}   |   Q-Factor = {format_num(q, 3)}   |   Bandwidth = {format_eng(bw, 'Hz')}")

        breakdown = build_5_step_breakdown(
            formula=f"f0 = 1 / (2{PI} {MULT} {SQRT}(L {MULT} C))   |   Q = (1/R) {MULT} {SQRT}(L/C)   |   BW = f0 / Q",
            given_dict={
                "Applied Voltage (Vin)": f"{vin} {vin_unit_text}",
                "Resistance (R)": f"{r} {r_unit_text}",
                "Inductance (L)": f"{l} {l_unit_text}",
                "Capacitance (C)": f"{c} {c_unit_text}"
            },
            substitution=(
                f"f0 = 1 / (2{PI} {MULT} {SQRT}({format_value_base(l, l_unit_text)} H {MULT} {format_value_base(c, c_unit_text)} F))\n"
                f"  Q = (1 / {format_value_base(r, r_unit_text)} {OHM}) {MULT} {SQRT}({format_value_base(l, l_unit_text)} H / {format_value_base(c, c_unit_text)} F)\n"
                f"  BW = f0 / Q"
            ),
            calculation=(
                f"f0 = 1 / (2{PI} {MULT} {SQRT}({format_num(base_l)} {MULT} {format_num(base_c)})) = {format_num(f0)} Hz\n"
                f"  Q = (1 / {format_num(base_r)}) {MULT} {SQRT}({format_num(base_l)} / {format_num(base_c)}) = {format_num(q, 3)}\n"
                f"  BW = {format_num(f0)} / {format_num(q, 3)} = {format_num(bw)} Hz\n"
                f"  Peak Current (Imax) = {format_num(imax)} A\n"
                f"  Half-Power Range: {format_num(f0 - bw/2)} Hz to {format_num(f0 + bw/2)} Hz"
            ),
            final_ans=f"f0 = {format_eng(f0, 'Hz')}   |   Q-Factor = {format_num(q, 3)}   |   Bandwidth = {format_eng(bw, 'Hz')}"
        )
        self.steps_text.setText(breakdown)

        self.current_vin = base_vin
        self.current_r = base_r
        self.current_l = base_l
        self.current_c = base_c
        self.current_f0 = f0
        self.current_q = q
        self.current_bw = bw
        self.current_imax = imax
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        vin = getattr(self, 'current_vin', 5.0)
        r = getattr(self, 'current_r', 10.0)
        l = getattr(self, 'current_l', 0.01)
        c = getattr(self, 'current_c', 1e-7)
        f0 = getattr(self, 'current_f0', 5032.0)
        bw = getattr(self, 'current_bw', 159.0)
        imax = getattr(self, 'current_imax', 0.5)

        # Sweeping frequency from f0 - 3*bw to f0 + 3*bw
        f_min = max(10.0, f0 - bw * 4)
        f_max = f0 + bw * 4
        f_sweep = np.linspace(f_min, f_max, 500)
        omega = 2.0 * np.pi * f_sweep
        
        # Impedance Z = R + j*(wL - 1/wC)
        z = np.sqrt(r**2 + (omega * l - 1.0 / (omega * c))**2)
        i_sweep = vin / z

        self.plot_canvas.ax.plot(f_sweep, i_sweep, color="#06b6d4", linewidth=2.5, label="I vs Freq")
        
        # Resonance marker
        self.plot_canvas.ax.scatter([f0], [imax], color="#ef4444", s=80, zorder=5, label="Resonance (f0)")
        
        # Half power points (70.7%)
        ihp = imax / np.sqrt(2.0)
        self.plot_canvas.ax.plot([f0 - bw/2, f0 + bw/2], [ihp, ihp], color="#ef4444", linestyle=":", label="-3dB Bandwidth")
        self.plot_canvas.ax.scatter([f0 - bw/2, f0 + bw/2], [ihp, ihp], color="#f59e0b", s=50, zorder=5)

        self.plot_canvas.ax.set_title(f"Series RLC Resonance Peak (Q = {self.current_q:.2f})")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Current (A)")
        self.plot_canvas.ax.legend(loc="upper right")
        self.plot_canvas.draw()

    def reset(self):
        self.vin_input.setText("5.0")
        self.vin_unit.setCurrentIndex(0)
        self.r_input.setText("10.0")
        self.r_unit.setCurrentIndex(0)
        self.l_input.setText("10.0")
        self.l_unit.setCurrentIndex(0)
        self.c_input.setText("100")
        self.c_unit.setCurrentIndex(0)
        self.r_slider.setValue(10)
        self.l_slider.setValue(10)
        self.c_slider.setValue(100)
        self.calculate()
