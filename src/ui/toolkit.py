from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QStackedWidget, QLabel, QFrame, QSplitter, QPushButton
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from src.core.logger import log
from src.core.config import config_manager

# Import all calculators
from src.ui.toolkit_modules.ohms_law import OhmsLawCalculator
from src.ui.toolkit_modules.voltage_divider import VoltageDividerCalculator
from src.ui.toolkit_modules.current_divider import CurrentDividerCalculator
from src.ui.toolkit_modules.power import PowerCalculator
from src.ui.toolkit_modules.rc_time import RCTimeConstantCalculator
from src.ui.toolkit_modules.rl_time import RLTimeConstantCalculator
from src.ui.toolkit_modules.rlc_resonance import RLCResonanceCalculator
from src.ui.toolkit_modules.frequency import FrequencyCalculator
from src.ui.toolkit_modules.capacitive_reactance import CapacitiveReactanceCalculator
from src.ui.toolkit_modules.inductive_reactance import InductiveReactanceCalculator
from src.ui.toolkit_modules.led_resistor import LEDSeriesResistorCalculator

class CalculatorRowWidget(QWidget):
    """Custom row item for QListWidget displaying calculator name and favorite star toggle."""
    
    def __init__(self, name: str, icon_str: str, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.name = name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(qta.icon(icon_str, color="#94a3b8").pixmap(15, 15))
        
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
        favs = config_manager.get("favorites") or []
        is_fav = str(self.index) in favs or self.index in favs
        icon_name = "fa5s.star"
        icon_color = "#f59e0b" if is_fav else "#475569"
        self.star_btn.setIcon(qta.icon(icon_name, color=icon_color))
        
    def toggle_favorite(self):
        favs = config_manager.get("favorites") or []
        str_idx = str(self.index)
        
        if str_idx in favs:
            favs.remove(str_idx)
        elif self.index in favs:
            favs.remove(self.index)
        else:
            favs.append(str_idx)
            
        config_manager.set("favorites", favs)
        self.update_star_icon()
        
        # Visual Toast
        top_window = self.window()
        if top_window and hasattr(top_window, "show_toast"):
            is_fav = str_idx in favs
            action_verb = "Added to" if is_fav else "Removed from"
            top_window.show_toast(f"{action_verb} Bookmarks: {self.name}", is_success=is_fav)

class ToolkitView(QWidget):
    """Container view coordinating the split-pane Engineering Toolkit module with search and list widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing ToolkitView split layout")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # QSplitter layout container (left list pane, right instrument panel)
        # -------------------------------------------------------------
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("toolkit-splitter")
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
        self.search_input.setPlaceholderText("Search instruments...")
        self.search_input.textChanged.connect(self.filter_calculators)
        
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
        self.list_widget.currentRowChanged.connect(self.on_calculator_selected)
        left_layout.addWidget(self.list_widget)

        # Empty Search Result Placeholder label
        self.empty_lbl = QLabel("No matches found")
        self.empty_lbl.setStyleSheet("color: #475569; font-style: italic; padding: 10px; font-size: 10pt;")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setVisible(False)
        left_layout.addWidget(self.empty_lbl)

        # Right Panel Stack
        self.right_stack = QStackedWidget()

        # Instantiate all 11 calculators
        self.calculators = [
            OhmsLawCalculator(self),                  # 0
            VoltageDividerCalculator(self),           # 1
            CurrentDividerCalculator(self),           # 2
            PowerCalculator(self),                    # 3
            RCTimeConstantCalculator(self),           # 4
            RLTimeConstantCalculator(self),           # 5
            RLCResonanceCalculator(self),             # 6
            FrequencyCalculator(self),                # 7
            CapacitiveReactanceCalculator(self),      # 8
            InductiveReactanceCalculator(self),       # 9
            LEDSeriesResistorCalculator(self)         # 10
        ]

        self.calc_definitions = [
            ("Ohm's Law", "fa5s.bolt"),
            ("Voltage Divider", "fa5s.compress-arrows-alt"),
            ("Current Divider", "fa5s.expand-arrows-alt"),
            ("Power Calculator", "fa5s.plug"),
            ("RC Time Constant", "fa5s.hourglass-half"),
            ("RL Time Constant", "fa5s.hourglass-start"),
            ("RLC Resonance", "fa5s.broadcast-tower"),
            ("Frequency Calculator", "fa5s.wave-square"),
            ("Capacitive Reactance", "fa5s.layer-group"),
            ("Inductive Reactance", "fa5s.scroll"),
            ("LED Series Resistor", "fa5s.lightbulb")
        ]

        # Populate custom row widgets
        for idx, ((name, icon_str), calc_view) in enumerate(zip(self.calc_definitions, self.calculators)):
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 42)) # Adjust height of item cell
            
            # Custom widget
            row_widget = CalculatorRowWidget(name, icon_str, idx, self)
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row_widget)
            self.right_stack.addWidget(calc_view)

        # Add left and right containers to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_stack)
        self.splitter.setSizes([270, 730]) # Default ratio
        
        self.main_layout.addWidget(self.splitter)
        
        # Default select first row
        self.list_widget.setCurrentRow(0)

    def on_calculator_selected(self, idx: int):
        """Switches details stacked view to target calculator and runs calculate."""
        if idx < 0 or idx >= len(self.calculators):
            return
        log.info(f"Calculator selected at index: {idx}")
        self.right_stack.setCurrentIndex(idx)
        
        # Record workspace history
        recent = config_manager.get("recently_used") or []
        str_idx = str(idx)
        if str_idx in recent:
            recent.remove(str_idx)
        recent.insert(0, str_idx)
        config_manager.set("recently_used", recent[:10])

        # Execute calculation to refresh plots automatically
        self.calculators[idx].calculate()

    def filter_calculators(self, text: str):
        """Filters calculator items matching search query."""
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
        """Notifies all calculators to repaint graphs under theme changes."""
        log.info("Refreshing all Matplotlib graphs for theme change")
        
        # Repaint star icons on list rows
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                row_widget.update_star_icon()
                
        for calc in self.calculators:
            calc.update_theme()
            
    def showEvent(self, event):
        """Reload star toggles states on dashboard returns."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row_widget = self.list_widget.itemWidget(item)
            if row_widget:
                row_widget.update_star_icon()
        super().showEvent(event)
