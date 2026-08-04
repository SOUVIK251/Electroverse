"""
Hub Dashboard Reusable UI Components Base
Provides standardized premium visual components, progress cards, metrics, and navigation widgets
used across all ElectroVerse subject hubs (Network Theory, Analog Electronics, Digital System Design, Signal & System).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QProgressBar, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta


def create_dashboard_banner(title: str, subtitle: str, tag: str = "SUBJECT DASHBOARD", resume_topic: str = "", on_resume_cb=None):
    """Creates a premium Subject Header Banner with Title, Subtitle, and Resume Learning CTA."""
    hdr_card = QFrame()
    hdr_card.setObjectName("card-panel")
    hdr_card.setStyleSheet("""
        QFrame#card-panel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #141B2D, stop:1 #1E293B);
            border: 1px solid #26334D;
            border-top: 4px solid #06B6D4;
            border-radius: 10px;
            padding: 16px;
        }
    """)
    h_lay = QVBoxLayout(hdr_card)
    h_lay.setSpacing(6)

    tag_lbl = QLabel(f"⚡ {tag.upper()}")
    tag_lbl.setStyleSheet("color: #06B6D4; font-size: 8.5pt; font-weight: bold; letter-spacing: 1px;")
    h_lay.addWidget(tag_lbl)

    row = QHBoxLayout()
    t_lay = QVBoxLayout()
    
    t_lbl = QLabel(title)
    t_lbl.setStyleSheet("font-size: 15pt; font-weight: bold; color: #FFFFFF;")
    
    sub_lbl = QLabel(subtitle)
    sub_lbl.setWordWrap(True)
    sub_lbl.setStyleSheet("color: #CBD5E1; font-size: 9.5pt;")

    t_lay.addWidget(t_lbl)
    t_lay.addWidget(sub_lbl)
    row.addLayout(t_lay, 1)

    if resume_topic and on_resume_cb:
        resume_btn = QPushButton(f"▶ Resume: {resume_topic}")
        resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        resume_btn.setStyleSheet("""
            QPushButton {
                background-color: #06B6D4;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 9pt;
                padding: 10px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0891B2;
            }
        """)
        resume_btn.setIcon(qta.icon("fa5s.play-circle", color="#FFFFFF"))
        resume_btn.clicked.connect(on_resume_cb)
        row.addWidget(resume_btn)

    h_lay.addLayout(row)
    return hdr_card


def create_metric_card(icon_str: str, title: str, val_str: str, sub_text: str, color: str) -> QFrame:
    """Creates a metric summary card with icon, value, and color accent top border."""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: #141B2D;
            border: 1px solid #26334D;
            border-top: 3px solid {color};
            border-radius: 8px;
            padding: 10px;
        }}
    """)
    c_lay = QVBoxLayout(card)
    c_lay.setSpacing(4)
    
    top_row = QHBoxLayout()
    ic = QLabel()
    ic.setPixmap(qta.icon(icon_str, color=color).pixmap(16, 16))
    tl = QLabel(title)
    tl.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: bold;")
    top_row.addWidget(ic)
    top_row.addWidget(tl)
    top_row.addStretch()
    
    vl = QLabel(val_str)
    vl.setStyleSheet("color: #FFFFFF; font-size: 14pt; font-weight: bold; padding: 2px 0px;")
    
    st = QLabel(sub_text)
    st.setStyleSheet("color: #64748B; font-size: 7.5pt;")

    c_lay.addLayout(top_row)
    c_lay.addWidget(vl)
    c_lay.addWidget(st)
    return card


def create_quick_access_grid(buttons_config: list) -> QFrame:
    """Creates a row/grid of 1-click Quick Access launching buttons to tabs."""
    card = QFrame()
    card.setObjectName("card-panel")
    card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
    j_lay = QVBoxLayout(card)
    j_lay.setSpacing(8)

    j_hdr = QLabel("🚀 Quick Access & Launchpad")
    j_hdr.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 4px;")
    j_lay.addWidget(j_hdr)

    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)

    for label, icon_name, color, callback in buttons_config:
        btn = QPushButton(f" {label}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1E293B;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 8.5pt;
                padding: 8px 12px;
                border: 1px solid #334155;
                border-radius: 6px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #26334D;
                border-color: {color};
            }}
        """)
        btn.setIcon(qta.icon(icon_name, color=color))
        if callback:
            btn.clicked.connect(callback)
        btn_row.addWidget(btn)

    j_lay.addLayout(btn_row)
    return card


def create_module_cards_grid(modules_data: list, on_module_click_cb) -> QFrame:
    """Creates a responsive grid of subject module completion cards."""
    card = QFrame()
    card.setObjectName("card-panel")
    card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
    lay = QVBoxLayout(card)
    lay.setSpacing(8)

    hdr = QLabel("📚 Subject Curriculum & Module Completion")
    hdr.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 4px;")
    lay.addWidget(hdr)

    grid = QGridLayout()
    grid.setSpacing(8)

    for idx, mod in enumerate(modules_data):
        row = idx // 4
        col = idx % 4
        
        m_card = QFrame()
        m_card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
            QFrame:hover {
                border-color: #06B6D4;
                background-color: #26334D;
            }
        """)
        m_lay = QVBoxLayout(m_card)
        m_lay.setSpacing(4)

        t_row = QHBoxLayout()
        ic_name = mod.get("icon", "fa5s.folder")
        mod_color = mod.get("color", "#06B6D4")
        
        ic_lbl = QLabel()
        ic_lbl.setPixmap(qta.icon(ic_name, color=mod_color).pixmap(14, 14))
        
        title_lbl = QLabel(mod.get("title", "Module"))
        title_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 8.5pt;")
        
        t_row.addWidget(ic_lbl)
        t_row.addWidget(title_lbl)
        t_row.addStretch()

        pct = mod.get("progress", 0)
        p_lbl = QLabel(f"{pct}%")
        p_lbl.setStyleSheet(f"color: {mod_color}; font-weight: bold; font-size: 8pt;")
        t_row.addWidget(p_lbl)
        
        m_lay.addLayout(t_row)

        sub_desc = QLabel(mod.get("topics_cnt", "4 Topics"))
        sub_desc.setStyleSheet("color: #94A3B8; font-size: 7.5pt;")
        m_lay.addWidget(sub_desc)

        pbar = QProgressBar()
        pbar.setRange(0, 100)
        pbar.setValue(pct)
        pbar.setFixedHeight(4)
        pbar.setTextVisible(False)
        pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #0F172A;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {mod_color};
                border-radius: 2px;
            }}
        """)
        m_lay.addWidget(pbar)

        grid.addWidget(m_card, row, col)

    lay.addLayout(grid)
    return card


def create_activity_log_card(activities: list) -> QFrame:
    """Creates recent session activity & recent history log card."""
    card = QFrame()
    card.setObjectName("card-panel")
    card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
    lay = QVBoxLayout(card)
    lay.setSpacing(6)

    hdr = QLabel("🕒 Recent Session Activity & History Log")
    hdr.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 4px;")
    lay.addWidget(hdr)

    for act_str, time_str, clr in activities:
        r = QHBoxLayout()
        al = QLabel(act_str)
        al.setStyleSheet(f"color: {clr}; font-size: 8.5pt; font-weight: 600;")
        tl = QLabel(time_str)
        tl.setStyleSheet("color: #64748B; font-size: 7.5pt;")
        r.addWidget(al)
        r.addStretch()
        r.addWidget(tl)
        lay.addLayout(r)

    return card


def create_subject_widgets_panel(widgets_config: list) -> QFrame:
    """Creates a side-by-side row of subject-specific educational widgets (Tip, Formula, Exam Mistake, Trivia)."""
    card = QFrame()
    card.setObjectName("card-panel")
    card.setStyleSheet("QFrame#card-panel { background-color: #141B2D; border: 1px solid #26334D; border-radius: 10px; padding: 12px; }")
    lay = QVBoxLayout(card)
    lay.setSpacing(8)

    hdr = QLabel("💡 Exam Insights, Formulas & Learning Tricks")
    hdr.setStyleSheet("color: #EC4899; font-weight: bold; font-size: 11pt; border-bottom: 1px solid #26334D; padding-bottom: 4px;")
    lay.addWidget(hdr)

    grid = QGridLayout()
    grid.setSpacing(8)

    for idx, w in enumerate(widgets_config):
        row = idx // 2
        col = idx % 2

        w_box = QFrame()
        clr = w.get("color", "#06B6D4")
        w_box.setStyleSheet(f"""
            QFrame {{
                background-color: #1E293B;
                border: 1px solid #334155;
                border-left: 4px solid {clr};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        wb_lay = QVBoxLayout(w_box)
        wb_lay.setSpacing(4)

        wt_row = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(w.get("icon", "fa5s.lightbulb"), color=clr).pixmap(14, 14))
        wt = QLabel(w.get("title", "Tip"))
        wt.setStyleSheet(f"color: {clr}; font-weight: bold; font-size: 8.5pt;")
        wt_row.addWidget(ic)
        wt_row.addWidget(wt)
        wt_row.addStretch()

        wb_lay.addLayout(wt_row)

        desc = QLabel(w.get("text", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #CBD5E1; font-size: 8pt; line-height: 1.3;")
        wb_lay.addWidget(desc)

        grid.addWidget(w_box, row, col)

    lay.addLayout(grid)
    return card
