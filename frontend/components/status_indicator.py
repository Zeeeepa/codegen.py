"""
Status indicator component for the Enhanced Codegen UI.

This module provides a status indicator component for the Enhanced Codegen UI,
displaying status information with appropriate styling.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.utils.constants import PADDING, COLORS, STATUS_COLORS


class StatusIndicator(BaseComponent):
    """
    Status indicator component for the Enhanced Codegen UI.
    
    This class provides a status indicator component for the Enhanced Codegen UI,
    displaying status information with appropriate styling.
    """
    
    def __init__(
        self,
        parent: Any,
        controller: Controller,
        status: str = "",
        status_type: str = "info",
        show_icon: bool = True
    ):
        """
        Initialize the status indicator.
        
        Args:
            parent: Parent widget
            controller: Application controller
            status: Initial status text
            status_type: Status type (info, success, warning, error)
            show_icon: Whether to show status icon
        """
        self.status = status
        self.status_type = status_type
        self.show_icon = show_icon
        
        super().__init__(parent, controller)
        
    def _create_variables(self):
        """Create component variables."""
        self.status_var = tk.StringVar(value=self.status)
        
    def _create_widgets(self):
        """Create component widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.X)
        
        # Create icon if enabled
        if self.show_icon:
            self.icon_label = ttk.Label(
                container,
                text=self._get_icon_for_status(self.status_type),
                foreground=self._get_color_for_status(self.status_type)
            )
            self.icon_label.pack(side=tk.LEFT, padx=(0, PADDING/2))
            
        # Create status label
        self.status_label = ttk.Label(
            container,
            textvariable=self.status_var,
            foreground=self._get_color_for_status(self.status_type)
        )
        self.status_label.pack(side=tk.LEFT)
        
    def _get_icon_for_status(self, status_type: str) -> str:
        """
        Get icon for status type.
        
        Args:
            status_type: Status type
            
        Returns:
            Icon text
        """
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "pending": "⋯",
            "running": "⟳",
            "completed": "✓",
            "failed": "✗",
            "cancelled": "⊗"
        }
        return icons.get(status_type, "•")
        
    def _get_color_for_status(self, status_type: str) -> str:
        """
        Get color for status type.
        
        Args:
            status_type: Status type
            
        Returns:
            Color
        """
        if status_type in STATUS_COLORS:
            return STATUS_COLORS[status_type]
            
        colors = {
            "info": COLORS["info"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }
        return colors.get(status_type, COLORS["text"])
        
    def set_status(self, status: str, status_type: Optional[str] = None):
        """
        Set the status.
        
        Args:
            status: Status text
            status_type: Status type
        """
        self.status_var.set(status)
        
        if status_type:
            self.status_type = status_type
            
            # Update icon if enabled
            if self.show_icon:
                self.icon_label.config(
                    text=self._get_icon_for_status(self.status_type),
                    foreground=self._get_color_for_status(self.status_type)
                )
                
            # Update status label color
            self.status_label.config(
                foreground=self._get_color_for_status(self.status_type)
            )
            
    def clear(self):
        """Clear the status."""
        self.set_status("", "info")

