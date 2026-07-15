from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient, QFont
import numpy as np

class CapacitorVisualizer(QWidget):
    """Paints a physical capacitor with animated charge buildup, field lines, and τ gauges."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.voltage_ratio = 0.0  # -1.0 to 1.0
        self.charge_mode = "charging"
        self.tau_ratio = 0.0  # time / tau factor

    def set_voltage_ratio(self, ratio: float, mode: str = "charging", tau_ratio: float = 0.0):
        self.voltage_ratio = max(-1.0, min(1.0, ratio))
        self.charge_mode = mode
        self.tau_ratio = tau_ratio
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)")) # Premium Slate-950
        
        # 2. Wire terminals
        painter.setPen(QPen(QColor("#475569"), 3))
        painter.drawLine(10, cy, cx - 40, cy)
        painter.drawLine(cx + 40, cy, w - 10, cy)
        
        # 3. Capacitor Plates
        plate_w, plate_h = 12, 70
        left_rect = QRectF(cx - 40, cy - plate_h // 2, plate_w, plate_h)
        right_rect = QRectF(cx + 28, cy - plate_h // 2, plate_w, plate_h)
        
        painter.setPen(Qt.PenStyle.NoPen)
        # Metal plate colors
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.drawRect(left_rect)
        painter.drawRect(right_rect)
        
        v = self.voltage_ratio
        abs_v = abs(v)
        
        # 4. Fill metal plates with charge color
        if abs_v > 0.01:
            left_color = QColor("#ef4444") if v > 0 else QColor("#3b82f6") # Red (+) or Blue (-)
            right_color = QColor("#3b82f6") if v > 0 else QColor("#ef4444")
            
            painter.setBrush(QBrush(left_color))
            painter.drawRect(left_rect.x(), left_rect.y(), plate_w, plate_h * abs_v)
            
            painter.setBrush(QBrush(right_color))
            painter.drawRect(right_rect.x(), right_rect.y(), plate_w, plate_h * abs_v)
            
            # Dielectric electric field glow
            field_grad = QLinearGradient(cx - 28, cy, cx + 28, cy)
            field_grad.setColorAt(0, left_color)
            field_grad.setColorAt(1, right_color)
            
            painter.setBrush(QBrush(field_grad))
            painter.setOpacity(0.3 * abs_v)
            painter.drawRect(cx - 28, cy - plate_h // 2, 56, plate_h)
            painter.setOpacity(1.0)
            
            # Draw moving electric field arrow lines
            painter.setPen(QPen(QColor("#f8fafc"), 1.0, Qt.PenStyle.DashLine))
            field_lines = 4
            for i in range(field_lines):
                ly = cy - 20 + i * 13
                if v > 0:
                    painter.drawLine(cx - 25, ly, cx + 23, ly)
                else:
                    painter.drawLine(cx + 23, ly, cx - 25, ly)

        # 5. Status Lights (τ and 5τ indicators)
        t_factor = self.tau_ratio
        tau_active = t_factor >= 1.0
        tau5_active = t_factor >= 5.0
        
        # Draw indicator background
        ind_y = cy - 40
        painter.setPen(QPen(QColor("#1e293b"), 1.5))
        
        # τ LED
        painter.setBrush(QBrush(QColor("#10b981") if tau_active else QColor("#334155")))
        painter.drawEllipse(15, ind_y, 10, 10)
        
        # 5τ LED
        painter.setBrush(QBrush(QColor("#10b981") if tau5_active else QColor("#334155")))
        painter.drawEllipse(15, ind_y + 20, 10, 10)
        
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(30, ind_y + 9, "τ Status (~63%)")
        painter.drawText(30, ind_y + 29, "5τ Status (~99%)")
        
        # 6. Voltage Gauge / Digital Display
        painter.setPen(QPen(QColor("#06b6d4"), 1.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        gauge_rect = QRectF(w - 140, cy - 35, 120, 55)
        painter.drawRoundedRect(gauge_rect, 6, 6)
        
        painter.setPen(QPen(QColor("#06b6d4"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(int(w - 130), int(cy - 20), "VOLTAGE READOUT")
        
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.drawText(int(w - 130), int(cy + 10), f"{v * 10.0:.2f} V")
        
        # Info Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, f"CAPACITOR TRANSIENT (State: {self.charge_mode.upper()})")


class InductorVisualizer(QWidget):
    """Paints a copper wire inductor with animating magnetic field flux lines, storage metrics, and current indicators."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.current_ratio = 0.0  # -1.0 to 1.0
        self.stored_energy = 0.0  # Joules
        self.electron_offset = 0.0
        
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.animate)
        self.timer.start()

    def set_inductor_metrics(self, ratio: float, energy: float):
        self.current_ratio = max(-1.0, min(1.0, ratio))
        self.stored_energy = energy

    def animate(self):
        self.electron_offset += self.current_ratio * 4.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # 2. Magnetic Flux Field Lines (translucent glowing ellipses around the coil)
        abs_c = abs(self.current_ratio)
        if abs_c > 0.01:
            painter.setPen(Qt.PenStyle.NoPen)
            # Create a radial gradient at the center of the coil
            field_gradient = QRadialGradient(cx, cy, 140)
            field_gradient.setColorAt(0, QColor(245, 158, 11, int(120 * abs_c))) # Glowing Amber
            field_gradient.setColorAt(0.6, QColor(245, 158, 11, int(30 * abs_c)))
            field_gradient.setColorAt(1, QColor(245, 158, 11, 0))
            
            painter.setBrush(QBrush(field_gradient))
            # Draw magnetic field bubbles
            painter.drawEllipse(QPoint(cx, cy), 130, 45)
            
            # Flux loop line contours
            painter.setPen(QPen(QColor(245, 158, 11, int(150 * abs_c)), 1.2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPoint(cx, cy), 110, 32)
            painter.drawEllipse(QPoint(cx, cy), 85, 20)

        # 3. Connection wires
        painter.setPen(QPen(QColor("#475569"), 3))
        painter.drawLine(10, cy, cx - 90, cy)
        painter.drawLine(cx + 90, cy, w - 10, cy)
        
        # 4. Inductor Coil Loop turns
        num_turns = 5
        turn_w = 34
        start_x = cx - (num_turns * turn_w) // 2
        
        # Draw background coil arcs
        painter.setPen(QPen(QColor("#b45309"), 3.5)) # Copper dark
        for i in range(num_turns):
            x = start_x + i * turn_w
            painter.drawArc(x, cy - 25, turn_w, 50, 0, 180 * 16)
            
        # Draw foreground coil arcs
        painter.setPen(QPen(QColor("#f59e0b"), 4.0)) # Copper bright
        for i in range(num_turns):
            x = start_x + i * turn_w
            painter.drawArc(x, cy - 25, turn_w, 50, 180 * 16, 180 * 16)

        # 5. Animating Current flowing dots (electrons)
        if abs_c > 0.02:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#10b981")))
            dots_count = 10
            for i in range(dots_count):
                pos = (self.electron_offset + i * (200 / dots_count)) % 200
                rel_pos = pos / 200.0  # 0 to 1
                
                # Coil coordinates interpolation
                coil_x = (cx - 90) + rel_pos * 180
                theta = rel_pos * num_turns * 2.0 * np.pi
                coil_y = cy + 23 * np.sin(theta)
                
                dot_color = QColor("#10b981") if np.cos(theta) > 0 else QColor("#047857")
                painter.setBrush(QBrush(dot_color))
                painter.drawEllipse(QPoint(int(coil_x), int(coil_y)), 4, 4)

        # 6. Metrics display box (Stored energy & Current)
        painter.setPen(QPen(QColor("#f59e0b"), 1.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        stats_rect = QRectF(w - 150, cy - 35, 130, 60)
        painter.drawRoundedRect(stats_rect, 6, 6)
        
        painter.setPen(QPen(QColor("#f59e0b"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(int(w - 140), int(cy - 20), "ENERGY STORED")
        
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        # E = 0.5 * L * I^2
        painter.drawText(int(w - 140), int(cy + 2), f"{self.stored_energy * 1e6:.2f} μJ")
        
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Normal))
        painter.drawText(int(w - 140), int(cy + 16), f"I: {self.current_ratio * 1000:.1f} mA")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, "INDUCTOR TRANSIENT RESPONSE (MAGNETIC FIELD DYNAMICS)")


class ResistorNetworkVisualizer(QWidget):
    """Paints a static DC Resistor Divider network diagram with live labels and level meters."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.vin = 10.0
        self.r1 = 1000.0
        self.r2 = 1000.0

    def set_values(self, vin: float, r1: float, r2: float):
        self.vin = vin
        self.r1 = r1
        self.r2 = r2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2 - 40, h // 2
        
        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # 2. Resistor Divider schematic lines
        painter.setPen(QPen(QColor("#64748b"), 2))
        
        # Vin line to R1
        painter.drawLine(cx - 60, cy - 30, cx, cy - 30)
        painter.drawLine(cx, cy - 30, cx, cy - 20)
        
        # R1 body (Box)
        painter.setBrush(QBrush(QColor("#1e293b")))
        r1_rect = QRectF(cx - 12, cy - 20, 24, 18)
        painter.drawRect(r1_rect)
        
        # R1 to R2 joint line
        painter.drawLine(cx, cy - 2, cx, cy + 10)
        # Vout tap off line
        painter.drawLine(cx, cy + 5, cx + 50, cy + 5)
        painter.drawLine(cx + 50, cy + 5, cx + 50, cy + 20)
        
        # R2 body (Box)
        r2_rect = QRectF(cx - 12, cy + 10, 24, 18)
        painter.drawRect(r2_rect)
        
        # R2 to Ground line
        painter.drawLine(cx, cy + 28, cx, cy + 40)
        # Ground symbol
        painter.drawLine(cx - 10, cy + 40, cx + 10, cy + 40)
        painter.drawLine(cx - 6, cy + 43, cx + 6, cy + 43)
        painter.drawLine(cx - 2, cy + 46, cx + 2, cy + 46)

        # 3. Text labels on schematic
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(int(cx - 80), int(cy - 36), f"Vin: {self.vin:.1f}V")
        
        # Resistors labels
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.drawText(int(cx + 18), int(cy - 10), f"R1: {self.r1:.0f}Ω")
        painter.drawText(int(cx + 18), int(cy + 22), f"R2: {self.r2:.0f}Ω")
        
        # Output Vout
        v_out = self.vin * self.r2 / (self.r1 + self.r2)
        v_drop_r1 = self.vin - v_out
        painter.setPen(QPen(QColor("#10b981"), 1))
        painter.drawText(int(cx + 62), int(cy + 30), f"Vout: {v_out:.2f}V")
        
        # 4. Voltage Level Meter Bar (Right Side)
        meter_x = w - 100
        meter_y = cy - 30
        meter_w = 24
        meter_h = 65
        
        # Frame
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRect(meter_x, meter_y, meter_w, meter_h)
        
        # Level color fill (Gradient)
        lvl_grad = QLinearGradient(meter_x, meter_y, meter_x, meter_y + meter_h)
        lvl_grad.setColorAt(0, QColor("#10b981"))
        lvl_grad.setColorAt(1, QColor("#06b6d4"))
        
        ratio = v_out / self.vin if self.vin > 0 else 0
        fill_h = int(meter_h * ratio)
        painter.fillRect(meter_x + 2, meter_y + meter_h - fill_h, meter_w - 3, fill_h, QBrush(lvl_grad))
        
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(meter_x - 12, meter_y - 8, "Vout Level")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, "DC RESISTOR NETWORK RATIO ANALYZER")


class RectifierCurrentVisualizer(QWidget):
    """Paints schematic diodes with animating current paths depending on AC cycles."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.vin = 0.0
        self.rect_type = "half"
        self.arrow_offset = 0.0
        
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.animate)
        self.timer.start()

    def set_ac_voltage(self, val: float, rect_type: str = "half"):
        self.vin = val
        self.rect_type = rect_type

    def animate(self):
        # Current speed is proportional to magnitude of input voltage (active conduction)
        if self.rect_type == "half":
            speed = max(0.0, self.vin) * 2.0
        else:
            speed = abs(self.vin) * 2.0
        self.arrow_offset = (self.arrow_offset + speed) % 100
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        v_in = self.vin
        is_pos = v_in > 0.05
        is_neg = v_in < -0.05
        
        if self.rect_type == "half":
            # --- Half-Wave Diode conduction layout ---
            diode_color = QColor("#10b981") if is_pos else QColor("#ef4444")
            
            # Wires loops
            painter.setPen(QPen(QColor("#475569"), 2))
            painter.drawRect(50, cy - 25, w - 100, 50)
            
            # Diode Triangle block
            painter.setPen(QPen(QColor("#334155"), 1.5))
            painter.setBrush(QBrush(diode_color))
            diode_pts = [QPoint(cx - 15, cy - 15 - 25), QPoint(cx - 15, cy + 15 - 25), QPoint(cx + 15, cy - 25)]
            painter.drawPolygon(diode_pts)
            # Plate bar
            painter.setPen(QPen(diode_color, 3.5))
            painter.drawLine(cx + 15, cy - 15 - 25, cx + 15, cy + 15 - 25)
            
            # Current arrows moving during positive half cycles
            if is_pos:
                painter.setPen(QPen(QColor("#10b981"), 2))
                painter.setBrush(QBrush(QColor("#10b981")))
                # Draw 4 moving arrows clockwise
                for i in range(4):
                    pos = (self.arrow_offset * 4 + i * (w - 100) / 4) % (w - 100)
                    painter.drawEllipse(int(50 + pos), cy - 25, 5, 5)
            
            # Status Indicator
            status = "CONDUCTING (FORWARD)" if is_pos else "BLOCKING (REVERSE)"
            painter.setPen(QPen(QColor("#94a3b8"), 1))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(w - 200, 45, f"Diode Bias: {status}")
            
        else:
            # --- Full-Wave Bridge conduction layout ---
            # Draw bridge diamond layout
            d1_color = QColor("#10b981") if is_pos else QColor("#475569")
            d2_color = QColor("#10b981") if is_neg else QColor("#475569")
            
            # Diodes markers
            painter.setPen(QPen(QColor("#334155"), 1.5))
            painter.setBrush(QBrush(d1_color))
            painter.drawEllipse(cx - 40, cy - 25, 30, 30)
            
            painter.setBrush(QBrush(d2_color))
            painter.drawEllipse(cx + 10, cy - 25, 30, 30)
            
            # Text inside
            painter.setPen(QPen(QColor("#ffffff"), 1.5))
            painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
            painter.drawText(int(cx - 34), int(cy - 7), "D1/D3")
            painter.drawText(int(cx + 16), int(cy - 7), "D2/D4")
            
            # Show current path indicators
            path = "D1/D3 conducting" if is_pos else ("D2/D4 conducting" if is_neg else "Idle")
            painter.setPen(QPen(QColor("#94a3b8"), 1))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(w - 180, 45, f"Bridge: {path}")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, f"CURRENT FLOW DIRECTIVITY ({self.rect_type.upper()}-WAVE RECTIFIER)")


class AttenuatorVisualizer(QWidget):
    """Paints signal attenuation block diagram with DB drop scale indicators."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.vin = 5.0
        self.vout = 2.5
        self.att_db = 6.0

    def set_metrics(self, vin: float, vout: float, att_db: float):
        self.vin = vin
        self.vout = vout
        self.att_db = att_db
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # 2. Block Diagram: Input -> Attenuator Pad -> Output
        block_w, block_h = 100, 50
        block_rect = QRectF(cx - block_w // 2, cy - block_h // 2, block_w, block_h)
        
        # Attenuator symbol (Pad block)
        painter.setPen(QPen(QColor("#06b6d4"), 2))
        painter.setBrush(QBrush(QColor("#1e293b")))
        painter.drawRoundedRect(block_rect, 6, 6)
        
        # Connection lines
        painter.setPen(QPen(QColor("#475569"), 2))
        painter.drawLine(20, cy, cx - block_w // 2, cy)
        painter.drawLine(cx + block_w // 2, cy, w - 20, cy)
        
        # Labels on diagram
        painter.setPen(QPen(QColor("#f8fafc"), 1.5))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(block_rect, Qt.AlignmentFlag.AlignCenter, f"-{self.att_db:.1f} dB\nPAD")
        
        # Input AC representation
        painter.setPen(QPen(QColor("#06b6d4"), 1.5))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(30, cy - 30, f"Vin Peak: {self.vin:.1f}V")
        
        # Output AC representation (reduced)
        painter.setPen(QPen(QColor("#10b981"), 1.5))
        painter.drawText(int(w - 140), int(cy - 30), f"Vout Peak: {self.vout:.2f}V")
        
        # Signal power ratios
        p_ratio = (self.vout / self.vin) ** 2 * 100 if self.vin > 0 else 0
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        painter.drawText(cx - 60, cy + 42, f"Power Transmitted: {p_ratio:.1f}%")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, "SIGNAL POWER ATTENUATOR NETWORKS")


class VoltageDividerVisualizer(QWidget):
    """Paints two vertical level bars showing scaling from Vin to Vout in real time."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.vin = 5.0
        self.vout = 2.5

    def set_voltages(self, vin: float, vout: float):
        self.vin = vin
        self.vout = vout
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # Draw two columns (Vin and Vout)
        bar_w = 30
        bar_h = 70
        y_pos = cy - bar_h // 2
        
        # Vin column (frame & fill)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRect(cx - 50, y_pos, bar_w, bar_h)
        
        vin_grad = QLinearGradient(cx - 50, y_pos, cx - 50, y_pos + bar_h)
        vin_grad.setColorAt(0, QColor("#06b6d4"))
        vin_grad.setColorAt(1, QColor("#0284c7"))
        painter.fillRect(cx - 48, y_pos + 2, bar_w - 3, bar_h - 3, QBrush(vin_grad))
        
        # Vout column (frame & fill proportional to ratio)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRect(cx + 20, y_pos, bar_w, bar_h)
        
        ratio = self.vout / self.vin if self.vin > 0 else 0.0
        ratio = max(0.0, min(1.0, ratio))
        fill_h = int(bar_h * ratio)
        
        vout_grad = QLinearGradient(cx + 20, y_pos, cx + 20, y_pos + bar_h)
        vout_grad.setColorAt(0, QColor("#10b981"))
        vout_grad.setColorAt(1, QColor("#047857"))
        painter.fillRect(cx + 22, y_pos + bar_h - fill_h + 1, bar_w - 3, fill_h - 2, QBrush(vout_grad))
        
        # Text labels
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(cx - 50, y_pos - 8, f"Vin")
        painter.drawText(cx + 20, y_pos - 8, f"Vout")
        
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.drawText(cx - 55, y_pos + bar_h + 15, f"{self.vin:.1f} V")
        painter.drawText(cx + 15, y_pos + bar_h + 15, f"{self.vout:.2f} V")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, "SIGNAL AMPLITUDE TRANSMISSION RATIO")


class ResonanceGlowVisualizer(QWidget):
    """Paints a tuning dial or indicator that glows neon green as frequency approaches f0 resonance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.proximity = 0.0  # 0.0 to 1.0 (closeness to resonance peak)

    def set_proximity(self, val: float):
        self.proximity = max(0.0, min(1.0, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # Draw a dial ring
        painter.setPen(QPen(QColor("#1e293b"), 6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(cx, cy), 40, 40)
        
        # Glow color based on proximity (intensity scaling)
        p = self.proximity
        glow_alpha = int(255 * p)
        
        # Radial gradient for glowing center
        radial_grad = QRadialGradient(cx, cy, 45)
        radial_grad.setColorAt(0, QColor(16, 185, 129, glow_alpha)) # Glowing Green
        radial_grad.setColorAt(0.7, QColor(6, 182, 212, int(glow_alpha * 0.4))) # Cyan border glow
        radial_grad.setColorAt(1, QColor(6, 182, 212, 0))
        
        painter.setBrush(QBrush(radial_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(cx, cy), 50, 50)
        
        # Neon marker dot in center
        if p > 0.05:
            painter.setBrush(QBrush(QColor("#f8fafc")))
            painter.drawEllipse(QPoint(cx, cy), 6, 6)
            
        # Draw percentage locking text
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(cx - 30, cy + 55, "Resonance Lock")
        
        # Digital readout
        painter.setPen(QPen(QColor("#10b981") if p > 0.9 else QColor("#f59e0b"), 1))
        painter.drawText(cx - 20, cy - 48, f"{p*100:.1f}%")

        # Title Header
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(15, 25, "SERIES RLC RESONANCE FREQUENCY SCANNER")

