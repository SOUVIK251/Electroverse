import sys
import os
import platform

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QStackedWidget, QStatusBar, QToolButton,
    QGraphicsOpacityEffect, QSizePolicy, QMessageBox, QDialog, QApplication
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QColor, QShortcut, QKeySequence, QIcon
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.core.theme import ThemeManager
from src.core.screen_protection import screen_protection

from src.ui.dashboard import DashboardView
from src.ui.library import LibraryView
from src.ui.dashboard import DashboardView
from src.ui.library import LibraryView
from src.ui.analog_hub import AnalogElectronicsHubView
from src.ui.learning_hub import LearningHubView
from src.ui.signals_hub import SignalSystemHubView
from src.ui.network_hub import NetworkHubView
from src.ui.mpmc_hub import MPMCHubView
from src.ui.grand_viva import GrandVivaView
from src.ui.settings import SettingsView
from src.core.navigation import ViewID, HubTabID

class MainWindow(QMainWindow):
    """Master application shell for ElectroVerse Platform."""

    HUB_NAMES = [
        "Dashboard",
        "Component Library",
        "Analog Electronics Circuit Hub",
        "Digital System Design Hub",
        "Signal & System Hub",
        "Network Theory Hub",
        "Microprocessor & Microcontroller Hub",
        "Grand Viva & Core Interview Board",
        "Settings"
    ]

    VIEW_INDEX_MAP = {
        ViewID.DASHBOARD: 0,
        ViewID.LIBRARY: 1,
        ViewID.ANALOG_HUB: 2,
        ViewID.DIGITAL_HUB: 3,
        ViewID.SIGNALS_HUB: 4,
        ViewID.NETWORK_HUB: 5,
        ViewID.MPMC_HUB: 6,
        ViewID.GRAND_VIVA: 7,
        ViewID.SETTINGS: 8,
    }

    def __init__(self):
        super().__init__()
        log.info("Initializing ElectroVerse MainWindow")

        self.nav_buttons = []
        self.session_activity = []
        self.current_theme = config_manager.get("theme") or "dark"

        self.setWindowTitle("ElectroVerse – Offline Virtual Engineering Laboratory")
        self.resize(1340, 860)
        self.setMinimumSize(1100, 700)

        # Apply Global Theme
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, self.current_theme)

        # Main Layout Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_main_container()
        self.setup_statusbar()
        self.setup_keyboard_shortcuts()

        # Default View: Dashboard (0)
        self.switch_view(0)
        self.apply_global_settings()


    def setup_sidebar(self):
        """Creates the collapsible left navigation sidebar."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("QFrame#sidebar { background-color: #0F172A; border-right: 1px solid #26334D; }")

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand Panel Header
        brand_panel = QFrame()
        brand_panel.setFixedHeight(70)
        brand_panel.setStyleSheet("border-bottom: 1px solid #26334D;")
        brand_layout = QHBoxLayout(brand_panel)
        brand_layout.setContentsMargins(20, 0, 20, 0)

        logo_icon = QLabel("⚡")
        logo_icon.setStyleSheet("font-size: 18pt; color: #06B6D4;")
        brand_layout.addWidget(logo_icon)

        brand_text = QLabel("ElectroVerse")
        brand_text.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFFFFF; letter-spacing: 1px;")
        brand_layout.addWidget(brand_text)
        brand_layout.addStretch()

        sidebar_layout.addWidget(brand_panel)

        # Navigation Panel Area
        nav_panel = QWidget()
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(6)

        nav_items = [
            ("Dashboard", "fa5s.th-large", ViewID.DASHBOARD),
            ("Component Library", "fa5s.book", ViewID.LIBRARY),
            ("Analog Electronics Circuit Hub", "fa5s.wave-square", ViewID.ANALOG_HUB),
            ("Digital System Design Hub", "fa5s.microchip", ViewID.DIGITAL_HUB),
            ("Signal & System Hub", "fa5s.chart-line", ViewID.SIGNALS_HUB),
            ("Network Theory Hub", "fa5s.project-diagram", ViewID.NETWORK_HUB),
            ("Microprocessor & MCU Hub", "fa5s.memory", ViewID.MPMC_HUB),
            ("Grand Viva & Core Interview", "fa5s.user-graduate", ViewID.GRAND_VIVA),
            ("Settings", "fa5s.cog", ViewID.SETTINGS)
        ]

        for text, icon_str, v_id in nav_items:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setIcon(qta.icon(icon_str, color="#94A3B8"))
            btn.setIconSize(QSize(18, 18))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(46)
            btn.setFixedWidth(240)
            btn.clicked.connect(lambda checked=False, target_vid=v_id: self.switch_to_view(target_vid))
            
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)


        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_panel)

        # Footer Panel
        footer_panel = QFrame()
        footer_panel.setFixedHeight(60)
        footer_panel.setStyleSheet("border-top: 1px solid #26334D;")
        footer_layout = QHBoxLayout(footer_panel)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        self.info_btn = QPushButton()
        self.info_btn.setObjectName("secondary")
        self.info_btn.setIcon(qta.icon("fa5s.question-circle", color="#94A3B8"))
        self.info_btn.setIconSize(QSize(16, 16))
        self.info_btn.setToolTip("Help & Keyboard Shortcuts (Ctrl+H)")
        self.info_btn.setFixedSize(32, 32)
        self.info_btn.clicked.connect(self.show_shortcuts_guide)

        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: #7A869A; font-size: 8.5pt;")

        footer_layout.addWidget(self.info_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.version_label)

        sidebar_layout.addWidget(footer_panel)

        self.main_layout.addWidget(self.sidebar)

    def setup_main_container(self):
        """Creates the header toolbar and stacked widget view controller."""
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header bar
        header_bar = QFrame()
        header_bar.setObjectName("header-bar")
        header_bar.setFixedHeight(70)
        header_bar.setStyleSheet("QFrame#header-bar { background-color: #101827; border-bottom: 1px solid #26334D; }")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(25, 0, 25, 0)

        # Breadcrumbs Layout
        self.breadcrumb_layout = QHBoxLayout()
        self.breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb_layout.setSpacing(8)
        header_layout.addLayout(self.breadcrumb_layout)

        header_layout.addStretch()

        # Active state indicator
        self.status_indicator = QLabel("System Status: Offline Engine Ready")
        self.status_indicator.setStyleSheet("color: #22C55E; font-size: 9.5pt; font-weight: 500;")
        header_layout.addWidget(self.status_indicator)

        content_layout.addWidget(header_bar)

        # Stacked Widget View Controller
        self.view_stack = QStackedWidget()
        
        # Instantiate views
        self.views = [
            DashboardView(self),              # 0: Dashboard
            LibraryView(self),                # 1: Component Library
            AnalogElectronicsHubView(self),   # 2: Analog Electronics Circuit Hub
            LearningHubView(self),            # 3: Digital System Design Hub
            SignalSystemHubView(self),        # 4: Signal & System Hub
            NetworkHubView(self),             # 5: Network Theory Hub
            MPMCHubView(self),                # 6: Microprocessor & Microcontroller Hub
            GrandVivaView(self),              # 7: Grand Viva & Core Interview
            SettingsView(self)                # 8: Settings
        ]

        for view in self.views:
            self.view_stack.addWidget(view)

        content_layout.addWidget(self.view_stack)
        self.main_layout.addWidget(self.content_container)

    def setup_statusbar(self):
        """Creates the bottom status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("ElectroVerse Virtual Lab booted successfully.")

    def setup_keyboard_shortcuts(self):
        """Binds general key combos to global actions."""
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_shortcuts_guide)
        QShortcut(QKeySequence("Ctrl+D"), self, lambda: self.switch_view(0))
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.switch_view(4))
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.switch_view(5))
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.switch_view(1))
        QShortcut(QKeySequence("Ctrl+A"), self, self.show_about_dialog)

    def toggle_sidebar(self):
        is_visible = self.sidebar.isVisible()
        self.sidebar.setVisible(not is_visible)

    def apply_global_settings(self):
        pass


    def set_breadcrumbs(self, path_list):
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, text in enumerate(path_list):
            if i > 0:
                sep = QLabel(" / ")
                sep.setStyleSheet("color: #64748B; font-size: 9pt;")
                self.breadcrumb_layout.addWidget(sep)
            lbl = QLabel(text)
            color = "#06B6D4" if i == len(path_list) - 1 else "#94A3B8"
            lbl.setStyleSheet(f"color: {color}; font-size: 9.5pt; font-weight: 600;")
            self.breadcrumb_layout.addWidget(lbl)

    def switch_to_view(self, target):
        """Routing resolver supporting ViewID enum, string name, or index."""
        if isinstance(target, ViewID):
            idx = self.VIEW_INDEX_MAP.get(target, 0)
        elif isinstance(target, str):
            try:
                vid = ViewID(target.lower())
                idx = self.VIEW_INDEX_MAP.get(vid, 0)
            except ValueError:
                idx = 0
        else:
            idx = int(target)

        self.switch_view(idx)

    def open_dashboard(self):
        """Explicitly opens the Main Dashboard workspace."""
        self.switch_to_view(ViewID.DASHBOARD)

    def open_simulation_workspace(self, hub=ViewID.ANALOG_HUB):
        """Explicitly opens the Interactive Simulation workspace."""
        self.switch_to_view(hub)
        curr_view = self.view_stack.currentWidget()
        target_obj = getattr(curr_view, "hub_view", curr_view)
        tabs_widget = getattr(target_obj, "main_tabs", getattr(target_obj, "tabs", getattr(target_obj, "tab_widget", None)))
        if tabs_widget:
            tabs_widget.setCurrentIndex(HubTabID.SIMULATION.value)

    def open_learning_workspace(self, hub=ViewID.DIGITAL_HUB):
        """Explicitly opens the Learning workspace."""
        self.switch_to_view(hub)
        curr_view = self.view_stack.currentWidget()
        target_obj = getattr(curr_view, "hub_view", curr_view)
        tabs_widget = getattr(target_obj, "main_tabs", getattr(target_obj, "tabs", getattr(target_obj, "tab_widget", None)))
        if tabs_widget:
            tabs_widget.setCurrentIndex(HubTabID.LEARN.value)



    def open_assessment_workspace(self):
        """Explicitly opens the Assessment workspace (Grand Viva / CBT)."""
        self.switch_to_view(ViewID.GRAND_VIVA)

    def open_settings(self):
        """Explicitly opens the Settings view."""
        self.switch_to_view(ViewID.SETTINGS)

    def switch_view(self, idx: int):
        if idx < 0 or idx >= len(self.views):
            return

        log.info(f"Switching view to index: {idx}")
        title = self.HUB_NAMES[idx]
        self.set_breadcrumbs(["Lab", title])
        self.status_bar.showMessage(f"Loaded {title} environment.")
        self.log_session_activity(f"Opened {title}")

        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
            btn.setProperty("active", "true" if i == idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Context awareness update for AI Drawer
        if hasattr(self, 'ai_drawer') and self.ai_drawer:
            self.ai_drawer.set_context({"hub_name": title})

        if config_manager.get("animations_enabled") and self.view_stack.currentWidget():
            self.opacity_effect = QGraphicsOpacityEffect(self.view_stack)
            self.view_stack.setGraphicsEffect(self.opacity_effect)
            
            self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out.setDuration(120)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            
            def on_fade_out_finished():
                self.view_stack.setCurrentIndex(idx)
                self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
                self.fade_in.setDuration(120)
                self.fade_in.setStartValue(0.0)
                self.fade_in.setEndValue(1.0)
                self.fade_in.start()

            self.fade_out.finished.connect(on_fade_out_finished)
            self.fade_out.start()
        else:
            self.view_stack.setCurrentIndex(idx)

    def navigate_to_component(self, comp_id):
        self.switch_to_view(ViewID.LIBRARY)
        lib_view = self.views[self.VIEW_INDEX_MAP[ViewID.LIBRARY]]
        if hasattr(lib_view, "load_component_detail"):
            lib_view.load_component_detail(comp_id)

    def navigate_to_lesson(self, lesson_id):
        self.switch_to_view(ViewID.DIGITAL_HUB)
        dsd_view = self.views[self.VIEW_INDEX_MAP[ViewID.DIGITAL_HUB]]
        if hasattr(dsd_view, "on_cross_link_clicked"):
            dsd_view.on_cross_link_clicked(lesson_id)

    def navigate_to_simulation(self, sim_idx):
        self.open_simulation_workspace(ViewID.ANALOG_HUB)

    def navigate_to_calculator(self, calc_idx):
        self.open_simulation_workspace(ViewID.ANALOG_HUB)


    def log_session_activity(self, action_str):
        self.session_activity.insert(0, action_str)
        if len(self.session_activity) > 10:
            self.session_activity.pop()

    def show_toast(self, text_msg):
        self.status_bar.showMessage(f"💡 {text_msg}", 5000)

    def show_shortcuts_guide(self):
        msg = (
            "<b>ElectroVerse Platform Keyboard Shortcuts:</b><br><br>"
            "• <b>Ctrl + B</b>: Toggle Left Sidebar<br>"
            "• <b>Ctrl + D</b>: Navigate to Main Dashboard<br>"
            "• <b>Ctrl + L</b>: Open Component Library<br>"
            "• <b>Ctrl + S</b>: Open Signal & System Hub<br>"
            "• <b>Ctrl + N</b>: Open Network Theory Hub<br>"
            "• <b>Ctrl + H</b>: Open Shortcuts Guide"
        )
        QMessageBox.information(self, "Keyboard Shortcuts Guide", msg)


    def show_about_dialog(self):
        self.switch_view(7)

    def showEvent(self, event):
        super().showEvent(event)
        screen_protection.enable_protection(self)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (event.Type.WindowStateChange, event.Type.ActivationChange):
            screen_protection.enable_protection(self)
