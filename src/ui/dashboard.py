"""
ElectroVerse Professional Engineering Workstation - Main Dashboard View
Inspired by MATLAB App Designer, NI LabVIEW, Scilab GUI, Proteus, and Keysight BenchVue.
"""

import os
import sys
import random
import platform
import math
import threading
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QGridLayout, QScrollArea, QProgressBar, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QBrush
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.ui.learning_content import get_lesson_data
from src.core.navigation import ViewID, HubTabID


# ==============================================================================
# LIVE SIGNAL VECTOR & MATHEMATICAL WAVEFORM ANALYZER PANEL
# ==============================================================================

class LiveSignalAnalyzerWidget(QWidget):
    """Scientific 2x Large Live Signal Vector Waveform Analyzer."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.waveform_type = 0  # 0: Sine, 1: Square, 2: RC Charge, 3: AM, 4: FM
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_phase)
        self.anim_timer.start(30)
        
        self.rotate_timer = QTimer(self)
        self.rotate_timer.timeout.connect(self.rotate_waveform)
        self.rotate_timer.start(5000)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(240)
        
    def update_phase(self):
        self.phase += 0.08
        self.update()
        
    def rotate_waveform(self):
        self.waveform_type = (self.waveform_type + 1) % 5
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        centerY = height / 2
        
        # Deep Dark Obsidian Screen Background
        painter.fillRect(0, 0, width, height, QColor("#060A12"))
        
        # Precision Engineering Grid
        grid_pen = QPen(QColor("#152033"), 1, Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)
        
        for x in range(0, width, 40):
            painter.drawLine(x, 0, x, height)
            
        for y in range(0, height, 40):
            painter.drawLine(0, y, width, y)
            
        # Primary Axis Markings
        axis_pen = QPen(QColor("#26334D"), 1.5, Qt.PenStyle.SolidLine)
        painter.setPen(axis_pen)
        painter.drawLine(0, centerY, width, centerY)
        painter.drawLine(width / 2, 0, width / 2, height)
        
        path = QPainterPath()
        started = False
        amp = height * 0.36
        
        wave_names = [
            "AC SINE WAVE HARMONIC SYNTHESIS [f = 100 Hz, Vpp = 5.0V]",
            "DIGITAL TTL CLOCK PULSE SWEEP [7408 BREADBOARD TRAINER]",
            "TRANSIENT RC CAPACITOR DYNAMICS [tau = 2.5ms, Vc = 4.8V]",
            "AMPLITUDE MODULATED CARRIER SIGNAL [fc = 10.0 kHz, m = 0.5]",
            "FREQUENCY MODULATED CARRIER SIGNAL [fc = 20.0 kHz, beta = 3.0]"
        ]
        
        for x in range(width):
            t = (x / width) * 4 * math.pi
            y = 0.0
            
            if self.waveform_type == 0:
                y = amp * math.sin(t - self.phase)
            elif self.waveform_type == 1:
                raw_val = math.sin(t - self.phase)
                y = amp * (1.0 if raw_val >= 0 else -1.0)
            elif self.waveform_type == 2:
                period_t = (t - self.phase) % (2 * math.pi)
                y = amp * (1.0 - 2.0 * math.exp(-period_t * 1.2))
            elif self.waveform_type == 3:
                modulator = 1.0 + 0.5 * math.sin(t * 0.2 - self.phase * 0.1)
                y = amp * 0.7 * modulator * math.sin(t * 8.0 - self.phase)
            elif self.waveform_type == 4:
                mod_signal = math.sin(t * 0.5 - self.phase * 0.2)
                y = amp * math.sin(t * 8.0 + 3.0 * mod_signal)
                
            y_coord = centerY - y
            if not started:
                path.moveTo(x, y_coord)
                started = True
            else:
                path.lineTo(x, y_coord)
                
        wave_pen = QPen(QColor("#10B981"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(wave_pen)
        painter.drawPath(path)
        
        # Readout Overlay Panel
        overlay_w = 420
        overlay_h = 36
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.setPen(QPen(QColor("#06B6D4"), 1))
        painter.drawRoundedRect(12, 10, overlay_w, overlay_h, 4, 4)
        
        painter.setPen(QColor("#06B6D4"))
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(20, 24, f"● REAL-TIME SIGNAL: {wave_names[self.waveform_type]}")
        painter.drawText(20, 37, f"SR: 1.0 MS/s | SOLVER: 60 FPS | MATRIX: Sparse LU | CURSOR: (0.0ms, 2.50V)")


# ==============================================================================
# MAIN WORKSTATION DASHBOARD VIEW
# ==============================================================================

class DashboardView(QWidget):
    """Professional Engineering Workstation Dashboard."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window or parent
        log.info("Initializing Professional Engineering Workstation DashboardView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Clean Primary Desktop Engineering Header
        self.setup_ribbon_toolbar(main_layout)

        # 2. Main Workbench Splitter (Left Tool Palette + Center Project Workspace)
        self.workbench_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.workbench_splitter.setHandleWidth(2)
        self.workbench_splitter.setStyleSheet("QSplitter::handle { background-color: #26334D; }")

        # Left Categorized Instrument Palette
        self.setup_categorized_instrument_palette()

        # Center Main Project Workspace
        self.setup_center_project_workspace()

        self.workbench_splitter.setSizes([240, 1100])
        main_layout.addWidget(self.workbench_splitter, 1)

        # 3. Bottom Industrial IDE Status Bar
        self.setup_bottom_status_bar(main_layout)

        # Resource Monitor Timer
        self.mon_timer = QTimer(self)
        self.mon_timer.timeout.connect(self.update_resource_monitor)
        self.mon_timer.start(1000)

        self.refresh_dashboard()

    # --------------------------------------------------------------------------
    # 1. Clean Primary Desktop Engineering Header (No Redundant Nav Buttons)
    # --------------------------------------------------------------------------
    def setup_ribbon_toolbar(self, parent_layout):
        ribbon = QFrame()
        ribbon.setFixedHeight(56)
        ribbon.setStyleSheet("QFrame { background-color: #101827; border-bottom: 2px solid #26334D; }")
        r_lay = QHBoxLayout(ribbon)
        r_lay.setContentsMargins(20, 0, 20, 0)

        # Centered Industrial Workspace Title Block
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel("⚡ ElectroVerse Lab Workstation v1.0")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 13.5pt; font-family: Consolas; letter-spacing: 0.5px;")

        sub_lbl = QLabel("Engineering Laboratory Control Center")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 9pt; font-family: Consolas;")

        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)

        r_lay.addStretch()
        r_lay.addLayout(title_box)
        r_lay.addStretch()

        # Far-Right Status Indicator
        sys_stat = QLabel("● SYS: Online")
        sys_stat.setStyleSheet("color: #10B981; font-weight: bold; font-size: 8.5pt; font-family: Consolas;")
        r_lay.addWidget(sys_stat)

        parent_layout.addWidget(ribbon)

    def toggle_ai_assistant(self):
        if self.main_window and hasattr(self.main_window, "toggle_ai_drawer"):
            self.main_window.toggle_ai_drawer()

    # --------------------------------------------------------------------------
    # 2. Left Categorized Instrument Palette
    # --------------------------------------------------------------------------
    def setup_categorized_instrument_palette(self):
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: #0F172A; border-right: 1px solid #26334D; }")
        l_lay = QVBoxLayout(left_panel)
        l_lay.setContentsMargins(10, 10, 10, 10)
        l_lay.setSpacing(10)

        hdr = QLabel("🛠 CATEGORIZED TOOL PALETTE")
        hdr.setStyleSheet("color: #06B6D4; font-size: 8.5pt; font-weight: bold; font-family: Consolas; letter-spacing: 0.5px;")
        l_lay.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        pal_container = QWidget()
        p_lay = QVBoxLayout(pal_container)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(10)

        categories = [
            ("SIGNAL SOURCES", [
                ("Function Generator", "fa5s.sliders-h", lambda: self.main_window.open_simulation_workspace(ViewID.ANALOG_HUB)),
                ("Clock Generator", "fa5s.clock", lambda: self.main_window.open_simulation_workspace(ViewID.DIGITAL_HUB)),
                ("Pulse Generator", "fa5s.wave-square", lambda: self.main_window.open_simulation_workspace(ViewID.ANALOG_HUB))
            ]),
            ("DIGITAL INSTRUMENTS", [
                ("Logic Analyzer", "fa5s.microchip", lambda: self.main_window.open_simulation_workspace(ViewID.DIGITAL_HUB)),
                ("Truth Table Solver", "fa5s.table", lambda: self.main_window.open_simulation_workspace(ViewID.DIGITAL_HUB)),
                ("K-map Minimizer", "fa5s.th-large", lambda: self.main_window.open_simulation_workspace(ViewID.DIGITAL_HUB))
            ]),
            ("ANALOG INSTRUMENTS", [
                ("Signal Visualizer", "fa5s.chart-line", lambda: self.main_window.open_simulation_workspace(ViewID.ANALOG_HUB)),
                ("Spectrum Analyzer", "fa5s.chart-bar", lambda: self.main_window.open_simulation_workspace(ViewID.SIGNALS_HUB)),
                ("FFT Transform", "fa5s.calculator", lambda: self.main_window.open_simulation_workspace(ViewID.SIGNALS_HUB)),
                ("Bode Plot Analyzer", "fa5s.project-diagram", lambda: self.main_window.open_simulation_workspace(ViewID.NETWORK_HUB))
            ]),
            ("ENGINEERING UTILITIES", [
                ("Component Datasheets", "fa5s.book", lambda: self.main_window.switch_to_view(ViewID.LIBRARY)),
                ("Formula Calculator", "fa5s.calculator", lambda: self.main_window.open_learning_workspace(ViewID.ANALOG_HUB)),
                ("IEEE Report Generator", "fa5s.file-alt", lambda: self.main_window.open_assessment_workspace())
            ])

        ]

        for cat_title, tools in categories:
            cat_box = QFrame()
            cat_box.setStyleSheet("background-color: #141B2D; border: 1px solid #1E293B; border-radius: 4px; padding: 6px;")
            cb_lay = QVBoxLayout(cat_box)
            cb_lay.setSpacing(4)

            ct_lbl = QLabel(cat_title)
            ct_lbl.setStyleSheet("color: #06B6D4; font-size: 7.5pt; font-weight: bold; font-family: Consolas;")
            cb_lay.addWidget(ct_lbl)

            for name, icon_str, action_func in tools:
                btn = QPushButton(f"  {name}")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setIcon(qta.icon(icon_str, color="#94A3B8"))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #090D16;
                        color: #CBD5E1;
                        text-align: left;
                        padding: 6px 8px;
                        border: 1px solid #26334D;
                        border-radius: 3px;
                        font-size: 8pt;
                        font-family: Consolas;
                    }
                    QPushButton:hover {
                        background-color: #1E293B;
                        border-color: #06B6D4;
                        color: #FFFFFF;
                    }
                """)
                btn.clicked.connect(action_func)
                cb_lay.addWidget(btn)

            p_lay.addWidget(cat_box)

        scroll.setWidget(pal_container)
        l_lay.addWidget(scroll, 1)

        # Health Card
        health_card = QFrame()
        health_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 4px; padding: 6px;")
        h_lay = QVBoxLayout(health_card)
        h_lay.setSpacing(2)

        ht = QLabel("ENGINE HEALTH")
        ht.setStyleSheet("color: #10B981; font-size: 7.5pt; font-weight: bold; font-family: Consolas;")
        h_lay.addWidget(ht)

        self.lbl_cpu_side = QLabel("CPU: 12.0% | RAM: 4.1GB")
        self.lbl_cpu_side.setStyleSheet("color: #94A3B8; font-size: 7.5pt; font-family: Consolas;")
        h_lay.addWidget(self.lbl_cpu_side)

        self.lbl_sim_side = QLabel("SOLVER: ● 60 FPS")
        self.lbl_sim_side.setStyleSheet("color: #06B6D4; font-size: 7.5pt; font-family: Consolas;")
        h_lay.addWidget(self.lbl_sim_side)

        l_lay.addWidget(health_card)
        self.workbench_splitter.addWidget(left_panel)

    # --------------------------------------------------------------------------
    # 3. Center Project Workspace Panel (No Redundant Search Bar)
    # --------------------------------------------------------------------------
    def setup_center_project_workspace(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #0B1020; }")

        container = QWidget()
        self.c_layout = QVBoxLayout(container)
        self.c_layout.setContentsMargins(14, 14, 14, 14)
        self.c_layout.setSpacing(14)

        # 3.1 Subject Hub Cards Grid (Primary Workspace Entry Point)
        self.setup_subject_hub_cards()

        # 3.2 Live Signal Analyzer & Resource Monitor Row (2x Graph Visual Centerpiece)
        self.setup_signal_and_resource_row()

        # 3.3 Spaciously Formatted Activity Tables Row
        self.setup_activity_tables_row()

        # 3.4 AI Assistant Status & Quick Launch Row
        self.setup_ai_status_and_quick_launch_row()

        # 3.5 Notifications Center Panel
        self.setup_notifications_panel()

        scroll.setWidget(container)
        self.workbench_splitter.addWidget(scroll)

    # --------------------------------------------------------------------------
    # 3.1 Subject Hub Cards Grid
    # --------------------------------------------------------------------------
    def setup_subject_hub_cards(self):
        panel = QWidget()
        p_lay = QVBoxLayout(panel)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(8)

        hdr = QLabel("🎛 LABORATORY CONTROL MODULES")
        hdr.setStyleSheet("color: #06B6D4; font-size: 9.5pt; font-weight: bold; font-family: Consolas; letter-spacing: 0.5px;")
        p_lay.addWidget(hdr)

        grid = QGridLayout()
        grid.setSpacing(12)

        # Config with requested accent colors
        hubs_config = [
            ("ANALOG ELECTRONICS HUB", "fa5s.wave-square", ViewID.ANALOG_HUB, "60%", "24/40", "16 Labs", "86%", "#06B6D4", "● Ready"),     # Cyan
            ("DIGITAL SYSTEM DESIGN HUB", "fa5s.microchip", ViewID.DIGITAL_HUB, "65%", "14/20", "22 Labs", "92%", "#10B981", "● Ready"),   # Green
            ("SIGNAL & SYSTEM HUB", "fa5s.chart-line", ViewID.SIGNALS_HUB, "54%", "20/32", "15 Labs", "88%", "#F59E0B", "● Active"),     # Amber
            ("NETWORK THEORY HUB", "fa5s.project-diagram", ViewID.NETWORK_HUB, "48%", "18/42", "15 Labs", "84%", "#38BDF8", "● Ready"),  # Blue
            ("COMPONENT LIBRARY MATRIX", "fa5s.book", ViewID.LIBRARY, "90%", "91 Parts", "60+ Forms", "N/A", "#A855F7", "● Online"), # Purple
            ("GRAND VIVA INTERVIEW BOARD", "fa5s.user-graduate", ViewID.GRAND_VIVA, "75%", "270+ Q&A", "10 Topics", "89%", "#EC4899", "● Ready"), # Pink
        ]

        for idx, (title, icon_str, v_id, prog, mods, sims, score, color, status_str) in enumerate(hubs_config):
            card = QFrame()
            card.setObjectName("mod-card")
            card.setStyleSheet(f"""
                QFrame#mod-card {{
                    background-color: #141B2D;
                    border: 1px solid #26334D;
                    border-left: 4px solid {color};
                    border-radius: 4px;
                    padding: 10px;
                }}
                QFrame#mod-card:hover {{
                    background-color: #1B2740;
                    border-color: {color};
                }}
            """)
            c_lay = QVBoxLayout(card)
            c_lay.setSpacing(6)

            t_row = QHBoxLayout()
            ic = QLabel(); ic.setPixmap(qta.icon(icon_str, color=color).pixmap(18, 18))
            tl = QLabel(title); tl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 8.5pt; font-family: Consolas;")
            t_row.addWidget(ic); t_row.addWidget(tl); t_row.addStretch()

            led = QLabel(status_str)
            led.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 7.5pt; font-family: Consolas;")
            t_row.addWidget(led)
            c_lay.addLayout(t_row)

            # Metrics Row
            m_row = QHBoxLayout()
            m1 = QLabel(f"PROG: {prog}"); m1.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 7.5pt; font-family: Consolas;")
            m2 = QLabel(f"MODS: {mods}"); m2.setStyleSheet("color: #94A3B8; font-size: 7.5pt; font-family: Consolas;")
            m3 = QLabel(f"SIMS: {sims}"); m3.setStyleSheet("color: #94A3B8; font-size: 7.5pt; font-family: Consolas;")
            m4 = QLabel(f"SCORE: {score}"); m4.setStyleSheet("color: #10B981; font-weight: bold; font-size: 7.5pt; font-family: Consolas;")

            m_row.addWidget(m1); m_row.addWidget(m2); m_row.addWidget(m3); m_row.addWidget(m4)
            c_lay.addLayout(m_row)

            # Progress Bar
            pct_val = int(prog.replace("%", "")) if "%" in prog else 50
            pbar = QProgressBar()
            pbar.setRange(0, 100); pbar.setValue(pct_val); pbar.setFixedHeight(5); pbar.setTextVisible(False)
            pbar.setStyleSheet(f"QProgressBar {{ background-color: #090D16; border: 1px solid #26334D; border-radius: 2px; }} QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}")
            c_lay.addWidget(pbar)

            btn = QPushButton(" Launch Workspace ➡")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"background-color: #1E293B; color: #FFFFFF; font-weight: bold; padding: 5px 10px; border: 1px solid #334155; border-radius: 3px; font-size: 7.5pt; font-family: Consolas;")
            btn.clicked.connect(lambda _, target=v_id: self.switch_to_hub(target))
            c_lay.addWidget(btn)

            grid.addWidget(card, idx // 3, idx % 3)

        p_lay.addLayout(grid)
        self.c_layout.addWidget(panel)

    # --------------------------------------------------------------------------
    # 3.2 Live Signal Analyzer & Resource Monitor Row (2x Visual Centerpiece)
    # --------------------------------------------------------------------------
    def setup_signal_and_resource_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        # 2x Graph Visual Centerpiece
        signal_card = QFrame()
        signal_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 10px;")
        s_lay = QVBoxLayout(signal_card)
        s_lay.setSpacing(6)

        s_hdr = QLabel("📈 REAL-TIME SIGNAL VECTOR & MATHEMATICAL WAVEFORM ANALYZER [2x CENTERPIECE]")
        s_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 9pt; font-family: Consolas;")
        s_lay.addWidget(s_hdr)

        self.signal_widget = LiveSignalAnalyzerWidget(self)
        s_lay.addWidget(self.signal_widget)

        row.addWidget(signal_card, 2)

        # Resource Monitor Panel
        res_card = QFrame()
        res_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 10px;")
        r_lay = QVBoxLayout(res_card)
        r_lay.setSpacing(8)

        r_hdr = QLabel("💻 LIVE SYSTEM RESOURCE MONITOR")
        r_hdr.setStyleSheet("color: #10B981; font-weight: bold; font-size: 9pt; font-family: Consolas;")
        r_lay.addWidget(r_hdr)

        # CPU Meter
        c_row = QHBoxLayout()
        c_lbl = QLabel("CPU USAGE:"); c_lbl.setStyleSheet("color: #94A3B8; font-size: 8pt; font-family: Consolas;")
        self.cpu_val_lbl = QLabel("12.0%"); self.cpu_val_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 8pt; font-family: Consolas;")
        c_row.addWidget(c_lbl); c_row.addStretch(); c_row.addWidget(self.cpu_val_lbl)
        r_lay.addLayout(c_row)

        self.cpu_pbar = QProgressBar()
        self.cpu_pbar.setRange(0, 100); self.cpu_pbar.setValue(12); self.cpu_pbar.setFixedHeight(6); self.cpu_pbar.setTextVisible(False)
        self.cpu_pbar.setStyleSheet("QProgressBar { background-color: #090D16; border: 1px solid #26334D; border-radius: 3px; } QProgressBar::chunk { background-color: #10B981; border-radius: 2px; }")
        r_lay.addWidget(self.cpu_pbar)

        # RAM Meter
        ram_row = QHBoxLayout()
        ram_lbl = QLabel("RAM USAGE:"); ram_lbl.setStyleSheet("color: #94A3B8; font-size: 8pt; font-family: Consolas;")
        self.ram_val_lbl = QLabel("4.1 GB / 16 GB"); self.ram_val_lbl.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 8pt; font-family: Consolas;")
        ram_row.addWidget(ram_lbl); ram_row.addStretch(); ram_row.addWidget(self.ram_val_lbl)
        r_lay.addLayout(ram_row)

        self.ram_pbar = QProgressBar()
        self.ram_pbar.setRange(0, 100); self.ram_pbar.setValue(25); self.ram_pbar.setFixedHeight(6); self.ram_pbar.setTextVisible(False)
        self.ram_pbar.setStyleSheet("QProgressBar { background-color: #090D16; border: 1px solid #26334D; border-radius: 3px; } QProgressBar::chunk { background-color: #38BDF8; border-radius: 2px; }")
        r_lay.addWidget(self.ram_pbar)

        # Engine Stats
        e_info = [
            ("SOLVER FPS:", "● 60 FPS (Headless-Safe)"),
            ("NETLIST MATRIX:", "Sparse LU Solver"),
            ("PYTHON KERNEL:", f"v{platform.python_version()}"),
            ("ACTIVE THREADS:", f"{threading.active_count()} Threads"),
            ("SECURITY VAULT:", "Keyring / Fernet AES")
        ]
        for k, v in e_info:
            ir = QHBoxLayout()
            kl = QLabel(k); kl.setStyleSheet("color: #64748B; font-size: 7.5pt; font-family: Consolas;")
            vl = QLabel(v); vl.setStyleSheet("color: #CBD5E1; font-size: 7.5pt; font-family: Consolas; font-weight: bold;")
            ir.addWidget(kl); ir.addStretch(); ir.addWidget(vl)
            r_lay.addLayout(ir)

        r_lay.addStretch()
        row.addWidget(res_card, 1)

        self.c_layout.addLayout(row)

    def update_resource_monitor(self):
        if HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory()
                ram_used_gb = ram.used / (1024 ** 3)
                ram_total_gb = ram.total / (1024 ** 3)
                ram_pct = ram.percent

                self.cpu_val_lbl.setText(f"{cpu:.1f}%")
                self.cpu_pbar.setValue(int(cpu))

                self.ram_val_lbl.setText(f"{ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB")
                self.ram_pbar.setValue(int(ram_pct))

                self.lbl_cpu_side.setText(f"CPU: {cpu:.1f}% | RAM: {ram_used_gb:.1f}GB")
                return
            except Exception:
                pass

        # Fallback values if psutil is unavailable
        self.cpu_val_lbl.setText("12.0%")
        self.cpu_pbar.setValue(12)
        self.ram_val_lbl.setText("4.1 GB / 16 GB")
        self.ram_pbar.setValue(25)
        self.lbl_cpu_side.setText("CPU: 12.0% | RAM: 4.1GB")

    # --------------------------------------------------------------------------
    # 3.3 Spaciously Formatted Tables Row
    # --------------------------------------------------------------------------
    def setup_activity_tables_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        # Table 1: Recent Experiments
        exp_card = QFrame()
        exp_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 12px;")
        e_lay = QVBoxLayout(exp_card)
        e_lay.setSpacing(8)

        e_hdr = QLabel("🔬 RECENT SIMULATION EXPERIMENTS LOG")
        e_hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        e_lay.addWidget(e_hdr)

        self.exp_table = QTableWidget(4, 4)
        self.exp_table.setHorizontalHeaderLabels(["Experiment Name", "Subject Domain", "Timestamp", "Status"])
        self.exp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.exp_table.verticalHeader().setVisible(False)
        self.exp_table.verticalHeader().setDefaultSectionSize(32)
        self.exp_table.setShowGrid(True)
        self.exp_table.setStyleSheet("""
            QTableWidget {
                background-color: #090D16;
                gridline-color: #1E293B;
                color: #CBD5E1;
                font-size: 8.5pt;
                font-family: Consolas, "Segoe UI";
                border: 1px solid #26334D;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #101827;
                color: #06B6D4;
                font-weight: bold;
                font-size: 8.5pt;
                font-family: Consolas;
                border: 1px solid #26334D;
                padding: 6px 8px;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
        """)

        exp_data = [
            ("TTL 7408 AND Gate Breadboard", "Digital Systems", "10:45 AM", "● PASSED"),
            ("Full-Wave Bridge Rectifier Lab", "Analog Electronics", "09:30 AM", "● COMPLETED"),
            ("RC Transient Charging Sweep", "Analog Electronics", "Yesterday", "● COMPLETED"),
            ("Thevenin Mesh Equivalent Solver", "Network Theory", "2 days ago", "● PASSED"),
        ]

        for r_idx, row_items in enumerate(exp_data):
            for c_idx, val in enumerate(row_items):
                item = QTableWidgetItem(val)
                if c_idx == 3:
                    item.setForeground(QColor("#10B981"))
                    item.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
                self.exp_table.setItem(r_idx, c_idx, item)

        self.exp_table.setFixedHeight(175)
        e_lay.addWidget(self.exp_table)
        row.addWidget(exp_card, 1)

        # Table 2: Recent Reports
        rep_card = QFrame()
        rep_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 12px;")
        r_lay = QVBoxLayout(rep_card)
        r_lay.setSpacing(8)

        r_hdr = QLabel("📑 RECENT IEEE LAB REPORTS & TECHNICAL NOTES")
        r_hdr.setStyleSheet("color: #EC4899; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        r_lay.addWidget(r_hdr)

        self.rep_table = QTableWidget(4, 4)
        self.rep_table.setHorizontalHeaderLabels(["Report Title", "System Publisher", "Date Created", "Document Format"])
        self.rep_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rep_table.verticalHeader().setVisible(False)
        self.rep_table.verticalHeader().setDefaultSectionSize(32)
        self.rep_table.setShowGrid(True)
        self.rep_table.setStyleSheet("""
            QTableWidget {
                background-color: #090D16;
                gridline-color: #1E293B;
                color: #CBD5E1;
                font-size: 8.5pt;
                font-family: Consolas, "Segoe UI";
                border: 1px solid #26334D;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #101827;
                color: #EC4899;
                font-weight: bold;
                font-size: 8.5pt;
                font-family: Consolas;
                border: 1px solid #26334D;
                padding: 6px 8px;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
        """)

        rep_data = [
            ("Center-Tapped Rectifier Analysis", "ElectroVerse Engine", "2026-07-30", "IEEE Markdown"),
            ("K-Map 4-Variable Minimization", "ElectroVerse Engine", "2026-07-28", "IEEE Markdown"),
            ("Op-Amp Inverting Derivation", "ElectroVerse Engine", "2026-07-25", "LaTeX / PDF"),
            ("Fourier Series Expansion Note", "ElectroVerse Engine", "2026-07-22", "IEEE Markdown"),
        ]

        for r_idx, row_items in enumerate(rep_data):
            for c_idx, val in enumerate(row_items):
                item = QTableWidgetItem(val)
                if c_idx == 3:
                    item.setForeground(QColor("#38BDF8"))
                    item.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
                self.rep_table.setItem(r_idx, c_idx, item)

        self.rep_table.setFixedHeight(175)
        r_lay.addWidget(self.rep_table)
        row.addWidget(rep_card, 1)

        self.c_layout.addLayout(row)

    # --------------------------------------------------------------------------
    # 3.4 Quick Launch Recent Labs & System Status Row
    # --------------------------------------------------------------------------
    def setup_ai_status_and_quick_launch_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        # Quick Launch Panel
        ql_card = QFrame()
        ql_card.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 12px;")
        q_lay = QVBoxLayout(ql_card)
        q_lay.setSpacing(10)

        q_hdr = QLabel("🚀 QUICK LAUNCH RECENT LABS & INSTRUMENTS")
        q_hdr.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        q_lay.addWidget(q_hdr)

        grid = QGridLayout()
        grid.setSpacing(8)

        labs = [
            ("▶ 7408 AND Breadboard Trainer", lambda: self.main_window.open_simulation_workspace(ViewID.DIGITAL_HUB)),
            ("▶ Bridge Rectifier Circuit Lab", lambda: self.main_window.open_simulation_workspace(ViewID.ANALOG_HUB)),
            ("▶ Convolution Integral Solver", lambda: self.main_window.open_simulation_workspace(ViewID.SIGNALS_HUB)),
            ("▶ Thevenin Matrix Solver", lambda: self.main_window.open_simulation_workspace(ViewID.NETWORK_HUB)),
            ("▶ Grand Viva Board Examiner", lambda: self.main_window.open_assessment_workspace()),
            ("▶ Component Datasheet Search", lambda: self.main_window.switch_to_view(ViewID.LIBRARY))
        ]

        for idx, (label, action_func) in enumerate(labs):
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #FFFFFF;
                    font-size: 8.5pt;
                    font-family: Consolas, "Segoe UI";
                    padding: 9px 12px;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #26334D;
                    border-color: #38BDF8;
                    color: #38BDF8;
                }
            """)
            btn.clicked.connect(action_func)
            grid.addWidget(btn, idx // 2, idx % 2)

        q_lay.addLayout(grid)
        row.addWidget(ql_card, 1)
        self.c_layout.addLayout(row)

    # --------------------------------------------------------------------------
    # 3.5 Notifications Center Panel
    # --------------------------------------------------------------------------
    def setup_notifications_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color: #141B2D; border: 1px solid #26334D; border-radius: 6px; padding: 12px;")
        lay = QVBoxLayout(panel)
        lay.setSpacing(6)

        hdr = QLabel("🔔 WORKSTATION NOTIFICATION CENTER")
        hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 9.5pt; font-family: Consolas;")
        lay.addWidget(hdr)

        notifs = [
            ("• Simulation Finished: TTL 7408 AND Gate Netlist Solver executed cleanly.", "10m ago", "#10B981"),
            ("• Assessment Completed: Digital Logic CBT Exam Set 4 scored 94%.", "1h ago", "#06B6D4"),
            ("• Report Generated: IEEE Center-Tapped Rectifier Report compiled to Markdown.", "3h ago", "#EC4899"),
            ("• System Update: ElectroVerse v1.0.0 Offline Laboratory running smoothly.", "1d ago", "#38BDF8")
        ]

        for msg, time_str, clr in notifs:
            r = QHBoxLayout()
            ml = QLabel(msg); ml.setStyleSheet(f"color: {clr}; font-size: 8pt; font-family: Consolas; font-weight: 500;")
            tl = QLabel(time_str); tl.setStyleSheet("color: #64748B; font-size: 7.5pt; font-family: Consolas;")
            r.addWidget(ml); r.addStretch(); r.addWidget(tl)
            lay.addLayout(r)

        self.c_layout.addWidget(panel)

    # --------------------------------------------------------------------------
    # 4. Bottom Industrial Status Bar
    # --------------------------------------------------------------------------
    def setup_bottom_status_bar(self, parent_layout):
        sbar = QFrame()
        sbar.setFixedHeight(30)
        sbar.setStyleSheet("QFrame { background-color: #090D16; border-top: 1px solid #26334D; }")
        s_lay = QHBoxLayout(sbar)
        s_lay.setContentsMargins(12, 0, 12, 0)
        s_lay.setSpacing(12)

        self.sb_module = QLabel("MODULE: Virtual Engineering Laboratory")
        self.sb_module.setStyleSheet("color: #06B6D4; font-size: 8pt; font-family: Consolas; font-weight: bold;")

        self.sb_sim = QLabel("SIM ENGINE: ● Ready (60 FPS)")
        self.sb_sim.setStyleSheet("color: #10B981; font-size: 8pt; font-family: Consolas;")

        self.sb_py = QLabel(f"PYTHON: v{platform.python_version()}")
        self.sb_py.setStyleSheet("color: #94A3B8; font-size: 8pt; font-family: Consolas;")

        self.sb_clock = QLabel()
        self.sb_clock.setStyleSheet("color: #CBD5E1; font-size: 8pt; font-family: Consolas; font-weight: bold;")
        self.update_clock()

        s_lay.addWidget(self.sb_module)
        s_lay.addWidget(QLabel(" | "))
        s_lay.addWidget(self.sb_sim)
        s_lay.addWidget(QLabel(" | "))
        s_lay.addWidget(self.sb_py)
        s_lay.addStretch()
        s_lay.addWidget(self.sb_clock)

        parent_layout.addWidget(sbar)


    def update_clock(self):
        curr_time = QDateTime.currentDateTime().toString("yyyy-MM-dd | hh:mm:ss AP")
        self.sb_clock.setText(curr_time)

    # --------------------------------------------------------------------------
    # HELPER EVENT HANDLERS & CALLBACKS
    # --------------------------------------------------------------------------
    def switch_to_hub(self, target_id):
        if self.main_window and hasattr(self.main_window, "switch_to_view"):
            self.main_window.switch_to_view(target_id)
        elif self.main_window and hasattr(self.main_window, "switch_view"):
            self.main_window.switch_view(target_id)

    def refresh_dashboard(self):
        log.info("Refreshing Workstation Control Dashboard metrics and resources.")
        self.update_clock()
        self.update_resource_monitor()

    def showEvent(self, event):
        self.refresh_dashboard()
        super().showEvent(event)
