import os
import sys

def get_resource_path(relative_path: str) -> str:
    """Gets the absolute path to a resource. Works for dev environment and PyInstaller build."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Standard local directory path
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.normpath(os.path.join(base_path, relative_path))
