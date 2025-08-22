"""
Login frame for the Enhanced Codegen UI.

This module provides the login frame for the Enhanced Codegen UI,
allowing users to authenticate with the Codegen API.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import logging
from typing import Any, Dict, List, Optional

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType
from enhanced_codegen_ui.utils.constants import PADDING, COLORS


class LoginFrame(ttk.Frame):
    """
    Login frame for the Enhanced Codegen UI.
    
    This class provides a login frame for the Enhanced Codegen UI,
    allowing users to authenticate with the Codegen API.
    """
    
    def __init__(self, parent: Any, controller: Controller):
        """
        Initialize the login frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.logger = logging.getLogger(__name__)
        
        # Create variables
        self.api_key_var = tk.StringVar()
        self.show_api_key_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar()
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _create_widgets(self):
        """Create the login frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create login form
        login_frame = ttk.Frame(container, padding=PADDING*2)
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header = ttk.Label(
            login_frame,
            text="Login to Codegen",
            style="Header.TLabel"
        )
        header.pack(pady=(0, PADDING*2))
        
        # Create form
        form = ttk.Frame(login_frame)
        form.pack(fill=tk.X)
        
        # Create API key label
        api_key_label = ttk.Label(form, text="API Key:")
        api_key_label.grid(row=0, column=0, sticky=tk.W, pady=PADDING)
        
        # Create API key entry
        self.api_key_entry = ttk.Entry(
            form,
            textvariable=self.api_key_var,
            width=40,
            show="*"
        )
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=PADDING)
        self.api_key_entry.bind("<Return>", lambda e: self._login())
        
        # Create show API key checkbox
        show_api_key_cb = ttk.Checkbutton(
            form,
            text="Show API Key",
            variable=self.show_api_key_var,
            command=self._toggle_api_key_visibility
        )
        show_api_key_cb.grid(row=1, column=1, sticky=tk.W, pady=PADDING)
        
        # Create login button
        login_button = ttk.Button(
            form,
            text="Login",
            command=self._login,
            style="Primary.TButton"
        )
        login_button.grid(row=2, column=1, sticky=tk.W, pady=PADDING*2)
        
        # Create status label
        status_label = ttk.Label(
            form,
            textvariable=self.status_var,
            foreground=COLORS["error"]
        )
        status_label.grid(row=3, column=1, sticky=tk.W, pady=PADDING)
        
        # Create get API key link
        get_api_key_frame = ttk.Frame(form)
        get_api_key_frame.grid(row=4, column=1, sticky=tk.W, pady=PADDING)
        
        get_api_key_label = ttk.Label(
            get_api_key_frame,
            text="Don't have an API key? "
        )
        get_api_key_label.pack(side=tk.LEFT)
        
        get_api_key_link = ttk.Label(
            get_api_key_frame,
            text="Get one here",
            foreground=COLORS["primary"],
            cursor="hand2"
        )
        get_api_key_link.pack(side=tk.LEFT)
        get_api_key_link.bind("<Button-1>", self._open_api_key_page)
        
        # Configure grid
        form.columnconfigure(1, weight=1)
        
    def _register_event_handlers(self):
        """Register event handlers."""
        # Register login events
        self.controller.event_bus.subscribe(
            EventType.LOGIN_SUCCEEDED,
            self._on_login_succeeded
        )
        
        self.controller.event_bus.subscribe(
            EventType.LOGIN_FAILED,
            self._on_login_failed
        )
        
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        show = self.show_api_key_var.get()
        self.api_key_entry.config(show="" if show else "*")
        
    def _login(self):
        """Handle login button click."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self.status_var.set("API key is required")
            return
            
        # Clear status
        self.status_var.set("")
        
        # Publish login requested event
        self.controller.event_bus.publish(
            Event(EventType.LOGIN_REQUESTED, {"api_key": api_key})
        )
        
    def _open_api_key_page(self, event):
        """
        Open the API key page in a web browser.
        
        Args:
            event: Event object
        """
        webbrowser.open("https://codegen.com/settings")
        
    def _on_login_succeeded(self, event: Event):
        """
        Handle login succeeded event.
        
        Args:
            event: Event object
        """
        # Clear API key
        self.api_key_var.set("")
        
        # Clear status
        self.status_var.set("")
        
    def _on_login_failed(self, event: Event):
        """
        Handle login failed event.
        
        Args:
            event: Event object
        """
        error = event.data.get("error", "Login failed")
        self.status_var.set(error)

