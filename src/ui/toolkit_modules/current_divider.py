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

class CurrentDividerCalculator(BaseCalculator):
    """Calculator for Current Divider circuits."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Current Divider Calculator",
            formula_str=f"I1 = Itotal {MULT} R2 / (R1 + R2)   |   I2 = Itotal {MULT} R1 / (R1 + R2)",
            explanation_str=(
                "A current divider is a simple linear circuit that produces an output current "
                "that is a fraction of its input current. Current division refers to the splitting "
                "of current between the parallel branches of the circuit."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Total Input Current (I_total)
        itotal_layout = QHBoxLayout()
        itotal_layout.addWidget(QLabel("Total Input Current (Itotal):"))
        self.itotal_input = QLineEdit("5.0")
        self.itotal_unit = QComboBox()
        self.itotal_unit.addItems(["A", "mA", "μA"])
        itotal_layout.addWidget(self.itotal_input)
        itotal_layout.addWidget(self.itotal_unit)
        layout.addLayout(itotal_layout)

        # Resistor R1
        r1_layout = QHBoxLayout()
        r1_layout.addWidget(QLabel("Branch 1 Resistor (R1):"))
        self.r1_input = QLineEdit("100")
        self.r1_unit = QComboBox()
        self.r1_unit.addItems(["Ω", "kΩ", "MΩ"])
        r1_layout.addWidget(self.r1_input)
        r1_layout.addWidget(self.r1_unit)
        layout.addLayout(r1_layout)

        # Resistor R2
        r2_layout = QHBoxLayout()
        r2_layout.addWidget(QLabel("Branch 2 Resistor (R2):"))
        self.r2_input = QLineEdit("200")
        self.r2_unit = QComboBox()
        self.r2_unit.addItems(["Ω", "kΩ", "MΩ"])
        r2_layout.addWidget(self.r2_input)
        r2_layout.addWidget(self.r2_unit)
        layout.addLayout(r2_layout)

        # Connect listeners
        self.itotal_input.textChanged.connect(self.trigger_recalc)
        self.r1_input.textChanged.connect(self.trigger_recalc)
        self.r2_input.textChanged.connect(self.trigger_recalc)
        self.itotal_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r1_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r2_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # I_total slider
        layout.addWidget(QLabel("Total Current Slider (0 - 10 A):"))
        self.itotal_slider = QSlider(Qt.Orientation.Horizontal)
        self.itotal_slider.setRange(0, 100)  # 0.0 to 10.0 A
        self.itotal_slider.setValue(50)      # 5.0 A
        self.itotal_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.itotal_slider)

        # R1 slider
        layout.addWidget(QLabel("R1 Resistor Slider (10 Ω - 1000 Ω):"))
        self.r1_slider = QSlider(Qt.Orientation.Horizontal)
        self.r1_slider.setRange(10, 1000)
        self.r1_slider.setValue(100)
        self.r1_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r1_slider)

        # R2 slider
        layout.addWidget(QLabel("R2 Resistor Slider (10 Ω - 1000 Ω):"))
        self.r2_slider = QSlider(Qt.Orientation.Horizontal)
        self.r2_slider.setRange(10, 1000)
        self.r2_slider.setValue(200)
        self.r2_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r2_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Current Division curves (I1 & I2 vs R1)")
        self.plot_canvas.ax.set_xlabel("R1 Resistance (Ω)")
        self.plot_canvas.ax.set_ylabel("Branch Current (A)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        itotal_val = self.itotal_slider.value() / 10.0
        r1_val = self.r1_slider.value()
        r2_val = self.r2_slider.value()

        self.itotal_input.blockSignals(True)
        self.r1_input.blockSignals(True)
        self.r2_input.blockSignals(True)

        self.itotal_input.setText(f"{itotal_val}")
        self.itotal_unit.setCurrentIndex(0) # A
        
        self.r1_input.setText(f"{r1_val}")
        self.r1_unit.setCurrentIndex(0) # Ω
        
        self.r2_input.setText(f"{r2_val}")
        self.r2_unit.setCurrentIndex(0) # Ω

        self.itotal_input.blockSignals(False)
        self.r1_input.blockSignals(False)
        self.r2_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            itotal = float(self.itotal_input.text())
            r1 = float(self.r1_input.text())
            r2 = float(self.r2_input.text())
            
            if itotal < 0 or r1 <= 0 or r2 <= 0:
                raise ValueError("Values must be positive numbers (resistors > 0).")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Parse units
        itotal_unit_text = self.itotal_unit.currentText()
        r1_unit_text = self.r1_unit.currentText()
        r2_unit_text = self.r2_unit.currentText()

        itotal_mult = {"A": 1.0, "mA": 1e-3, "μA": 1e-6}[itotal_unit_text]
        r1_mult = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6}[r1_unit_text]
        r2_mult = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6}[r2_unit_text]

        base_itotal = itotal * itotal_mult
        base_r1 = r1 * r1_mult
        base_r2 = r2 * r2_mult

        # Current divider calculation
        i1 = base_itotal * (base_r2 / (base_r1 + base_r2))
        i2 = base_itotal * (base_r1 / (base_r1 + base_r2))
        
        # Display answers
        self.answer_label.setText(f"I1 = {format_eng(i1, 'A')}   |   I2 = {format_eng(i2, 'A')}")

        breakdown = build_5_step_breakdown(
            formula=f"I1 = Itotal {MULT} R2 / (R1 + R2)   |   I2 = Itotal {MULT} R1 / (R1 + R2)",
            given_dict={
                "Total Current (Itotal)": f"{itotal} {itotal_unit_text}",
                "Resistor 1 (R1)": f"{r1} {r1_unit_text}",
                "Resistor 2 (R2)": f"{r2} {r2_unit_text}"
            },
            substitution=(
                f"I1 = {format_value_base(itotal, itotal_unit_text)} A {MULT} {format_value_base(r2, r2_unit_text)} {OHM} / "
                f"({format_value_base(r1, r1_unit_text)} {OHM} + {format_value_base(r2, r2_unit_text)} {OHM})\n"
                f"  I2 = {format_value_base(itotal, itotal_unit_text)} A {MULT} {format_value_base(r1, r1_unit_text)} {OHM} / "
                f"({format_value_base(r1, r1_unit_text)} {OHM} + {format_value_base(r2, r2_unit_text)} {OHM})"
            ),
            calculation=(
                f"I1 = {format_num(base_itotal)} {MULT} {format_num(base_r2)} / ({format_num(base_r1)} + {format_num(base_r2)}) = {format_num(i1)} A\n"
                f"  I2 = {format_num(base_itotal)} {MULT} {format_num(base_r1)} / ({format_num(base_r1)} + {format_num(base_r2)}) = {format_num(i2)} A"
            ),
            final_ans=f"I1 = {format_eng(i1, 'A')}\n  I2 = {format_eng(i2, 'A')}"
        )
        self.steps_text.setText(breakdown)

        # Store for plotting
        self.current_itotal = base_itotal
        self.current_r1 = base_r1
        self.current_r2 = base_r2
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        itotal = getattr(self, 'current_itotal', 5.0)
        r2 = getattr(self, 'current_r2', 200.0)
        r1_active = getattr(self, 'current_r1', 100.0)

        # Sweep R1 to show how currents change
        r1_sweep = np.linspace(10, max(r2 * 5, r1_active * 1.5), 300)
        i1_sweep = itotal * (r2 / (r1_sweep + r2))
        i2_sweep = itotal * (r1_sweep / (r1_sweep + r2))

        self.plot_canvas.ax.plot(r1_sweep, i1_sweep, color="#06b6d4", linewidth=2.5, label="I1 (Current in R1)")
        self.plot_canvas.ax.plot(r1_sweep, i2_sweep, color="#10b981", linewidth=2.5, label="I2 (Current in R2)")

        # Highlight active operating point
        active_i1 = itotal * (r2 / (r1_active + r2))
        active_i2 = itotal * (r1_active / (r1_active + r2))
        self.plot_canvas.ax.scatter([r1_active], [active_i1], color="#ef4444", s=80, zorder=5, label="Branch 1 Operating Point")
        self.plot_canvas.ax.scatter([r1_active], [active_i2], color="#f59e0b", s=80, zorder=5, label="Branch 2 Operating Point")

        self.plot_canvas.ax.set_title("Current Divider split characteristics")
        self.plot_canvas.ax.set_xlabel("R1 Resistance (Ω)")
        self.plot_canvas.ax.set_ylabel("Current (A)")
        self.plot_canvas.ax.legend(loc="upper right")
        self.plot_canvas.draw()

    def reset(self):
        self.itotal_input.setText("5.0")
        self.itotal_unit.setCurrentIndex(0)
        self.r1_input.setText("100")
        self.r1_unit.setCurrentIndex(0)
        self.r2_input.setText("200")
        self.r2_unit.setCurrentIndex(0)
        self.itotal_slider.setValue(50)
        self.r1_slider.setValue(100)
        self.r2_slider.setValue(200)
        self.calculate()
