import os
import sys
import random
import platform
import math
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QGridLayout, QScrollArea, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QBrush
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.ui.learning_content import get_lesson_data

TIPS = [
    "Always place a bypass capacitor close to the power pins of an IC to reduce supply noise.",
    "To maximize power transfer, match the load resistance to the internal source resistance.",
    "Ensure feedback loops in high-frequency amplifiers are as short as possible to prevent parasitic oscillations.",
    "For sensitive analog components, separate the analog and digital ground planes to avoid cross-talk.",
    "Use decoupling capacitors of different values (e.g. 10uF and 0.1uF) in parallel to filter both low and high frequency noise.",
    "When designing voltage dividers, make sure the load impedance is at least 10 times the output resistor value to avoid load loading errors."
]

CHALLENGES = [
    {
        "question": "Why is a Zener diode connected in reverse bias in voltage regulators?",
        "answer": "In reverse bias, a Zener diode operates in its breakdown region. Once the reverse voltage exceeds the Zener breakdown voltage ($V_Z$), the diode maintains a very stable voltage across its terminals despite large variations in input voltage or load current, providing voltage regulation."
    },
    {
        "question": "What is the main advantage of a Full-Wave Rectifier over a Half-Wave Rectifier?",
        "answer": "A full-wave rectifier utilizes both halves of the AC input cycle. This doubles the rectification efficiency, increases the average output DC voltage, and results in a ripple frequency that is twice the input AC frequency, making it much easier to filter and smooth."
    },
    {
        "question": "How does a capacitor behave in a DC circuit at steady-state?",
        "answer": "Initially, a capacitor charges up. Once fully charged (steady-state), the voltage across the capacitor equals the supply DC voltage, opposing any further charge flow. Therefore, it blocks all direct current, acting as an open circuit."
    },
    {
        "question": "What is the phase relationship between voltage and current in a purely inductive AC circuit?",
        "answer": "In a purely inductive circuit, the alternating current lags the applied voltage by exactly 90 degrees (or $\\pi/2$ radians). This is because the self-induced back-EMF opposes the change in current, delaying the current build-up."
    },
    {
        "question": "Why does a coaxial cable have a specific characteristic impedance (e.g., 50 Ohm or 75 Ohm)?",
        "answer": "The characteristic impedance is determined solely by the physical geometry (diameter of inner conductor and outer shield) and the dielectric constant of the insulating material. It is independent of cable length and ensures maximum power transfer and minimum reflection at high frequencies."
    }
]

FEATURED_EXPERIMENTS = [
    ("RC Charging/Discharging", 0, "Analyze transient charging and discharging waveforms of an RC network under square wave input."),
    ("RL Transient Response", 1, "Simulate current growth and decay curves in an RL circuit, illustrating inductive time constant effects."),
    ("Series RLC Resonance", 2, "Sweep AC signal frequencies to witness voltage amplification, impedance minimisation, and phase shifts at resonance."),
    ("Low Pass RC Filter", 3, "Explore frequency attenuation curves, phase angle sweeps, and cut-off frequencies for passive RC low-pass filters."),
    ("High Pass RC Filter", 4, "Explore passive high-pass filtering of AC inputs, showcasing cut-off sweeps and high-frequency passage."),
    ("Half-Wave Rectifier", 5, "Examine diode single-phase rectification, load effects, and ripple smoothing capacitors on the DSO."),
    ("Full-Wave Rectifier", 6, "Examine bridge rectifier operations, full-wave ripple frequency, and voltage regulation dynamics."),
    ("Signal Attenuation", 7, "Analyze passive resistor attenuation networks, examining decibel (dB) reduction levels on dual-channel DSO sweeps."),
    ("Voltage Divider Visual", 8, "Simulate division ratios under resistive load variations to analyze the impact of loading effects."),
    ("Resonance Explorer", 9, "Perform graphical scans of series vs parallel RLC curves, plotting magnitude sweeps across resonant bands.")
]

LESSON_LIST = [
    ("voltage", "Voltage Theory"),
    ("current", "Current & Electron Flow"),
    ("resistance", "Resistance & Ohm's Law"),
    ("ohm_law", "Ohm's Law Concepts"),
    ("kvl", "Kirchhoff's Voltage Law (KVL)"),
    ("kcl", "Kirchhoff's Current Law (KCL)"),
    ("resistor", "Resistor Construction"),
    ("capacitor", "Capacitor Energy Storage"),
    ("inductor", "Inductance & Magnetic Fields"),
    ("pn_diode", "PN Junction Diode Operation"),
    ("zener_diode", "Zener Diode Voltage Regulation"),
    ("led", "Light Emitting Diodes"),
    ("bjt", "Bipolar Junction Transistors"),
    ("mosfet", "MOSFET Switching Dynamics"),
    ("half_wave", "Half Wave Rectification"),
    ("full_wave", "Full Wave Bridge Rectifiers"),
    ("pos_clipper", "Positive Clipper Circuits"),
    ("neg_clipper", "Negative Clipper Circuits"),
    ("pos_clamper", "Positive Clamper Circuits"),
    ("neg_clamper", "Negative Clamper Circuits"),
    ("low_pass", "Low Pass Filter Sweeps"),
    ("high_pass", "High Pass Filter Sweeps"),
    ("rc_charging", "RC Transient Dynamics"),
    ("rlc_resonance", "RLC Resonance Sweeps")
]

CALCULATOR_NAMES = [
    "Ohm's Law Calculator",
    "Voltage Divider Calculator",
    "Current Divider Calculator",
    "Power Calculator",
    "RC Time Constant Calculator",
    "RL Time Constant Calculator",
    "RLC Resonance Calculator",
    "Frequency Calculator",
    "Capacitive Reactance Calculator",
    "Inductive Reactance Calculator",
    "LED Series Resistor Calculator"
]

class AnimatedWaveformWidget(QWidget):
    """Headless-safe vector waveform animation panel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.waveform_type = 0  # 0: Sine, 1: Square, 2: RC Charge, 3: RC Discharge, 4: AM, 5: FM
        
        # 30ms timer for smooth wave sweep (phase update)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_phase)
        self.anim_timer.start(30)
        
        # 5-second timer to rotate wave types
        self.rotate_timer = QTimer(self)
        self.rotate_timer.timeout.connect(self.rotate_waveform)
        self.rotate_timer.start(5000)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(150)
        
    def update_phase(self):
        self.phase += 0.08
        self.update()
        
    def rotate_waveform(self):
        self.waveform_type = (self.waveform_type + 1) % 6
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        centerY = height / 2
        
        # 1. Dark Grid Background
        painter.fillRect(0, 0, width, height, QColor("#0B1020"))
        grid_pen = QPen(QColor("#2B3245"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        
        # Draw vertical grid lines
        for x in range(0, width, 40):
            painter.drawLine(x, 0, x, height)
            
        # Draw horizontal grid lines
        for y in range(0, height, 40):
            painter.drawLine(0, y, width, y)
            
        # Center line
        painter.setPen(QPen(QColor("#4A5675"), 1.5, Qt.PenStyle.SolidLine))
        painter.drawLine(0, centerY, width, centerY)
        
        # 2. Compute Waveform Path
        path = QPainterPath()
        started = False
        
        # Adjust amplitude based on widget height (reduce slightly to avoid overflow)
        amp = height * 0.28
        
        wave_names = [
            "SINE WAVE SWEEP",
            "SQUARE WAVE PULSE",
            "RC TRANSIENT CHARGING",
            "RC TRANSIENT DISCHARGING",
            "AMPLITUDE MODULATION (AM)",
            "FREQUENCY MODULATION (FM)"
        ]
        
        for x in range(width):
            t = (x / width) * 4 * math.pi
            y = 0.0
            
            if self.waveform_type == 0:
                y = amp * math.sin(t - self.phase)
            elif self.waveform_type == 1:
                raw_val = math.sin(t - self.phase)
                y = amp * (1.0 if raw_val >= 0 else -1.0)
                if abs(raw_val) < 0.1:
                    y = amp * (raw_val / 0.1)
            elif self.waveform_type == 2:
                period_t = (t - self.phase) % (2 * math.pi)
                y = amp * (1.0 - 2.0 * math.exp(-period_t * 1.2))
            elif self.waveform_type == 3:
                period_t = (t - self.phase) % (2 * math.pi)
                y = amp * (-1.0 + 2.0 * math.exp(-period_t * 1.2))
            elif self.waveform_type == 4:
                modulator = 1.0 + 0.5 * math.sin(t * 0.2 - self.phase * 0.1)
                carrier = math.sin(t * 8.0 - self.phase)
                y = amp * 0.7 * modulator * carrier
            elif self.waveform_type == 5:
                mod_signal = math.sin(t * 0.5 - self.phase * 0.2)
                y = amp * math.sin(t * 8.0 + 3.0 * mod_signal)
                
            y_coord = centerY - y
            if not started:
                path.moveTo(x, y_coord)
                started = True
            else:
                path.lineTo(x, y_coord)
                
        # 3. Draw Waveform Path
        wave_pen = QPen(QColor("#06B6D4"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(wave_pen)
        painter.drawPath(path)
        
        # 4. Corner Info Label Overlay Card
        overlay_w = 270
        overlay_h = 38
        painter.setBrush(QBrush(QColor("#141B2D")))
        painter.setPen(QPen(QColor("#26334D"), 1))
        painter.drawRoundedRect(12, 10, overlay_w, overlay_h, 6, 6)
        
        painter.setPen(QColor("#06B6D4"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.drawText(20, 23, f"STATUS: DIGITAL SYSTEM DESIGN HUB OPERATIONAL")
        painter.setPen(QColor("#C9D1E3"))
        painter.drawText(20, 36, f"VISUALIZATION: {wave_names[self.waveform_type]}")
        painter.setBrush(Qt.BrushStyle.NoBrush)


class DashboardView(QWidget):
    """Redesigned professional Engineering Control Center dashboard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing redesigned DashboardView")
        
        # Initialize rotating content
        self.active_tip = random.choice(TIPS)
        self.active_challenge = random.choice(CHALLENGES)
        self.active_experiment = random.choice(FEATURED_EXPERIMENTS)
        
        # Get random lesson
        rand_lesson_id, rand_lesson_title = random.choice(LESSON_LIST)
        lesson_meta = get_lesson_data(rand_lesson_id)
        if lesson_meta:
            self.active_topic = {
                "id": rand_lesson_id,
                "title": lesson_meta.get("title", rand_lesson_title),
                "category": lesson_meta.get("category", "Basic Electronics"),
                "read_time": lesson_meta.get("read_time", "6 min read")
            }
        else:
            self.active_topic = {
                "id": "voltage",
                "title": "Voltage Concepts",
                "category": "Basic Electronics",
                "read_time": "5 min read"
            }
            
        self.challenge_revealed = False
        
        # Scroll Area container
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.container = QWidget()
        self.container.setObjectName("dashboard-container")
        self.scroll.setWidget(self.container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        # Outer container layout
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(25, 25, 25, 20)
        self.layout.setSpacing(20)
        
        # 1. Setup Header & System Status Banner
        self.setup_system_status_banner()
        
        # 2. Setup Global Search Bar
        self.setup_search_bar()
        
        # 3. Setup Metrics cards
        self.setup_metrics_row()
        
        # 4. Setup Workspace Launcher cards
        self.setup_workspace_launcher()
        
        # 5. Mid grid (Featured, Challenge, Tip)
        self.setup_mid_section()
        
        # 6. Bottom grid (Waveform, Activity, Updates)
        self.setup_bottom_section()
        self.setup_footer()
        self.refresh_dashboard()
        
    def setup_system_status_banner(self):
        banner = QFrame()
        banner.setObjectName("card-panel")
        banner.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-left: 5px solid #22C55E; border-radius: 10px; }")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(20, 15, 20, 15)
        
        text_layout = QVBoxLayout()
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 22pt; font-weight: bold; color: #22C55E;")
        title_layout.addWidget(logo)
        
        title_text = QLabel("ElectroVerse — Engineering Control Center")
        title_text.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FFFFFF;")
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        desc = QLabel("Headless-safe interactive electronic engineering design and analysis environment.")
        desc.setStyleSheet("color: #C9D1E3; font-size: 9.5pt;")
        
        text_layout.addLayout(title_layout)
        text_layout.addWidget(desc)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        sys_grid = QGridLayout()
        sys_grid.setHorizontalSpacing(20)
        sys_grid.setVerticalSpacing(4)
        labels = [("Version:", "v1.0.0"), ("Platform:", platform.system()), ("Theme:", "Dark Mode"), ("Modules Loaded:", "8"), ("Status:", "Ready")]
        for r, (key, val) in enumerate(labels):
            k_lbl = QLabel(key); k_lbl.setStyleSheet("color: #7A869A; font-weight: bold; font-size: 8.5pt;")
            v_lbl = QLabel(val); v_lbl.setStyleSheet("color: #22C55E; font-weight: bold; font-size: 8.5pt;" if key == "Status:" else "color: #C9D1E3; font-size: 8.5pt;")
            sys_grid.addWidget(k_lbl, r, 0); sys_grid.addWidget(v_lbl, r, 1)
        layout.addLayout(sys_grid)
        self.layout.addWidget(banner)
        
    def setup_search_bar(self):
        search_container = QWidget()
        layout = QVBoxLayout(search_container)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(5)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Components, Lessons, Simulations, Calculators, Q&As, Formulas...")
        self.search_input.setStyleSheet("""QLineEdit { background-color: #111827; border: 1px solid #26334D; border-radius: 8px; padding: 10px 15px; color: #FFFFFF; font-size: 11pt; } QLineEdit:focus { border-color: #06B6D4; }""")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        self.search_results_list = QListWidget()
        self.search_results_list.setStyleSheet("""QListWidget { background-color: #111827; border: 1px solid #06B6D4; border-radius: 8px; color: #FFFFFF; font-size: 10pt; padding: 5px; } QListWidget::item { padding: 8px 12px; border-bottom: 1px solid #26334D; } QListWidget::item:hover { background-color: #1B2740; color: #06B6D4; } QListWidget::item:selected { background-color: #1E3A5F; color: #06B6D4; }""")
        self.search_results_list.itemClicked.connect(self.on_search_item_clicked)
        self.search_results_list.setVisible(False); self.search_results_list.setMaximumHeight(200)
        layout.addWidget(self.search_results_list)
        self.layout.addWidget(search_container)

    def setup_metrics_row(self):
        row = QWidget(); layout = QHBoxLayout(row); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)
        metrics = [("91", "Components", "📚 Open Library", 1), ("29", "Lessons", "🎓 Open syllabus", 2), ("12", "Simulators", "🧪 Run simulations", 4), ("11", "Calculators", "🛠 Open calculators", 3), ("270+", "Q&A Questions", "🎓 Test knowledge", 2), ("60+", "Formulas", "🛠 Calculate formulas", 3)]
        for val, label, tooltip, view_idx in metrics:
            card = QFrame(); card.setObjectName("metric-card"); card.setStyleSheet("QFrame#metric-card { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; } QFrame#metric-card:hover { border-color: #06B6D4; background-color: #1B2740; }"); card.setCursor(Qt.CursorShape.PointingHandCursor); card.mousePressEvent = lambda event, idx=view_idx: self.window().switch_view(idx)
            c_layout = QVBoxLayout(card); c_layout.setContentsMargins(5, 5, 5, 5); c_layout.setSpacing(2)
            val_lbl = QLabel(val); val_lbl.setStyleSheet("font-size: 20pt; font-weight: 800; color: #38BDF8;"); lbl_lbl = QLabel(label); lbl_lbl.setStyleSheet("color: #FFFFFF; font-size: 9pt; font-weight: 600;"); tip_lbl = QLabel(tooltip); tip_lbl.setStyleSheet("color: #94A3B8; font-size: 7.5pt; font-style: italic;"); c_layout.addWidget(val_lbl); c_layout.addWidget(lbl_lbl); c_layout.addWidget(tip_lbl); layout.addWidget(card)
        self.layout.addWidget(row)

    def setup_workspace_launcher(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(10); header = QLabel("Quick Launch Workspace"); header.setStyleSheet("color: #06B6D4; font-size: 11pt; font-weight: bold; letter-spacing: 0.5px;"); layout.addWidget(header); grid = QGridLayout(); grid.setSpacing(15); shortcuts = [("Component Library", "📚 Browse electronic parts.", "fa5s.book", 1), ("Learning Mode", "🎓 Learn basic electronics theory.", "fa5s.graduation-cap", 2), ("Engineering Toolkit", "🛠 Run engineering calculation formulas.", "fa5s.tools", 3), ("Simulation Lab", "🧪 Open real-time transient solvers.", "fa5s.flask", 4), ("Digital System Design Hub", "⚡ Digital Electronics Learning Hub: Theory, Sequential Path, Breadboard Trainer & IC Matrix.", "fa5s.microchip", 5), ("Grand Viva Board", "🎓 Core viva and interview prep.", "fa5s.user-graduate", 6)]
        for i, (name, desc, icon, idx) in enumerate(shortcuts):
            card = QFrame(); card.setObjectName("launch-card"); card.setStyleSheet("QFrame#launch-card { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 15px; } QFrame#launch-card:hover { border-color: #06B6D4; background-color: #1B2740; }"); card.setCursor(Qt.CursorShape.PointingHandCursor); card.mousePressEvent = lambda event, target_idx=idx: self.window().switch_view(target_idx); c_layout = QHBoxLayout(card); c_layout.setContentsMargins(10, 10, 10, 10); c_layout.setSpacing(15); icon_lbl = QLabel(); icon_lbl.setPixmap(qta.icon(icon, color="#06B6D4").pixmap(24, 24)); c_layout.addWidget(icon_lbl); txt_layout = QVBoxLayout(); txt_layout.setSpacing(3); name_lbl = QLabel(name); name_lbl.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 11pt;"); desc_lbl = QLabel(desc); desc_lbl.setStyleSheet("color: #C9D1E3; font-size: 9pt;"); desc_lbl.setWordWrap(True); txt_layout.addWidget(name_lbl); txt_layout.addWidget(desc_lbl); c_layout.addLayout(txt_layout); grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid); self.layout.addWidget(widget)

    def setup_mid_section(self):
        row = QWidget(); layout = QHBoxLayout(row); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(20)
        self.featured_card = QFrame(); self.featured_card.setObjectName("card-panel"); self.featured_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #06B6D4; border-radius: 10px; }"); f_layout = QVBoxLayout(self.featured_card); f_layout.setContentsMargins(20, 20, 20, 20); f_layout.setSpacing(10); f_header = QHBoxLayout(); f_icon = QLabel(); f_icon.setPixmap(qta.icon("fa5s.flask", color="#06B6D4").pixmap(18, 18)); f_title = QLabel("Featured Experiment"); f_title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 11pt;"); f_header.addWidget(f_icon); f_header.addWidget(f_title); f_header.addStretch(); f_layout.addLayout(f_header); name_lbl, sim_idx, exp_desc = self.active_experiment; self.f_name_lbl = QLabel(name_lbl); self.f_name_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #06B6D4;"); self.f_desc_lbl = QLabel(exp_desc); self.f_desc_lbl.setStyleSheet("color: #C9D1E3; font-size: 9.5pt;"); self.f_desc_lbl.setWordWrap(True); f_btn = QPushButton(" Launch Experiment"); f_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 8px 16px; border-radius: 10px;"); f_btn.setIcon(qta.icon("fa5s.play", color="#ffffff")); f_btn.clicked.connect(lambda: self.window().navigate_to_simulation(sim_idx)); f_layout.addWidget(self.f_name_lbl); f_layout.addWidget(self.f_desc_lbl); f_layout.addStretch(); f_layout.addWidget(f_btn); layout.addWidget(self.featured_card)
        self.challenge_card = QFrame(); self.challenge_card.setObjectName("card-panel"); self.challenge_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #EF4444; border-radius: 10px; }"); c_layout = QVBoxLayout(self.challenge_card); c_layout.setContentsMargins(20, 20, 20, 20); c_layout.setSpacing(10); c_header = QHBoxLayout(); c_icon = QLabel(); c_icon.setPixmap(qta.icon("fa5s.brain", color="#EF4444").pixmap(18, 18)); c_title = QLabel("Today's Engineering Challenge"); c_title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 11pt;"); c_header.addWidget(c_icon); c_header.addWidget(c_title); c_header.addStretch(); c_layout.addLayout(c_header); self.c_question_lbl = QLabel(self.active_challenge["question"]); self.c_question_lbl.setStyleSheet("font-size: 10pt; font-weight: bold; color: #C9D1E3;"); self.c_question_lbl.setWordWrap(True); self.c_answer_lbl = QLabel(self.active_challenge["answer"]); self.c_answer_lbl.setStyleSheet("color: #22C55E; font-size: 9.5pt; background-color: #111827; padding: 8px; border-radius: 6px; border: 1px solid #26334D;"); self.c_answer_lbl.setWordWrap(True); self.c_answer_lbl.setVisible(False); self.c_btn = QPushButton("Reveal Answer"); self.c_btn.setObjectName("secondary"); self.c_btn.clicked.connect(self.toggle_challenge_answer); c_layout.addWidget(self.c_question_lbl); c_layout.addWidget(self.c_answer_lbl); c_layout.addStretch(); c_layout.addWidget(self.c_btn); layout.addWidget(self.challenge_card)
        self.topic_card = QFrame(); self.topic_card.setObjectName("card-panel"); self.topic_card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-top: 3px solid #22C55E; border-radius: 10px; }"); t_layout = QVBoxLayout(self.topic_card); t_layout.setContentsMargins(20, 20, 20, 20); t_layout.setSpacing(10); t_header = QHBoxLayout(); t_icon = QLabel(); t_icon.setPixmap(qta.icon("fa5s.graduation-cap", color="#22C55E").pixmap(18, 18)); t_title = QLabel("Recommended Topic"); t_title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 11pt;"); t_header.addWidget(t_icon); t_header.addWidget(t_title); t_header.addStretch(); t_layout.addLayout(t_header); self.t_name_lbl = QLabel(self.active_topic["title"]); self.t_name_lbl.setStyleSheet("font-size: 12pt; font-weight: bold; color: #22C55E;"); self.t_desc_lbl = QLabel(f"Category: {self.active_topic['category']}\nReading Time: {self.active_topic['read_time']}"); self.t_desc_lbl.setStyleSheet("color: #C9D1E3; font-size: 9.5pt; line-height: 1.4;"); t_btn = QPushButton(" Start Study"); t_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 8px 16px; border-radius: 10px;"); t_btn.setIcon(qta.icon("fa5s.book-reader", color="#ffffff")); t_btn.clicked.connect(lambda: self.window().navigate_to_lesson(self.active_topic["id"])); t_layout.addWidget(self.t_name_lbl); t_layout.addWidget(self.t_desc_lbl); t_layout.addStretch(); t_layout.addWidget(t_btn); layout.addWidget(self.topic_card); self.layout.addWidget(row)

    def toggle_challenge_answer(self):
        self.challenge_revealed = not self.challenge_revealed
        self.c_answer_lbl.setVisible(self.challenge_revealed)
        self.c_btn.setText("Hide Answer" if self.challenge_revealed else "Reveal Answer")

    def setup_bottom_section(self):
        row = QWidget(); layout = QHBoxLayout(row); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(20)
        anim_card = QFrame(); anim_card.setObjectName("card-panel"); anim_layout = QVBoxLayout(anim_card); anim_layout.setContentsMargins(15, 15, 15, 15); anim_layout.setSpacing(10); anim_lbl = QLabel("Scientific Visualization Engine"); anim_lbl.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;"); anim_layout.addWidget(anim_lbl); self.wave_widget = AnimatedWaveformWidget(self); anim_layout.addWidget(self.wave_widget); layout.addWidget(anim_card, stretch=2)
        self.favorite_card = QFrame(); self.favorite_card.setObjectName("card-panel"); self.fav_layout = QVBoxLayout(self.favorite_card); self.fav_layout.setContentsMargins(15, 15, 15, 15); self.fav_layout.setSpacing(10); layout.addWidget(self.favorite_card, stretch=1.2)
        right_panel = QWidget(); r_layout = QVBoxLayout(right_panel); r_layout.setContentsMargins(0, 0, 0, 0); r_layout.setSpacing(15); up_card = QFrame(); up_card.setObjectName("card-panel"); up_layout = QVBoxLayout(up_card); up_layout.setContentsMargins(15, 15, 15, 15); up_layout.setSpacing(8); up_header = QLabel("🆕 Recent Updates"); up_header.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;"); up_layout.addWidget(up_header); updates = ["✓ Digital System Design Hub Integrated", "✓ Added 74-Series TTL IC Trainer & Breadboard", "✓ Interactive Logic Analyzer & Waveform Timing Graphs", "✓ Added Cross-Module Inspector & Learning Links"];
        for up in updates: up_lbl = QLabel(up); up_lbl.setStyleSheet("color: #94a3b8; font-size: 9.5pt;"); up_layout.addWidget(up_lbl)
        r_layout.addWidget(up_card); tip_card = QFrame(); tip_card.setObjectName("card-panel"); tip_layout = QVBoxLayout(tip_card); tip_layout.setContentsMargins(15, 15, 15, 15); tip_layout.setSpacing(8); tip_header = QHBoxLayout(); tip_icon = QLabel(); tip_icon.setPixmap(qta.icon("fa5s.lightbulb", color="#e2e8f0").pixmap(14, 14)); tip_title = QLabel("Engineering Tip"); tip_title.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 11pt;"); tip_header.addWidget(tip_icon); tip_header.addWidget(tip_title); tip_header.addStretch(); tip_layout.addLayout(tip_header); self.tip_lbl = QLabel(self.active_tip); self.tip_lbl.setStyleSheet("color: #94a3b8; font-size: 9pt; line-height: 1.4;"); self.tip_lbl.setWordWrap(True); tip_layout.addWidget(self.tip_lbl); r_layout.addWidget(tip_card); layout.addWidget(right_panel, stretch=1); self.layout.addWidget(row)

    def setup_footer(self):
        self.footer = QLabel("ElectroVerse Virtual Engineering Laboratory   |   Version 1.0.0   |   Created & Developed by Souvik Kundu   |   Python • PySide6 • NumPy • Matplotlib   |   © 2026")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter); self.footer.setStyleSheet("color: #475569; font-size: 8.5pt; font-weight: bold; border-top: 1px solid rgba(255, 255, 255, 0.03); padding-top: 15px; margin-top: 20px;"); self.layout.addWidget(self.footer)

    def on_search_text_changed(self, text):
        if not text.strip(): self.search_results_list.setVisible(False); return
        text = text.lower().strip(); self.search_results_list.clear(); components_db = {}
        library_view = self.window().views[1] if hasattr(self.window(), "views") else None
        if library_view and hasattr(library_view, "components_db"): components_db = library_view.components_db
        comp_matches = []; lesson_matches = []; sim_matches = []; calc_matches = []; qa_matches = []; tip_matches = []; formula_matches = []
        for comp_id, comp in components_db.items():
            if text in comp["name"].lower() or text in comp.get("short_description", "").lower(): comp_matches.append((comp["name"], "comp", comp_id))
            if "formulas" in comp:
                form_val = comp["formulas"]
                if isinstance(form_val, list):
                    for f in form_val:
                        if isinstance(f, dict) and text in f.get("name", "").lower():
                            formula_matches.append((f"Formula: {f['name']} (in {comp['name']})", "comp", comp_id))
                elif isinstance(form_val, str):
                    if text in form_val.lower():
                        formula_matches.append((f"Formula in {comp['name']}", "comp", comp_id))
            if "interview_questions" in comp:
                qa_val = comp["interview_questions"]
                if isinstance(qa_val, list):
                    for qa in qa_val:
                        if isinstance(qa, dict) and (text in qa.get("question", "").lower() or text in qa.get("answer", "").lower()):
                            qa_matches.append((f"Q&A: {qa['question']}", "comp", comp_id))
        for lesson_id, lesson_title in LESSON_LIST:
            lesson_meta = get_lesson_data(lesson_id)
            if lesson_meta:
                title = lesson_meta.get("title", lesson_title)
                if text in title.lower(): lesson_matches.append((title, "lesson", lesson_id))
                if "formulas" in lesson_meta:
                    for f in lesson_meta["formulas"]:
                        if text in f.get("name", "").lower(): formula_matches.append((f"Formula: {f['name']} (in {title})", "lesson", lesson_id))
        for name, idx, desc in FEATURED_EXPERIMENTS:
            if text in name.lower() or text in desc.lower(): sim_matches.append((name, "sim", idx))
        for idx, name in enumerate(CALCULATOR_NAMES):
            if text in name.lower(): calc_matches.append((name, "calc", idx))
        for tip in TIPS:
            if text in tip.lower(): tip_matches.append((f"Tip: {tip[:45]}...", "tip", tip))
        total_results = 0; groups = [("Components", comp_matches), ("Lessons", lesson_matches), ("Simulations", sim_matches), ("Calculators", calc_matches), ("Formulas", formula_matches), ("Q&As", qa_matches), ("Tips", tip_matches)]
        for group_name, matches in groups:
            if matches:
                header_item = QListWidgetItem(f"--- {group_name} ---"); header_item.setFlags(Qt.ItemFlag.NoItemFlags); header_item.setForeground(QColor("#06b6d4")); self.search_results_list.addItem(header_item)
                for label, target_type, target_val in matches[:4]: item = QListWidgetItem(f"   {label}"); item.setData(Qt.ItemDataRole.UserRole, (target_type, target_val)); self.search_results_list.addItem(item); total_results += 1
        self.search_results_list.setVisible(total_results > 0)

    def on_search_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data: return
        target_type, target_val = data; self.search_input.clear(); self.search_results_list.setVisible(False); win = self.window()
        if target_type == "comp": win.navigate_to_component(target_val)
        elif target_type == "lesson": win.navigate_to_lesson(target_val)
        elif target_type == "sim": win.navigate_to_simulation(target_val)
        elif target_type == "calc": win.navigate_to_calculator(target_val)
        elif target_type == "tip": win.show_toast(target_val)

    def refresh_dashboard(self):
        fav_list = config_manager.get("favorites") or []
        while self.fav_layout.count():
            child = self.fav_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        fav_header = QHBoxLayout(); fav_icon = QLabel(); fav_icon.setPixmap(qta.icon("fa5s.star", color="#f59e0b").pixmap(14, 14)); fav_title = QLabel("⭐ Favorite Components"); fav_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;"); fav_header.addWidget(fav_icon); fav_header.addWidget(fav_title); fav_header.addStretch(); self.fav_layout.addLayout(fav_header)
        if fav_list:
            for comp_id in fav_list:
                comp_name = comp_id.replace("_", " ").title(); btn = QPushButton(f"  {comp_name}"); btn.setIcon(qta.icon("fa5s.star", color="#f59e0b")); btn.setObjectName("secondary"); btn.setIconSize(QSize(12, 12)); btn.clicked.connect(lambda checked=False, cid=comp_id: self.window().navigate_to_component(cid)); self.fav_layout.addWidget(btn)
        else: empty_lbl = QLabel("No components starred."); empty_lbl.setStyleSheet("color: #475569; font-style: italic; font-size: 9pt;"); empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.fav_layout.addWidget(empty_lbl)
        self.fav_layout.addSpacing(15); act_header = QHBoxLayout(); act_icon = QLabel(); act_icon.setPixmap(qta.icon("fa5s.history", color="#10b981").pixmap(14, 14)); act_title = QLabel("Recent Activity"); act_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;"); act_header.addWidget(act_icon); act_header.addWidget(act_title); act_header.addStretch(); self.fav_layout.addLayout(act_header); self.refresh_activity_logs()

    def refresh_activity_logs(self):
        win = self.window()
        if hasattr(win, "session_activity") and win.session_activity:
            for act in win.session_activity:
                lbl = QLabel(f"• {act}")
                lbl.setStyleSheet("color: #94a3b8; font-size: 9pt; padding-left: 5px;")
                lbl.setWordWrap(True)
                self.fav_layout.addWidget(lbl)
        else:
            empty_lbl = QLabel("No activity yet.\nLaunch a module to begin.")
            empty_lbl.setStyleSheet("color: #475569; font-style: italic; font-size: 9pt; line-height: 1.3;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fav_layout.addWidget(empty_lbl)
            
        self.fav_layout.addStretch()
        
    def showEvent(self, event):
        """Triggers dynamic stats updates and rotates Featured/Recommended elements."""
        self.refresh_dashboard()
        self.active_tip = random.choice(TIPS)
        self.active_challenge = random.choice(CHALLENGES)
        self.active_experiment = random.choice(FEATURED_EXPERIMENTS)
        
        self.tip_lbl.setText(self.active_tip)
        self.c_question_lbl.setText(self.active_challenge["question"])
        self.c_answer_lbl.setText(self.active_challenge["answer"])
        self.c_answer_lbl.setVisible(False)
        self.challenge_revealed = False
        self.c_btn.setText("Reveal Answer")
        
        name_lbl, sim_idx, exp_desc = self.active_experiment
        self.f_name_lbl.setText(name_lbl)
        self.f_desc_lbl.setText(exp_desc)
        
        rand_lesson_id, rand_lesson_title = random.choice(LESSON_LIST)
        lesson_meta = get_lesson_data(rand_lesson_id)
        if lesson_meta:
            self.active_topic = {
                "id": rand_lesson_id,
                "title": lesson_meta.get("title", rand_lesson_title),
                "category": lesson_meta.get("category", "Basic Electronics"),
                "read_time": lesson_meta.get("read_time", "6 min read")
            }
        else:
            self.active_topic = {
                "id": "voltage",
                "title": "Voltage Concepts",
                "category": "Basic Electronics",
                "read_time": "5 min read"
            }
        self.t_name_lbl.setText(self.active_topic["title"])
        self.t_desc_lbl.setText(f"Category: {self.active_topic['category']}\nReading Time: {self.active_topic['read_time']}")
        
        super().showEvent(event)
        
    def update_theme(self):
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)

