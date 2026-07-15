import numpy as np
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider
)
from PySide6.QtCore import Qt
from src.ui.components.base_calculator import BaseCalculator
from src.core.logger import log
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, build_5_step_breakdown,
    MULT, DIV, OHM
)

class OhmsLawCalculator(BaseCalculator):
    """Calculator for Ohm's Law (V = I * R)."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Ohm's Law Calculator",
            formula_str=f"V = I {MULT} R   |   I = V {DIV} R   |   R = V {DIV} I",
            explanation_str=(
                "Ohm's Law states that the current (I) flowing through a conductor "
                "between two points is directly proportional to the voltage (V) across "
                "the two points, and inversely proportional to the resistance (R) between them."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Solve For:"))
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Voltage (V)", "Current (I)", "Resistance (R)"])
        self.mode_cb.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_cb)
        layout.addLayout(mode_layout)

        # Parameter 1 input
        self.param1_layout = QHBoxLayout()
        self.param1_label = QLabel("Current (I):")
        self.param1_input = QLineEdit("1.0")
        self.param1_unit = QComboBox()
        self.param1_unit.addItems(["A", "mA", "μA"])
        self.param1_layout.addWidget(self.param1_label)
        self.param1_layout.addWidget(self.param1_input)
        self.param1_layout.addWidget(self.param1_unit)
        layout.addLayout(self.param1_layout)

        # Parameter 2 input
        self.param2_layout = QHBoxLayout()
        self.param2_label = QLabel("Resistance (R):")
        self.param2_input = QLineEdit("10.0")
        self.param2_unit = QComboBox()
        self.param2_unit.addItems(["Ω", "kΩ", "MΩ"])
        self.param2_layout.addWidget(self.param2_label)
        self.param2_layout.addWidget(self.param2_input)
        self.param2_layout.addWidget(self.param2_unit)
        layout.addLayout(self.param2_layout)

        # Add event listeners for text changes to update
        self.param1_input.textChanged.connect(self.trigger_recalc)
        self.param2_input.textChanged.connect(self.trigger_recalc)
        self.param1_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.param2_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Voltage slider (0-50 V)
        layout.addWidget(QLabel("Voltage Sweep Slider (0 - 50 V):"))
        self.v_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_slider.setRange(0, 500)  # Represents 0.0 to 50.0 V
        self.v_slider.setValue(100)     # 10.0 V
        self.v_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.v_slider)

        # Resistance slider (1-1000 Ω)
        layout.addWidget(QLabel("Resistance Sweep Slider (1 - 1000 Ω):"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(1, 1000)
        self.r_slider.setValue(100)     # 100 Ω
        self.r_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Ohm's Law: I vs V Curve")
        self.plot_canvas.ax.set_xlabel("Voltage (V)")
        self.plot_canvas.ax.set_ylabel("Current (A)")
        self.plot_canvas.refresh_plot()

    def on_mode_changed(self, idx: int):
        # Update input labels and units based on solving mode
        if idx == 0:  # Solve for V
            self.param1_label.setText("Current (I):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["A", "mA", "μA"])
            self.param1_input.setText("1.0")
            
            self.param2_label.setText("Resistance (R):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["Ω", "kΩ", "MΩ"])
            self.param2_input.setText("10.0")
        elif idx == 1:  # Solve for I
            self.param1_label.setText("Voltage (V):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["V", "mV", "kV"])
            self.param1_input.setText("10.0")
            
            self.param2_label.setText("Resistance (R):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["Ω", "kΩ", "MΩ"])
            self.param2_input.setText("10.0")
        else:  # Solve for R
            self.param1_label.setText("Voltage (V):")
            self.param1_unit.clear()
            self.param1_unit.addItems(["V", "mV", "kV"])
            self.param1_input.setText("10.0")
            
            self.param2_label.setText("Current (I):")
            self.param2_unit.clear()
            self.param2_unit.addItems(["A", "mA", "μA"])
            self.param2_input.setText("1.0")

        self.trigger_recalc()

    def on_slider_changed(self):
        # Sliders modify input fields directly, triggering recalculation
        v_val = self.v_slider.value() / 10.0
        r_val = self.r_slider.value()

        # Update input fields according to current solver mode
        mode = self.mode_cb.currentIndex()
        
        # Block signals temporarily to prevent loop trigger
        self.param1_input.blockSignals(True)
        self.param2_input.blockSignals(True)

        if mode == 0: # Solving for V
            # Slider updates Current (I) and Resistance (R)
            self.param1_input.setText(f"{v_val / r_val:.4f}")
            self.param1_unit.setCurrentIndex(0) # A
            self.param2_input.setText(f"{r_val}")
            self.param2_unit.setCurrentIndex(0) # Ω
        elif mode == 1: # Solving for I
            # Slider updates Voltage (V) and Resistance (R)
            self.param1_input.setText(f"{v_val}")
            self.param1_unit.setCurrentIndex(0) # V
            self.param2_input.setText(f"{r_val}")
            self.param2_unit.setCurrentIndex(0) # Ω
        else: # Solving for R
            # Slider updates Voltage (V) and Current (I)
            self.param1_input.setText(f"{v_val}")
            self.param1_unit.setCurrentIndex(0) # V
            self.param2_input.setText(f"{v_val / r_val:.4f}")
            self.param2_unit.setCurrentIndex(0) # A

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
                raise ValueError("Values must be positive non-zero numbers.")
                
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Parse units and convert to base SI units
        # Parameter 1
        unit1 = self.param1_unit.currentText()
        mult1 = 1.0
        if unit1 in ["mA", "mV"]:
            mult1 = 1e-3
        elif unit1 in ["μA"]:
            mult1 = 1e-6
        elif unit1 in ["kV", "kΩ"]:
            mult1 = 1e3
        elif unit1 in ["MΩ"]:
            mult1 = 1e6
        base_val1 = val1 * mult1

        # Parameter 2
        unit2 = self.param2_unit.currentText()
        mult2 = 1.0
        if unit2 in ["mA", "mV"]:
            mult2 = 1e-3
        elif unit2 in ["μA"]:
            mult2 = 1e-6
        elif unit2 in ["kV", "kΩ"]:
            mult2 = 1e3
        elif unit2 in ["MΩ"]:
            mult2 = 1e6
        base_val2 = val2 * mult2

        # Perform Calculation
        v, i, r = 0.0, 0.0, 0.0
        
        if mode == 0:  # Solve for V (I, R given)
            i, r = base_val1, base_val2
            v = i * r
            self.answer_label.setText(f"Voltage (V) = {format_eng(v, 'V')}")
            
            breakdown = build_5_step_breakdown(
                formula=f"V = I {MULT} R",
                given_dict={"Current (I)": f"{val1} {unit1}", "Resistance (R)": f"{val2} {unit2}"},
                substitution=f"V = {format_value_base(val1, unit1)} A {MULT} {format_value_base(val2, unit2)} {OHM}",
                calculation=f"V = {format_num(i)} {MULT} {format_num(r)} = {format_num(v)} V",
                final_ans=f"Voltage = {format_eng(v, 'V')}"
            )
        elif mode == 1:  # Solve for I (V, R given)
            v, r = base_val1, base_val2
            i = v / r
            self.answer_label.setText(f"Current (I) = {format_eng(i, 'A')}")
            
            breakdown = build_5_step_breakdown(
                formula=f"I = V {DIV} R",
                given_dict={"Voltage (V)": f"{val1} {unit1}", "Resistance (R)": f"{val2} {unit2}"},
                substitution=f"I = {format_value_base(val1, unit1)} V {DIV} {format_value_base(val2, unit2)} {OHM}",
                calculation=f"I = {format_num(v)} {DIV} {format_num(r)} = {format_num(i)} A",
                final_ans=f"Current = {format_eng(i, 'A')}"
            )
        else:  # Solve for R (V, I given)
            v, i = base_val1, base_val2
            r = v / i
            self.answer_label.setText(f"Resistance (R) = {format_eng(r, OHM)}")
            
            breakdown = build_5_step_breakdown(
                formula=f"R = V {DIV} I",
                given_dict={"Voltage (V)": f"{val1} {unit1}", "Current (I)": f"{val2} {unit2}"},
                substitution=f"R = {format_value_base(val1, unit1)} V {DIV} {format_value_base(val2, unit2)} A",
                calculation=f"R = {format_num(v)} {DIV} {format_num(i)} = {format_num(r)} {OHM}",
                final_ans=f"Resistance = {format_eng(r, OHM)}"
            )

        self.steps_text.setText(breakdown)
        self.current_v, self.current_i, self.current_r = v, i, r
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()
        
        # Plot current vs voltage sweep for the current resistance value
        r_val = getattr(self, 'current_r', 10.0)
        v_val = getattr(self, 'current_v', 10.0)
        
        # Max sweep voltage: either 1.5x active voltage or default 30V
        max_v = max(v_val * 1.5, 30.0)
        v_sweep = np.linspace(0, max_v, 200)
        i_sweep = v_sweep / r_val
        
        self.plot_canvas.ax.plot(v_sweep, i_sweep, color="#06b6d4", linewidth=2.5, label=f"R = {r_val:.4g} Ω")
        
        # Highlight active operating point
        self.plot_canvas.ax.scatter([v_val], [v_val / r_val], color="#ef4444", s=80, zorder=5, label="Operating Point")
        
        self.plot_canvas.ax.set_title(f"Ohm's Law Sweep (I vs V)")
        self.plot_canvas.ax.set_xlabel("Voltage (V)")
        self.plot_canvas.ax.set_ylabel("Current (A)")
        self.plot_canvas.ax.legend(loc="upper left")
        self.plot_canvas.draw()

    def reset(self):
        self.mode_cb.setCurrentIndex(0)
        self.param1_input.setText("1.0")
        self.param1_unit.setCurrentIndex(0)
        self.param2_input.setText("10.0")
        self.param2_unit.setCurrentIndex(0)
        self.v_slider.setValue(100)
        self.r_slider.setValue(100)
        self.calculate()
