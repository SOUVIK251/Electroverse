from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox, EngineeringSpinBox


from src.core.analog_engine import AnalogEngine

class AnalogProblemSolvingView(QWidget):
    """Problem Solving Lab with Decision Tree, Interactive Solvers & Offline Hints."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hint_step = 0
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(8, 8, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(15)

        # 1. Circuit Selector Bar
        hdr = QFrame()
        hdr.setObjectName("card-panel")
        hdr.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 10px; }")
        h_lay = QHBoxLayout(hdr)

        h_lbl = QLabel("🧠 Select Circuit Problem Solver:")
        h_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11pt;")

        self.circuit_combo = QComboBox()
        self.circuit_combo.addItems([
            "Biased Clipper Circuit Solver",
            "Clamper DC Offset Solver",
            "Multivibrator Frequency & Duty Cycle"
        ])
        self.circuit_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
        self.circuit_combo.currentIndexChanged.connect(self.on_circuit_changed)

        h_lay.addWidget(h_lbl)
        h_lay.addWidget(self.circuit_combo)
        h_lay.addStretch()
        lay.addWidget(hdr)

        # 2. Recognition Guide (YES/NO Decision Tree)
        dec_card = QFrame()
        dec_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #F59E0B; border-radius: 10px; padding: 15px;")
        d_lay = QVBoxLayout(dec_card)

        d_title = QLabel("🌲 Recognition Guide — How to Identify the Circuit Type")
        d_title.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
        
        self.tree_text = QLabel("Signal peak needs to be cut off above a reference? ➔ YES ➔ Diode in series/parallel with Bias V_B ➔ Use Clipper Circuit!")
        self.tree_text.setStyleSheet("color: #FCD34D; font-size: 10pt; font-weight: 500;")
        self.tree_text.setWordWrap(True)

        d_lay.addWidget(d_title)
        d_lay.addWidget(self.tree_text)
        lay.addWidget(dec_card)

        # 3. Interactive Numerical Solver & Rule-Based Hints
        solver_card = QFrame()
        solver_card.setObjectName("card-panel")
        solver_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; }")
        s_lay = QVBoxLayout(solver_card)

        s_title = QLabel("⚙️ Interactive Step-by-Step Numerical Circuit Solver")
        s_title.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 12pt; border-bottom: 1px solid #26334D; padding-bottom: 6px;")
        s_lay.addWidget(s_title)

        inputs_row = QHBoxLayout()
        
        inputs_row.addWidget(QLabel("Peak Vin (V):", styleSheet="color: #94A3B8;"))
        self.sb_vin = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=100.0, unit="V")
        self.sb_vin.setValue(10.0)
        self.sb_vin.valueChanged.connect(self.calculate_solution)
        inputs_row.addWidget(self.sb_vin)

        inputs_row.addWidget(QLabel("Param 2 (R/RL):", styleSheet="color: #94A3B8;"))
        self.sb_param2 = EngineeringDoubleSpinBox(self, step=10.0, min_val=1.0, max_val=1e6, unit="Ω")
        self.sb_param2.setValue(1000.0)
        self.sb_param2.valueChanged.connect(self.calculate_solution)
        inputs_row.addWidget(self.sb_param2)

        inputs_row.addWidget(QLabel("Param 3 (C/Beta):", styleSheet="color: #94A3B8;"))
        self.sb_param3 = EngineeringDoubleSpinBox(self, step=1.0, min_val=0.01, max_val=1000.0)
        self.sb_param3.setValue(100.0)
        self.sb_param3.valueChanged.connect(self.calculate_solution)
        inputs_row.addWidget(self.sb_param3)


        s_lay.addLayout(inputs_row)

        self.sol_output = QLabel()
        self.sol_output.setStyleSheet("color: #34D399; font-size: 10.5pt; font-weight: bold; background-color: #09121E; padding: 12px; border-radius: 6px; font-family: Consolas, monospace;")
        self.sol_output.setWordWrap(True)
        s_lay.addWidget(self.sol_output)

        # Rule-Based Hint Box
        hint_box = QFrame()
        hint_box.setStyleSheet("background-color: #0F172A; border: 1px solid #38BDF8; border-radius: 6px; padding: 10px;")
        h_box_lay = QHBoxLayout(hint_box)
        
        self.hint_lbl = QLabel("💡 Hint 1: Clipper circuits remove part of the AC waveform above/below threshold.")
        self.hint_lbl.setStyleSheet("color: #38BDF8; font-weight: 500; font-size: 9.5pt;")

        get_hint_btn = QPushButton("Next Hint 💡")
        get_hint_btn.setStyleSheet("background-color: #0284C7; color: #FFF; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
        get_hint_btn.clicked.connect(self.next_hint)

        h_box_lay.addWidget(self.hint_lbl, 1)
        h_box_lay.addWidget(get_hint_btn)
        s_lay.addWidget(hint_box)

        lay.addWidget(solver_card)

        scroll.setWidget(container)
        main_lay.addWidget(scroll)

        self.calculate_solution()

    def on_circuit_changed(self, idx):
        self.hint_step = 0
        if idx == 0:
            self.tree_text.setText("Signal peak needs to be cut off above a reference? ➔ YES ➔ Diode + Bias V_B ➔ Biased Clipper!")
        elif idx == 1:
            self.tree_text.setText("Need to add a DC voltage shift without changing peak-to-peak amplitude? ➔ Clamper Circuit!")
        else:
            self.tree_text.setText("Need continuous square wave pulse train output? ➔ 555 Timer Astable Multivibrator!")
        self.calculate_solution()

    def next_hint(self):
        self.hint_step = (self.hint_step + 1) % 3
        c_name = self.circuit_combo.currentText()
        hint = AnalogEngine.get_hints_for_topic(c_name, self.hint_step)
        self.hint_lbl.setText(hint)

    def calculate_solution(self):
        vin = self.sb_vin.value()
        p2 = self.sb_param2.value()
        p3 = self.sb_param3.value()

        idx = self.circuit_combo.currentIndex()
        if idx == 0: # Clipper
            vclip = p2 + p3
            txt = f"Clipper Solution:\n" \
                  f"Input Peak Vin = {vin} V\n" \
                  f"Bias Voltage Vb = {p2} V  |  Diode Barrier Vgamma = {p3} V\n" \
                  f"Clipping Threshold V_clip = Vb + Vgamma = {vclip:.2f} V\n" \
                  f"Clipped Output Peak = {vclip:.2f} V"
        elif idx == 1: # Clamper
            vdc = vin + p2
            txt = f"Clamper Solution:\n" \
                  f"Input Peak Vin = {vin} V  |  Bias Vb = {p2} V\n" \
                  f"DC Shift Voltage Vdc = Vin + Vb = {vdc:.2f} V\n" \
                  f"Clamped Output Max = {2*vin + p2:.2f} V  |  Output Min = {p2:.2f} V"
        else: # Multivibrator
            _, _, freq, duty = AnalogEngine.solve_multivibrator(r_a_k=p2, r_b_k=p3, c_uf=0.1)
            txt = f"555 Timer Astable Multivibrator Solution:\n" \
                  f"RA = {p2} kΩ  |  RB = {p3} kΩ  |  C = 0.1 μF\n" \
                  f"Oscillation Frequency f = {freq:.1f} Hz\n" \
                  f"Output Duty Cycle D = {duty:.1f} %"

        self.sol_output.setText(txt)
