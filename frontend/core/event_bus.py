"""
Event bus for the Codegen UI.

This module provides an event bus for the Codegen UI.
"""

from typing import Dict, List, Any, Callable


class EventBus:
    """Event bus for the Codegen UI."""
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event.
        
        Args:
            event_type: The type of event to subscribe to.
            callback: The function to call when the event is published.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event.
        
        Args:
            event_type: The type of event to unsubscribe from.
            callback: The function to unsubscribe.
        """
        if event_type not in self.subscribers:
            return
        
        self.subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Any = None):
        """Publish an event.
        
        Args:
            event_type: The type of event to publish.
            data: The data to pass to the subscribers.
        """
        if event_type not in self.subscribers:
            return
        
        for callback in self.subscribers[event_type]:
            callback(data)

