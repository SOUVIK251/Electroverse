"""
ElectroVerse Standardized Professional Engineering SpinBox Components
Provides MATLAB / LabVIEW / Multisim style numeric controls with mouse wheeling,
PageUp/PageDown 10x steps, Escape-restore, smooth acceleration, and real-time sync.
"""

from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QWheelEvent, QKeyEvent


from src.core.logger import log


class EngineeringDoubleSpinBox(QDoubleSpinBox):
    """Professional Engineering Double SpinBox with Mouse Wheel & Key Acceleration."""

    value_applied = Signal(float)

    def __init__(self, parent=None, unit: str = "", step: float = 1.0, min_val: float = 0.0, max_val: float = 1e6, decimals: int = 2):
        super().__init__(parent)
        self._previous_value = min_val
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRange(min_val, max_val)
        self.setSingleStep(step)
        self.setDecimals(decimals)
        if unit:
            self.setSuffix(f" {unit}")
        
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1E293B;
                color: #FFFFFF;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                font-family: Consolas, monospace;
            }
            QDoubleSpinBox:focus {
                border-color: #06B6D4;
                background-color: #0F172A;
            }
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #334155;
                background-color: #1E293B;
                border-top-right-radius: 4px;
            }
            QDoubleSpinBox::up-button:hover {
                background-color: #0284C7;
            }
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
                border-left: 1px solid #334155;
                background-color: #1E293B;
                border-bottom-right-radius: 4px;
            }
            QDoubleSpinBox::down-button:hover {
                background-color: #0284C7;
            }
        """)

        self.valueChanged.connect(self._handle_value_change)

    def _handle_value_change(self, val: float):
        log.debug(f"[SpinBox Update] Value changed: {val}")
        self.value_applied.emit(val)

    def safe_set_value(self, val: float):
        """Sets value without triggering circular signal loops."""
        self.blockSignals(True)
        self.setValue(val)
        self.blockSignals(False)


    def wheelEvent(self, event: QWheelEvent):
        """Mouse Wheel Up = Increment, Mouse Wheel Down = Decrement."""
        if event.angleDelta().y() > 0:
            self.stepUp()
        else:
            self.stepDown()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """PageUp = 10x Step, PageDown = -10x Step, Enter = Apply, Escape = Restore."""
        key = event.key()
        if key == Qt.Key.Key_PageUp:
            self.setValue(self.value() + (10.0 * self.singleStep()))
            event.accept()
        elif key == Qt.Key.Key_PageDown:
            self.setValue(self.value() - (10.0 * self.singleStep()))
            event.accept()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._previous_value = self.value()
            self.clearFocus()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            self.setValue(self._previous_value)
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self._previous_value = self.value()
        super().focusInEvent(event)


class EngineeringSpinBox(QSpinBox):
    """Professional Engineering Integer SpinBox with Mouse Wheel & Key Acceleration."""

    value_applied = Signal(int)

    def __init__(self, parent=None, unit: str = "", step: int = 1, min_val: int = 0, max_val: int = 10000):
        super().__init__(parent)
        self._previous_value = min_val
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRange(min_val, max_val)
        self.setSingleStep(step)
        if unit:
            self.setSuffix(f" {unit}")

        self.setStyleSheet("""
            QSpinBox {
                background-color: #1E293B;
                color: #FFFFFF;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                font-family: Consolas, monospace;
            }
            QSpinBox:focus {
                border-color: #06B6D4;
                background-color: #0F172A;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #334155;
                background-color: #1E293B;
                border-top-right-radius: 4px;
            }
            QSpinBox::up-button:hover {
                background-color: #0284C7;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
                border-left: 1px solid #334155;
                background-color: #1E293B;
                border-bottom-right-radius: 4px;
            }
            QSpinBox::down-button:hover {
                background-color: #0284C7;
            }
        """)

        self.valueChanged.connect(self._handle_value_change)

    def _handle_value_change(self, val: int):
        log.debug(f"[SpinBox Update] Value changed: {val}")
        self.value_applied.emit(val)

    def safe_set_value(self, val: int):
        """Sets value without triggering circular signal loops."""
        self.blockSignals(True)
        self.setValue(val)
        self.blockSignals(False)


    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.stepUp()
        else:
            self.stepDown()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_PageUp:
            self.setValue(self.value() + (10 * self.singleStep()))
            event.accept()
        elif key == Qt.Key.Key_PageDown:
            self.setValue(self.value() - (10 * self.singleStep()))
            event.accept()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._previous_value = self.value()
            self.clearFocus()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            self.setValue(self._previous_value)
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self._previous_value = self.value()
        super().focusInEvent(event)
