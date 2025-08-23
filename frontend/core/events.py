"""
Event system for the Enhanced Codegen UI.

This module provides an event system for the Enhanced Codegen UI,
allowing components to communicate with each other.
"""

import uuid
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Callable


class EventType(Enum):
    """Event types for the Enhanced Codegen UI."""
    
    # Authentication events
    LOGIN_REQUESTED = auto()
    LOGIN_SUCCEEDED = auto()
    LOGIN_FAILED = auto()
    LOGOUT_REQUESTED = auto()
    
    # Agent run events
    AGENT_RUN_REQUESTED = auto()
    AGENT_RUN_STARTED = auto()
    AGENT_RUN_SUCCEEDED = auto()
    AGENT_RUN_FAILED = auto()
    AGENT_RUN_CANCELLED = auto()
    AGENT_RUN_CONTINUED = auto()
    
    # Data events
    DATA_REQUESTED = auto()
    DATA_LOADED = auto()
    DATA_LOAD_FAILED = auto()
    
    # Navigation events
    NAVIGATION_REQUESTED = auto()
    
    # Error events
    ERROR_OCCURRED = auto()
    
    # Refresh events
    REFRESH_REQUESTED = auto()
    
    # UI events
    UI_STATE_CHANGED = auto()


class Event:
    """Event for the Enhanced Codegen UI."""
    
    def __init__(self, event_type: EventType, data: Optional[Dict[str, Any]] = None):
        """
        Initialize the event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        self.event_type = event_type
        self.data = data or {}
        self.id = str(uuid.uuid4())


class EventBus:
    """Event bus for the Enhanced Codegen UI."""
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers = {}
        
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
            
        Returns:
            Subscription ID
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
            
        subscription_id = str(uuid.uuid4())
        
        self._subscribers[event_type].append({
            "id": subscription_id,
            "handler": handler
        })
        
        return subscription_id
        
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from an event.
        
        Args:
            subscription_id: Subscription ID to unsubscribe
            
        Returns:
            Whether the subscription was found and removed
        """
        for event_type, subscribers in self._subscribers.items():
            for i, subscription in enumerate(subscribers):
                if subscription["id"] == subscription_id:
                    self._subscribers[event_type].pop(i)
                    return True
        return False
        
    def publish(self, event: Event):
        """
        Publish an event.
        
        Args:
            event: Event to publish
        """
        if event.event_type in self._subscribers:
            for subscription in self._subscribers[event.event_type]:
                try:
                    subscription["handler"](event)
                except Exception as e:
                    print(f"Error handling event {event.event_type}: {str(e)}")

