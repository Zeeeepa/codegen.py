"""
Tests for the BaseComponent class.

This module contains tests for the BaseComponent class,
verifying its lifecycle hooks, event handling, and resource management.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.events import EventType, Event


class TestBaseComponent:
    """Tests for the BaseComponent class."""
    
    def test_init(self, root, mock_controller):
        """Test component initialization."""
        # Create component
        component = BaseComponent(root, mock_controller)
        
        # Verify initialization
        assert component.controller == mock_controller
        assert component.logger is not None
        assert component._event_subscriptions == []
        assert component._resources == []
        assert component._timers == []
        assert component._mounted is False
        
    def test_lifecycle_hooks(self, root, mock_controller):
        """Test component lifecycle hooks."""
        # Create component with mock _on_mount
        component = BaseComponent(root, mock_controller)
        component._on_mount = MagicMock()
        
        # Pack component to trigger mount
        component.pack()
        
        # Verify mount hook called
        component._on_mount.assert_called_once()
        assert component._mounted is True
        
        # Pack again should not call mount hook again
        component._on_mount.reset_mock()
        component.pack()
        component._on_mount.assert_not_called()
        
    def test_event_subscription(self, root, mock_controller, event_callback):
        """Test event subscription and unsubscription."""
        # Create component
        component = BaseComponent(root, mock_controller)
        
        # Subscribe to event
        mock_controller.event_bus.subscribe.return_value = "subscription-id"
        subscription_id = component.subscribe(EventType.AGENT_RUN_REQUESTED, event_callback)
        
        # Verify subscription
        assert subscription_id == "subscription-id"
        assert component._event_subscriptions == ["subscription-id"]
        mock_controller.event_bus.subscribe.assert_called_once_with(
            EventType.AGENT_RUN_REQUESTED, event_callback
        )
        
        # Destroy component
        component.destroy()
        
        # Verify unsubscription
        mock_controller.event_bus.unsubscribe.assert_called_once_with("subscription-id")
        
    def test_resource_management(self, root, mock_controller):
        """Test resource management."""
        # Create component
        component = BaseComponent(root, mock_controller)
        
        # Create mock resource and cleanup function
        resource = MagicMock()
        cleanup_func = MagicMock()
        
        # Register resource
        result = component.register_resource(resource, cleanup_func)
        
        # Verify registration
        assert result == resource
        assert component._resources == [(resource, cleanup_func)]
        
        # Destroy component
        component.destroy()
        
        # Verify cleanup
        cleanup_func.assert_called_once_with(resource)
        
    def test_resource_cleanup_error(self, root, mock_controller):
        """Test resource cleanup error handling."""
        # Create component
        component = BaseComponent(root, mock_controller)
        component.logger = MagicMock()
        
        # Create mock resource and cleanup function that raises exception
        resource = MagicMock()
        cleanup_func = MagicMock(side_effect=Exception("Cleanup error"))
        
        # Register resource
        component.register_resource(resource, cleanup_func)
        
        # Destroy component
        component.destroy()
        
        # Verify cleanup attempted and error logged
        cleanup_func.assert_called_once_with(resource)
        component.logger.error.assert_called_once()
        assert "Cleanup error" in component.logger.error.call_args[0][0]
        
    def test_timer_management(self, root, mock_controller, patch_after):
        """Test timer management."""
        # Create component
        component = BaseComponent(root, mock_controller)
        
        # Create mock callback
        callback = MagicMock()
        
        # Schedule timer
        timer_id = component.schedule_timer(1000, callback)
        
        # Verify timer scheduled
        assert timer_id == 1
        assert component._timers == [1]
        
        # Cancel timers
        component.cancel_timers()
        
        # Verify timers cancelled
        assert component._timers == []
        
    def test_repeating_timer(self, root, mock_controller):
        """Test repeating timer."""
        # Create component
        component = BaseComponent(root, mock_controller)
        
        # Create mock callback
        callback = MagicMock()
        
        # Mock after method
        component.after = MagicMock(return_value=1)
        
        # Schedule repeating timer
        timer_id = component.schedule_timer(1000, callback, repeat=True)
        
        # Verify timer scheduled
        assert timer_id == 1
        assert component._timers == [1]
        
        # Get the callback function passed to after
        after_callback = component.after.call_args[0][1]
        
        # Call the callback function to simulate timer firing
        after_callback()
        
        # Verify callback called and timer rescheduled
        callback.assert_called_once()
        assert len(component._timers) == 2
        
    def test_destroy_cancels_timers(self, root, mock_controller, patch_after):
        """Test that destroy cancels timers."""
        # Create component
        component = BaseComponent(root, mock_controller)
        component.cancel_timers = MagicMock()
        
        # Schedule timer
        component.schedule_timer(1000, MagicMock())
        
        # Destroy component
        component.destroy()
        
        # Verify timers cancelled
        component.cancel_timers.assert_called_once()

