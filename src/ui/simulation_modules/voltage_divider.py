from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame, QWidget
)
from PySide6.QtCore import Qt, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont
import numpy as np
import qtawesome as qta

from src.ui.components.base_simulation import BaseSimulation
from src.core.config import config_manager
from src.utils.formula_formatter import format_eng, format_num

class DividerCircuitVisualizer(QWidget):
    """Paints a premium interactive DC Voltage Divider schematic, live voltmeter, and horizontal voltage bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.vin = 10.0
        self.r1 = 1000.0
        self.r2 = 1000.0
        self.vout = 5.0
        self.current = 0.005 # Amps

    def update_data(self, vin: float, r1: float, r2: float, vout: float, current: float):
        self.vin = vin
        self.r1 = r1
        self.r2 = r2
        self.vout = vout
        self.current = current
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2 - 80, h // 2
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("rgba(15, 23, 42, 0.95)"))
        
        # Draw connections
        painter.setPen(QPen(QColor("#64748b"), 2))
        
        # Vin line to R1
        painter.drawLine(cx - 70, cy - 30, cx, cy - 30)
        painter.drawLine(cx, cy - 30, cx, cy - 20)
        
        # R1 body (Box)
        painter.setBrush(QBrush(QColor("#1e293b")))
        r1_rect = QRectF(cx - 12, cy - 20, 24, 20)
        painter.drawRect(r1_rect)
        
        # R1 to R2 joint line
        painter.drawLine(cx, cy, cx, cy + 15)
        # Vout tap line
        painter.drawLine(cx, cy + 5, cx + 60, cy + 5)
        painter.drawLine(cx + 60, cy + 5, cx + 60, cy + 20)
        
        # R2 body (Box)
        r2_rect = QRectF(cx - 12, cy + 15, 24, 20)
        painter.drawRect(r2_rect)
        
        # R2 to Ground line
        painter.drawLine(cx, cy + 35, cx, cy + 50)
        # Ground symbol
        painter.drawLine(cx - 12, cy + 50, cx + 12, cy + 50)
        painter.drawLine(cx - 8, cy + 53, cx + 8, cy + 53)
        painter.drawLine(cx - 4, cy + 56, cx + 4, cy + 56)

        # Draw labels directly on schematic
        painter.setPen(QPen(QColor("#06b6d4"), 1))
        painter.setFont(QFont("Segoe UI", 8.5, QFont.Weight.Bold))
        painter.drawText(int(cx - 95), int(cy - 35), f"Vin: {self.vin:.1f} V")
        
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        painter.drawText(int(cx + 18), int(cy - 10), f"R1 = {format_eng(self.r1, 'Ω')}")
        painter.drawText(int(cx + 18), int(cy + 28), f"R2 = {format_eng(self.r2, 'Ω')}")
        
        painter.setPen(QPen(QColor("#10b981"), 1))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(int(cx + 70), int(cy + 5), f"Vout = {self.vout:.2f} V")
        
        # Display Current
        painter.setPen(QPen(QColor("#f59e0b"), 1))
        painter.setFont(QFont("Consolas", 8.5, QFont.Weight.Bold))
        painter.drawText(int(cx - 110), int(cy + 45), f"Current: {self.current * 1000:.2f} mA")

        # -------------------------------------------------------------
        # Voltmeter Dial Gauge (Right side center)
        # -------------------------------------------------------------
        vm_cx, vm_cy = w - 180, cy - 10
        vm_r = 45
        
        # Voltmeter Outer Ring
        painter.setPen(QPen(QColor("#334155"), 2.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawEllipse(QPoint(vm_cx, vm_cy), vm_r, vm_r)
        
        # Voltmeter Arc
        painter.setPen(QPen(QColor("#06b6d4"), 2, Qt.PenStyle.SolidLine))
        painter.drawArc(vm_cx - vm_r + 8, vm_cy - vm_r + 8, 2 * vm_r - 16, 2 * vm_r - 16, 30 * 16, 120 * 16)
        
        # Voltmeter Needle
        max_voltage = max(20.0, self.vin)
        ratio = self.vout / max_voltage if max_voltage > 0 else 0
        ratio = max(0.0, min(1.0, ratio))
        
        # Map 0..1 ratio to angle 150..30 degrees (inverted polar)
        angle_rad = np.radians(150.0 - ratio * 120.0)
        nx = vm_cx + (vm_r - 12) * np.cos(angle_rad)
        ny = vm_cy - (vm_r - 12) * np.sin(angle_rad)
        
        painter.setPen(QPen(QColor("#ef4444"), 2))
        painter.drawLine(vm_cx, vm_cy, int(nx), int(ny))
        painter.setBrush(QBrush(QColor("#ef4444")))
        painter.drawEllipse(QPoint(vm_cx, vm_cy), 3, 3)
        
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(vm_cx - 8, vm_cy + 22, "Vout (V)")
        painter.drawText(vm_cx - vm_r + 10, vm_cy + 5, "0V")
        painter.drawText(vm_cx + vm_r - 28, vm_cy + 5, f"{int(max_voltage)}V")

        # -------------------------------------------------------------
        # Horizontal Voltage level bar (Right bottom)
        # -------------------------------------------------------------
        bar_x = w - 240
        bar_y = h - 35
        bar_w = 200
        bar_h = 16
        
        # Background frame
        painter.setPen(QPen(QColor("#334155"), 1.5))
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)
        
        # Active Fill Gradient
        if self.vin > 0:
            fill_ratio = self.vout / self.vin
            fill_w = int(bar_w * max(0.0, min(1.0, fill_ratio)))
            
            bar_grad = QLinearGradient(bar_x, bar_y, bar_x + fill_w, bar_y)
            bar_grad.setColorAt(0, QColor("#06b6d4"))
            bar_grad.setColorAt(1, QColor("#10b981"))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_grad))
            painter.drawRoundedRect(bar_x + 1, bar_y + 1, fill_w - 2, bar_h - 2, 2, 2)
            
        # Level text
        painter.setPen(QPen(QColor("#f8fafc"), 1))
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.Bold))
        painter.drawText(bar_x + 6, bar_y + 11, f"Output Voltage Level: {self.vout:.2f}V / {self.vin:.1f}V")


class VoltageDividerSimulation(BaseSimulation):
    """Interactive swept simulation for Resistor Voltage Dividers."""
    
    def __init__(self, parent=None):
        super().__init__(
            title="Voltage Divider Visualization",
            formula_str="Vout = Vin × R2 / (R1 + R2)",
            explanation_str=(
                "A voltage divider outputs a fraction of its input voltage based on the resistor ratio. "
                "Press the Play button to scan R2 values automatically. Moving any slider manually "
                "immediately updates the circuit diagram, voltmeter needle, and voltage level bar."
            ),
            parent=parent
        )

    def setup_inputs(self, layout: QVBoxLayout):
        # 1. Slider Vin
        v_title_layout = QHBoxLayout()
        v_title_layout.addWidget(QLabel("Input Voltage (Vin):"))
        self.vin_lbl = QLabel("10.0 V")
        self.vin_lbl.setStyleSheet("font-weight: bold; color: #06b6d4;")
        v_title_layout.addStretch()
        v_title_layout.addWidget(self.vin_lbl)
        layout.addLayout(v_title_layout)
        
        self.vin_slider = QSlider(Qt.Orientation.Horizontal)
        self.vin_slider.setRange(10, 200) # 1.0V to 20.0V (scaled by 10)
        self.vin_slider.setValue(100)
        layout.addWidget(self.vin_slider)

        # 2. Slider R1
        r1_title_layout = QHBoxLayout()
        r1_title_layout.addWidget(QLabel("Resistor R1 (Ω):"))
        self.r1_lbl = QLabel("1.00 kΩ")
        self.r1_lbl.setStyleSheet("font-weight: bold; color: #f8fafc;")
        r1_title_layout.addStretch()
        r1_title_layout.addWidget(self.r1_lbl)
        layout.addLayout(r1_title_layout)
        
        self.r1_slider = QSlider(Qt.Orientation.Horizontal)
        self.r1_slider.setRange(100, 10000) # 100Ω to 10kΩ
        self.r1_slider.setValue(1000)
        layout.addWidget(self.r1_slider)

        # 3. Slider R2
        r2_title_layout = QHBoxLayout()
        r2_title_layout.addWidget(QLabel("Resistor R2 (Ω):"))
        self.r2_lbl = QLabel("1.00 kΩ")
        self.r2_lbl.setStyleSheet("font-weight: bold; color: #f8fafc;")
        r2_title_layout.addStretch()
        r2_title_layout.addWidget(self.r2_lbl)
        layout.addLayout(r2_title_layout)
        
        self.r2_slider = QSlider(Qt.Orientation.Horizontal)
        self.r2_slider.setRange(100, 10000) # 100Ω to 10kΩ
        self.r2_slider.setValue(1000)
        layout.addWidget(self.r2_slider)

        # Connect value change signals to update loop
        self.vin_slider.valueChanged.connect(self.on_slider_dragged)
        self.r1_slider.valueChanged.connect(self.on_slider_dragged)
        self.r2_slider.valueChanged.connect(self.on_slider_dragged)

    def setup_visualizer(self, layout: QVBoxLayout):
        self.visualizer = DividerCircuitVisualizer(self)
        layout.addWidget(self.visualizer)

    def init_simulation(self):
        self.plot_canvas.ax.set_title("Vout vs Resistor R2")
        self.plot_canvas.ax.set_xlabel("Resistance R2 (Ω)")
        self.plot_canvas.ax.set_ylabel("Output Voltage Vout (V)")
        self.reset_data()

    def reset_data(self):
        self.sim_time = 0.0
        # Reset R2 to default 1.0k
        self.r2_slider.blockSignals(True)
        self.r2_slider.setValue(1000)
        self.r2_slider.blockSignals(False)
        self.calculate_instantly()

    def on_slider_dragged(self):
        # Sync sim_time to the manually dragged R2 slider position
        if not self.is_running:
            r2_min = 100.0
            r2_max = 10000.0
            r2_val = float(self.r2_slider.value())
            # Set time proportional to swept R2 ratio
            self.sim_time = ((r2_val - r2_min) / (r2_max - r2_min)) * 5.0
            
        self.calculate_instantly()

    def update_simulation_step(self, dt: float):
        # Sweeping R2 from minimum to maximum over a 5-second loop
        t_max = 5.0
        self.sim_time += dt * self.sim_speed
        
        # Loop continuously
        if self.sim_time > t_max:
            self.sim_time = self.sim_time % t_max
            
        r2_min = 100.0
        r2_max = 10000.0
        r2_val = r2_min + (self.sim_time / t_max) * (r2_max - r2_min)
        
        # Set slider position matching swept calculations (suppress recursion signals)
        self.r2_slider.blockSignals(True)
        self.r2_slider.setValue(int(r2_val))
        self.r2_slider.blockSignals(False)
        
        self.calculate_instantly()

    def calculate_instantly(self):
        vin = self.vin_slider.value() / 10.0
        r1 = float(self.r1_slider.value())
        r2 = float(self.r2_slider.value())

        # Update text value labels
        self.vin_lbl.setText(f"{vin:.1f} V")
        self.r1_lbl.setText(format_eng(r1, "Ω"))
        self.r2_lbl.setText(format_eng(r2, "Ω"))

        # Math calculations
        vout = vin * r2 / (r1 + r2)
        current = vin / (r1 + r2)

        # Update visualizer schematic & voltmeter
        self.visualizer.update_data(vin, r1, r2, vout, current)

        # Update answer bar text
        self.time_lbl.setText(f"Sweep Time: {self.sim_time:.2f}s")
        self.answer_label.setText(f"Vout: {vout:.2f} V  |  Current: {current*1000:.2f} mA")

        # Display static graph updates
        self.update_plot_canvas_static(vin, r1, r2, vout)

        self.steps_text.setText(
            f"**Voltage Divider DC Analysis**:\n\n"
            f"- **Input Voltage (Vin)**: {vin:.1f} V\n"
            f"- **Voltage drop R1 (V_drop)**: {vin - vout:.2f} V\n"
            f"- **Output Voltage (Vout)**: {vout:.2f} V\n"
            f"- **Divider Ratio**: {r2 / (r1 + r2):.4f}\n"
            f"- **Loop Current (I)**: {format_eng(current, 'A')}\n"
            f"- **Total Impedance (R1 + R2)**: {format_eng(r1 + r2, 'Ω')}"
        )

    def update_plot_canvas_static(self, vin, r1, r2, vout):
        self.plot_canvas.ax.clear()
        self.plot_canvas.apply_theme_colors()

        r2_min = 100.0
        r2_max = float(self.r2_slider.maximum())
        r2_axis = np.linspace(r2_min, r2_max, 500)
        vout_axis = vin * r2_axis / (r1 + r2_axis)

        line_w = config_manager.get("graph_line_width") or 2
        self.plot_canvas.ax.plot(r2_axis, vout_axis, color="#10b981", linewidth=line_w, label="Vout vs R2 curve")
        
        # Highlight active operating point
        self.plot_canvas.ax.scatter([r2], [vout], color="#ef4444", s=70, zorder=5, label="Active Operating Point")

        self.plot_canvas.ax.set_title("Vout vs Resistance R2 Curve")
        self.plot_canvas.ax.set_xlabel("Resistance R2 (Ω)")
        self.plot_canvas.ax.set_ylabel("Output Voltage Vout (V)")
        self.plot_canvas.ax.set_xlim(r2_min, r2_max)
        self.plot_canvas.ax.set_ylim(0, 1.05 * vin)
        self.plot_canvas.ax.legend(loc="lower right")
        self.plot_canvas.draw()

    def get_oscilloscope_waveforms(self, time_axis):
        try:
            vin = self.vin_slider.value() / 10.0
            r1 = float(self.r1_slider.value())
            r2 = float(self.r2_slider.value())
        except Exception:
            vin, r1, r2 = 5.0, 1000.0, 1000.0
            
        ch1 = vin * np.sin(2.0 * np.pi * 1000.0 * time_axis)
        ch2 = vin * (r2 / (r1 + r2)) * np.sin(2.0 * np.pi * 1000.0 * time_axis)
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
