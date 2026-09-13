"""
ElectroVerse AI Tutor Controller
Main orchestrator for engineering tutoring, viva examinations, problem solving explanations,
and 8085 program debugging.
"""

from typing import Dict, Any, Tuple
from src.core.logger import log
from src.ai.context_manager import context_manager
from src.ai.safety import safety_manager
from src.ai.ai_provider import ProviderFactory


class ElectroVerseTutor:
    """Master AI Tutor Controller for ElectroVerse."""

    SYSTEM_PROMPT = """You are ElectroVerse AI Tutor, an engineering mentor and assistant built directly into the ElectroVerse Virtual Engineering Laboratory.
Subtitle: "Understand engineering, don't just memorize it."

YOUR MISSION:
Help engineering students deeply understand concepts, formulas, circuit behaviors, component specifications, digital logic, signals & systems, network theory, microprocessors (8085, 8086), microcontrollers (8051), assembly programs, and laboratory experiments.

RULES & CONSTRAINTS:
1. EXPLAIN concepts at an engineering-student level. Use clear language first, then introduce rigorous engineering terminology.
2. ALWAYS prioritize verified ElectroVerse project knowledge, local datasets, IC pinouts, component specs, and 8085 opcodes.
3. NEVER invent or hallucinate opcodes, machine cycles, flag effects, component specs, or circuit behaviors.
4. When explaining 8085 instructions, state the instruction mnemonic, byte count, machine cycles, flag effects, and a simple 16-bit register worked example (e.g. DAD B adds BC to HL; if HL=2000H and BC=1000H, HL becomes 3000H).
5. When explaining circuits or simulations, reference the actual live values provided in the live context (e.g. A=00H, VCC=5V, logic states).
6. Be concise, structured, and use Markdown formatting with equations, bold headers, and bullet points.
"""

    def __init__(self):
        pass

    def ask(self, query: str, mode: str = "Tutor", extra_context: Dict[str, Any] = None) -> str:
        """Processes a student query with live context, exam safeguards, and provider resolution."""
        log.info(f"[ElectroVerseTutor] Processing query (Mode: {mode}): {query}")

        # 1. Get Live Context Snapshot
        ctx = context_manager.get_summary_context()
        if extra_context:
            ctx.update(extra_context)

        # 2. Check CBT Graded Assessment Safeguard
        is_blocked, guard_msg = safety_manager.apply_assessment_guard(query, ctx)
        if is_blocked:
            return guard_msg

        # 3. Construct Mode-Specific Prompt
        mode_prefix = ""
        if mode == "Viva Examiner":
            mode_prefix = "MODE: Viva Examiner ('Viva Me'). Evaluate the student's answer or ask a challenging, curriculum-aligned oral viva question on the current topic.\n"
        elif mode == "Problem Solver":
            mode_prefix = "MODE: Problem Solver. Provide a step-by-step breakdown (Given Values -> Governing Formula -> Substitution -> Calculation -> Final Answer -> Engineering Interpretation).\n"
        elif mode == "Debug Assistant":
            mode_prefix = "MODE: 8085 Assembly Debug Assistant. Analyze the current 8085 program/registers, identify logical bugs, explain flag changes, and show corrected assembly code.\n"

        prompt = f"{mode_prefix}{query}"

        # 4. Resolve Provider & Generate Response
        provider = ProviderFactory.get_provider()
        response = provider.generate_response(prompt, ctx, self.SYSTEM_PROMPT)
        return response


# Global Singleton
electroverse_tutor = ElectroVerseTutor()
