"""
ElectroVerse Core Knowledge Base (ECKB) Data Loader
=====================================================
Unified data loader for 22 root datasets and 8 split learning content files in src/data/.
Acts as the single source of truth for Digital Logic Engine, Intelligent Wiring Assistant,
Component Library, Learning Mode, and Grand Viva.
"""

import os
import json
from typing import Dict, Any, Optional, List
from src.core.logger import log


class ECKBLoader:
    """Singleton data loader for ElectroVerse Core Knowledge Base."""
    
    _data_cache: Dict[str, Any] = {}
    _learning_cache: Dict[str, Any] = {}
    _initialized: bool = False

    @classmethod
    def get_data_dir(cls) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )

    @classmethod
    def initialize(cls):
        """Loads all ECKB datasets into memory cache."""
        if cls._initialized:
            return
            
        data_dir = cls.get_data_dir()
        if not os.path.exists(data_dir):
            log.error(f"[ECKBLoader] Data directory does not exist: {data_dir}")
            return
            
        # Root datasets
        root_files = [
            "ic_registry", "ic_pin_map", "logic_models", "logic_gates", "truth_tables",
            "components", "component_categories", "pin_diagrams", "connection_templates",
            "virtual_lab_steps", "experiments", "simulation_rules", "wiring_rules",
            "wire_styles", "breadboard_rules", "fault_cases", "diagnostics",
            "common_mistakes", "questions_bank", "example_circuits", "ic_examples",
            "component_links", "input_terminals", "output_terminals", "breadboard_grid", "canvas_components"
        ]
        
        for name in root_files:
            file_path = os.path.join(data_dir, f"{name}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        cls._data_cache[name] = json.load(fp)
                    log.info(f"[ECKBLoader] Loaded dataset '{name}.json'")
                except Exception as e:
                    log.error(f"[ECKBLoader] Failed to parse '{name}.json': {e}")
                    
        # Learning split datasets
        learning_dir = os.path.join(data_dir, "learning")
        if os.path.exists(learning_dir):
            for fname in os.listdir(learning_dir):
                if fname.endswith(".json"):
                    key = fname[:-5]
                    file_path = os.path.join(learning_dir, fname)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as fp:
                            cls._learning_cache[key] = json.load(fp)
                        log.info(f"[ECKBLoader] Loaded learning topic '{fname}'")
                    except Exception as e:
                        log.error(f"[ECKBLoader] Failed to parse learning topic '{fname}': {e}")
                        
        cls._initialized = True
        log.info(f"[ECKBLoader] Initialized ECKB with {len(cls._data_cache)} root datasets and {len(cls._learning_cache)} learning topics.")

    @classmethod
    def get_dataset(cls, name: str) -> Dict[str, Any]:
        """Returns a root dataset by name."""
        cls.initialize()
        return cls._data_cache.get(name, {})

    @classmethod
    def get_learning_topic(cls, topic: str) -> Dict[str, Any]:
        """Returns a split learning topic by name."""
        cls.initialize()
        return cls._learning_cache.get(topic, {})

    @classmethod
    def get_ic(cls, ic_number: str) -> Optional[Dict[str, Any]]:
        """Returns IC metadata from ic_registry."""
        registry = cls.get_dataset("ic_registry")
        records = registry.get("records", {})
        return records.get(str(ic_number)) or registry.get(str(ic_number))

    @classmethod
    def get_pin_map(cls, ic_number: str) -> Dict[str, str]:
        """Returns electrical pin map for an IC."""
        pin_map_data = cls.get_dataset("ic_pin_map")
        records = pin_map_data.get("records", {})
        return records.get(str(ic_number), {})

    @classmethod
    def get_simulation_rules(cls) -> Dict[str, Any]:
        """Returns engine simulation constraints."""
        rules = cls.get_dataset("simulation_rules")
        return rules.get("rules", {})

    @classmethod
    def get_connection_template(cls, ic_number: str) -> Dict[str, Any]:
        """Returns standard wiring template for an IC."""
        templates = cls.get_dataset("connection_templates")
        records = templates.get("records", {})
        return records.get(str(ic_number), {})

    @classmethod
    def get_fault_cases(cls) -> List[Dict[str, Any]]:
        """Returns troubleshooting fault scenarios."""
        faults = cls.get_dataset("fault_cases")
        return faults.get("records", [])

    @classmethod
    def get_example_circuit(cls, circuit_id: str) -> Dict[str, Any]:
        """Returns a preset demo circuit."""
        circuits = cls.get_dataset("example_circuits")
        records = circuits.get("records", {})
        return records.get(circuit_id, {})
