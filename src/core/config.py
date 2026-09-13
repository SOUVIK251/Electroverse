import json
import os
from typing import Any, Dict
from src.core.logger import log

class ConfigManager:
    """Manages local settings storage for ElectroVerse in a JSON configuration file."""
    
    DEFAULT_CONFIG: Dict[str, Any] = {
        "theme": "dark",
        "font_size": 11,
        "animations_enabled": True,
        "recent_experiments": [],
        "show_formulas": True,
        "graph_line_width": 2,
        "ai_api_key": "",
        "ai_provider": "auto",
        "ai_enabled": True
    }

    def __init__(self):
        # Save in user's home directory under .electroverse
        self.config_dir = os.path.join(os.path.expanduser("~"), ".electroverse")
        self.config_path = os.path.join(self.config_dir, "settings.json")
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Loads configuration from the file. Fallback to default if load fails."""
        if not os.path.exists(self.config_path):
            log.info("No existing configuration found. Using default settings.")
            self.save()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge loaded keys to support updates in defaults
                for k, v in self.DEFAULT_CONFIG.items():
                    if k not in data:
                        data[k] = v
                self.config = data
                log.info(f"Configuration loaded successfully from {self.config_path}")
        except Exception as e:
            log.error(f"Error loading configuration: {e}. Reverting to defaults.")
            self.config = self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Saves current configuration to local settings file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            log.info("Configuration saved successfully.")
        except Exception as e:
            log.error(f"Error saving configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value."""
        return self.config.get(key, self.DEFAULT_CONFIG.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Updates a configuration value and saves to disk."""
        self.config[key] = value
        self.save()

# Global configuration instance
config_manager = ConfigManager()
