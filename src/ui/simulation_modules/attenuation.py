from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox
)
import numpy as np
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import AttenuatorVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class AttenuationSimulation(BaseSimulation):
    """Simulator for Pi and T-pad Attenuators with real-time waveform comparison."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Signal Attenuator Simulator",
            formula_str="Vout = Vin / K   |   K = 10^(A_db / 20)",
            explanation_str=(
                "An attenuator is a passive network that reduces the power of a signal without "
                "distorting its waveform. It matches system impedance (Z0) while reducing amplitude. "
                "Common types are Pi and T networks. Attenuation is measured in decibels (dB)."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Impedance (Z0)
        z_layout = QHBoxLayout()
        z_layout.addWidget(QLabel("System Impedance (Z0):"))
        self.z0_input = QLineEdit("50.0")
        self.z0_unit = QComboBox()
        self.z0_unit.addItems(["Ω", "kΩ"])
        z_layout.addWidget(self.z0_input)
        z_layout.addWidget(self.z0_unit)
        layout.addLayout(z_layout)

        # Attenuation (dB)
        att_layout = QHBoxLayout()
        att_layout.addWidget(QLabel("Attenuation (dB):"))
        self.att_input = QLineEdit("6.0")
        self.att_unit = QComboBox()
        self.att_unit.addItems(["dB"])
        att_layout.addWidget(self.att_input)
        att_layout.addWidget(self.att_unit)
        layout.addLayout(att_layout)

        # Input peak (Vin)
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Input Peak (Vin):"))
        self.vin_input = QLineEdit("5.0")
        self.vin_unit = QComboBox()
        self.vin_unit.addItems(["V", "mV"])
        v_layout.addWidget(self.vin_input)
        v_layout.addWidget(self.vin_unit)
        layout.addLayout(v_layout)

        # Validators
        self.register_input_validator(self.z0_input, lambda v: v > 0)
        self.register_input_validator(self.att_input, lambda v: v > 0)
        self.register_input_validator(self.vin_input, lambda v: v > 0)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = AttenuatorVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("Input Waveform vs Attenuated Output")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Voltage (V)")
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        self.time_points = []
        self.vin_points = []
        self.vout_points = []
        self.visualizer.set_metrics(5.0, 2.5, 6.0)
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            z0 = float(self.z0_input.text())
            att = float(self.att_input.text())
            vin = float(self.vin_input.text())
            if z0 <= 0 or att <= 0 or vin <= 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        z0_mult = {"Ω": 1.0, "kΩ": 1e3}[self.z0_unit.currentText()]
        vin_mult = {"V": 1.0, "mV": 1e-3}[self.vin_unit.currentText()]

        base_z0 = z0 * z0_mult
        base_vin = vin * vin_mult
        
        # Calculate attenuation factor K
        k = 10.0 ** (att / 20.0)
        base_vout = base_vin / k

        # Resistors calculation
        # T-pad values
        t_r1 = base_z0 * (k - 1.0) / (k + 1.0)
        t_r2 = base_z0 * 2.0 * k / (k**2 - 1.0)

        # Pi-pad values
        pi_r1 = base_z0 * (k + 1.0) / (k - 1.0)
        pi_r2 = base_z0 * (k**2 - 1.0) / (2.0 * k)

        t = self.sim_time
        
        # AC Waveforms (using a 100 Hz frequency for demonstration)
        v_in_t = base_vin * np.sin(2.0 * np.pi * 100.0 * t)
        v_out_t = base_vout * np.sin(2.0 * np.pi * 100.0 * t)

        # Rolling window
        self.time_points.append(t)
        self.vin_points.append(v_in_t)
        self.vout_points.append(v_out_t)

        if len(self.time_points) > 150:
            self.time_points.pop(0)
            self.vin_points.pop(0)
            self.vout_points.pop(0)

        # Update visuals
        self.visualizer.set_metrics(base_vin, base_vout, att)
        self.update_plot_canvas()

        self.time_lbl.setText(f"Sim Time: {t:.4f}s")
        self.answer_label.setText(f"V_out Peak: {format_eng(base_vout, 'V')}  |  K: {k:.2f}")

        self.steps_text.setText(
            f"**Attenuator Resistor Pad Config**:\n\n"
            f"- **K factor**: {k:.2f} (V_in / V_out)\n"
            f"- **T-pad Values**: R1 = {format_eng(t_r1, 'Ω')}, R2 = {format_eng(t_r2, 'Ω')}\n"
            f"- **Pi-pad Values**: R1 = {format_eng(pi_r1, 'Ω')}, R2 = {format_eng(pi_r2, 'Ω')}\n"
            f"- **Output Power Drop**: -{att:.1f} dB"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        if len(self.time_points) > 1:
            line_w = config_manager.get("graph_line_width") or 2
            self.plot_canvas.ax.plot(self.time_points, self.vin_points, color="#06b6d4", linestyle="--", linewidth=1.2, label="Input (Vin)")
            self.plot_canvas.ax.plot(self.time_points, self.vout_points, color="#10b981", linewidth=line_w, label="Output (Vout)")
            self.plot_canvas.ax.scatter([self.sim_time], [self.vout_points[-1]], color="#ef4444", s=60, zorder=5)

        self.plot_canvas.ax.set_title("Signal Attenuation Waveforms")
        self.plot_canvas.ax.set_xlabel("Time (seconds)")
        self.plot_canvas.ax.set_ylabel("Voltage (V)")
        self.plot_canvas.ax.legend(loc="upper right")
        
        if not self.orig_limits_saved and len(self.time_points) > 10:
            self.plot_canvas.store_original_limits()
            
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vin = float(self.vin_input.text())
            att = float(self.att_input.text())
            vin_mult = {"V": 1.0, "mV": 1e-3}[self.vin_unit.currentText()]
            base_vin = vin * vin_mult
        except ValueError:
            base_vin, att = 5.0, 6.0
            
        k = 10.0 ** (att / 20.0)
        ch1 = base_vin * np.sin(2.0 * np.pi * 100.0 * time_axis)
        ch2 = ch1 / k
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
