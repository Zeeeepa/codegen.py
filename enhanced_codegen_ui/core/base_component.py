"""
Base component for the Enhanced Codegen UI.

This module provides a base component class for the Enhanced Codegen UI,
implementing common functionality for UI components.
"""

import tkinter as tk
from tkinter import ttk
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Tuple

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType


class BaseComponent(ttk.Frame):
    """
    Base component for the Enhanced Codegen UI.
    
    This class provides common functionality for UI components,
    including lifecycle hooks, event handling, and resource management.
    """
    
    def __init__(self, parent: Any, controller: Controller):
        """
        Initialize the base component.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.logger = logging.getLogger(self.__class__.__name__)
        self._event_subscriptions = []
        self._resources = []
        self._timers = []
        self._mounted = False
        
        # Initialize component
        self._init_component()
        
    def _init_component(self):
        """Initialize the component."""
        # Create variables
        self._create_variables()
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _create_variables(self):
        """Create component variables."""
        pass
        
    def _create_widgets(self):
        """Create component widgets."""
        pass
        
    def _register_event_handlers(self):
        """Register event handlers."""
        pass
        
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """
        Subscribe to an event.
        
        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
            
        Returns:
            Subscription ID
        """
        subscription_id = self.controller.event_bus.subscribe(event_type, handler)
        self._event_subscriptions.append(subscription_id)
        return subscription_id
        
    def register_resource(self, resource: Any, cleanup_func: Callable[[Any], None]) -> Any:
        """
        Register a resource for cleanup.
        
        Args:
            resource: Resource to register
            cleanup_func: Function to clean up the resource
            
        Returns:
            The registered resource
        """
        self._resources.append((resource, cleanup_func))
        return resource
        
    def schedule_timer(self, delay: int, callback: Callable, repeat: bool = False) -> int:
        """
        Schedule a timer.
        
        Args:
            delay: Delay in milliseconds
            callback: Callback function
            repeat: Whether to repeat the timer
            
        Returns:
            Timer ID
        """
        if repeat:
            def _callback():
                callback()
                self._timers.append(self.after(delay, _callback))
            timer_id = self.after(delay, _callback)
        else:
            timer_id = self.after(delay, callback)
            
        self._timers.append(timer_id)
        return timer_id
        
    def cancel_timers(self):
        """Cancel all timers."""
        for timer_id in self._timers:
            self.after_cancel(timer_id)
        self._timers = []
        
    def pack(self, **kwargs):
        """
        Pack the component and mark as mounted.
        
        Args:
            **kwargs: Pack options
        """
        super().pack(**kwargs)
        if not self._mounted:
            self._mounted = True
            self._on_mount()
            
    def _on_mount(self):
        """Called when the component is mounted."""
        pass
        
    def destroy(self):
        """Destroy the component and clean up resources."""
        # Cancel timers
        self.cancel_timers()
        
        # Clean up event subscriptions
        for subscription_id in self._event_subscriptions:
            self.controller.event_bus.unsubscribe(subscription_id)
            
        # Clean up resources
        for resource, cleanup_func in self._resources:
            try:
                cleanup_func(resource)
            except Exception as e:
                self.logger.error(f"Error cleaning up resource: {str(e)}")
                
        # Call destroy
        super().destroy()

