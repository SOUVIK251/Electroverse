"""
ElectroVerse Microprocessor & Microcontroller Hub Dashboard View
State-of-the-Art Industrial Workstation Dashboard for Microprocessors, 8051, ARM, and Embedded Systems.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from src.core.logger import log


class MPMCDashboardView(QWidget):
    """Premium Workstation Control Dashboard for Microprocessor & Microcontroller Hub."""

    tab_jump_requested = Signal(int)

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view
        log.info("Initializing MPMCDashboardView premium workstation dashboard")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area for clean resolution scaling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #0B1020; }")

        container = QFrame()
        container.setStyleSheet("QFrame { background-color: #0B1020; }")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(16)

        # ----------------------------------------------------------------------
        # 1. Premium High-Tech Header Banner
        # ----------------------------------------------------------------------
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E1B4B, stop:0.4 #0F172A, stop:1 #061826);
                border: 1px solid #312E81;
                border-left: 5px solid #F97316;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        b_lay = QHBoxLayout(banner)
        b_lay.setContentsMargins(15, 12, 15, 12)

        # Left Icon & Title Info
        hdr_info = QHBoxLayout()
        hdr_info.setSpacing(14)

        icon_box = QLabel()
        icon_box.setPixmap(qta.icon("fa5s.memory", color="#F97316").pixmap(42, 42))
        hdr_info.addWidget(icon_box)

        v_lay = QVBoxLayout()
        v_lay.setSpacing(4)
        title_lbl = QLabel("MICROPROCESSOR & MICROCONTROLLER HUB")
        title_lbl.setStyleSheet("font-size: 16pt; font-weight: 800; color: #FFFFFF; letter-spacing: 1.2px; font-family: 'Segoe UI', sans-serif;")
        
        sub_lbl = QLabel("Virtual Engineering Laboratory for Microprocessor & Embedded System Design")
        sub_lbl.setStyleSheet("font-size: 10pt; font-weight: 600; color: #38BDF8; font-family: 'Segoe UI', sans-serif;")

        v_lay.addWidget(title_lbl)
        v_lay.addWidget(sub_lbl)
        hdr_info.addLayout(v_lay)

        b_lay.addLayout(hdr_info)
        b_lay.addStretch()

        # Right Status Badge
        status_badge = QLabel("● System Engine: Ready (Intel / ARM Core Active)")
        status_badge.setStyleSheet("""
            QLabel {
                color: #34D399;
                font-weight: 700;
                font-size: 9.5pt;
                background-color: #064E3B;
                border: 1px solid #059669;
                border-radius: 18px;
                padding: 8px 18px;
                font-family: Consolas, 'Segoe UI';
            }
        """)
        b_lay.addWidget(status_badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        c_layout.addWidget(banner)

        # ----------------------------------------------------------------------
        # 2. Progress & Metrics Cards Grid
        # ----------------------------------------------------------------------
        grid = QGridLayout()
        grid.setSpacing(14)

        cards_data = [
            ("Theory Curriculum", "8085 / 8086 / 8051 / ARM Cortex", "85%", "4 Modules Active", "#06B6D4", "fa5s.book-reader", 1),
            ("Interactive Simulation", "21+ Architecture & Peripheral Visualizers", "78%", "Real-time Animators", "#3B82F6", "fa5s.microchip", 2),
            ("CBT Assessment", "CBT Exam & GATE Level Question Bank", "88%", "GATE & University Prep", "#10B981", "fa5s.graduation-cap", 3),
            ("1000+ Program Database", "1000+ Program Database & Recognition", "95%", "1000+ Programs Ready", "#F97316", "fa5s.database", 4)
        ]

        for i, (title, desc, pct, sub_info, color, icon_name, tab_idx) in enumerate(cards_data):
            card = QFrame()
            card.setObjectName("metric-card")
            card.setStyleSheet(f"""
                QFrame#metric-card {{
                    background-color: #141B2D;
                    border: 1px solid #26334D;
                    border-top: 3px solid {color};
                    border-radius: 8px;
                    padding: 14px;
                }}
                QFrame#metric-card:hover {{
                    background-color: #1B2740;
                    border-color: {color};
                }}
            """)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(12, 12, 12, 12)
            c_lay.setSpacing(8)

            # Top Header Row
            hdr = QHBoxLayout()
            lbl = QLabel(title)
            lbl.setStyleSheet("font-size: 11pt; font-weight: 700; color: #FFFFFF;")
            
            icon = QLabel()
            icon.setPixmap(qta.icon(icon_name, color=color).pixmap(22, 22))
            hdr.addWidget(lbl)
            hdr.addStretch()
            hdr.addWidget(icon)
            c_lay.addLayout(hdr)

            # Value & Sub-info Row
            val_row = QHBoxLayout()
            val_lbl = QLabel(pct)
            val_lbl.setStyleSheet(f"font-size: 22pt; font-weight: 800; color: {color}; font-family: 'Segoe UI', sans-serif;")
            
            badge_lbl = QLabel(sub_info)
            badge_lbl.setStyleSheet(f"font-size: 8pt; font-weight: 700; color: {color}; background-color: #0F172A; border: 1px solid {color}; border-radius: 10px; padding: 3px 8px;")
            
            val_row.addWidget(val_lbl)
            val_row.addStretch()
            val_row.addWidget(badge_lbl)
            c_lay.addLayout(val_row)

            # Description
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 9pt; color: #94A3B8;")
            c_lay.addWidget(desc_lbl)

            # Progress Bar
            pbar = QProgressBar()
            pbar.setValue(int(pct.replace("%", "")))
            pbar.setFixedHeight(6)
            pbar.setTextVisible(False)
            pbar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #090D16;
                    border: 1px solid #26334D;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
            c_lay.addWidget(pbar)

            # Launch Button
            btn = QPushButton("Launch Workspace Module ➡")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1E293B;
                    color: #FFFFFF;
                    border: 1px solid #334155;
                    border-radius: 5px;
                    padding: 8px 12px;
                    font-weight: 700;
                    font-size: 9pt;
                    margin-top: 4px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: #FFFFFF;
                    border-color: {color};
                }}
            """)
            btn.clicked.connect(lambda _, idx=tab_idx: self.tab_jump_requested.emit(idx))
            c_lay.addWidget(btn)

            grid.addWidget(card, i // 2, i % 2)

        c_layout.addLayout(grid)

        # ----------------------------------------------------------------------
        # 3. Quick Launch & Workstation Status Row
        # ----------------------------------------------------------------------
        row2 = QHBoxLayout()
        row2.setSpacing(14)

        # Left Panel: Quick Launch Workspace
        ql_box = QFrame()
        ql_box.setStyleSheet("""
            QFrame {
                background-color: #141B2D;
                border: 1px solid #26334D;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        ql_lay = QVBoxLayout(ql_box)
        ql_lay.setSpacing(10)

        ql_hdr = QHBoxLayout()
        ql_title = QLabel("⚡ QUICK LAUNCH WORKSPACE")
        ql_title.setStyleSheet("font-size: 11pt; font-weight: 800; color: #F97316; font-family: Consolas, 'Segoe UI';")
        ql_hdr.addWidget(ql_title)
        ql_hdr.addStretch()
        ql_lay.addLayout(ql_hdr)

        quick_btns = [
            ("8085 / 8086 Instruction Set Explorer", "fa5s.code", 1),
            ("8051 Timer & Baud Rate Calculator", "fa5s.clock", 2),
            ("Address Decoder & Memory Mapping Solver", "fa5s.microchip", 2),
            ("Interactive 8085 Bus & 8086 Pipeline Simulator", "fa5s.play-circle", 3),
            ("Microprocessor & Embedded System CBT Exam", "fa5s.pen-nib", 4),
            ("Pin Diagrams & Formula Reference Sheet", "fa5s.file-alt", 5)
        ]

        for text, icon_name, tab_idx in quick_btns:
            qb = QPushButton(f"   {text}")
            qb.setIcon(qta.icon(icon_name, color="#F97316"))
            qb.setCursor(Qt.CursorShape.PointingHandCursor)
            qb.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 9px 14px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 9.5pt;
                }
                QPushButton:hover {
                    background-color: #F97316;
                    color: #FFFFFF;
                    border-color: #F97316;
                }
            """)
            qb.clicked.connect(lambda _, idx=tab_idx: self.tab_jump_requested.emit(idx))
            ql_lay.addWidget(qb)

        row2.addWidget(ql_box, 1)

        # Right Panel: Workstation Status & Curriculum Modules
        st_box = QFrame()
        st_box.setStyleSheet("""
            QFrame {
                background-color: #141B2D;
                border: 1px solid #26334D;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        st_lay = QVBoxLayout(st_box)
        st_lay.setSpacing(10)

        st_hdr = QHBoxLayout()
        st_title = QLabel("📌 WORKSTATION STATUS & CURRICULUM MODULES")
        st_title.setStyleSheet("font-size: 11pt; font-weight: 800; color: #06B6D4; font-family: Consolas, 'Segoe UI';")
        st_hdr.addWidget(st_title)
        st_hdr.addStretch()
        st_lay.addLayout(st_hdr)

        notes = [
            ("Module I: 8085 & 8086 Architecture, Registers & Buses", "Ready", "#10B981"),
            ("Module II: 8255 PPI, 8253 Timer, 8251 USART & 8087 NDP", "Ready", "#10B981"),
            ("Module III: 80286 to Pentium Protected Mode & 8051 MCU", "Ready", "#10B981"),
            ("Module IV: RISC vs CISC, ARM Cortex-M, RTOS & IoT Buses", "Ready", "#10B981"),
            ("Interactive Simulation: 21 Architecture Visualizers Active", "Active", "#06B6D4")
        ]

        for text, status_text, status_color in notes:
            row_item = QFrame()
            row_item.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 6px 10px;")
            r_lay = QHBoxLayout(row_item)
            r_lay.setContentsMargins(6, 4, 6, 4)

            chk_icon = QLabel("✔")
            chk_icon.setStyleSheet("color: #10B981; font-weight: bold; font-size: 10pt;")
            r_lay.addWidget(chk_icon)

            txt_lbl = QLabel(text)
            txt_lbl.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 9pt;")
            r_lay.addWidget(txt_lbl)

            r_lay.addStretch()

            st_badge = QLabel(status_text)
            st_badge.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 8pt; background-color: #0F172A; border: 1px solid {status_color}; border-radius: 8px; padding: 2px 8px;")
            r_lay.addWidget(st_badge)

            st_lay.addWidget(row_item)

        st_lay.addStretch()
        row2.addWidget(st_box, 1)

        c_layout.addLayout(row2)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
