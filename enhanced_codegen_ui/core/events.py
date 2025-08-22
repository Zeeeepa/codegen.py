"""
Event system for the Enhanced Codegen UI.

This module provides an event system for the Enhanced Codegen UI,
allowing components to communicate with each other in a decoupled way.
"""

import enum
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional, Set


class EventType(enum.Enum):
    """Event types for the Enhanced Codegen UI."""
    
    # Authentication events
    LOGIN_REQUESTED = "login_requested"
    LOGIN_SUCCEEDED = "login_succeeded"
    LOGIN_FAILED = "login_failed"
    LOGOUT_REQUESTED = "logout_requested"
    LOGOUT_SUCCEEDED = "logout_succeeded"
    
    # Agent run events
    AGENT_RUN_REQUESTED = "agent_run_requested"
    AGENT_RUN_SUCCEEDED = "agent_run_succeeded"
    AGENT_RUN_FAILED = "agent_run_failed"
    AGENT_RUN_CANCEL_REQUESTED = "agent_run_cancel_requested"
    AGENT_RUN_CANCEL_SUCCEEDED = "agent_run_cancel_succeeded"
    AGENT_RUN_CANCEL_FAILED = "agent_run_cancel_failed"
    AGENT_RUN_CONTINUE_REQUESTED = "agent_run_continue_requested"
    AGENT_RUN_CONTINUE_SUCCEEDED = "agent_run_continue_succeeded"
    AGENT_RUN_CONTINUE_FAILED = "agent_run_continue_failed"
    
    # Data loading events
    AGENT_RUNS_LOADED = "agent_runs_loaded"
    REPOSITORIES_LOADED = "repositories_loaded"
    MODELS_LOADED = "models_loaded"
    LOAD_ERROR = "load_error"
    
    # UI events
    REFRESH_REQUESTED = "refresh_requested"
    VIEW_AGENT_RUN_REQUESTED = "view_agent_run_requested"
    VIEW_AGENT_RUNS_REQUESTED = "view_agent_runs_requested"
    VIEW_REPOSITORIES_REQUESTED = "view_repositories_requested"
    VIEW_CREATE_AGENT_REQUESTED = "view_create_agent_requested"
    
    # Organization events
    ORGANIZATION_CHANGE_REQUESTED = "organization_change_requested"
    ORGANIZATION_CHANGED = "organization_changed"


@dataclass
class Event:
    """
    Event class for the Enhanced Codegen UI.
    
    Attributes:
        type: Event type
        data: Event data
    """
    
    type: EventType
    data: Dict[str, Any]


class EventBus:
    """
    Event bus for the Enhanced Codegen UI.
    
    This class provides a central event bus for the Enhanced Codegen UI,
    allowing components to publish and subscribe to events.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers = {}
        self.logger = logging.getLogger(__name__)
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            callback: Callback to execute when an event of this type is published
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = set()
            
        self.subscribers[event_type].add(callback)
        self.logger.debug(f"Subscribed to {event_type.value}")
        
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Event type to unsubscribe from
            callback: Callback to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(callback)
            self.logger.debug(f"Unsubscribed from {event_type.value}")
            
    def publish(self, event: Event) -> None:
        """
        Publish an event.
        
        Args:
            event: Event to publish
        """
        self.logger.debug(f"Publishing event {event.type.value}")
        
        if event.type not in self.subscribers:
            return
            
        for callback in self.subscribers[event.type]:
            try:
                callback(event)
            except Exception as e:
                self.logger.exception(f"Error in event handler for {event.type.value}: {str(e)}")
                
    def clear(self) -> None:
        """Clear all subscribers."""
        self.subscribers.clear()
        self.logger.debug("Cleared all subscribers")

