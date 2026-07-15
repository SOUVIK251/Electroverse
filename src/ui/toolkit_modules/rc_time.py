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

class RCTimeConstantCalculator(BaseCalculator):
    """Calculator for RC Time Constant and Transient response."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RC Time Constant Calculator",
            formula_str=f"τ = R {MULT} C   |   Vc(t) = Vin {MULT} (1 - e^(-t/τ)) [Charging]   |   Vc(t) = Vin {MULT} e^(-t/τ) [Discharging]",
            explanation_str=(
                "The RC time constant (τ, tau) is the time required to charge a capacitor "
                "through a resistor to approximately 63.2% of its full charge voltage, or "
                "discharge it down to 36.8% of its initial charge voltage. After 5 time constants (5τ), "
                "the transient is practically complete (99.3%)."
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
        self.r_input = QLineEdit("10.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["kΩ", "Ω", "MΩ"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Capacitor C
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Capacitance (C):"))
        self.c_input = QLineEdit("100")
        self.c_unit = QComboBox()
        self.c_unit.addItems(["μF", "nF", "pF", "mF"])
        c_layout.addWidget(self.c_input)
        c_layout.addWidget(self.c_unit)
        layout.addLayout(c_layout)

        # Connect listeners
        self.vin_input.textChanged.connect(self.trigger_recalc)
        self.r_input.textChanged.connect(self.trigger_recalc)
        self.c_input.textChanged.connect(self.trigger_recalc)
        self.vin_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.c_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # R slider
        layout.addWidget(QLabel("Resistance Slider (100 Ω - 100 kΩ):"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(100, 100000)
        self.r_slider.setValue(10000) # 10k
        self.r_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r_slider)

        # C slider
        layout.addWidget(QLabel("Capacitance Slider (1 μF - 1000 μF):"))
        self.c_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_slider.setRange(1, 1000)
        self.c_slider.setValue(100) # 100uF
        self.c_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.c_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("RC Capacitor Transient Response (Charging / Discharging)")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Capacitor Voltage Vc (V)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        r_val = self.r_slider.value()
        c_val = self.c_slider.value()

        self.r_input.blockSignals(True)
        self.c_input.blockSignals(True)

        self.r_input.setText(f"{r_val / 1000.0}")
        self.r_unit.setCurrentIndex(0) # kΩ
        
        self.c_input.setText(f"{c_val}")
        self.c_unit.setCurrentIndex(0) # μF

        self.r_input.blockSignals(False)
        self.c_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            vin = float(self.vin_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            
            if vin <= 0 or r <= 0 or c <= 0:
                raise ValueError("Values must be positive non-zero numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        vin_unit_text = self.vin_unit.currentText()
        r_unit_text = self.r_unit.currentText()
        c_unit_text = self.c_unit.currentText()

        vin_mult = {"V": 1.0, "mV": 1e-3}[vin_unit_text]
        r_mult = {"kΩ": 1e3, "Ω": 1.0, "MΩ": 1e6}[r_unit_text]
        c_mult = {"μF": 1e-6, "nF": 1e-9, "pF": 1e-12, "mF": 1e-3}[c_unit_text]

        base_vin = vin * vin_mult
        base_r = r * r_mult
        base_c = c * c_mult

        # Time constant calculation
        tau = base_r * base_c
        
        # Display engineering values
        self.answer_label.setText(f"Time Constant (τ) = {format_eng(tau, 's')}")

        breakdown = build_5_step_breakdown(
            formula=f"τ = R {MULT} C",
            given_dict={
                "Resistance (R)": f"{r} {r_unit_text}",
                "Capacitance (C)": f"{c} {c_unit_text}"
            },
            substitution=f"τ = {format_value_base(r, r_unit_text)} {OHM} {MULT} {format_value_base(c, c_unit_text)} F",
            calculation=(
                f"τ = {format_num(base_r)} {MULT} {format_num(base_c)} = {format_num(tau)} seconds\n"
                f"  At 1τ: Vc = {format_num(base_vin * 0.6321)} V (63.2% charged)\n"
                f"  At 5τ: Vc = {format_num(base_vin * 0.9932)} V (99.3% charged)"
            ),
            final_ans=f"Time Constant (τ) = {format_eng(tau, 's')}"
        )
        self.steps_text.setText(breakdown)

        self.current_vin = base_vin
        self.current_tau = tau
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        vin = getattr(self, 'current_vin', 10.0)
        tau = getattr(self, 'current_tau', 0.01)

        # Plot sweep up to 5 tau
        t_sweep = np.linspace(0, tau * 5, 400)
        v_charging = vin * (1.0 - np.exp(-t_sweep / tau))
        v_discharging = vin * np.exp(-t_sweep / tau)

        # Plot curves
        self.plot_canvas.ax.plot(t_sweep, v_charging, color="#06b6d4", linewidth=2.5, label="Charging Vc(t)")
        self.plot_canvas.ax.plot(t_sweep, v_discharging, color="#10b981", linewidth=2.5, label="Discharging Vc(t)")

        # Highlight 1 tau marker
        self.plot_canvas.ax.axvline(tau, color="#ef4444", linestyle="--", alpha=0.5, label="1 Time Constant (1τ)")
        self.plot_canvas.ax.scatter([tau], [vin * 0.632], color="#ef4444", s=80, zorder=5, label="63.2% Charged")
        self.plot_canvas.ax.scatter([tau], [vin * 0.368], color="#ef4444", s=80, zorder=5, label="36.8% Discharged")

        # Format axes
        self.plot_canvas.ax.set_title("RC Time Constant transient curves")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Capacitor Voltage (V)")
        self.plot_canvas.ax.legend(loc="right")
        self.plot_canvas.draw()

    def reset(self):
        self.vin_input.setText("10.0")
        self.vin_unit.setCurrentIndex(0)
        self.r_input.setText("10.0")
        self.r_unit.setCurrentIndex(0)
        self.c_input.setText("100")
        self.c_unit.setCurrentIndex(0)
        self.r_slider.setValue(10000)
        self.c_slider.setValue(100)
        self.calculate()
