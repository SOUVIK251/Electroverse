import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager

FACTS = [
    "The electric eel can generate discharge voltages up to 860V to stun prey.",
    "The resistor color code was established in the 1920s by the Radio Manufacturers Association.",
    "Maxwell's equations unified electricity, magnetism, and light into one electromagnetic theory.",
    "Lightning strikes heat the air to 30,000 K - five times hotter than the sun's surface.",
    "Superconductivity is the complete loss of electrical resistance in materials cooled below critical temps.",
    "The first solid-state transistor was successfully tested at Bell Labs in December 1947."
]

TIPS = [
    "Decoupling capacitors filter high-frequency noise. Place them closest to IC power supply pins.",
    "To maximize power transfer, match the load resistance to the internal source resistance.",
    "Always keep return current loops small to minimize parasitic EMI emissions.",
    "Resistive dividers change voltage based on load. Ensure load impedance is at least 10x higher."
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

class DashboardView(QWidget):
    """Redesigned professional dashboard providing an IDE-like engineering workspace."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing DashboardView")
        
        # Outer Scroll Area for responsive sizing
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # -------------------------------------------------------------
        # Left Workspace Column
        # -------------------------------------------------------------
        self.left_col = QVBoxLayout()
        self.left_col.setSpacing(20)
        
        # Welcome Panel Card
        self.setup_welcome_card()
        
        # Statistics Widget Grid
        self.setup_stats_cards()
        
        # Engineering Fact of the Day Panel
        self.setup_fact_card()
        
        self.left_col.addStretch()
        self.layout.addLayout(self.left_col, stretch=3)

        # -------------------------------------------------------------
        # Right Control Panel Column
        # -------------------------------------------------------------
        self.right_col = QVBoxLayout()
        self.right_col.setSpacing(20)

        # Quick Actions Launcher Panel
        self.setup_launcher_card()
        
        # Recent & Favorite Calculators Lists
        self.setup_activity_lists()
        
        # Quick Learning Tips Box
        self.setup_tips_card()
        
        self.right_col.addStretch()
        self.layout.addLayout(self.right_col, stretch=2)

        # Dynamic state loader
        self.refresh_dashboard()

    def setup_welcome_card(self):
        """Creates the brand greeting hero banner."""
        card = QFrame()
        card.setObjectName("card-panel")
        
        # Glassmorphic style with neon emerald accent
        card.setStyleSheet("QFrame#card-panel { border-left: 5px solid #10b981; }")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("ElectroVerse – Engineering Workspace")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #f8fafc;")
        
        desc = QLabel("Welcome to your virtual electronics laboratory. Perform component sweeps, "
                      "analyze time-domain signals, calculate equations, and export reports in real-time.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 10.5pt; line-height: 1.5; margin-top: 10px;")
        
        layout.addWidget(title)
        layout.addWidget(desc)
        self.left_col.addWidget(card)

    def setup_stats_cards(self):
        """Builds stat boxes showing tool counts and user bookmarks."""
        stats_widget = QWidget()
        grid = QGridLayout(stats_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(15)

        # 1. Total Calculators Card
        c1 = QFrame()
        c1.setObjectName("card-panel")
        l1 = QVBoxLayout(c1)
        l1.setContentsMargins(15, 15, 15, 15)
        val1 = QLabel("11")
        val1.setStyleSheet("font-size: 26pt; font-weight: bold; color: #06b6d4;")
        lbl1 = QLabel("Toolkit Calculators")
        lbl1.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
        l1.addWidget(val1)
        l1.addWidget(lbl1)
        grid.addWidget(c1, 0, 0)

        # 2. Favorites Card
        self.c2 = QFrame()
        self.c2.setObjectName("card-panel")
        l2 = QVBoxLayout(self.c2)
        l2.setContentsMargins(15, 15, 15, 15)
        self.val2 = QLabel("0")
        self.val2.setStyleSheet("font-size: 26pt; font-weight: bold; color: #ef4444;")
        lbl2 = QLabel("Bookmarked Tools")
        lbl2.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
        l2.addWidget(self.val2)
        l2.addWidget(lbl2)
        grid.addWidget(self.c2, 0, 1)

        # 3. Lab Modules Card
        c3 = QFrame()
        c3.setObjectName("card-panel")
        l3 = QVBoxLayout(c3)
        l3.setContentsMargins(15, 15, 15, 15)
        val3 = QLabel("10")
        val3.setStyleSheet("font-size: 26pt; font-weight: bold; color: #10b981;")
        lbl3 = QLabel("Active Lab Modules")
        lbl3.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
        l3.addWidget(val3)
        l3.addWidget(lbl3)
        grid.addWidget(c3, 0, 2)

        self.left_col.addWidget(stats_widget)

    def setup_fact_card(self):
        """Creates the Fact of the Day panel with random facts."""
        self.fact_card = QFrame()
        self.fact_card.setObjectName("card-panel")
        layout = QVBoxLayout(self.fact_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.lightbulb", color="#e2e8f0").pixmap(18, 18))
        title = QLabel("Engineering Fact of the Day")
        title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.fact_text = QLabel(random.choice(FACTS))
        self.fact_text.setWordWrap(True)
        self.fact_text.setStyleSheet("color: #94a3b8; line-height: 1.45; font-size: 10pt;")
        layout.addWidget(self.fact_text)

        self.left_col.addWidget(self.fact_card)

    def setup_launcher_card(self):
        """Quick launch quick navigation shortcuts panel."""
        card = QFrame()
        card.setObjectName("card-panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("IDE Shortcuts Panel")
        title.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 11pt;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        actions = [
            ("Component Library", "fa5s.book", 1),
            ("Learning Mode", "fa5s.graduation-cap", 2),
            ("Engineering Toolkit", "fa5s.tools", 3),
            ("Simulation Lab", "fa5s.flask", 4)
        ]

        for i, (label, icon_str, view_idx) in enumerate(actions):
            btn = QPushButton(f" {label}")
            btn.setIcon(qta.icon(icon_str, color="#ffffff"))
            btn.setIconSize(QSize(14, 14))
            btn.setFixedHeight(38)
            # Custom click router
            btn.clicked.connect(lambda chk=False, idx=view_idx: self.parent().switch_view(idx))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        self.right_col.addWidget(card)

    def setup_activity_lists(self):
        """Creates lists showing recent calculations and favorite instruments."""
        self.activity_card = QFrame()
        self.activity_card.setObjectName("card-panel")
        self.activity_layout = QVBoxLayout(self.activity_card)
        self.activity_layout.setContentsMargins(20, 20, 20, 20)
        self.activity_layout.setSpacing(12)

        self.right_col.addWidget(self.activity_card)

    def setup_tips_card(self):
        """Learning focus card."""
        card = QFrame()
        card.setObjectName("card-panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.info-circle", color="#06b6d4").pixmap(18, 18))
        title = QLabel("Pro Design Tip")
        title.setStyleSheet("font-weight: bold; color: #06b6d4; font-size: 11pt;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        tip_lbl = QLabel(random.choice(TIPS))
        tip_lbl.setWordWrap(True)
        tip_lbl.setStyleSheet("color: #94a3b8; line-height: 1.4; font-size: 9.5pt;")
        layout.addWidget(tip_lbl)

        self.right_col.addWidget(card)

    def refresh_dashboard(self):
        """Reloads bookmarks and activity lists dynamically."""
        # 1. Favorites count
        fav_list = config_manager.get("favorites") or []
        self.val2.setText(str(len(fav_list)))

        # 2. Clear dynamic list elements in list card
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add Favorite tools title
        fav_title = QLabel("Favorite Instruments")
        fav_title.setStyleSheet("font-weight: bold; color: #ef4444; font-size: 11pt; margin-top: 5px;")
        self.activity_layout.addWidget(fav_title)

        if fav_list:
            for item in fav_list:
                try:
                    idx = int(item)
                    btn = QPushButton(f"  {CALCULATOR_NAMES[idx]}")
                    btn.setIcon(qta.icon("fa5s.star", color="#f59e0b"))
                    btn.setObjectName("secondary")
                    btn.setIconSize(QSize(12, 12))
                    btn.clicked.connect(lambda chk=False, target_idx=idx: self.open_calculator(target_idx))
                    self.activity_layout.addWidget(btn)
                except Exception as e:
                    log.error(f"Error listing favorite: {e}")
        else:
            empty_lbl = QLabel("No bookmarks selected.")
            empty_lbl.setStyleSheet("color: #475569; font-style: italic; font-size: 9.5pt; padding: 5px;")
            self.activity_layout.addWidget(empty_lbl)

        # Add Recent Activity section
        rec_title = QLabel("Recent Calculations")
        rec_title.setStyleSheet("font-weight: bold; color: #10b981; font-size: 11pt; margin-top: 15px;")
        self.activity_layout.addWidget(rec_title)

        recent_list = config_manager.get("recently_used") or []
        # Filter duplicates keeping ordering
        seen = set()
        recent_filtered = []
        for r in recent_list:
            if r not in seen:
                seen.add(r)
                recent_filtered.append(r)
        
        # Display max 3 recent calculations
        recent_filtered = recent_filtered[:3]

        if recent_filtered:
            for item in recent_filtered:
                try:
                    idx = int(item)
                    btn = QPushButton(f"  {CALCULATOR_NAMES[idx]}")
                    btn.setIcon(qta.icon("fa5s.history", color="#10b981"))
                    btn.setObjectName("secondary")
                    btn.setIconSize(QSize(12, 12))
                    btn.clicked.connect(lambda chk=False, target_idx=idx: self.open_calculator(target_idx))
                    self.activity_layout.addWidget(btn)
                except Exception as e:
                    log.error(f"Error listing recent: {e}")
        else:
            empty_lbl = QLabel("No recent calculations found.")
            empty_lbl.setStyleSheet("color: #475569; font-style: italic; font-size: 9.5pt; padding: 5px;")
            self.activity_layout.addWidget(empty_lbl)

    def open_calculator(self, idx: int):
        """Tells parent window to switch to Toolkit view and load selected index."""
        # parent() is MainWindow
        self.parent().switch_view(3) # Switch view stack to ToolkitView
        toolkit_view = self.parent().views[3]
        toolkit_view.list_widget.setCurrentRow(idx)

    def showEvent(self, event):
        """Called when dashboard view is displayed inside view stack."""
        self.refresh_dashboard()
        super().showEvent(event)

    def update_theme(self):
        """Dynamic stylesheet repaint trigger."""
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)
