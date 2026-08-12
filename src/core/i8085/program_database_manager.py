"""
i8085.program_database_manager — Educational 8085 Program Knowledge Base & Smart Recognition Engine
===================================================================================================
Manages a modular JSON-based 8085 Program Database. Automatically discovers,
indexes, normalizes, and matches 8085 programs from JSON files with detailed signature diff debugging.
"""

from __future__ import annotations
import os
import json
import glob
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def normalize_signature(raw: Any) -> str:
    """
    Normalize raw hex input (string, list, or bytes) into a clean, uppercase, continuous hex string.
    Removes spaces, commas, newlines, tabs, 0x prefixes, and trailing H suffixes.
    """
    if isinstance(raw, list):
        clean_items = []
        for b in raw:
            s = str(b).upper().strip()
            s = re.sub(r'[^0-9A-F]', '', s)
            if s:
                clean_items.append(s.zfill(2))
        return "".join(clean_items)
    elif isinstance(raw, str):
        s = raw.upper()
        s = re.sub(r'0X|H|\s|,|\n|\r|\t', '', s)
        return re.sub(r'[^0-9A-F]', '', s)
    elif isinstance(raw, (bytes, bytearray)):
        return "".join(f"{b:02X}" for b in raw)
    return ""


class ProgramDatabaseManager:
    """
    Singleton / Central Manager for the 8085 Program Database.

    Discovers all JSON files in ProgramDatabase directories, loads program metadata,
    and performs Smart Program Recognition against normalized hex signatures with character-by-character diffs.
    """

    _instance: Optional[ProgramDatabaseManager] = None

    def __new__(cls, db_dirs: Optional[List[str]] = None) -> ProgramDatabaseManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_dirs: Optional[List[str]] = None):
        if self._initialized:
            return

        self._programs: Dict[str, Dict[str, Any]] = {}          # id -> program_dict
        self._categories: Dict[str, List[Dict[str, Any]]] = {}   # category_name -> list of programs
        self._signature_index: List[Tuple[str, Dict[str, Any]]] = []  # (normalized_sig, program_dict)
        self._total_json_files = 0

        # Default search directories
        base_dir = Path(__file__).resolve().parent.parent.parent  # src/
        root_dir = base_dir.parent                                 # repo root

        self.db_dirs = [
            str(base_dir / "data" / "ProgramDatabase"),
            str(root_dir / "ProgramDatabase"),
            str(base_dir / "data" / "mpmc" / "programs"),
        ]
        if db_dirs:
            self.db_dirs.extend(db_dirs)

        self.reload_database()
        self._initialized = True

    def reload_database(self) -> int:
        """Scan all registered directories and load all .json program profiles."""
        self._programs.clear()
        self._categories.clear()
        self._signature_index.clear()
        self._total_json_files = 0

        loaded_count = 0
        for db_dir in self.db_dirs:
            if not os.path.exists(db_dir):
                continue

            json_files = glob.glob(os.path.join(db_dir, "**", "*.json"), recursive=True)
            self._total_json_files += len(json_files)

            for json_path in json_files:
                try:
                    with open(json_path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)

                    prog_id = data.get("id") or Path(json_path).stem
                    data["id"] = prog_id
                    data["file_path"] = json_path

                    category = data.get("category", "General")
                    data["category"] = category

                    self._programs[prog_id] = data

                    if category not in self._categories:
                        self._categories[category] = []
                    self._categories[category].append(data)

                    # Build normalized signature
                    hex_code = data.get("machine_code_hex", [])
                    norm_sig = normalize_signature(hex_code)
                    data["normalized_signature"] = norm_sig

                    if norm_sig:
                        self._signature_index.append((norm_sig, data))

                    loaded_count += 1
                except Exception as e:
                    print(f"[ProgramDatabaseManager] Error loading {json_path}: {e}")

        # Startup Console Print
        print("=" * 75)
        print("PROGRAM DATABASE ENGINE INITIALIZATION")
        print(f"Total JSON Files Discovered: {self._total_json_files}")
        print(f"Total Programs Loaded: {loaded_count}")
        print("Loaded Program Samples:")
        sample_keys = list(self._programs.keys())[:15]
        for k in sample_keys:
            p = self._programs[k]
            print(f" - [{p['id']}] {p.get('program_name')} | Sig: {p.get('normalized_signature')}")
        if len(self._programs) > 15:
            print(f" ... and {len(self._programs) - 15} more programs.")
        print("=" * 75)

        return loaded_count

    def get_all_programs(self) -> List[Dict[str, Any]]:
        """Return list of all loaded program dicts."""
        return list(self._programs.values())

    def get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return category name -> list of program dicts."""
        return self._categories

    def get_program_by_id(self, prog_id: str) -> Optional[Dict[str, Any]]:
        """Fetch program by string ID."""
        return self._programs.get(prog_id)

    def search_programs(self, query: str) -> List[Dict[str, Any]]:
        """Search programs by name, category, objective, or assembly code."""
        q = query.lower().strip()
        if not q:
            return self.get_all_programs()

        results = []
        for prog in self._programs.values():
            if (q in prog.get("program_name", "").lower() or
                q in prog.get("category", "").lower() or
                q in prog.get("objective", "").lower() or
                q in prog.get("assembly_code", "").lower()):
                results.append(prog)
        return results

    def recognize_program(self, hex_bytes: List[str] | List[int] | str) -> Optional[Dict[str, Any]]:
        """
        Smart Program Recognition:
        Converts input bytes to normalized signature string and compares against stored signatures.
        """
        if not hex_bytes:
            return None

        gen_sig = normalize_signature(hex_bytes)

        # If generated signature contains HLT (76), trim trailing bytes after 76
        if "76" in gen_sig:
            hlt_idx = gen_sig.find("76")
            gen_sig = gen_sig[:hlt_idx + 2]

        for stored_sig, prog_data in self._signature_index:
            if gen_sig == stored_sig:
                return prog_data

        return None

    def debug_recognition(self, hex_bytes: List[str] | List[int] | str) -> Dict[str, Any]:
        """
        Detailed Recognition Debugger:
        Normalizes input signature, searches for exact or closest candidate, and produces
        a character-by-character comparison diff report.
        """
        gen_sig = normalize_signature(hex_bytes)
        if "76" in gen_sig:
            hlt_idx = gen_sig.find("76")
            gen_sig = gen_sig[:hlt_idx + 2]

        matched = None
        closest_prog = None
        closest_score = -1
        closest_diff = ""

        for stored_sig, prog_data in self._signature_index:
            if gen_sig == stored_sig:
                matched = prog_data
                break

            # Calculate similarity score (common prefix length / ratio)
            score = self._common_prefix_length(gen_sig, stored_sig)
            if score > closest_score:
                closest_score = score
                closest_prog = prog_data

        if matched:
            return {
                "matched": True,
                "program": matched,
                "generated_signature": gen_sig,
                "json_signature": matched.get("normalized_signature"),
                "diff_report": "MATCH PERFECT! Signatures match 100% character-by-character."
            }

        # Character-by-character diff against closest candidate
        diff_lines = []
        if closest_prog:
            json_sig = closest_prog.get("normalized_signature", "")
            diff_lines.append(f"Generated Signature: {gen_sig}")
            diff_lines.append(f"JSON Signature     : {json_sig}")
            diff_lines.append("Diff Pointer       : " + self._build_diff_pointer(gen_sig, json_sig))
            reason = f"Mismatch at index {self._first_mismatch_index(gen_sig, json_sig)}. Closest candidate: '{closest_prog.get('program_name')}'"
        else:
            reason = "No stored signatures in database to compare against."

        return {
            "matched": False,
            "program": None,
            "closest_candidate": closest_prog,
            "generated_signature": gen_sig,
            "json_signature": closest_prog.get("normalized_signature") if closest_prog else "",
            "diff_report": "\n".join(diff_lines),
            "reason": reason
        }

    def _common_prefix_length(self, s1: str, s2: str) -> int:
        count = 0
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                count += 1
            else:
                break
        return count

    def _first_mismatch_index(self, s1: str, s2: str) -> int:
        for i, (c1, c2) in enumerate(zip(s1, s2)):
            if c1 != c2:
                return i
        return min(len(s1), len(s2))

    def _build_diff_pointer(self, s1: str, s2: str) -> str:
        pointer = []
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                pointer.append(" ")
            else:
                pointer.append("^")
        if len(s1) != len(s2):
            pointer.append("^ (Length mismatch)")
        return "".join(pointer)
