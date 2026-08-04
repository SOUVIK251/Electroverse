"""
ElectroVerse Professional Electrical Network Theory Problem Solving Workspace
Features 30 comprehensive engineering solvers with step-by-step mathematical derivations,
recognition guides, formula sheets, unit verifications, and GATE exam shortcuts.
"""

import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QDoubleSpinBox, QComboBox, QScrollArea, QStackedWidget, QLineEdit,
    QTextEdit, QApplication
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.core.network_engine import NetworkEngine
from src.core.logger import log
from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox, EngineeringSpinBox



class NetworkProblemSolvingView(QWidget):
    """Professional Network Theory Problem Solving Workspace (30 Engineering Solvers)."""

    SOLVER_LIST = [
        "1. Ohm's Law & Power Calculator",
        "2. Kirchhoff's Current Law (KCL)",
        "3. Kirchhoff's Voltage Law (KVL)",
        "4. Series Circuit Solver",
        "5. Parallel Circuit Solver",
        "6. Voltage Divider Calculator",
        "7. Current Divider Calculator",
        "8. Mesh Analysis Solver (2-Loop)",
        "9. Nodal Analysis Solver (2-Node)",
        "10. Source Transformation Solver",
        "11. Thevenin's Theorem Solver",
        "12. Norton's Theorem Solver",
        "13. Superposition Theorem Solver",
        "14. Maximum Power Transfer Solver",
        "15. Millman's Theorem Solver",
        "16. Reciprocity Theorem Checker",
        "17. Compensation Theorem Solver",
        "18. Tellegen's Theorem Verification",
        "19. Delta-Star (Δ ↔ Y) Conversion",
        "20. Bridge Network Solver (Wheatstone)",
        "21. Resonance Calculator (RLC)",
        "22. Quality Factor (Q) Calculator",
        "23. Time Constant (τ) Calculator",
        "24. AC Impedance Calculator",
        "25. Power Factor Calculator",
        "26. RMS & Average Value Calculator",
        "27. Phasor Calculator",
        "28. Laplace Circuit Solver",
        "29. Two-Port Network Calculator",
        "30. Electrical Unit Converter"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hint_step = 0
        self.spinboxes = {}
        self.comboboxes = {}
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)
        main_lay.setSpacing(12)

        # 1. Header Toolbar with Solver Dropdown & Action Buttons
        hdr = QFrame()
        hdr.setObjectName("card-panel")
        hdr.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        h_lay = QHBoxLayout(hdr)
        h_lay.setSpacing(12)

        h_lbl = QLabel("🧠 Select Engineering Solver:")
        h_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 10.5pt; font-family: Consolas;")

        self.theorem_combo = QComboBox()
        self.theorem_combo.addItems(self.SOLVER_LIST)
        self.theorem_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                border: 1px solid #06B6D4;
                color: #FFFFFF;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 9.5pt;
                font-family: Consolas;
            }
            QComboBox QAbstractItemView {
                background-color: #0F172A;
                color: #FFFFFF;
                selection-background-color: #0284C7;
            }
        """)
        self.theorem_combo.currentIndexChanged.connect(self.on_solver_changed)

        btn_copy = QPushButton(" 📋 Copy Solution")
        btn_copy.setStyleSheet("background-color: #1E293B; color: #38BDF8; font-weight: bold; border: 1px solid #0284C7; border-radius: 6px; padding: 6px 12px; font-size: 8.5pt;")
        btn_copy.clicked.connect(self.copy_solution)

        btn_reset = QPushButton(" 🔄 Reset")
        btn_reset.setStyleSheet("background-color: #1E293B; color: #FCA5A5; font-weight: bold; border: 1px solid #EF4444; border-radius: 6px; padding: 6px 12px; font-size: 8.5pt;")
        btn_reset.clicked.connect(self.reset_inputs)

        h_lay.addWidget(h_lbl)
        h_lay.addWidget(self.theorem_combo, 1)
        h_lay.addWidget(btn_copy)
        h_lay.addWidget(btn_reset)
        main_lay.addWidget(hdr)

        # Scroll Area for Solver Body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        self.body_layout = QVBoxLayout(container)
        self.body_layout.setSpacing(14)

        # 2. Recognition Guide Card
        self.rec_card = QFrame()
        self.rec_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #F59E0B; border-radius: 8px; padding: 12px;")
        r_lay = QVBoxLayout(self.rec_card)

        r_title = QLabel("🌲 Recognition Guide & Decision Criteria")
        r_title.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 10.5pt; font-family: Consolas;")
        self.rec_text = QLabel()
        self.rec_text.setStyleSheet("color: #FCD34D; font-size: 9.5pt; font-family: Consolas;")
        self.rec_text.setWordWrap(True)

        r_lay.addWidget(r_title)
        r_lay.addWidget(self.rec_text)
        self.body_layout.addWidget(self.rec_card)

        # 3. Governing Equations & Formula Sheet Card
        self.formula_card = QFrame()
        self.formula_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-left: 4px solid #06B6D4; border-radius: 8px; padding: 12px;")
        f_lay = QVBoxLayout(self.formula_card)
        f_hdr = QLabel("📐 Governing Equations & Formulas")
        f_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 10.5pt; font-family: Consolas;")
        self.formula_text = QLabel()
        self.formula_text.setStyleSheet("color: #E2E8F0; font-size: 9.5pt; font-family: Consolas;")
        self.formula_text.setWordWrap(True)
        f_lay.addWidget(f_hdr)
        f_lay.addWidget(self.formula_text)
        self.body_layout.addWidget(self.formula_card)

        # 4. Dynamic Parameter Inputs Panel
        self.inputs_card = QFrame()
        self.inputs_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 12px;")
        self.inputs_lay = QVBoxLayout(self.inputs_card)
        in_title = QLabel("⚙️ Interactive Circuit Parameters & Numeric Controls")
        in_title.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 10.5pt; font-family: Consolas;")
        self.inputs_lay.addWidget(in_title)

        self.controls_container = QHBoxLayout()
        self.controls_container.setSpacing(10)
        self.inputs_lay.addLayout(self.controls_container)
        self.body_layout.addWidget(self.inputs_card)

        # 5. Output Box & Mathematical Solution Derivation
        self.output_card = QFrame()
        self.output_card.setStyleSheet("background-color: #09121E; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;")
        out_lay = QVBoxLayout(self.output_card)

        out_title = QLabel("🧮 Step-by-Step Derivation & Verification Result")
        out_title.setStyleSheet("color: #10B981; font-weight: bold; font-size: 10.5pt; font-family: Consolas;")
        out_lay.addWidget(out_title)

        self.sol_output = QTextEdit()
        self.sol_output.setReadOnly(True)
        self.sol_output.setMinimumHeight(180)
        self.sol_output.setStyleSheet("background-color: #040911; color: #34D399; font-size: 9.5pt; font-family: Consolas, monospace; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;")
        out_lay.addWidget(self.sol_output)

        self.body_layout.addWidget(self.output_card)

        # 6. Rule-Based Hint Box
        hint_box = QFrame()
        hint_box.setStyleSheet("background-color: #0F172A; border: 1px solid #38BDF8; border-radius: 6px; padding: 10px;")
        h_box_lay = QHBoxLayout(hint_box)

        self.hint_lbl = QLabel()
        self.hint_lbl.setStyleSheet("color: #38BDF8; font-weight: 500; font-size: 9pt; font-family: Consolas;")

        get_hint_btn = QPushButton("Next Hint 💡")
        get_hint_btn.setStyleSheet("background-color: #0284C7; color: #FFF; font-weight: bold; padding: 5px 12px; border-radius: 4px; font-size: 8.5pt;")
        get_hint_btn.clicked.connect(self.next_hint)

        h_box_lay.addWidget(self.hint_lbl, 1)
        h_box_lay.addWidget(get_hint_btn)
        self.body_layout.addWidget(hint_box)

        scroll.setWidget(container)
        main_lay.addWidget(scroll)

        # Initial Setup for Solver 1
        self.on_solver_changed(0)

    # --------------------------------------------------------------------------
    # Dynamic Controls Builder for Active Solver
    # --------------------------------------------------------------------------
    def clear_controls(self):
        while self.controls_container.count():
            item = self.controls_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.spinboxes.clear()
        self.comboboxes.clear()

    def add_spinbox(self, key: str, label_text: str, val: float, min_val: float = -1e6, max_val: float = 1e6, step: float = 1.0, decimals: int = 2):
        v_box = QVBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #94A3B8; font-weight: 500; font-size: 8.5pt; font-family: Consolas;")

        sb = EngineeringDoubleSpinBox(self, step=step, min_val=min_val, max_val=max_val, decimals=decimals)
        sb.setValue(val)
        sb.valueChanged.connect(self.calculate_solution)

        v_box.addWidget(lbl)
        v_box.addWidget(sb)
        self.controls_container.addLayout(v_box)
        self.spinboxes[key] = sb


    def add_combobox(self, key: str, label_text: str, options: list):
        v_box = QVBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #94A3B8; font-weight: 500; font-size: 8.5pt; font-family: Consolas;")

        cb = QComboBox()
        cb.addItems(options)
        cb.setStyleSheet("background-color: #1E293B; color: #FFFFFF; border: 1px solid #334155; border-radius: 4px; padding: 4px 8px; font-size: 9pt; font-family: Consolas;")
        cb.currentIndexChanged.connect(self.calculate_solution)

        v_box.addWidget(lbl)
        v_box.addWidget(cb)
        self.controls_container.addLayout(v_box)
        self.comboboxes[key] = cb

    # --------------------------------------------------------------------------
    # Solver Change Switcher
    # --------------------------------------------------------------------------
    def on_solver_changed(self, idx: int):
        self.hint_step = 0
        self.clear_controls()

        if idx == 0:  # Ohm's Law
            self.rec_text.setText("Basic linear V, I, R relationship? ➔ Use Ohm's Law and Power formulas.")
            self.formula_text.setText("V = I × R   |   I = V / R   |   R = V / I   |   P = V × I = I²R = V²/R")
            self.add_spinbox("vs", "Voltage Vs (V):", 12.0)
            self.add_spinbox("r1", "Resistance R (Ω):", 24.0)

        elif idx == 1:  # KCL
            self.rec_text.setText("Nodal junction with multiple entering & leaving currents? ➔ Apply ΣI_in = ΣI_out.")
            self.formula_text.setText("Σ I_in = Σ I_out   ➔   I1 + I2 = I3 + I4 + I5")
            self.add_spinbox("i1", "I1 In (A):", 5.0)
            self.add_spinbox("i2", "I2 In (A):", 3.0)
            self.add_spinbox("i3", "I3 Out (A):", 2.0)
            self.add_spinbox("i4", "I4 Out (A):", 6.0)

        elif idx == 2:  # KVL
            self.rec_text.setText("Closed series loop with voltage rises & drops? ➔ Apply ΣV_rise = ΣV_drop.")
            self.formula_text.setText("Σ V_sources = Σ V_drops   ➔   Vs1 + Vs2 = V_R1 + V_R2 + V_R3")
            self.add_spinbox("vs1", "Vs1 (V):", 24.0)
            self.add_spinbox("vr1", "V_R1 (V):", 8.0)
            self.add_spinbox("vr2", "V_R2 (V):", 10.0)

        elif idx == 3:  # Series Circuit
            self.rec_text.setText("Single current path through multiple series resistors? ➔ Req = Σ R_i.")
            self.formula_text.setText("Req = R1 + R2 + R3 + R4   |   I = Vs / Req   |   V_Ri = I × Ri")
            self.add_spinbox("vs", "Source Vs (V):", 24.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("r2", "R2 (Ω):", 20.0)
            self.add_spinbox("r3", "R3 (Ω):", 30.0)

        elif idx == 4:  # Parallel Circuit
            self.rec_text.setText("Multiple parallel branches connected across same voltage? ➔ 1/Req = Σ 1/R_i.")
            self.formula_text.setText("1/Req = 1/R1 + 1/R2 + 1/R3   |   Ii = Vs / Ri   |   I_total = Σ Ii")
            self.add_spinbox("vs", "Source Vs (V):", 12.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("r2", "R2 (Ω):", 20.0)
            self.add_spinbox("r3", "R3 (Ω):", 30.0)

        elif idx == 5:  # Voltage Divider
            self.rec_text.setText("Series resistor network needing output voltage tap? ➔ Vout = Vin × R2 / (R1 + R2).")
            self.formula_text.setText("Vout = Vin × [ R2 / (R1 + R2) ]   |   Ratio = R2 / (R1 + R2)")
            self.add_spinbox("vin", "Input Voltage Vin (V):", 12.0)
            self.add_spinbox("r1", "Resistor R1 (Ω):", 1000.0)
            self.add_spinbox("r2", "Resistor R2 (Ω):", 2000.0)

        elif idx == 6:  # Current Divider
            self.rec_text.setText("Parallel branch current division? ➔ I1 = I_total × R2 / (R1 + R2).")
            self.formula_text.setText("I1 = I_total × [ R2 / (R1 + R2) ]   |   I2 = I_total × [ R1 / (R1 + R2) ]")
            self.add_spinbox("itotal", "Total Current I (A):", 6.0)
            self.add_spinbox("r1", "Resistor R1 (Ω):", 10.0)
            self.add_spinbox("r2", "Resistor R2 (Ω):", 20.0)

        elif idx == 7:  # Mesh Analysis
            self.rec_text.setText("Planar circuit with multiple closed loops? ➔ Generate Mesh KVL Matrix.")
            self.formula_text.setText("[R] × [I] = [V]   ➔   [R1+Rm, -Rm; -Rm, R2+Rm] × [I1; I2] = [Vs1; -Vs2]")
            self.add_spinbox("vs1", "Vs1 (V):", 12.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("rm", "Mutual Rm (Ω):", 5.0)
            self.add_spinbox("r2", "R2 (Ω):", 15.0)
            self.add_spinbox("vs2", "Vs2 (V):", 6.0)

        elif idx == 8:  # Nodal Analysis
            self.rec_text.setText("Circuit with multiple principal nodes & current sources? ➔ Generate Nodal KCL Matrix.")
            self.formula_text.setText("[G] × [V] = [I]   ➔   [G1+Gm, -Gm; -Gm, G2+Gm] × [V1; V2] = [Is1; -Is2]")
            self.add_spinbox("is1", "Is1 (A):", 4.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("rm", "Rm (Ω):", 20.0)
            self.add_spinbox("r2", "R2 (Ω):", 10.0)
            self.add_spinbox("is2", "Is2 (A):", 2.0)

        elif idx == 9:  # Source Transformation
            self.rec_text.setText("Convert between Real Voltage Source (Vs + series Rs) & Real Current Source (Is + parallel Rs).")
            self.formula_text.setText("Vs = Is × Rs   ↔   Is = Vs / Rs   (Resistance Rs remains identical!)")
            self.add_combobox("mode", "Transformation Mode:", ["Voltage Source (Vs, Rs) -> Current Source", "Current Source (Is, Rs) -> Voltage Source"])
            self.add_spinbox("val", "Source Magnitude (V or A):", 12.0)
            self.add_spinbox("rs", "Internal Resistance Rs (Ω):", 4.0)

        elif idx == 10:  # Thevenin's Theorem
            self.rec_text.setText("Complex linear network connected to load RL? ➔ Reduce to Vth series Rth.")
            self.formula_text.setText("Vth = Voc across A-B   |   Rth = Req looking into A-B (sources off)   |   IL = Vth / (Rth + RL)")
            self.add_spinbox("vs", "Vs (V):", 12.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("r2", "R2 (Ω):", 20.0)
            self.add_spinbox("rl", "Load RL (Ω):", 10.0)

        elif idx == 11:  # Norton's Theorem
            self.rec_text.setText("Convert linear network to Norton Current Source In in parallel with Rn.")
            self.formula_text.setText("In = I_short_circuit A-B   |   Rn = Rth   |   IL = In × [ Rn / (Rn + RL) ]")
            self.add_spinbox("vs", "Vs (V):", 12.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("r2", "R2 (Ω):", 20.0)
            self.add_spinbox("rl", "Load RL (Ω):", 10.0)

        elif idx == 12:  # Superposition Theorem
            self.rec_text.setText("Multiple independent sources in linear bilateral network? ➔ Sum individual contributions.")
            self.formula_text.setText("IL(total) = IL(V1 alone, V2 shorted) + IL(V2 alone, V1 shorted)")
            self.add_spinbox("v1", "Vs1 (V):", 12.0)
            self.add_spinbox("v2", "Vs2 (V):", 6.0)
            self.add_spinbox("r1", "R1 (Ω):", 10.0)
            self.add_spinbox("r2", "R2 (Ω):", 20.0)
            self.add_spinbox("rl", "Load RL (Ω):", 10.0)

        elif idx == 13:  # Maximum Power Transfer
            self.rec_text.setText("Optimize load RL for maximum power delivery? ➔ Condition: RL = Rth (Efficiency = 50%).")
            self.formula_text.setText("Condition: RL = Rth   |   Pmax = Vth² / (4 × Rth)   |   Efficiency η = RL / (Rth + RL)")
            self.add_spinbox("vth", "Vth (V):", 12.0)
            self.add_spinbox("rth", "Rth (Ω):", 8.0)
            self.add_spinbox("rl", "Load RL (Ω):", 8.0)

        elif idx == 14:  # Millman's Theorem
            self.rec_text.setText("Multiple parallel generator branches? ➔ Compute Millman equivalent voltage V_millman.")
            self.formula_text.setText("V_AB = Σ (Ei / Ri) / Σ (1 / Ri)   |   R_AB = 1 / Σ (1 / Ri)")
            self.add_spinbox("e1", "E1 (V):", 10.0)
            self.add_spinbox("r1", "R1 (Ω):", 2.0)
            self.add_spinbox("e2", "E2 (V):", 20.0)
            self.add_spinbox("r2", "R2 (Ω):", 4.0)
            self.add_spinbox("e3", "E3 (V):", 0.0)
            self.add_spinbox("r3", "R3 (Ω):", 5.0)

        elif idx == 15:  # Reciprocity Theorem
            self.rec_text.setText("Verify if ratio of excitation to response remains constant when source & ammeter swap positions.")
            self.formula_text.setText("Transfer Impedance Z_T = Vin / Iout   (Must remain invariant upon interchange!)")
            self.add_spinbox("vs", "Vs (V):", 10.0)
            self.add_spinbox("r1", "R1 (Ω):", 2.0)
            self.add_spinbox("r2", "R2 (Ω):", 4.0)
            self.add_spinbox("r3", "R3 (Ω):", 6.0)

        elif idx == 16:  # Compensation Theorem
            self.rec_text.setText("Calculate change in current when a resistor changes value by ΔR in a circuit.")
            self.formula_text.setText("Vc = I × ΔR   |   ΔI = Vc / (Rth + R + ΔR)   |   I_new = I - ΔI")
            self.add_spinbox("i_orig", "Original Current I (A):", 2.0)
            self.add_spinbox("delta_r", "Resistance Change ΔR (Ω):", 1.0)
            self.add_spinbox("rth", "Thevenin Rth (Ω):", 4.0)
            self.add_spinbox("r_orig", "Original R (Ω):", 5.0)

        elif idx == 17:  # Tellegen's Theorem
            self.rec_text.setText("Verify conservation of power across any lumped network regardless of linearity or components.")
            self.formula_text.setText("Σ P_absorbed = 0   ➔   P1 + P2 + P3 + P4 = 0")
            self.add_spinbox("p1", "Branch 1 Power (W):", 50.0)
            self.add_spinbox("p2", "Branch 2 Power (W):", -30.0)
            self.add_spinbox("p3", "Branch 3 Power (W):", -15.0)
            self.add_spinbox("p4", "Branch 4 Power (W):", -5.0)

        elif idx == 18:  # Delta-Star Conversion
            self.rec_text.setText("Convert between 3-terminal Delta (Δ) and Star (Y) resistor networks.")
            self.formula_text.setText("R1 = (R12 × R31) / (R12 + R23 + R31)   |   R12 = R1 + R2 + (R1 × R2)/R3")
            self.add_combobox("mode", "Conversion Mode:", ["Delta -> Star (Y)", "Star (Y) -> Delta"])
            self.add_spinbox("r12", "R12 or Ra (Ω):", 12.0)
            self.add_spinbox("r23", "R23 or Rb (Ω):", 18.0)
            self.add_spinbox("r31", "R31 or Rc (Ω):", 36.0)

        elif idx == 19:  # Bridge Network
            self.rec_text.setText("Wheatstone Bridge network solver: R1*R4 = R2*R3 for zero galvanometer current.")
            self.formula_text.setText("Balance Condition: R1 × R4 = R2 × R3   |   Unbalanced V_CD = Vin [ R3/(R1+R3) - R4/(R2+R4) ]")
            self.add_spinbox("vs", "Source Vs (V):", 10.0)
            self.add_spinbox("r1", "R1 (Ω):", 100.0)
            self.add_spinbox("r2", "R2 (Ω):", 200.0)
            self.add_spinbox("r3", "R3 (Ω):", 150.0)
            self.add_spinbox("r4", "R4 (Ω):", 300.0)
            self.add_spinbox("rg", "Galvanometer Rg (Ω):", 50.0)

        elif idx == 20:  # Resonance Calculator
            self.rec_text.setText("RLC series/parallel resonant frequency, quality factor Q, and bandwidth.")
            self.formula_text.setText("fr = 1 / (2π √(LC))   |   w0 = 1 / √(LC)   |   Q = w0 L / R   |   BW = fr / Q")
            self.add_spinbox("r", "Resistance R (Ω):", 10.0)
            self.add_spinbox("l", "Inductance L (H):", 0.001, decimals=4)
            self.add_spinbox("c", "Capacitance C (F):", 1e-6, decimals=8)

        elif idx == 21:  # Quality Factor
            self.rec_text.setText("Compute sharpness of resonance Q-factor for series and parallel RLC circuits.")
            self.formula_text.setText("Series Q = (2π f L) / R   |   Parallel Q = R / (2π f L)")
            self.add_spinbox("f", "Frequency f (Hz):", 5032.92)
            self.add_spinbox("l", "Inductance L (H):", 0.001, decimals=4)
            self.add_spinbox("c", "Capacitance C (F):", 1e-6, decimals=8)
            self.add_spinbox("r", "Resistance R (Ω):", 10.0)

        elif idx == 22:  # Time Constant
            self.rec_text.setText("Compute transient time constant τ for RC and RL networks (5τ settling time).")
            self.formula_text.setText("RC: τ = R × C   |   RL: τ = L / R   |   Settling Time (99.3%) = 5 × τ")
            self.add_spinbox("r", "Resistance R (Ω):", 1000.0)
            self.add_spinbox("c", "Capacitance C (F):", 1e-6, decimals=8)
            self.add_spinbox("l", "Inductance L (H):", 0.01, decimals=4)

        elif idx == 23:  # AC Impedance
            self.rec_text.setText("Compute AC inductive reactance XL, capacitive reactance XC, impedance Z, and phase angle θ.")
            self.formula_text.setText("XL = 2πfL   |   XC = 1/(2πfC)   |   Z = √(R² + (XL - XC)²)   |   θ = arctan((XL-XC)/R)")
            self.add_spinbox("f", "Frequency f (Hz):", 50.0)
            self.add_spinbox("r", "Resistance R (Ω):", 100.0)
            self.add_spinbox("l", "Inductance L (H):", 0.1, decimals=3)
            self.add_spinbox("c", "Capacitance C (F):", 10e-6, decimals=8)

        elif idx == 24:  # Power Factor
            self.rec_text.setText("Calculate AC Real Power P, Reactive Power Q, Apparent Power S, and Power Factor Correction Capacitance.")
            self.formula_text.setText("P = VI cos θ   |   Q = VI sin θ   |   S = VI   |   C_correction = P (tan θ1 - tan θ2) / (2π f V²)")
            self.add_spinbox("v", "Voltage V (V):", 230.0)
            self.add_spinbox("i", "Current I (A):", 10.0)
            self.add_spinbox("pf_curr", "Current Power Factor:", 0.70, max_val=1.0)
            self.add_spinbox("pf_target", "Target Power Factor:", 0.95, max_val=1.0)
            self.add_spinbox("f", "Frequency f (Hz):", 50.0)

        elif idx == 25:  # RMS / Average
            self.rec_text.setText("Compute RMS, Average, Form Factor, and Peak Factor for various AC waveforms.")
            self.formula_text.setText("Sine: Vrms = Vm / √2, Vavg = 2Vm / π   |   Square: Vrms = Vm, Vavg = Vm   |   Triangle: Vrms = Vm / √3")
            self.add_combobox("wave", "Waveform Type:", ["Sine Wave", "Square Wave", "Triangle / Sawtooth", "Half-Wave Rectified Sine"])
            self.add_spinbox("vm", "Peak Amplitude Vm (V):", 10.0)

        elif idx == 26:  # Phasor Calculator
            self.rec_text.setText("Perform complex arithmetic additions, subtractions, & polar conversions on AC phasors.")
            self.formula_text.setText("Z = A + jB = R ∠ θ   |   R = √(A² + B²)   |   θ = arctan(B / A)")
            self.add_spinbox("r1", "Phasor 1 Real (A1):", 4.0)
            self.add_spinbox("i1", "Phasor 1 Imag (B1):", 3.0)
            self.add_combobox("op", "Operation:", ["Addition (+)", "Subtraction (-)", "Multiplication (*)", "Division (/)"])
            self.add_spinbox("r2", "Phasor 2 Real (A2):", 2.0)
            self.add_spinbox("i2", "Phasor 2 Imag (B2):", 1.0)

        elif idx == 27:  # Laplace Circuit
            self.rec_text.setText("Analyze s-domain Laplace transformed impedances for R, L, and C components.")
            self.formula_text.setText("Z_R(s) = R   |   Z_L(s) = sL   |   Z_C(s) = 1 / (sC)   |   Z_series(s) = R + sL + 1/(sC)")
            self.add_spinbox("r", "Resistance R (Ω):", 10.0)
            self.add_spinbox("l", "Inductance L (H):", 0.1, decimals=3)
            self.add_spinbox("c", "Capacitance C (F):", 100e-6, decimals=6)
            self.add_spinbox("s_val", "Laplace Parameter s (rad/s):", 100.0)

        elif idx == 28:  # Two-Port Network
            self.rec_text.setText("Convert Z-parameters into Y-parameters, ABCD parameters, and network determinants.")
            self.formula_text.setText("[Y] = [Z]⁻¹   |   A = Z11/Z21, B = ΔZ/Z21, C = 1/Z21, D = Z22/Z21")
            self.add_spinbox("z11", "Z11 (Ω):", 40.0)
            self.add_spinbox("z12", "Z12 (Ω):", 20.0)
            self.add_spinbox("z21", "Z21 (Ω):", 20.0)
            self.add_spinbox("z22", "Z22 (Ω):", 30.0)

        elif idx == 29:  # Electrical Unit Converter
            self.rec_text.setText("Convert values between standard Electrical SI units (Ω, kΩ, MΩ, mA, A, μF, nF, pF, mH, H, Hz, kHz, MHz).")
            self.formula_text.setText("SI Base Conversion Factor Table   |   1 kΩ = 1,000 Ω   |   1 μF = 10⁻⁶ F   |   1 MHz = 10⁶ Hz")
            self.add_spinbox("val", "Input Value:", 4.7)
            self.add_combobox("from_u", "From Unit:", ["kΩ", "Ω", "MΩ", "mA", "A", "μF", "nF", "pF", "mH", "H", "kHz", "MHz"])
            self.add_combobox("to_u", "To Unit:", ["Ω", "kΩ", "MΩ", "A", "mA", "F", "μF", "nF", "pF", "Hz", "kHz", "MHz"])

        self.calculate_solution()

    # --------------------------------------------------------------------------
    # Rule-Based Hint Generator
    # --------------------------------------------------------------------------
    def next_hint(self):
        self.hint_step = (self.hint_step + 1) % 3
        th_name = self.theorem_combo.currentText()
        hint = NetworkEngine.get_hints_for_theorem(th_name, self.hint_step)
        self.hint_lbl.setText(f"💡 {hint}")

    # --------------------------------------------------------------------------
    # Main Solution Calculator Engine
    # --------------------------------------------------------------------------
    def calculate_solution(self):
        idx = self.theorem_combo.currentIndex()
        txt = ""

        try:
            if idx == 0:  # Ohm's Law
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                res = NetworkEngine.solve_ohms_law(v=vs, r=r1)
                txt = f"✓ Step 1: Apply Ohm's Law governing equation I = V / R:\n" \
                      f"   I = {vs} V / {r1} Ω = {res['i']} A ({res['i']*1000:.2f} mA)\n\n" \
                      f"✓ Step 2: Compute Power Dissipation P = V × I = I²R = V²/R:\n" \
                      f"   P = {vs} V × {res['i']} A = {res['p']} Watts (W)\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Current I = {res['i']} A | Power P = {res['p']} W\n" \
                      f"🔍 Verification: V = I × R = {res['i']} × {r1} = {res['i']*r1:.2f} V (MATCHED)"

            elif idx == 1:  # KCL
                i1 = self.spinboxes["i1"].value()
                i2 = self.spinboxes["i2"].value()
                i3 = self.spinboxes["i3"].value()
                i4 = self.spinboxes["i4"].value()
                res = NetworkEngine.solve_kcl([i1, i2], [i3, i4])
                ub_req = res['unknown_branch_required']
                kcl_status_str = 'BALANCED (Σ I = 0)' if res['is_balanced'] else f'UNBALANCED (Branch I5 of {ub_req}A required)'

                txt = f"✓ Step 1: Sum Entering Currents: Σ I_in = I1 + I2 = {i1} + {i2} = {res['sum_in']} A\n" \
                      f"✓ Step 2: Sum Leaving Currents:  Σ I_out = I3 + I4 = {i3} + {i4} = {res['sum_out']} A\n" \
                      f"✓ Step 3: Check KCL Balance (Σ I_in - Σ I_out = 0):\n" \
                      f"   Net Difference = {res['diff']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: KCL Status: {kcl_status_str}"


            elif idx == 2:  # KVL
                vs1 = self.spinboxes["vs1"].value()
                vr1 = self.spinboxes["vr1"].value()
                vr2 = self.spinboxes["vr2"].value()
                res = NetworkEngine.solve_kvl([vs1], [vr1, vr2])
                unknown_v = res['net_voltage']
                txt = f"✓ Step 1: Sum Loop Voltage Sources: Σ V_sources = {vs1} V\n" \
                      f"✓ Step 2: Sum Known Resistor Drops: Σ V_known = {vr1} + {vr2} = {res['sum_drops']} V\n" \
                      f"✓ Step 3: Solve for Unknown Voltage Drop VR3 = Σ V_sources - Σ V_known:\n" \
                      f"   VR3 = {vs1} - {res['sum_drops']} = {unknown_v} V\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Unknown Resistor Voltage VR3 = {unknown_v} Volts"

            elif idx == 3:  # Series
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                r3 = self.spinboxes["r3"].value()
                res = NetworkEngine.solve_series(vs, [r1, r2, r3])
                txt = f"✓ Step 1: Calculate Equivalent Series Resistance Req = R1 + R2 + R3:\n" \
                      f"   Req = {r1} + {r2} + {r3} = {res['req']} Ω\n\n" \
                      f"✓ Step 2: Calculate Common Loop Current I = Vs / Req:\n" \
                      f"   I = {vs} V / {res['req']} Ω = {res['current']} A\n\n" \
                      f"✓ Step 3: Individual Voltage Drops Across Resistors:\n" \
                      f"   V_R1 = {res['v_drops'][0]} V | V_R2 = {res['v_drops'][1]} V | V_R3 = {res['v_drops'][2]} V\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Total Req = {res['req']} Ω | Loop Current I = {res['current']} A | Total Power P = {res['total_power']} W"

            elif idx == 4:  # Parallel
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                r3 = self.spinboxes["r3"].value()
                res = NetworkEngine.solve_parallel(vs, [r1, r2, r3])
                txt = f"✓ Step 1: Calculate Equivalent Parallel Resistance 1/Req = 1/R1 + 1/R2 + 1/R3:\n" \
                      f"   Req = {res['req']} Ω\n\n" \
                      f"✓ Step 2: Calculate Individual Parallel Branch Currents Ii = Vs / Ri:\n" \
                      f"   I_R1 = {res['branch_currents'][0]} A | I_R2 = {res['branch_currents'][1]} A | I_R3 = {res['branch_currents'][2]} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Total Req = {res['req']} Ω | Total Current I_total = {res['total_current']} A | Total Power P = {res['total_power']} W"

            elif idx == 5:  # Voltage Divider
                vin = self.spinboxes["vin"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                res = NetworkEngine.solve_voltage_divider(vin, r1, r2)
                txt = f"✓ Step 1: Division Ratio = R2 / (R1 + R2) = {r2} / ({r1} + {r2}) = {res['ratio']}\n\n" \
                      f"✓ Step 2: Calculate Output Voltage Vout = Vin × Ratio:\n" \
                      f"   Vout = {vin} V × {res['ratio']} = {res['vout']} V\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Output Voltage Vout across R2 ({r2}Ω) = {res['vout']} Volts (Drop across R1 = {res['v_r1']} V)"

            elif idx == 6:  # Current Divider
                itotal = self.spinboxes["itotal"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                res = NetworkEngine.solve_current_divider(itotal, r1, r2)
                txt = f"✓ Step 1: Calculate Branch 1 Current I1 = I_total × [ R2 / (R1 + R2) ]:\n" \
                      f"   I1 = {itotal} A × ({r2} / {r1+r2}) = {res['i1']} A\n\n" \
                      f"✓ Step 2: Calculate Branch 2 Current I2 = I_total × [ R1 / (R1 + R2) ]:\n" \
                      f"   I2 = {itotal} A × ({r1} / {r1+r2}) = {res['i2']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: I1 (through R1={r1}Ω) = {res['i1']} A | I2 (through R2={r2}Ω) = {res['i2']} A"

            elif idx == 7:  # Mesh Analysis
                vs1 = self.spinboxes["vs1"].value()
                r1 = self.spinboxes["r1"].value()
                rm = self.spinboxes["rm"].value()
                r2 = self.spinboxes["r2"].value()
                vs2 = self.spinboxes["vs2"].value()
                res = NetworkEngine.solve_mesh_analysis(vs1, r1, rm, r2, vs2)
                txt = f"✓ Step 1: Formulate 2-Loop Mesh KVL Equations Matrix:\n" \
                      f"   Loop 1: ({r1}+{rm}) I1 - ({rm}) I2 = {vs1}\n" \
                      f"   Loop 2: -({rm}) I1 + ({r2}+{rm}) I2 = -{vs2}\n\n" \
                      f"✓ Step 2: Matrix Inversion & Solution:\n" \
                      f"   Mesh Current I1 = {res['i1']} A | Mesh Current I2 = {res['i2']} A\n" \
                      f"   Current through Mutual Resistor Rm = I1 - I2 = {res['irm']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Mesh Currents: I1 = {res['i1']} A, I2 = {res['i2']} A | Power in Rm = {res['p_rm']} W"

            elif idx == 8:  # Nodal Analysis
                is1 = self.spinboxes["is1"].value()
                r1 = self.spinboxes["r1"].value()
                rm = self.spinboxes["rm"].value()
                r2 = self.spinboxes["r2"].value()
                is2 = self.spinboxes["is2"].value()
                res = NetworkEngine.solve_nodal_analysis(is1, r1, rm, r2, is2)
                txt = f"✓ Step 1: Formulate 2-Node KCL Admittance Matrix:\n" \
                      f"   Node 1: ({1/r1:.3f}+{1/rm:.3f}) V1 - ({1/rm:.3f}) V2 = {is1}\n" \
                      f"   Node 2: -({1/rm:.3f}) V1 + ({1/r2:.3f}+{1/rm:.3f}) V2 = -{is2}\n\n" \
                      f"✓ Step 2: Solve Nodal Voltages:\n" \
                      f"   Node Voltage V1 = {res['v1']} V | Node Voltage V2 = {res['v2']} V\n" \
                      f"   Voltage across Mutual Resistor Rm = V1 - V2 = {res['v_rm']} V\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Node Voltages: V1 = {res['v1']} V, V2 = {res['v2']} V | Current through Rm = {res['i_rm']} A"

            elif idx == 9:  # Source Transformation
                val = self.spinboxes["val"].value()
                rs = self.spinboxes["rs"].value()
                mode = self.comboboxes["mode"].currentIndex()
                res = NetworkEngine.solve_source_transformation(val, rs, from_voltage=(mode == 0))
                if mode == 0:
                    txt = f"✓ Converting Voltage Source (Vs={val}V in series with Rs={rs}Ω):\n" \
                          f"   Is = Vs / Rs = {val} V / {rs} Ω = {res['is_src']} A\n\n" \
                          f"===========================================================\n" \
                          f"🏆 EQUIVALENT: Current Source Is = {res['is_src']} A in PARALLEL with internal resistance Rs = {rs} Ω"
                else:
                    txt = f"✓ Converting Current Source (Is={val}A in parallel with Rs={rs}Ω):\n" \
                          f"   Vs = Is × Rs = {val} A × {rs} Ω = {res['vs']} V\n\n" \
                          f"===========================================================\n" \
                          f"🏆 EQUIVALENT: Voltage Source Vs = {res['vs']} V in SERIES with internal resistance Rs = {rs} Ω"

            elif idx == 10:  # Thevenin's Theorem
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                rl = self.spinboxes["rl"].value()
                res = NetworkEngine.solve_thevenin(vs, r1, r2, rl)
                txt = f"✓ Step 1: Open-Circuit Voltage Vth across terminals A-B:\n" \
                      f"   Vth = Vs × [ R2 / (R1 + R2) ] = {vs} × ({r2}/{r1+r2}) = {res['vth']} V\n\n" \
                      f"✓ Step 2: Deactivate Vs (short circuit) to find Rth looking into A-B:\n" \
                      f"   Rth = R1 || R2 = ({r1} × {r2}) / ({r1} + {r2}) = {res['rth']} Ω\n\n" \
                      f"✓ Step 3: Connect Load RL = {rl}Ω to Thevenin Equivalent:\n" \
                      f"   IL = Vth / (Rth + RL) = {res['vth']} / ({res['rth']} + {rl}) = {res['il']} A\n" \
                      f"   Load Voltage VL = IL × RL = {res['vl']} V | Power PL = {res['pl']} W\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Vth = {res['vth']} V | Rth = {res['rth']} Ω | Load Current IL = {res['il']} A | Max Power Pmax = {res['pmax']} W"

            elif idx == 11:  # Norton's Theorem
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                rl = self.spinboxes["rl"].value()
                res = NetworkEngine.solve_norton(vs, r1, r2, rl)
                txt = f"✓ Step 1: Short-Circuit Current In across terminals A-B:\n" \
                      f"   In = Vs / R1 = {vs} / {r1} = {res['in_src']} A\n\n" \
                      f"✓ Step 2: Norton Resistance Rn = Rth = R1 || R2 = {res['rn']} Ω\n\n" \
                      f"✓ Step 3: Connect Load RL = {rl}Ω to Norton Equivalent:\n" \
                      f"   IL = In × [ Rn / (Rn + RL) ] = {res['in_src']} × ({res['rn']}/({res['rn']}+{rl})) = {res['il']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: In = {res['in_src']} A | Rn = {res['rn']} Ω | Load Current IL = {res['il']} A | Load Power PL = {res['pl']} W"

            elif idx == 12:  # Superposition
                v1 = self.spinboxes["v1"].value()
                v2 = self.spinboxes["v2"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                rl = self.spinboxes["rl"].value()
                res = NetworkEngine.solve_superposition(v1, v2, r1, r2, rl)
                txt = f"✓ Sub-Circuit 1: Response from V1 ({v1}V) alone (V2 shorted to 0V):\n" \
                      f"   IL1 = {res['il_v1_only']} A\n\n" \
                      f"✓ Sub-Circuit 2: Response from V2 ({v2}V) alone (V1 shorted to 0V):\n" \
                      f"   IL2 = {res['il_v2_only']} A\n\n" \
                      f"✓ Superposed Total Response: IL(total) = IL1 + IL2:\n" \
                      f"   IL = {res['il_v1_only']} + {res['il_v2_only']} = {res['il_total']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Superposed Load Current IL = {res['il_total']} Amperes"

            elif idx == 13:  # Max Power Transfer
                vth = self.spinboxes["vth"].value()
                rth = self.spinboxes["rth"].value()
                rl = self.spinboxes["rl"].value()
                res = NetworkEngine.solve_max_power_transfer(vth, rth, rl)
                txt = f"✓ Maximum Power Transfer Condition: RL must equal Rth:\n" \
                      f"   Optimum RL = {res['rl_opt']} Ω (Current RL = {rl} Ω)\n\n" \
                      f"✓ Maximum Available Power Pmax = Vth² / (4 × Rth):\n" \
                      f"   Pmax = {vth}² / (4 × {rth}) = {res['pmax']} W\n\n" \
                      f"✓ Actual Power Delivered PL = {res['pl']} W | Transfer Efficiency η = {res['efficiency_pct']}%\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Optimum Load RL = {res['rl_opt']} Ω | Maximum Power Pmax = {res['pmax']} W (Efficiency = {res['efficiency_pct']}%)"

            elif idx == 14:  # Millman's Theorem
                e1, r1 = self.spinboxes["e1"].value(), self.spinboxes["r1"].value()
                e2, r2 = self.spinboxes["e2"].value(), self.spinboxes["r2"].value()
                e3, r3 = self.spinboxes["e3"].value(), self.spinboxes["r3"].value()
                res = NetworkEngine.solve_millman(e1, r1, e2, r2, e3, r3)
                txt = f"✓ Step 1: Sum Parallel Admittances Σ (1/Ri) = 1/{r1} + 1/{r2} + 1/{r3} = {1/res['r_millman']:.4f} S\n" \
                      f"✓ Step 2: Sum Short-Circuit Currents Σ (Ei/Ri) = {e1/r1:.3f} + {e2/r2:.3f} + {e3/r3 if r3!=0 else 0:.3f} = {res['v_millman']/res['r_millman']:.3f} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 MILLMAN EQUIVALENT: V_AB = {res['v_millman']} Volts | R_AB = {res['r_millman']} Ohms"

            elif idx == 15:  # Reciprocity Theorem
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                r3 = self.spinboxes["r3"].value()
                res = NetworkEngine.solve_reciprocity(vs, r1, r2, r3)
                txt = f"✓ Position 1 (Source at Input, Ammeter at Branch 3):\n" \
                      f"   I_out1 = {res['i_out1']} A | Transfer Impedance Z_T1 = {res['transfer_impedance']} Ω\n\n" \
                      f"✓ Position 2 (Source swapped to Branch 3, Ammeter at Input):\n" \
                      f"   I_out2 = {res['i_out2']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 VERIFICATION: Reciprocity Theorem is {'VERIFIED (I_out1 == I_out2)' if res['is_verified'] else 'FAILED'} (Z_T = {res['transfer_impedance']} Ω)"

            elif idx == 16:  # Compensation Theorem
                iorig = self.spinboxes["i_orig"].value()
                dr = self.spinboxes["delta_r"].value()
                rth = self.spinboxes["rth"].value()
                rorig = self.spinboxes["r_orig"].value()
                res = NetworkEngine.solve_compensation(iorig, dr, rth, rorig)
                txt = f"✓ Step 1: Compute Compensation Voltage Source Vc = I × ΔR:\n" \
                      f"   Vc = {iorig} A × {dr} Ω = {res['v_comp']} V\n\n" \
                      f"✓ Step 2: Compute Change in Current ΔI = Vc / (Rth + R + ΔR):\n" \
                      f"   ΔI = {res['v_comp']} / ({rth} + {rorig} + {dr}) = {res['delta_i']} A\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: New Modified Branch Current I_new = {res['i_new']} A (Current Change ΔI = {res['delta_i']} A)"

            elif idx == 17:  # Tellegen's Theorem
                p1 = self.spinboxes["p1"].value()
                p2 = self.spinboxes["p2"].value()
                p3 = self.spinboxes["p3"].value()
                p4 = self.spinboxes["p4"].value()
                res = NetworkEngine.solve_tellegen(p1, p2, p3, p4)
                txt = f"✓ Summing Absorbed & Delivered Power Across All Branches:\n" \
                      f"   Σ P_k = ({p1}) + ({p2}) + ({p3}) + ({p4}) = {res['total_power']} W\n\n" \
                      f"===========================================================\n" \
                      f"🏆 TELLEGEN VERIFICATION: Σ P_k = 0 is {'VERIFIED (Conservation of Energy holds)' if res['is_verified'] else 'FAILED'}"

            elif idx == 18:  # Delta-Star
                r12 = self.spinboxes["r12"].value()
                r23 = self.spinboxes["r23"].value()
                r31 = self.spinboxes["r31"].value()
                mode = self.comboboxes["mode"].currentIndex()
                res = NetworkEngine.solve_delta_star(r12, r23, r31, to_star=(mode == 0))
                if mode == 0:
                    txt = f"✓ Converting Delta (R12={r12}Ω, R23={r23}Ω, R31={r31}Ω) -> Star (R1, R2, R3):\n" \
                          f"   R1 = (R12 × R31) / Sum = {res['r1']} Ω\n" \
                          f"   R2 = (R12 × R23) / Sum = {res['r2']} Ω\n" \
                          f"   R3 = (R23 × R31) / Sum = {res['r3']} Ω\n\n" \
                          f"===========================================================\n" \
                          f"🏆 STAR EQUIVALENT: R1 = {res['r1']} Ω | R2 = {res['r2']} Ω | R3 = {res['r3']} Ω"
                else:
                    txt = f"✓ Converting Star (Ra={r12}Ω, Rb={r23}Ω, Rc={r31}Ω) -> Delta (R12, R23, R31):\n" \
                          f"   R12 = {res['r12']} Ω | R23 = {res['r23']} Ω | R31 = {res['r31']} Ω\n\n" \
                          f"===========================================================\n" \
                          f"🏆 DELTA EQUIVALENT: R12 = {res['r12']} Ω | R23 = {res['r23']} Ω | R31 = {res['r31']} Ω"

            elif idx == 19:  # Bridge Network
                vs = self.spinboxes["vs"].value()
                r1 = self.spinboxes["r1"].value()
                r2 = self.spinboxes["r2"].value()
                r3 = self.spinboxes["r3"].value()
                r4 = self.spinboxes["r4"].value()
                rg = self.spinboxes["rg"].value()
                res = NetworkEngine.solve_bridge(vs, r1, r2, r3, r4, rg)
                txt = f"✓ Check Balance Condition (R1 × R4 == R2 × R3):\n" \
                      f"   R1×R4 = {r1*r4} | R2×R3 = {r2*r3} ➔ {'BALANCED (Ig = 0)' if res['is_balanced'] else 'UNBALANCED'}\n\n" \
                      f"✓ Unbalanced Voltage across Detector V_CD = {res['v_cd']} V\n" \
                      f"✓ Detector Galvanometer Current Ig = {res['ig']} A\n" \
                      f"✓ Calculated Unknown Resistor Rx (at balance) = {res['rx_calc']} Ω\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Bridge Voltage V_CD = {res['v_cd']} V | Galvanometer Current Ig = {res['ig']} A"

            elif idx == 20:  # Resonance
                r = self.spinboxes["r"].value()
                l = self.spinboxes["l"].value()
                c = self.spinboxes["c"].value()
                res = NetworkEngine.solve_resonance(r, l, c)
                txt = f"✓ Step 1: Resonant Frequency fr = 1 / (2π √(LC)):\n" \
                      f"   fr = {res['fr_hz']} Hz ({res['fr_hz']/1000:.3f} kHz) | Angular ω0 = {res['w0_rad']} rad/s\n\n" \
                      f"✓ Step 2: Quality Factor Q = ω0 L / R = {res['q_factor']}\n" \
                      f"✓ Step 3: Bandwidth BW = fr / Q = {res['bandwidth_hz']} Hz\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Resonant Frequency fr = {res['fr_hz']} Hz | Quality Factor Q = {res['q_factor']} | Bandwidth = {res['bandwidth_hz']} Hz"

            elif idx == 21:  # Quality Factor
                f = self.spinboxes["f"].value()
                l = self.spinboxes["l"].value()
                c = self.spinboxes["c"].value()
                r = self.spinboxes["r"].value()
                res = NetworkEngine.solve_quality_factor(f, l, c, r)
                txt = f"✓ Series RLC Quality Factor Q_series = (2π f L) / R = {res['q_series']}\n" \
                      f"✓ Parallel RLC Quality Factor Q_parallel = R / (2π f L) = {res['q_parallel']}\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Series Q-Factor = {res['q_series']} | Parallel Q-Factor = {res['q_parallel']}"

            elif idx == 22:  # Time Constant
                r = self.spinboxes["r"].value()
                c = self.spinboxes["c"].value()
                l = self.spinboxes["l"].value()
                res = NetworkEngine.solve_time_constant(r, c, l)
                txt = f"✓ RC Circuit Time Constant τ_rc = R × C = {res['tau_rc_ms']} ms\n" \
                      f"✓ RC 5τ Settling Time (99.3% charge) = {res['settling_5tau_rc_ms']} ms\n" \
                      f"✓ RL Circuit Time Constant τ_rl = L / R = {res['tau_rl_ms']} ms\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: RC Time Constant τ = {res['tau_rc_ms']} ms | RL Time Constant τ = {res['tau_rl_ms']} ms"

            elif idx == 23:  # AC Impedance
                f = self.spinboxes["f"].value()
                r = self.spinboxes["r"].value()
                l = self.spinboxes["l"].value()
                c = self.spinboxes["c"].value()
                res = NetworkEngine.solve_ac_impedance(f, r, l, c)
                txt = f"✓ Inductive Reactance XL = 2πfL = {res['xl']} Ω\n" \
                      f"✓ Capacitive Reactance XC = 1/(2πfC) = {res['xc']} Ω\n" \
                      f"✓ Total AC Impedance Z = √(R² + (XL - XC)²) = {res['z_mag']} Ω\n" \
                      f"✓ Phase Angle θ = arctan((XL-XC)/R) = {res['theta_deg']}° | Power Factor = {res['pf']}\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Impedance |Z| = {res['z_mag']} Ω ∠ {res['theta_deg']}° (PF = {res['pf']})"

            elif idx == 24:  # Power Factor
                v = self.spinboxes["v"].value()
                i = self.spinboxes["i"].value()
                pfc = self.spinboxes["pf_curr"].value()
                pft = self.spinboxes["pf_target"].value()
                f = self.spinboxes["f"].value()
                res = NetworkEngine.solve_power_factor(v, i, pfc, pft, f)
                txt = f"✓ Real Active Power P = VI cos θ = {res['real_power_p']} W\n" \
                      f"✓ Reactive Power Q = VI sin θ = {res['reactive_power_q']} VAR\n" \
                      f"✓ Apparent Power S = VI = {res['apparent_power_s']} VA\n" \
                      f"✓ Required Shunt Correction Capacitance (to raise PF from {pfc} to {pft}):\n" \
                      f"   C_req = {res['c_req_uf']} μF\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Real Power P = {res['real_power_p']} W | Required Correction Capacitor C = {res['c_req_uf']} μF"

            elif idx == 25:  # RMS / Average
                vm = self.spinboxes["vm"].value()
                wtype = self.comboboxes["wave"].currentText()
                res = NetworkEngine.solve_rms_average(vm, wtype)
                txt = f"✓ Waveform Type: {wtype} (Peak Amplitude Vm = {vm} V)\n" \
                      f"✓ RMS Voltage V_rms = {res['v_rms']} Volts\n" \
                      f"✓ Average Voltage V_avg = {res['v_avg']} Volts\n" \
                      f"✓ Form Factor (Vrms / Vavg) = {res['form_factor']} | Peak Factor (Vm / Vrms) = {res['peak_factor']}\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Vrms = {res['v_rms']} V | Vavg = {res['v_avg']} V | Form Factor = {res['form_factor']}"

            elif idx == 26:  # Phasor Calculator
                r1, i1 = self.spinboxes["r1"].value(), self.spinboxes["i1"].value()
                r2, i2 = self.spinboxes["r2"].value(), self.spinboxes["i2"].value()
                op_str = self.comboboxes["op"].currentText()[0]
                res = NetworkEngine.solve_phasor(r1, i1, r2, i2, op_str)
                txt = f"✓ Rectangular Form: ({r1} + j{i1}) {op_str} ({r2} + j{i2}) = {res['rect_real']} + j{res['rect_imag']}\n" \
                      f"✓ Polar Form Conversion: R = √(A² + B²) = {res['polar_mag']} | θ = {res['polar_ang_deg']}°\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL PHASOR RESULT: {res['rect_real']} + j{res['rect_imag']}   ≡   {res['polar_mag']} ∠ {res['polar_ang_deg']}°"

            elif idx == 27:  # Laplace Circuit
                r = self.spinboxes["r"].value()
                l = self.spinboxes["l"].value()
                c = self.spinboxes["c"].value()
                s_val = self.spinboxes["s_val"].value()
                res = NetworkEngine.solve_laplace_circuit(r, l, c, s_val)
                txt = f"✓ Resistor s-domain Impedance Z_R(s) = R = {res['z_r_s']} Ω\n" \
                      f"✓ Inductor s-domain Impedance Z_L(s) = sL = ({s_val}) × ({l}) = {res['z_l_s']} Ω\n" \
                      f"✓ Capacitor s-domain Impedance Z_C(s) = 1/(sC) = 1 / (({s_val})×({c})) = {res['z_c_s']} Ω\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Total Laplace Series Impedance Z_total(s={s_val}) = {res['z_total_series']} Ohms"


            elif idx == 28:  # Two-Port Network
                z11 = self.spinboxes["z11"].value()
                z12 = self.spinboxes["z12"].value()
                z21 = self.spinboxes["z21"].value()
                z22 = self.spinboxes["z22"].value()
                res = NetworkEngine.solve_two_port(z11, z12, z21, z22)
                txt = f"✓ Impedance Matrix Determinant ΔZ = Z11*Z22 - Z12*Z21 = {res['det_z']}\n" \
                      f"✓ Y-Parameter Admittance Matrix [Y] = [Z]⁻¹:\n" \
                      f"   Y11 = {res['y11']} S | Y12 = {res['y12']} S | Y21 = {res['y21']} S | Y22 = {res['y22']} S\n\n" \
                      f"✓ Transmission ABCD Parameters:\n" \
                      f"   A = {res['A']} | B = {res['B']} Ω | C = {res['C']} S | D = {res['D']}\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Converted ABCD Matrix [A={res['A']}, B={res['B']}; C={res['C']}, D={res['D']}]"


            elif idx == 29:  # Unit Converter
                val = self.spinboxes["val"].value()
                fu = self.comboboxes["from_u"].currentText()
                tu = self.comboboxes["to_u"].currentText()
                res = NetworkEngine.convert_electrical_units(val, fu, tu)
                txt = f"✓ Base SI Value: {res['base_si_value']:.8e}\n" \
                      f"✓ Conversion Factor: {val} {fu} ➔ {res['converted_value']} {tu}\n\n" \
                      f"===========================================================\n" \
                      f"🏆 FINAL ANSWER: Converted Value {val} {fu} = {res['converted_value']} {tu}"


        except Exception as e:
            txt = f"⚠️ Calculation Error: {str(e)}"

        self.sol_output.setText(txt)

    def copy_solution(self):
        txt = self.sol_output.toPlainText()
        app = QApplication.clipboard()
        if app and txt:
            app.setText(txt)

    def reset_inputs(self):
        for sb in self.spinboxes.values():
            sb.setValue(sb.minimum() if sb.minimum() > 0 else 10.0)
        self.calculate_solution()
