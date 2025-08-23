"""
Event system for the Codegen UI.

This module provides an event bus system for communication between UI components.
"""

import enum
from typing import Any, Callable, Dict, List, Optional, Set


class EventType(enum.Enum):
    """Event types for the Codegen UI."""
    
    # Application events
    APP_INIT = "app_init"
    APP_EXIT = "app_exit"
    
    # Authentication events
    LOGIN = "login"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    
    # Navigation events
    NAVIGATE = "navigate"
    
    # Agent events
    AGENT_RUN_CREATED = "agent_run_created"
    AGENT_RUN_UPDATED = "agent_run_updated"
    AGENT_RUN_COMPLETED = "agent_run_completed"
    AGENT_RUN_FAILED = "agent_run_failed"
    
    # UI events
    UI_REFRESH = "ui_refresh"
    UI_ERROR = "ui_error"
    UI_SUCCESS = "ui_success"
    UI_WARNING = "ui_warning"
    UI_INFO = "ui_info"


class Event:
    """Event class for the Codegen UI."""
    
    def __init__(self, event_type: EventType, data: Optional[Any] = None):
        """
        Initialize an event.
        
        Args:
            event_type: The type of event.
            data: Optional data associated with the event.
        """
        self.event_type = event_type
        self.data = data


class EventBus:
    """Event bus for the Codegen UI."""
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: The event type to subscribe to.
            callback: The callback function to call when the event is published.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from.
            callback: The callback function to unsubscribe.
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event: Event):
        """
        Publish an event.
        
        Args:
            event: The event to publish.
        """
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)
    
    def clear(self):
        """Clear all subscribers."""
        self._subscribers.clear()

