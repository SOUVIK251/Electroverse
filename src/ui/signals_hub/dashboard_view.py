"""
Signal & System Hub - Subject Learning Dashboard View
Dedicated landing screen for Signal & System Hub.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from src.ui.components.hub_dashboard_base import (
    create_dashboard_banner, create_metric_card, create_quick_access_grid,
    create_module_cards_grid, create_activity_log_card, create_subject_widgets_panel
)


class SignalsDashboardView(QWidget):
    """Subject Dashboard Landing Screen for Signal & System Hub."""

    tab_jump_requested = Signal(int)  # Emits target tab index (1=Learn, 2=Interactive Simulation, 3=Assessment, 4=Reference)

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
            title="⚡ Signal & System Engineering & Mathematical Transform Suite",
            subtitle="Analyze continuous/discrete signals, LTI systems, convolution integral, Fourier series/transforms, Laplace s-plane & Z-transform ROC.",
            tag="SIGNAL & SYSTEM DASHBOARD",
            resume_topic="Continuous Convolution & LTI Response Lab",
            on_resume_cb=lambda: self.tab_jump_requested.emit(2)  # Jump to Interactive Simulation (Tab 2)
        )
        lay.addWidget(banner)

        # 2. Metric Analytics Cards Row
        m_container = QFrame()
        m_lay = QVBoxLayout(m_container)
        m_lay.setContentsMargins(0, 0, 0, 0)
        
        r1 = QHBoxLayout()
        r1.addWidget(create_metric_card("fa5s.chart-line", "CURRICULUM FINISHED", "20 / 32", "62% Modules Covered", "#06B6D4"))
        r1.addWidget(create_metric_card("fa5s.chart-bar", "OVERALL PROGRESS", "54%", "Intermediate Level", "#10B981"))
        r1.addWidget(create_metric_card("fa5s.wave-square", "GRAPH SIMULATIONS", "15 Labs", "Convolution & FFT", "#F59E0B"))
        r1.addWidget(create_metric_card("fa5s.clipboard-check", "ASSESSMENT AVERAGE", "88%", "Grade: A (Passed)", "#38BDF8"))
        r1.addWidget(create_metric_card("fa5s.history", "STUDY TIME", "12.8 hrs", "Interactive Plotting", "#EC4899"))
        
        m_lay.addLayout(r1)
        lay.addWidget(m_container)

        # 3. Quick Access Launchpad
        buttons_config = [
            ("📖 Learn Theory", "fa5s.book-open", "#06B6D4", lambda: self.tab_jump_requested.emit(1)),
            ("🧪 Signal & Graph Simulator", "fa5s.chart-area", "#F59E0B", lambda: self.tab_jump_requested.emit(2)),
            ("📝 CBT Exam Engine", "fa5s.file-signature", "#10B981", lambda: self.tab_jump_requested.emit(3)),
            ("📚 Transform Tables & Formulas", "fa5s.table", "#EC4899", lambda: self.tab_jump_requested.emit(4)),
        ]
        lay.addWidget(create_quick_access_grid(buttons_config))

        # 4. Signal & System Subject Modules Grid
        signals_modules = [
            {"title": "Signals", "icon": "fa5s.wave-square", "color": "#06B6D4", "progress": 90, "topics_cnt": "Continuous & Discrete"},
            {"title": "Systems", "icon": "fa5s.project-diagram", "color": "#F59E0B", "progress": 85, "topics_cnt": "LTI, Causality & Stability"},
            {"title": "Convolution", "icon": "fa5s.layer-group", "color": "#10B981", "progress": 75, "topics_cnt": "Continuous & Discrete Integral"},
            {"title": "Fourier Series", "icon": "fa5s.chart-line", "color": "#38BDF8", "progress": 65, "topics_cnt": "Trigonometric & Complex"},
            {"title": "Fourier Transform", "icon": "fa5s.bolt", "color": "#A855F7", "progress": 50, "topics_cnt": "CTFT, DTFT & Spectrum"},
            {"title": "Laplace Transform", "icon": "fa5s.square-root-alt", "color": "#EC4899", "progress": 45, "topics_cnt": "s-Plane Pole-Zero & ROC"},
            {"title": "Z Transform", "icon": "fa5s.dot-circle", "color": "#EAB308", "progress": 35, "topics_cnt": "z-Domain & Inverse ZT"},
            {"title": "Sampling", "icon": "fa5s.random", "color": "#3B82F6", "progress": 25, "topics_cnt": "Nyquist Theorem & Aliasing"},
        ]
        lay.addWidget(create_module_cards_grid(signals_modules, None))

        # 5. Recent Activity & Highlights
        signals_activities = [
            ("• Analyzed Continuous Convolution y(t) = x(t) * h(t) Integral Plot", "Today at 18:50", "#10B981"),
            ("• Plotted Fast Fourier Transform (FFT) Magnitude & Phase Spectrum", "Yesterday at 15:20", "#06B6D4"),
            ("• Computed Laplace Transform Pole-Zero Map & ROC Stability", "2 days ago", "#F59E0B"),
            ("• Evaluated Nyquist Sampling Rate Criteria (fs >= 2 fm)", "3 days ago", "#A855F7")
        ]
        lay.addWidget(create_activity_log_card(signals_activities))

        # 6. Educational Widgets
        widgets_config = [
            {
                "title": "Formula Spotlight: Convolution Integral",
                "icon": "fa5s.square-root-alt",
                "color": "#06B6D4",
                "text": "y(t) = ∫_{-∞}^{+∞} x(τ) h(t - τ) dτ\nProperties: Commutative x*h = h*x, Associative (x*h1)*h2 = x*(h1*h2)."
            },
            {
                "title": "Exam Tip: LTI System Stability Rule",
                "icon": "fa5s.lightbulb",
                "color": "#F59E0B",
                "text": "A Continuous-Time LTI system is BIBO Stable if and only if ∫_{-∞}^{+∞} |h(t)| dt < ∞ (Impulse response is absolutely integrable)."
            },
            {
                "title": "Memory Trick: Nyquist Rate vs Interval",
                "icon": "fa5s.brain",
                "color": "#10B981",
                "text": "Nyquist Rate = 2 f_max (Minimum Sampling Frequency)\nNyquist Interval = 1 / (2 f_max) (Maximum Sampling Period between samples)."
            },
            {
                "title": "Common Exam Mistake: Laplace ROC Boundary",
                "icon": "fa5s.exclamation-triangle",
                "color": "#EC4899",
                "text": "The Region of Convergence (ROC) in the s-plane NEVER contains any poles! For causal systems, ROC is to the right of the rightmost pole."
            }
        ]
        lay.addWidget(create_subject_widgets_panel(widgets_config))

        scroll.setWidget(container)
        main_lay.addWidget(scroll)
