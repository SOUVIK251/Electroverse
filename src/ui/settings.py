from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QSlider, QCheckBox, QRadioButton, QButtonGroup, QApplication,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.core.theme import ThemeManager

class SettingsView(QWidget):
    """Redesigned app settings & platform About section panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing SettingsView")

        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area Wrapper
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: #0b0f19;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # -------------------------------------------------------------
        # 1. Preferences Card
        # -------------------------------------------------------------
        self.card = QFrame()
        self.card.setObjectName("card-panel")
        self.card.setStyleSheet("""
            QFrame#card-panel {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)

        # Title
        title_layout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.cog", color="#06b6d4").pixmap(24, 24))
        title = QLabel("Application Settings & Preferences")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #06b6d4;")
        title_layout.addWidget(icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)

        # Global Theme Display Info
        theme_layout = QHBoxLayout()
        theme_lbl = QLabel("App Color Theme:")
        theme_lbl.setStyleSheet("font-weight: 500; color: #e2e8f0;")
        
        theme_val = QLabel("Dark Engineering Theme (Default)")
        theme_val.setStyleSheet("color: #06b6d4; font-weight: bold;")
        
        theme_layout.addWidget(theme_lbl)
        theme_layout.addWidget(theme_val)
        theme_layout.addStretch()
        card_layout.addLayout(theme_layout)


        # Font Size Scaling
        font_layout = QHBoxLayout()
        font_lbl = QLabel("Global Text Size:")
        font_lbl.setStyleSheet("font-weight: 500; color: #e2e8f0;")
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(9, 16)
        self.font_slider.setFixedWidth(200)
        
        self.font_val_lbl = QLabel("11 pt")
        self.font_val_lbl.setStyleSheet("color: #06b6d4; font-weight: bold;")
        
        font_layout.addWidget(font_lbl)
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_val_lbl)
        font_layout.addStretch()
        card_layout.addLayout(font_layout)

        # Transitions & Animations
        anim_layout = QHBoxLayout()
        anim_lbl = QLabel("Interface Transitions:")
        anim_lbl.setStyleSheet("font-weight: 500; color: #e2e8f0;")
        
        self.anim_cb = QCheckBox("Enable page fade & sliding sidebar animations")
        self.anim_cb.setStyleSheet("color: #f8fafc;")
        
        anim_layout.addWidget(anim_lbl)
        anim_layout.addWidget(self.anim_cb)
        anim_layout.addStretch()
        card_layout.addLayout(anim_layout)

        # Graph Line Width
        graph_layout = QHBoxLayout()
        graph_lbl = QLabel("Chart Line Thickness:")
        graph_lbl.setStyleSheet("font-weight: 500; color: #e2e8f0;")
        
        self.graph_slider = QSlider(Qt.Orientation.Horizontal)
        self.graph_slider.setRange(1, 5)
        self.graph_slider.setFixedWidth(200)
        
        self.graph_val_lbl = QLabel("2 px")
        self.graph_val_lbl.setStyleSheet("color: #06b6d4; font-weight: bold;")
        
        graph_layout.addWidget(graph_lbl)
        graph_layout.addWidget(self.graph_slider)
        graph_layout.addWidget(self.graph_val_lbl)
        graph_layout.addStretch()
        card_layout.addLayout(graph_layout)

        # Action Buttons
        actions_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.reset_btn = QPushButton("Reset Defaults")
        self.reset_btn.setStyleSheet("background-color: #1e293b; color: white; padding: 8px 16px; border-radius: 4px;")
        self.reset_btn.clicked.connect(self.reset_defaults)
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.reset_btn)
        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        layout.addWidget(self.card)


        # -------------------------------------------------------------
        # 3. About Section Card
        # -------------------------------------------------------------
        self.about_card = QFrame()
        self.about_card.setObjectName("card-panel")
        self.about_card.setStyleSheet("""
            QFrame#card-panel {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-left: 5px solid #06b6d4;
                border-radius: 8px;
            }
        """)
        about_layout = QVBoxLayout(self.about_card)
        about_layout.setContentsMargins(25, 25, 25, 25)
        about_layout.setSpacing(15)

        # Header
        a_title_layout = QHBoxLayout()
        a_icon = QLabel()
        a_icon.setPixmap(qta.icon("fa5s.info-circle", color="#06b6d4").pixmap(24, 24))
        a_title = QLabel("About ElectroVerse Platform")
        a_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f8fafc;")
        a_title_layout.addWidget(a_icon)
        a_title_layout.addWidget(a_title)
        a_title_layout.addStretch()
        about_layout.addLayout(a_title_layout)

        # Description
        a_desc = QLabel(
            "ElectroVerse is an offline interactive engineering learning platform and simulation environment designed for electronics engineering students, educators, and researchers. It combines digital logic design, breadboard circuit simulation, structured ECE/CSE textbook lessons, formula shortcuts, and oral board viva preparation into a unified desktop application."
        )
        a_desc.setWordWrap(True)
        a_desc.setStyleSheet("color: #94a3b8; font-size: 10pt; line-height: 1.5;")
        about_layout.addWidget(a_desc)

        # Feature Highlights Grid
        f_grid = QGridLayout()
        f_grid.setSpacing(12)
        features = [
            ("⚡ Digital System Design Hub", "Textbook reader, 280px sidebar, 320x220 diagram gallery, and formula memory shortcuts."),
            ("🧪 Virtual Breadboard Lab", "2D solderless breadboard simulator supporting 74-Series TTL ICs (7400, 7402, 7404, 7408, 7411, 7432, 7486, 74266)."),
            ("🎓 Grand Viva & Interview Prep", "2,200+ conceptual questions across 22 ECE/CSE subjects with governing equations and instant memory tricks."),
            ("🛠 Engineering Toolkit", "Real-time transient circuit solvers, 60+ formulas, and comprehensive component library.")
        ]
        for idx, (f_title_str, f_desc_str) in enumerate(features):
            box = QFrame()
            box.setStyleSheet("background-color: #111827; border: 1px solid #1e293b; border-radius: 6px; padding: 12px;")
            b_lay = QVBoxLayout(box)
            b_title = QLabel(f_title_str)
            b_title.setStyleSheet("color: #06b6d4; font-size: 10pt; font-weight: bold;")
            b_desc = QLabel(f_desc_str)
            b_desc.setStyleSheet("color: #94a3b8; font-size: 8.5pt;")
            b_desc.setWordWrap(True)
            b_lay.addWidget(b_title)
            b_lay.addWidget(b_desc)
            f_grid.addWidget(box, idx // 2, idx % 2)
        about_layout.addLayout(f_grid)

        # Developer / Creator Credit Banner
        credit_box = QFrame()
        credit_box.setStyleSheet("""
            QFrame {
                background-color: #1e1b4b;
                border: 2px solid #6366f1;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        c_layout = QHBoxLayout(credit_box)
        c_icon = QLabel("👨‍💻")
        c_icon.setStyleSheet("font-size: 26pt;")
        c_layout.addWidget(c_icon)

        c_text_lay = QVBoxLayout()
        c_tag = QLabel("PROJECT CREATOR & LEAD DEVELOPER")
        c_tag.setStyleSheet("color: #818cf8; font-weight: bold; font-size: 8pt; letter-spacing: 1px;")
        
        c_name = QLabel("Created & Developed by Souvik Kundu")
        c_name.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold;")
        
        c_sub = QLabel("Designed and engineered with passion by Souvik Kundu to make offline electronics engineering education intuitive, visual, and accessible.")
        c_sub.setStyleSheet("color: #cbd5e1; font-size: 9pt; font-style: italic;")
        c_sub.setWordWrap(True)

        c_text_lay.addWidget(c_tag)
        c_text_lay.addWidget(c_name)
        c_text_lay.addWidget(c_sub)
        c_layout.addLayout(c_text_lay)
        c_layout.addStretch()

        about_layout.addWidget(credit_box)
        layout.addWidget(self.about_card)

        self.scroll.setWidget(container)
        main_layout.addWidget(self.scroll)

        # Connect value change listeners to update labels live
        self.font_slider.valueChanged.connect(lambda v: self.font_val_lbl.setText(f"{v} pt"))
        self.graph_slider.valueChanged.connect(lambda v: self.graph_val_lbl.setText(f"{v} px"))

        # Load values
        self.load_settings()

    def load_settings(self):
        font_size = config_manager.get("font_size") or 11
        self.font_slider.setValue(font_size)
        self.font_val_lbl.setText(f"{font_size} pt")
        
        anim_enabled = config_manager.get("animations_enabled")
        if anim_enabled is None:
            anim_enabled = True
        self.anim_cb.setChecked(anim_enabled)
        
        graph_width = config_manager.get("graph_line_width") or 2
        self.graph_slider.setValue(graph_width)
        self.graph_val_lbl.setText(f"{graph_width} px")

    def save_settings(self):
        font_size = self.font_slider.value()
        anim_enabled = self.anim_cb.isChecked()
        graph_width = self.graph_slider.value()
        
        config_manager.set("theme", "dark")
        config_manager.set("font_size", font_size)
        config_manager.set("animations_enabled", anim_enabled)
        config_manager.set("graph_line_width", graph_width)
        config_manager.save()
        
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, "dark")
        
        if self.window() and hasattr(self.window(), "apply_global_settings"):
            self.window().apply_global_settings()
            
        log.info("Settings saved and applied successfully.")


    def reset_defaults(self):
        config_manager.reset_to_defaults()
        self.load_settings()
        self.save_settings()
        log.info("Settings reset to defaults.")
