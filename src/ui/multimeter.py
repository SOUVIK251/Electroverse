from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from src.core.logger import log

class MultimeterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing MultimeterView")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        card = QFrame()
        card.setObjectName("card-panel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("⭐ Virtual Multimeter")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #06b6d4;")
        
        desc = QLabel("Interactive Digital Multimeter showing voltage, current, and resistance will be implemented here in Phase 7.")
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11pt; color: #94a3b8; margin-top: 10px;")
        
        card_layout.addWidget(title)
        card_layout.addWidget(desc)
        card_layout.addStretch()
        
        layout.addWidget(card)
