"""
ElectroVerse AI Tutor Safety & Exam Safeguard Manager
Protects academic integrity during live CBT exams and prevents hallucinations in offline mode.
"""

import re
from typing import Dict, Any, Tuple, Optional


class SafetyManager:
    """Safety & Exam Integrity Guard for ElectroVerse AI Tutor."""

    EXAM_DIRECT_ANSWER_PATTERNS = [
        r"what is the answer",
        r"give me the answer",
        r"tell me the answer",
        r"solve this question for me",
        r"which option is correct",
        r"is option [a-d] correct",
        r"select option",
        r"answer key"
    ]

    UNVERIFIED_OFFLINE_MESSAGE = (
        "I don't have enough verified information in the ElectroVerse knowledge base to answer this reliably."
    )

    @classmethod
    def is_exam_answer_requested(cls, query: str) -> bool:
        q_lower = query.lower()
        for pat in cls.EXAM_DIRECT_ANSWER_PATTERNS:
            if re.search(pat, q_lower):
                return True
        return False

    @classmethod
    def apply_assessment_guard(cls, query: str, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """If graded assessment is active, blocks direct answer keys and returns learning guidance."""
        if context.get("cbt_exam_graded_mode", False):
            if cls.is_exam_answer_requested(query):
                guard_msg = (
                    "🔒 **Live Graded Assessment Active**\n\n"
                    "I cannot provide the direct answer key to an active exam question during a graded test.\n\n"
                    "**Learning Guidance:**\n"
                    "- Review the governing formulas and definitions in the **📖 Learn** tab.\n"
                    "- Break down the question into given variables and required engineering parameters.\n"
                    "- Check your units and sign conventions carefully!"
                )
                return True, guard_msg
        return False, None

    @classmethod
    def format_hallucination_fallback(cls) -> str:
        return cls.UNVERIFIED_OFFLINE_MESSAGE


# Singleton
safety_manager = SafetyManager()
