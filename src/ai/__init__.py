"""
ElectroVerse AI Tutor Package
Provides intelligent engineering tutor capabilities, local dataset knowledge search,
context awareness, exam safeguards, and asynchronous provider integration.
"""

from src.ai.knowledge_base import knowledge_base, KnowledgeBase
from src.ai.context_manager import context_manager, ContextManager
from src.ai.safety import safety_manager, SafetyManager
from src.ai.ai_provider import ProviderFactory, BaseAIProvider
from src.ai.tutor import electroverse_tutor, ElectroVerseTutor
from src.ai.tutor_panel import AITutorPanel

__all__ = [
    "knowledge_base",
    "KnowledgeBase",
    "context_manager",
    "ContextManager",
    "safety_manager",
    "SafetyManager",
    "ProviderFactory",
    "BaseAIProvider",
    "electroverse_tutor",
    "ElectroVerseTutor",
    "AITutorPanel",
]
