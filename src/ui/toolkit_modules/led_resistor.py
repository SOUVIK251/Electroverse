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

class LEDSeriesResistorCalculator(BaseCalculator):
    """Calculator for LED Series Current Limiting Resistor."""
    
    # Predefined forward voltages for LED types
    LED_PRESETS = {
        "Red (~2.0 V)": 2.0,
        "Yellow (~2.1 V)": 2.1,
        "Green (~3.0 V)": 3.0,
        "Blue (~3.3 V)": 3.3,
        "White (~3.3 V)": 3.3,
        "Custom (User Defined)": 2.0
    }

    def __init__(self, parent=None):
        super().__init__(
            title="LED Series Resistor Calculator",
            formula_str=f"Rseries = (Vsource - Vled) / Iled   |   Presistor = Iled{SUP_2} {MULT} Rseries",
            explanation_str=(
                "LEDs are current-driven devices that have a relatively constant forward voltage drop (Vled). "
                "To prevent them from burning out due to excessive current, a series resistor (Rseries) is placed "
                "in series to limit the current (Iled) to a safe level (typically 10-20 mA). "
                "We must also verify the power rating of the resistor (Presistor) to ensure it doesn't overheat."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Preset LED Type Selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("LED Color/Type:"))
        self.type_cb = QComboBox()
        self.type_cb.addItems(list(self.LED_PRESETS.keys()))
        self.type_cb.currentIndexChanged.connect(self.on_preset_changed)
        type_layout.addWidget(self.type_cb)
        layout.addLayout(type_layout)

        # Source Voltage (V_source)
        vsrc_layout = QHBoxLayout()
        vsrc_layout.addWidget(QLabel("Source Voltage (Vsource):"))
        self.vsrc_input = QLineEdit("9.0")
        self.vsrc_unit = QComboBox()
        self.vsrc_unit.addItems(["V", "mV"])
        vsrc_layout.addWidget(self.vsrc_input)
        vsrc_layout.addWidget(self.vsrc_unit)
        layout.addLayout(vsrc_layout)

        # LED Forward Voltage (V_led)
        vled_layout = QHBoxLayout()
        vled_layout.addWidget(QLabel("LED Forward Voltage (Vled):"))
        self.vled_input = QLineEdit("2.0")
        self.vled_unit = QComboBox()
        self.vled_unit.addItems(["V", "mV"])
        vled_layout.addWidget(self.vled_input)
        vled_layout.addWidget(self.vled_unit)
        layout.addLayout(vled_layout)

        # LED Target Current (I_led)
        iled_layout = QHBoxLayout()
        iled_layout.addWidget(QLabel("LED Target Current (Iled):"))
        self.iled_input = QLineEdit("20.0")
        self.iled_unit = QComboBox()
        self.iled_unit.addItems(["mA", "A", "μA"])
        iled_layout.addWidget(self.iled_input)
        iled_layout.addWidget(self.iled_unit)
        layout.addLayout(iled_layout)

        # Connect listeners
        self.vsrc_input.textChanged.connect(self.trigger_recalc)
        self.vled_input.textChanged.connect(self.trigger_recalc)
        self.iled_input.textChanged.connect(self.trigger_recalc)
        self.vsrc_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.vled_unit.currentIndexChanged.connect(self.trigger_recalc)
        self.iled_unit.currentIndexChanged.connect(self.trigger_recalc)

    def setup_sliders(self, layout: QVBoxLayout):
        # Vsrc slider
        layout.addWidget(QLabel("Source Voltage Slider (3 V - 24 V):"))
        self.vsrc_slider = QSlider(Qt.Orientation.Horizontal)
        self.vsrc_slider.setRange(3, 24)
        self.vsrc_slider.setValue(9)
        self.vsrc_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.vsrc_slider)

        # Current slider
        layout.addWidget(QLabel("LED Current Slider (2 mA - 50 mA):"))
        self.iled_slider = QSlider(Qt.Orientation.Horizontal)
        self.iled_slider.setRange(2, 50)
        self.iled_slider.setValue(20)
        self.iled_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.iled_slider)

    def init_plot(self):
        self.plot_canvas.ax.set_title("LED Current vs Series Resistance")
        self.plot_canvas.ax.set_xlabel("Resistance Rseries (Ω)")
        self.plot_canvas.ax.set_ylabel("LED Current (A)")
        self.plot_canvas.refresh_plot()

    def on_preset_changed(self, idx: int):
        preset_name = self.type_cb.currentText()
        v_drop = self.LED_PRESETS[preset_name]
        
        # If not custom, set read-only forward voltage
        if preset_name != "Custom (User Defined)":
            self.vled_input.setText(f"{v_drop}")
            self.vled_input.setEnabled(False)
        else:
            self.vled_input.setEnabled(True)

        self.trigger_recalc()

    def on_slider_changed(self):
        vsrc_val = self.vsrc_slider.value()
        iled_val = self.iled_slider.value()

        self.vsrc_input.blockSignals(True)
        self.iled_input.blockSignals(True)

        self.vsrc_input.setText(f"{vsrc_val}.0")
        self.vsrc_unit.setCurrentIndex(0) # V
        
        self.iled_input.setText(f"{iled_val}.0")
        self.iled_unit.setCurrentIndex(0) # mA

        self.vsrc_input.blockSignals(False)
        self.iled_input.blockSignals(False)

        self.calculate()

    def calculate(self):
        self.error_label.setText("")
        try:
            vsrc = float(self.vsrc_input.text())
            vled = float(self.vled_input.text())
            iled = float(self.iled_input.text())
            
            if vsrc <= 0 or vled <= 0 or iled <= 0:
                raise ValueError("All inputs must be positive non-zero numbers.")
            if vsrc <= vled:
                raise ValueError("Source Voltage (Vsource) must be greater than LED Voltage drop (Vled).")
        except ValueError as e:
            self.error_label.setText(f"Validation Error: {e}")
            self.answer_label.setText("Answer: Error")
            return

        # Unit conversions
        vsrc_unit_text = self.vsrc_unit.currentText()
        vled_unit_text = self.vled_unit.currentText()
        iled_unit_text = self.iled_unit.currentText()

        vsrc_mult = {"V": 1.0, "mV": 1e-3}[vsrc_unit_text]
        vled_mult = {"V": 1.0, "mV": 1e-3}[vled_unit_text]
        iled_mult = {"mA": 1e-3, "A": 1.0, "μA": 1e-6}[iled_unit_text]

        base_vsrc = vsrc * vsrc_mult
        base_vled = vled * vled_mult
        base_iled = iled * iled_mult

        # Check again in base units to be safe
        if base_vsrc <= base_vled:
            self.error_label.setText("Error: Source voltage must be greater than LED forward voltage.")
            self.answer_label.setText("Answer: Error")
            return

        # Formulas
        v_diff = base_vsrc - base_vled
        r_series = v_diff / base_iled
        p_res = (base_iled ** 2) * r_series

        self.answer_label.setText(f"Resistor R = {format_eng(r_series, OHM)}   |   Resistor Power = {format_eng(p_res, 'W')}")

        breakdown = build_5_step_breakdown(
            formula=f"Rseries = (Vsource - Vled) / Iled   |   Presistor = Iled{SUP_2} {MULT} Rseries",
            given_dict={
                "Source Voltage (Vsource)": f"{vsrc} {vsrc_unit_text}",
                "LED Voltage Drop (Vled)": f"{vled} {vled_unit_text}",
                "LED Current (Iled)": f"{iled} {iled_unit_text}"
            },
            substitution=(
                f"Rseries = ({format_value_base(vsrc, vsrc_unit_text)} V - {format_value_base(vled, vled_unit_text)} V) / {format_value_base(iled, iled_unit_text)} A\n"
                f"  Presistor = ({format_value_base(iled, iled_unit_text)} A){SUP_2} {MULT} Rseries"
            ),
            calculation=(
                f"Rseries = ({format_num(base_vsrc)} - {format_num(base_vled)}) / {format_num(base_iled)} = {format_num(r_series)} {OHM}\n"
                f"  Presistor = ({format_num(base_iled)}){SUP_2} {MULT} {format_num(r_series)} = {format_num(p_res)} W"
            ),
            final_ans=(
                f"Resistor Resistance = {format_eng(r_series, OHM)}\n"
                f"  Resistor Power = {format_eng(p_res, 'W')}\n\n"
                f"**Resistor Selection Tip:**\n"
                f"- Use a standard commercial resistor value (e.g. next highest E24 value like 390 {OHM} for 350 {OHM} calculated).\n"
                f"- Resistor power rating should be at least double the calculated rating (i.e. use a {format_eng(2.0 * p_res, 'W')} rated resistor)."
            )
        )
        self.steps_text.setText(breakdown)

        self.current_vsrc = base_vsrc
        self.current_vled = base_vled
        self.current_iled = base_iled
        self.current_r = r_series
        self.update_plot()

    def update_plot(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        vsrc = getattr(self, 'current_vsrc', 9.0)
        vled = getattr(self, 'current_vled', 2.0)
        active_r = getattr(self, 'current_r', 350.0)
        active_i = getattr(self, 'current_iled', 0.02)

        # Plot I vs R series curve
        # Sweep R from R_minimum to 2000 Ω
        r_min = max(5.0, (vsrc - vled) / 0.1) # Limits current to 100mA max to avoid plotting infinity
        r_sweep = np.linspace(r_min, 2000, 400)
        i_sweep = (vsrc - vled) / r_sweep

        self.plot_canvas.ax.plot(r_sweep, i_sweep * 1000.0, color="#06b6d4", linewidth=2.5, label="LED Current (mA)")
        
        # Highlight operating point
        self.plot_canvas.ax.scatter([active_r], [active_i * 1000.0], color="#ef4444", s=80, zorder=5, label="Calculated Point")

        # Visual highlights: Green safe operating current zone (10 - 25 mA)
        self.plot_canvas.ax.axhspan(10, 25, color=(16/255, 185/255, 129/255, 0.12), label="Safe Operating Region (10-25 mA)")
        self.plot_canvas.ax.axhline(30, color="#ef4444", linestyle=":", alpha=0.6, label="Max Limit (30 mA)")

        self.plot_canvas.ax.set_title("LED Current vs Series Resistance (I_led vs R)")
        self.plot_canvas.ax.set_xlabel("Rseries Resistance (Ω)")
        self.plot_canvas.ax.set_ylabel("Current Iled (mA)")
        self.plot_canvas.ax.legend(loc="upper right")
        self.plot_canvas.draw()

    def reset(self):
        self.type_cb.setCurrentIndex(0)
        self.vsrc_input.setText("9.0")
        self.vsrc_unit.setCurrentIndex(0)
        self.vled_input.setText("2.0")
        self.vled_unit.setCurrentIndex(0)
        self.iled_input.setText("20.0")
        self.iled_unit.setCurrentIndex(0)
        self.vsrc_slider.setValue(9)
        self.iled_slider.setValue(20)
        self.calculate()
