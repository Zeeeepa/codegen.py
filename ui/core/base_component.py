"""
Base component for the Codegen UI.

This module provides a base component class for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Callable

from ui.core.events import EventBus, Event, EventType


class BaseComponent:
    """Base component for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the base component.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        self.parent = parent
        self.controller = controller
        self.event_bus = controller.event_bus
        self.frame = ttk.Frame(parent)
        
        # Register event handlers
        self._register_event_handlers()
        
        # Initialize UI
        self._init_ui()
    
    def _register_event_handlers(self):
        """Register event handlers."""
        # Override in subclasses
        pass
    
    def _init_ui(self):
        """Initialize the UI."""
        # Override in subclasses
        pass
    
    def pack(self, **kwargs):
        """
        Pack the component.
        
        Args:
            **kwargs: Keyword arguments to pass to the pack method.
        """
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Unpack the component."""
        self.frame.pack_forget()
    
    def grid(self, **kwargs):
        """
        Grid the component.
        
        Args:
            **kwargs: Keyword arguments to pass to the grid method.
        """
        self.frame.grid(**kwargs)
    
    def grid_forget(self):
        """Remove the component from the grid."""
        self.frame.grid_forget()
    
    def place(self, **kwargs):
        """
        Place the component.
        
        Args:
            **kwargs: Keyword arguments to pass to the place method.
        """
        self.frame.place(**kwargs)
    
    def place_forget(self):
        """Remove the component from the place manager."""
        self.frame.place_forget()

