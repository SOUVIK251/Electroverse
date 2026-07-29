"""
Event Bus System (Decoupled Module Communication)
===================================================
Provides a lightweight Publish/Subscribe event system for communication
between DigitalLogicEngine, breadboard canvas, UI components, and diagnostic tools.
"""

from typing import Callable, Dict, List
from src.core.logger import log


class EventChannels:
    WIRE_CONNECTED = "WIRE_CONNECTED"
    WIRE_REMOVED = "WIRE_REMOVED"
    COMPONENT_PLACED = "COMPONENT_PLACED"
    COMPONENT_DELETED = "COMPONENT_DELETED"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_STOPPED = "SIMULATION_STOPPED"
    POWER_CHANGED = "POWER_CHANGED"
    SWITCH_TOGGLED = "SWITCH_TOGGLED"
    CLOCK_PULSE = "CLOCK_PULSE"
    LOGIC_UPDATED = "LOGIC_UPDATED"
    ERROR_DETECTED = "ERROR_DETECTED"


class EventBus:
    """Central Publish/Subscribe Event Bus singleton."""
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, channel: str, callback: Callable):
        """Subscribes a callback listener function to an event channel."""
        if channel not in cls._subscribers:
            cls._subscribers[channel] = []
        if callback not in cls._subscribers[channel]:
            cls._subscribers[channel].append(callback)
            log.info(f"[EventBus] Subscribed callback to channel: {channel}")

    @classmethod
    def unsubscribe(cls, channel: str, callback: Callable):
        """Unsubscribes a callback listener function from an event channel."""
        if channel in cls._subscribers and callback in cls._subscribers[channel]:
            cls._subscribers[channel].remove(callback)

    @classmethod
    def publish(cls, channel: str, **kwargs):
        """Publishes an event payload to all subscribed listeners."""
        if channel in cls._subscribers:
            for callback in cls._subscribers[channel]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    log.error(f"[EventBus] Error dispatching event '{channel}': {e}")
