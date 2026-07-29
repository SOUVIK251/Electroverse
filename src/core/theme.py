from PySide6.QtWidgets import QApplication
from src.core.logger import log
from src.core.config import config_manager

class ThemeManager:
    """Centralized Theme Manager providing a modern, premium engineering laboratory theme."""

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

    LIGHT_PALETTE = {
        "bg_window": "#F8FAFC",
        "bg_sidebar": "#F1F5F9",
        "sidebar_selected": "#E2E8F0",
        "sidebar_hover": "#EDF2F7",
        "bg_card": "#FFFFFF",
        "bg_card_hover": "#F8FAFC",
        "top_nav": "#FFFFFF",
        "border_color": "#CBD5E1",
        "border_focus": "#2563EB",
        "accent_primary": "#06B6D4",
        "accent_secondary": "#2563EB",
        "accent_secondary_hover": "#3B82F6",
        "accent_secondary_pressed": "#1D4ED8",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "icon_inactive": "#64748B",
        "icon_active": "#2563EB",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "info": "#0284C7",
        "table_header": "#F1F5F9",
        "table_row": "#FFFFFF",
        "table_row_alt": "#F8FAFC",
        "table_selection": "#DBEAFE",
        "dialog_bg": "#FFFFFF",
        "dialog_border": "#CBD5E1"
    }

    @classmethod
    def get_palette(cls, theme_name: str = "dark") -> dict:
        return cls.DARK_PALETTE if theme_name == "dark" else cls.LIGHT_PALETTE

    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        """Returns the centralized QSS stylesheet for the requested theme."""
        palette = cls.get_palette(theme_name)
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
            font-size: {base_fs - 1.5}pt;
        }}
        QLabel[muted="true"] {{
            color: {palette["text_muted"]};
            font-size: {base_fs - 2}pt;
        }}

        /* Premium Laboratory Cards */
        QFrame#card-panel, QFrame.CardPanel, QFrame#card, QFrame#metric-card, QFrame#launch-card, QFrame#qb-card {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 10px;
        }}
        QFrame#card-panel:hover, QFrame#metric-card:hover, QFrame#launch-card:hover, QFrame#qb-card:hover {{
            border-color: {palette["border_focus"]};
            background-color: {palette["bg_card_hover"]};
        }}

        /* Top Navigation Header Bar */
        QFrame#header-bar {{
            background-color: {palette["top_nav"]};
            border-bottom: 1px solid {palette["border_color"]};
        }}

        /* Side Navigation Panel */
        QFrame#sidebar {{
            background-color: {palette["bg_sidebar"]};
            border-right: 1px solid {palette["border_color"]};
        }}

        /* Navigation Buttons (Sidebar Tools) */
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 10px 14px;
            color: {palette["icon_inactive"]};
            text-align: left;
            font-weight: 500;
        }}
        QToolButton:hover {{
            background-color: {palette["sidebar_hover"]};
            color: {palette["text_primary"]};
        }}
        QToolButton:checked, QToolButton[active="true"] {{
            background-color: {palette["sidebar_selected"]};
            border-left: 3px solid {palette["accent_secondary"]};
            color: {palette["accent_primary"]};
            font-weight: 600;
            border-radius: 0px;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }}

        /* Standard Buttons */
        QPushButton {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 10px;
            padding: 8px 16px;
            color: {palette["text_primary"]};
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {palette["bg_card_hover"]};
            border-color: {palette["border_focus"]};
            color: {palette["text_primary"]};
        }}
        QPushButton:pressed {{
            background-color: {palette["bg_sidebar"]};
        }}

        /* Primary Accent Buttons */
        QPushButton[primary="true"], QPushButton#btn-primary {{
            background-color: {palette["accent_secondary"]};
            border: 1px solid {palette["accent_secondary"]};
            color: #FFFFFF;
            border-radius: 10px;
            font-weight: bold;
        }}
        QPushButton[primary="true"]:hover, QPushButton#btn-primary:hover {{
            background-color: {palette["accent_secondary_hover"]};
            border-color: {palette["accent_secondary_hover"]};
        }}
        QPushButton[primary="true"]:pressed, QPushButton#btn-primary:pressed {{
            background-color: {palette["accent_secondary_pressed"]};
            border-color: {palette["accent_secondary_pressed"]};
        }}

        /* Secondary Transparent Buttons */
        QPushButton[secondary="true"], QPushButton#secondary {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            color: {palette["text_secondary"]};
            border-radius: 10px;
        }}
        QPushButton[secondary="true"]:hover, QPushButton#secondary:hover {{
            color: {palette["text_primary"]};
            background-color: {palette["bg_card_hover"]};
            border-color: {palette["border_focus"]};
        }}

        /* Search Bars & Text Inputs */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {palette["bg_sidebar"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 8px;
            padding: 8px 12px;
            color: {palette["text_primary"]};
            selection-background-color: {palette["table_selection"]};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {palette["border_focus"]};
        }}
        QLineEdit::placeholder {{
            color: {palette["text_muted"]};
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {palette["bg_sidebar"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 8px;
            padding: 6px 12px;
            color: {palette["text_primary"]};
        }}
        QComboBox:focus, QComboBox:hover {{
            border-color: {palette["border_focus"]};
        }}
        QComboBox QAbstractItemView {{
            background-color: {palette["bg_sidebar"]};
            border: 1px solid {palette["border_color"]};
            selection-background-color: {palette["table_selection"]};
            selection-color: {palette["accent_primary"]};
            color: {palette["text_primary"]};
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            height: 6px;
            background: {palette["border_color"]};
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: {palette["accent_secondary"]};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {palette["text_primary"]};
            border: 1px solid {palette["border_color"]};
            width: 16px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {palette["accent_primary"]};
            border-color: {palette["border_focus"]};
        }}

        /* Tables & Lists */
        QTableWidget, QTreeWidget, QListWidget {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            gridline-color: {palette["border_color"]};
            color: {palette["text_primary"]};
            border-radius: 8px;
        }}
        QTableWidget::item, QListWidget::item {{
            padding: 6px 10px;
            border-bottom: 1px solid {palette["border_color"]};
        }}
        QTableWidget::item:alternate, QListWidget::item:alternate {{
            background-color: {palette["table_row_alt"]};
        }}
        QTableWidget::item:hover, QListWidget::item:hover {{
            background-color: {palette["bg_card_hover"]};
            color: {palette["accent_primary"]};
        }}
        QTableWidget::item:selected, QListWidget::item:selected {{
            background-color: {palette["table_selection"]};
            color: {palette["accent_primary"]};
            font-weight: bold;
        }}
        QHeaderView::section {{
            background-color: {palette["table_header"]};
            color: {palette["text_secondary"]};
            font-weight: bold;
            padding: 8px;
            border: none;
            border-bottom: 1px solid {palette["border_color"]};
        }}

        /* Dialog Windows */
        QDialog {{
            background-color: {palette["dialog_bg"]};
            border: 1px solid {palette["dialog_border"]};
            border-radius: 12px;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {palette["border_color"]};
            min-height: 24px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {palette["accent_primary"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {palette["border_color"]};
            min-width: 24px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {palette["accent_primary"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}

        /* Tab Bar */
        QTabWidget::pane {{
            border: 1px solid {palette["border_color"]};
            border-radius: 8px;
            background-color: {palette["bg_card"]};
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {palette["text_muted"]};
            padding: 10px 18px;
            margin-right: 4px;
            border-bottom: 2px solid transparent;
            font-weight: 500;
        }}
        QTabBar::tab:hover {{
            color: {palette["text_secondary"]};
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
    def apply_theme(cls, app: QApplication, theme_name: str) -> None:
        """Applies the specified theme to the application instance."""
        try:
            stylesheet = cls.get_stylesheet(theme_name)
            app.setStyleSheet(stylesheet)
            log.info(f"Theme '{theme_name}' applied successfully.")
        except Exception as e:
            log.error(f"Error applying theme: {e}")

# Helper function to switch theme
def switch_theme() -> None:
    app = QApplication.instance()
    if app:
        current_theme = config_manager.get("theme")
        new_theme = "light" if current_theme == "dark" else "dark"
        config_manager.set("theme", new_theme)
        ThemeManager.apply_theme(app, new_theme)
