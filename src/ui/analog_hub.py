from PySide6.QtWidgets import QWidget, QVBoxLayout
from src.core.logger import log
from src.ui.analog_hub.analog_hub_view import AnalogHubView

class AnalogElectronicsHubView(QWidget):
    """Unified master hub for Analog Electronics Hub delegating to AnalogHubView."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        log.info("Initializing AnalogElectronicsHubView standardized workspace")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.hub_view = AnalogHubView(main_window=main_window, parent=self)
        layout.addWidget(self.hub_view)
