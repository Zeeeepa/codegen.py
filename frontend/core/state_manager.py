"""
State manager for the Codegen UI.

This module provides a state manager for the Codegen UI.
"""

from typing import Dict, Any, Callable, List

from frontend.core.event_bus import EventBus


class StateManager:
    """State manager for the Codegen UI."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the state manager.
        
        Args:
            event_bus: The event bus to use for publishing state changes.
        """
        self.event_bus = event_bus
        self.state: Dict[str, Any] = {}
    
    def get_state(self, key: str) -> Any:
        """Get a state value.
        
        Args:
            key: The key of the state value.
        
        Returns:
            The state value, or None if the key does not exist.
        """
        return self.state.get(key)
    
    def set_state(self, key: str, value: Any):
        """Set a state value.
        
        Args:
            key: The key of the state value.
            value: The value to set.
        """
        self.state[key] = value
        self.event_bus.publish(f"state_change:{key}", value)
    
    def delete_state(self, key: str):
        """Delete a state value.
        
        Args:
            key: The key of the state value.
        """
        if key in self.state:
            del self.state[key]
            self.event_bus.publish(f"state_delete:{key}", None)
    
    def clear_state(self):
        """Clear all state values."""
        self.state.clear()
        self.event_bus.publish("state_clear", None)

