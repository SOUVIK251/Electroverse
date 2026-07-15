from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox
)
import numpy as np
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import RectifierCurrentVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class FullWaveRectifierSimulation(BaseSimulation):
    """Simulator for Full-Wave Diode Bridge Rectification with rolling time waveform."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Full-Wave Rectifier Simulator",
            formula_str="Vout(t) = max(0, |Vin(t)| - 2 × Vd)",
            explanation_str=(
                "A full-wave bridge rectifier uses four diodes to route both half-cycles of AC "
                "input into a unipolar positive DC output. This doubles the DC ripple frequency "
                "and improves efficiency, but drops voltage by 2 × Vd because two diodes conduct "
                "in series on each half-cycle."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Input Peak Voltage (Vac)
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Peak AC Voltage (Vac):"))
        self.vac_input = QLineEdit("5.0")
        self.vac_unit = QComboBox()
        self.vac_unit.addItems(["V", "mV"])
        v_layout.addWidget(self.vac_input)
        v_layout.addWidget(self.vac_unit)
        layout.addLayout(v_layout)

        # AC Frequency (f)
        f_layout = QHBoxLayout()
        f_layout.addWidget(QLabel("AC Frequency (f):"))
        self.f_input = QLineEdit("50.0")
        self.f_unit = QComboBox()
        self.f_unit.addItems(["Hz", "kHz"])
        f_layout.addWidget(self.f_input)
        f_layout.addWidget(self.f_unit)
        layout.addLayout(f_layout)

        # Diode Drop (Vd)
        vd_layout = QHBoxLayout()
        vd_layout.addWidget(QLabel("Diode Drop (Vd):"))
        self.vd_input = QLineEdit("0.7")
        self.vd_unit = QComboBox()
        self.vd_unit.addItems(["V", "mV"])
        vd_layout.addWidget(self.vd_input)
        vd_layout.addWidget(self.vd_unit)
        layout.addLayout(vd_layout)

        # Validators
        self.register_input_validator(self.vac_input, lambda v: v > 0)
        self.register_input_validator(self.f_input, lambda v: v > 0)
        self.register_input_validator(self.vd_input, lambda v: v >= 0)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = RectifierCurrentVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("AC Input vs Rectified DC Output")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Voltage (V)")
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        self.time_points = []
        self.vin_points = []
        self.vout_points = []
        self.visualizer.set_ac_voltage(0.0, "full")
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            vac = float(self.vac_input.text())
            freq = float(self.f_input.text())
            vd = float(self.vd_input.text())
            if vac <= 0 or freq <= 0 or vd < 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        vac_mult = {"V": 1.0, "mV": 1e-3}[self.vac_unit.currentText()]
        freq_mult = {"Hz": 1.0, "kHz": 1e3}[self.f_unit.currentText()]
        vd_mult = {"V": 1.0, "mV": 1e-3}[self.vd_unit.currentText()]

        base_vac = vac * vac_mult
        base_freq = freq * freq_mult
        base_vd = vd * vd_mult

        t = self.sim_time
        
        # Calculate instantaneous voltages
        vin = base_vac * np.sin(2.0 * np.pi * base_freq * t)
        if abs(vin) > 2.0 * base_vd:
            vout = abs(vin) - 2.0 * base_vd
        else:
            vout = 0.0

        # Keep a rolling window of the last 150 points
        self.time_points.append(t)
        self.vin_points.append(vin)
        self.vout_points.append(vout)
        
        if len(self.time_points) > 150:
            self.time_points.pop(0)
            self.vin_points.pop(0)
            self.vout_points.pop(0)

        # Update visuals (bridge alternating D1/D3 vs D2/D4 conduction paths)
        self.visualizer.set_ac_voltage(vin, "full")
        self.update_plot_canvas()

        # Update labels
        self.time_lbl.setText(f"Sim Time: {t:.4f}s")
        self.answer_label.setText(f"Vin: {format_eng(vin, 'V')}  |  Vout: {format_eng(vout, 'V')}")

        self.steps_text.setText(
            f"**Full-Wave Rectifier Status**:\n\n"
            f"- **Input Frequency**: {format_eng(base_freq, 'Hz')}\n"
            f"- **Bridge Diode Loss**: {format_eng(2.0 * base_vd, 'V')}\n"
            f"- **AC Peak Voltage**: {format_eng(base_vac, 'V')}\n"
            f"- **DC Peak Output**: {format_eng(max(0.0, base_vac - 2.0 * base_vd), 'V')}"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        if len(self.time_points) > 1:
            line_w = config_manager.get("graph_line_width") or 2
            self.plot_canvas.ax.plot(self.time_points, self.vin_points, color="#06b6d4", linestyle="--", linewidth=1.2, label="Vin AC")
            self.plot_canvas.ax.plot(self.time_points, self.vout_points, color="#10b981", linewidth=line_w, label="Vout DC")
            self.plot_canvas.ax.scatter([self.sim_time], [self.vout_points[-1]], color="#f59e0b", s=60, zorder=5)

        self.plot_canvas.ax.set_title("Full-Wave Rectification Waveforms")
        self.plot_canvas.ax.set_xlabel("Time (seconds)")
        self.plot_canvas.ax.set_ylabel("Voltage (V)")
        self.plot_canvas.ax.legend(loc="upper right")
        
        if not self.orig_limits_saved and len(self.time_points) > 10:
            self.plot_canvas.store_original_limits()
            
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vac = float(self.vac_input.text())
            f = float(self.f_input.text())
            vd = float(self.vd_input.text())
            vac_mult = {"V": 1.0, "mV": 1e-3}[self.vac_unit.currentText()]
            f_mult = {"Hz": 1.0, "kHz": 1e3}[self.f_unit.currentText()]
            vd_mult = {"V": 1.0, "mV": 1e-3}[self.vd_unit.currentText()]
            base_vac = vac * vac_mult
            base_f = f * f_mult
            base_vd = vd * vd_mult
        except ValueError:
            base_vac, base_f, base_vd = 5.0, 50.0, 0.7
            
        ch1 = base_vac * np.sin(2.0 * np.pi * base_f * time_axis)
        ch2 = np.maximum(0.0, np.abs(ch1) - 2.0 * base_vd)
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
