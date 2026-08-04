from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QScrollArea, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.ui.components.engineering_spinbox import EngineeringDoubleSpinBox



class AnalogReferenceView(QWidget):
    """Formula Explorer, Engineering Calculators & Reference Lookup Suite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(8, 8, 8, 8)

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
        self.srch_box.setPlaceholderText("Search analog formulas (e.g., 'Clipper', 'Clamper', 'Ripple', 'Cutoff')...")
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
            ("Biased Clipper Threshold", "V_clip = V_B + V_gamma", "Vclip (Volts), VB (Volts), Vgamma = 0.7V", "Determines clipping level for biased positive/negative diode clippers."),
            ("Clamper DC Shift", "V_dc = V_m - V_B", "Vdc (Volts), Vm (Peak AC Volts)", "Calculates DC offset shift added by clamping capacitor."),
            ("Rectifier Ripple Factor", "gamma = 1 / (4 * sqrt(3) * f * R_L * C)", "gamma (unitless), f (Hz), RL (Ohms), C (Farads)", "Quantifies AC ripple ratio in filtered DC output."),
            ("RC Filter Cutoff Frequency", "f_c = 1 / (2 * pi * R * C)", "fc (Hertz), R (Ohms), C (Farads)", "-3dB frequency boundary for Low Pass and High Pass RC filters."),
            ("Astable Multivibrator Frequency", "f = 1.44 / ((R_A + 2 * R_B) * C)", "f (Hertz), RA, RB (Ohms), C (Farads)", "Oscillation frequency for 555 timer square wave generator.")
        ]

        self.render_formulas(self.formulas_data)
        scroll.setWidget(self.form_container)
        exp_lay.addWidget(scroll)

        tabs.addTab(exp_widget, "🔍 Formula Explorer & Cheat Sheets")

        # Tab 2: Calculators
        calc_widget = QWidget()
        c_lay = QVBoxLayout(calc_widget)

        c_hdr = QLabel("⚙️ Interactive Analog Calculators Suite")
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
            "1. Clipper Threshold Calculator",
            "2. Clamper DC Shift Calculator",
            "3. Filter Cutoff Frequency Calculator"
        ])
        self.calc_combo.setStyleSheet("background-color: #1E293B; border: 1px solid #26334D; color: #FFF; padding: 6px;")
        self.calc_combo.currentIndexChanged.connect(self.run_calculator)
        c_row.addWidget(self.calc_combo)
        c_row.addStretch()
        cb_lay.addLayout(c_row)

        c_in_row = QHBoxLayout()
        # Interactive Inputs
        self.lbl_p1 = QLabel("Parameter 1 (Vin / V1):", styleSheet="color: #94A3B8;")
        self.c_p1 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.1, max_val=1000.0)
        self.c_p1.setValue(10.0)
        self.c_p1.valueChanged.connect(self.run_calculator)
        c_in_row.addWidget(self.lbl_p1)
        c_in_row.addWidget(self.c_p1)

        self.lbl_p2 = QLabel("Parameter 2 (R / Resistance):", styleSheet="color: #94A3B8;")
        self.c_p2 = EngineeringDoubleSpinBox(self, step=0.1, min_val=0.01, max_val=100000.0)
        self.c_p2.setValue(1000.0)
        self.c_p2.valueChanged.connect(self.run_calculator)
        c_in_row.addWidget(self.lbl_p2)
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

        if idx == 0: # Clipper Threshold (VB=p1, Vgamma=0.7)
            vclip = p1 + 0.7
            self.c_out_lbl.setText(f"Clipper Threshold:\nV_clip = V_B + V_gamma = {p1}V + 0.7V = {vclip:.2f} Volts")
        elif idx == 1: # Clamper DC Shift (Vm=p1, VB=p2)
            vdc = p1 + p2
            self.c_out_lbl.setText(f"Clamper DC Level Shift:\nV_dc = V_m + V_B = {p1}V + {p2}V = {vdc:.2f} Volts")
        else: # Filter Cutoff (R=p1 kΩ, C=p2 μF)
            import math
            fc = 1.0 / (2 * math.pi * (p1 * 1e3) * (p2 * 1e-6))
            self.c_out_lbl.setText(f"Filter Cutoff Frequency (R={p1}kΩ, C={p2}μF):\nfc = 1 / (2πRC) = {fc:.2f} Hertz")
