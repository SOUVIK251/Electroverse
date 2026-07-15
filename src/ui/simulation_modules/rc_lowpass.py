from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox
)
import numpy as np
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import VoltageDividerVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class RCLowPassSimulation(BaseSimulation):
    """Simulator for RC Low-Pass filter frequency sweep with animated frequency dot."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RC Low-Pass Filter Frequency Sweeper",
            formula_str="H(f) = 1 / √(1 + (2π × f × R × C)²)   |   fc = 1 / (2π × R × C)",
            explanation_str=(
                "A low-pass filter passes signals below its cutoff frequency (fc) and attenuates "
                "signals above it. At fc, the output voltage drops to 70.7% of the input voltage (-3dB). "
                "The phase shift at cutoff is -45 degrees."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Input voltage (Vin)
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Input Voltage (Vin):"))
        self.vin_input = QLineEdit("5.0")
        self.vin_unit = QComboBox()
        self.vin_unit.addItems(["V", "mV"])
        v_layout.addWidget(self.vin_input)
        v_layout.addWidget(self.vin_unit)
        layout.addLayout(v_layout)

        # Resistor R
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("1.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["kΩ", "Ω"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Capacitor C
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Capacitance (C):"))
        self.c_input = QLineEdit("100")
        self.c_unit = QComboBox()
        self.c_unit.addItems(["nF", "μF"])
        c_layout.addWidget(self.c_input)
        c_layout.addWidget(self.c_unit)
        layout.addLayout(c_layout)

        # Validators
        self.register_input_validator(self.vin_input, lambda v: v > 0)
        self.register_input_validator(self.r_input, lambda v: v > 0)
        self.register_input_validator(self.c_input, lambda v: v > 0)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = VoltageDividerVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("Low-Pass Frequency Response (Bode Plot)")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Gain (dB)")
        self.plot_canvas.ax.set_xscale("log")
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        self.current_f = 1.0
        self.visualizer.set_voltages(5.0, 5.0)
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            vin = float(self.vin_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            if vin <= 0 or r <= 0 or c <= 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        vin_mult = {"V": 1.0, "mV": 1e-3}[self.vin_unit.currentText()]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
        c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]

        base_vin = vin * vin_mult
        base_r = r * r_mult
        base_c = c * c_mult

        # Cutoff frequency fc
        fc = 1.0 / (2.0 * np.pi * base_r * base_c)

        # Logarithmic sweep from 1Hz to 100kHz using sim_time
        # Let's map sim_time (0 to 10s) to 10^0 to 10^5 Hz
        t_max = 8.0
        if self.sim_time > t_max:
            self.sim_time = t_max
            self.timer.stop()
            self.is_running = False
            self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
            self.answer_label.setText("State: Completed")
            self.show_toast("Frequency Sweep Completed.")

        t_ratio = self.sim_time / t_max
        f_swept = 10.0 ** (t_ratio * 5.0) # 1 Hz to 100 kHz

        # Gain H(f)
        h = 1.0 / np.sqrt(1.0 + (2.0 * np.pi * f_swept * base_r * base_c) ** 2)
        gain_db = 20.0 * np.log10(h)
        vout = base_vin * h

        self.current_f = f_swept
        self.update_plot_canvas()

        # Update visualizer
        self.visualizer.set_voltages(base_vin, vout)

        self.time_lbl.setText(f"Freq: {format_eng(f_swept, 'Hz')}")
        self.answer_label.setText(f"Gain: {gain_db:.1f} dB  |  V_out: {format_eng(vout, 'V')}")

        self.steps_text.setText(
            f"**Low-Pass Filter Metrics**:\n\n"
            f"- **Cutoff Freq (fc)**: {format_eng(fc, 'Hz')} (-3dB point)\n"
            f"- **Swept Frequency**: {format_eng(f_swept, 'Hz')}\n"
            f"- **Signal Attenuation**: {gain_db:.2f} dB\n"
            f"- **Output Amplitude**: {format_num(vout)} V"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        try:
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]
            base_r = r * r_mult
            base_c = c * c_mult
            fc = 1.0 / (2.0 * np.pi * base_r * base_c)
        except ValueError:
            fc = 1591.0

        # Plot full bode curve from 1Hz to 100kHz
        f_axis = np.logspace(0, 5, 300)
        h_axis = 1.0 / np.sqrt(1.0 + (2.0 * np.pi * f_axis * base_r * base_c) ** 2)
        db_axis = 20.0 * np.log10(h_axis)

        line_w = config_manager.get("graph_line_width") or 2
        self.plot_canvas.ax.plot(f_axis, db_axis, color="#06b6d4", linewidth=line_w, label="Gain Magnitude")
        
        # Current operating point
        f_swept = getattr(self, 'current_f', 1.0)
        h_swept = 1.0 / np.sqrt(1.0 + (2.0 * np.pi * f_swept * base_r * base_c) ** 2)
        db_swept = 20.0 * np.log10(h_swept)
        self.plot_canvas.ax.scatter([f_swept], [db_swept], color="#10b981", s=70, zorder=5, label="Active Sweeper")

        # Shaded passband and stopband
        self.plot_canvas.ax.axvspan(1.0, fc, facecolor="#10b981", alpha=0.12, label="Passband")
        self.plot_canvas.ax.axvspan(fc, 100000.0, facecolor="#ef4444", alpha=0.08, label="Stopband")

        # Cutoff marker (-3dB)
        self.plot_canvas.ax.axvline(fc, color="#ef4444", linestyle="--", label=f"fc = {format_eng(fc, 'Hz')}")
        self.plot_canvas.ax.axhline(-3.0, color="#ef4444", linestyle=":")

        self.plot_canvas.ax.set_title("RC Low-Pass Bode Frequency Sweep")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz) [Log Scale]")
        self.plot_canvas.ax.set_ylabel("Gain (dB)")
        self.plot_canvas.ax.set_xscale("log")
        self.plot_canvas.ax.set_ylim(-40, 2)
        self.plot_canvas.ax.legend(loc="lower left")

        if not self.orig_limits_saved:
            self.plot_canvas.store_original_limits()
            
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vin = float(self.vin_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            vin_mult = {"V": 1.0, "mV": 1e-3}[self.vin_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]
            base_vin = vin * vin_mult
            base_r = r * r_mult
            base_c = c * c_mult
        except Exception:
            base_vin, base_r, base_c = 5.0, 1000.0, 100e-9
            
        f = getattr(self, "current_f", 1000.0)
        if f <= 0:
            f = 1000.0
            
        fc = 1.0 / (2.0 * np.pi * base_r * base_c)
        gain = 1.0 / np.sqrt(1.0 + (f / fc)**2)
        gain = max(0.1, gain)  # ensure it never becomes flat line
        phase = -np.arctan2(f, fc)
        
        ch1 = base_vin * np.sin(2.0 * np.pi * f * time_axis)
        ch2 = base_vin * gain * np.sin(2.0 * np.pi * f * time_axis + phase)
            
        return {
            "time": time_axis,
            "time_axis": time_axis,
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0
        }
