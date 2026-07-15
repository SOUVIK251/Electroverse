from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSlider, QFrame, QWidget, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient, QFont
import numpy as np

from src.ui.components.base_simulation import BaseSimulation
from src.utils.formula_formatter import format_eng, format_num, PI

class ResonanceCircuitWidget(QWidget):
    """Paints RLC circuit loop, animated electron speeds, charges, and magnetic fields."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.current_ratio = 0.0
        self.cap_voltage_ratio = 0.0
        self.ind_current_ratio = 0.0
        self.electron_offset = 0.0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.animate)
        self.timer.start()

    def update_metrics(self, current_ratio: float, cap_voltage_ratio: float, ind_current_ratio: float):
        self.current_ratio = current_ratio
        self.cap_voltage_ratio = cap_voltage_ratio
        self.ind_current_ratio = ind_current_ratio

    def animate(self):
        # Animation speed proportional to current loop ratio
        self.electron_offset += self.current_ratio * 5.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # Loop wires
        painter.setPen(QPen(QColor("#475569"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(40, cy - 30, w - 80, 60)
        
        # 1. Resistor block (Left side)
        painter.setPen(QPen(QColor("#334155"), 1.5))
        painter.setBrush(QBrush(QColor("#1e293b")))
        r_rect = QRectF(40 - 8, cy - 15, 16, 30)
        painter.drawRect(r_rect)
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(int(40 - 25), int(cy - 20), "R")

        # 2. Inductor Coil (Top side center)
        ind_cx = cx - 50
        painter.setPen(QPen(QColor("#b45309"), 2.5))
        for i in range(4):
            painter.drawArc(ind_cx + i * 16, cy - 40, 16, 20, 0, 180 * 16)
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.drawText(ind_cx + 25, cy - 45, "L")

        # Inductor magnetic flux indicator
        abs_l_ratio = abs(self.ind_current_ratio)
        if abs_l_ratio > 0.05:
            painter.setPen(Qt.PenStyle.NoPen)
            field_grad = QRadialGradient(ind_cx + 32, cy - 30, 40)
            field_grad.setColorAt(0, QColor(245, 158, 11, int(150 * abs_l_ratio)))
            field_grad.setColorAt(1, QColor(245, 158, 11, 0))
            painter.setBrush(QBrush(field_grad))
            painter.drawEllipse(QPoint(ind_cx + 32, cy - 30), 45, 20)

        # 3. Capacitor Plates (Top side right)
        cap_cx = cx + 50
        painter.setPen(QPen(QColor("#64748b"), 3.5))
        painter.drawLine(cap_cx - 5, cy - 40, cap_cx - 5, cy - 20)
        painter.drawLine(cap_cx + 5, cy - 40, cap_cx + 5, cy - 20)
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.drawText(cap_cx - 4, cy - 45, "C")

        # Capacitor charge fills
        abs_c_ratio = abs(self.cap_voltage_ratio)
        if abs_c_ratio > 0.05:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#ef4444") if self.cap_voltage_ratio > 0 else QColor("#3b82f6")))
            painter.drawRect(cap_cx - 10, cy - 40, 4, int(20 * abs_c_ratio))
            painter.setBrush(QBrush(QColor("#3b82f6") if self.cap_voltage_ratio > 0 else QColor("#ef4444")))
            painter.drawRect(cap_cx + 6, cy - 40, 4, int(20 * abs_c_ratio))

        # 4. Animated Current Flowing Dots (Electrons)
        if self.current_ratio > 0.01:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#10b981")))
            loop_perimeter = 2 * (w - 80) + 120
            dots_count = 12
            for i in range(dots_count):
                pos = (self.electron_offset + i * (loop_perimeter / dots_count)) % loop_perimeter
                
                # Interpolate position around loop rect
                if pos < (w - 80): # Top wire
                    x = 40 + pos
                    y = cy - 30
                elif pos < (w - 80 + 60): # Right wire
                    x = w - 40
                    y = cy - 30 + (pos - (w - 80))
                elif pos < (2 * (w - 80) + 60): # Bottom wire
                    x = w - 40 - (pos - (w - 80 + 60))
                    y = cy + 30
                else: # Left wire
                    x = 40
                    y = cy + 30 - (pos - (2 * (w - 80) + 60))
                    
                painter.drawEllipse(QPoint(int(x), int(y)), 4, 4)

        # 5. Neon Glowing Resonance Lock Indicator Dial (Right Center)
        vm_cx, vm_cy = w - 80, cy
        vm_r = 30
        
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawEllipse(QPoint(vm_cx, vm_cy), vm_r, vm_r)
        
        # Glow based on resonance proximity
        prox = self.current_ratio
        glow_alpha = int(240 * prox)
        if prox > 0.02:
            radial_grad = QRadialGradient(vm_cx, vm_cy, vm_r)
            radial_grad.setColorAt(0, QColor(16, 185, 129, glow_alpha)) # Neon Green
            radial_grad.setColorAt(1, QColor(16, 185, 129, 0))
            painter.setBrush(QBrush(radial_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(vm_cx, vm_cy), vm_r + 5, vm_r + 5)
            
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.drawText(vm_cx - 24, vm_cy + 5, "RESONANCE")
        painter.drawText(vm_cx - 12, vm_cy + 15, "LOCK")


class ReactanceBarWidget(QWidget):
    """Paints side-by-side interactive comparison bar charts of XL and XC reactances."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(75)
        self.xl = 100.0
        self.xc = 100.0

    def update_reactances(self, xl: float, xc: float):
        self.xl = xl
        self.xc = xc
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        max_val = max(100.0, self.xl, self.xc)
        
        # Bar dimensions
        bar_w = 120
        bar_h = 14
        
        # XL Bar (Top) - Cyan
        painter.setPen(QPen(QColor("#334155"), 1.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRoundedRect(cx - 60, cy - 22, bar_w, bar_h, 3, 3)
        
        xl_fill_w = int(bar_w * (self.xl / max_val))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#06b6d4")))
        painter.drawRoundedRect(cx - 60, cy - 22, xl_fill_w, bar_h, 3, 3)
        
        # XC Bar (Bottom) - Magenta
        painter.setPen(QPen(QColor("#334155"), 1.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRoundedRect(cx - 60, cy + 5, bar_w, bar_h, 3, 3)
        
        xc_fill_w = int(bar_w * (self.xc / max_val))
        painter.setBrush(QBrush(QColor("#ec4899")))
        painter.drawRoundedRect(cx - 60, cy + 5, xc_fill_w, bar_h, 3, 3)
        
        # Text Labels
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(cx - 150, cy - 11, f"XL = {format_eng(self.xl, 'Ω')}")
        painter.drawText(cx - 150, cy + 16, f"XC = {format_eng(self.xc, 'Ω')}")
        
        # Comparative lock text
        if abs(self.xl - self.xc) < 0.05 * max_val:
            painter.setPen(QPen(QColor("#10b981"), 1.5))
            painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
            painter.drawText(cx + 80, cy + 5, "XL = XC (Resonance)")
        else:
            diff = self.xl - self.xc
            verdict = "Inductive (XL > XC)" if diff > 0 else "Capacitive (XC > XL)"
            painter.setPen(QPen(QColor("#94a3b8"), 1))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(cx + 80, cy + 5, verdict)


class ResonanceExplorerSimulation(BaseSimulation):
    """Educational Frequency Sweeper RLC Resonance visualization widget."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Resonance Frequency Explorer",
            formula_str=f"f0 = 1 / (2{PI} × √(L × C))   |   Ipeak = Vs / R",
            explanation_str=(
                "Resonance occurs when inductive and capacitive reactances cancel out. "
                "Use the interactive slider in the right panel to scan source frequencies, "
                "observing electron speed loops, reactive element metrics, and energy shifts."
            ),
            parent=parent
        )
        
        # Hide default Matplotlib canvas & clock controls
        self.plot_canvas.hide()
        # Hide standard clock control panel (static tool) by scanning layouts
        for i in range(self.right_layout.count()):
            item = self.right_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QFrame):
                if hasattr(self, 'play_btn') and self.play_btn.parentWidget() == widget:
                    widget.hide()
            
        # Initialize custom widgets layout inside right pane
        self.setup_explorer_view()

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
        self.r_input = QLineEdit("15.0")
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

        # Instantly recalculate on input changes
        self.vs_input.textChanged.connect(self.calculate_explorer_state)
        self.vs_unit.currentIndexChanged.connect(self.calculate_explorer_state)
        self.r_input.textChanged.connect(self.calculate_explorer_state)
        self.r_unit.currentIndexChanged.connect(self.calculate_explorer_state)
        self.l_input.textChanged.connect(self.calculate_explorer_state)
        self.l_unit.currentIndexChanged.connect(self.calculate_explorer_state)
        self.c_input.textChanged.connect(self.calculate_explorer_state)
        self.c_unit.currentIndexChanged.connect(self.calculate_explorer_state)

    def setup_visualizer(self, layout: QVBoxLayout):
        # Place a dummy label, we override visualizer layout entirely on the right
        layout.addWidget(QLabel("RLC Resonance Parameters Scan"))

    def setup_explorer_view(self):
        """Constructs right-panel interactive dials, energy stats, and scan slider."""
        
        # 1. Circuit Animation
        self.circuit_view = ResonanceCircuitWidget(self)
        self.right_layout.addWidget(self.circuit_view)
        
        # 2. Reactance Bar Comparator
        self.reactance_view = ReactanceBarWidget(self)
        self.right_layout.addWidget(self.reactance_view)
        
        # 3. Frequency Sweep Slider
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.Shape.StyledPanel)
        slider_layout = QHBoxLayout(slider_frame)
        
        slider_layout.addWidget(QLabel("AC Freq Sweep:"))
        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setRange(10, 200) # 0.1x to 2.0x of f0
        self.freq_slider.setValue(100) # 1.0x f0 (resonance)
        self.freq_slider.valueChanged.connect(self.calculate_explorer_state)
        slider_layout.addWidget(self.freq_slider)
        
        self.freq_val_lbl = QLabel("1.00 kHz")
        self.freq_val_lbl.setStyleSheet("font-family: Consolas; font-weight: bold; color: #10b981;")
        slider_layout.addWidget(self.freq_val_lbl)
        self.right_layout.addWidget(slider_frame)

        # 4. Energy Stats Indicators Grid
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        stats_layout.setSpacing(10)
        
        stats_layout.addWidget(QLabel("Capacitor Energy:"), 0, 0)
        self.energy_c_lbl = QLabel("0.00 μJ")
        self.energy_c_lbl.setStyleSheet("font-weight: bold; color: #ec4899;")
        stats_layout.addWidget(self.energy_c_lbl, 0, 1)
        
        stats_layout.addWidget(QLabel("Inductor Energy:"), 0, 2)
        self.energy_l_lbl = QLabel("0.00 μJ")
        self.energy_l_lbl.setStyleSheet("font-weight: bold; color: #06b6d4;")
        stats_layout.addWidget(self.energy_l_lbl, 0, 3)
        
        stats_layout.addWidget(QLabel("Quality Factor (Q):"), 1, 0)
        self.q_lbl = QLabel("1.00")
        self.q_lbl.setStyleSheet("font-weight: bold; color: #f59e0b;")
        stats_layout.addWidget(self.q_lbl, 1, 1)
        
        stats_layout.addWidget(QLabel("Bandwidth (BW):"), 1, 2)
        self.bw_lbl = QLabel("100 Hz")
        self.bw_lbl.setStyleSheet("font-weight: bold; color: #a855f7;")
        stats_layout.addWidget(self.bw_lbl, 1, 3)
        
        self.right_layout.addWidget(stats_frame)

        # 5. Live Explanation Panel (Text block)
        self.explanation_card = QFrame()
        self.explanation_card.setStyleSheet("background-color: rgba(30, 41, 59, 0.3); border-radius: 6px; padding: 6px;")
        exp_layout = QVBoxLayout(self.explanation_card)
        self.exp_title = QLabel("Circuit State: Tuning...")
        self.exp_title.setStyleSheet("font-weight: bold; color: #f8fafc;")
        self.exp_text = QLabel("Adjust the frequency sweep slider to explore resonance.")
        self.exp_text.setWordWrap(True)
        self.exp_text.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        exp_layout.addWidget(self.exp_title)
        exp_layout.addWidget(self.exp_text)
        self.right_layout.addWidget(self.explanation_card)
        
        # Run first calculation
        self.calculate_explorer_state()

    def init_simulation(self):
        # Overridden to prevent canvas title setup crashes since plot is hidden
        pass

    def calculate_explorer_state(self):
        try:
            vs = float(self.vs_input.text())
            r = float(self.r_input.text())
            l = float(self.l_input.text())
            c = float(self.c_input.text())
            if vs <= 0 or r <= 0 or l <= 0 or c <= 0:
                raise ValueError()
        except ValueError:
            return

        vs_mult = {"V": 1.0, "mV": 1e-3}[self.vs_unit.currentText()]
        r_mult = {"Ω": 1.0, "kΩ": 1e3}[self.r_unit.currentText()]
        l_mult = {"mH": 1e-3, "μH": 1e-6}[self.l_unit.currentText()]
        c_mult = {"nF": 1e-9, "μF": 1e-6}[self.c_unit.currentText()]

        base_vs = vs * vs_mult
        base_r = r * r_mult
        base_l = l * l_mult
        base_c = c * c_mult

        # Core resonance parameters
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
        q = (1.0 / base_r) * np.sqrt(base_l / base_c)
        bw = f0 / q

        # Read sweep frequency from slider value (mapped around f0)
        swept_ratio = self.freq_slider.value() / 100.0
        f_swept = swept_ratio * f0
        
        self.freq_val_lbl.setText(f"{format_eng(f_swept, 'Hz')} ({swept_ratio:.2f} × f0)")

        # Math calculations at swept frequency
        omega = 2.0 * np.pi * f_swept
        xl = omega * base_l
        xc = 1.0 / (omega * base_c) if omega > 0 else 1e9
        z = np.sqrt(base_r**2 + (xl - xc)**2)
        i_val = base_vs / z
        
        vc = i_val * xc
        
        # Stored energy:
        # Cap: E = 0.5 * C * Vc^2
        energy_c = 0.5 * base_c * (vc ** 2)
        # Ind: E = 0.5 * L * I^2
        energy_l = 0.5 * base_l * (i_val ** 2)

        # Update text indicators
        self.energy_c_lbl.setText(format_eng(energy_c, "J"))
        self.energy_l_lbl.setText(format_eng(energy_l, "J"))
        self.q_lbl.setText(f"{q:.2f}")
        self.bw_lbl.setText(format_eng(bw, "Hz"))

        # Update animations
        max_i = base_vs / base_r
        current_ratio = i_val / max_i if max_i > 0 else 0.0
        self.circuit_view.update_metrics(
            current_ratio=current_ratio,
            cap_voltage_ratio=vc / base_vs if base_vs > 0 else 0.0,
            ind_current_ratio=i_val / max_i if max_i > 0 else 0.0
        )
        self.reactance_view.update_reactances(xl, xc)

        # Update Live Explanation panel text
        diff_percent = abs(swept_ratio - 1.0)
        if diff_percent < 0.03: # Within 3% of resonance
            self.exp_title.setText("Circuit State: AT RESONANCE (Balanced)")
            self.exp_text.setText(
                "At exactly resonance, inductive and capacitive reactances cancel out (XL = XC). "
                "The circuit impedance is at its minimum (Z = R) and current is maximum. "
                "Energy transfer between L and C is highly efficient."
            )
            self.exp_title.setStyleSheet("font-weight: bold; color: #10b981;") # Green
        elif swept_ratio < 1.0:
            self.exp_title.setText("Circuit State: BELOW RESONANCE (Capacitive)")
            self.exp_text.setText(
                f"Below resonance, capacitive reactance dominates (XC > XL). "
                f"The circuit is highly capacitive, current leads the source voltage, "
                f"and most of the energy is stored inside the electric field of the capacitor."
            )
            self.exp_title.setStyleSheet("font-weight: bold; color: #ec4899;") # Magenta/Pink
        else:
            self.exp_title.setText("Circuit State: ABOVE RESONANCE (Inductive)")
            self.exp_text.setText(
                f"Above resonance, inductive reactance dominates (XL > XC). "
                f"The circuit is highly inductive, current lags the source voltage, "
                f"and most of the energy is stored inside the magnetic field of the inductor."
            )
            self.exp_title.setStyleSheet("font-weight: bold; color: #06b6d4;") # Cyan

        self.answer_label.setText(f"Z: {format_eng(z, 'Ω')}  |  I: {format_eng(i_val, 'A')}")
        self.steps_text.setText(
            f"**RLC Scan Statistics**:\n\n"
            f"- **Natural Resonant Freq (f0)**: {format_eng(f0, 'Hz')}\n"
            f"- **Quality Factor (Q)**: {q:.2f}\n"
            f"- **Impedance (Z)**: {format_eng(z, 'Ω')}\n"
            f"- **Reactance Difference (XL - XC)**: {format_eng(xl - xc, 'Ω')}\n"
            f"- **Capacitor Energy**: {format_eng(energy_c, 'J')}\n"
            f"- **Inductor Energy**: {format_eng(energy_l, 'J')}"
        )

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
            base_vs, base_r, base_l, base_c = 5.0, 15.0, 0.01, 10e-6
            
        f0 = 1.0 / (2.0 * np.pi * np.sqrt(base_l * base_c))
        swept_ratio = self.freq_slider.value() / 100.0
        f = swept_ratio * f0
        
        ch1 = base_vs * np.sin(2.0 * np.pi * f * time_axis)
        
        omega = 2.0 * np.pi * f
        xl = omega * base_l
        xc = 1.0 / (omega * base_c) if omega > 0 else 1e9
        z = np.sqrt(base_r**2 + (xl - xc)**2)
        i_peak = base_vs / z
        theta = np.arctan2(xl - xc, base_r)
        ch2 = i_peak * base_r * np.sin(2.0 * np.pi * f * time_axis - theta)
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
