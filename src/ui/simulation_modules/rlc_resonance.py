from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox
)
import numpy as np
import qtawesome as qta
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import ResonanceGlowVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class RLCResonanceSimulation(BaseSimulation):
    """Frequency sweep analyzer for Series RLC circuits displaying resonance peak, impedance, and Q-factor."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Series RLC Resonance Frequency Sweep",
            formula_str=f"f0 = 1 / (2{PI} × √(L × C))   |   Q = (1 / R) × √(L / C)",
            explanation_str=(
                "At resonance, inductive and capacitive reactances cancel (XL = XC). "
                "The circuit impedance drops to its minimum (Z = R) and the current reaches its peak. "
                "The Quality Factor (Q) determines the sharpness of the peak, and the Bandwidth (BW) "
                "marks the frequency boundaries where current drops to 70.7% of the maximum value."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Applied Voltage Vs
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Applied Voltage (Vs):"))
        self.vs_input = QLineEdit("5.0")
        self.vs_unit = QComboBox()
        self.vs_unit.addItems(["V", "mV"])
        v_layout.addWidget(self.vs_input)
        v_layout.addWidget(self.vs_unit)
        layout.addLayout(v_layout)

        # Resistance R
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("20.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["Ω", "kΩ"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Inductance L
        l_layout = QHBoxLayout()
        l_layout.addWidget(QLabel("Inductance (L):"))
        self.l_input = QLineEdit("10.0")
        self.l_unit = QComboBox()
        self.l_unit.addItems(["mH", "μH"])
        l_layout.addWidget(self.l_input)
        self.l_unit.addItems(["mH", "μH"])
        l_layout.addWidget(self.l_unit)
        layout.addLayout(l_layout)

        # Capacitance C
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Capacitance (C):"))
        self.c_input = QLineEdit("100")
        self.c_unit = QComboBox()
        self.c_unit.addItems(["nF", "μF"])
        c_layout.addWidget(self.c_input)
        c_layout.addWidget(self.c_unit)
        layout.addLayout(c_layout)

        # Validators
        self.register_input_validator(self.vs_input, lambda v: v > 0)
        self.register_input_validator(self.r_input, lambda v: v > 0)
        self.register_input_validator(self.l_input, lambda v: v > 0)
        self.register_input_validator(self.c_input, lambda v: v > 0)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = ResonanceGlowVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("Current Amplitude vs Frequency Sweep")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Current I (A)")
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        try:
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            l_mult = {"mH": 1e-3, "μH": 1e-6}[self.l_unit.currentText()]
            c_mult = {"nF": 1e-9, "μF": 1e-6}[self.c_unit.currentText()]
            base_l = l * l_mult
            base_c = c * c_mult
            f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c)) if (base_l * base_c) > 0 else 503.29
            self.current_f = f0
        except Exception:
            self.current_f = 503.29
            
        self.visualizer.set_proximity(1.0)
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            if vs <= 0 or r <= 0 or l <= 0 or c <= 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
        l_mult = {"mH": 1e-3, "μH": 1e-6}[self.l_unit.currentText()]
        c_mult = {"nF": 1e-9, "μF": 1e-6}[self.c_unit.currentText()]

        base_vs = vs * vs_mult
        base_r = r * r_mult
        base_l = l * l_mult
        base_c = c * c_mult

        # Resonant calculations
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
        q = (1.0 / base_r) * np.sqrt(base_l / base_c)
        bw = f0 / q

        # Sweep range from f0 - 3*bw to f0 + 3*bw over time
        t_max = 6.0
        if self.sim_time > t_max:
            self.sim_time = t_max
            self.timer.stop()
            self.is_running = False
            self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
            self.answer_label.setText("State: Completed")
            self.show_toast("Frequency Sweep Completed.")

        t_ratio = self.sim_time / t_max
        f_min = max(10.0, f0 - 3.0 * bw)
        f_max = f0 + 3.0 * bw
        f_swept = f_min + t_ratio * (f_max - f_min)

        omega = 2.0 * np.pi * f_swept
        z = np.sqrt(base_r**2 + (omega * base_l - 1.0 / (omega * base_c))**2)
        i_val = base_vs / z

        self.current_f = f_swept
        self.update_plot_canvas()

        # Update neon glow visualizer
        proximity = i_val / (base_vs / base_r) if base_r > 0 else 0
        self.visualizer.set_proximity(proximity)

        self.time_lbl.setText(f"Freq: {format_eng(f_swept, 'Hz')}")
        self.answer_label.setText(f"Impedance Z: {format_eng(z, 'Ω')}  |  I: {format_eng(i_val, 'A')}")

        self.steps_text.setText(
            f"**RLC Resonance Metrics**:\n\n"
            f"- **Resonant Freq (f0)**: {format_eng(f0, 'Hz')}\n"
            f"- **Bandwidth (BW)**: {format_eng(bw, 'Hz')} (f1 to f2)\n"
            f"- **Quality Factor (Q)**: {q:.2f}\n"
            f"- **Peak Current (Vs / R)**: {format_eng(base_vs / base_r, 'A')}\n"
            f"- **Impedance at Swept Freq**: {format_eng(z, 'Ω')}"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            l_mult = {"mH": 1e-3, "μH": 1e-6}[self.l_unit.currentText()]
            c_mult = {"nF": 1e-9, "μF": 1e-6}[self.c_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_l = l * l_mult
            base_c = c * c_mult
            f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
            q = (1.0 / base_r) * np.sqrt(base_l / base_c)
            bw = f0 / q
        except ValueError:
            f0 = 5032.0
            bw = 159.0
            base_vs = 5.0
            base_r = 10.0

        # Plot full response curve
        f_min = max(10.0, f0 - 3 * bw)
        f_max = f0 + 3 * bw
        f_axis = np.linspace(f_min, f_max, 400)
        omega_axis = 2.0 * np.pi * f_axis
        z_axis = np.sqrt(base_r**2 + (omega_axis * base_l - 1.0 / (omega_axis * base_c))**2)
        i_axis = base_vs / z_axis

        line_w = config_manager.get("graph_line_width") or 2
        self.plot_canvas.ax.plot(f_axis, i_axis, color="#06b6d4", linewidth=line_w, label="Current I")
        
        # Current swept dot
        f_swept = getattr(self, 'current_f', f0)
        omega_swept = 2.0 * np.pi * f_swept
        z_swept = np.sqrt(base_r**2 + (omega_swept * base_l - 1.0 / (omega_swept * base_c))**2)
        i_swept = base_vs / z_swept
        self.plot_canvas.ax.scatter([f_swept], [i_swept], color="#ef4444", s=70, zorder=5, label="Active Sweep")

        # Peak indicator
        self.plot_canvas.ax.axvline(f0, color="#10b981", linestyle="--", label=f"f0 = {format_eng(f0, 'Hz')}")
        
        # Bandwidth markers
        f1 = f0 - bw / 2.0
        f2 = f0 + bw / 2.0
        self.plot_canvas.ax.axvline(f1, color="#f59e0b", linestyle=":", label="f1/f2 (-3dB points)")
        self.plot_canvas.ax.axvline(f2, color="#f59e0b", linestyle=":")

        self.plot_canvas.ax.set_title("Series RLC Resonance Curve")
        self.plot_canvas.ax.set_xlabel("Frequency (Hz)")
        self.plot_canvas.ax.set_ylabel("Current I (A)")
        self.plot_canvas.ax.legend(loc="upper right")

        if not self.orig_limits_saved:
            self.plot_canvas.store_original_limits()
            
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            l_mult = {"mH": 1e-3, "μH": 1e-6}[self.l_unit.currentText()]
            c_mult = {"nF": 1e-9, "μF": 1e-6}[self.c_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_l = l * l_mult
            base_c = c * c_mult
        except ValueError:
            base_vs, base_r, base_l, base_c = 5.0, 20.0, 0.01, 10e-6
            
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
        f = getattr(self, "current_f", f0)
        
        omega = 2.0 * np.pi * f
        xl = omega * base_l
        xc = 1.0 / (omega * base_c) if (omega * base_c) > 0 else 1e9
        z = np.sqrt(base_r**2 + (xl - xc)**2)
        vr_peak = (base_vs / z) * base_r if z > 0 else 0.0
        
        # phi = atan((xc - xl)/r) to match leading below resonance and lagging above resonance
        phi = np.arctan2(xc - xl, base_r)
        
        ch1 = base_vs * np.sin(omega * time_axis)
        ch2 = vr_peak * np.sin(omega * time_axis + phi)
        
        return {
            "time": time_axis,
            "time_axis": time_axis,
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0
        }
