"""
Enhanced event bus for the Enhanced Codegen UI.

This module provides an enhanced event bus for the Enhanced Codegen UI,
with support for typed events, event history, and metrics.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Tuple, Union
from collections import defaultdict, deque, Counter

from enhanced_codegen_ui.core.events import EventType


class TypedEvent:
    """
    Typed event with validation.
    
    This class represents a typed event with validation support,
    ensuring that event data conforms to expected schemas.
    """
    
    def __init__(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, schema: Optional[Any] = None):
        """
        Initialize the typed event.
        
        Args:
            event_type: Event type
            data: Event data
            schema: Optional schema for validation
        """
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
        self.id = str(uuid.uuid4())
        
        # Validate data against schema if provided
        if schema and not self._validate_schema(schema):
            raise ValueError(f"Invalid event data for {event_type}")
            
    def _validate_schema(self, schema: Any) -> bool:
        """
        Validate event data against schema.
        
        Args:
            schema: Schema to validate against
            
        Returns:
            Whether the data is valid
        """
        try:
            schema.validate(self.data)
            return True
        except ValueError as e:
            logging.error(f"Event validation error: {str(e)}")
            # Re-raise the exception to be caught by the caller
            raise
        except Exception as e:
            logging.error(f"Event validation error: {str(e)}")
            return False


class EnhancedEventBus:
    """
    Enhanced event bus with debugging and metrics.
    
    This class provides an enhanced event bus with support for
    typed events, event history, and metrics.
    """
    
    def __init__(self, history_size: int = 100):
        """
        Initialize the enhanced event bus.
        
        Args:
            history_size: Maximum number of events to keep in history
        """
        self._subscribers = {}
        self._event_history = deque(maxlen=history_size)
        self._metrics = defaultdict(Counter)
        # Initialize metrics categories to ensure they exist even if empty
        self._metrics["published"] = Counter()
        self._metrics["handled"] = Counter()
        self._metrics["errors"] = Counter()
        self.logger = logging.getLogger(__name__)
        
    def subscribe(self, event_type: EventType, handler: Callable[[TypedEvent], None], priority: int = 0) -> str:
        """
        Subscribe to an event type with priority.
        
        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
            priority: Handler priority (higher first)
            
        Returns:
            Subscription ID
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
            
        subscription_id = str(uuid.uuid4())
        
        subscription = {
            "id": subscription_id,
            "handler": handler,
            "priority": priority
        }
        
        self._subscribers[event_type].append(subscription)
        # Sort by priority (higher first)
        self._subscribers[event_type].sort(key=lambda s: -s["priority"])
        
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
        
    def publish(self, event: TypedEvent) -> None:
        """
        Publish an event.
        
        Args:
            event: Event to publish
        """
        # Record event
        self._event_history.append(event)
        self._metrics["published"][event.event_type] += 1
        
        # Notify subscribers
        if event.event_type in self._subscribers:
            for subscription in self._subscribers[event.event_type]:
                try:
                    subscription["handler"](event)
                    self._metrics["handled"][event.event_type] += 1
                except Exception as e:
                    self.logger.error(f"Error handling event {event.event_type}: {str(e)}")
                    self._metrics["errors"][event.event_type] += 1
                    
    def get_metrics(self) -> Dict[str, Dict[EventType, int]]:
        """
        Get event metrics.
        
        Returns:
            Event metrics
        """
        return {
            category: dict(counter)
            for category, counter in self._metrics.items()
        }
        
    def get_history(self) -> List[TypedEvent]:
        """
        Get event history.
        
        Returns:
            Event history
        """
        return list(self._event_history)
        
    def clear(self) -> None:
        """Clear all subscriptions, history, and metrics."""
        self._subscribers = {}
        self._event_history.clear()
        self._metrics = defaultdict(Counter)
        # Re-initialize metrics categories
        self._metrics["published"] = Counter()
        self._metrics["handled"] = Counter()
        self._metrics["errors"] = Counter()
