"""
Event System Interfaces

Defines the contracts for event-driven communication between layers.
Enables loose coupling and extensibility through plugin architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import datetime
import uuid


class EventType(Enum):
    """Event types for the system"""
    # Agent Run Events
    AGENT_RUN_CREATED = "agent_run_created"
    AGENT_RUN_STARTED = "agent_run_started"
    AGENT_RUN_COMPLETED = "agent_run_completed"
    AGENT_RUN_FAILED = "agent_run_failed"
    AGENT_RUN_CANCELLED = "agent_run_cancelled"
    AGENT_RUN_PAUSED = "agent_run_paused"
    AGENT_RUN_RESUMED = "agent_run_resumed"
    
    # Workspace Events
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_SWITCHED = "workspace_switched"
    WORKSPACE_SYNCED = "workspace_synced"
    WORKSPACE_DELETED = "workspace_deleted"
    
    # Template Events
    TEMPLATE_CREATED = "template_created"
    TEMPLATE_APPLIED = "template_applied"
    TEMPLATE_DELETED = "template_deleted"
    
    # Workflow Events
    WORKFLOW_CREATED = "workflow_created"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIG_CHANGED = "config_changed"
    ERROR_OCCURRED = "error_occurred"
    
    # User Events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    COMMAND_EXECUTED = "command_executed"
    
    # Plugin Events
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"
    PLUGIN_ERROR = "plugin_error"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Event data model"""
    id: str
    type: EventType
    source: str
    timestamp: datetime.datetime
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.datetime.now()


class IEventHandler(ABC):
    """
    Interface for event handlers.
    
    Components that want to handle events must implement this interface.
    """
    
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        """Handle an event"""
        pass
    
    @abstractmethod
    def get_supported_events(self) -> List[EventType]:
        """Get list of event types this handler supports"""
        pass
    
    @abstractmethod
    def get_handler_name(self) -> str:
        """Get unique name for this handler"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get handler priority (lower numbers = higher priority)"""
        pass


class IEventBus(ABC):
    """
    Interface for event bus.
    
    Manages event publishing, subscription, and delivery.
    """
    
    @abstractmethod
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers"""
        pass
    
    @abstractmethod
    def subscribe(
        self,
        event_type: EventType,
        handler: IEventHandler,
        filter_func: Optional[Callable[[Event], bool]] = None
    ) -> str:
        """Subscribe to events of a specific type"""
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        pass
    
    @abstractmethod
    def unsubscribe_handler(self, handler: IEventHandler) -> int:
        """Unsubscribe all subscriptions for a handler"""
        pass
    
    @abstractmethod
    def get_subscribers(self, event_type: EventType) -> List[IEventHandler]:
        """Get all subscribers for an event type"""
        pass
    
    @abstractmethod
    def clear_all_subscriptions(self) -> None:
        """Clear all subscriptions"""
        pass
    
    @abstractmethod
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history"""
        pass


class IEventStore(ABC):
    """
    Interface for event storage.
    
    Provides persistence for events and event history.
    """
    
    @abstractmethod
    def store_event(self, event: Event) -> None:
        """Store an event"""
        pass
    
    @abstractmethod
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """Query stored events"""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        pass
    
    @abstractmethod
    def delete_events_before(self, timestamp: datetime.datetime) -> int:
        """Delete events older than timestamp"""
        pass
    
    @abstractmethod
    def get_event_count(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None
    ) -> int:
        """Get count of stored events"""
        pass


class IEventMiddleware(ABC):
    """
    Interface for event middleware.
    
    Allows processing of events before they are delivered to handlers.
    """
    
    @abstractmethod
    def process_event(self, event: Event) -> Optional[Event]:
        """Process event before delivery. Return None to stop propagation."""
        pass
    
    @abstractmethod
    def get_middleware_name(self) -> str:
        """Get unique name for this middleware"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get middleware priority (lower numbers = higher priority)"""
        pass


# Event creation helper functions
def create_agent_run_event(
    event_type: EventType,
    agent_run_id: int,
    source: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> Event:
    """Create an agent run related event"""
    data = {"agent_run_id": agent_run_id}
    if additional_data:
        data.update(additional_data)
    
    return Event(
        id=str(uuid.uuid4()),
        type=event_type,
        source=source,
        timestamp=datetime.datetime.now(),
        data=data
    )


def create_workspace_event(
    event_type: EventType,
    workspace_name: str,
    source: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> Event:
    """Create a workspace related event"""
    data = {"workspace_name": workspace_name}
    if additional_data:
        data.update(additional_data)
    
    return Event(
        id=str(uuid.uuid4()),
        type=event_type,
        source=source,
        timestamp=datetime.datetime.now(),
        data=data
    )


def create_system_event(
    event_type: EventType,
    source: str,
    message: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> Event:
    """Create a system event"""
    data = {"message": message}
    if additional_data:
        data.update(additional_data)
    
    return Event(
        id=str(uuid.uuid4()),
        type=event_type,
        source=source,
        timestamp=datetime.datetime.now(),
        data=data,
        priority=EventPriority.HIGH
    )

