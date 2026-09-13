"""
ElectroVerse Knowledge Base Search Engine
Provides verified local search across ECKB, Theory Lessons, 8085 Assembly Databases,
Component Specs, Formula Cheat Sheets, and Viva Voce Banks.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from src.core.logger import log
from src.core.eckb_loader import ECKBLoader


class KnowledgeBase:
    """Offline Knowledge Base Search Engine for ElectroVerse verified engineering data."""

    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.theory_dir = os.path.join(self.base_dir, "data", "theory")
        self.program_db_dir = os.path.join(self.base_dir, "data", "ProgramDatabase", "8085")
        self.assessment_dir = os.path.join(self.base_dir, "data", "assessment")
        self.components_dir = os.path.join(self.base_dir, "data", "components")

        # Cache for quick lookup
        self._theory_cache: Dict[str, Dict[str, Any]] = {}
        self._program_cache: Dict[str, Dict[str, Any]] = {}
        self._load_theory_cache()
        self._load_program_cache()

    def _load_theory_cache(self):
        """Loads all theory JSON files into memory cache."""
        if not os.path.exists(self.theory_dir):
            return
        for root, _, files in os.walk(self.theory_dir):
            for file in files:
                if file.endswith(".json") and file != "learning_path.json":
                    fp = os.path.join(root, file)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "id" in data:
                                self._theory_cache[data["id"]] = data
                    except Exception as e:
                        log.debug(f"[KnowledgeBase] Could not cache {fp}: {e}")

    def _load_program_cache(self):
        """Loads all 8085 pre-built assembly program JSONs into memory cache."""
        if not os.path.exists(self.program_db_dir):
            return
        for root, _, files in os.walk(self.program_db_dir):
            for file in files:
                if file.endswith(".json"):
                    fp = os.path.join(root, file)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "title" in data:
                                self._program_cache[file] = data
                    except Exception as e:
                        log.debug(f"[KnowledgeBase] Could not cache program {fp}: {e}")

    def search_theory(self, query: str) -> List[Dict[str, Any]]:
        """Searches cached theory topics for matching keywords."""
        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
        if not query_words:
            return []

        results = []
        for topic_id, data in self._theory_cache.items():
            score = 0
            text_block = (
                data.get("title", "") + " " +
                data.get("summary", "") + " " +
                data.get("working_principle", "") + " " +
                " ".join(data.get("quick_notes", [])) + " " +
                data.get("boolean_equation", "")
            ).lower()

            for qw in query_words:
                if qw in text_block:
                    score += 1
                if qw in data.get("title", "").lower():
                    score += 3

            if score > 0:
                results.append((score, data))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:3]]

    def search_8085_instruction(self, mnemonic: str) -> Optional[Dict[str, Any]]:
        """Searches 8085 opcode database for a specific instruction mnemonic or opcode."""
        clean_m = mnemonic.strip().upper()
        # Search in ECKB logic models or custom 8085 dictionary
        opcodes_db = {
            "MOV": {"bytes": 1, "cycles": 4, "flags": "None", "desc": "Move register to register or memory.", "example": "MOV A, B (Copy B into Accumulator A)"},
            "MVI": {"bytes": 2, "cycles": 7, "flags": "None", "desc": "Move 8-bit immediate data to register or memory.", "example": "MVI A, 05H (Load 05H into A)"},
            "LXI": {"bytes": 3, "cycles": 10, "flags": "None", "desc": "Load 16-bit immediate data into register pair.", "example": "LXI H, 2000H (Load 2000H into HL pair)"},
            "LDA": {"bytes": 3, "cycles": 13, "flags": "None", "desc": "Load Accumulator directly from 16-bit memory address.", "example": "LDA 2050H"},
            "STA": {"bytes": 3, "cycles": 13, "flags": "None", "desc": "Store Accumulator contents directly into 16-bit memory address.", "example": "STA 2050H"},
            "ADD": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY, AC", "desc": "Add register or memory contents to Accumulator.", "example": "ADD B (A = A + B)"},
            "SUB": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY, AC", "desc": "Subtract register or memory contents from Accumulator.", "example": "SUB C (A = A - C)"},
            "ADI": {"bytes": 2, "cycles": 7, "flags": "Z, S, P, CY, AC", "desc": "Add 8-bit immediate data to Accumulator.", "example": "ADI 05H (A = A + 05H)"},
            "SUI": {"bytes": 2, "cycles": 7, "flags": "Z, S, P, CY, AC", "desc": "Subtract 8-bit immediate data from Accumulator.", "example": "SUI 02H (A = A - 02H)"},
            "INR": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, AC", "desc": "Increment register or memory contents by 1.", "example": "INR B (B = B + 1)"},
            "DCR": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, AC", "desc": "Decrement register or memory contents by 1.", "example": "DCR C (C = C - 1)"},
            "INX": {"bytes": 1, "cycles": 6, "flags": "None", "desc": "Increment 16-bit register pair by 1.", "example": "INX H (HL = HL + 1)"},
            "DCX": {"bytes": 1, "cycles": 6, "flags": "None", "desc": "Decrement 16-bit register pair by 1.", "example": "DCX H (HL = HL - 1)"},
            "DAD": {"bytes": 1, "cycles": 10, "flags": "CY", "desc": "Add 16-bit register pair contents to HL pair.", "example": "DAD B (HL = HL + BC). For example, HL=2000H and BC=1000H gives HL=3000H."},
            "ANA": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY=0, AC=1", "desc": "Logical AND register or memory with Accumulator.", "example": "ANA B (A = A AND B)"},
            "ORA": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY=0, AC=0", "desc": "Logical OR register or memory with Accumulator.", "example": "ORA C (A = A OR C)"},
            "XRA": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY=0, AC=0", "desc": "Logical XOR register or memory with Accumulator.", "example": "XRA A (Clears Accumulator A to 00H and sets Zero Flag Z=1)"},
            "CMA": {"bytes": 1, "cycles": 4, "flags": "None", "desc": "Complement Accumulator (1's complement of A).", "example": "CMA (Inverts all bits in Accumulator A)"},
            "CMP": {"bytes": 1, "cycles": 4, "flags": "Z, S, P, CY, AC", "desc": "Compare register/memory with Accumulator without modifying A.", "example": "CMP B (Sets Z=1 if A=B, CY=1 if A<B, CY=0 if A>B)"},
            "JMP": {"bytes": 3, "cycles": 10, "flags": "None", "desc": "Unconditional Jump to 16-bit address.", "example": "JMP 2000H"},
            "JZ":  {"bytes": 3, "cycles": "7/10", "flags": "None", "desc": "Jump if Zero flag Z = 1 (result of previous operation was 0).", "example": "JZ 2050H"},
            "JNZ": {"bytes": 3, "cycles": "7/10", "flags": "None", "desc": "Jump if Not Zero flag Z = 0.", "example": "JNZ 2020H"},
            "JC":  {"bytes": 3, "cycles": "7/10", "flags": "None", "desc": "Jump if Carry flag CY = 1.", "example": "JC 2080H"},
            "JNC": {"bytes": 3, "cycles": "7/10", "flags": "None", "desc": "Jump if No Carry flag CY = 0.", "example": "JNC 2030H"},
            "CALL": {"bytes": 3, "cycles": 18, "flags": "None", "desc": "Call subroutine at 16-bit address (pushes PC to stack).", "example": "CALL 3000H"},
            "RET":  {"bytes": 1, "cycles": 10, "flags": "None", "desc": "Return from subroutine (pops return address from stack into PC).", "example": "RET"},
            "PUSH": {"bytes": 1, "cycles": 12, "flags": "None", "desc": "Push 16-bit register pair onto stack.", "example": "PUSH B (Pushes BC onto stack)"},
            "POP":  {"bytes": 1, "cycles": 10, "flags": "All if PSW", "desc": "Pop 16-bit data from stack into register pair.", "example": "POP H (Pops stack into HL)"},
            "NOP":  {"bytes": 1, "cycles": 4, "flags": "None", "desc": "No Operation. Performs no action, consumes 4 T-states.", "example": "NOP"},
            "HLT":  {"bytes": 1, "cycles": 5, "flags": "None", "desc": "Halt execution. Stops CPU until interrupt or reset.", "example": "HLT"}
        }

        first_word = clean_m.split()[0] if clean_m else ""
        if first_word in opcodes_db:
            return opcodes_db[first_word]
        return None

    def search_program_db(self, query: str) -> Optional[Dict[str, Any]]:
        """Matches a user assembly program or query against pre-built 8085 programs."""
        q_clean = query.strip().lower()
        for filename, prog in self._program_cache.items():
            if prog.get("title", "").lower() in q_clean or filename.replace(".json", "") in q_clean:
                return prog
        return None

    def search_ic_registry(self, ic_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves TTL IC metadata from ECKB registry."""
        registry = ECKBLoader.get_dataset("ic_registry") or {}
        return registry.get(ic_key) or registry.get(f"IC_{ic_key}") or registry.get(ic_key.replace("IC_", ""))

    def search_component_db(self, name_query: str) -> Optional[Dict[str, Any]]:
        """Searches component database for electronic components (diodes, transistors, gates, etc.)."""
        clean_q = name_query.strip().lower()
        if not os.path.exists(self.components_dir):
            return None
        for file in os.listdir(self.components_dir):
            if file.endswith(".json"):
                fp = os.path.join(self.components_dir, file)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if clean_q in data.get("name", "").lower() or clean_q in data.get("id", "").lower():
                            return data
                except Exception:
                    pass
        return None


# Global KnowledgeBase Singleton
knowledge_base = KnowledgeBase()
