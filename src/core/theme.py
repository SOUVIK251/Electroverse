from PySide6.QtWidgets import QApplication
from src.core.logger import log
from src.core.config import config_manager

class ThemeManager:
    """Manages the styling of the application using QSS stylesheets."""

    DARK_PALETTE = {
        "bg_primary": "#0b0f19",
        "bg_secondary": "#111827",
        "bg_card": "rgba(30, 41, 59, 0.7)",  # Glassmorphic base
        "border_color": "#1e293b",
        "border_focus": "#06b6d4",            # Neon Cyan
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent": "#10b981",                  # Neon Emerald
        "accent_hover": "#059669",
        "danger": "#ef4444",
        "surface_hover": "#1e293b"
    }

    LIGHT_PALETTE = {
        "bg_primary": "#f8fafc",
        "bg_secondary": "#f1f5f9",
        "bg_card": "rgba(255, 255, 255, 0.8)",
        "border_color": "#e2e8f0",
        "border_focus": "#3b82f6",            # Electric Blue
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "accent": "#6366f1",                  # Indigo
        "accent_hover": "#4f46e5",
        "danger": "#dc2626",
        "surface_hover": "#e2e8f0"
    }

    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        """Returns the QSS stylesheet for the requested theme dynamically scaling font size."""
        palette = cls.DARK_PALETTE if theme_name == "dark" else cls.LIGHT_PALETTE
        
        # Load user set font size
        base_fs = config_manager.get("font_size") or 11
        
        # Modern global QSS styling
        qss = f"""
        /* Global Defaults */
        QWidget {{
            background-color: transparent;
            color: {palette["text_primary"]};
            font-family: "Segoe UI", "Inter", "Helvetica", Arial, sans-serif;
            font-size: {base_fs}pt;
        }}

        QMainWindow {{
            background-color: {palette["bg_primary"]};
        }}

        /* Central Widget */
        #central-widget {{
            background-color: {palette["bg_primary"]};
        }}

        /* Labels */
        QLabel {{
            color: {palette["text_primary"]};
        }}
        QLabel[secondary="true"] {{
            color: {palette["text_secondary"]};
            font-size: {base_fs - 1.5}pt;
        }}

        /* Rounded Glassmorphic Panels / Cards */
        QFrame#card-panel, QFrame.CardPanel {{
            background-color: {palette["bg_card"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 12px;
        }}

        /* Side Navigation Panel */
        QFrame#sidebar {{
            background-color: {palette["bg_secondary"]};
            border-right: 1px solid {palette["border_color"]};
        }}

        /* Buttons styling */
        QPushButton {{
            background-color: {palette["surface_hover"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 6px;
            padding: 8px 16px;
            color: {palette["text_primary"]};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {palette["border_color"]};
            border-color: {palette["border_focus"]};
        }}
        QPushButton:pressed {{
            background-color: {palette["bg_primary"]};
        }}

        QPushButton[primary="true"] {{
            background-color: {palette["accent"]};
            border-color: {palette["accent"]};
            color: #ffffff;
        }}
        QPushButton[primary="true"]:hover {{
            background-color: {palette["accent_hover"]};
            border-color: {palette["accent_hover"]};
        }}
        
        QPushButton[secondary="true"] {{
            background-color: transparent;
            border-color: transparent;
            color: {palette["text_secondary"]};
        }}
        QPushButton[secondary="true"]:hover {{
            color: {palette["text_primary"]};
            background-color: {palette["surface_hover"]};
        }}

        /* Tool Buttons (Sidebar Icons) */
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 10px;
            color: {palette["text_secondary"]};
            text-align: left;
        }}
        QToolButton:hover {{
            background-color: {palette["surface_hover"]};
            color: {palette["text_primary"]};
        }}
        QToolButton:checked, QToolButton[active="true"] {{
            background-color: {palette["accent"]}22; /* 12% opacity */
            border-left: 3px solid {palette["accent"]};
            color: {palette["text_primary"]};
            border-radius: 0px;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }}

        /* Inputs & Textboxes */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {palette["bg_secondary"]};
            border: 1px solid {palette["border_color"]};
            border-radius: 6px;
            padding: 6px 10px;
            color: {palette["text_primary"]};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {palette["border_focus"]};
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            height: 6px;
            background: {palette["border_color"]};
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: {palette["accent"]};
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
            background: {palette["accent"]};
            border-color: {palette["border_focus"]};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {palette["text_secondary"]}44;
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {palette["text_secondary"]}aa;
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
            background: {palette["text_secondary"]}44;
            min-width: 20px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {palette["text_secondary"]}aa;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {palette["border_color"]};
            border-radius: 8px;
            background-color: {palette["bg_card"]};
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {palette["text_secondary"]};
            padding: 8px 16px;
            margin-right: 4px;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:hover {{
            color: {palette["text_primary"]};
        }}
        QTabBar::tab:selected {{
            color: {palette["accent"]};
            border-bottom: 2px solid {palette["accent"]};
            font-weight: 600;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {palette["bg_secondary"]};
            border-top: 1px solid {palette["border_color"]};
            color: {palette["text_secondary"]};
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
