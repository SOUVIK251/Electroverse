import os
import json
import random

from .timer_manager import TimerController
from .scoring_engine import ScoringEngine
from .analytics_engine import AnalyticsEngine
from .parametric_generator import ParametricGenerator

class AssessmentEngine:
    """Master CBT Examination Coordinator and Dataset Loader."""

    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.data_dir = os.path.join("src", "data", "assessment", subject_id)
        self.question_bank = self._load_json("question_bank.json").get("questions", [])
        self.exam_sets = self._load_json("exam_sets.json").get("exam_sets", [])
        self.q_map = {q["question_id"]: q for q in self.question_bank}
        
        self.parametric_gen = ParametricGenerator()

    def _load_json(self, file_name):
        p = os.path.join(self.data_dir, file_name)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_exam_sets(self):
        return self.exam_sets

    def prepare_exam_session(self, set_id, mode="Mixed"):
        # Find exam set
        s_obj = next((s for s in self.exam_sets if s["set_id"] == set_id), None)
        if not s_obj:
            s_obj = self.exam_sets[0] if self.exam_sets else {}

        q_ids = s_obj.get("question_ids", [])
        raw_qs = [self.q_map[qid] for qid in q_ids if qid in self.q_map]

        if mode == "Easy":
            raw_qs = [q for q in self.question_bank if q["difficulty"] == "Easy"][:30]
        elif mode == "Medium":
            raw_qs = [q for q in self.question_bank if q["difficulty"] == "Medium"][:30]
        elif mode == "Hard":
            raw_qs = [q for q in self.question_bank if q["difficulty"] == "Hard"][:30]

        # Apply parametric instantiation and shuffling
        session_qs = []
        for q in raw_qs:
            q_inst = self.parametric_gen.instantiate_question(q)
            session_qs.append(q_inst)

        random.seed()
        random.shuffle(session_qs)

        return {
            "set_id": set_id,
            "set_title": s_obj.get("set_title", f"CBT Exam {set_id}"),
            "duration_sec": s_obj.get("duration_minutes", 30) * 60,
            "passing_percentage": s_obj.get("passing_percentage", 60.0),
            "questions": session_qs
        }
