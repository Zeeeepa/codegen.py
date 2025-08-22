"""
Action button component for the Enhanced Codegen UI.

This module provides an action button component for the Enhanced Codegen UI,
with support for different button types and states.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.utils.constants import PADDING, COLORS


class ActionButton(BaseComponent):
    """
    Action button component for the Enhanced Codegen UI.
    
    This class provides an action button component for the Enhanced Codegen UI,
    with support for different button types and states.
    """
    
    def __init__(
        self,
        parent: Any,
        controller: Controller,
        text: str,
        command: Callable,
        button_type: str = "primary",
        icon: Optional[str] = None,
        tooltip: Optional[str] = None,
        enabled: bool = True,
        width: Optional[int] = None
    ):
        """
        Initialize the action button.
        
        Args:
            parent: Parent widget
            controller: Application controller
            text: Button text
            command: Button command
            button_type: Button type (primary, secondary, danger, success)
            icon: Button icon
            tooltip: Button tooltip
            enabled: Whether the button is enabled
            width: Button width
        """
        self.text = text
        self.command = command
        self.button_type = button_type
        self.icon = icon
        self.tooltip = tooltip
        self.enabled = enabled
        self.width = width
        
        super().__init__(parent, controller)
        
    def _create_widgets(self):
        """Create component widgets."""
        # Create button style
        style_name = f"{self.button_type.capitalize()}.TButton"
        
        # Create button
        button_args = {
            "text": self.text,
            "command": self.command,
            "style": style_name
        }
        
        if self.width:
            button_args["width"] = self.width
            
        self.button = ttk.Button(self, **button_args)
        self.button.pack(fill=tk.X)
        
        # Set state
        if not self.enabled:
            self.button.state(["disabled"])
            
        # Create tooltip if provided
        if self.tooltip:
            self._create_tooltip()
            
    def _create_tooltip(self):
        """Create tooltip for the button."""
        self.tooltip_window = None
        
        self.button.bind("<Enter>", self._show_tooltip)
        self.button.bind("<Leave>", self._hide_tooltip)
        
    def _show_tooltip(self, event):
        """
        Show tooltip.
        
        Args:
            event: Event object
        """
        if self.tooltip_window or not self.tooltip:
            return
            
        x, y, _, _ = self.button.bbox("insert")
        x += self.button.winfo_rootx() + 25
        y += self.button.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.button)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip label
        label = ttk.Label(
            self.tooltip_window,
            text=self.tooltip,
            background=COLORS["surface"],
            foreground=COLORS["text"],
            relief="solid",
            borderwidth=1,
            padding=PADDING/2
        )
        label.pack()
        
    def _hide_tooltip(self, event):
        """
        Hide tooltip.
        
        Args:
            event: Event object
        """
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def set_enabled(self, enabled: bool):
        """
        Set whether the button is enabled.
        
        Args:
            enabled: Whether the button is enabled
        """
        self.enabled = enabled
        if enabled:
            self.button.state(["!disabled"])
        else:
            self.button.state(["disabled"])
            
    def set_text(self, text: str):
        """
        Set the button text.
        
        Args:
            text: Button text
        """
        self.text = text
        self.button.config(text=text)
        
    def set_command(self, command: Callable):
        """
        Set the button command.
        
        Args:
            command: Button command
        """
        self.command = command
        self.button.config(command=command)
        
    def set_tooltip(self, tooltip: str):
        """
        Set the button tooltip.
        
        Args:
            tooltip: Button tooltip
        """
        self.tooltip = tooltip
        
        # Remove existing tooltip if any
        if hasattr(self, "tooltip_window") and self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
        # Create tooltip if not already set up
        if not hasattr(self, "tooltip_window"):
            self._create_tooltip()

