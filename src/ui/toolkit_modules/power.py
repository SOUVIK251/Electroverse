import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown,
    MULT, OHM, SUP_2
)

class PowerCalculator(BaseCalculator):
    """Calculator for Electrical Power (P = V*I = I^2 * R = V^2 / R)."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Electrical Power Calculator",
            formula_str=f"P = V {MULT} I   |   P = I{SUP_2} {MULT} R   |   P = V{SUP_2} / R",
            explanation_str=(
                "Electrical power (P) is the rate at which electrical energy is transferred "
                "by an electric circuit per unit time. The SI unit of power is the watt (W). "
                "Power can be calculated using Voltage (V), Current (I), and Resistance (R)."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Given Variables:"))
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Voltage & Current (V, I)", "Current & Resistance (I, R)", "Voltage & Resistance (V, R)"])
        self.mode_cb.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_cb)
        layout.addLayout(mode_layout)

        # Parameter 1 input
        self.param1_layout = QHBoxLayout()
        self.param1_label = QLabel("Voltage (V):")
        self.param1_input = QLineEdit("12.0")
        self.param1_unit = QComboBox()
        self.param1_unit.addItems(["V", "mV", "kV"])
        self.param1_layout.addWidget(self.param1_label)
        self.param1_layout.addWidget(self.param1_input)
        self.param1_layout.addWidget(self.param1_unit)
        layout.addLayout(self.param1_layout)

        # Parameter 2 input
        self.param2_layout = QHBoxLayout()
        self.param2_label = QLabel("Current (I):")
        self.param2_input = QLineEdit("2.0")
        self.param2_unit = QComboBox()
        self.param2_unit.addItems(["A", "mA", "μA"])
        self.param2_layout.addWidget(self.param2_label)
        self.param2_layout.addWidget(self.param2_input)
        self.param2_layout.addWidget(self.param2_unit)
        layout.addLayout(self.param2_layout)

        # Connect listeners
        self.param1_input.textChanged.connect(self.trigger_recalc)
        self.param2_input.textChanged.connect(self.trigger_recalc)
        self.param1_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.param2_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Slider for primary variables
        layout.addWidget(QLabel("Voltage Sweep Slider (0 - 50 V):"))
        self.v_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_slider.setRange(0, 500)  # 0.0 to 50.0 V
        self.v_slider.setValue(120)     # 12.0 V
        self.v_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.v_slider)

        layout.addWidget(QLabel("Current Sweep Slider (0 - 10 A):"))
        self.i_slider = QSlider(Qt.Orientation.Horizontal)
        self.i_slider.setRange(0, 100)  # 0.0 to 10.0 A
        self.i_slider.setValue(20)      # 2.0 A
        self.i_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.i_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Power vs Current Characteristic")
        self.plot_canvas.ax.set_xlabel("Current (I)")
        self.plot_canvas.ax.set_ylabel("Power (W)")
        self.plot_canvas.refresh_plot()

    def on_mode_changed(self, idx: int):
        # Disable/relabel inputs according to selection
        if idx == 0:  # V & I
            self.param1_label.setText("Voltage (V):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["V", "mV", "kV"])
            self.param1_input.setText("12.0")
            
            self.param2_label.setText("Current (I):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["A", "mA", "μA"])
            self.param2_input.setText("2.0")
        elif idx == 1:  # I & R
            self.param1_label.setText("Current (I):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["A", "mA", "μA"])
            self.param1_input.setText("2.0")
            
            self.param2_label.setText("Resistance (R):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["Ω", "kΩ", "MΩ"])
            self.param2_input.setText("6.0")
        else:  # V & R
            self.param1_label.setText("Voltage (V):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["V", "mV", "kV"])
            self.param1_input.setText("12.0")
            
            self.param2_label.setText("Resistance (R):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["Ω", "kΩ", "MΩ"])
            self.param2_input.setText("6.0")

        self.trigger_recalc()

    def on_slider_changed(self):
        v_val = self.v_slider.value() / 10.0
        i_val = self.i_slider.value() / 10.0
        r_val = max(1.0, v_val / max(0.01, i_val)) # Derived resistance

        mode = self.mode_cb.currentIndex()

        self.param1_input.blockSignals(True)
        self.param2_input.blockSignals(True)

        if mode == 0: # V & I
            self.param1_input.setText(f"{v_val}")
            self.param1_unit.setCurrentIndex(0) # V
            self.param2_input.setText(f"{i_val}")
            self.param2_unit.setCurrentIndex(0) # A
        elif mode == 1: # I & R
            self.param1_input.setText(f"{i_val}")
            self.param1_unit.setCurrentIndex(0) # A
            self.param2_input.setText(f"{r_val:.2f}")
            self.param2_unit.setCurrentIndex(0) # Ω
        else: # V & R
            self.param1_input.setText(f"{v_val}")
            self.param1_unit.setCurrentIndex(0) # V
            self.param2_input.setText(f"{r_val:.2f}")
            self.param2_unit.setCurrentIndex(0) # Ω

        self.param1_input.blockSignals(False)
        self.param2_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        mode = self.mode_cb.currentIndex()
        
        try:
            val1 = float(self.param1_input.text())
            val2 = float(self.param2_input.text())
            if val1 <= 0 or val2 <= 0:
                raise ValueError("Values must be positive numbers.")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit Conversions
        unit1 = self.param1_unit.currentText()
        mult1 = {"V": 1.0, "mV": 1e-3, "kV": 1e3, "A": 1.0, "mA": 1e-3, "μA": 1e-6}[unit1]
        base_val1 = val1 * mult1

        unit2 = self.param2_unit.currentText()
        mult2 = {"A": 1.0, "mA": 1e-3, "μA": 1e-6, "Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6}[unit2]
        base_val2 = val2 * mult2

        p, v, i, r = 0.0, 0.0, 0.0, 0.0

        if mode == 0:  # V and I given
            v, i = base_val1, base_val2
            p = v * i
            r = v / i
            self.answer_label.setText(f"Power (P) = {format_eng(p, 'W')}")
            
            breakdown = build_5_step_breakdown(
                formula=f"P = V {MULT} I",
                given_dict={
                    "Voltage (V)": f"{val1} {unit1}",
                    "Current (I)": f"{val2} {unit2}"
                },
                substitution=f"P = {format_value_base(val1, unit1)} V {MULT} {format_value_base(val2, unit2)} A",
                calculation=f"P = {format_num(v)} {MULT} {format_num(i)} = {format_num(p)} W\n  Equivalent Resistance: {format_eng(r, OHM)}",
                final_ans=f"Power = {format_eng(p, 'W')}"
            )
        elif mode == 1:  # I and R given
            i, r = base_val1, base_val2
            p = (i ** 2) * r
            v = i * r
            self.answer_label.setText(f"Power (P) = {format_eng(p, 'W')}")
            
            breakdown = build_5_step_breakdown(
                formula=f"P = I{SUP_2} {MULT} R",
                given_dict={
                    "Current (I)": f"{val1} {unit1}",
                    "Resistance (R)": f"{val2} {unit2}"
                },
                substitution=f"P = ({format_value_base(val1, unit1)} A){SUP_2} {MULT} {format_value_base(val2, unit2)} {OHM}",
                calculation=f"P = ({format_num(i)}){SUP_2} {MULT} {format_num(r)} = {format_num(p)} W\n  Equivalent Voltage: {format_eng(v, 'V')}",
                final_ans=f"Power = {format_eng(p, 'W')}"
            )
        else:  # V and R given
            v, r = base_val1, base_val2
            p = (v ** 2) / r
            i = v / r
            self.answer_label.setText(f"Power (P) = {format_eng(p, 'W')}")
            
            breakdown = build_5_step_breakdown(
                formula=f"P = V{SUP_2} / R",
                given_dict={
                    "Voltage (V)": f"{val1} {unit1}",
                    "Resistance (R)": f"{val2} {unit2}"
                },
                substitution=f"P = ({format_value_base(val1, unit1)} V){SUP_2} / {format_value_base(val2, unit2)} {OHM}",
                calculation=f"P = ({format_num(v)}){SUP_2} / {format_num(r)} = {format_num(p)} W\n  Equivalent Current: {format_eng(i, 'A')}",
                final_ans=f"Power = {format_eng(p, 'W')}"
            )

        self.steps_text.setText(breakdown)
        self.current_p = p
        self.current_v = v
        self.current_i = i
        self.current_r = r
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        r = getattr(self, 'current_r', 6.0)
        active_i = getattr(self, 'current_i', 2.0)
        active_p = getattr(self, 'current_p', 24.0)

        # Plot P vs I curve (quadratic)
        i_sweep = np.linspace(0, max(active_i * 1.8, 10.0), 300)
        p_sweep = (i_sweep ** 2) * r

        self.plot_canvas.ax.plot(i_sweep, p_sweep, color="#06b6d4", linewidth=2.5, label=f"P = I² × {r:.2f}Ω")
        self.plot_canvas.ax.scatter([active_i], [active_p], color="#ef4444", s=80, zorder=5, label="Operating Point")

        self.plot_canvas.ax.set_title("Power dissipation curve")
        self.plot_canvas.ax.set_xlabel("Current (I)")
        self.plot_canvas.ax.set_ylabel("Power (W)")
        self.plot_canvas.ax.legend(loc="upper left")
        self.plot_canvas.draw()

    def reset(self):
        self.mode_cb.setCurrentIndex(0)
        self.param1_input.setText("12.0")
        self.param1_unit.setCurrentIndex(0)
        self.param2_input.setText("2.0")
        self.param2_unit.setCurrentIndex(0)
        self.v_slider.setValue(120)
        self.i_slider.setValue(20)
        self.calculate()
