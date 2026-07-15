from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QRadioButton, QButtonGroup
)
import numpy as np
import qtawesome as qta
from src.ui.components.base_simulation import BaseSimulation
from src.ui.components.simulation_visualizers import InductorVisualizer
from src.utils.formula_formatter import (
    format_eng, format_num, format_value_base, PI, MULT
)
from src.core.config import config_manager

class RLTransientSimulation(BaseSimulation):
    """Simulator for RL Transient current buildup and decay."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="RL Transient Response Simulator",
            formula_str="I(t) = (Vs / R) × (1 - e^(-R × t / L))   |   τ = L / R",
            explanation_str=(
                "An inductor opposes changes in current by storing energy in a magnetic field. "
                "When a voltage is applied, current builds up exponentially. The time constant "
                "is determined by τ = L / R. At t = 5τ, the current is considered fully built up (~99.3%)."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # Mode selector (Charging / Decay)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Simulation Mode:"))
        self.mode_group = QButtonGroup(self)
        self.energize_radio = QRadioButton("Charging")
        self.energize_radio.setChecked(True)
        self.decay_radio = QRadioButton("Decay")
        
        self.mode_group.addButton(self.energize_radio)
        self.mode_group.addButton(self.decay_radio)
        mode_layout.addWidget(self.energize_radio)
        mode_layout.addWidget(self.decay_radio)
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

        # Resistance R
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resistance (R):"))
        self.r_input = QLineEdit("10.0")
        self.r_unit = QComboBox()
        self.r_unit.addItems(["Ω", "kΩ"])
        r_layout.addWidget(self.r_input)
        r_layout.addWidget(self.r_unit)
        layout.addLayout(r_layout)

        # Inductor (L)
        l_layout = QHBoxLayout()
        l_layout.addWidget(QLabel("Inductance (L):"))
        self.l_input = QLineEdit("100")
        self.l_unit = QComboBox()
        self.l_unit.addItems(["mH", "μH", "H"])
        l_layout.addWidget(self.l_input)
        l_layout.addWidget(self.l_unit)
        layout.addLayout(l_layout)

        # Validators
        self.register_input_validator(self.vs_input, lambda v: v > 0)
        self.register_input_validator(self.r_input, lambda v: v > 0)
        self.register_input_validator(self.l_input, lambda v: v > 0)

        self.energize_radio.toggled.connect(self.reset_simulation)
        self.decay_radio.toggled.connect(self.reset_simulation)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = InductorVisualizer()
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("RL Transient Response Waveforms")
        self.plot_canvas.ax.set_xlabel("Time (s)")
        self.plot_canvas.ax.set_ylabel("Current I (A)")
        
        self.time_points = []
        self.i_points = []
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        self.time_points = [0.0]
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            max_i = base_vs / base_r
        except ValueError:
            max_i = 0.5

        if self.energize_radio.isChecked():
            self.i_points = [0.0]
        else:
            self.i_points = [max_i]
            
        self.visualizer.set_inductor_metrics(self.i_points[0] / max_i if max_i > 0 else 0, 0.0)
        self.update_plot_canvas()

    def update_simulation_step(self, dt: float):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            
            if vs <= 0 or r <= 0 or l <= 0:
                raise ValueError()
        except ValueError:
            self.error_label.setText("Error: Enter valid positive numbers.")
            return

        self.error_label.setText("")

        vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
        l_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[self.l_unit.currentText()]

        base_vs = vs * vs_mult
        base_r = r * r_mult
        base_l = l * l_mult
        tau = base_l / base_r
        max_i = base_vs / base_r

        # Cap simulation at 5.2τ
        if self.sim_time > 5.2 * tau:
            self.sim_time = 5.2 * tau
            self.timer.stop()
            self.is_running = False
            self.play_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
            self.play_btn.setStyleSheet("background-color: #10b981; border: none; border-radius: 18px;")
            self.answer_label.setText("State: Completed")
            self.show_toast("Simulation Completed.")
            
        t = self.sim_time
        
        # Calculate correct transient equation
        if self.energize_radio.isChecked():
            i_val = max_i * (1.0 - np.exp(-base_r * t / base_l))
        else:
            i_val = max_i * np.exp(-base_r * t / base_l)

        if t == 0.0:
            self.time_points = [0.0]
            self.i_points = [i_val]
        else:
            self.time_points.append(t)
            self.i_points.append(i_val)

        # Stored energy = 0.5 * L * I^2
        energy = 0.5 * base_l * (i_val ** 2)

        # Update visuals
        self.visualizer.set_inductor_metrics(i_val / max_i if max_i > 0 else 0, energy)
        self.update_plot_canvas()
        
        self.time_lbl.setText(f"Sim Time: {t:.4f}s")
        self.answer_label.setText(f"Current I: {format_eng(i_val, 'A')}  |  {(i_val/max_i)*100:.1f}%")

        self.steps_text.setText(
            f"**Transient Breakdown**:\n\n"
            f"- **Time constant (τ)**: L / R = {format_eng(tau, 's')}\n"
            f"- **Steady-state Current (Imax)**: {format_eng(max_i, 'A')}\n"
            f"- **Stored Energy (E)**: {format_eng(energy, 'J')}\n"
            f"- **Current Time (t)**: {format_num(t)} s\n"
            f"- **Current Value**: {format_num(i_val)} A"
        )

    def update_plot_canvas(self):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        line_w = config_manager.get("graph_line_width") or 2
        
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            l_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[self.l_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_l = l * l_mult
            tau = base_l / base_r
            max_i = base_vs / base_r
        except ValueError:
            tau = 1.0
            max_i = 0.5

        # Plot current
        self.plot_canvas.ax.plot(self.time_points, self.i_points, color="#f59e0b", linewidth=line_w, label="I(t) current")
        self.plot_canvas.ax.scatter([self.sim_time], [self.i_points[-1]], color="#10b981", s=60, zorder=5)

        # Dotted lines at tau and 5tau
        self.plot_canvas.ax.axvline(tau, color="#ef4444", linestyle=":", label="τ Marker")
        self.plot_canvas.ax.axvline(5.0 * tau, color="#10b981", linestyle=":", label="5τ Marker")

        self.plot_canvas.ax.set_title("RL Transient Response Waveform")
        self.plot_canvas.ax.set_xlabel("Time (seconds)")
        self.plot_canvas.ax.set_ylabel("Current I (A)")
        
        # Lock axes coordinates explicitly to avoid scaling anomalies
        self.plot_canvas.ax.set_xlim(0, 5.2 * tau)
        self.plot_canvas.ax.set_ylim(0, 1.05 * max_i)
        
        self.plot_canvas.ax.legend(loc="lower right" if self.energize_radio.isChecked() else "upper right")
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
            r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
            l_mult = {"mH": 1e-3, "μH": 1e-6, "H": 1.0}[self.l_unit.currentText()]
            base_vs = vs * vs_mult
            base_r = r * r_mult
            base_l = l * l_mult
        except ValueError:
            base_vs, base_r, base_l = 5.0, 10.0, 0.1
            
        tau = base_l / base_r
        t_pulse = 10.0 * tau if tau > 0 else 0.01
        
        ch1 = np.where((time_axis % t_pulse) < (5.0 * tau), base_vs, 0.0)
        t_mod = time_axis % t_pulse
        i_max = base_vs / base_r
        i_val = np.where(
            t_mod < (5.0 * tau),
            i_max * (1.0 - np.exp(-base_r * t_mod / (base_l if base_l > 0 else 1.0))),
            i_max * np.exp(-base_r * (t_mod - 5.0 * tau) / (base_l if base_l > 0 else 1.0))
        )
        ch2 = i_val * base_r # Voltage across resistor
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
