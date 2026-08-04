"""
Analog Electronics Hub - Subject Learning Dashboard View
Dedicated landing screen for Analog Electronics Circuit Hub.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from PySide6.QtCore import Qt, Signal

from src.ui.components.hub_dashboard_base import (
    create_dashboard_banner, create_metric_card, create_quick_access_grid,
    create_module_cards_grid, create_activity_log_card, create_subject_widgets_panel
)


class AnalogDashboardView(QWidget):
    """Subject Dashboard Landing Screen for Analog Electronics Hub."""

    tab_jump_requested = Signal(int)  # Emits target tab index (1=Learn, 2=ProblemSolving, 3=Sim, 4=Assessment, 5=Ref)

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
            title="⚡ Analog Electronics & Semiconductor Circuit Engineering Suite",
            subtitle="Master P-N junction diodes, wave-shaping clippers/clampers, BJT/FET amplifiers, active filters, and 555 multivibrators.",
            tag="ANALOG ELECTRONICS DASHBOARD",
            resume_topic="Biased Positive Combination Clipper Circuit",
            on_resume_cb=lambda: self.tab_jump_requested.emit(3)  # Jump to Interactive Simulation (Tab 3)
        )
        lay.addWidget(banner)

        # 2. Metric Analytics Cards Row
        metrics_row = QVBoxLayout()
        m_container = QFrame()
        m_lay = QVBoxLayout(m_container)
        m_lay.setContentsMargins(0, 0, 0, 0)
        
        # Grid of metrics
        from PySide6.QtWidgets import QHBoxLayout
        r1 = QHBoxLayout()
        r1.addWidget(create_metric_card("fa5s.book-reader", "CURRICULUM FINISHED", "24 / 40", "60% Syllabus Complete", "#06B6D4"))
        r1.addWidget(create_metric_card("fa5s.chart-line", "OVERALL PROGRESS", "58%", "On Track for Distinction", "#10B981"))
        r1.addWidget(create_metric_card("fa5s.wave-square", "WAVEFORM SIMULATIONS", "16 Labs", "Clippers & Clampers Done", "#F59E0B"))
        r1.addWidget(create_metric_card("fa5s.clipboard-check", "ASSESSMENT AVERAGE", "86%", "Grade: A+ (Passed)", "#38BDF8"))
        r1.addWidget(create_metric_card("fa5s.stopwatch", "STUDY TIME", "14.5 hrs", "Active Hands-On Time", "#EC4899"))
        
        m_lay.addLayout(r1)
        lay.addWidget(m_container)

        # 3. Quick Access Launchpad
        buttons_config = [
            ("📖 Learn Theory", "fa5s.book-open", "#06B6D4", lambda: self.tab_jump_requested.emit(1)),
            ("🧠 Problem Solving", "fa5s.brain", "#A855F7", lambda: self.tab_jump_requested.emit(2)),
            ("🧪 Waveform Simulator", "fa5s.flask", "#F59E0B", lambda: self.tab_jump_requested.emit(3)),
            ("📝 CBT Assessment", "fa5s.file-signature", "#10B981", lambda: self.tab_jump_requested.emit(4)),
            ("📚 Formula Reference", "fa5s.bookmark", "#EC4899", lambda: self.tab_jump_requested.emit(5)),
        ]
        lay.addWidget(create_quick_access_grid(buttons_config))

        # 4. Analog Subject Modules Grid
        analog_modules = [
            {"title": "P-N Diodes", "icon": "fa5s.bolt", "color": "#06B6D4", "progress": 85, "topics_cnt": "5 Topics Completed"},
            {"title": "Clippers", "icon": "fa5s.cut", "color": "#F59E0B", "progress": 100, "topics_cnt": "7 Wave Shaping Sims"},
            {"title": "Clampers", "icon": "fa5s.arrows-alt-v", "color": "#10B981", "progress": 75, "topics_cnt": "4 DC Restorers"},
            {"title": "Rectifiers", "icon": "fa5s.microchip", "color": "#38BDF8", "progress": 90, "topics_cnt": "Half & Full Wave"},
            {"title": "Filters", "icon": "fa5s.filter", "color": "#A855F7", "progress": 50, "topics_cnt": "Low/High/Band Pass"},
            {"title": "Transistors", "icon": "fa5s.project-diagram", "color": "#EC4899", "progress": 40, "topics_cnt": "BJT & MOSFET Biasing"},
            {"title": "Op-Amps", "icon": "fa5s.compress-arrows-alt", "color": "#EAB308", "progress": 60, "topics_cnt": "Inverting & Summing"},
            {"title": "Multivibrators", "icon": "fa5s.clock", "color": "#3B82F6", "progress": 30, "topics_cnt": "555 Astable & Monostable"},
        ]
        lay.addWidget(create_module_cards_grid(analog_modules, None))

        # 5. Recent Activity & Highlights
        analog_activities = [
            ("• Simulated Biased Combination Clipper Waveform (±2.5V Bias)", "Today at 19:30", "#F59E0B"),
            ("• Analyzed Full-Wave Bridge Rectifier Ripple Factor (r = 0.48)", "Yesterday at 16:15", "#10B981"),
            ("• Designed 2nd-Order Sallen-Key Low Pass Active Filter (fc = 1 kHz)", "2 days ago", "#06B6D4"),
            ("• Solved BJT Voltage-Divider Bias Numerical Calculation (VCE = 6.2V)", "3 days ago", "#A855F7")
        ]
        lay.addWidget(create_activity_log_card(analog_activities))

        # 6. Educational Widgets (Formula Spotlight, Exam Tips, Mnemonic)
        widgets_config = [
            {
                "title": "Formula Spotlight: Clipper Transfer Characteristic",
                "icon": "fa5s.square-root-alt",
                "color": "#06B6D4",
                "text": "For a Positive Series Clipper with DC Bias V_B: V_out = V_in when V_in < V_B + V_γ. Above threshold, V_out = V_B + V_γ."
            },
            {
                "title": "Exam Tip: Clamper DC Shift Theorem",
                "icon": "fa5s.lightbulb",
                "color": "#F59E0B",
                "text": "Clamper circuits change the DC level of a signal without altering its peak-to-peak amplitude (V_p-p remains constant)."
            },
            {
                "title": "Memory Trick: Diode Bias Direction",
                "icon": "fa5s.brain",
                "color": "#10B981",
                "text": "Forward Bias: Anode connected to Positive (+), Cathode to Negative (-). Arrow points in direction of conventional current flow!"
            },
            {
                "title": "Common Exam Mistake: Rectifier PIV",
                "icon": "fa5s.exclamation-triangle",
                "color": "#EC4899",
                "text": "Don't confuse Peak Inverse Voltage (PIV)! Center-Tapped Full-Wave PIV = 2 V_m, while Bridge Rectifier PIV = V_m."
            }
        ]
        lay.addWidget(create_subject_widgets_panel(widgets_config))

        scroll.setWidget(container)
        main_lay.addWidget(scroll)
