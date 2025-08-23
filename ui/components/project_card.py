"""
Project card component for the Codegen UI.

This module provides a card component for displaying project information.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, Callable

from ui.utils.constants import PADDING, COLORS

logger = logging.getLogger(__name__)

class ProjectCard(ttk.Frame):
    """
    Card component for displaying project information.
    
    This component displays a card with project information, including
    name, description, and actions.
    """
    
    def __init__(
        self, 
        parent, 
        project: Dict[str, Any], 
        on_view: Optional[Callable[[str], None]] = None,
        on_star: Optional[Callable[[str, bool], None]] = None,
        on_create_run: Optional[Callable[[str], None]] = None,
        is_starred: bool = False,
        has_setup_commands: bool = False
    ):
        """
        Initialize the project card.
        
        Args:
            parent: Parent widget
            project: Project data
            on_view: Callback for viewing project details
            on_star: Callback for starring/unstarring project
            on_create_run: Callback for creating a run for the project
            is_starred: Whether the project is starred
            has_setup_commands: Whether the project has setup commands
        """
        super().__init__(parent, style="Card.TFrame")
        
        self.project = project
        self.on_view = on_view
        self.on_star = on_star
        self.on_create_run = on_create_run
        self.is_starred = is_starred
        self.has_setup_commands = has_setup_commands
        
        # Configure style
        self.configure(padding=PADDING)
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for the project card."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False)
        
        # Create setup commands indicator
        if self.has_setup_commands:
            setup_indicator = ttk.Label(
                header_frame,
                text="⚙",
                foreground=COLORS["SETUP"],
                font=("Helvetica", 16)
            )
            setup_indicator.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create title
        title = ttk.Label(
            header_frame,
            text=self.project.get("name", "Unknown Project"),
            style="Subheader.TLabel"
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create star button
        star_text = "★" if self.is_starred else "☆"
        star_style = "Star.TButton" if self.is_starred else "Unstar.TButton"
        self.star_button = ttk.Button(
            header_frame,
            text=star_text,
            style=star_style,
            width=3,
            command=self._on_star_click
        )
        self.star_button.pack(side=tk.RIGHT, padx=(PADDING, 0))
        
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
        description = self.project.get("description", "No description")
        if len(description) > 100:
            description = description[:97] + "..."
        
        description_text = ttk.Label(
            content_frame,
            text=description,
            wraplength=400
        )
        description_text.pack(fill=tk.X, expand=True, pady=(0, PADDING))
        
        # Create repository label
        repo_name = self.project.get("full_name", "Unknown Repository")
        repo_label = ttk.Label(
            content_frame,
            text=f"Repository: {repo_name}",
            style="Small.TLabel"
        )
        repo_label.pack(anchor=tk.W)
        
        # Create actions frame
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X, expand=False, pady=(PADDING, 0))
        
        # Create view button
        view_button = ttk.Button(
            actions_frame,
            text="View Details",
            command=self._on_view_click
        )
        view_button.pack(side=tk.LEFT)
        
        # Create create run button
        create_run_button = ttk.Button(
            actions_frame,
            text="Create Run",
            command=self._on_create_run_click
        )
        create_run_button.pack(side=tk.LEFT, padx=(PADDING, 0))
    
    def _on_view_click(self):
        """Handle view button click."""
        if self.on_view:
            self.on_view(self.project.get("id"))
    
    def _on_star_click(self):
        """Handle star button click."""
        if self.on_star:
            self.is_starred = not self.is_starred
            star_text = "★" if self.is_starred else "☆"
            star_style = "Star.TButton" if self.is_starred else "Unstar.TButton"
            self.star_button.configure(text=star_text, style=star_style)
            self.on_star(self.project.get("id"), self.is_starred)
    
    def _on_create_run_click(self):
        """Handle create run button click."""
        if self.on_create_run:
            self.on_create_run(self.project.get("id"))
    
    def update(
        self, 
        project: Dict[str, Any], 
        is_starred: bool = None,
        has_setup_commands: bool = None
    ):
        """
        Update the project card.
        
        Args:
            project: Project data
            is_starred: Whether the project is starred
            has_setup_commands: Whether the project has setup commands
        """
        self.project = project
        
        if is_starred is not None:
            self.is_starred = is_starred
        
        if has_setup_commands is not None:
            self.has_setup_commands = has_setup_commands
        
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate widgets
        self._create_widgets()

