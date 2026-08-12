"""
ElectroVerse Microprocessor & Microcontroller Interactive Simulation View
Hosts the Virtual 8085 Trainer Kit and provides Opcode Reference inspection.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from src.core.logger import log
from .trainer_8085_widget import Virtual8085TrainerWidget
from src.ui.components.opcode_viewer_dialog import OpcodeViewerDialog


class MPMCSimulationView(QWidget):
    """Interactive Simulation Lab — hosts Virtual 8085 Trainer."""

    def __init__(self, hub_view=None, parent=None):
        super().__init__(parent)
        self.hub_view = hub_view
        log.info("Initializing MPMCSimulationView")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header / title bar
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { background-color: #0F172A; border: 1px solid #1E293B;"
            " border-radius: 8px; padding: 6px 14px; }"
        )
        h_lay = QHBoxLayout(hdr)
        h_lay.setContentsMargins(0, 0, 0, 0)
        h_lay.setSpacing(10)

        title = QLabel("🔬  INTERACTIVE SIMULATION LABORATORY")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #3B82F6;")
        h_lay.addWidget(title)
        h_lay.addStretch()

        # Static label instead of dropdown (Requirement 1)
        sim_hdr_lbl = QLabel("Simulation: ")
        sim_hdr_lbl.setStyleSheet("color: #94A3B8; font-size: 9.5pt;")
        h_lay.addWidget(sim_hdr_lbl)

        self._sim_title_lbl = QLabel("Virtual 8085 Microprocessor Trainer Kit")
        self._sim_title_lbl.setStyleSheet(
            "QLabel { background-color: #1E293B; color: #F8FAFC;"
            " border: 1px solid #3B82F6; border-radius: 6px; padding: 5px 12px;"
            " font-weight: bold; font-size: 9.5pt; }"
        )
        h_lay.addWidget(self._sim_title_lbl)

        # Perfect Circular Info "i" Button
        self._info_btn = QPushButton("i")
        self._info_btn.setFixedSize(26, 26)
        self._info_btn.setToolTip("8085 Opcode Reference")
        self._info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._info_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #10B981;
                border: 2px solid #10B981;
                border-radius: 13px;
                font-family: Arial, sans-serif;
                font-size: 12pt;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #FFFFFF;
                border-color: #10B981;
            }
        """)
        self._info_btn.clicked.connect(self._open_opcode_reference)
        h_lay.addWidget(self._info_btn)

        layout.addWidget(hdr)

        # Canvas area
        self._canvas = QFrame()
        self._canvas.setStyleSheet(
            "QFrame { background-color: #0B1020; border: 1px solid #1E293B;"
            " border-radius: 8px; }"
        )
        self._canvas_lay = QVBoxLayout(self._canvas)
        self._canvas_lay.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._canvas, 1)

        # Instantiate Virtual 8085 Trainer Kit
        self.trainer = Virtual8085TrainerWidget(self)
        self._canvas_lay.addWidget(self.trainer)

    def _open_opcode_reference(self):
        """Open the local Intel 8085 Opcode Reference chart modal viewer."""
        import traceback
        from PySide6.QtWidgets import QMessageBox
        try:
            print("INFO button clicked")
            from src.ui.components.opcode_viewer_dialog import OpcodeViewerDialog
            dlg = OpcodeViewerDialog(self)
            print("Dialog created")

            img_path = dlg._resolve_image_path()
            print(f"Image path: {img_path}")

            exists = img_path.exists() if (img_path and hasattr(img_path, 'exists')) else False
            print(f"Image exists: {exists}")

            if hasattr(dlg, 'pixmap_item') and dlg.pixmap_item and not dlg.pixmap_item.pixmap().isNull():
                pm = dlg.pixmap_item.pixmap()
                print(f"Pixmap loaded: {pm.width()}x{pm.height()} px")
            else:
                print("Pixmap loaded: False")

            print("Dialog shown")
            dlg.exec()
        except Exception as e:
            print(f"ERROR in _open_opcode_reference: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error Opening Opcode Reference",
                f"Failed to open Intel 8085 Opcode Reference dialog:\n\n{e}\n\n{traceback.format_exc()}"
            )
