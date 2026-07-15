import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown,
    MULT, OHM
)

class RLTimeConstantCalculator(BaseCalculator):
    """Calculator for RL Time Constant and transient current response."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RL Time Constant Calculator",
            formula_str=f"τ = L / R   |   I(t) = Imax {MULT} (1 - e^(-t/τ)) [Buildup]   |   It = Imax {MULT} e^(-t/τ) [Decay]",
            explanation_str=(
                "The RL time constant (τ, tau) is the time required for current in an inductor "
                "to reach approximately 63.2% of its maximum steady-state value (Imax = Vin / R) "
                "when a voltage is applied, or decay down to 36.8% when the source is bypassed. "
                "The inductor opposes sudden changes in current."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Input Voltage (V_in)
        vin_layout = QHBoxLayout()
        vin_layout.addWidget(QLabel("Input Voltage (Vin):"))
        self.vin_input = QLineEdit("10.0")
        self.vin_unit = QComboBox()
        self.vin_unit.addItems(["V", "mV"])
        vin_layout.addWidget(self.vin_input)
        vin_layout.addWidget(self.vin_unit)
        layout.addLayout(vin_layout)

        # Resistor R
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("100")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["Ω", "kΩ", "MΩ"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Inductor L
        l_layout = QHBoxLayout()
        l_layout.addWidget(QLabel("Inductance (L):"))
        self.l_input = QLineEdit("100")
        self.l_unit = QComboBox()
        self.l_unit.addItems(["mH", "μH", "H"])
        l_layout.addWidget(self.l_input)
        l_layout.addWidget(self.l_unit)
        layout.addLayout(l_layout)

        # Connect listeners
        self.vin_input.textChanged.connect(self.trigger_recalc)
        self.r_input.textChanged.connect(self.trigger_recalc)
        self.l_input.textChanged.connect(self.trigger_recalc)
        self.vin_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.l_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # R slider
        layout.addWidget(QLabel("Resistance Slider (10 Ω - 1000 Ω):"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(10, 1000)
        self.r_slider.setValue(100)
        self.r_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r_slider)

        # L slider
        layout.addWidget(QLabel("Inductance Slider (10 mH - 1000 mH):"))
        self.l_slider = QSlider(Qt.Orientation.Horizontal)
        self.l_slider.setRange(10, 1000)
        self.l_slider.setValue(100)
        self.l_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.l_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("RL Inductor Transient Current Response")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Inductor Current Il (A)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        r_val = self.r_slider.value()
        l_val = self.l_slider.value()

        self.r_input.blockSignals(True)
        self.l_input.blockSignals(True)

        self.r_input.setText(f"{r_val}")
        self.r_unit.setCurrentIndex(0) # Ω
        
        self.l_input.setText(f"{l_val}")
        self.l_unit.setCurrentIndex(0) # mH

        self.r_input.blockSignals(False)
        self.l_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            vin = float(self.vin_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            
            if vin <= 0 or r <= 0 or l <= 0:
                raise ValueError("Values must be positive non-zero numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        vin_unit_text = self.vin_unit.currentText()
        r_unit_text = self.r_unit.currentText()
        l_unit_text = self.l_unit.currentText()

        vin_mult = {"V": 1.0, "mV": 1e-3}[vin_unit_text]
        r_mult = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6}[r_unit_text]
        l_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[l_unit_text]

        base_vin = vin * vin_mult
        base_r = r * r_mult
        base_l = l * l_mult

        # Calculations
        tau = base_l / base_r
        imax = base_vin / base_r

        # Display engineering values
        self.answer_label.setText(f"Time Constant (τ) = {format_eng(tau, 's')}   |   Imax = {format_eng(imax, 'A')}")

        breakdown = build_5_step_breakdown(
            formula=f"τ = L / R   |   Imax = Vin / R",
            given_dict={
                "Input Voltage (Vin)": f"{vin} {vin_unit_text}",
                "Resistance (R)": f"{r} {r_unit_text}",
                "Inductance (L)": f"{l} {l_unit_text}"
            },
            substitution=(
                f"τ = {format_value_base(l, l_unit_text)} H / {format_value_base(r, r_unit_text)} {OHM}\n"
                f"  Imax = {format_value_base(vin, vin_unit_text)} V / {format_value_base(r, r_unit_text)} {OHM}"
            ),
            calculation=(
                f"τ = {format_num(base_l)} / {format_num(base_r)} = {format_num(tau)} seconds\n"
                f"  Imax = {format_num(base_vin)} / {format_num(base_r)} = {format_num(imax)} A\n"
                f"  At 1τ: I = {format_num(imax * 0.6321)} A (63.2% build-up)\n"
                f"  At 5τ: I = {format_num(imax * 0.9932)} A (99.3% build-up)"
            ),
            final_ans=f"Time Constant (τ) = {format_eng(tau, 's')}   |   Imax = {format_eng(imax, 'A')}"
        )
        self.steps_text.setText(breakdown)

        self.current_vin = base_vin
        self.current_r = base_r
        self.current_tau = tau
        self.current_imax = imax
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        tau = getattr(self, 'current_tau', 0.001)
        imax = getattr(self, 'current_imax', 0.1)

        t_sweep = np.linspace(0, tau * 5, 400)
        i_buildup = imax * (1.0 - np.exp(-t_sweep / tau))
        i_decay = imax * np.exp(-t_sweep / tau)

        # Plot curves
        self.plot_canvas.ax.plot(t_sweep, i_buildup, color="#06b6d4", linewidth=2.5, label="Current Buildup Il(t)")
        self.plot_canvas.ax.plot(t_sweep, i_decay, color="#10b981", linewidth=2.5, label="Current Decay Il(t)")

        # Highlight 1 tau marker
        self.plot_canvas.ax.axvline(tau, color="#ef4444", linestyle="--", alpha=0.5, label="1 Time Constant (1τ)")
        self.plot_canvas.ax.scatter([tau], [imax * 0.632], color="#ef4444", s=80, zorder=5, label="63.2% Buildup")
        self.plot_canvas.ax.scatter([tau], [imax * 0.368], color="#ef4444", s=80, zorder=5, label="36.8% Decayed")

        self.plot_canvas.ax.set_title("RL Time Constant transient current curves")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Inductor Current (A)")
        self.plot_canvas.ax.legend(loc="right")
        self.plot_canvas.draw()

    def reset(self):
        self.vin_input.setText("10.0")
        self.vin_unit.setCurrentIndex(0)
        self.r_input.setText("100")
        self.r_unit.setCurrentIndex(0)
        self.l_input.setText("100")
        self.l_unit.setCurrentIndex(0)
        self.r_slider.setValue(100)
        self.l_slider.setValue(100)
        self.calculate()
