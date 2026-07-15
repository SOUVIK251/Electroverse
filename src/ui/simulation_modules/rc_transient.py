from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QRadioButton, QButtonGroup
)
import numpy as np
import qtawesome as qta
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import CapacitorVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class RCTransientSimulation(BaseSimulation):
    """Simulator for RC Charging and Discharging transient response."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RC Charging & Discharging Transient Simulator",
            formula_str="Vc(t) = Vs × (1 - e^(-t / τ))   |   τ = R × C",
            explanation_str=(
                "A capacitor stores energy in an electric field. When a voltage is applied through "
                "a resistor, the capacitor charges exponentially. The speed of charging is determined "
                "by the Time Constant (τ = R × C). At t = 5τ, the capacitor is considered fully charged (~99.3%)."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Mode selector (Charging / Discharging)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Simulation Mode:"))
        self.mode_group = QButtonGroup(self)
        self.charge_radio = QRadioButton("Charging")
        self.charge_radio.setChecked(True)
        self.discharge_radio = QRadioButton("Discharging")
        
        self.mode_group.addButton(self.charge_radio)
        self.mode_group.addButton(self.discharge_radio)
        mode_layout.addWidget(self.charge_radio)
        mode_layout.addWidget(self.discharge_radio)
        layout.addLayout(mode_layout)

        # Source Voltage (Vs)
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Source Voltage (Vs):"))
        self.vs_input = QLineEdit("5.0")
        self.vs_unit = QComboBox()
        self.vs_unit.addItems(["V", "mV"])
        v_layout.addWidget(self.vs_input)
        v_layout.addWidget(self.vs_unit)
        layout.addLayout(v_layout)

        # Resistor (R)
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("10.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["kΩ", "Ω"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Capacitor (C)
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Capacitance (C):"))
        self.c_input = QLineEdit("100")
        self.c_unit = QComboBox()
        self.c_unit.addItems(["μF", "nF"])
        c_layout.addWidget(self.c_input)
        c_layout.addWidget(self.c_unit)
        layout.addLayout(c_layout)

        # Validators
        self.register_input_validator(self.vs_input, lambda v: v > 0)
        self.register_input_validator(self.r_input, lambda v: v > 0)
        self.register_input_validator(self.c_input, lambda v: v > 0)

        # Trigger recalcs on toggle
        self.charge_radio.toggled.connect(self.reset_simulation)
        self.discharge_radio.toggled.connect(self.reset_simulation)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = CapacitorVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("RC Transient Response Waveforms")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Voltage Vc (V)")
        
        self.time_points = []
        self.vc_points = []
        self.reset_data()

    def reset_data(self):
        self.time_points = [0.0]
        
        try:
            vs = float(self.vs_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            base_vs = vs * vs_mult
        except ValueError:
            base_vs = 5.0

        # Initial point
        if self.charge_radio.isChecked():
            self.vc_points = [0.0]
            self.visualizer.set_voltage_ratio(0.0, "charging", tau_ratio=0.0)
        else:
            self.vc_points = [base_vs]
            self.visualizer.set_voltage_ratio(1.0, "discharging", tau_ratio=0.0)
            
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            
            if vs <= 0 or r <= 0 or c <= 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
        c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]

        base_vs = vs * vs_mult
        base_r = r * r_mult
        base_c = c * c_mult
        tau = base_r * base_c

        # Cap time simulation limit at 5.2*tau to see 5τ completion clearly
        if self.sim_time > 5.2 * tau:
            self.sim_time = 5.2 * tau
            self.timer.stop()
            self.is_running = False
            self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
            self.answer_label.setText("State: Completed")
            self.show_toast("Simulation Completed.")
            
        t = self.sim_time
        
        # Calculate transient formula
        if self.charge_radio.isChecked():
            vc = base_vs * (1.0 - np.exp(-t / tau))
            mode_str = "charging"
        else:
            vc = base_vs * np.exp(-t / tau)
            mode_str = "discharging"

        # Record simulation path
        self.time_points.append(t)
        self.vc_points.append(vc)

        # Update visualizer (voltage ratio, mode, tau_ratio)
        self.visualizer.set_voltage_ratio(vc / base_vs, mode_str, tau_ratio=t/tau if tau > 0 else 0)
        self.update_plot_canvas()
        
        # Stats summary
        current_charge = (vc / base_vs) * 100
        self.time_lbl.setText(f"Sim Time: {t:.4f}s")
        self.answer_label.setText(f"V_cap: {format_eng(vc, 'V')}  |  {current_charge:.1f}%")

        self.steps_text.setText(
            f"**Transient Breakdown**:\n\n"
            f"- **Time constant (τ)**: R × C = {format_eng(tau, 's')}\n"
            f"- **Current Time (t)**: {format_num(t)} s ({t/tau:.1f}τ)\n"
            f"- **Equation**: Vc(t) = Vs × {'(1 - e^(-t / τ))' if mode_str == 'charging' else 'e^(-t / τ)'}\n"
            f"- **Current Voltage**: {format_num(vc)} V"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        line_w = config_manager.get("graph_line_width") or 2
        
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_c = c * c_mult
            tau = base_r * base_c
        except ValueError:
            base_vs = 5.0
            tau = 1.0

        # Plot simulation path
        self.plot_canvas.ax.plot(self.time_points, self.vc_points, color="#10b981", linewidth=line_w, label="V_cap (t)")
        self.plot_canvas.ax.scatter([self.sim_time], [self.vc_points[-1]], color="#06b6d4", s=60, zorder=5)

        # Draw τ marker
        self.plot_canvas.ax.axvline(tau, color="#ef4444", linestyle=":", label="τ (Time Constant)")
        # Draw 5τ marker
        self.plot_canvas.ax.axvline(5.0 * tau, color="#f59e0b", linestyle=":", label="5τ (Fully Charged)")

        # Target threshold horizontal markers
        if self.charge_radio.isChecked():
            self.plot_canvas.ax.axhline(0.632 * base_vs, color="#ef4444", linestyle="--", alpha=0.5)
            self.plot_canvas.ax.axhline(0.993 * base_vs, color="#f59e0b", linestyle="--", alpha=0.5)
        else:
            self.plot_canvas.ax.axhline(0.368 * base_vs, color="#ef4444", linestyle="--", alpha=0.5)
            self.plot_canvas.ax.axhline(0.007 * base_vs, color="#f59e0b", linestyle="--", alpha=0.5)

        self.plot_canvas.ax.set_title("RC Transient Response Waveform")
        self.plot_canvas.ax.set_xlabel("Time (seconds)")
        self.plot_canvas.ax.set_ylabel("Voltage Vc (V)")
        self.plot_canvas.ax.legend(loc="lower right")
        
        # Save limits for zoom lock
        if not self.orig_limits_saved and len(self.time_points) > 1:
            self.plot_canvas.store_original_limits()
            
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            c = float(self.c_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            c_mult = {"μF": 1e-6, "nF": 1e-9}[self.c_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_c = c * c_mult
        except ValueError:
            base_vs, base_r, base_c = 5.0, 1000.0, 1e-6
            
        tau = base_r * base_c
        t_pulse = 10.0 * tau if tau > 0 else 0.01
        
        ch1 = np.where((time_axis % t_pulse) < (5.0 * tau), base_vs, 0.0)
        t_mod = time_axis % t_pulse
        ch2 = np.where(
            t_mod < (5.0 * tau),
            base_vs * (1.0 - np.exp(-t_mod / (tau if tau > 0 else 1.0))),
            base_vs * np.exp(-(t_mod - 5.0 * tau) / (tau if tau > 0 else 1.0))
        )
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
