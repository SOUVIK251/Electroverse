from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QSlider, QCheckBox, QRadioButton, QButtonGroup, QApplication
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.core.theme import ThemeManager

class SettingsView(QWidget):
    """Redesigned app settings panel providing full IDE customization controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing SettingsView")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card container
        self.card = QFrame()
        self.card.setObjectName("card-panel")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Title
        title_layout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.cog", color="#06b6d4").pixmap(24, 24))
        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #06b6d4;")
        title_layout.addWidget(icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)

        # -------------------------------------------------------------
        # 1. Theme Configuration
        # -------------------------------------------------------------
        theme_layout = QHBoxLayout()
        theme_lbl = QLabel("App Color Scheme:")
        theme_lbl.setStyleSheet("font-weight: 500;")
        
        self.theme_group = QButtonGroup(self)
        self.dark_radio = QRadioButton("Midnight Dark")
        self.light_radio = QRadioButton("Clean Light")
        self.theme_group.addButton(self.dark_radio)
        self.theme_group.addButton(self.light_radio)
        
        theme_layout.addWidget(theme_lbl)
        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.light_radio)
        theme_layout.addStretch()
        card_layout.addLayout(theme_layout)

        # -------------------------------------------------------------
        # 2. Font Size Scaling
        # -------------------------------------------------------------
        font_layout = QHBoxLayout()
        font_lbl = QLabel("Global Text Size:")
        font_lbl.setStyleSheet("font-weight: 500;")
        
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

        # -------------------------------------------------------------
        # 3. Transitions & Animations
        # -------------------------------------------------------------
        anim_layout = QHBoxLayout()
        anim_lbl = QLabel("Interface Transitions:")
        anim_lbl.setStyleSheet("font-weight: 500;")
        
        self.anim_cb = QCheckBox("Enable page fade & sliding sidebar animations")
        
        anim_layout.addWidget(anim_lbl)
        anim_layout.addWidget(self.anim_cb)
        anim_layout.addStretch()
        card_layout.addLayout(anim_layout)

        # -------------------------------------------------------------
        # 4. Graph Line Width
        # -------------------------------------------------------------
        graph_layout = QHBoxLayout()
        graph_lbl = QLabel("Chart Line Thickness:")
        graph_lbl.setStyleSheet("font-weight: 500;")
        
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

        card_layout.addSpacing(15)

        # -------------------------------------------------------------
        # Action Buttons
        # -------------------------------------------------------------
        actions_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.setProperty("primary", "true")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.reset_btn = QPushButton("Reset Defaults")
        self.reset_btn.clicked.connect(self.reset_defaults)
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.reset_btn)
        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        card_layout.addStretch()
        layout.addWidget(self.card)

        # Connect value change listeners to update labels live
        self.font_slider.valueChanged.connect(lambda v: self.font_val_lbl.setText(f"{v} pt"))
        self.graph_slider.valueChanged.connect(lambda v: self.graph_val_lbl.setText(f"{v} px"))

        # Load values
        self.load_settings()

    def load_settings(self):
        """Loads and checks controls matching active configuration parameters."""
        theme = config_manager.get("theme")
        if theme == "light":
            self.light_radio.setChecked(True)
        else:
            self.dark_radio.setChecked(True)
            
        font_size = config_manager.get("font_size") or 11
        self.font_slider.setValue(font_size)
        self.font_val_lbl.setText(f"{font_size} pt")
        
        anim_enabled = config_manager.get("animations_enabled")
        self.anim_cb.setChecked(anim_enabled)
        
        line_w = config_manager.get("graph_line_width") or 2
        self.graph_slider.setValue(line_w)
        self.graph_val_lbl.setText(f"{line_w} px")

    def save_settings(self):
        """Saves control parameters and forces dynamic stylesheet rebuild."""
        theme = "light" if self.light_radio.isChecked() else "dark"
        font_size = self.font_slider.value()
        anim_enabled = self.anim_cb.isChecked()
        line_w = self.graph_slider.value()

        config_manager.set("theme", theme)
        config_manager.set("font_size", font_size)
        config_manager.set("animations_enabled", anim_enabled)
        config_manager.set("graph_line_width", line_w)

        # Apply styles dynamically
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, theme)

        # Re-polish MainWindow
        top_window = self.window()
        if top_window:
            top_window.central_widget.style().unpolish(top_window.central_widget)
            top_window.central_widget.style().polish(top_window.central_widget)
            
            # Repaint other views that have dynamic updates
            for view in top_window.views:
                if hasattr(view, "update_theme"):
                    view.update_theme()
                    
            if hasattr(top_window, "show_toast"):
                top_window.show_toast("Preferences applied successfully.")

        log.info("Settings saved and styles updated dynamically.")

    def reset_defaults(self):
        """Restores config defaults."""
        config_manager.set("theme", "dark")
        config_manager.set("font_size", 11)
        config_manager.set("animations_enabled", True)
        config_manager.set("graph_line_width", 2)
        
        self.load_settings()
        self.save_settings()
        
        top_window = self.window()
        if top_window and hasattr(top_window, "show_toast"):
            top_window.show_toast("Restored default preferences.", is_success=True)
