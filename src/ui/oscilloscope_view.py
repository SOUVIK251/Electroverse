"""
DEVELOPER NOTES & ROOT CAUSE AUDIT:
1. Disappearing Channels:
   - Root Cause: Desynchronization of channel rendering logic, where checkboxes for CH2 were unchecked or disabled by default during manual override switching.
   - Refactor: Enforce layout and channel state logic inside on_circuit_override to auto-enable both channels on dual-signal circuits.
2. Frozen Waveforms:
   - Root Cause: Multiple animation timers running concurrently, conflicting with main GUI event loop rendering, and absence of manual updates during paused state.
   - Refactor: Extracted all generation/processing into a single centralized method `generate_and_process_waveforms` that runs both on timer ticks (if active) and immediately on any slider/config parameter change event regardless of play/pause state.
3. Incorrect Waveforms:
   - Root Cause: Reusing generic wave generators without modeling ECE circuit behavior mathematically.
   - Refactor: Modularized math-correct simulators for all 20+ laboratory experiments.
"""

import sys
import numpy as np
import csv
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QSlider, QGridLayout, QFileDialog, QLineEdit, QSplitter,
    QTabWidget, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPixmap
import qtawesome as qta
from src.core.logger import log
from src.core.config import config_manager
from src.utils.formula_formatter import format_eng
from src.engine.simulation_engine import (
    StandaloneOscilloscopeSimulation,
    SignalGeneratorSimulation,
    VoltageDividerSimulation,
    RCTransientSimulation,
    RLTransientSimulation,
    RectifierSimulation,
    ClipperSimulation,
    ClamperSimulation,
    AttenuatorSimulation,
    FilterSimulation,
    ResonanceSimulation,
    CommunicationSimulation
)

class ChannelRenderer:
    """Holds the complete independent render state for one oscilloscope channel.

    No state from this object is ever shared with another ChannelRenderer.
    Moving vertical_position on CH1's renderer has zero effect on CH2's renderer.
    """

    def __init__(self, color_core: str, color_glow: str, label: str):
        # Identity
        self.label = label                  # "CH1" or "CH2"
        self.color_core = color_core        # "#eab308" / "#ec4899"
        self.color_glow = color_glow        # rgba glow string

        # Waveform data (numpy arrays set by the parent widget)
        self.waveform: np.ndarray = np.array([])   # voltage samples

        # Scale settings (set by OscilloscopeView.set_ch*_scale)
        self.vscale: float = 1.0            # V/div
        self.dc_offset: float = 0.0        # V  (electrical zero shift)

        # Visual-only vertical position: divisions, +up / -down
        # THIS IS THE ONLY VARIABLE that the Position slider writes.
        # dc_offset is never touched by the Position slider.
        self.vertical_position: float = 0.0   # divisions

        # Enable flag
        self.enabled: bool = True

    # ------------------------------------------------------------------
    # Public setters — each one touches ONLY this renderer's own fields
    # ------------------------------------------------------------------

    def set_waveform(self, data: np.ndarray):
        self.waveform = data

    def set_scale(self, vscale: float, dc_offset: float):
        self.vscale = vscale
        self.dc_offset = dc_offset

    def set_vertical_position(self, divisions: float):
        """Visual shift in grid divisions. Positive = up. Never touches dc_offset."""
        self.vertical_position = divisions

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    # ------------------------------------------------------------------
    # Rendering — called by OscilloscopeScreen.paintEvent
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter, w: int, h: int, dy: float):
        """Draw this channel's waveform onto the painter.

        Parameters
        ----------
        painter : active QPainter
        w, h    : screen pixel dimensions
        dy      : pixels per grid division  (= h / 8)

        The centre of the screen (cy = h/2) is the electrical zero line for
        BOTH channels independently — each channel shifts away from that
        centre using its OWN dc_offset AND its OWN vertical_position.
        Nothing here reads or writes the other channel's data.
        """
        if not self.enabled or len(self.waveform) < 2:
            return

        n_pts = len(self.waveform)
        cy = h / 2.0
        v_span = 8.0 * self.vscale          # total voltage span across 8 rows

        # pos_px: pixels to shift the trace upward (positive = up = negative y)
        pos_px = self.vertical_position * dy

        # Build pixel points independently for THIS channel only
        pts = []
        for idx in range(n_pts):
            x = int(idx / (n_pts - 1) * w)
            # Voltage → pixel Y:
            #   cy             : screen centre (electrical 0 V reference)
            #   dc_offset term : shifts centre for non-zero DC offset
            #   pos_px         : visual-only shift from the Position slider
            volt = self.waveform[idx]
            y = cy - (volt - self.dc_offset) / v_span * h - pos_px
            pts.append(QPoint(x, int(y)))

        # Glow pass (wide, translucent)
        glow_pen = QPen(QColor(self.color_glow), 5,
                        Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

        # Core pass (sharp, opaque)
        core_pen = QPen(QColor(self.color_core), 1.8,
                        Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(core_pen)
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

        # Ground-reference marker arrow on left edge
        # Points to where 0 V sits on screen for this channel
        marker_y = int(cy - self.dc_offset / v_span * h - pos_px)
        painter.setBrush(QBrush(QColor(self.color_core)))
        painter.setPen(Qt.PenStyle.NoPen)
        arrow = [
            QPoint(0, marker_y),
            QPoint(10, marker_y - 5),
            QPoint(10, marker_y + 5),
        ]
        painter.drawPolygon(arrow)
        painter.setPen(QPen(QColor(self.color_core), 1))
        painter.setFont(QFont("Consolas", 7, QFont.Weight.Bold))
        painter.drawText(12, marker_y + 4, self.label)


class OscilloscopeScreen(QWidget):
    """Custom paint widget representing a real-time dual-channel DSO screen.

    Architecture
    ------------
    Two completely independent ChannelRenderer objects (ch1, ch2) own ALL
    per-channel state.  The paintEvent draws:

        Background → Grid → CH1 (via ch1.draw) → CH2 (via ch2.draw)
            → Trigger line → Cursors

    The two renderers NEVER share a Y-offset, a position variable, or any
    other vertical coordinate.  Modifying ch1.vertical_position has zero
    effect on ch2, by construction.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 260)
        self.setMaximumHeight(280)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # --- Two independent channel renderers ----------------------------
        self.ch1 = ChannelRenderer(
            color_core="#eab308",
            color_glow="rgba(234, 179, 8, 0.3)",
            label="CH1",
        )
        self.ch2 = ChannelRenderer(
            color_core="#06b6d4",
            color_glow="rgba(6, 182, 212, 0.3)",
            label="CH2",
        )

        # --- Grid / trigger / cursor shared parameters -------------------
        self.time_base: float = 0.001       # s/div
        self.trigger_level: float = 0.0    # V
        self.trigger_source: str = "CH1"
        self.trigger_edge: str = "Rising"
        self.trigger_state: str = "Auto"

        # Legacy compatibility: expose flat offsets so existing callers
        # (sync_offset_inputs, set_scales) keep working unchanged.
        # These are just pass-through properties that write into the renderers.
        self._ch1_offset: float = 0.0
        self._ch2_offset: float = 0.0

        # Movable cursor state
        self.cursors_enabled: bool = False
        self.cursor_x1: float = 0.25
        self.cursor_x2: float = 0.75
        self.cursor_y1: float = 0.3
        self.cursor_y2: float = 0.7
        self.active_cursor = None

        # Mouse-drag pan state
        self.drag_start = None
        self.orig_ch1_offset: float = 0.0
        self.orig_ch2_offset: float = 0.0

    # ------------------------------------------------------------------
    # Legacy flat-property shims (keep existing OscilloscopeView callers happy)
    # ------------------------------------------------------------------

    @property
    def ch1_offset(self) -> float:
        return self._ch1_offset

    @ch1_offset.setter
    def ch1_offset(self, v: float):
        self._ch1_offset = v
        self.ch1.dc_offset = v

    @property
    def ch2_offset(self) -> float:
        return self._ch2_offset

    @ch2_offset.setter
    def ch2_offset(self, v: float):
        self._ch2_offset = v
        self.ch2.dc_offset = v

    @property
    def ch1_enabled(self) -> bool:
        return self.ch1.enabled

    @ch1_enabled.setter
    def ch1_enabled(self, v: bool):
        self.ch1.enabled = v

    @property
    def ch2_enabled(self) -> bool:
        return self.ch2.enabled

    @ch2_enabled.setter
    def ch2_enabled(self, v: bool):
        self.ch2.enabled = v

    @property
    def ch1_vscale(self) -> float:
        return self.ch1.vscale

    @ch1_vscale.setter
    def ch1_vscale(self, v: float):
        self.ch1.vscale = v

    @property
    def ch2_vscale(self) -> float:
        return self.ch2.vscale

    @ch2_vscale.setter
    def ch2_vscale(self, v: float):
        self.ch2.vscale = v

    @property
    def ch1_volt(self) -> np.ndarray:
        return self.ch1.waveform

    @ch1_volt.setter
    def ch1_volt(self, v: np.ndarray):
        self.ch1.waveform = v

    @property
    def ch2_volt(self) -> np.ndarray:
        return self.ch2.waveform

    @ch2_volt.setter
    def ch2_volt(self, v: np.ndarray):
        self.ch2.waveform = v

    # ------------------------------------------------------------------
    # Public API called by OscilloscopeView
    # ------------------------------------------------------------------

    def set_waveforms(self, t, ch1_v, ch2_v, ch1_en, ch2_en):
        """Update waveform data and enable flags for both channels."""
        # Time axis kept here only for cursor calculations
        self.time_data = t
        self.ch1.set_waveform(ch1_v)
        self.ch2.set_waveform(ch2_v)
        self.ch1.set_enabled(ch1_en)
        self.ch2.set_enabled(ch2_en)
        self.update()

    def set_scales(self, time_base, ch1_vscale, ch2_vscale,
                   ch1_offset, ch2_offset,
                   trig_level, trig_src, trig_edge, trig_state):
        """Update grid and trigger parameters. Vertical positions are untouched."""
        self.time_base = time_base
        self.ch1.set_scale(ch1_vscale, ch1_offset)
        self.ch2.set_scale(ch2_vscale, ch2_offset)
        self._ch1_offset = ch1_offset
        self._ch2_offset = ch2_offset
        self.trigger_level = trig_level
        self.trigger_source = trig_src
        self.trigger_edge = trig_edge
        self.trigger_state = trig_state
        self.update()

    def set_positions(self, ch1_pos: float, ch2_pos: float):
        """Set visual vertical position for both channels simultaneously.

        Each value is written only to its own ChannelRenderer — they never
        interact.  This method exists for bulk resets (e.g. Auto Scale).
        """
        self.ch1.set_vertical_position(ch1_pos)
        self.ch2.set_vertical_position(ch2_pos)
        self.update()

    def set_ch1_position(self, pos: float):
        """Move ONLY CH1 vertically.  CH2.vertical_position is never read or written."""
        self.ch1.set_vertical_position(pos)
        self.update()

    def set_ch2_position(self, pos: float):
        """Move ONLY CH2 vertically.  CH1.vertical_position is never read or written."""
        self.ch2.set_vertical_position(pos)
        self.update()

    # ------------------------------------------------------------------
    # paintEvent — strict rendering order with independent channel calls
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        divs_x = 10
        divs_y = 8
        dx = w / divs_x
        dy = h / divs_y   # pixels per grid division — used by ChannelRenderer.draw

        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("#000000"))

        # 2. Soft grid lines
        grid_pen = QPen(QColor("rgba(74, 85, 104, 0.3)"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(1, divs_x):
            painter.drawLine(int(i * dx), 0, int(i * dx), h)
        for j in range(1, divs_y):
            painter.drawLine(0, int(j * dy), w, int(j * dy))

        # 3. Centre axis lines
        axis_pen = QPen(QColor("rgba(74, 85, 104, 0.7)"), 1.5)
        painter.setPen(axis_pen)
        painter.drawLine(cx, 0, cx, h)
        painter.drawLine(0, cy, w, cy)

        # 4. Centre tick marks
        tick_pen = QPen(QColor("rgba(74, 85, 104, 0.8)"), 1)
        painter.setPen(tick_pen)
        tick_size = 4
        for y in range(0, h, max(1, int(dy / 5))):
            painter.drawLine(cx - tick_size, y, cx + tick_size, y)
        for x in range(0, w, max(1, int(dx / 5))):
            painter.drawLine(x, cy - tick_size, x, cy + tick_size)

        # 5. Trigger level line (red, drawn BEFORE waveforms)
        trig_renderer = self.ch1 if self.trigger_source == "CH1" else self.ch2
        trig_y = int(cy - (self.trigger_level - trig_renderer.dc_offset)
                     / (8.0 * trig_renderer.vscale) * h)
        if 0 <= trig_y <= h:
            trig_pen = QPen(QColor("rgba(239, 68, 68, 0.6)"), 1, Qt.PenStyle.DotLine)
            painter.setPen(trig_pen)
            painter.drawLine(0, trig_y, w, trig_y)
            painter.setBrush(QBrush(QColor("#ef4444")))
            painter.setPen(Qt.PenStyle.NoPen)
            arrow = [QPoint(w, trig_y), QPoint(w - 8, trig_y - 4), QPoint(w - 8, trig_y + 4)]
            painter.drawPolygon(arrow)

        # 6. CH1 — drawn independently using ch1.vertical_position only
        self.ch1.draw(painter, w, h, dy)

        # 7. CH2 — drawn independently using ch2.vertical_position only
        self.ch2.draw(painter, w, h, dy)

        # 8. Movable cursors
        if self.cursors_enabled:
            x1_px = int(self.cursor_x1 * w)
            x2_px = int(self.cursor_x2 * w)
            y1_px = int(self.cursor_y1 * h)
            y2_px = int(self.cursor_y2 * h)

            painter.setPen(QPen(QColor("#06b6d4"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(x1_px, 0, x1_px, h)
            painter.drawLine(x2_px, 0, x2_px, h)

            painter.setPen(QPen(QColor("#a855f7"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(0, y1_px, w, y1_px)
            painter.drawLine(0, y2_px, w, y2_px)

            painter.setPen(QPen(QColor("#a855f7"), 1))
            painter.drawText(5, y1_px - 4, "Y1")
            painter.drawText(5, y2_px - 4, "Y2")

    # ------------------------------------------------------------------
    # Mouse / wheel event handlers (unchanged logic, now using properties)
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        pos = event.position()
        w, h = self.width(), self.height()

        if self.cursors_enabled:
            margin = 10
            if abs(pos.x() - self.cursor_x1 * w) < margin:
                self.active_cursor = 'X1'; return
            elif abs(pos.x() - self.cursor_x2 * w) < margin:
                self.active_cursor = 'X2'; return
            elif abs(pos.y() - self.cursor_y1 * h) < margin:
                self.active_cursor = 'Y1'; return
            elif abs(pos.y() - self.cursor_y2 * h) < margin:
                self.active_cursor = 'Y2'; return

        self.drag_start = pos
        self.orig_ch1_offset = self._ch1_offset
        self.orig_ch2_offset = self._ch2_offset

    def mouseMoveEvent(self, event):
        pos = event.position()
        w, h = self.width(), self.height()

        if self.active_cursor:
            if self.active_cursor == 'X1':
                self.cursor_x1 = max(0.0, min(1.0, pos.x() / w))
            elif self.active_cursor == 'X2':
                self.cursor_x2 = max(0.0, min(1.0, pos.x() / w))
            elif self.active_cursor == 'Y1':
                self.cursor_y1 = max(0.0, min(1.0, pos.y() / h))
            elif self.active_cursor == 'Y2':
                self.cursor_y2 = max(0.0, min(1.0, pos.y() / h))
            self.update()
            parent = self.parent()
            if parent and hasattr(parent, "update_cursor_calculations"):
                parent.update_cursor_calculations()

        elif self.drag_start:
            dy_px = pos.y() - self.drag_start.y()
            # Each channel pans independently using its own vscale
            if self.ch1.enabled:
                v_span1 = 8.0 * self.ch1.vscale
                new_off1 = self.orig_ch1_offset + (dy_px / h) * v_span1
                self.ch1_offset = new_off1   # property → ch1.dc_offset
            if self.ch2.enabled:
                v_span2 = 8.0 * self.ch2.vscale
                new_off2 = self.orig_ch2_offset + (dy_px / h) * v_span2
                self.ch2_offset = new_off2   # property → ch2.dc_offset
            self.update()
            parent = self.parent()
            if parent and hasattr(parent, "sync_offset_inputs"):
                parent.sync_offset_inputs(self._ch1_offset, self._ch2_offset)

    def mouseReleaseEvent(self, event):
        self.active_cursor = None
        self.drag_start = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        parent = self.parent()
        if parent:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                parent.scale_volts(1.25 if delta < 0 else 0.8)
            else:
                parent.scale_timebase(1.25 if delta < 0 else 0.8)


class OscilloscopeView(QWidget):
    """Laboratory-grade benchtop Digital Storage Oscilloscope (DSO) simulated environment."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing laboratory-grade dual-channel DSO module")
        
        self.is_running = True
        self.sampling_rate = 250000.0 # 250 kHz high-resolution sampling
        self.sim_time = 0.0
        self.fps_counter = 0
        self.fps_rate = 60
        self.manual_override = False
        self.last_circuit = None
        
        # Smooth rendering variables for real DSO behavior
        self.tbase_smooth = 0.05
        self.ch1_vscale_smooth = 2.0
        self.ch2_vscale_smooth = 1.0
        self.ch1_offset_smooth = 0.0
        self.ch2_offset_smooth = 0.0

        # Target variables for smooth scaling
        self.tbase_target = 0.05
        self.ch1_vscale_target = 2.0
        self.ch2_vscale_target = 1.0
        self.ch1_offset_target = 0.0
        self.ch2_offset_target = 0.0

        # Parameter Defaults
        self.param_R = 1000.0
        self.param_C = 10e-6
        self.param_L = 10e-3
        self.param_Load = 10000.0
        self.param_Vcc = 5.0
        self.param_Duty = 0.5

        # Mathematical simulation engine instances
        self.math_sims = {
            "Standalone Oscilloscope": StandaloneOscilloscopeSimulation(),
            "Signal Generator": SignalGeneratorSimulation(),
            "Voltage Divider": VoltageDividerSimulation(),
            "RC Charging": RCTransientSimulation("Charging"),
            "RC Discharging": RCTransientSimulation("Discharging"),
            "RL Transient": RLTransientSimulation(),
            "Low Pass Filter": FilterSimulation("LowPass"),
            "High Pass Filter": FilterSimulation("HighPass"),
            "Half Wave Rectifier": RectifierSimulation("HalfWave"),
            "Full Wave Rectifier": RectifierSimulation("FullWave"),
            "Positive Clipper": ClipperSimulation("Positive"),
            "Negative Clipper": ClipperSimulation("Negative"),
            "Positive Clamper": ClamperSimulation("Positive"),
            "Negative Clamper": ClamperSimulation("Negative"),
            "Signal Attenuator": AttenuatorSimulation(),
            "Amplitude Modulation": CommunicationSimulation("AM"),
            "Frequency Modulation": CommunicationSimulation("FM"),
            "ASK": CommunicationSimulation("ASK"),
            "FSK": CommunicationSimulation("FSK"),
            "PSK": CommunicationSimulation("PSK"),
            "BPSK": CommunicationSimulation("BPSK"),
            "QPSK": CommunicationSimulation("QPSK"),
            "RLC Resonance": ResonanceSimulation()
        }
        
        self.fps_timer = QTimer(self)
        self.fps_timer.setInterval(1000)
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start()

        # Channel 1 Parameter Defaults
        self.ch1_en = True
        self.ch1_type = "Sine"
        self.ch1_freq = 1000.0
        self.ch1_amp = 3.0
        self.ch1_phase = 0.0
        self.ch1_offset = 0.0

        # Channel 2 Parameter Defaults
        self.ch2_en = True
        self.ch2_type = "Triangle"
        self.ch2_freq = 2000.0
        self.ch2_amp = 2.0
        self.ch2_phase = 90.0
        self.ch2_offset = 0.0

        self.noise_lvl = 0.0
        
        # Primary Layout: Left Panels (width ~25%), Right CRT Screen View (width ~75%)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # -------------------------------------------------------------
        # Controls Tab (Compact, placed at the bottom)
        # -------------------------------------------------------------
        self.controls_tab = QTabWidget()
        self.controls_tab.setFixedHeight(170)
        self.setup_ch1_tab()
        self.setup_ch2_tab()
        self.setup_trig_tab()
        self.setup_vertical_tab()
        self.setup_parameters_tab()

        # -------------------------------------------------------------
        # Display Block (Occupies top area)
        # -------------------------------------------------------------
        self.crt_layout = QVBoxLayout()
        self.crt_layout.setSpacing(6)
        
        # Toolbar Top
        self.setup_toolbar()
        
        # Screen (occupies 75-80% height of display block)
        self.display_screen = OscilloscopeScreen(self)
        self.crt_layout.addWidget(self.display_screen, stretch=6)
        
        # Measurements Grid Bottom
        self.setup_measurements_bottom()
        
        # Status Bar Bottom
        self.setup_status_bar()
        
        self.main_layout.addLayout(self.crt_layout, stretch=4)
        self.main_layout.addWidget(self.controls_tab, stretch=0)

        # Set initial parameters
        self.on_inputs_changed()

        # Animation Trigger tick (runs at ~45 FPS)
        self.timer = QTimer(self)
        self.timer.setInterval(22)
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start()

    def setup_ch1_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        col1 = QVBoxLayout()
        self.ch1_en_chk = QCheckBox("Enable CH1 (Yellow)")
        self.ch1_en_chk.setChecked(True)
        self.ch1_en_chk.toggled.connect(self.on_inputs_changed)
        col1.addWidget(self.ch1_en_chk)
        col1.addWidget(QLabel("Waveform Type:"))
        self.ch1_type_combo = QComboBox()
        self.ch1_type_combo.addItems(["Sine", "Square", "Triangle", "Sawtooth", "Pulse", "Noise"])
        self.ch1_type_combo.currentTextChanged.connect(self.on_inputs_changed)
        col1.addWidget(self.ch1_type_combo)
        layout.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Frequency (Hz):"))
        self.ch1_freq_inp = QLineEdit("1000.0")
        self.ch1_freq_inp.textChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.ch1_freq_inp)
        col2.addWidget(QLabel("Amplitude (V):"))
        self.ch1_amp_inp = QLineEdit("3.0")
        self.ch1_amp_inp.textChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.ch1_amp_inp)
        layout.addLayout(col2)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("DC Offset (V):"))
        self.ch1_offset_inp = QLineEdit("0.0")
        self.ch1_offset_inp.textChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.ch1_offset_inp)
        col3.addWidget(QLabel("Phase (deg):"))
        self.ch1_phase_inp = QLineEdit("0.0")
        self.ch1_phase_inp.textChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.ch1_phase_inp)
        layout.addLayout(col3)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Volts/Div Scale:"))
        self.ch1_vscale_combo = QComboBox()
        self.ch1_vscale_combo.addItems(["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"])
        self.ch1_vscale_combo.setCurrentText("2 V")
        self.ch1_vscale_combo.currentTextChanged.connect(self.on_inputs_changed)
        col4.addWidget(self.ch1_vscale_combo)
        col4.addStretch()
        layout.addLayout(col4)

        self.controls_tab.addTab(tab, "CH 1")

    def setup_ch2_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        col1 = QVBoxLayout()
        self.ch2_en_chk = QCheckBox("Enable CH2 (Cyan)")
        self.ch2_en_chk.setChecked(True)
        self.ch2_en_chk.toggled.connect(self.on_inputs_changed)
        col1.addWidget(self.ch2_en_chk)
        col1.addWidget(QLabel("Waveform Type:"))
        self.ch2_type_combo = QComboBox()
        self.ch2_type_combo.addItems(["Sine", "Square", "Triangle", "Sawtooth", "Pulse", "Noise"])
        self.ch2_type_combo.currentTextChanged.connect(self.on_inputs_changed)
        col1.addWidget(self.ch2_type_combo)
        layout.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Frequency (Hz):"))
        self.ch2_freq_inp = QLineEdit("2000.0")
        self.ch2_freq_inp.textChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.ch2_freq_inp)
        col2.addWidget(QLabel("Amplitude (V):"))
        self.ch2_amp_inp = QLineEdit("2.0")
        self.ch2_amp_inp.textChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.ch2_amp_inp)
        layout.addLayout(col2)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("DC Offset (V):"))
        self.ch2_offset_inp = QLineEdit("0.0")
        self.ch2_offset_inp.textChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.ch2_offset_inp)
        col3.addWidget(QLabel("Phase (deg):"))
        self.ch2_phase_inp = QLineEdit("90.0")
        self.ch2_phase_inp.textChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.ch2_phase_inp)
        layout.addLayout(col3)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Volts/Div Scale:"))
        self.ch2_vscale_combo = QComboBox()
        self.ch2_vscale_combo.addItems(["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"])
        self.ch2_vscale_combo.setCurrentText("1 V")
        self.ch2_vscale_combo.currentTextChanged.connect(self.on_inputs_changed)
        col4.addWidget(self.ch2_vscale_combo)
        col4.addStretch()
        layout.addLayout(col4)

        self.controls_tab.addTab(tab, "CH 2")

    def setup_trig_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Time Base (Sec/Div):"))
        self.tbase_combo = QComboBox()
        self.tbase_combo.addItems([
            "100 μs", "500 μs", "1 ms", "2 ms", "5 ms", "10 ms", "20 ms", "50 ms", "100 ms",
            "200 ms", "500 ms", "1 s", "2 s"
        ])
        self.tbase_combo.setCurrentText("50 ms")
        self.tbase_combo.currentTextChanged.connect(self.on_inputs_changed)
        col1.addWidget(self.tbase_combo)
        col1.addStretch()
        layout.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Trigger Source:"))
        self.trig_src_combo = QComboBox()
        self.trig_src_combo.addItems(["CH1", "CH2"])
        self.trig_src_combo.currentTextChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.trig_src_combo)
        col2.addWidget(QLabel("Trigger Mode:"))
        self.trig_mode_combo = QComboBox()
        self.trig_mode_combo.addItems(["Auto", "Normal", "Single"])
        self.trig_mode_combo.currentTextChanged.connect(self.on_inputs_changed)
        col2.addWidget(self.trig_mode_combo)
        layout.addLayout(col2)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Trigger Edge:"))
        self.trig_edge_combo = QComboBox()
        self.trig_edge_combo.addItems(["Rising", "Falling"])
        self.trig_edge_combo.currentTextChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.trig_edge_combo)
        col3.addWidget(QLabel("Trigger Level (V):"))
        self.trig_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.trig_level_slider.setRange(-50, 50)
        self.trig_level_slider.setValue(0)
        self.trig_level_slider.valueChanged.connect(self.on_inputs_changed)
        col3.addWidget(self.trig_level_slider)
        layout.addLayout(col3)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Gaussian Noise (%):"))
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setRange(0, 100)
        self.noise_slider.setValue(0)
        self.noise_slider.valueChanged.connect(self.on_inputs_changed)
        col4.addWidget(self.noise_slider)
        col4.addStretch()
        layout.addLayout(col4)

        self.controls_tab.addTab(tab, "DSO Config")

    def setup_vertical_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        col1 = QVBoxLayout()
        ch1_label = QLabel("Channel 1 Position")
        ch1_label.setStyleSheet("color: #eab308; font-weight: bold; font-size: 12px;")
        col1.addWidget(ch1_label)
        self.ch1_pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.ch1_pos_slider.setRange(-50, 50)
        self.ch1_pos_slider.setValue(0)
        self.ch1_pos_slider.setTickInterval(10)
        self.ch1_pos_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ch1_pos_slider.setToolTip("CH1 vertical position (-5 to +5 div)")
        self.ch1_pos_slider.valueChanged.connect(self._on_ch1_pos_changed)
        self.ch1_pos_label = QLabel("0.0 div")
        self.ch1_pos_label.setStyleSheet("color: #eab308;")
        col1.addWidget(self.ch1_pos_slider)
        col1.addWidget(self.ch1_pos_label)
        layout.addLayout(col1)

        col2 = QVBoxLayout()
        ch2_label = QLabel("Channel 2 Position")
        ch2_label.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 12px;")
        col2.addWidget(ch2_label)
        self.ch2_pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.ch2_pos_slider.setRange(-50, 50)
        self.ch2_pos_slider.setValue(0)
        self.ch2_pos_slider.setTickInterval(10)
        self.ch2_pos_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ch2_pos_slider.setToolTip("CH2 vertical position (-5 to +5 div)")
        self.ch2_pos_slider.valueChanged.connect(self._on_ch2_pos_changed)
        self.ch2_pos_label = QLabel("0.0 div")
        self.ch2_pos_label.setStyleSheet("color: #06b6d4;")
        col2.addWidget(self.ch2_pos_slider)
        col2.addWidget(self.ch2_pos_label)
        layout.addLayout(col2)

        col3 = QVBoxLayout()
        ch1_reset_btn = QPushButton("Reset CH1")
        ch1_reset_btn.setFixedHeight(26)
        ch1_reset_btn.setStyleSheet(
            "QPushButton { background:#1e293b; color:#eab308; border:1px solid #334155; border-radius:4px; font-size:11px; }"
            "QPushButton:hover { background:#334155; }"
        )
        ch1_reset_btn.clicked.connect(lambda: self.ch1_pos_slider.setValue(0))
        col3.addWidget(ch1_reset_btn)
        
        ch2_reset_btn = QPushButton("Reset CH2")
        ch2_reset_btn.setFixedHeight(26)
        ch2_reset_btn.setStyleSheet(
            "QPushButton { background:#1e293b; color:#06b6d4; border:1px solid #334155; border-radius:4px; font-size:11px; }"
            "QPushButton:hover { background:#334155; }"
        )
        ch2_reset_btn.clicked.connect(lambda: self.ch2_pos_slider.setValue(0))
        col3.addWidget(ch2_reset_btn)
        layout.addLayout(col3)

        col4 = QVBoxLayout()
        reset_all_btn = QPushButton("Reset All Positions")
        reset_all_btn.setFixedHeight(32)
        reset_all_btn.setStyleSheet(
            "QPushButton { background:#1e293b; color:#94a3b8; border:1px solid #334155; border-radius:4px; font-size:12px; }"
            "QPushButton:hover { background:#334155; color:#f1f5f9; }"
        )
        reset_all_btn.clicked.connect(self._reset_all_positions)
        col4.addWidget(reset_all_btn)
        info = QLabel("Vertical position is visual only. Measurements are never affected.")
        info.setStyleSheet("color:#64748b; font-size:10px;")
        info.setWordWrap(True)
        col4.addWidget(info)
        layout.addLayout(col4)

        self.controls_tab.addTab(tab, "Vertical")

    def setup_parameters_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Resistance (R) - Ω:"))
        self.slider_R = QSlider(Qt.Orientation.Horizontal)
        self.slider_R.setRange(10, 1000)
        self.slider_R.setValue(100)
        self.slider_R.valueChanged.connect(self.on_param_changed)
        col1.addWidget(self.slider_R)
        self.lbl_R = QLabel("1000 Ω")
        self.lbl_R.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col1.addWidget(self.lbl_R)
        layout.addLayout(col1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Capacitance (C) - μF:"))
        self.slider_C = QSlider(Qt.Orientation.Horizontal)
        self.slider_C.setRange(1, 100)
        self.slider_C.setValue(10)
        self.slider_C.valueChanged.connect(self.on_param_changed)
        col2.addWidget(self.slider_C)
        self.lbl_C = QLabel("10 μF")
        self.lbl_C.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col2.addWidget(self.lbl_C)
        layout.addLayout(col2)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Inductance (L) - mH:"))
        self.slider_L = QSlider(Qt.Orientation.Horizontal)
        self.slider_L.setRange(1, 100)
        self.slider_L.setValue(10)
        self.slider_L.valueChanged.connect(self.on_param_changed)
        col3.addWidget(self.slider_L)
        self.lbl_L = QLabel("10 mH")
        self.lbl_L.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col3.addWidget(self.lbl_L)
        layout.addLayout(col3)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Load Resistance (RL) - Ω:"))
        self.slider_Load = QSlider(Qt.Orientation.Horizontal)
        self.slider_Load.setRange(10, 1000)
        self.slider_Load.setValue(200)
        self.slider_Load.valueChanged.connect(self.on_param_changed)
        col4.addWidget(self.slider_Load)
        self.lbl_Load = QLabel("10000 Ω")
        self.lbl_Load.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col4.addWidget(self.lbl_Load)
        layout.addLayout(col4)

        col5 = QVBoxLayout()
        col5.addWidget(QLabel("Supply Voltage (Vcc) - V:"))
        self.slider_Vcc = QSlider(Qt.Orientation.Horizontal)
        self.slider_Vcc.setRange(10, 150)
        self.slider_Vcc.setValue(50)
        self.slider_Vcc.valueChanged.connect(self.on_param_changed)
        col5.addWidget(self.slider_Vcc)
        self.lbl_Vcc = QLabel("5.0 V")
        self.lbl_Vcc.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col5.addWidget(self.lbl_Vcc)
        layout.addLayout(col5)

        col6 = QVBoxLayout()
        col6.addWidget(QLabel("Duty Cycle - %:"))
        self.slider_Duty = QSlider(Qt.Orientation.Horizontal)
        self.slider_Duty.setRange(5, 95)
        self.slider_Duty.setValue(50)
        self.slider_Duty.valueChanged.connect(self.on_param_changed)
        col6.addWidget(self.slider_Duty)
        self.lbl_Duty = QLabel("50 %")
        self.lbl_Duty.setStyleSheet("color: #06b6d4; font-weight: bold;")
        col6.addWidget(self.lbl_Duty)
        layout.addLayout(col6)

        self.controls_tab.addTab(tab, "Parameters")

    def on_param_changed(self):
        r_val = self.slider_R.value() * 10
        c_val = self.slider_C.value()
        l_val = self.slider_L.value()
        load_val = self.slider_Load.value() * 50
        vcc_val = self.slider_Vcc.value() / 10.0
        duty_val = self.slider_Duty.value()
        
        self.lbl_R.setText(f"{r_val} Ω")
        self.lbl_C.setText(f"{c_val} μF")
        self.lbl_L.setText(f"{l_val} mH")
        self.lbl_Load.setText(f"{load_val} Ω")
        self.lbl_Vcc.setText(f"{vcc_val:.1f} V")
        self.lbl_Duty.setText(f"{duty_val} %")
        
        self.param_R = float(r_val)
        self.param_C = float(c_val) / 1e6
        self.param_L = float(l_val) / 1000.0
        self.param_Load = float(load_val)
        self.param_Vcc = float(vcc_val)
        self.param_Duty = float(duty_val) / 100.0
        
        self.on_inputs_changed()

    def _on_ch1_pos_changed(self, value):
        """CH1 slider moved — update only CH1 position. CH2 is never touched."""
        ch1_pos = value / 10.0   # integer ticks → float divisions
        self.ch1_pos_label.setText(f"{ch1_pos:+.1f} div")
        self.display_screen.set_ch1_position(ch1_pos)   # ONLY CH1 written

    def _on_ch2_pos_changed(self, value):
        """CH2 slider moved — update only CH2 position. CH1 is never touched."""
        ch2_pos = value / 10.0
        self.ch2_pos_label.setText(f"{ch2_pos:+.1f} div")
        self.display_screen.set_ch2_position(ch2_pos)   # ONLY CH2 written

    def _reset_all_positions(self):
        """Reset both channel positions to centre (0 div) independently."""
        # Block signals so each setValue fires its dedicated handler silently
        self.ch1_pos_slider.blockSignals(True)
        self.ch2_pos_slider.blockSignals(True)
        self.ch1_pos_slider.setValue(0)
        self.ch2_pos_slider.setValue(0)
        self.ch1_pos_slider.blockSignals(False)
        self.ch2_pos_slider.blockSignals(False)
        # Update labels
        self.ch1_pos_label.setText("0.0 div")
        self.ch2_pos_label.setText("0.0 div")
        # Write each channel separately — never a shared call
        self.display_screen.set_ch1_position(0.0)
        self.display_screen.set_ch2_position(0.0)

    def setup_toolbar(self):
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #0f172a; border-radius: 6px; padding: 4px;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(5, 5, 5, 5)
        tb_layout.setSpacing(6)

        # Zoom In / Out / Reset
        self.btn_zin = QPushButton()
        self.btn_zin.setIcon(qta.icon("fa5s.search-plus", color="#94a3b8"))
        self.btn_zin.setFixedSize(30, 30)
        self.btn_zin.clicked.connect(lambda: self.scale_timebase(0.8))
        
        self.btn_zout = QPushButton()
        self.btn_zout.setIcon(qta.icon("fa5s.search-minus", color="#94a3b8"))
        self.btn_zout.setFixedSize(30, 30)
        self.btn_zout.clicked.connect(lambda: self.scale_timebase(1.25))
        
        self.btn_zreset = QPushButton()
        self.btn_zreset.setIcon(qta.icon("fa5s.compress", color="#94a3b8"))
        self.btn_zreset.setFixedSize(30, 30)
        self.btn_zreset.clicked.connect(self.reset_zoom_scales)
        
        # Cursors toggle
        self.btn_cursor = QPushButton()
        self.btn_cursor.setIcon(qta.icon("fa5s.arrows-alt", color="#94a3b8"))
        self.btn_cursor.setFixedSize(30, 30)
        self.btn_cursor.setCheckable(True)
        self.btn_cursor.toggled.connect(self.toggle_cursors)

        self.btn_auto = QPushButton("Auto Scale")
        self.btn_auto.setIcon(qta.icon("fa5s.sync", color="#ffffff"))
        self.btn_auto.setStyleSheet("background-color: #3b82f6; border: none; border-radius: 4px; padding: 5px; font-weight: bold;")
        self.btn_auto.clicked.connect(self.auto_scale_waveform)

        # Dropdown selection for active circuit mode
        tb_layout.addWidget(self.btn_zin)
        tb_layout.addWidget(self.btn_zout)
        tb_layout.addWidget(self.btn_zreset)
        tb_layout.addWidget(self.btn_cursor)
        tb_layout.addWidget(self.btn_auto)

        tb_layout.addWidget(QLabel("Circuit:"))
        self.circuit_combo = QComboBox()
        self.circuit_combo.addItems([
            "Standalone Oscilloscope",
            "Signal Generator",
            "Voltage Divider",
            "RC Charging",
            "RC Discharging",
            "RL Transient",
            "Low Pass Filter",
            "High Pass Filter",
            "Half Wave Rectifier",
            "Full Wave Rectifier",
            "Positive Clipper",
            "Negative Clipper",
            "Positive Clamper",
            "Negative Clamper",
            "Signal Attenuator",
            "Amplitude Modulation",
            "Frequency Modulation",
            "ASK",
            "FSK",
            "PSK",
            "BPSK",
            "QPSK",
            "RLC Resonance"
        ])
        self.circuit_combo.currentTextChanged.connect(self.on_circuit_override)
        tb_layout.addWidget(self.circuit_combo)

        #动态LED连接标识
        self.lbl_connected_status = QLabel("● Standalone Mode")
        self.lbl_connected_status.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 9pt;")
        tb_layout.addWidget(self.lbl_connected_status)

        tb_layout.addStretch()

        # RUN, PAUSE, STOP switches
        self.btn_run = QPushButton()
        self.btn_run.setToolTip("RUN sweep acquisition")
        self.btn_run.setIcon(qta.icon("fa5s.play", color="#ffffff"))
        self.btn_run.setStyleSheet("background-color: #10b981; border: none; border-radius: 4px; padding: 4px;")
        self.btn_run.setFixedSize(30, 30)
        self.btn_run.clicked.connect(self.start_oscilloscope)
        
        self.btn_pause = QPushButton()
        self.btn_pause.setToolTip("PAUSE sweep trace")
        self.btn_pause.setIcon(qta.icon("fa5s.pause", color="#ffffff"))
        self.btn_pause.setStyleSheet("background-color: #f59e0b; border: none; border-radius: 4px; padding: 4px;")
        self.btn_pause.setFixedSize(30, 30)
        self.btn_pause.clicked.connect(self.pause_oscilloscope)
        
        self.btn_stop = QPushButton()
        self.btn_stop.setToolTip("STOP & FREEZE sweep buffer")
        self.btn_stop.setIcon(qta.icon("fa5s.stop", color="#ffffff"))
        self.btn_stop.setStyleSheet("background-color: #ef4444; border: none; border-radius: 4px; padding: 4px;")
        self.btn_stop.setFixedSize(30, 30)
        self.btn_stop.clicked.connect(self.stop_oscilloscope)

        self.btn_clear = QPushButton()
        self.btn_clear.setToolTip("CLEAR display & measurements")
        self.btn_clear.setIcon(qta.icon("fa5s.trash-alt", color="#ffffff"))
        self.btn_clear.setStyleSheet("background-color: #475569; border: none; border-radius: 4px; padding: 4px;")
        self.btn_clear.setFixedSize(30, 30)
        self.btn_clear.clicked.connect(self.clear_oscilloscope)

        # Capture exports
        self.btn_shot = QPushButton()
        self.btn_shot.setIcon(qta.icon("fa5s.camera", color="#94a3b8"))
        self.btn_shot.setFixedSize(30, 30)
        self.btn_shot.clicked.connect(self.export_screenshot)
        
        self.btn_csv = QPushButton()
        self.btn_csv.setIcon(qta.icon("fa5s.file-csv", color="#94a3b8"))
        self.btn_csv.setFixedSize(30, 30)
        self.btn_csv.clicked.connect(self.export_csv_data)

        tb_layout.addWidget(self.btn_run)
        tb_layout.addWidget(self.btn_pause)
        tb_layout.addWidget(self.btn_stop)
        tb_layout.addWidget(self.btn_clear)
        tb_layout.addWidget(self.btn_shot)
        tb_layout.addWidget(self.btn_csv)

        self.crt_layout.addWidget(toolbar)

    def setup_measurements_bottom(self):
        self.meas_card = QFrame()
        self.meas_card.setFixedHeight(120)
        self.meas_card.setStyleSheet("background-color: #0f172a; border-radius: 8px; border: 1px solid #1e293b;")
        meas_layout = QHBoxLayout(self.meas_card)
        meas_layout.setContentsMargins(10, 6, 10, 6)
        
        # CH1 measurements (Yellow theme)
        ch1_box = QGroupBox("CH1 Measurements")
        ch1_box.setStyleSheet("QGroupBox { color: #eab308; font-weight: bold; border: 1px solid rgba(234, 179, 8, 0.2); border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }")
        ch1_layout = QGridLayout(ch1_box)
        ch1_layout.setContentsMargins(6, 10, 6, 6)
        ch1_layout.setSpacing(4)
        
        self.ch1_lbls = {}
        ch1_metrics = [
            ("Freq", "Freq:", 0, 0), ("Period", "Period:", 0, 1), ("Vpp", "Vpp:", 0, 2), ("Vmax", "Vmax:", 0, 3),
            ("Vmin", "Vmin:", 1, 0), ("Vrms", "Vrms:", 1, 1), ("Avg", "Avg:", 1, 2), ("Duty", "Duty:", 1, 3),
            ("Rise", "Rise:", 2, 0), ("Fall", "Fall:", 2, 1)
        ]
        for key, text, r, c in ch1_metrics:
            ch1_layout.addWidget(QLabel(text), r, c * 2)
            lbl = QLabel("---")
            lbl.setStyleSheet("color: #eab308; font-weight: bold; font-family: Consolas;")
            ch1_layout.addWidget(lbl, r, c * 2 + 1)
            self.ch1_lbls[key] = lbl
            
        meas_layout.addWidget(ch1_box)

        # CH2 measurements (Cyan theme)
        ch2_box = QGroupBox("CH2 Measurements")
        ch2_box.setStyleSheet("QGroupBox { color: #06b6d4; font-weight: bold; border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }")
        ch2_layout = QGridLayout(ch2_box)
        ch2_layout.setContentsMargins(6, 10, 6, 6)
        ch2_layout.setSpacing(4)
        
        self.ch2_lbls = {}
        ch2_metrics = [
            ("Freq", "Freq:", 0, 0), ("Period", "Period:", 0, 1), ("Vpp", "Vpp:", 0, 2), ("Vmax", "Vmax:", 0, 3),
            ("Vmin", "Vmin:", 1, 0), ("Vrms", "Vrms:", 1, 1), ("Avg", "Avg:", 1, 2), ("Duty", "Duty:", 1, 3),
            ("Rise", "Rise:", 2, 0), ("Fall", "Fall:", 2, 1)
        ]
        for key, text, r, c in ch2_metrics:
            ch2_layout.addWidget(QLabel(text), r, c * 2)
            lbl = QLabel("---")
            lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-family: Consolas;")
            ch2_layout.addWidget(lbl, r, c * 2 + 1)
            self.ch2_lbls[key] = lbl
            
        meas_layout.addWidget(ch2_box)

        # Delta Cursor Card (embedded inside bottom area)
        self.cursor_card = QFrame()
        self.cursor_card.setFixedWidth(200)
        self.cursor_card.setStyleSheet("background-color: rgba(30, 41, 59, 0.3); border-radius: 6px; padding: 6px;")
        cc_layout = QVBoxLayout(self.cursor_card)
        cc_layout.setSpacing(4)
        cc_layout.addWidget(QLabel("Cursor Deltas & Phase:"))
        
        self.lbl_delta_t = QLabel("ΔT: ---")
        self.lbl_delta_t.setStyleSheet("font-family: Consolas; font-size: 8.5pt; color: #06b6d4;")
        self.lbl_delta_v = QLabel("ΔV: ---")
        self.lbl_delta_v.setStyleSheet("font-family: Consolas; font-size: 8.5pt; color: #a855f7;")
        self.lbl_phase_diff = QLabel("Phase Diff: ---")
        self.lbl_phase_diff.setStyleSheet("font-family: Consolas; font-size: 8.5pt; color: #10b981;")
        
        cc_layout.addWidget(self.lbl_delta_t)
        cc_layout.addWidget(self.lbl_delta_v)
        cc_layout.addWidget(self.lbl_phase_diff)
        self.cursor_card.setVisible(False)
        meas_layout.addWidget(self.cursor_card)

        self.crt_layout.addWidget(self.meas_card)

    def setup_status_bar(self):
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("background-color: #020617; border-top: 1px solid #1e293b;")
        sb_layout = QHBoxLayout(self.status_bar)
        sb_layout.setContentsMargins(10, 0, 10, 0)
        
        self.status_led = QLabel("● RUN")
        self.status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8pt;")
        
        self.status_fps = QLabel("FPS: 60")
        self.status_fps.setStyleSheet("color: #94a3b8; font-size: 8pt; font-family: Consolas;")
        
        self.status_samples = QLabel("Samples: 1000")
        self.status_samples.setStyleSheet("color: #94a3b8; font-size: 8pt;")
        
        self.status_trig = QLabel("Trig: Locked")
        self.status_trig.setStyleSheet("color: #f59e0b; font-size: 8pt;")
        
        self.status_scale = QLabel("T: 1.0ms/div | CH1: 1V/div | CH2: 1V/div")
        self.status_scale.setStyleSheet("color: #06b6d4; font-size: 8pt; font-family: Consolas;")
        
        sb_layout.addWidget(self.status_led)
        sb_layout.addSpacing(15)
        sb_layout.addWidget(self.status_fps)
        sb_layout.addSpacing(15)
        sb_layout.addWidget(self.status_samples)
        sb_layout.addSpacing(15)
        sb_layout.addWidget(self.status_trig)
        sb_layout.addStretch()
        sb_layout.addWidget(self.status_scale)
        
        self.crt_layout.addWidget(self.status_bar)

    def start_oscilloscope(self):
        """RUN: Resume continuous live acquisition."""
        self.is_running = True
        self.status_led.setText("RUN")
        self.status_led.setStyleSheet("color: #10b981; font-weight: bold; font-size: 8pt;")

    def pause_oscilloscope(self):
        """PAUSE: Freeze the current waveform display without clearing it."""
        self.is_running = False
        self.status_led.setText("PAUSE")
        self.status_led.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 8pt;")

    def stop_oscilloscope(self):
        """STOP: Freeze waveform at current capture (Single capture mode)."""
        self.is_running = False
        self.status_led.setText("STOP")
        self.status_led.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8pt;")
        # Do NOT clear points — STOP freezes the current waveform
        self.show_toast("DSO stopped. Waveform frozen. Press RUN to resume.")

    def clear_oscilloscope(self):
        """CLEAR: Reset display and measurements. Does NOT stop acquisition."""
        self.sim_time = 0.0
        self.t_points = np.array([])
        self.ch1_points = np.array([])
        self.ch2_points = np.array([])
        # Reset change-detection history so auto-scale re-fires on next frame
        for attr in ['last_v1_pp', 'last_v2_pp', 'last_v1_avg', 'last_v2_avg', 'last_p_detected', 'last_circuit']:
            if hasattr(self, attr):
                delattr(self, attr)
        if hasattr(self, 'display_screen'):
            self.display_screen.set_waveforms(self.t_points, self.ch1_points, self.ch2_points, self.ch1_en, self.ch2_en)
        self.calculate_realtime_metrics()
        self.show_toast("DSO display cleared. Acquisition will restart on next RUN.")

    def on_circuit_override(self):
        new_circuit = self.circuit_combo.currentText()
        # Signal Generator uses only CH1
        one_channel_circuits = ["Signal Generator"]
        if new_circuit in one_channel_circuits:
            self.ch1_en_chk.setChecked(True)
            self.ch1_en_chk.setEnabled(True)
            self.ch2_en_chk.setChecked(False)
            self.ch2_en_chk.setEnabled(False)
        else:
            self.ch1_en_chk.setChecked(True)
            self.ch1_en_chk.setEnabled(True)
            self.ch2_en_chk.setChecked(True)
            self.ch2_en_chk.setEnabled(True)

        if new_circuit == "Standalone Oscilloscope":
            self.transition_to_standalone()
        else:
            self.transition_to_connected(new_circuit)

    def transition_to_standalone(self):
        log.info("DSO: Switching to Standalone Mode")
        self.manual_override = True
        
        # Clear all waveform buffers
        self.t_points = np.array([])
        self.ch1_points = np.array([])
        self.ch2_points = np.array([])
        if hasattr(self, 'display_screen'):
            self.display_screen.set_waveforms(self.t_points, self.ch1_points, self.ch2_points, self.ch1_en, self.ch2_en)
            
        # Reset trigger state
        self.trig_level_slider.setValue(0)
        self.trig_src_combo.setCurrentText("CH1")
        self.trig_edge_combo.setCurrentText("Rising")
        self.trig_mode_combo.setCurrentText("Auto")
        
        # Reset channel history (used by parameter change detection)
        if hasattr(self, 'last_v1_pp'): delattr(self, 'last_v1_pp')
        if hasattr(self, 'last_v2_pp'): delattr(self, 'last_v2_pp')
        if hasattr(self, 'last_v1_avg'): delattr(self, 'last_v1_avg')
        if hasattr(self, 'last_v2_avg'): delattr(self, 'last_v2_avg')
        if hasattr(self, 'last_p_detected'): delattr(self, 'last_p_detected')

        # Disconnect references to the previous simulation
        self.last_circuit = "Standalone Oscilloscope"
        
        # Enable all waveform generator controls and apply changes
        self.update_generator_controls_state()
        self.on_inputs_changed()

    def transition_to_connected(self, circuit_name):
        log.info(f"DSO: Switching to Connected Circuit Mode ({circuit_name})")
        self.manual_override = True
        
        # Clear old buffers
        self.t_points = np.array([])
        self.ch1_points = np.array([])
        self.ch2_points = np.array([])
        if hasattr(self, 'display_screen'):
            self.display_screen.set_waveforms(self.t_points, self.ch1_points, self.ch2_points, self.ch1_en, self.ch2_en)

        # Reset channel history
        if hasattr(self, 'last_v1_pp'): delattr(self, 'last_v1_pp')
        if hasattr(self, 'last_v2_pp'): delattr(self, 'last_v2_pp')
        if hasattr(self, 'last_v1_avg'): delattr(self, 'last_v1_avg')
        if hasattr(self, 'last_v2_avg'): delattr(self, 'last_v2_avg')
        if hasattr(self, 'last_p_detected'): delattr(self, 'last_p_detected')

        # Immediately snap timebase to the correct preset for the circuit type.
        # This ensures the very first rendered frame already has the right time scale.
        ac_circuits = {
            "Positive Clipper", "Negative Clipper",
            "Signal Attenuation",
            "Half Wave Rectifier", "Full Wave Rectifier",
            "Voltage Divider",
        }
        freq_circuits = {
            "Low Pass Filter", "High Pass Filter",
        }
        if circuit_name in ac_circuits:
            # All these circuits run at 100 Hz → period 10 ms → 10 ms/div shows 10 full cycles
            self.tbase_smooth = 0.010
            self.tbase_target = 0.010
        elif circuit_name in freq_circuits:
            # Filters/resonance run around 1000 Hz → period 1 ms → 1 ms/div shows 10 full cycles
            self.tbase_smooth = 0.001
            self.tbase_target = 0.001

        # Connect to the selected simulation module by clearing last_circuit so that auto-scale triggers
        self.last_circuit = None
        
        # Disable generator controls
        self.update_generator_controls_state()
        self.on_inputs_changed()

    def auto_scale_waveform(self):
        """Forces the timebase and voltage scales of both channels to automatically
        adjust so that the waveforms are perfectly fitted on the screen.
        """
        # Snap time base
        # Look at the active frequencies to select a suitable time base
        f_max = max(self.ch1_freq if self.ch1_en else 1.0, self.ch2_freq if self.ch2_en else 1.0)
        t_period = 1.0 / f_max if f_max > 0 else 0.001
        # We want to fit ~2 periods across 10 divisions, so timebase ~ t_period / 5
        target_tb = t_period / 5.0
        
        tb_values = [1e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 0.1, 0.2, 0.5, 1.0, 2.0]
        tb_names = [
            "100 μs", "500 μs", "1 ms", "2 ms", "5 ms", "10 ms", "20 ms", "50 ms", "100 ms",
            "200 ms", "500 ms", "1 s", "2 s"
        ]
        tb_idx = np.argmin(np.abs(np.array(tb_values) - target_tb))
        self.tbase_combo.setCurrentText(tb_names[tb_idx])
        
        # Snap CH1 scale
        if self.ch1_en and len(self.ch1_points) > 0:
            v_max = np.max(self.ch1_points)
            v_min = np.min(self.ch1_points)
            v_pp = v_max - v_min
            # We want v_pp to occupy 5 divisions, so vscale ~ v_pp / 5
            target_vs = max(0.01, v_pp / 5.0)
            vs_values = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
            vs_names = ["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"]
            vs_idx = np.argmin(np.abs(np.array(vs_values) - target_vs))
            self.ch1_vscale_combo.setCurrentText(vs_names[vs_idx])
            
            # Snap offset to center of waveform
            avg = (v_max + v_min) / 2.0
            self.ch1_offset_inp.setText(f"{avg:.2f}")
            self.display_screen.ch1.set_vertical_position(0.0)
            
        # Snap CH2 scale
        if self.ch2_en and len(self.ch2_points) > 0:
            v_max = np.max(self.ch2_points)
            v_min = np.min(self.ch2_points)
            v_pp = v_max - v_min
            target_vs = max(0.01, v_pp / 5.0)
            vs_values = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
            vs_names = ["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"]
            vs_idx = np.argmin(np.abs(np.array(vs_values) - target_vs))
            self.ch2_vscale_combo.setCurrentText(vs_names[vs_idx])
            
            avg = (v_max + v_min) / 2.0
            self.ch2_offset_inp.setText(f"{avg:.2f}")
            self.display_screen.ch2.set_vertical_position(0.0)
            
        self.trig_level_slider.setValue(0)
        self.on_inputs_changed()
        self.show_toast("Auto Scale executed: Waveforms scaled to fit display.")

    # Replaced by dynamic auto-scale pipeline

    def reset_zoom_scales(self):
        self.tbase_combo.setCurrentText("50 ms")
        self.ch1_vscale_combo.setCurrentText("2 V")
        self.ch2_vscale_combo.setCurrentText("1 V")
        self.display_screen.ch1_offset = 0.0
        self.display_screen.ch2_offset = 0.0
        self.on_inputs_changed()

    def scale_timebase(self, factor):
        tb_val = self.get_timebase_value() * factor
        tb_options = [
            0.0001, 0.0005, 0.001, 0.002, 0.005, 0.010, 0.020, 0.050, 0.100,
            0.200, 0.500, 1.000, 2.000
        ]
        closest_idx = np.argmin(np.abs(np.array(tb_options) - tb_val))
        tb_names = [
            "100 μs", "500 μs", "1 ms", "2 ms", "5 ms", "10 ms", "20 ms", "50 ms", "100 ms",
            "200 ms", "500 ms", "1 s", "2 s"
        ]
        self.tbase_combo.blockSignals(True)
        self.tbase_combo.setCurrentText(tb_names[closest_idx])
        self.tbase_combo.blockSignals(False)
        self.on_inputs_changed()

    def scale_volts(self, factor):
        if self.ch1_en:
            v_val = self.get_ch1_vscale_value() * factor
            v_options = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
            closest_idx = np.argmin(np.abs(np.array(v_options) - v_val))
            v_names = ["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"]
            self.ch1_vscale_combo.blockSignals(True)
            self.ch1_vscale_combo.setCurrentText(v_names[closest_idx])
            self.ch1_vscale_combo.blockSignals(False)
        if self.ch2_en:
            v_val = self.get_ch2_vscale_value() * factor
            v_options = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
            closest_idx = np.argmin(np.abs(np.array(v_options) - v_val))
            v_names = ["100 mV", "200 mV", "500 mV", "1 V", "2 V", "5 V", "10 V"]
            self.ch2_vscale_combo.blockSignals(True)
            self.ch2_vscale_combo.setCurrentText(v_names[closest_idx])
            self.ch2_vscale_combo.blockSignals(False)
        self.on_inputs_changed()

    def toggle_cursors(self, enabled):
        self.display_screen.cursors_enabled = enabled
        self.cursor_card.setVisible(enabled)
        self.update_cursor_calculations()
        self.display_screen.update()

    def sync_offset_inputs(self, offset1, offset2):
        self.ch1_offset_inp.blockSignals(True)
        self.ch1_offset_inp.setText(f"{offset1:.2f}")
        self.ch1_offset_inp.blockSignals(False)
        
        self.ch2_offset_inp.blockSignals(True)
        self.ch2_offset_inp.setText(f"{offset2:.2f}")
        self.ch2_offset_inp.blockSignals(False)
        
        self.ch1_offset = offset1
        self.ch2_offset = offset2
        self.calculate_realtime_metrics()

    def get_timebase_value(self):
        text = self.tbase_combo.currentText()
        if "μs" in text:
            return float(text.replace(" μs", "")) * 1e-6
        elif "ms" in text:
            return float(text.replace(" ms", "")) * 1e-3
        elif "s" in text:
            return float(text.replace(" s", "")) * 1.0
        else:
            return 1.0

    def get_ch1_vscale_value(self):
        text = self.ch1_vscale_combo.currentText()
        if "mV" in text:
            return float(text.replace(" mV", "")) * 1e-3
        elif "V" in text:
            return float(text.replace(" V", "")) * 1.0
        else:
            return 1.0

    def get_ch2_vscale_value(self):
        text = self.ch2_vscale_combo.currentText()
        if "mV" in text:
            return float(text.replace(" mV", "")) * 1e-3
        elif "V" in text:
            return float(text.replace(" V", "")) * 1.0
        else:
            return 1.0

    def on_inputs_changed(self):
        self.ch1_en = self.ch1_en_chk.isChecked()
        self.ch2_en = self.ch2_en_chk.isChecked()
        
        self.ch1_type = self.ch1_type_combo.currentText()
        self.ch2_type = self.ch2_type_combo.currentText()
        
        try:
            self.ch1_freq = float(self.ch1_freq_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch1_amp = float(self.ch1_amp_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch1_offset = float(self.ch1_offset_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch1_phase = float(self.ch1_phase_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch2_freq = float(self.ch2_freq_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch2_amp = float(self.ch2_amp_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch2_offset = float(self.ch2_offset_inp.text())
        except ValueError:
            pass
            
        try:
            self.ch2_phase = float(self.ch2_phase_inp.text())
        except ValueError:
            pass

        self.noise_lvl = self.noise_slider.value() / 100.0

        t_base = self.get_timebase_value()
        v1_scale = self.get_ch1_vscale_value()
        v2_scale = self.get_ch2_vscale_value()

        self.tbase_target = t_base
        self.ch1_vscale_target = v1_scale
        self.ch2_vscale_target = v2_scale
        self.ch1_offset_target = self.ch1_offset
        self.ch2_offset_target = self.ch2_offset

        self.generate_and_process_waveforms()

    def get_simulation_view(self):
        """Safely lookup the SimulationView instance in MainWindow views."""
        top_window = self.window()
        if not top_window:
            return None
        if hasattr(top_window, "views"):
            for view in top_window.views:
                if view.__class__.__name__ == "SimulationView":
                    return view
        return None

    def get_active_simulation_widget(self):
        """Helper to safely lookup the current Simulation Lab simulation widget."""
        sim_view = self.get_simulation_view()
        if not sim_view or not hasattr(sim_view, "right_stack"):
            return None
        return sim_view.right_stack.currentWidget()

    def get_connected_simulation_widget(self):
        """Returns the active math simulation engine object for the selected circuit."""
        selected_circuit = self.circuit_combo.currentText()
        # Always prefer math_sims (new engine)
        if selected_circuit in self.math_sims:
            return self.math_sims[selected_circuit]
        return None

    def sync_math_sim_params(self, sim):
        """Push current DSO UI parameter values into the simulation engine object."""
        sim.update_parameters(
            freq=self.ch1_freq, amp=self.ch1_amp, offset=self.ch1_offset,
            phase=self.ch1_phase, noise_lvl=self.noise_lvl, duty=self.param_Duty,
            ch1_type=self.ch1_type, ch2_type=self.ch2_type,
            ch1_freq=self.ch1_freq, ch2_freq=self.ch2_freq,
            ch1_amp=self.ch1_amp, ch2_amp=self.ch2_amp,
            ch1_offset=self.ch1_offset, ch2_offset=self.ch2_offset,
            ch1_phase=self.ch1_phase, ch2_phase=self.ch2_phase,
            param_R=self.param_R, param_C=self.param_C,
            param_L=self.param_L, param_Load=self.param_Load,
            param_Vcc=self.param_Vcc
        )

    def detect_and_sync_active_circuit(self):
        """No-op: auto-detect of Simulation Lab is disabled in engine mode.
        All circuits are now driven by math_sims directly from the DSO dropdown.
        """
        pass

    def get_connected_simulation_freq(self, selected_circuit):
        """Returns the primary frequency of the active simulation for time-base calculation."""
        sim = self.get_connected_simulation_widget()
        if sim is None:
            return None
        info = sim.get_channel_info()
        tdiv = info.get("recommended_tdiv")
        if tdiv and tdiv > 0:
            return 0.25 / tdiv  # freq = 1 cycle / (4 * tdiv)
        return None

    def generate_and_process_waveforms(self):
        # Detect if circuit changed
        current_circuit = self.circuit_combo.currentText()
        circuit_changed = False
        if not hasattr(self, 'last_circuit') or self.last_circuit != current_circuit:
            circuit_changed = True
            self.last_circuit = current_circuit

        # Use smooth timebase to generate display time buffer
        t_span = 10.0 * self.tbase_smooth
        n_samples = 1000
        t_buffer = np.linspace(self.sim_time, self.sim_time + t_span, n_samples)

        ch1_raw = None
        ch2_raw = None
        ch1_label_val = "CH1"
        ch2_label_val = "CH2"
        sim_recommended_v1_scale = None
        sim_recommended_v2_scale = None
        sim_recommended_tbase = None

        # ------------------------------------------------------------------
        # 1. Query the math simulation engine (new decoupled architecture)
        # ------------------------------------------------------------------
        sim_engine = self.get_connected_simulation_widget()
        if sim_engine is not None:
            try:
                # Push all current UI parameters into the engine
                self.sync_math_sim_params(sim_engine)
                # Generate both channels
                ch1_raw, ch2_raw = sim_engine.generate(t_buffer)
                # Read channel metadata
                info = sim_engine.get_channel_info()
                ch1_label_val = info.get("ch1_label", "CH1")
                ch2_label_val = info.get("ch2_label", "CH2")
                sim_recommended_v1_scale = info.get("recommended_vdiv")
                sim_recommended_v2_scale = info.get("recommended_vdiv_ch2", info.get("recommended_vdiv"))
                sim_recommended_tbase = info.get("recommended_tdiv")
                # Hide CH2 if the simulation only produces CH1
                if not info.get("ch2_enabled", True):
                    self.ch2_en_chk.setChecked(False)
                self.lbl_connected_status.setText(f"● Connected: {current_circuit}")
                self.lbl_connected_status.setStyleSheet("color: #10b981; font-weight: bold; font-size: 9pt;")
            except Exception as e:
                log.error(f"DSO engine error for '{current_circuit}': {e}")
                ch1_raw = None
                ch2_raw = None
                self.lbl_connected_status.setText("⚠ Waveform unavailable")
                self.lbl_connected_status.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 9pt;")

        # ------------------------------------------------------------------
        # 2. Fall back to Standalone Oscilloscope Mode (Fully isolated)
        # ------------------------------------------------------------------
        if ch1_raw is None or ch2_raw is None:
            self.lbl_connected_status.setText("● Standalone Mode")
            self.lbl_connected_status.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 9pt;")
            from src.engine.simulation_engine import StandaloneSignalGenerator as _SSG
            ch1_raw = _SSG.generate(t_buffer, self.ch1_type, self.ch1_freq, self.ch1_amp, self.ch1_offset, self.ch1_phase, self.noise_lvl, self.param_Duty)
            ch2_raw = _SSG.generate(t_buffer, self.ch2_type, self.ch2_freq, self.ch2_amp, self.ch2_offset, self.ch2_phase, self.noise_lvl, self.param_Duty)

        # Update trace labels on screen
        self.display_screen.ch1.label = ch1_label_val
        self.display_screen.ch2.label = ch2_label_val

        # ------------------------------------------------------------------
        # 3. Dynamic Auto Scale Target Calculations (Runs before trigger slice)
        # ------------------------------------------------------------------
        p_detected = None
        is_transient = current_circuit in ("RC Charging", "RC Discharging", "RL Transient")

        # A. Horizontal Timebase target (Time/Div)
        if sim_recommended_tbase is not None and sim_recommended_tbase > 0:
            # Engine recommends a tdiv — use it directly
            tbase_target = sim_recommended_tbase
        else:
            # Fallback: waveform analysis then generator frequency
            p1 = self._estimate_period_raw(ch1_raw, t_buffer) if ch1_raw is not None else None
            p2 = self._estimate_period_raw(ch2_raw, t_buffer) if ch2_raw is not None else None
            p_detected = p1 if p1 is not None else p2
            if p_detected is not None:
                if "Half Wave Rectifier" in current_circuit:
                    tbase_target = p_detected * 0.5
                elif "Full Wave Rectifier" in current_circuit:
                    tbase_target = p_detected * 0.25
                else:
                    tbase_target = p_detected * 1.0
            else:
                f_ref = max(self.ch1_freq if self.ch1_en else 0.0, self.ch2_freq if self.ch2_en else 0.0, 1.0)
                tbase_target = 1.0 / f_ref

        tbase_target = max(0.0001, min(2.0, tbase_target))

        # B. Combined Vertical Volts/Div & DC Offset targets
        v1_min = np.min(ch1_raw) if ch1_raw is not None and len(ch1_raw) > 0 else 0.0
        v1_max = np.max(ch1_raw) if ch1_raw is not None and len(ch1_raw) > 0 else 0.0
        v2_min = np.min(ch2_raw) if ch2_raw is not None and len(ch2_raw) > 0 else 0.0
        v2_max = np.max(ch2_raw) if ch2_raw is not None and len(ch2_raw) > 0 else 0.0

        v_min_combined = min(v1_min, v2_min)
        v_max_combined = max(v1_max, v2_max)
        v_pp_combined = float(v_max_combined - v_min_combined)

        if sim_recommended_v1_scale is not None:
            v1_scale_target = sim_recommended_v1_scale
            v2_scale_target = sim_recommended_v2_scale if sim_recommended_v2_scale is not None else sim_recommended_v1_scale
            v1_offset_target = 0.0
            v2_offset_target = 0.0
            offset_target = 0.0
        else:
            # Volts/Div target: fit waveform into ~60% of display (4.8 of 8 divisions)
            v_scale_target = v_pp_combined / 4.8 if v_pp_combined > 1e-4 else 1.0
            v_scale_target = max(0.1, min(10.0, v_scale_target))
            offset_target = float(v_max_combined + v_min_combined) / 2.0
            v1_scale_target = v_scale_target
            v2_scale_target = v_scale_target
            v1_offset_target = offset_target
            v2_offset_target = offset_target

        # Automatically center the trigger level slider on circuit change
        if circuit_changed:
            self.trig_level_slider.blockSignals(True)
            self.trig_level_slider.setValue(int(offset_target * 10))
            self.trig_level_slider.blockSignals(False)

        # Check if parameters changed significantly (> 5% change)
        if not hasattr(self, 'last_v1_pp'):
            self.last_v1_pp = v_pp_combined
            self.last_v2_pp = v_pp_combined
            self.last_v1_avg = offset_target
            self.last_v2_avg = offset_target
            self.last_p_detected = p_detected

        param_changed = False
        v1_pp_current = float(v1_max - v1_min)
        v2_pp_current = float(v2_max - v2_min)
        v1_avg_current = float(v1_max + v1_min) / 2.0
        v2_avg_current = float(v2_max + v2_min) / 2.0

        if abs(v1_pp_current - self.last_v1_pp) > 0.05 * (self.last_v1_pp + 0.1): param_changed = True
        if abs(v2_pp_current - self.last_v2_pp) > 0.05 * (self.last_v2_pp + 0.1): param_changed = True
        if abs(v1_avg_current - self.last_v1_avg) > 0.05 * (abs(self.last_v1_avg) + 0.1): param_changed = True
        if abs(v2_avg_current - self.last_v2_avg) > 0.05 * (abs(self.last_v2_avg) + 0.1): param_changed = True
        if p_detected is not None and self.last_p_detected is not None:
            if abs(p_detected - self.last_p_detected) > 0.05 * self.last_p_detected: param_changed = True
        elif (p_detected is None) != (self.last_p_detected is None):
            param_changed = True

        self.last_v1_pp = v1_pp_current
        self.last_v2_pp = v2_pp_current
        self.last_v1_avg = v1_avg_current
        self.last_v2_avg = v2_avg_current
        self.last_p_detected = p_detected

        # C. Update smooth targets if circuit or parameters changed
        if circuit_changed or param_changed:
            tb_presets = [0.0001, 0.0005, 0.001, 0.002, 0.005, 0.010, 0.020, 0.050, 0.100, 0.200, 0.500, 1.000, 2.000]
            self.tbase_target = tb_presets[np.argmin(np.abs(np.array(tb_presets) - tbase_target))]
            v_presets = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
            self.ch1_vscale_target = v_presets[np.argmin(np.abs(np.array(v_presets) - v1_scale_target))]
            self.ch2_vscale_target = v_presets[np.argmin(np.abs(np.array(v_presets) - v2_scale_target))]
            self.ch1_offset_target = v1_offset_target
            self.ch2_offset_target = v2_offset_target

        # D. Exponential decay smoothing
        alpha = 1.0 if (circuit_changed or not hasattr(self, 'tbase_smooth')) else 0.15
        self.tbase_smooth += alpha * (self.tbase_target - self.tbase_smooth)
        self.ch1_vscale_smooth += alpha * (self.ch1_vscale_target - self.ch1_vscale_smooth)
        self.ch2_vscale_smooth += alpha * (self.ch2_vscale_target - self.ch2_vscale_smooth)
        self.ch1_offset_smooth += alpha * (self.ch1_offset_target - self.ch1_offset_smooth)
        self.ch2_offset_smooth += alpha * (self.ch2_offset_target - self.ch2_offset_smooth)

        # E. Keep combo boxes in sync visually
        tb_presets = [0.0001, 0.0005, 0.001, 0.002, 0.005, 0.010, 0.020, 0.050, 0.100, 0.200, 0.500, 1.000, 2.000]
        v_presets = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        self._sync_combo(self.tbase_combo, self.tbase_smooth, tb_presets)
        self._sync_combo(self.ch1_vscale_combo, self.ch1_vscale_smooth, v_presets)
        self._sync_combo(self.ch2_vscale_combo, self.ch2_vscale_smooth, v_presets)

        # ------------------------------------------------------------------
        # 4. Synchronized Trigger Edge Lock & Slice
        # ------------------------------------------------------------------
        trig_src = self.trig_src_combo.currentText()
        trig_edge = self.trig_edge_combo.currentText()
        trig_mode = self.trig_mode_combo.currentText()
        trig_level = self.trig_level_slider.value() / 10.0

        trig_target_buffer = ch1_raw if trig_src == "CH1" else ch2_raw
        trig_idx = -1
        search_end = int(n_samples * 0.70)
        for idx in range(1, search_end):
            if trig_edge == "Rising":
                if trig_target_buffer[idx - 1] <= trig_level < trig_target_buffer[idx]:
                    trig_idx = idx
                    break
            else:
                if trig_target_buffer[idx - 1] >= trig_level > trig_target_buffer[idx]:
                    trig_idx = idx
                    break

        if trig_idx != -1:
            pre_trig = int(n_samples * 0.12) if is_transient else int(n_samples * 0.20)
            slice_start = max(0, trig_idx - pre_trig)
            slice_end = min(n_samples, slice_start + n_samples)
            if slice_end - slice_start < n_samples:
                slice_start = max(0, slice_end - n_samples)

            self.t_points = t_buffer[slice_start:slice_end]
            self.ch1_points = ch1_raw[slice_start:slice_end]
            self.ch2_points = ch2_raw[slice_start:slice_end]
            self.status_trig.setText("Trig: Locked")
            self.status_trig.setStyleSheet("color: #10b981;")

            if trig_mode == "Single" and self.is_running:
                self.is_running = False
                self.status_led.setText("STOP")
                self.status_led.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 8pt;")
                self.show_toast("DSO single capture complete.")
        else:
            self.status_trig.setText("Trig: Scan...")
            self.status_trig.setStyleSheet("color: #ef4444;")

            if trig_mode == "Auto":
                self.t_points = t_buffer
                self.ch1_points = ch1_raw
                self.ch2_points = ch2_raw
            else:
                if not hasattr(self, 'ch1_points') or len(self.ch1_points) == 0:
                    self.t_points = t_buffer
                    self.ch1_points = ch1_raw
                    self.ch2_points = ch2_raw

        # Set display screen scale data
        self.display_screen.set_scales(
            time_base=self.tbase_smooth,
            ch1_vscale=self.ch1_vscale_smooth,
            ch2_vscale=self.ch2_vscale_smooth,
            ch1_offset=self.ch1_offset_smooth,
            ch2_offset=self.ch2_offset_smooth,
            trig_level=trig_level,
            trig_src=trig_src,
            trig_edge=trig_edge,
            trig_state=trig_mode
        )
        self.status_scale.setText(f"T: {self.tbase_combo.currentText()}/div | CH1: {self.ch1_vscale_combo.currentText()}/div | CH2: {self.ch2_vscale_combo.currentText()}/div")

        self.display_screen.set_waveforms(self.t_points, self.ch1_points, self.ch2_points, self.ch1_en, self.ch2_en)
        self.status_samples.setText(f"Samples: {len(self.t_points)}")
        self.fps_counter += 1
        self.calculate_realtime_metrics()
        self.update_generator_controls_state()

    def on_timer_tick(self):
        if not self.is_running:
            return
        if self.status_led.text() == "STOP":
            return

        self.sim_time += 0.033
        self.generate_and_process_waveforms()

    def _sync_combo(self, combo, value, presets):
        closest_idx = np.argmin(np.abs(np.array(presets) - value))
        combo.blockSignals(True)
        combo.setCurrentIndex(closest_idx)
        combo.blockSignals(False)

    def _estimate_period_raw(self, waveform, t_axis):
        if waveform is None or len(waveform) < 4:
            return None
        v_max = np.max(waveform)
        v_min = np.min(waveform)
        v_pp = v_max - v_min
        if v_pp < 1e-4:
            return None
        mid = (v_max + v_min) / 2.0
        crossings = []
        for k in range(1, len(waveform)):
            if waveform[k - 1] < mid <= waveform[k]:
                frac = (mid - waveform[k - 1]) / (waveform[k] - waveform[k - 1]) if (waveform[k] - waveform[k - 1]) > 0 else 0.0
                crossings.append(t_axis[k - 1] + frac * (t_axis[k] - t_axis[k - 1]))
        if len(crossings) < 2:
            return None
        return float(np.median(np.diff(crossings)))

    def update_generator_controls_state(self):
        is_standalone = (self.circuit_combo.currentText() == "Standalone Oscilloscope")
        
        # Enforce enabled/disabled state of signal generator controls
        self.ch1_type_combo.setEnabled(is_standalone)
        self.ch1_freq_inp.setEnabled(is_standalone)
        self.ch1_amp_inp.setEnabled(is_standalone)
        self.ch1_offset_inp.setEnabled(is_standalone)
        self.ch1_phase_inp.setEnabled(is_standalone)
        
        self.ch2_type_combo.setEnabled(is_standalone)
        self.ch2_freq_inp.setEnabled(is_standalone)
        self.ch2_amp_inp.setEnabled(is_standalone)
        self.ch2_offset_inp.setEnabled(is_standalone)
        self.ch2_phase_inp.setEnabled(is_standalone)

        # If connected to a circuit, sync the input text fields with the measured live metrics
        if not is_standalone:
            try:
                self.ch1_type_combo.blockSignals(True)
                self.ch2_type_combo.blockSignals(True)
                
                # Determine waveform type based on circuit
                circuit_name = self.circuit_combo.currentText()
                if "Rectifier" in circuit_name:
                    self.ch1_type_combo.setCurrentText("Sine")
                    self.ch2_type_combo.setCurrentText("Sine")
                elif "Clipper" in circuit_name:
                    self.ch1_type_combo.setCurrentText("Sine")
                    self.ch2_type_combo.setCurrentText("Sine")
                elif "RC Charging" in circuit_name or "RL Transient" in circuit_name:
                    self.ch1_type_combo.setCurrentText("Square")
                    self.ch2_type_combo.setCurrentText("Triangle")
                else:
                    self.ch1_type_combo.setCurrentText("Sine")
                    self.ch2_type_combo.setCurrentText("Sine")
                    
                self.ch1_type_combo.blockSignals(False)
                self.ch2_type_combo.blockSignals(False)

                # Update frequency line edits
                self._update_read_only_input(self.ch1_freq_inp, self.ch1_lbls["Freq"].text().replace(" Hz", "").replace(" k", "000").replace(" M", "000000"))
                self._update_read_only_input(self.ch2_freq_inp, self.ch2_lbls["Freq"].text().replace(" Hz", "").replace(" k", "000").replace(" M", "000000"))
                
                # Amplitude = Vpp / 2
                try:
                    v1_pp_text = self.ch1_lbls["Vpp"].text().replace(" V", "")
                    if v1_pp_text != "---":
                        self._update_read_only_input(self.ch1_amp_inp, f"{float(v1_pp_text)/2.0:.2f}")
                except ValueError:
                    pass
                try:
                    v2_pp_text = self.ch2_lbls["Vpp"].text().replace(" V", "")
                    if v2_pp_text != "---":
                        self._update_read_only_input(self.ch2_amp_inp, f"{float(v2_pp_text)/2.0:.2f}")
                except ValueError:
                    pass
                
                # DC Offset = Avg
                self._update_read_only_input(self.ch1_offset_inp, self.ch1_lbls["Avg"].text().replace(" V", ""))
                self._update_read_only_input(self.ch2_offset_inp, self.ch2_lbls["Avg"].text().replace(" V", ""))
                
                # Phase
                self._update_read_only_input(self.ch1_phase_inp, "0.0")
                phase_text = self.lbl_phase_diff.text().replace("Phase Diff: ", "").replace("°", "")
                if phase_text != "---" and phase_text != "Phase Diff: ---":
                    self._update_read_only_input(self.ch2_phase_inp, phase_text)
                else:
                    self._update_read_only_input(self.ch2_phase_inp, "0.0")
            except Exception:
                pass

    def _update_read_only_input(self, line_edit, value_str):
        if value_str and value_str != "---" and value_str != "Phase Diff: ---":
            line_edit.blockSignals(True)
            line_edit.setText(value_str)
            line_edit.blockSignals(False)

    def calculate_realtime_metrics(self):
        if not hasattr(self, 'ch1_points') or len(self.ch1_points) == 0:
            for k in self.ch1_lbls: self.ch1_lbls[k].setText("---")
            for k in self.ch2_lbls: self.ch2_lbls[k].setText("---")
            self.lbl_phase_diff.setText("Phase Diff: ---")
            return
            
        t = self.t_points
        trig_level = self.trig_level_slider.value() / 10.0

        def _calculate_channel_metrics(v, ch_lbls):
            v_max = np.max(v)
            v_min = np.min(v)
            v_pp = v_max - v_min
            v_rms = np.sqrt(np.mean(v**2))
            v_avg = np.mean(v)
            
            crossings = []
            for idx in range(1, len(v)):
                if v[idx - 1] <= trig_level and v[idx] > trig_level:
                    crossings.append(t[idx])
            
            if len(crossings) >= 2:
                p = np.mean(np.diff(crossings))
                ch_lbls["Freq"].setText(f"{format_eng(1.0/p, 'Hz')}")
                ch_lbls["Period"].setText(f"{format_eng(p, 's')}")
            else:
                # Fallback to theoretical frequency for live updating
                f_fallback = self.ch1_freq if ch_lbls is self.ch1_lbls else self.ch2_freq
                ch_lbls["Freq"].setText(f"{format_eng(f_fallback, 'Hz')}")
                ch_lbls["Period"].setText(f"{format_eng(1.0/f_fallback, 's')}")
                
            ch_lbls["Vpp"].setText(f"{v_pp:.2f} V")
            ch_lbls["Vmax"].setText(f"{v_max:.2f} V")
            ch_lbls["Vmin"].setText(f"{v_min:.2f} V")
            ch_lbls["Vrms"].setText(f"{v_rms:.2f} V")
            ch_lbls["Avg"].setText(f"{v_avg:.2f} V")
            
            # Duty Cycle
            mid = (v_max + v_min) / 2.0
            if v_pp > 1e-4:
                above_mid = v > mid
                duty = (np.sum(above_mid) / len(v)) * 100.0
                ch_lbls["Duty"].setText(f"{duty:.1f}%")
            else:
                ch_lbls["Duty"].setText("---")
                
            # Rise/Fall Time (10% to 90%)
            if v_pp > 1e-4:
                v10 = v_min + 0.10 * v_pp
                v90 = v_min + 0.90 * v_pp
                rise_times = []
                fall_times = []
                idx = 0
                n = len(v)
                while idx < n - 1:
                    # Rising transition
                    if v[idx] < v10:
                        j = idx + 1
                        while j < n and v[j] <= v90:
                            if v[j] < v10:
                                idx = j
                            j += 1
                        if j < n:
                            t_10 = t[idx] + (v10 - v[idx]) / (v[j] - v[idx]) * (t[j] - t[idx]) if (v[j] - v[idx]) > 0 else t[idx]
                            k = idx
                            while k < j and v[k] < v90:
                                k += 1
                            t_90 = t[k-1] + (v90 - v[k-1]) / (v[k] - v[k-1]) * (t[k] - t[k-1]) if (v[k] - v[k-1]) > 0 else t[k]
                            rise_times.append(t_90 - t_10)
                            idx = j
                            continue
                    # Falling transition
                    elif v[idx] > v90:
                        j = idx + 1
                        while j < n and v[j] >= v10:
                            if v[j] > v90:
                                idx = j
                            j += 1
                        if j < n:
                            t_90 = t[idx] + (v90 - v[idx]) / (v[j] - v[idx]) * (t[j] - t[idx]) if (v[idx] - v[j]) > 0 else t[idx]
                            k = idx
                            while k < j and v[k] > v10:
                                k += 1
                            t_10 = t[k-1] + (v10 - v[k-1]) / (v[k] - v[k-1]) * (t[k] - t[k-1]) if (v[k-1] - v[k]) > 0 else t[k]
                            fall_times.append(t_10 - t_90)
                            idx = j
                            continue
                    idx += 1
                
                if len(rise_times) > 0:
                    ch_lbls["Rise"].setText(f"{format_eng(np.mean(rise_times), 's')}")
                else:
                    ch_lbls["Rise"].setText("---")
                if len(fall_times) > 0:
                    ch_lbls["Fall"].setText(f"{format_eng(np.mean(fall_times), 's')}")
                else:
                    ch_lbls["Fall"].setText("---")
            else:
                ch_lbls["Rise"].setText("---")
                ch_lbls["Fall"].setText("---")

        # 1. CH1 Metrics
        if self.ch1_en:
            _calculate_channel_metrics(self.ch1_points, self.ch1_lbls)
        else:
            for k in self.ch1_lbls: self.ch1_lbls[k].setText("---")

        # 2. CH2 Metrics
        if self.ch2_en:
            _calculate_channel_metrics(self.ch2_points, self.ch2_lbls)
        else:
            for k in self.ch2_lbls: self.ch2_lbls[k].setText("---")

        # 3. Phase difference calculation (CH1 ↔ CH2)
        if self.ch1_en and self.ch2_en:
            try:
                # Find zero crossing times on positive slopes
                c1 = []
                c2 = []
                for idx in range(1, len(self.ch1_points)):
                    if self.ch1_points[idx-1] <= 0 and self.ch1_points[idx] > 0:
                        c1.append(t[idx])
                for idx in range(1, len(self.ch2_points)):
                    if self.ch2_points[idx-1] <= 0 and self.ch2_points[idx] > 0:
                        c2.append(t[idx])
                        
                if len(c1) > 0 and len(c2) > 0:
                    t1 = c1[0]
                    # Find closest zero crossing of CH2 relative to CH1
                    t2 = c2[np.argmin(np.abs(np.array(c2) - t1))]
                    # Calculate period
                    p = np.mean(np.diff(c1)) if len(c1) >= 2 else (1.0/self.ch1_freq)
                    
                    phase_deg = ((t2 - t1) / p) * 360.0
                    phase_deg = (phase_deg + 180.0) % 360.0 - 180.0
                    self.lbl_phase_diff.setText(f"Phase Diff: {phase_deg:.1f}°")
                else:
                    self.lbl_phase_diff.setText("Phase Diff: ---")
            except Exception:
                self.lbl_phase_diff.setText("Phase Diff: ---")
        else:
            self.lbl_phase_diff.setText("Phase Diff: ---")

    def update_cursor_calculations(self):
        if not self.display_screen.cursors_enabled or len(self.t_points) == 0:
            return
            
        t_span = 10.0 * self.get_timebase_value()
        t1 = self.sim_time + self.display_screen.cursor_x1 * t_span
        t2 = self.sim_time + self.display_screen.cursor_x2 * t_span
        delta_t = abs(t2 - t1)
        freq_cursor = 1.0 / delta_t if delta_t > 0 else 0.0
        
        self.lbl_delta_t.setText(f"ΔT: {format_eng(delta_t, 's')} | 1/ΔT: {format_eng(freq_cursor, 'Hz')}")
        
        v_span = 8.0 * self.get_ch1_vscale_value()
        y1_v = self.ch1_offset + (0.5 - self.display_screen.cursor_y1) * v_span
        y2_v = self.ch1_offset + (0.5 - self.display_screen.cursor_y2) * v_span
        delta_v = abs(y2_v - y1_v)
        self.lbl_delta_v.setText(f"ΔV (CH1): {delta_v:.2f} V")

    def update_fps(self):
        self.fps_rate = self.fps_counter
        self.fps_counter = 0
        self.status_fps.setText(f"FPS: {self.fps_rate}")

    def export_screenshot(self):
        pixmap = self.display_screen.grab()
        path, _ = QFileDialog.getSaveFileName(self, "Export Screen Capture", "", "PNG Image (*.png)")
        if path:
            pixmap.save(path)
            self.show_toast("Screenshot exported successfully.")

    def export_csv_data(self):
        if not hasattr(self, 'ch1_points') or len(self.ch1_points) == 0:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Export DSO Waveform", "", "CSV File (*.csv)")
        if path:
            with open(path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time (s)", "CH1 Voltage (V)", "CH2 Voltage (V)"])
                for t_val, v1_val, v2_val in zip(self.t_points, self.ch1_points, self.ch2_points):
                    writer.writerow([t_val, v1_val, v2_val])
            self.show_toast("DSO data exported successfully.")

    def show_toast(self, message: str):
        top_window = self.window()
        if top_window and hasattr(top_window, "show_toast"):
            top_window.show_toast(message)

    def showEvent(self, event):
        super().showEvent(event)
        # Enable dynamic auto-detection on show
        self.manual_override = False
        self.detect_and_sync_active_circuit()
        self.on_inputs_changed()
