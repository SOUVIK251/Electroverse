"""
Digital System Design Hub - Subject Learning Dashboard View
Dedicated landing screen for Digital System Design Hub.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from src.ui.components.hub_dashboard_base import (
    create_dashboard_banner, create_metric_card, create_quick_access_grid,
    create_module_cards_grid, create_activity_log_card, create_subject_widgets_panel
)


class DSDDashboardView(QWidget):
    """Subject Dashboard Landing Screen for Digital System Design Hub."""

    tab_jump_requested = Signal(int)  # Emits target tab index (1=Learn, 2=Practice, 3=Assessment, 4=Reference)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(6, 6, 6, 6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(12)

        # 1. Header Banner with Resume CTA
        banner = create_dashboard_banner(
            title="⚡ Digital System Design & VLSI Logic Engineering Suite",
            subtitle="Explore Boolean algebra, K-Map minimization, TTL 74xx logic ICs, combinational adders/MUXs, flip-flops & sequential counters.",
            tag="DIGITAL SYSTEM DESIGN DASHBOARD",
            resume_topic="IC 7408 AND Gate Breadboard Wiring Trainer",
            on_resume_cb=lambda: self.tab_jump_requested.emit(2)  # Jump to Practice (Tab 2)
        )
        lay.addWidget(banner)

        # 2. Metric Analytics Cards Row
        m_container = QFrame()
        m_lay = QVBoxLayout(m_container)
        m_lay.setContentsMargins(0, 0, 0, 0)
        
        r1 = QHBoxLayout()
        r1.addWidget(create_metric_card("fa5s.microchip", "IC EXPERIMENTS", "14 / 20", "TTL 74xx IC Series", "#06B6D4"))
        r1.addWidget(create_metric_card("fa5s.chart-line", "OVERALL PROGRESS", "65%", "Advanced Logic Level", "#10B981"))
        r1.addWidget(create_metric_card("fa5s.cogs", "TRAINER KIT SIMS", "22 Labs", "Pure Electrical Netlist", "#F59E0B"))
        r1.addWidget(create_metric_card("fa5s.clipboard-check", "ASSESSMENT ACCURACY", "92%", "Grade: A+ (Outstanding)", "#38BDF8"))
        r1.addWidget(create_metric_card("fa5s.clock", "PRACTICE TIME", "18.2 hrs", "Solderless Breadboard", "#EC4899"))
        
        m_lay.addLayout(r1)
        lay.addWidget(m_container)

        # 3. Quick Access Launchpad
        buttons_config = [
            ("📖 Learn Theory", "fa5s.book-open", "#06B6D4", lambda: self.tab_jump_requested.emit(1)),
            ("🧪 Breadboard Trainer Kit", "fa5s.microchip", "#F59E0B", lambda: self.tab_jump_requested.emit(2)),
            ("📝 CBT Exam Engine", "fa5s.file-signature", "#10B981", lambda: self.tab_jump_requested.emit(3)),
            ("📚 IC Pinout Matrix", "fa5s.th", "#EC4899", lambda: self.tab_jump_requested.emit(4)),
        ]
        lay.addWidget(create_quick_access_grid(buttons_config))

        # 4. Digital Subject Modules Grid
        dsd_modules = [
            {"title": "Number System", "icon": "fa5s.calculator", "color": "#06B6D4", "progress": 100, "topics_cnt": "Binary, Hex & BCD"},
            {"title": "Logic Gates", "icon": "fa5s.door-open", "color": "#F59E0B", "progress": 95, "topics_cnt": "AND, OR, NOT, NAND"},
            {"title": "Boolean Algebra", "icon": "fa5s.square-root-alt", "color": "#10B981", "progress": 90, "topics_cnt": "DeMorgan's Laws & SOP"},
            {"title": "K-Map", "icon": "fa5s.table", "color": "#38BDF8", "progress": 80, "topics_cnt": "2, 3 & 4 Variable Maps"},
            {"title": "Combinational Circuits", "icon": "fa5s.project-diagram", "color": "#A855F7", "progress": 70, "topics_cnt": "Adders, MUX & Decoders"},
            {"title": "Sequential Circuits", "icon": "fa5s.sync", "color": "#EC4899", "progress": 55, "topics_cnt": "SR, JK, D & T Flip-Flops"},
            {"title": "Counters", "icon": "fa5s.sort-numeric-up", "color": "#EAB308", "progress": 40, "topics_cnt": "Synchronous & Asynchronous"},
            {"title": "Registers", "icon": "fa5s.layer-group", "color": "#3B82F6", "progress": 30, "topics_cnt": "SIPO, PISO & Shift Registers"},
        ]
        lay.addWidget(create_module_cards_grid(dsd_modules, None))

        # 5. Recent Activity & Highlights
        dsd_activities = [
            ("• Completed Breadboard Trainer Kit Test: IC 7408 Pin 3 -> Y0 Net", "Today at 20:10", "#10B981"),
            ("• Verified 4-Variable K-Map Minimization (Don't Care conditions)", "Yesterday at 17:40", "#06B6D4"),
            ("• Simulated 2:1 MUX & 2:4 Decoder Output Routing", "2 days ago", "#F59E0B"),
            ("• Passed Combinational Logic CBT Exam (Score 95%)", "3 days ago", "#38BDF8")
        ]
        lay.addWidget(create_activity_log_card(dsd_activities))

        # 6. Educational Widgets
        widgets_config = [
            {
                "title": "Formula Spotlight: DeMorgan's Theorems",
                "icon": "fa5s.square-root-alt",
                "color": "#06B6D4",
                "text": "1. (A · B)' = A' + B'  (NAND equals Negative OR)\n2. (A + B)' = A' · B'  (NOR equals Negative AND)"
            },
            {
                "title": "Exam Tip: K-Map Grouping Rule",
                "icon": "fa5s.lightbulb",
                "color": "#F59E0B",
                "text": "Always group adjacent 1s in powers of 2 (1, 2, 4, 8, 16). Larger groups produce simpler simplified Boolean expressions!"
            },
            {
                "title": "Memory Trick: Universal Gates",
                "icon": "fa5s.brain",
                "color": "#10B981",
                "text": "NAND and NOR are Universal Gates because ANY logic function (AND, OR, NOT, XOR) can be constructed using ONLY NAND or ONLY NOR gates."
            },
            {
                "title": "Common Exam Mistake: JK Flip-Flop Toggle Mode",
                "icon": "fa5s.exclamation-triangle",
                "color": "#EC4899",
                "text": "When J=1 and K=1, the JK Flip-Flop toggles (Q_next = Q'). Avoid race-around condition by using edge-triggering or Master-Slave configuration!"
            }
        ]
        lay.addWidget(create_subject_widgets_panel(widgets_config))

        scroll.setWidget(container)
        main_lay.addWidget(scroll)
