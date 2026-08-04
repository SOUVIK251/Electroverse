"""
ElectroVerse Centralized Theme Engine - Professional Dark Engineering Theme
Provides a single unified dark engineering theme throughout ElectroVerse.
"""

from PySide6.QtWidgets import QApplication
from src.core.logger import log
from src.core.config import config_manager


class ThemeManager:
    """Centralized Theme Manager providing a modern, premium engineering laboratory dark theme."""

    DARK_PALETTE = {
        "bg_window": "#0B1020",             # Window Background
        "bg_sidebar": "#111827",            # Sidebar Background
        "sidebar_selected": "#1E293B",      # Sidebar Selected Item
        "sidebar_hover": "#182235",         # Sidebar Hover
        "bg_card": "#141B2D",               # Cards Background
        "bg_card_hover": "#1B2740",          # Cards Hover
        "top_nav": "#101827",               # Top Navigation Background
        "border_color": "#26334D",          # Borders & Gridlines
        "border_focus": "#06B6D4",          # Focus / Active Borders
        "accent_primary": "#06B6D4",        # Primary Accent (highlights, active icons, selected tabs, links)
        "accent_secondary": "#2563EB",      # Secondary Accent (primary buttons, nav highlights)
        "accent_secondary_hover": "#3B82F6",
        "accent_secondary_pressed": "#1D4ED8",
        "text_primary": "#FFFFFF",          # Primary Text
        "text_secondary": "#C9D1E3",        # Secondary Text
        "text_muted": "#7A869A",            # Muted / Subtitle Text
        "icon_inactive": "#94A3B8",         # Inactive Icons
        "icon_active": "#06B6D4",           # Active Icons
        "success": "#22C55E",               # Success / Ready Status
        "warning": "#F59E0B",               # Warning Status
        "danger": "#EF4444",                # Error Status
        "info": "#38BDF8",                  # Info / Stats Numbers
        "table_header": "#111827",          # Table Header Background
        "table_row": "#141B2D",             # Table Row Background
        "table_row_alt": "#182235",         # Table Alternate Row
        "table_selection": "#1E3A5F",       # Table Selection
        "dialog_bg": "#141B2D",             # Dialog Window Background
        "dialog_border": "#26334D"
    }

    @classmethod
    def get_palette(cls, theme_name: str = "dark") -> dict:
        return cls.DARK_PALETTE

    @classmethod
    def get_stylesheet(cls, theme_name: str = "dark") -> str:
        """Returns the centralized Dark Engineering QSS stylesheet."""
        palette = cls.DARK_PALETTE
        base_fs = config_manager.get("font_size") or 11
        
        qss = f"""
        /* Global Defaults */
        QWidget {{
            background-color: transparent;
            color: {palette["text_primary"]};
            font-family: "Segoe UI", "Inter", system-ui, -apple-system, sans-serif;
            font-size: {base_fs}pt;
        }}

        QMainWindow {{
            background-color: {palette["bg_window"]};
        }}

        /* Central Widget Container */
        #central-widget {{
            background-color: {palette["bg_window"]};
        }}

        /* Labels */
        QLabel {{
            color: {palette["text_primary"]};
        }}
        QLabel[secondary="true"] {{
            color: {palette["text_secondary"]};
        }}
        QLabel[muted="true"] {{
            color: {palette["text_muted"]};
        }}

        /* Sidebar Styling */
        #sidebar {{
            background-color: {palette["bg_sidebar"]};
            border-right: 1px solid {palette["border_color"]};
        }}

        /* Navigation Buttons inside Sidebar */
        #sidebar QToolButton {{
            background-color: transparent;
            color: {palette["text_secondary"]};
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            text-align: left;
            font-weight: 500;
        }}

        #sidebar QToolButton:hover {{
            background-color: {palette["sidebar_hover"]};
            color: {palette["text_primary"]};
        }}

        #sidebar QToolButton:checked {{
            background-color: {palette["sidebar_selected"]};
            color: {palette["accent_primary"]};
            border-left: 3px solid {palette["accent_primary"]};
            font-weight: 600;
        }}

        /* Card Panels / Containers */
        .QFrame, QFrame#card-panel {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 8px;
        }}

        /* Top Navigation & Headers */
        #header-bar {{
            background-color: {palette["top_nav"]};
            border-bottom: 1px solid {palette["border_color"]};
        }}

        /* Push Buttons */
        QPushButton {{
            background-color: {palette["accent_secondary"]};
            color: {palette["text_primary"]};
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {palette["accent_secondary_hover"]};
        }}

        QPushButton:pressed {{
            background-color: {palette["accent_secondary_pressed"]};
        }}

        QPushButton[outlined="true"] {{
            background-color: transparent;
            border: 1px solid {palette["border_color"]};
            color: {palette["text_primary"]};
        }}

        QPushButton[outlined="true"]:hover {{
            background-color: {palette["sidebar_hover"]};
            border-color: {palette["accent_primary"]};
        }}

        /* LineEdits / Inputs */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {palette["bg_sidebar"]};
            color: {palette["text_primary"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 6px;
            padding: 6px 12px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
            border-color: {palette["border_focus"]};
        }}

        /* Tables & Lists */
        QTableWidget, QTreeWidget, QListWidget {{
            background-color: {palette["bg_card"]};
            gridline-color: {palette["border_color"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 6px;
        }}

        QHeaderView::section {{
            background-color: {palette["table_header"]};
            color: {palette["text_secondary"]};
            padding: 6px 12px;
            border: none;
            border-bottom: 1px solid {palette["border_color"]};
            font-weight: 600;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background: {palette["bg_sidebar"]};
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {palette["border_color"]};
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {palette["accent_primary"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        /* Tab Bar */
        QTabBar::tab {{
            background-color: {palette["bg_sidebar"]};
            color: {palette["text_muted"]};
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:selected {{
            color: {palette["accent_primary"]};
            border-bottom: 2px solid {palette["accent_primary"]};
            font-weight: 600;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {palette["top_nav"]};
            border-top: 1px solid {palette["border_color"]};
            color: {palette["text_muted"]};
            font-size: {base_fs - 1.5}pt;
        }}
        """
        return qss

    @classmethod
    def apply_theme(cls, app: QApplication, theme_name: str = "dark") -> None:
        """Applies the single Dark Engineering Theme to the application instance."""
        try:
            stylesheet = cls.get_stylesheet("dark")
            app.setStyleSheet(stylesheet)
            log.info("Dark Engineering Theme applied successfully.")
        except Exception as e:
            log.error(f"Error applying theme: {e}")
