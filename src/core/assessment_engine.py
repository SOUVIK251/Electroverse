import os
import json
import random

from .timer_manager import TimerController
from .scoring_engine import ScoringEngine
from .analytics_engine import AnalyticsEngine
from .parametric_generator import ParametricGenerator
from .assessment_quality_engine import AssessmentQualityEngine

class AssessmentEngine:
    """Master CBT Examination Coordinator and Dataset Loader."""

    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.data_dir = os.path.join("src", "data", "assessment", subject_id)
        self.question_bank = self._load_json("question_bank.json").get("questions", [])
        self.exam_sets = self._load_json("exam_sets.json").get("exam_sets", [])
        self.q_map = {q.get("question_id") or q.get("id"): q for q in self.question_bank}
        
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

        set_q_ids = [str(qid) for qid in s_obj.get("question_ids", [])]
        target_count = 30

        # Filter set questions from question bank
        raw_set_qs = [q for q in self.question_bank if str(q.get("id")) in set_q_ids or str(q.get("question_id")) in set_q_ids]
        if not raw_set_qs:
            raw_set_qs = self.question_bank[:target_count]

        # Combine set questions with candidate pool to allow DuplicateDetector to replace raw duplicates seamlessly
        candidate_pool = raw_set_qs + [q for q in self.question_bank if q not in raw_set_qs]

        # Use Master Quality Engine for diverse sampling, stem polish, distractor enrichment, & option balancing
        diverse_qs = AssessmentQualityEngine.sample_diverse_exam(
            candidate_pool=candidate_pool,
            target_count=target_count,
            mode_id=mode.lower(),
            difficulty_filter="ALL"
        )

        is_valid, final_qs, quality_report = AssessmentQualityEngine.validate_and_finalize_exam(diverse_qs, target_count)

        return {
            "set_id": set_id,
            "set_title": s_obj.get("set_title", f"CBT Exam {set_id}"),
            "duration_sec": s_obj.get("duration_minutes", 30) * 60,
            "passing_percentage": s_obj.get("passing_percentage", 60.0),
            "total_questions": len(final_qs),
            "questions": final_qs,
            "quality_report": quality_report
        }
