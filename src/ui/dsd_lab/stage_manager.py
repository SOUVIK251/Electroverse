"""
Stage & Progress Manager for Digital System Design Lab
Manages per-experiment stage progression (Foundation -> Optimization -> Industrial Practice)
and tracking status (Not Started, In Progress, Completed, Mastered).
"""

from enum import Enum
from PySide6.QtCore import QObject, Signal

class StageLevel(Enum):
    FOUNDATION = "Foundation"
    OPTIMIZATION = "Optimization"
    INDUSTRIAL = "Industrial Practice"

class ExperimentStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    MASTERED = "Mastered"

class StageManager(QObject):
    stage_changed = Signal(str, str) # experiment_id, stage_name
    status_changed = Signal(str, str) # experiment_id, status_name
    
    def __init__(self):
        super().__init__()
        # experiment_id -> current StageLevel
        self.experiment_stages = {}
        # experiment_id -> current ExperimentStatus
        self.experiment_statuses = {}
        # experiment_id -> set of unlocked StageLevels
        self.unlocked_stages = {}

    def get_current_stage(self, exp_id: str) -> StageLevel:
        return self.experiment_stages.get(exp_id, StageLevel.FOUNDATION)

    def get_status(self, exp_id: str) -> ExperimentStatus:
        return self.experiment_statuses.get(exp_id, ExperimentStatus.NOT_STARTED)

    def is_stage_unlocked(self, exp_id: str, stage: StageLevel) -> bool:
        if stage == StageLevel.FOUNDATION:
            return True
        unlocked = self.unlocked_stages.get(exp_id, {StageLevel.FOUNDATION})
        return stage in unlocked

    def set_stage(self, exp_id: str, stage: StageLevel):
        if self.is_stage_unlocked(exp_id, stage):
            self.experiment_stages[exp_id] = stage
            if exp_id not in self.experiment_statuses or self.experiment_statuses[exp_id] == ExperimentStatus.NOT_STARTED:
                self.set_status(exp_id, ExperimentStatus.IN_PROGRESS)
            self.stage_changed.emit(exp_id, stage.value)

    def unlock_stage(self, exp_id: str, stage: StageLevel):
        if exp_id not in self.unlocked_stages:
            self.unlocked_stages[exp_id] = {StageLevel.FOUNDATION}
        self.unlocked_stages[exp_id].add(stage)

    def set_status(self, exp_id: str, status: ExperimentStatus):
        self.experiment_statuses[exp_id] = status
        self.status_changed.emit(exp_id, status.value)

    def complete_stage(self, exp_id: str, current_stage: StageLevel):
        if current_stage == StageLevel.FOUNDATION:
            self.unlock_stage(exp_id, StageLevel.OPTIMIZATION)
            self.set_status(exp_id, ExperimentStatus.IN_PROGRESS)
        elif current_stage == StageLevel.OPTIMIZATION:
            self.unlock_stage(exp_id, StageLevel.INDUSTRIAL)
            self.set_status(exp_id, ExperimentStatus.COMPLETED)
        elif current_stage == StageLevel.INDUSTRIAL:
            self.set_status(exp_id, ExperimentStatus.MASTERED)
