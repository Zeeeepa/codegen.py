"""
Event system for the Codegen UI.

This module provides an event system for the Codegen UI, allowing
components to communicate with each other.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types."""
    
    # Authentication
    LOGIN = auto()
    LOGOUT = auto()
    
    # Agent runs
    AGENT_RUN_CREATED = auto()
    AGENT_RUN_UPDATED = auto()
    AGENT_RUN_COMPLETED = auto()
    AGENT_RUN_ERROR = auto()
    AGENT_RUN_PAUSED = auto()
    AGENT_RUN_RESUMED = auto()
    AGENT_RUN_STARRED = auto()
    AGENT_RUN_UNSTARRED = auto()
    
    # Projects
    PROJECT_STARRED = auto()
    PROJECT_UNSTARRED = auto()
    
    # Templates
    TEMPLATE_CREATED = auto()
    TEMPLATE_UPDATED = auto()
    TEMPLATE_DELETED = auto()
    
    # ProRun configurations
    PRORUN_CONFIG_CREATED = auto()
    PRORUN_CONFIG_UPDATED = auto()
    PRORUN_CONFIG_DELETED = auto()
    
    # Notifications
    NOTIFICATION_RECEIVED = auto()
    
    # Refresh
    REFRESH_REQUESTED = auto()

class Event:
    """
    Event class.
    
    This class represents an event in the Codegen UI.
    """
    
    def __init__(self, type: str, data: Dict[str, Any]):
        """
        Initialize the event.
        
        Args:
            type: Event type
            data: Event data
        """
        self.type = type
        self.data = data
    
    def __str__(self) -> str:
        """
        Get string representation.
        
        Returns:
            String representation
        """
        return f"Event(type={self.type}, data={self.data})"
    
    def __repr__(self) -> str:
        """
        Get string representation.
        
        Returns:
            String representation
        """
        return self.__str__()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get event data.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Event data
        """
        return self.data.get(key, default)

class EventBus:
    """
    Event bus class.
    
    This class provides an event bus for the Codegen UI, allowing
    components to communicate with each other.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers = {}
    
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event.
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event.
        
        Args:
            event: Event
        """
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
    
    def clear(self) -> None:
        """Clear all subscribers."""
        self.subscribers = {}

