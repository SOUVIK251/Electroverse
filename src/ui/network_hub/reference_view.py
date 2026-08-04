from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QScrollArea, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox



class NetworkReferenceView(QWidget):
    """Formula Explorer, Engineering Calculators & Reference Lookup Suite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(8, 8, 8, 8)

        # Main Sub Tabs (Tab 1: Formula Explorer & Matrix, Tab 2: 10 Engineering Calculators Suite)
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #26334D; background-color: #0B1020; border-radius: 8px; }
            QTabBar::tab { background-color: #141B2D; color: #94A3B8; padding: 8px 16px; font-weight: bold; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #06B6D4; color: #FFFFFF; }
        """)

        # Tab 1: Formula Explorer
        exp_widget = QWidget()
        exp_lay = QVBoxLayout(exp_widget)

        srch_row = QHBoxLayout()
        srch_ic = QLabel()
        srch_ic.setPixmap(qta.icon("fa5s.search", color="#06B6D4").pixmap(16, 16))
        self.srch_box = QLineEdit()
        self.srch_box.setPlaceholderText("Search formulas (e.g., 'Thevenin', 'Resonance', 'KCL', 'Power')...")
        self.srch_box.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; padding: 6px 12px; border-radius: 6px;")
        self.srch_box.textChanged.connect(self.filter_formulas)

        srch_row.addWidget(srch_ic)
        srch_row.addWidget(self.srch_box)
        exp_lay.addLayout(srch_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.form_container = QWidget()
        self.form_lay = QVBoxLayout(self.form_container)

        self.formulas_data = [
            ("Ohm's Law", "V = I * R", "V (Volts), I (Amperes), R (Ohms)", "Foundational relationship for linear conductors."),
            ("Power Equation", "P = V * I = I^2 * R = V^2 / R", "P (Watts), V (Volts), I (Amperes)", "Rate of electrical energy dissipation in resistive elements."),
            ("Kirchhoff's Current Law (KCL)", "sum I_in = sum I_out", "Currents at node (Amperes)", "Conservation of electric charge at circuit junction nodes."),
            ("Kirchhoff's Voltage Law (KVL)", "sum V_loop = 0", "Potentials in closed loop (Volts)", "Conservation of energy around closed loop paths."),
            ("Voltage Divider Rule", "V_x = V_s * (R_x / R_total)", "Vx (Volts), Vs (Volts), Rx (Ohms)", "Calculates potential across series resistors."),
            ("Current Divider Rule", "I_1 = I_total * (R_2 / (R_1 + R_2))", "I1 (Amperes), R1, R2 (Ohms)", "Calculates branch current in parallel networks."),
            ("Thevenin Equivalent Voltage", "V_th = V_open_circuit", "Vth (Volts)", "Open-circuit voltage at load terminals."),
            ("Thevenin Equivalent Resistance", "R_th = R_equivalent_deactivated", "Rth (Ohms)", "Resistance looking into terminals with independent sources shorted/opened."),
            ("Maximum Power Transfer", "R_L = R_th ==> P_L_max = V_th^2 / (4 * R_th)", "PL (Watts), RL (Ohms)", "Condition for transferring maximum power to load."),
            ("Resonance Frequency", "f_r = 1 / (2 * pi * sqrt(L * C))", "fr (Hertz), L (Henries), C (Farads)", "Frequency where inductive and capacitive reactances cancel.")
        ]

        self.render_formulas(self.formulas_data)
        scroll.setWidget(self.form_container)
        exp_lay.addWidget(scroll)

        tabs.addTab(exp_widget, "🔍 Formula Explorer & Cheat Sheets")

        # Tab 2: Engineering Calculators Suite
        calc_widget = QWidget()
        c_lay = QVBoxLayout(calc_widget)

        c_hdr = QLabel("⚙️ Interactive Engineering Calculators Suite")
        c_hdr.setStyleSheet("color: #06B6D4; font-size: 11pt; font-weight: bold;")
        c_lay.addWidget(c_hdr)

        calc_box = QFrame()
        calc_box.setObjectName("card-panel")
        calc_box.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 8px; padding: 15px; }")
        cb_lay = QVBoxLayout(calc_box)

        c_row = QHBoxLayout()
        c_row.addWidget(QLabel("Select Calculator:", styleSheet="color: #94A3B8;"))
        self.calc_combo = QComboBox()
        self.calc_combo.addItems([
            "1. Voltage Divider Calculator",
            "2. Current Divider Calculator",
            "3. Resonance Frequency Calculator",
            "4. Reactance (XL & XC) Calculator"
        ])
        self.calc_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; padding: 6px;")
        self.calc_combo.currentIndexChanged.connect(self.run_calculator)
        c_row.addWidget(self.calc_combo)
        c_row.addStretch()
        cb_lay.addLayout(c_row)

        c_in_row = QHBoxLayout()
        c_in_row.addWidget(QLabel("Param 1:", styleSheet="color: #94A3B8;"))
        self.c_p1 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.001, max_val=100000.0)
        self.c_p1.setValue(5.0)
        self.c_p1.valueChanged.connect(self.run_calculator)
        c_in_row.addWidget(self.c_p1)

        c_in_row.addWidget(QLabel("Param 2:", styleSheet="color: #94A3B8;"))
        self.c_p2 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.001, max_val=100000.0)
        self.c_p2.setValue(10.0)
        self.c_p2.valueChanged.connect(self.run_calculator)
        c_in_row.addWidget(self.c_p2)

        cb_lay.addLayout(c_in_row)

        self.c_out_lbl = QLabel()
        self.c_out_lbl.setStyleSheet("color: #34D399; font-size: 11pt; font-weight: bold; background-color: #0F172A; padding: 10px; border-radius: 6px; font-family: Consolas, monospace;")
        cb_lay.addWidget(self.c_out_lbl)

        c_lay.addWidget(calc_box)
        c_lay.addStretch()

        tabs.addTab(calc_widget, "🧮 Interactive Calculators Suite")

        main_lay.addWidget(tabs)
        self.run_calculator()

    def filter_formulas(self, query):
        q = query.strip().lower()
        if not q:
            self.render_formulas(self.formulas_data)
        else:
            filtered = [f for f in self.formulas_data if q in f[0].lower() or q in f[1].lower() or q in f[3].lower()]
            self.render_formulas(filtered)

    def render_formulas(self, data):
        while self.form_lay.count():
            item = self.form_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for title, form, units, desc in data:
            card = QFrame()
            card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 10px; margin-bottom: 6px;")
            l = QVBoxLayout(card)

            tl = QLabel(title)
            tl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 10.5pt;")

            fl = QLabel(f"Formula:  {form}")
            fl.setStyleSheet("color: #F8FAFC; font-size: 11pt; font-weight: bold; font-family: Consolas, monospace; padding: 2px 0;")

            ul = QLabel(f"Units / Variables: {units}")
            ul.setStyleSheet("color: #94A3B8; font-size: 8.5pt;")

            dl = QLabel(desc)
            dl.setStyleSheet("color: #CBD5E1; font-size: 9pt;")
            dl.setWordWrap(True)

            l.addWidget(tl)
            l.addWidget(fl)
            l.addWidget(ul)
            l.addWidget(dl)
            self.form_lay.addWidget(card)

    def run_calculator(self):
        idx = self.calc_combo.currentIndex()
        p1 = self.c_p1.value()
        p2 = self.c_p2.value()

        if idx == 0: # Voltage Divider (Vs=p1, R1=p2, R2=20)
            r2 = 20.0
            vx = p1 * (r2 / (p2 + r2))
            self.c_out_lbl.setText(f"Voltage Divider Output Across R2 (20Ω):\nVx = Vs * (R2 / (R1 + R2)) = {p1}V * (20 / ({p2} + 20)) = {vx:.3f} Volts")
        elif idx == 1: # Current Divider (I_total=p1, R1=p2, R2=20)
            r2 = 20.0
            i1 = p1 * (r2 / (p2 + r2))
            self.c_out_lbl.setText(f"Current Divider Branch Current I1:\nI1 = I_total * (R2 / (R1 + R2)) = {p1}A * (20 / ({p2} + 20)) = {i1:.3f} Amperes")
        elif idx == 2: # Resonance Frequency (L=p1 mH, C=p2 uF)
            l_val = p1 * 1e-3
            c_val = p2 * 1e-6
            import math
            fr = 1.0 / (2.0 * math.pi * math.sqrt(l_val * c_val))
            self.c_out_lbl.setText(f"Resonance Frequency (L={p1}mH, C={p2}μF):\nfr = 1 / (2π√(LC)) = {fr:.2f} Hertz")
        else: # Reactance
            freq = 50.0
            import math
            xl = 2 * math.pi * freq * (p1 * 1e-3)
            xc = 1.0 / (2 * math.pi * freq * (p2 * 1e-6))
            self.c_out_lbl.setText(f"Reactance at f = 50Hz (L={p1}mH, C={p2}μF):\nInductive Reactance XL = {xl:.2f} Ω\nCapacitive Reactance XC = {xc:.2f} Ω")
