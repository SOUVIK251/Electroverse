import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QPushButton, QStackedWidget, QProgressBar
)
from PySide6.QtCore import Qt
import qtawesome as qta

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox
from src.core.network_engine import NetworkEngine

class NetworkSimulationView(QWidget):
    """Dedicated, Topic-Specific Simulation Engine for Network Theory Experiments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.superposition_mode = "sum" # "sum", "v1", "v2"
        self.thevenin_step = 0          # 0..3
        self.norton_step = 0            # 0..3
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

        m_lbl = QLabel("🧪 Select Network Experiment:")
        m_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9.5pt;")

        self.sim_combo = QComboBox()
        self.sim_combo.addItems([
            "1. Ohm's Law (I-V Characteristic & Power)",
            "2. KCL Explorer (Junction Node & ΣI = 0)",
            "3. KVL Explorer (Closed Loop & ΣV = 0)",
            "4. Voltage Divider (Potential Distribution)",
            "5. Current Divider (Branch Current Splitting)",
            "6. Superposition Theorem (Source Activation Workflow)",
            "7. Thevenin's Theorem (4-Step Equivalent Builder)",
            "8. Norton's Theorem (Current Source Equivalent)",
            "9. Maximum Power Transfer Theorem (Peak PL vs RL)",
            "10. AC Phasor Simulator (Complex Plane Vectors)",
            "11. Series Resonance Explorer (fr & Q-Factor)",
            "12. Active & Passive Filters (Bode Plot & Cutoff)"
        ])
        self.sim_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; font-weight: bold; padding: 4px 8px; border-radius: 6px;")
        self.sim_combo.currentIndexChanged.connect(self.on_sim_changed)

        t_lay.addWidget(m_lbl)
        t_lay.addWidget(self.sim_combo)
        t_lay.addStretch()

        main_lay.addWidget(top_frame)

        # 2. Main Workspace Layout (Left Controls | Right Dedicated Canvas & Diagram)
        work_lay = QHBoxLayout()

        # Left Controls Panel (1 Stretch)
        self.ctrl_frame = QFrame()
        self.ctrl_frame.setObjectName("card-panel")
        self.ctrl_frame.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
        self.c_lay = QVBoxLayout(self.ctrl_frame)

        self.c_lay.addWidget(QLabel("⚙️ Experiment Controls", styleSheet="color: #10B981; font-weight: bold; font-size: 10pt;"))

        # Param 1
        self.lbl_p1 = QLabel("Voltage Source Vs1 (V):", styleSheet="color: #94A3B8;")
        self.sp_p1 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=500.0, unit="V")
        self.sp_p1.setValue(12.0)
        self.sp_p1.valueChanged.connect(self.update_simulation)

        # Param 2
        self.lbl_p2 = QLabel("Resistance R1 (Ω):", styleSheet="color: #94A3B8;")
        self.sp_p2 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=5000.0, unit="Ω")
        self.sp_p2.setValue(4.0)
        self.sp_p2.valueChanged.connect(self.update_simulation)

        # Param 3
        self.lbl_p3 = QLabel("Resistance R2 / Load RL (Ω):", styleSheet="color: #94A3B8;")
        self.sp_p3 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=5000.0, unit="Ω")
        self.sp_p3.setValue(6.0)
        self.sp_p3.valueChanged.connect(self.update_simulation)


        self.c_lay.addWidget(self.lbl_p1)
        self.c_lay.addWidget(self.sp_p1)
        self.c_lay.addWidget(self.lbl_p2)
        self.c_lay.addWidget(self.sp_p2)
        self.c_lay.addWidget(self.lbl_p3)
        self.c_lay.addWidget(self.sp_p3)

        # Special Mode Buttons Area (For Superposition, Thevenin, Norton)
        self.btn_area = QWidget()
        self.btn_lay = QVBoxLayout(self.btn_area)
        self.btn_lay.setContentsMargins(0, 5, 0, 5)
        self.c_lay.addWidget(self.btn_area)

        # Calculation Output Box
        self.res_card = QFrame()
        self.res_card.setStyleSheet("background-color: #0F172A; border: 1px solid #06B6D4; border-radius: 6px; padding: 10px;")
        rc_lay = QVBoxLayout(self.res_card)
        self.res_lbl = QLabel()
        self.res_lbl.setStyleSheet("color: #34D399; font-weight: bold; font-size: 9.5pt; font-family: Consolas, monospace;")
        self.res_lbl.setWordWrap(True)
        rc_lay.addWidget(self.res_lbl)
        self.c_lay.addWidget(self.res_card)

        # Virtual Lab Manual Summary
        man_box = QFrame()
        man_box.setStyleSheet("background-color: #0B1220; border: 1px solid #26334D; border-radius: 6px; padding: 8px;")
        m_lay = QVBoxLayout(man_box)
        m_hdr = QLabel("📋 Virtual Lab Manual")
        m_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 8.5pt;")
        self.m_txt = QLabel("• Verification of electrical network laws and circuit theorems.")
        self.m_txt.setStyleSheet("color: #94A3B8; font-size: 8pt;")
        self.m_txt.setWordWrap(True)
        m_lay.addWidget(m_hdr)
        m_lay.addWidget(self.m_txt)
        self.c_lay.addWidget(man_box)

        self.c_lay.addStretch()
        work_lay.addWidget(self.ctrl_frame, 1)

        # Right Matplotlib Plot Canvas (3 Stretch)
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        self.canvas = FigureCanvas(fig)
        self.fig = fig

        work_lay.addWidget(self.canvas, 3)
        main_lay.addLayout(work_lay, 1)

        self.on_sim_changed(0)

    def clear_btn_area(self):
        while self.btn_lay.count():
            item = self.btn_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def on_sim_changed(self, idx):
        self.clear_btn_area()

        if idx == 5: # Superposition
            lbl = QLabel("Source Activation Toggle:", styleSheet="color: #F59E0B; font-weight: bold; font-size: 8.5pt;")
            b_both = QPushButton("Original (V1 & V2 ON)")
            b_v1 = QPushButton("V1 Only (V2 Shorted)")
            b_v2 = QPushButton("V2 Only (V1 Shorted)")
            for b in [b_both, b_v1, b_v2]:
                b.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 4px; border-radius: 4px; font-size: 8.5pt;")
            
            b_both.clicked.connect(lambda: self.set_superposition_mode("sum"))
            b_v1.clicked.connect(lambda: self.set_superposition_mode("v1"))
            b_v2.clicked.connect(lambda: self.set_superposition_mode("v2"))

            self.btn_lay.addWidget(lbl)
            self.btn_lay.addWidget(b_both)
            self.btn_lay.addWidget(b_v1)
            self.btn_lay.addWidget(b_v2)

        elif idx in [6, 7]: # Thevenin / Norton
            lbl = QLabel("Decomposition Steps:", styleSheet="color: #06B6D4; font-weight: bold; font-size: 8.5pt;")
            b0 = QPushButton("Step 1: Original Circuit")
            b1 = QPushButton("Step 2: Measure Open/Short")
            b2 = QPushButton("Step 3: Calculate Req")
            b3 = QPushButton("Step 4: Equivalent Circuit")
            for b in [b0, b1, b2, b3]:
                b.setStyleSheet("background-color: #1E293B; color: #FFF; font-weight: bold; padding: 4px; border-radius: 4px; font-size: 8.5pt;")

            b0.clicked.connect(lambda: self.set_equiv_step(0))
            b1.clicked.connect(lambda: self.set_equiv_step(1))
            b2.clicked.connect(lambda: self.set_equiv_step(2))
            b3.clicked.connect(lambda: self.set_equiv_step(3))

            self.btn_lay.addWidget(lbl)
            self.btn_lay.addWidget(b0)
            self.btn_lay.addWidget(b1)
            self.btn_lay.addWidget(b2)
            self.btn_lay.addWidget(b3)

        self.update_simulation()

    def set_superposition_mode(self, mode):
        self.superposition_mode = mode
        self.update_simulation()

    def set_equiv_step(self, step):
        self.thevenin_step = step
        self.norton_step = step
        self.update_simulation()

    def update_simulation(self):
        self.fig.clear()
        idx = self.sim_combo.currentIndex()

        p1 = self.sp_p1.value()
        p2 = self.sp_p2.value()
        p3 = self.sp_p3.value()

        if idx == 0: # Ohm's Law (I-V & Power)
            self.render_ohms_law(p1, p2)
        elif idx == 1: # KCL Explorer
            self.render_kcl(p1, p2, p3)
        elif idx == 2: # KVL Explorer
            self.render_kvl(p1, p2, p3)
        elif idx == 3: # Voltage Divider
            self.render_voltage_divider(p1, p2, p3)
        elif idx == 4: # Current Divider
            self.render_current_divider(p1, p2, p3)
        elif idx == 5: # Superposition Theorem
            self.render_superposition(p1, 5.0, p2, p3)
        elif idx == 6: # Thevenin's Theorem
            self.render_thevenin(p1, p2, p3)
        elif idx == 7: # Norton's Theorem
            self.render_norton(p1, p2, p3)
        elif idx == 8: # Max Power Transfer
            self.render_max_power(p1, p2, p3)
        elif idx == 9: # AC Phasors
            self.render_phasors(p1, p2)
        elif idx == 10: # Resonance Explorer
            self.render_resonance(p1, p2, p3)
        else: # Filters
            self.render_filters(p1, p2)

        self.canvas.draw_idle()

    # -------------------------------------------------------------
    # Topic-Specific Dedicated Renderers
    # -------------------------------------------------------------

    def render_ohms_law(self, v, r):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        for ax in [ax1, ax2]:
            ax.set_facecolor("#0F172A")
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        i_val = v / r
        p_val = v * i_val

        # I-V Line Graph
        v_arr = np.linspace(0, v * 1.5, 100)
        i_arr = v_arr / r
        ax1.plot(v_arr, i_arr, color="#06B6D4", linewidth=2.5, label=f"I = V / {r:.1f}Ω")
        ax1.plot([v], [i_val], "o", color="#EF4444", markersize=8, label=f"Operating Point ({v}V, {i_val:.2f}A)")
        ax1.set_title("Ohm's Law Characteristic (I-V Line)", color="#FFF", fontsize=9.5, fontweight="bold")
        ax1.set_xlabel("Voltage V (Volts)", color="#94A3B8")
        ax1.set_ylabel("Current I (Amperes)", color="#94A3B8")
        ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        # Power Bar Chart
        ax2.bar(["Voltage V", "Current I", "Power P"], [v, i_val, p_val], color=["#06B6D4", "#34D399", "#F59E0B"])
        ax2.set_title("DC Circuit Operating Parameters", color="#FFF", fontsize=9.5, fontweight="bold")

        self.res_lbl.setText(f"Ohm's Law Operating State:\nVoltage V = {v:.2f} Volts\nResistance R = {r:.2f} Ohms\nCurrent I = {i_val:.3f} Amperes\nPower P = {p_val:.3f} Watts")

    def render_kcl(self, i1, i2, i3):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")
        ax.tick_params(colors="#94A3B8")
        ax.axis("off")

        i_out_total = i1 + i2
        i4 = i_out_total - i3

        # Draw Node Graphic
        ax.plot([0], [0], "o", color="#06B6D4", markersize=20, label="Junction Node N")
        ax.annotate("Node N", (0, 0.15), color="#06B6D4", fontweight="bold", ha="center")

        # Incoming Arrows
        ax.annotate("", xy=(0, 0), xytext=(-1, 1), arrowprops=dict(arrowstyle="->", color="#34D399", lw=3))
        ax.text(-0.6, 0.6, f"I1 = {i1:.1f}A ➔", color="#34D399", fontweight="bold")

        ax.annotate("", xy=(0, 0), xytext=(-1, -1), arrowprops=dict(arrowstyle="->", color="#34D399", lw=3))
        ax.text(-0.6, -0.6, f"I2 = {i2:.1f}A ➔", color="#34D399", fontweight="bold")

        # Outgoing Arrows
        ax.annotate("", xy=(1, 1), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#EF4444", lw=3))
        ax.text(0.5, 0.6, f"➔ I3 = {i3:.1f}A", color="#EF4444", fontweight="bold")

        ax.annotate("", xy=(1, -1), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#EF4444", lw=3))
        ax.text(0.5, -0.6, f"➔ I4 = {i4:.1f}A", color="#EF4444", fontweight="bold")

        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_title(f"KCL Node Junction Balance: ΣI_in ({i1+i2:.1f}A) = ΣI_out ({i3+i4:.1f}A)", color="#FFF", fontsize=10, fontweight="bold")

        self.res_lbl.setText(f"Kirchhoff's Current Law (KCL):\nSum of Entering Currents: I1 + I2 = {i1+i2:.2f} A\nSum of Leaving Currents: I3 + I4 = {i3+i4:.2f} A\nVerification: ΣI = 0.00 A (Charge Conserved)")

    def render_kvl(self, vs, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        i_val = vs / (r1 + r2)
        v1 = i_val * r1
        v2 = i_val * r2

        ax.bar(["Vs (Rise)", "V1 Drop (-)", "V2 Drop (-)", "Sum Loop ΣV"], [vs, -v1, -v2, vs - v1 - v2], color=["#10B981", "#EF4444", "#EF4444", "#06B6D4"])
        ax.set_title(f"KVL Closed-Loop Potential Tracker: +{vs}V - {v1:.2f}V - {v2:.2f}V = 0V", color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Kirchhoff's Voltage Law (KVL):\nSource Potential Rise: +{vs:.2f} Volts\nResistor 1 Voltage Drop: -{v1:.2f} Volts\nResistor 2 Voltage Drop: -{v2:.2f} Volts\nLoop Summation: ΣV = 0.00 Volts")

    def render_voltage_divider(self, vs, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        v1 = vs * (r1 / (r1 + r2))
        v2 = vs * (r2 / (r1 + r2))

        ax.bar(["Source Vs", "V_R1", "V_out (R2)"], [vs, v1, v2], color=["#06B6D4", "#F59E0B", "#10B981"])
        ax.set_title(f"Voltage Divider Distribution: V_out = {v2:.2f}V across R2", color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Voltage Divider Formula:\nV_out = Vs * (R2 / (R1 + R2))\nV_out = {vs}V * ({r2} / ({r1} + {r2})) = {v2:.3f} Volts")

    def render_current_divider(self, is_val, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        i1 = is_val * (r2 / (r1 + r2))
        i2 = is_val * (r1 / (r1 + r2))

        ax.bar(["Total Is", "Branch I1 (R1)", "Branch I2 (R2)"], [is_val, i1, i2], color=["#06B6D4", "#EC4899", "#34D399"])
        ax.set_title(f"Current Splitting Distribution: I1={i1:.2f}A, I2={i2:.2f}A", color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Current Divider Formula:\nI1 = Is * (R2 / (R1 + R2)) = {i1:.3f} A\nI2 = Is * (R1 / (R1 + R2)) = {i2:.3f} A")

    def render_superposition(self, v1, v2, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        res = NetworkEngine.solve_superposition(v1, v2, r1, r2, 10.0)

        if self.superposition_mode == "v1":
            vals = [res['il_v1_only'], 0, res['il_v1_only']]
            title = "Sub-Circuit 1: V1 Active (12V), V2 Shorted (0V)"
        elif self.superposition_mode == "v2":
            vals = [0, res['il_v2_only'], res['il_v2_only']]
            title = "Sub-Circuit 2: V2 Active (5V), V1 Shorted (0V)"
        else:
            vals = [res['il_v1_only'], res['il_v2_only'], res['il_total']]
            title = f"Superposition Algebraic Sum: IL = IL1 ({res['il_v1_only']}A) + IL2 ({res['il_v2_only']}A)"

        ax.bar(["IL (V1 Only)", "IL (V2 Only)", "Superposed Total IL"], vals, color=["#06B6D4", "#F59E0B", "#10B981"])
        ax.set_title(title, color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Superposition Theorem Workflow:\nResponse from V1 Alone: IL1 = {res['il_v1_only']} A\nResponse from V2 Alone: IL2 = {res['il_v2_only']} A\nTotal Superposed Current IL = {res['il_total']} A")

    def render_thevenin(self, vs, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        rl = 10.0
        res = NetworkEngine.solve_thevenin(vs, r1, r2, rl)

        labels = ["Vs (Source)", "Vth (Open-Circuit)", "Rth (Ohms)", "Load IL (Amps)"]
        if self.thevenin_step == 0:
            vals = [vs, 0, 0, res['il']]
            title = "Step 1: Original Circuit with Load RL Connected"
        elif self.thevenin_step == 1:
            vals = [vs, res['vth'], 0, 0]
            title = f"Step 2: Measure Open-Circuit Voltage Vth = {res['vth']} V"
        elif self.thevenin_step == 2:
            vals = [0, 0, res['rth'], 0]
            title = f"Step 3: Deactivate Source (Short Vs) ➔ Rth = {res['rth']} Ω"
        else:
            vals = [0, res['vth'], res['rth'], res['il']]
            title = f"Step 4: Thevenin Equivalent Circuit (Vth={res['vth']}V, Rth={res['rth']}Ω) ➔ IL={res['il']}A"

        ax.bar(labels, vals, color=["#06B6D4", "#F59E0B", "#EC4899", "#10B981"])
        ax.set_title(title, color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Thevenin Equivalent Parameters:\nThevenin Voltage Vth = {res['vth']:.3f} Volts\nThevenin Resistance Rth = {res['rth']:.3f} Ohms\nLoad Current IL = {res['il']:.3f} Amperes")

    def render_norton(self, vs, r1, r2):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        rl = 10.0
        res = NetworkEngine.solve_thevenin(vs, r1, r2, rl)
        i_norton = res['vth'] / (res['rth'] if res['rth'] != 0 else 1)

        ax.bar(["Vs Source", "Short IN", "Norton RN", "Load IL"], [vs, i_norton, res['rth'], res['il']], color=["#06B6D4", "#34D399", "#EC4899", "#10B981"])
        ax.set_title(f"Norton Equivalent Circuit: IN = {i_norton:.2f}A in parallel with RN = {res['rth']:.2f}Ω", color="#FFF", fontsize=10, fontweight="bold")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")

        self.res_lbl.setText(f"Norton Equivalent Parameters:\nShort-Circuit Current IN = {i_norton:.3f} Amperes\nNorton Resistance RN = {res['rth']:.3f} Ohms\nLoad Current IL = {res['il']:.3f} Amperes")

    def render_max_power(self, vs, r1, r2):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        for ax in [ax1, ax2]:
            ax.set_facecolor("#0F172A")
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        rth = r1
        vth = vs / 2.0
        rl_arr = np.linspace(0.1, rth * 3, 200)
        pl_arr = ((vth / (rth + rl_arr)) ** 2) * rl_arr
        eff_arr = (rl_arr / (rth + rl_arr)) * 100.0

        ax1.plot(rl_arr, pl_arr, color="#10B981", linewidth=2.5, label="Load Power PL")
        ax1.axvline(rth, color="#EF4444", linestyle="--", label=f"RL = Rth ({rth:.1f}Ω)")
        ax1.set_title("Maximum Power Peak Curve", color="#FFF", fontsize=9.5, fontweight="bold")
        ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        ax2.plot(rl_arr, eff_arr, color="#38BDF8", linewidth=2.5, label="Efficiency (%)")
        ax2.set_title("Efficiency Curve (50% at RL=Rth)", color="#FFF", fontsize=9.5, fontweight="bold")
        ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        p_max = (vth ** 2) / (4 * rth) if rth != 0 else 0
        self.res_lbl.setText(f"Maximum Power Transfer Condition:\nRth = {rth:.2f} Ω  |  Peak Power RL = {rth:.2f} Ω\nMaximum Delivered Power P_max = {p_max:.3f} Watts\nEfficiency at Peak = 50.0%")

    def render_phasors(self, vm, im):
        ax1 = self.fig.add_subplot(121, polar=True)
        ax2 = self.fig.add_subplot(122)

        ax1.set_facecolor("#0F172A")
        ax2.set_facecolor("#0F172A")
        for ax in [ax1, ax2]:
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        # Polar Vectors
        theta_v = 0.0
        theta_i = np.radians(45.0) # Current leads by 45 deg

        ax1.annotate("", xy=(theta_v, vm), xytext=(0,0), arrowprops=dict(arrowstyle="->", color="#06B6D4", lw=3))
        ax1.annotate("", xy=(theta_i, im), xytext=(0,0), arrowprops=dict(arrowstyle="->", color="#F59E0B", lw=3))
        ax1.set_title("Complex Phasor Vectors", color="#FFF", fontsize=9.5, fontweight="bold")

        # Time-Domain AC Waveforms
        t = np.linspace(0, 0.04, 300)
        w = 2 * np.pi * 50
        v_t = vm * np.sin(w * t)
        i_t = im * np.sin(w * t + np.radians(45.0))

        ax2.plot(t, v_t, color="#06B6D4", linewidth=2, label="v(t) Voltage")
        ax2.plot(t, i_t, color="#F59E0B", linewidth=2, label="i(t) Current (Leads 45°)")
        ax2.set_title("AC Time-Domain Sinusoids", color="#FFF", fontsize=9.5, fontweight="bold")
        ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        self.res_lbl.setText(f"AC Phasor Analysis (f = 50Hz):\nVoltage Phasor V = {vm:.2f} ∠ 0.0° V\nCurrent Phasor I = {im:.2f} ∠ +45.0° A\nPhase Angle θ = +45.0° (Capacitive Leading)")

    def render_resonance(self, l_mh, c_uf, r_ohm):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        l_h = l_mh * 1e-3
        c_f = c_uf * 1e-6

        fr = 1.0 / (2 * np.pi * np.sqrt(l_h * c_f))
        f_arr = np.linspace(fr * 0.2, fr * 2.0, 300)
        w_arr = 2 * np.pi * f_arr

        xl = w_arr * l_h
        xc = 1.0 / (w_arr * c_f)
        z = np.sqrt(r_ohm**2 + (xl - xc)**2)
        i_resp = 10.0 / z

        ax.plot(f_arr, i_resp, color="#10B981", linewidth=2.5, label="Series Current I(f)")
        ax.axvline(fr, color="#EF4444", linestyle="--", label=f"Resonance fr = {fr:.1f} Hz")
        ax.set_title(f"Series Resonance Peak Curve (fr = {fr:.1f} Hz)", color="#FFF", fontsize=10, fontweight="bold")
        ax.set_xlabel("Frequency f (Hz)", color="#94A3B8")
        ax.set_ylabel("Current I (A)", color="#94A3B8")
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, color="#1E293B", linestyle=":")
        ax.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        q_factor = (2 * np.pi * fr * l_h) / r_ohm if r_ohm != 0 else 0
        self.res_lbl.setText(f"Series RLC Resonance Parameters:\nResonance Frequency fr = {fr:.2f} Hz\nQuality Factor Q = {q_factor:.2f}\nBandwidth BW = {fr/q_factor:.2f} Hz")

    def render_filters(self, r_k, c_uf):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        for ax in [ax1, ax2]:
            ax.set_facecolor("#0F172A")
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, color="#1E293B", linestyle=":")

        r_val = r_k * 1e3
        c_val = c_uf * 1e-6
        fc = 1.0 / (2 * np.pi * r_val * c_val)

        f_arr = np.logspace(1, 5, 300)
        w_arr = 2 * np.pi * f_arr
        h_mag = 1.0 / np.sqrt(1 + (w_arr * r_val * c_val)**2)
        h_db = 20 * np.log10(h_mag)
        phase_deg = -np.degrees(np.arctan(w_arr * r_val * c_val))

        ax1.semilogx(f_arr, h_db, color="#06B6D4", linewidth=2.5, label="Bode Magnitude (dB)")
        ax1.axvline(fc, color="#EF4444", linestyle="--", label=f"Cutoff fc = {fc:.1f} Hz")
        ax1.axhline(-3, color="#F59E0B", linestyle=":", label="-3dB Cutoff Line")
        ax1.set_title("RC Low Pass Bode Magnitude", color="#FFF", fontsize=9.5, fontweight="bold")
        ax1.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        ax2.semilogx(f_arr, phase_deg, color="#EC4899", linewidth=2.5, label="Bode Phase (deg)")
        ax2.axvline(fc, color="#EF4444", linestyle="--", label=f"fc = {fc:.1f} Hz (-45°)")
        ax2.set_title("Bode Phase Response", color="#FFF", fontsize=9.5, fontweight="bold")
        ax2.legend(facecolor="#1E293B", edgecolor="#26334D", labelcolor="#FFF")

        self.res_lbl.setText(f"RC Low-Pass Filter Frequency Response:\nCutoff Frequency fc = 1 / (2πRC) = {fc:.2f} Hz\nAttenuation at fc: -3.01 dB\nPhase Shift at fc: -45.0°")
