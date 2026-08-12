"""
ElectroVerse Central Navigation Architecture & Enum Routing Definitions.
Replaces all hardcoded integer page indices with explicit ViewID enums and handlers.
"""

from enum import Enum

class ViewID(Enum):
    DASHBOARD = "dashboard"
    LIBRARY = "library"
    ANALOG_HUB = "analog_hub"
    DIGITAL_HUB = "digital_hub"
    SIGNALS_HUB = "signals_hub"
    NETWORK_HUB = "network_hub"
    MPMC_HUB = "mpmc_hub"
    GRAND_VIVA = "grand_viva"
    SETTINGS = "settings"

class HubTabID(Enum):
    DASHBOARD = 0
    LEARN = 1
    PROBLEM_SOLVING = 2
    SIMULATION = 3
    ASSESSMENT = 4
    REFERENCE = 5
