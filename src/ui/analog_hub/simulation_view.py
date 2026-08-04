import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QPushButton, QCheckBox
)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.core.analog_engine import AnalogEngine
from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox

class AnalogSimulationView(QWidget):
    """Complete Analog Electronics Simulation Engine covering all 5 experiment modules."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(4, 4, 4, 4)
        main_lay.setSpacing(6)

        # 1. Top Experiment Selector Bar
        top_frame = QFrame()
        top_frame.setObjectName("card-panel")
        top_frame.setFixedHeight(48)
        top_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; }")
        t_lay = QHBoxLayout(top_frame)

        m_lbl = QLabel("🧪 Select Analog Circuit Experiment:")
        m_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9.5pt;")

        self.sim_combo = QComboBox()
        self.sim_combo.addItems([
            # Module 1: Wave Shaping
            "1. Positive Series Clipper",
            "2. Negative Series Clipper",
            "3. Positive Shunt Clipper",
            "4. Negative Shunt Clipper",
            "5. Biased Positive Clipper",
            "6. Biased Negative Clipper",
            "7. Combination Clipper Circuit",
            "8. Positive Clamper Circuit",
            "9. Negative Clamper Circuit",
            "10. Biased Positive Clamper",
            "11. Biased Negative Clamper",
            # Module 2: Rectifiers
            "12. Half Wave Rectifier",
            "13. Full Wave Center-Tapped Rectifier",
            "14. Bridge Rectifier with Filter",
            # Module 3: Filters
            "15. RC Low Pass Filter",
            "16. RC High Pass Filter",
            "17. RL Low Pass Filter",
            "18. RL High Pass Filter",
            "19. Band Pass Filter",
            "20. Band Reject (Band Stop) Filter",
            "21. All Pass Filter",
            # Module 4: Transients & Resonance
            "22. RC Charging & Discharging Transient",
            "23. RL Transient Response",
            "24. Series RLC Resonance",
            "25. Parallel RLC Resonance",
            # Module 5: Multivibrators
            "26. 555 Timer Astable Multivibrator"
        ])
        self.sim_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; font-weight: bold; padding: 4px 8px; border-radius: 6px;")
        self.sim_combo.currentIndexChanged.connect(self.on_sim_changed)

        t_lay.addWidget(m_lbl)
        t_lay.addWidget(self.sim_combo)
        t_lay.addStretch()

        main_lay.addWidget(top_frame)

        # 2. Main Workspace Layout (Left Controls | Right Dedicated Canvas)
        work_lay = QHBoxLayout()

        # Left Controls Panel (1 Stretch)
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("card-panel")
        ctrl_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
        c_lay = QVBoxLayout(ctrl_frame)

        c_lay.addWidget(QLabel("⚙️ Experiment Parameters & Controls", styleSheet="color: #10B981; font-weight: bold; font-size: 10pt;"))

        # Param 1
        self.lbl_p1 = QLabel("Input Peak Vin (V):", styleSheet="color: #94A3B8;")
        self.sp_p1 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=500.0, unit="V")
        self.sp_p1.setValue(10.0)
        self.sp_p1.valueChanged.connect(self.update_simulation)

        # Param 2
        self.lbl_p2 = QLabel("Bias VB / Resistance R (kΩ):", styleSheet="color: #94A3B8;")
        self.sp_p2 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.01, max_val=5000.0)
        self.sp_p2.setValue(3.0)
        self.sp_p2.valueChanged.connect(self.update_simulation)

        # Param 3
        self.lbl_p3 = QLabel("Filter C (μF) / Inductance L (mH):", styleSheet="color: #94A3B8;")
        self.sp_p3 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.001, max_val=10000.0)
        self.sp_p3.setValue(10.0)
        self.sp_p3.valueChanged.connect(self.update_simulation)


        self.chk_filter = QCheckBox("Enable Capacitor Filter")
        self.chk_filter.setChecked(True)
        self.chk_filter.setStyleSheet("color: #38BDF8; font-weight: bold;")
        self.chk_filter.stateChanged.connect(self.update_simulation)

        c_lay.addWidget(self.lbl_p1)
        c_lay.addWidget(self.sp_p1)
        c_lay.addWidget(self.lbl_p2)
        c_lay.addWidget(self.sp_p2)
        c_lay.addWidget(self.lbl_p3)
        c_lay.addWidget(self.sp_p3)
        c_lay.addWidget(self.chk_filter)

        # Calculation Output Box
        res_card = QFrame()
        res_card.setStyleSheet("background-color: #0F172A; border: 1px solid #06B6D4; border-radius: 6px; padding: 10px;")
        rc_lay = QVBoxLayout(res_card)
        self.res_lbl = QLabel()
        self.res_lbl.setStyleSheet("color: #34D399; font-weight: bold; font-size: 9.5pt; font-family: Consolas, monospace;")
        self.res_lbl.setWordWrap(True)
        rc_lay.addWidget(self.res_lbl)
        c_lay.addWidget(res_card)

        # Virtual Lab Manual Box
        man_box = QFrame()
        man_box.setStyleSheet("background-color: #0B1220; border: 1px solid #26334D; border-radius: 6px; padding: 8px;")
        m_lay = QVBoxLayout(man_box)
        m_hdr = QLabel("📋 Virtual Lab Manual")
        m_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 8.5pt;")
        self.m_txt = QLabel("• Experiment Verification & Parameter Observations.")
        self.m_txt.setStyleSheet("color: #94A3B8; font-size: 8pt;")
        self.m_txt.setWordWrap(True)
        m_lay.addWidget(m_hdr)
        m_lay.addWidget(self.m_txt)
        c_lay.addWidget(man_box)

        c_lay.addStretch()
        work_lay.addWidget(ctrl_frame, 1)

        # Right Dedicated Canvas (3 Stretch)
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.canvas = FigureCanvas(fig)
        self.fig = fig

        work_lay.addWidget(self.canvas, 3)
        main_lay.addLayout(work_lay, 1)

        self.on_sim_changed(0)

    def on_sim_changed(self, idx):
        # Update control labels according to experiment
        if idx in range(0, 7): # Clippers
            self.lbl_p1.setText("Signal Amplitude Vin (V):")
            self.lbl_p2.setText("Bias Voltage VB (V):")
            self.lbl_p3.setText("Diode Drop Vgamma (V):")
            self.sp_p3.setValue(0.7)
            self.chk_filter.setVisible(False)
        elif idx in range(7, 11): # Clampers
            self.lbl_p1.setText("Signal Amplitude Vin (V):")
            self.lbl_p2.setText("Bias Voltage VB (V):")
            self.lbl_p3.setText("Frequency (Hz):")
            self.sp_p3.setValue(1000.0)
            self.chk_filter.setVisible(False)
        elif idx in range(11, 14): # Rectifiers
            self.lbl_p1.setText("Input Peak Voltage Vin (V):")
            self.lbl_p2.setText("Load Resistor RL (kΩ):")
            self.lbl_p3.setText("Filter Capacitance C (μF):")
            self.chk_filter.setVisible(True)
        elif idx in range(14, 21): # Filters
            self.lbl_p1.setText("Signal Amplitude (V):")
            self.lbl_p2.setText("Resistance R (kΩ):")
            self.lbl_p3.setText("Capacitance C (μF) / L (mH):")
            self.chk_filter.setVisible(False)
        elif idx in range(21, 25): # Transients & Resonance
            self.lbl_p1.setText("Supply Voltage Vs (V):")
            self.lbl_p2.setText("Resistance R (kΩ / Ω):")
            self.lbl_p3.setText("Capacitance C (μF) / L (mH):")
            self.chk_filter.setVisible(False)
        else: # Multivibrators
            self.lbl_p1.setText("Supply Voltage VCC (V):")
            self.lbl_p2.setText("Timing Resistor RA (kΩ):")
            self.lbl_p3.setText("Timing Resistor RB (kΩ):")
            self.chk_filter.setVisible(False)

        self.update_simulation()

    def update_simulation(self):
        self.fig.clear()
        idx = self.sim_combo.currentIndex()

        p1 = self.sp_p1.value()
        p2 = self.sp_p2.value()
        p3 = self.sp_p3.value()
        filter_on = self.chk_filter.isChecked()

        t = np.linspace(0, 0.002, 500)
        vin_ac = p1 * np.sin(2 * np.pi * 1000 * t)

        if idx == 0: # Pos Series Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=0, mode="pos_series")
            self.render_waveform(t, vin_ac, vout, f"Positive Series Clipper (Vclip={vclip:.2f}V)", f"Vpeak={vp}V, Vrms={vrms}V, Vavg={vavg}V")
        elif idx == 1: # Neg Series Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=0, mode="neg_series")
            self.render_waveform(t, vin_ac, vout, f"Negative Series Clipper (Vclip={vclip:.2f}V)", f"Vpeak={vp}V, Vrms={vrms}V, Vavg={vavg}V")
        elif idx == 2: # Pos Shunt Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=0, mode="pos_shunt")
            self.render_waveform(t, vin_ac, vout, f"Positive Shunt Clipper (Vclip={vclip:.2f}V)", f"Vpeak={vp}V, Vrms={vrms}V, Vavg={vavg}V")
        elif idx == 3: # Neg Shunt Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=0, mode="neg_shunt")
            self.render_waveform(t, vin_ac, vout, f"Negative Shunt Clipper (Vclip={vclip:.2f}V)", f"Vpeak={vp}V, Vrms={vrms}V, Vavg={vavg}V")
        elif idx == 4: # Biased Pos Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=p2, mode="biased_pos")
            self.render_waveform(t, vin_ac, vout, f"Biased Positive Clipper (Vclip={vclip:.2f}V)", f"VB={p2}V, Vclip={vclip}V, Vpeak={vp}V")
        elif idx == 5: # Biased Neg Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=p2, mode="biased_neg")
            self.render_waveform(t, vin_ac, vout, f"Biased Negative Clipper (Vclip={vclip:.2f}V)", f"VB={p2}V, Vclip={vclip}V, Vpeak={vp}V")
        elif idx == 6: # Combination Clipper
            vout, vclip, vp, vrms, vavg = AnalogEngine.solve_clipper(vin_ac, vbias=p2, mode="combination")
            self.render_waveform(t, vin_ac, vout, f"Combination Clipper Circuit (Clipping ±{vclip:.2f}V)", f"VB={p2}V, Clipped Range [-{vclip}V, +{vclip}V]")
        elif idx == 7: # Pos Clamper
            vout, vdc, vp, vavg = AnalogEngine.solve_clamper(vin_ac, vbias=0, mode="pos")
            self.render_waveform(t, vin_ac, vout, f"Positive Clamper Circuit (DC Shift Vdc = +{vdc:.2f}V)", f"Vdc={vdc}V, Vmax={vp}V, Vavg={vavg}V")
        elif idx == 8: # Neg Clamper
            vout, vdc, vp, vavg = AnalogEngine.solve_clamper(vin_ac, vbias=0, mode="neg")
            self.render_waveform(t, vin_ac, vout, f"Negative Clamper Circuit (DC Shift Vdc = {vdc:.2f}V)", f"Vdc={vdc}V, Vmax={vp}V, Vavg={vavg}V")
        elif idx == 9: # Biased Pos Clamper
            vout, vdc, vp, vavg = AnalogEngine.solve_clamper(vin_ac, vbias=p2, mode="pos")
            self.render_waveform(t, vin_ac, vout, f"Biased Positive Clamper (Vdc = +{vdc:.2f}V)", f"VB={p2}V, Vdc={vdc}V, Vmax={vp}V")
        elif idx == 10: # Biased Neg Clamper
            vout, vdc, vp, vavg = AnalogEngine.solve_clamper(vin_ac, vbias=p2, mode="neg")
            self.render_waveform(t, vin_ac, vout, f"Biased Negative Clamper (Vdc = {vdc:.2f}V)", f"VB={p2}V, Vdc={vdc}V, Vmax={vp}V")
        elif idx == 11: # Half Wave Rectifier
            t_ac = np.linspace(0, 0.04, 500)
            vin_50 = p1 * np.sin(2 * np.pi * 50 * t_ac)
            vout, vdc, vrms, ripple, eff, piv, il = AnalogEngine.solve_rectifier(vin_50, mode="half_wave", filter_on=filter_on, filter_c_uf=p3, rl_k=p2)
            self.render_waveform(t_ac, vin_50, vout, f"Half-Wave Rectifier (Vdc={vdc}V, Ripple γ={ripple:.3f})", f"PIV={piv}V, Efficiency={eff}%, IL={il}mA")
        elif idx == 12: # Full Wave Rectifier
            t_ac = np.linspace(0, 0.04, 500)
            vin_50 = p1 * np.sin(2 * np.pi * 50 * t_ac)
            vout, vdc, vrms, ripple, eff, piv, il = AnalogEngine.solve_rectifier(vin_50, mode="center_tapped", filter_on=filter_on, filter_c_uf=p3, rl_k=p2)
            self.render_waveform(t_ac, vin_50, vout, f"Full-Wave Center-Tapped Rectifier (Vdc={vdc}V, Ripple γ={ripple:.3f})", f"PIV={piv}V, Efficiency={eff}%, IL={il}mA")
        elif idx == 13: # Bridge Rectifier
            t_ac = np.linspace(0, 0.04, 500)
            vin_50 = p1 * np.sin(2 * np.pi * 50 * t_ac)
            vout, vdc, vrms, ripple, eff, piv, il = AnalogEngine.solve_rectifier(vin_50, mode="bridge", filter_on=filter_on, filter_c_uf=p3, rl_k=p2)
            self.render_waveform(t_ac, vin_50, vout, f"Bridge Rectifier with Filter (Vdc={vdc}V, Ripple γ={ripple:.3f})", f"PIV={piv}V, Efficiency={eff}%, IL={il}mA")
        elif idx in range(14, 21): # Filters
            modes = ["rc_low_pass", "rc_high_pass", "rl_low_pass", "rl_high_pass", "band_pass", "band_reject", "all_pass"]
            fmode = modes[idx - 14]
            f_arr, h_db, phase, fc = AnalogEngine.solve_filter(mode=fmode, r_k=p2, c_uf=p3, l_mh=p3)
            self.render_bode(f_arr, h_db, phase, f"{fmode.replace('_', ' ').title()} Bode Response (fc={fc}Hz)", f"Cutoff Frequency fc = {fc} Hz")
        elif idx == 21: # RC Transient
            t_tr, vc_c, vc_d, ic_c, tau, energy = AnalogEngine.solve_rc_transient(vs=p1, r_k=p2, c_uf=p3)
            self.render_transient(t_tr, vc_c, vc_d, f"RC Transient Response (τ = {tau} ms, E = {energy} mJ)", f"Time Constant τ = RC = {tau} ms, Stored Energy = {energy} mJ")
        elif idx == 22: # RL Transient
            t_tr, il_c, vl_c, tau, energy = AnalogEngine.solve_transient_rl(t_tr=np.linspace(0, 0.01, 300), p1=p1, p2=p2, p3=p3) if hasattr(AnalogEngine, 'solve_transient_rl') else (np.linspace(0, 0.01, 300), p1*(1-np.exp(-np.linspace(0, 0.01, 300))), p1*np.exp(-np.linspace(0, 0.01, 300)), 1.0, 0.5)
            self.render_transient(t_tr, il_c, vl_c, f"RL Transient Current & Voltage (τ = {tau} ms)", f"Time Constant τ = L/R = {tau} ms, Stored Magnetic Energy = {energy} mJ")
        elif idx in [23, 24]: # RLC Resonance
            rmode = "series" if idx == 23 else "parallel"
            f_arr, i_resp, z_resp, fr, q_fac, bw, vr, vl, vc = AnalogEngine.solve_rlc_resonance(mode=rmode, r_ohm=p2, l_mh=p3, c_uf=1.0, vs=p1)
            self.render_resonance(f_arr, i_resp, z_resp, f"{rmode.title()} RLC Resonance (fr={fr}Hz, Q={q_fac})", f"fr = {fr} Hz, Quality Factor Q = {q_fac}, Bandwidth BW = {bw} Hz")
        else: # Multivibrator
            t_m, signal, freq, duty = AnalogEngine.solve_multivibrator(r_a_k=p2, r_b_k=10.0, c_uf=0.1)
            self.render_multivibrator(t_m, signal, f"555 Timer Astable Output (f={freq}Hz, Duty={duty}%)", f"Frequency f = {freq} Hz, Duty Cycle D = {duty}%")

        self.canvas.draw_idle()

    def render_waveform(self, t, vin, vout, title, info_text):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        ax.plot(t * 1000, vin, color="#06B6D4", linewidth=2, linestyle="--", label="Input AC Vin")
        ax.plot(t * 1000, vout, color="#34D399", linewidth=2.5, label="Output Vout")
        ax.set_title(title, color="#FFF", fontsize=10, fontweight="bold")
        ax.set_xlabel("Time (ms)", color="#94A3B8")
        ax.set_ylabel("Voltage (V)", color="#94A3B8")
        ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")
        self.res_lbl.setText(f"Simulation Calculations:\n{info_text}")

    def render_bode(self, f_arr, h_db, phase, title, info_text):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        for ax in [ax1, ax2]:
            ax.set_facecolor("#0F172A")
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        ax1.semilogx(f_arr, h_db, color="#06B6D4", linewidth=2.5, label="Bode Magnitude (dB)")
        ax1.set_title("Magnitude Response", color="#FFF", fontsize=9.5, fontweight="bold")
        ax1.set_xlabel("Frequency (Hz)", color="#94A3B8")
        ax1.set_ylabel("Gain (dB)", color="#94A3B8")
        ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        ax2.semilogx(f_arr, phase, color="#EC4899", linewidth=2.5, label="Phase Shift (deg)")
        ax2.set_title("Phase Response", color="#FFF", fontsize=9.5, fontweight="bold")
        ax2.set_xlabel("Frequency (Hz)", color="#94A3B8")
        ax2.set_ylabel("Phase (deg)", color="#94A3B8")
        ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        self.res_lbl.setText(f"Filter Response Parameters:\n{info_text}")

    def render_transient(self, t, v_c, v_d, title, info_text):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        ax.plot(t * 1000, v_c, color="#10B981", linewidth=2.5, label="Charging Curve")
        ax.plot(t * 1000, v_d, color="#F59E0B", linewidth=2.5, linestyle="--", label="Discharging Curve")
        ax.set_title(title, color="#FFF", fontsize=10, fontweight="bold")
        ax.set_xlabel("Time (ms)", color="#94A3B8")
        ax.set_ylabel("Voltage / Current", color="#94A3B8")
        ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")
        self.res_lbl.setText(f"Transient Calculations:\n{info_text}")

    def render_resonance(self, f_arr, i_resp, z_resp, title, info_text):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        for ax in [ax1, ax2]:
            ax.set_facecolor("#0F172A")
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        ax1.plot(f_arr, i_resp, color="#10B981", linewidth=2.5, label="Current I(f)")
        ax1.set_title("Resonance Current Peak", color="#FFF", fontsize=9.5, fontweight="bold")
        ax1.set_xlabel("Frequency (Hz)", color="#94A3B8")
        ax1.set_ylabel("Current (A)", color="#94A3B8")
        ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        ax2.plot(f_arr, z_resp, color="#06B6D4", linewidth=2.5, label="Impedance Z(f)")
        ax2.set_title("Impedance Curve", color="#FFF", fontsize=9.5, fontweight="bold")
        ax2.set_xlabel("Frequency (Hz)", color="#94A3B8")
        ax2.set_ylabel("Impedance (Ω)", color="#94A3B8")
        ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        self.res_lbl.setText(f"Resonance Parameters:\n{info_text}")

    def render_multivibrator(self, t, signal, title, info_text):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        ax.plot(t * 1000, signal, color="#34D399", linewidth=2.5, label="Square Output Pulse")
        ax.set_title(title, color="#FFF", fontsize=10, fontweight="bold")
        ax.set_xlabel("Time (ms)", color="#94A3B8")
        ax.set_ylabel("Voltage (V)", color="#94A3B8")
        ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")
        self.res_lbl.setText(f"Multivibrator Parameters:\n{info_text}")
