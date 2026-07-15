from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QStackedWidget, QLabel, QFrame, QSplitter, QPushButton
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager

# Import all simulation modules
from src.ui.simulation_modules.rc_transient import RCTransientSimulation
from src.ui.simulation_modules.rl_transient import RLTransientSimulation
from src.ui.simulation_modules.rlc_resonance import RLCResonanceSimulation
from src.ui.simulation_modules.rc_lowpass import RCLowPassSimulation
from src.ui.simulation_modules.rc_highpass import RCHighPassSimulation
from src.ui.simulation_modules.half_rectifier import HalfWaveRectifierSimulation
from src.ui.simulation_modules.full_rectifier import FullWaveRectifierSimulation
from src.ui.simulation_modules.attenuation import AttenuationSimulation
from src.ui.simulation_modules.voltage_divider import VoltageDividerSimulation
from src.ui.simulation_modules.resonance_explorer import ResonanceExplorerSimulation

class SimulationRowWidget(QWidget):
    """Custom row item for QListWidget displaying simulation name and favorite star toggle."""
    
    def __init__(self, name: str, icon_str: str, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.name = name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(qta.icon(icon_str, color="#06b6d4").pixmap(15, 15))
        
        # Title Label
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: 500; font-size: 10pt; color: #f8fafc;")
        
        # Star Favorite Toggle
        self.star_btn = QPushButton()
        self.star_btn.setFixedSize(22, 22)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.star_btn.setStyleSheet("border: none; background: transparent; padding: 0px;")
        
        self.update_star_icon()
        self.star_btn.clicked.connect(self.toggle_favorite)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.star_btn)
        
    def update_star_icon(self):
        favs = config_manager.get("sim_favorites") or []
        is_fav = str(self.index) in favs or self.index in favs
        icon_name = "fa5s.star"
        icon_color = "#f59e0b" if is_fav else "#475569"
        self.star_btn.setIcon(qta.icon(icon_name, color=icon_color))
        
    def toggle_favorite(self):
        favs = config_manager.get("sim_favorites") or []
        str_idx = str(self.index)
        
        if str_idx in favs:
            favs.remove(str_idx)
        elif self.index in favs:
            favs.remove(self.index)
        else:
            favs.append(str_idx)
            
        config_manager.set("sim_favorites", favs)
        self.update_star_icon()
        
        # Visual Toast
        top_window = self.window()
        if top_window and hasattr(top_window, "show_toast"):
            is_fav = str_idx in favs
            action_verb = "Added to" if is_fav else "Removed from"
            top_window.show_toast(f"{action_verb} Bookmarks: {self.name}", is_success=is_fav)

class SimulationView(QWidget):
    """Container view coordinating the split-pane Simulation Lab module with experiments list and search."""

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing SimulationView split layout")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # QSplitter layout container (left list pane, right experiment view)
        # -------------------------------------------------------------
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("sim-splitter")
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1e293b;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #06b6d4;
            }
        """)

        # Left Panel (List Shell)
        self.left_panel = QFrame()
        self.left_panel.setObjectName("card-panel")
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        # Search Bar layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search experiments...")
        self.search_input.textChanged.connect(self.filter_simulations)
        
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon("fa5s.search", color="#94a3b8").pixmap(QSize(13, 13)))
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                border-radius: 6px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(30, 41, 59, 0.4);
            }
            QListWidget::item:selected {
                background-color: rgba(6, 182, 212, 0.12);
                border-left: 3px solid #06b6d4;
                border-radius: 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
        """)
        self.list_widget.currentRowChanged.connect(self.on_simulation_selected)
        left_layout.addWidget(self.list_widget)

        # Empty Search Result Placeholder label
        self.empty_lbl = QLabel("No matches found")
        self.empty_lbl.setStyleSheet("color: #475569; font-style: italic; padding: 10px; font-size: 10pt;")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setVisible(False)
        left_layout.addWidget(self.empty_lbl)

        # Right Panel Stack
        self.right_stack = QStackedWidget()

        # Instantiate all 10 simulations
        self.simulations = [
            RCTransientSimulation(self),             # 0
            RLTransientSimulation(self),             # 1
            RLCResonanceSimulation(self),            # 2
            RCLowPassSimulation(self),               # 3
            RCHighPassSimulation(self),              # 4
            HalfWaveRectifierSimulation(self),       # 5
            FullWaveRectifierSimulation(self),       # 6
            AttenuationSimulation(self),             # 7
            VoltageDividerSimulation(self),           # 8
            ResonanceExplorerSimulation(self)        # 9
        ]

        self.sim_definitions = [
            ("RC Charging/Discharging", "fa5s.hourglass-half"),
            ("RL Transient Response", "fa5s.hourglass-start"),
            ("Series RLC Resonance", "fa5s.broadcast-tower"),
            ("Low Pass RC Filter", "fa5s.compress-arrows-alt"),
            ("High Pass RC Filter", "fa5s.expand-arrows-alt"),
            ("Half-Wave Rectifier", "fa5s.bolt"),
            ("Full-Wave Rectifier", "fa5s.plug"),
            ("Signal Attenuation", "fa5s.volume-mute"),
            ("Voltage Divider Visual", "fa5s.sliders-h"),
            ("Resonance Explorer", "fa5s.search-plus")
        ]

        # Populate custom row widgets
        for idx, ((name, icon_str), sim_view) in enumerate(zip(self.sim_definitions, self.simulations)):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 42)) # Adjust height of item cell
            
            row_widget = SimulationRowWidget(name, icon_str, idx, self)
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row_widget)
            self.right_stack.addWidget(sim_view)

        # Add left and right containers to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_stack)
        self.splitter.setSizes([270, 730]) # Default ratio
        
        self.main_layout.addWidget(self.splitter)
        
        # Default select first row
        self.list_widget.setCurrentRow(0)

    def on_simulation_selected(self, idx: int):
        """Switches details stacked view to target simulation."""
        if idx < 0 or idx >= len(self.simulations):
            return
        log.info(f"Simulation selected at index: {idx}")
        
        # Stop previously running simulation if any
        current_sim = self.right_stack.currentWidget()
        if current_sim and hasattr(current_sim, "reset_simulation"):
            try:
                current_sim.reset_simulation()
            except Exception as e:
                log.error(f"Error resetting current simulation: {e}")

        self.right_stack.setCurrentIndex(idx)
        
        # Set breadcrumbs
        top_window = self.window()
        if top_window and hasattr(top_window, "set_breadcrumbs"):
            top_window.set_breadcrumbs(["Lab", "Simulation Lab", self.sim_definitions[idx][0]])

    def filter_simulations(self, text: str):
        """Filters simulations matching search query."""
        text = text.lower()
        any_visible = False
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                match = text in row_widget.name.lower()
                item.setHidden(not match)
                if match:
                    any_visible = True
        self.empty_lbl.setVisible(not any_visible)

    def update_theme(self):
        """Notifies all simulations to repaint graphs under theme changes."""
        log.info("Refreshing all simulation graphs for theme change")
        
        # Repaint star icons on list rows
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                row_widget.update_star_icon()
                
        for sim in self.simulations:
            sim.update_theme()
            
    def showEvent(self, event):
        """Reload star toggles states on returns."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                row_widget.update_star_icon()
        super().showEvent(event)
