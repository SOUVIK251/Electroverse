"""
ElectroVerse Live Context Manager
Extracts and maintains real-time context from active Hub Views, 8085 Trainer Registers,
Breadboard Simulators, Component Library, and Assessment Status.
"""

from typing import Dict, Any, Optional
from src.core.logger import log


class ContextManager:
    """Centralized Live Context Tracking Engine for ElectroVerse AI Tutor."""

    def __init__(self):
        self.current_hub: str = "Dashboard"
        self.current_view_id: str = "dashboard"
        self.active_tab: str = "Learn"
        self.current_topic_title: str = "Overview"
        self.current_topic_data: Dict[str, Any] = {}

        # 8085 Trainer Live State
        self.cpu_8085_state: Dict[str, Any] = {
            "A": "00H", "B": "00H", "C": "00H", "D": "00H",
            "E": "00H", "H": "00H", "L": "00H", "PC": "2000H", "SP": "27FFH",
            "FLAGS": {"S": 0, "Z": 0, "AC": 0, "P": 0, "CY": 0},
            "current_instruction": "NOP",
            "program_code": ""
        }

        # Breadboard / DSD Simulation Live State
        self.dsd_state: Dict[str, Any] = {
            "active_ic": "74266",
            "inputs": {"IN_A": 0, "IN_B": 0},
            "outputs": {"OUT_Y0": 0, "OUT_Y1": 0, "OUT_Y2": 0, "OUT_Y3": 0},
            "wire_count": 0
        }

        # Component Library Live State
        self.active_component: Dict[str, Any] = {
            "name": "Zener Diode",
            "type": "Diode",
            "description": "Voltage regulator diode"
        }

        # CBT Assessment Live State
        self.assessment_state: Dict[str, Any] = {
            "is_graded_exam_active": False,
            "exam_name": "",
            "active_question_id": "",
            "active_question_text": ""
        }

    def set_active_hub(self, hub_name: str, view_id: str = ""):
        self.current_hub = hub_name
        if view_id:
            self.current_view_id = view_id
        log.debug(f"[ContextManager] Active hub set to: {self.current_hub}")

    def update_topic_context(self, topic_title: str, topic_data: Optional[Dict[str, Any]] = None):
        self.current_topic_title = topic_title
        if topic_data:
            self.current_topic_data = topic_data

    def update_8085_state(self, registers: Dict[str, str], flags: Dict[str, int], pc: str = "2000H", sp: str = "27FFH", inst: str = "NOP", code: str = ""):
        self.cpu_8085_state["A"] = registers.get("A", "00H")
        self.cpu_8085_state["B"] = registers.get("B", "00H")
        self.cpu_8085_state["C"] = registers.get("C", "00H")
        self.cpu_8085_state["D"] = registers.get("D", "00H")
        self.cpu_8085_state["E"] = registers.get("E", "00H")
        self.cpu_8085_state["H"] = registers.get("H", "00H")
        self.cpu_8085_state["L"] = registers.get("L", "00H")
        self.cpu_8085_state["PC"] = pc
        self.cpu_8085_state["SP"] = sp
        self.cpu_8085_state["FLAGS"] = flags
        self.cpu_8085_state["current_instruction"] = inst
        if code:
            self.cpu_8085_state["program_code"] = code

    def update_dsd_state(self, ic_key: str, inputs: Dict[str, int], outputs: Dict[str, int], wire_count: int = 0):
        self.dsd_state["active_ic"] = ic_key
        self.dsd_state["inputs"] = inputs
        self.dsd_state["outputs"] = outputs
        self.dsd_state["wire_count"] = wire_count

    def update_component_context(self, component_name: str, comp_data: Dict[str, Any]):
        self.active_component = {"name": component_name, "data": comp_data}

    def update_assessment_context(self, is_active: bool, exam_name: str = "", q_id: str = "", q_text: str = ""):
        self.assessment_state["is_graded_exam_active"] = is_active
        self.assessment_state["exam_name"] = exam_name
        self.assessment_state["active_question_id"] = q_id
        self.assessment_state["active_question_text"] = q_text

    def get_summary_context(self) -> Dict[str, Any]:
        """Returns a snapshot of current system context for prompt engineering."""
        summary = {
            "current_hub": self.current_hub,
            "active_tab": self.active_tab,
            "topic_title": self.current_topic_title,
        }

        if "microprocessor" in self.current_hub.lower() or "8085" in self.current_hub.lower():
            b_val = self.cpu_8085_state["B"].replace("H", "")
            c_val = self.cpu_8085_state["C"].replace("H", "")
            d_val = self.cpu_8085_state["D"].replace("H", "")
            e_val = self.cpu_8085_state["E"].replace("H", "")
            h_val = self.cpu_8085_state["H"].replace("H", "")
            l_val = self.cpu_8085_state["L"].replace("H", "")
            summary["8085_registers"] = {
                "A": self.cpu_8085_state["A"],
                "BC": f"{b_val}{c_val}H",
                "DE": f"{d_val}{e_val}H",
                "HL": f"{h_val}{l_val}H",
                "PC": self.cpu_8085_state["PC"],
                "SP": self.cpu_8085_state["SP"],
                "FLAGS": self.cpu_8085_state["FLAGS"]
            }
            summary["8085_current_instruction"] = self.cpu_8085_state["current_instruction"]

        if "digital" in self.current_hub.lower() or "breadboard" in self.current_hub.lower():
            summary["dsd_simulator"] = self.dsd_state

        if "component" in self.current_hub.lower():
            summary["component"] = self.active_component

        if self.assessment_state["is_graded_exam_active"]:
            summary["cbt_exam_graded_mode"] = True
            summary["exam_name"] = self.assessment_state["exam_name"]

        return summary


# Global Singleton
context_manager = ContextManager()
