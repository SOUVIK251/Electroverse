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

class VoltageDividerCalculator(BaseCalculator):
    """Calculator for Voltage Divider circuits."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Voltage Divider Calculator",
            formula_str=f"Vout = Vin {MULT} R2 / (R1 + R2)",
            explanation_str=(
                "A voltage divider is a simple passive linear circuit that produces "
                "an output voltage (Vout) that is a fraction of its input voltage (Vin). "
                "Voltage division is the result of distributing the input voltage among "
                "the components of the divider."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Input Voltage (V_in)
        vin_layout = QHBoxLayout()
        vin_layout.addWidget(QLabel("Input Voltage (Vin):"))
        self.vin_input = QLineEdit("10.0")
        self.vin_unit = QComboBox()
        self.vin_unit.addItems(["V", "mV", "kV"])
        vin_layout.addWidget(self.vin_input)
        vin_layout.addWidget(self.vin_unit)
        layout.addLayout(vin_layout)

        # Resistor R1
        r1_layout = QHBoxLayout()
        r1_layout.addWidget(QLabel("Resistor 1 (R1):"))
        self.r1_input = QLineEdit("1.0")
        self.r1_unit = QComboBox()
        self.r1_unit.addItems(["kΩ", "Ω", "MΩ"])
        r1_layout.addWidget(self.r1_input)
        r1_layout.addWidget(self.r1_unit)
        layout.addLayout(r1_layout)

        # Resistor R2
        r2_layout = QHBoxLayout()
        r2_layout.addWidget(QLabel("Resistor 2 (R2):"))
        self.r2_input = QLineEdit("1.0")
        self.r2_unit = QComboBox()
        self.r2_unit.addItems(["kΩ", "Ω", "MΩ"])
        r2_layout.addWidget(self.r2_input)
        r2_layout.addWidget(self.r2_unit)
        layout.addLayout(r2_layout)

        # Connect listeners
        self.vin_input.textChanged.connect(self.trigger_recalc)
        self.r1_input.textChanged.connect(self.trigger_recalc)
        self.r2_input.textChanged.connect(self.trigger_recalc)
        self.vin_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r1_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.r2_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # V_in slider
        layout.addWidget(QLabel("Input Voltage Slider (0 - 30 V):"))
        self.vin_slider = QSlider(Qt.Orientation.Horizontal)
        self.vin_slider.setRange(0, 300)  # 0.0 to 30.0 V
        self.vin_slider.setValue(100)     # 10.0 V
        self.vin_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.vin_slider)

        # R1 slider
        layout.addWidget(QLabel("R1 Resistor Slider (10 Ω - 10 kΩ):"))
        self.r1_slider = QSlider(Qt.Orientation.Horizontal)
        self.r1_slider.setRange(10, 10000)
        self.r1_slider.setValue(1000)
        self.r1_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r1_slider)

        # R2 slider
        layout.addWidget(QLabel("R2 Resistor Slider (10 Ω - 10 kΩ):"))
        self.r2_slider = QSlider(Qt.Orientation.Horizontal)
        self.r2_slider.setRange(10, 10000)
        self.r2_slider.setValue(1000)
        self.r2_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.r2_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("Vout vs R2 curve")
        self.plot_canvas.ax.set_xlabel("R2 (Ω)")
        self.plot_canvas.ax.set_ylabel("Vout (V)")
        self.plot_canvas.refresh_plot()

    def on_slider_changed(self):
        vin_val = self.vin_slider.value() / 10.0
        r1_val = self.r1_slider.value()
        r2_val = self.r2_slider.value()

        self.vin_input.blockSignals(True)
        self.r1_input.blockSignals(True)
        self.r2_input.blockSignals(True)

        self.vin_input.setText(f"{vin_val}")
        self.vin_unit.setCurrentIndex(0) # V
        
        self.r1_input.setText(f"{r1_val}")
        self.r1_unit.setCurrentIndex(1) # Ω
        
        self.r2_input.setText(f"{r2_val}")
        self.r2_unit.setCurrentIndex(1) # Ω

        self.vin_input.blockSignals(False)
        self.r1_input.blockSignals(False)
        self.r2_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            vin = float(self.vin_input.text())
            r1 = float(self.r1_input.text())
            r2 = float(self.r2_input.text())
            
            if vin < 0 or r1 <= 0 or r2 <= 0:
                raise ValueError("Values must be positive numbers (resistors > 0).")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Parse units
        vin_unit_text = self.vin_unit.currentText()
        r1_unit_text = self.r1_unit.currentText()
        r2_unit_text = self.r2_unit.currentText()

        vin_mult = {"V": 1.0, "mV": 1e-3, "kV": 1e3}[vin_unit_text]
        r1_mult = {"kΩ": 1e3, "Ω": 1.0, "MΩ": 1e6}[r1_unit_text]
        r2_mult = {"kΩ": 1e3, "Ω": 1.0, "MΩ": 1e6}[r2_unit_text]

        base_vin = vin * vin_mult
        base_r1 = r1 * r1_mult
        base_r2 = r2 * r2_mult

        # Voltage divider equation
        v_out = base_vin * (base_r2 / (base_r1 + base_r2))
        
        # Display answers
        self.answer_label.setText(f"Output Voltage (Vout) = {format_eng(v_out, 'V')}")

        ratio = base_r2 / (base_r1 + base_r2)
        
        breakdown = build_5_step_breakdown(
            formula=f"Vout = Vin {MULT} R2 / (R1 + R2)",
            given_dict={
                "Input Voltage (Vin)": f"{vin} {vin_unit_text}",
                "Resistor 1 (R1)": f"{r1} {r1_unit_text}",
                "Resistor 2 (R2)": f"{r2} {r2_unit_text}"
            },
            substitution=(
                f"Vout = {format_value_base(vin, vin_unit_text)} V {MULT} {format_value_base(r2, r2_unit_text)} {OHM} / "
                f"({format_value_base(r1, r1_unit_text)} {OHM} + {format_value_base(r2, r2_unit_text)} {OHM})"
            ),
            calculation=(
                f"Ratio = {format_num(base_r2)} / ({format_num(base_r1)} + {format_num(base_r2)}) = {format_num(ratio, 4)}\n"
                f"  Vout = {format_num(base_vin)} {MULT} {format_num(ratio, 4)} = {format_num(v_out)} V"
            ),
            final_ans=f"Output Voltage = {format_eng(v_out, 'V')}"
        )
        self.steps_text.setText(breakdown)

        # Store for plotting
        self.current_vin = base_vin
        self.current_r1 = base_r1
        self.current_r2 = base_r2
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        vin = getattr(self, 'current_vin', 10.0)
        r1 = getattr(self, 'current_r1', 1000.0)
        r2_active = getattr(self, 'current_r2', 1000.0)

        # Sweep R2 from 0 to 5x R1 to show full curvature
        r2_sweep = np.linspace(0, max(r1 * 5, r2_active * 1.5), 300)
        vout_sweep = vin * (r2_sweep / (r1 + r2_sweep))

        self.plot_canvas.ax.plot(r2_sweep, vout_sweep, color="#06b6d4", linewidth=2.5, label="Vout vs R2")
        
        # Highlight active operating point
        active_vout = vin * (r2_active / (r1 + r2_active))
        self.plot_canvas.ax.scatter([r2_active], [active_vout], color="#ef4444", s=80, zorder=5, label="Operating Point")

        # Theoretical limits
        self.plot_canvas.ax.axhline(vin, color="#ef4444", linestyle=":", alpha=0.5, label="Vin Limit")

        self.plot_canvas.ax.set_title("Voltage Divider characteristic curve")
        self.plot_canvas.ax.set_xlabel("R2 Resistance (Ω)")
        self.plot_canvas.ax.set_ylabel("Output Voltage Vout (V)")
        self.plot_canvas.ax.legend(loc="lower right")
        self.plot_canvas.draw()

    def reset(self):
        self.vin_input.setText("10.0")
        self.vin_unit.setCurrentIndex(0)
        self.r1_input.setText("1.0")
        self.r1_unit.setCurrentIndex(0)
        self.r2_input.setText("1.0")
        self.r2_unit.setCurrentIndex(0)
        self.vin_slider.setValue(100)
        self.r1_slider.setValue(1000)
        self.r2_slider.setValue(1000)
        self.calculate()
