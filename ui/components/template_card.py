"""
Template card component for the Codegen UI.

This module provides a card component for displaying template information.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, Callable

from ui.utils.constants import PADDING, COLORS

logger = logging.getLogger(__name__)

class TemplateCard(ttk.Frame):
    """
    Card component for displaying template information.
    
    This component displays a card with template information, including
    name, description, and actions.
    """
    
    def __init__(
        self, 
        parent, 
        template: Dict[str, Any], 
        on_view: Optional[Callable[[str], None]] = None,
        on_edit: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        on_use: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the template card.
        
        Args:
            parent: Parent widget
            template: Template data
            on_view: Callback for viewing template details
            on_edit: Callback for editing template
            on_delete: Callback for deleting template
            on_use: Callback for using template
        """
        super().__init__(parent, style="Card.TFrame")
        
        self.template = template
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_use = on_use
        
        # Configure style
        self.configure(padding=PADDING)
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for the template card."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False)
        
        # Create category indicator
        category = self.template.get("category", "UNKNOWN")
        category_color = COLORS.get(category, COLORS["UNKNOWN"])
        category_indicator = ttk.Label(
            header_frame,
            text="●",
            foreground=category_color,
            font=("Helvetica", 16)
        )
        category_indicator.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create title
        title = ttk.Label(
            header_frame,
            text=self.template.get("name", "Unknown Template"),
            style="Subheader.TLabel"
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=PADDING)
        
        # Create description label
        description_label = ttk.Label(
            content_frame,
            text="Description:",
            style="Bold.TLabel"
        )
        description_label.pack(anchor=tk.W)
        
        # Create description text
        description = self.template.get("description", "No description")
        if len(description) > 100:
            description = description[:97] + "..."
        
        description_text = ttk.Label(
            content_frame,
            text=description,
            wraplength=400
        )
        description_text.pack(fill=tk.X, expand=True, pady=(0, PADDING))
        
        # Create category label
        category_label = ttk.Label(
            content_frame,
            text=f"Category: {category}",
            style="Small.TLabel"
        )
        category_label.pack(anchor=tk.W)
        
        # Create actions frame
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X, expand=False, pady=(PADDING, 0))
        
        # Create view button
        view_button = ttk.Button(
            actions_frame,
            text="View",
            command=self._on_view_click
        )
        view_button.pack(side=tk.LEFT)
        
        # Create edit button
        edit_button = ttk.Button(
            actions_frame,
            text="Edit",
            command=self._on_edit_click
        )
        edit_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create delete button
        delete_button = ttk.Button(
            actions_frame,
            text="Delete",
            command=self._on_delete_click
        )
        delete_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create use button
        use_button = ttk.Button(
            actions_frame,
            text="Use",
            command=self._on_use_click
        )
        use_button.pack(side=tk.RIGHT)
    
    def _on_view_click(self):
        """Handle view button click."""
        if self.on_view:
            self.on_view(self.template.get("id"))
    
    def _on_edit_click(self):
        """Handle edit button click."""
        if self.on_edit:
            self.on_edit(self.template.get("id"))
    
    def _on_delete_click(self):
        """Handle delete button click."""
        if self.on_delete:
            self.on_delete(self.template.get("id"))
    
    def _on_use_click(self):
        """Handle use button click."""
        if self.on_use:
            self.on_use(self.template.get("id"))
    
    def update(self, template: Dict[str, Any]):
        """
        Update the template card.
        
        Args:
            template: Template data
        """
        self.template = template
        
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate widgets
        self._create_widgets()

