"""
State management for the Enhanced Codegen UI.

This module provides state management for the Enhanced Codegen UI,
allowing components to share and update state.
"""

from typing import Dict, Any, Optional, List, Set, Callable


class State:
    """State for the Enhanced Codegen UI."""
    
    def __init__(self):
        """Initialize the state."""
        self._state = {}
        self._listeners = {}
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a state value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value
        """
        return self._state.get(key, default)
        
    def set(self, key: str, value: Any):
        """
        Set a state value.
        
        Args:
            key: State key
            value: State value
        """
        old_value = self._state.get(key)
        self._state[key] = value
        
        # Notify listeners if value changed
        if old_value != value and key in self._listeners:
            for listener in self._listeners[key]:
                listener(value, old_value)
                
    def delete(self, key: str):
        """
        Delete a state value.
        
        Args:
            key: State key
        """
        if key in self._state:
            old_value = self._state[key]
            del self._state[key]
            
            # Notify listeners
            if key in self._listeners:
                for listener in self._listeners[key]:
                    listener(None, old_value)
                    
    def clear(self):
        """Clear all state."""
        old_state = self._state.copy()
        self._state = {}
        
        # Notify listeners
        for key, old_value in old_state.items():
            if key in self._listeners:
                for listener in self._listeners[key]:
                    listener(None, old_value)
                    
    def listen(self, key: str, listener: Callable[[Any, Any], None]) -> Callable[[], None]:
        """
        Listen for state changes.
        
        Args:
            key: State key to listen for
            listener: Listener function that takes (new_value, old_value)
            
        Returns:
            Function to remove the listener
        """
        if key not in self._listeners:
            self._listeners[key] = set()
            
        self._listeners[key].add(listener)
        
        def remove_listener():
            """Remove the listener."""
            if key in self._listeners and listener in self._listeners[key]:
                self._listeners[key].remove(listener)
                if not self._listeners[key]:
                    del self._listeners[key]
                    
        return remove_listener
        
    def get_all(self) -> Dict[str, Any]:
        """
        Get all state.
        
        Returns:
            All state
        """
        return self._state.copy()

