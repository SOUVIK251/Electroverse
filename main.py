import sys
import os
import time

# Add root folder to sys.path to resolve module paths correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QCoreApplication

from src.core.logger import log
from src.core.config import config_manager
from src.core.theme import ThemeManager
from src.ui.main_window import MainWindow

class ElectroVerseSplash(QSplashScreen):
    """Premium splash screen with neon branding and animated progress bar."""
    
    def __init__(self):
        # Create 500x320 canvas
        pix = QPixmap(500, 320)
        pix.fill(QColor("#0f172a")) # Premium Slate-900
        super().__init__(pix)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 30)
        self.layout.setSpacing(10)
        
        # Logo
        logo = QLabel("⚡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 52pt; color: #10b981; font-weight: bold;")
        
        # Title
        title = QLabel("ELECTROVERSE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22pt; font-weight: 800; color: #f8fafc; letter-spacing: 4px;")
        
        # Subtitle
        subtitle = QLabel("VIRTUAL ENGINEERING LAB")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 9.5pt; color: #94a3b8; letter-spacing: 2px; font-weight: 500;")
        
        self.layout.addWidget(logo)
        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)
        self.layout.addStretch()
        
        # Loading Step Info text
        self.step_label = QLabel("Initializing components...")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet("font-size: 9pt; color: #64748b; font-weight: 500;")
        self.layout.addWidget(self.step_label)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #06b6d4;
                border-radius: 2px;
            }
        """)
        self.layout.addWidget(self.progress)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

    def set_progress(self, value: int, message: str):
        """Sets the progress bar value and updates the step text."""
        self.progress.setValue(value)
        self.step_label.setText(message)

def main():
    log.info("Starting ElectroVerse Application bootstrap...")

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("ElectroVerse")
    app.setApplicationVersion("1.0.0")

    # Load and apply theme from saved settings
    saved_theme = config_manager.get("theme")
    ThemeManager.apply_theme(app, saved_theme)

    # Show Splash Screen
    splash = ElectroVerseSplash()
    splash.show()
    
    # Smooth loading steps animation
    loading_steps = [
        (10, "Loading components..."),
        (25, "Initializing DSP core..."),
        (45, "Loading mathematical models..."),
        (70, "Preparing engineering workspace..."),
        (90, "Configuring toolkit modules..."),
        (100, "Starting laboratory environment...")
    ]
    
    current_val = 0
    for target_val, step_text in loading_steps:
        while current_val < target_val:
            current_val += 1
            splash.set_progress(current_val, step_text)
            # Sleep slightly to make loading animation visible
            time.sleep(0.008)
            app.processEvents()
            
    time.sleep(0.1) # Tiny wait for user satisfaction

    # Initialize and display Main Window
    window = MainWindow()
    window.show()
    
    # Hide splash
    splash.finish(window)

    log.info("MainWindow displayed. Running Qt event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
