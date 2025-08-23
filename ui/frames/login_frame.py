"""
Login frame for the Codegen UI.

This module provides a login frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class LoginFrame(BaseComponent):
    """Login frame for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the login frame.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create login frame
        login_frame = ttk.LabelFrame(self.frame, text="Login", padding=PADDING)
        login_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create API key label and entry
        ttk.Label(login_frame, text="API Key:").grid(
            row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING
        )
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(login_frame, width=40, show="*", textvariable=self.api_key_var)
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=PADDING, pady=PADDING)
        
        # Create login button
        login_button = ttk.Button(
            login_frame, text="Login", command=self._login
        )
        login_button.grid(row=1, column=1, sticky=tk.E, padx=PADDING, pady=PADDING)
        
        # Create status label
        self.status_var = tk.StringVar()
        self.status_var.set("Enter your API key to login")
        status_label = ttk.Label(
            login_frame, textvariable=self.status_var, foreground="gray"
        )
        status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=PADDING, pady=PADDING)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        self.event_bus.subscribe(EventType.LOGIN_SUCCESS, self._handle_login_success)
        self.event_bus.subscribe(EventType.LOGIN_FAILURE, self._handle_login_failure)
    
    def _login(self):
        """Log in to the Codegen API."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self.status_var.set("API key cannot be empty")
            return
        
        # Update status
        self.status_var.set("Logging in...")
        
        # Publish login event
        self.event_bus.publish(
            Event(
                EventType.LOGIN,
                {"api_key": api_key}
            )
        )
    
    def _handle_login_success(self, event: Event):
        """
        Handle login success event.
        
        Args:
            event: The login success event.
        """
        self.status_var.set("Login successful")
    
    def _handle_login_failure(self, event: Event):
        """
        Handle login failure event.
        
        Args:
            event: The login failure event.
        """
        error = event.data.get("error", "Login failed")
        self.status_var.set(f"Login failed: {error}")
    
    def clear(self):
        """Clear the login form."""
        self.api_key_var.set("")
        self.status_var.set("Enter your API key to login")

