from PySide6.QtCore import QObject, QTimer, Signal

class TimerController(QObject):
    """30-Minute CBT Countdown Timer with 5m/1m warnings and auto-submit."""
    
    tick = Signal(int)             # Emits remaining seconds
    warning_5min = Signal()         # Emits when <= 300s
    warning_1min = Signal()         # Emits when <= 60s
    time_expired = Signal()         # Emits when 0s (Auto-submit)

    def __init__(self, duration_sec=1800, parent=None):
        super().__init__(parent)
        self.total_duration = duration_sec
        self.remaining_sec = duration_sec
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.warned_5m = False
        self.warned_1m = False

    def start(self):
        self.timer.start(1000)

    def stop(self):
        self.timer.stop()

    def reset(self, duration_sec=None):
        self.timer.stop()
        if duration_sec is not None:
            self.total_duration = duration_sec
        self.remaining_sec = self.total_duration
        self.warned_5m = False
        self.warned_1m = False
        self.tick.emit(self.remaining_sec)

    def _on_tick(self):
        if self.remaining_sec > 0:
            self.remaining_sec -= 1
            self.tick.emit(self.remaining_sec)

            if self.remaining_sec <= 300 and not self.warned_5m:
                self.warned_5m = True
                self.warning_5min.emit()

            if self.remaining_sec <= 60 and not self.warned_1m:
                self.warned_1m = True
                self.warning_1min.emit()

        if self.remaining_sec <= 0:
            self.timer.stop()
            self.time_expired.emit()

    def get_time_string(self):
        mins = self.remaining_sec // 60
        secs = self.remaining_sec % 60
        return f"{mins:02d}:{secs:02d}"
