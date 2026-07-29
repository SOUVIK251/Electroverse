import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QLabel, QPushButton, QStackedWidget, QStatusBar,
    QGraphicsDropShadowEffect, QToolButton, QSizePolicy,
    QGraphicsOpacityEffect, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QShortcut, QKeySequence, QColor
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager
from src.core.theme import switch_theme

# Import Views
from src.ui.dashboard import DashboardView
from src.ui.library import LibraryView
from src.ui.analog_hub import AnalogElectronicsHubView
from src.ui.learning_hub import LearningHubView
from src.ui.grand_viva import GrandVivaView
from src.ui.settings import SettingsView

class CustomDialog(QDialog):
    """Custom styled dark-mode-friendly modal dialog."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(450, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #141B2D;
                border: 1px solid #26334D;
                border-radius: 12px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #2563EB;
                border: 1px solid #2563EB;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                border-color: #3B82F6;
            }
        """)

class MainWindow(QMainWindow):
    """Main window container for the ElectroVerse application shell."""

    def __init__(self):
        super().__init__()
        log.info("Initializing ElectroVerse MainWindow")
        self.setWindowTitle("⚡ ElectroVerse – Virtual Engineering Lab")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 720)
        
        # Session activity tracking
        self.session_activity = []

        # Central Widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central-widget")
        self.setCentralWidget(self.central_widget)

        # Global layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.nav_buttons = []
        
        # Setup layouts
        self.setup_sidebar()
        self.setup_main_container()
        self.setup_statusbar()

        # Keyboard Shortcuts
        self.setup_keyboard_shortcuts()

        # Restore window geometry state
        self.restore_window_state()

        # Default view load
        self.switch_view(0)

    def setup_sidebar(self):
        """Creates the collapsible left vertical navigation panel with animations."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand Header Panel
        brand_panel = QFrame()
        brand_panel.setFixedHeight(70)
        brand_panel.setStyleSheet("border-bottom: 1px solid rgba(255, 255, 255, 0.05);")
        brand_layout = QHBoxLayout(brand_panel)
        brand_layout.setContentsMargins(15, 0, 15, 0)
        brand_layout.setSpacing(10)

        # Collapse Button
        self.sidebar_toggle_btn = QPushButton()
        self.sidebar_toggle_btn.setFixedSize(32, 32)
        self.sidebar_toggle_btn.setStyleSheet("border: none; background: transparent; padding: 0px;")
        self.sidebar_toggle_btn.setIcon(qta.icon("fa5s.bars", color="#94a3b8"))
        self.sidebar_toggle_btn.setToolTip("Toggle Sidebar (Ctrl+B)")
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)

        logo_label = QLabel("⚡")
        logo_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #06B6D4;")
        
        self.title_label = QLabel("ElectroVerse")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold; letter-spacing: 1px; color: #FFFFFF;")

        brand_layout.addWidget(self.sidebar_toggle_btn)
        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(self.title_label)
        brand_layout.addStretch()

        sidebar_layout.addWidget(brand_panel)

        # Navigation Panel Area
        nav_panel = QWidget()
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(6)

        nav_items = [
            ("Dashboard", "fa5s.th-large", 0),
            ("Component Library", "fa5s.book", 1),
            ("Analog Electronics Circuit Hub", "fa5s.wave-square", 2),
            ("Digital System Design Hub", "fa5s.microchip", 3),
            ("Grand Viva & Core Interview", "fa5s.user-graduate", 4),
            ("Settings", "fa5s.cog", 5)
        ]

        for text, icon_str, idx in nav_items:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setIcon(qta.icon(icon_str, color="#94A3B8"))
            btn.setIconSize(QSize(18, 18))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(46)
            btn.setFixedWidth(240)
            btn.clicked.connect(lambda checked=False, target_idx=idx: self.switch_view(target_idx))
            
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_panel)

        # Footer Panel (Theme Switcher / Version / Shortcuts)
        footer_panel = QFrame()
        footer_panel.setFixedHeight(60)
        footer_panel.setStyleSheet("border-top: 1px solid #26334D;")
        footer_layout = QHBoxLayout(footer_panel)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("secondary")
        self.theme_btn.setIcon(qta.icon("fa5s.moon", color="#94A3B8"))
        self.theme_btn.setIconSize(QSize(16, 16))
        self.theme_btn.setToolTip("Switch Light/Dark Theme (Ctrl+T)")
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.clicked.connect(self.toggle_theme_icon)

        self.info_btn = QPushButton()
        self.info_btn.setObjectName("secondary")
        self.info_btn.setIcon(qta.icon("fa5s.question-circle", color="#94A3B8"))
        self.info_btn.setIconSize(QSize(16, 16))
        self.info_btn.setToolTip("Help & Keyboard Shortcuts (Ctrl+H)")
        self.info_btn.setFixedSize(32, 32)
        self.info_btn.clicked.connect(self.show_shortcuts_guide)

        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: #7A869A; font-size: 8.5pt;")

        footer_layout.addWidget(self.theme_btn)
        footer_layout.addWidget(self.info_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.version_label)

        sidebar_layout.addWidget(footer_panel)
        self.main_layout.addWidget(self.sidebar)

    def setup_main_container(self):
        """Creates the header toolbar and the stacked widget for views."""
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

        # Active state banner/indicator
        self.status_indicator = QLabel("System Status: Online")
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
            GrandVivaView(self),              # 4: Grand Viva & Core Interview
            SettingsView(self)                # 5: Settings
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
        QShortcut(QKeySequence("Ctrl+T"), self, self.toggle_theme_icon)
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_shortcuts_guide)
        QShortcut(QKeySequence("Ctrl+D"), self, lambda: self.switch_view(0))
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.switch_view(4))
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.switch_view(1))
        QShortcut(QKeySequence("Ctrl+A"), self, self.show_about_dialog)

    def toggle_sidebar(self):
        """Collapses or expands the navigation sidebar smoothly."""
        is_collapsed = self.sidebar.width() <= 80
        target_width = 260 if is_collapsed else 70

        if not config_manager.get("animations_enabled"):
            self.sidebar.setFixedWidth(target_width)
            self.title_label.setVisible(not is_collapsed)
            self.version_label.setVisible(not is_collapsed)
            for btn in self.nav_buttons:
                if not is_collapsed:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                    btn.setFixedWidth(46)
                else:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                    btn.setFixedWidth(240)
            return

        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setDuration(220)
        self.sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(target_width)
        
        self.sidebar_max_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_max_anim.setDuration(220)
        self.sidebar_max_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.sidebar_max_anim.setStartValue(self.sidebar.width())
        self.sidebar_max_anim.setEndValue(target_width)

        def on_anim_step():
            current_w = self.sidebar.width()
            collapsing = current_w < 160
            self.title_label.setVisible(not collapsing)
            self.version_label.setVisible(not collapsing)
            
            for btn in self.nav_buttons:
                if collapsing:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                    btn.setToolTip(btn.text().strip())
                    btn.setFixedWidth(46)
                else:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                    btn.setToolTip("")
                    btn.setFixedWidth(240)

        self.sidebar_anim.valueChanged.connect(lambda v: on_anim_step())
        self.sidebar_anim.finished.connect(on_anim_step)
        
        self.sidebar_anim.start()
        self.sidebar_max_anim.start()

    def set_breadcrumbs(self, path_list):
        """Sets the path indicators in the header toolbar dynamically."""
        # Clear existing breadcrumbs
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i, path in enumerate(path_list):
            label = QLabel(path)
            if i == len(path_list) - 1:
                label.setStyleSheet("color: #FFFFFF; font-weight: 600; font-size: 14pt;")
            else:
                label.setStyleSheet("color: #7A869A; font-weight: 500; font-size: 14pt;")
            self.breadcrumb_layout.addWidget(label)

            if i < len(path_list) - 1:
                sep = QLabel("/")
                sep.setStyleSheet("color: #26334D; font-size: 14pt;")
                self.breadcrumb_layout.addWidget(sep)

    def switch_view(self, idx: int):
        """Switches the stacked widget view smoothly with opacity transitions."""
        if idx < 0 or idx >= len(self.views):
            return

        log.info(f"Switching view to index: {idx}")
        
        # Breadcrumbs update
        titles = [
            "Dashboard", "Component Library", "Learning Mode",
            "Engineering Toolkit", "Simulation Lab", "Digital Oscilloscope",
            "Grand Viva & Core Interview", "Settings"
        ]
        self.set_breadcrumbs(["Lab", titles[idx]])
        self.status_bar.showMessage(f"Loaded {titles[idx]} environment.")
        self.log_session_activity(f"Opened {titles[idx]}")

        # Update sidebar button checkable highlights
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
            btn.setProperty("active", "true" if i == idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Transition Animation
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
                self.fade_in.setDuration(150)
                self.fade_in.setStartValue(0.0)
                self.fade_in.setEndValue(1.0)
                def clean_up():
                    self.view_stack.setGraphicsEffect(None)
                self.fade_in.finished.connect(clean_up)
                self.fade_in.start()
                
            self.fade_out.finished.connect(on_fade_out_finished)
            self.fade_out.start()
        else:
            self.view_stack.setCurrentIndex(idx)

    def toggle_theme_icon(self):
        """Toggles current application theme (dark/light) dynamically."""
        switch_theme()
        current_theme = config_manager.get("theme")
        
        # Style triggers refresh
        self.central_widget.style().unpolish(self.central_widget)
        self.central_widget.style().polish(self.central_widget)

        if current_theme == "dark":
            self.theme_btn.setIcon(qta.icon("fa5s.moon", color="#94a3b8"))
        else:
            self.theme_btn.setIcon(qta.icon("fa5s.sun", color="#475569"))
            
        for view in self.views:
            if hasattr(view, "update_theme"):
                try:
                    view.update_theme()
                except Exception as e:
                    log.error(f"Error updating theme on view: {e}")

        self.show_toast(f"Switched theme to {current_theme.title()} mode.")
        log.info(f"Main Window theme toggled to {current_theme}")

    def show_toast(self, message: str, is_success: bool = True):
        """Overlay Toast display helper."""
        from src.ui.components.toast import ToastNotification
        ToastNotification(self, message, is_success)

    def show_shortcuts_guide(self):
        """Displays beautiful keyboard shortcut mappings in a custom dialog."""
        dlg = CustomDialog("Keyboard Shortcuts Guide", self)
        dlg.setMinimumSize(500, 360)
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Keyboard Shortcut Mappings")
        title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #06b6d4;")
        layout.addWidget(title)

        table = QTableWidget(5, 2)
        table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                border: 1px solid #1e293b;
                gridline-color: #1e293b;
                color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        shortcuts = [
            ("Toggle Sidebar Panel", "Ctrl + B"),
            ("Toggle Dark/Light Theme", "Ctrl + T"),
            ("Navigate to Dashboard", "Ctrl + D"),
            ("Navigate to Engineering Toolkit", "Ctrl + K"),
            ("Show About Dialog Info", "Ctrl + A")
        ]

        for row, (action, keys) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(keys))

        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.exec()

    def show_about_dialog(self):
        """Displays ElectroVerse about product information and creator credits."""
        dlg = CustomDialog("About ElectroVerse", self)
        dlg.setMinimumSize(480, 420)
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        logo = QLabel("⚡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 36pt; color: #10b981;")

        title = QLabel("ElectroVerse – Virtual Engineering Lab")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #f8fafc;")

        version = QLabel("Version 1.0.0 (Offline Edition)")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 9pt;")

        desc = QLabel(
            "An offline, interactive desktop suite for electronics engineering education, digital logic design, virtual breadboard circuit simulation, and core interview viva preparation."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #94a3b8; font-size: 9.5pt; line-height: 1.4;")

        credit_card = QFrame()
        credit_card.setStyleSheet("""
            QFrame {
                background-color: #1e1b4b;
                border: 2px solid #6366f1;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        cc_lay = QVBoxLayout(credit_card)
        cc_lay.setSpacing(4)
        cc_tag = QLabel("PROJECT CREATOR & LEAD DEVELOPER")
        cc_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cc_tag.setStyleSheet("color: #818cf8; font-weight: bold; font-size: 7.5pt; letter-spacing: 1px;")
        
        cc_name = QLabel("Created & Developed by Souvik Kundu")
        cc_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cc_name.setStyleSheet("color: #ffffff; font-size: 12.5pt; font-weight: bold;")
        
        cc_lay.addWidget(cc_tag)
        cc_lay.addWidget(cc_name)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #06b6d4; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        close_btn.clicked.connect(dlg.accept)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(desc)
        layout.addWidget(credit_card)
        layout.addWidget(close_btn)
        
        dlg.exec()

    def save_window_state(self):
        """Saves window geometries to settings configuration."""
        config_manager.set("window_geometry", self.saveGeometry().toHex().data().decode())
        config_manager.set("window_state", self.saveState().toHex().data().decode())
        config_manager.set("window_maximized", self.isMaximized())

    def restore_window_state(self):
        """Restores window geometries from settings configuration."""
        geom_hex = config_manager.get("window_geometry")
        state_hex = config_manager.get("window_state")
        is_max = config_manager.get("window_maximized")
        
        if geom_hex:
            try:
                self.restoreGeometry(bytes.fromhex(geom_hex))
            except Exception as e:
                log.error(f"Error restoring geometry: {e}")
        if state_hex:
            try:
                self.restoreState(bytes.fromhex(state_hex))
            except Exception as e:
                log.error(f"Error restoring state: {e}")
        if is_max:
            self.showMaximized()

    def closeEvent(self, event):
        """Save settings and geometry coordinates on exit."""
        self.save_window_state()
        super().closeEvent(event)

    def log_session_activity(self, action_text: str):
        """Logs user session action and refreshes Dashboard if displayed."""
        if not action_text:
            return
        # Avoid consecutive duplicates
        if self.session_activity and self.session_activity[0] == action_text:
            return
        self.session_activity.insert(0, action_text)
        if len(self.session_activity) > 5:
            self.session_activity = self.session_activity[:5]
        
        # If dashboard is visible, refresh it
        if hasattr(self, "views") and len(self.views) > 0:
            dashboard = self.views[0]
            if hasattr(dashboard, "refresh_activity_logs"):
                dashboard.refresh_activity_logs()

    def navigate_to_component(self, comp_id: str):
        """Helper to switch to Component Library and select a component by ID."""
        self.switch_view(1)
        library_view = self.views[1]
        if hasattr(library_view, "select_component_by_id"):
            library_view.select_component_by_id(comp_id)

    def navigate_to_lesson(self, lesson_id: str):
        """Helper to switch to Analog Hub (Theory sub-tab) and load a lesson by ID."""
        self.switch_view(2)
        analog_hub = self.views[2]
        if hasattr(analog_hub, "load_lesson"):
            analog_hub.load_lesson(lesson_id)

    def navigate_to_calculator(self, calc_index: int):
        """Helper to switch to Analog Hub (Toolkit sub-tab) and load a calculator by index."""
        self.switch_view(2)
        analog_hub = self.views[2]
        if hasattr(analog_hub, "select_calculator"):
            analog_hub.select_calculator(calc_index)

    def navigate_to_simulation(self, sim_index: int):
        """Helper to switch to Analog Hub (Simulation Lab sub-tab) and load a simulation by index."""
        self.switch_view(2)
        analog_hub = self.views[2]
        if hasattr(analog_hub, "select_simulation"):
            analog_hub.select_simulation(sim_index)
