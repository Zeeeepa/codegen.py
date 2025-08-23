"""
Tests for the EnhancedEventBus class.

This module contains tests for the EnhancedEventBus class,
verifying its event handling, metrics, and history tracking.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging
from collections import Counter

from enhanced_codegen_ui.core.enhanced_event_bus import EnhancedEventBus, TypedEvent
from enhanced_codegen_ui.core.events import EventType


class TestTypedEvent:
    """Tests for the TypedEvent class."""
    
    def test_init(self):
        """Test event initialization."""
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Verify initialization
        assert event.event_type == EventType.AGENT_RUN_REQUESTED
        assert event.data == {"key": "value"}
        assert event.timestamp is not None
        assert event.id is not None
        
    def test_init_without_data(self):
        """Test event initialization without data."""
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED)
        
        # Verify initialization
        assert event.event_type == EventType.AGENT_RUN_REQUESTED
        assert event.data == {}
        
    def test_validation_success(self):
        """Test event validation success."""
        # Create mock schema
        schema = MagicMock()
        schema.validate.return_value = True
        
        # Create event with schema
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"}, schema)
        
        # Verify validation
        schema.validate.assert_called_once_with({"key": "value"})
        
    def test_validation_failure(self):
        """Test event validation failure."""
        # Create mock schema
        schema = MagicMock()
        schema.validate.side_effect = ValueError("Invalid data")
        
        # Create event with schema
        with pytest.raises(ValueError) as excinfo:
            TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"}, schema)
            
        # Verify validation
        assert "Invalid data" in str(excinfo.value)
        schema.validate.assert_called_once_with({"key": "value"})


class TestEnhancedEventBus:
    """Tests for the EnhancedEventBus class."""
    
    def test_init(self):
        """Test event bus initialization."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Verify initialization
        assert event_bus._subscribers == {}
        assert len(event_bus._event_history) == 0
        assert event_bus._metrics["published"] == Counter()
        assert event_bus._metrics["handled"] == Counter()
        assert event_bus._metrics["errors"] == Counter()
        
    def test_subscribe(self):
        """Test event subscription."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handler
        handler = MagicMock()
        
        # Subscribe to event
        subscription_id = event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Verify subscription
        assert subscription_id is not None
        assert EventType.AGENT_RUN_REQUESTED in event_bus._subscribers
        assert len(event_bus._subscribers[EventType.AGENT_RUN_REQUESTED]) == 1
        assert event_bus._subscribers[EventType.AGENT_RUN_REQUESTED][0]["handler"] == handler
        assert event_bus._subscribers[EventType.AGENT_RUN_REQUESTED][0]["id"] == subscription_id
        assert event_bus._subscribers[EventType.AGENT_RUN_REQUESTED][0]["priority"] == 0
        
    def test_subscribe_with_priority(self):
        """Test event subscription with priority."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handlers
        handler1 = MagicMock()
        handler2 = MagicMock()
        
        # Subscribe to event with different priorities
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler1, priority=1)
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler2, priority=2)
        
        # Verify subscription order (higher priority first)
        assert event_bus._subscribers[EventType.AGENT_RUN_REQUESTED][0]["handler"] == handler2
        assert event_bus._subscribers[EventType.AGENT_RUN_REQUESTED][1]["handler"] == handler1
        
    def test_unsubscribe(self):
        """Test event unsubscription."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handler
        handler = MagicMock()
        
        # Subscribe to event
        subscription_id = event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Verify subscription
        assert len(event_bus._subscribers[EventType.AGENT_RUN_REQUESTED]) == 1
        
        # Unsubscribe from event
        result = event_bus.unsubscribe(subscription_id)
        
        # Verify unsubscription
        assert result is True
        assert len(event_bus._subscribers[EventType.AGENT_RUN_REQUESTED]) == 0
        
    def test_unsubscribe_nonexistent(self):
        """Test unsubscription of nonexistent subscription."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Unsubscribe from nonexistent subscription
        result = event_bus.unsubscribe("nonexistent-id")
        
        # Verify unsubscription
        assert result is False
        
    def test_publish(self):
        """Test event publishing."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handler
        handler = MagicMock()
        
        # Subscribe to event
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Publish event
        event_bus.publish(event)
        
        # Verify handler called
        handler.assert_called_once_with(event)
        
        # Verify metrics
        assert event_bus._metrics["published"][EventType.AGENT_RUN_REQUESTED] == 1
        assert event_bus._metrics["handled"][EventType.AGENT_RUN_REQUESTED] == 1
        assert event_bus._metrics["errors"][EventType.AGENT_RUN_REQUESTED] == 0
        
        # Verify history
        assert len(event_bus._event_history) == 1
        assert event_bus._event_history[0] == event
        
    def test_publish_multiple_handlers(self):
        """Test event publishing with multiple handlers."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handlers
        handler1 = MagicMock()
        handler2 = MagicMock()
        
        # Subscribe to event
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler1)
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler2)
        
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Publish event
        event_bus.publish(event)
        
        # Verify handlers called
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)
        
        # Verify metrics
        assert event_bus._metrics["published"][EventType.AGENT_RUN_REQUESTED] == 1
        assert event_bus._metrics["handled"][EventType.AGENT_RUN_REQUESTED] == 2
        
    def test_publish_handler_error(self):
        """Test event publishing with handler error."""
        # Create event bus
        event_bus = EnhancedEventBus()
        event_bus.logger = MagicMock()
        
        # Create mock handler that raises exception
        handler = MagicMock(side_effect=Exception("Handler error"))
        
        # Subscribe to event
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Publish event
        event_bus.publish(event)
        
        # Verify handler called
        handler.assert_called_once_with(event)
        
        # Verify error logged
        event_bus.logger.error.assert_called_once()
        assert "Handler error" in event_bus.logger.error.call_args[0][0]
        
        # Verify metrics
        assert event_bus._metrics["published"][EventType.AGENT_RUN_REQUESTED] == 1
        assert event_bus._metrics["handled"][EventType.AGENT_RUN_REQUESTED] == 0
        assert event_bus._metrics["errors"][EventType.AGENT_RUN_REQUESTED] == 1
        
    def test_get_metrics(self):
        """Test getting event metrics."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handler
        handler = MagicMock()
        
        # Subscribe to event
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Publish event
        event_bus.publish(event)
        
        # Get metrics
        metrics = event_bus.get_metrics()
        
        # Verify metrics
        assert "published" in metrics
        assert "handled" in metrics
        assert "errors" in metrics
        assert metrics["published"][EventType.AGENT_RUN_REQUESTED] == 1
        assert metrics["handled"][EventType.AGENT_RUN_REQUESTED] == 1
        assert metrics["errors"][EventType.AGENT_RUN_REQUESTED] == 0
        
    def test_get_history(self):
        """Test getting event history."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create events
        event1 = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value1"})
        event2 = TypedEvent(EventType.AGENT_RUN_SUCCEEDED, {"key": "value2"})
        
        # Publish events
        event_bus.publish(event1)
        event_bus.publish(event2)
        
        # Get history
        history = event_bus.get_history()
        
        # Verify history
        assert len(history) == 2
        assert history[0] == event1
        assert history[1] == event2
        
    def test_history_limit(self):
        """Test event history limit."""
        # Create event bus with small history size
        event_bus = EnhancedEventBus(history_size=2)
        
        # Create events
        event1 = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value1"})
        event2 = TypedEvent(EventType.AGENT_RUN_SUCCEEDED, {"key": "value2"})
        event3 = TypedEvent(EventType.AGENT_RUN_FAILED, {"key": "value3"})
        
        # Publish events
        event_bus.publish(event1)
        event_bus.publish(event2)
        event_bus.publish(event3)
        
        # Get history
        history = event_bus.get_history()
        
        # Verify history (oldest event should be dropped)
        assert len(history) == 2
        assert history[0] == event2
        assert history[1] == event3
        
    def test_clear(self):
        """Test clearing event bus."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock handler
        handler = MagicMock()
        
        # Subscribe to event
        event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, handler)
        
        # Create event
        event = TypedEvent(EventType.AGENT_RUN_REQUESTED, {"key": "value"})
        
        # Publish event
        event_bus.publish(event)
        
        # Verify state before clear
        assert len(event_bus._subscribers) > 0
        assert len(event_bus._event_history) > 0
        assert len(event_bus._metrics) > 0
        
        # Clear event bus
        event_bus.clear()
        
        # Verify state after clear
        assert event_bus._subscribers == {}
        assert len(event_bus._event_history) == 0
        assert event_bus._metrics["published"] == Counter()
        assert event_bus._metrics["handled"] == Counter()
        assert event_bus._metrics["errors"] == Counter()

