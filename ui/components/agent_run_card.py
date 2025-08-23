"""
Agent run card component for the Codegen UI.

This module provides a card component for displaying agent run information.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, Callable

from ui.utils.constants import PADDING, COLORS

logger = logging.getLogger(__name__)

class AgentRunCard(ttk.Frame):
    """
    Card component for displaying agent run information.
    
    This component displays a card with agent run information, including
    status, prompt, and actions.
    """
    
    def __init__(
        self, 
        parent, 
        agent_run: Dict[str, Any], 
        on_view: Optional[Callable[[str], None]] = None,
        on_star: Optional[Callable[[str, bool], None]] = None,
        on_resume: Optional[Callable[[str], None]] = None,
        on_stop: Optional[Callable[[str], None]] = None,
        is_starred: bool = False
    ):
        """
        Initialize the agent run card.
        
        Args:
            parent: Parent widget
            agent_run: Agent run data
            on_view: Callback for viewing agent run details
            on_star: Callback for starring/unstarring agent run
            on_resume: Callback for resuming agent run
            on_stop: Callback for stopping agent run
            is_starred: Whether the agent run is starred
        """
        super().__init__(parent, style="Card.TFrame")
        
        self.agent_run = agent_run
        self.on_view = on_view
        self.on_star = on_star
        self.on_resume = on_resume
        self.on_stop = on_stop
        self.is_starred = is_starred
        
        # Configure style
        self.configure(padding=PADDING)
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create widgets for the agent run card."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False)
        
        # Create status indicator
        status = self.agent_run.get("status", "UNKNOWN")
        status_color = COLORS.get(status, COLORS["UNKNOWN"])
        status_indicator = ttk.Label(
            header_frame,
            text="●",
            foreground=status_color,
            font=("Helvetica", 16)
        )
        status_indicator.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create title
        title = ttk.Label(
            header_frame,
            text=f"Run #{self.agent_run.get('id', 'Unknown')}",
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
        
        # Create prompt label
        prompt_label = ttk.Label(
            content_frame,
            text="Prompt:",
            style="Bold.TLabel"
        )
        prompt_label.pack(anchor=tk.W)
        
        # Create prompt text
        prompt = self.agent_run.get("prompt", "No prompt")
        if len(prompt) > 100:
            prompt = prompt[:97] + "..."
        
        prompt_text = ttk.Label(
            content_frame,
            text=prompt,
            wraplength=400
        )
        prompt_text.pack(fill=tk.X, expand=True, pady=(0, PADDING))
        
        # Create status label
        status_label = ttk.Label(
            content_frame,
            text=f"Status: {status}",
            style=f"{status}.TLabel"
        )
        status_label.pack(anchor=tk.W)
        
        # Create timestamp label
        created_at = self.agent_run.get("created_at", "Unknown")
        timestamp_label = ttk.Label(
            content_frame,
            text=f"Created: {created_at}",
            style="Small.TLabel"
        )
        timestamp_label.pack(anchor=tk.W)
        
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
        
        # Create resume button if status is PAUSED
        if status == "PAUSED":
            resume_button = ttk.Button(
                actions_frame,
                text="Resume",
                command=self._on_resume_click
            )
            resume_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create stop button if status is RUNNING
        if status == "RUNNING":
            stop_button = ttk.Button(
                actions_frame,
                text="Stop",
                command=self._on_stop_click
            )
            stop_button.pack(side=tk.LEFT, padx=(PADDING, 0))
    
    def _on_view_click(self):
        """Handle view button click."""
        if self.on_view:
            self.on_view(self.agent_run.get("id"))
    
    def _on_star_click(self):
        """Handle star button click."""
        if self.on_star:
            self.is_starred = not self.is_starred
            star_text = "★" if self.is_starred else "☆"
            star_style = "Star.TButton" if self.is_starred else "Unstar.TButton"
            self.star_button.configure(text=star_text, style=star_style)
            self.on_star(self.agent_run.get("id"), self.is_starred)
    
    def _on_resume_click(self):
        """Handle resume button click."""
        if self.on_resume:
            self.on_resume(self.agent_run.get("id"))
    
    def _on_stop_click(self):
        """Handle stop button click."""
        if self.on_stop:
            self.on_stop(self.agent_run.get("id"))
    
    def update(self, agent_run: Dict[str, Any], is_starred: bool = None):
        """
        Update the agent run card.
        
        Args:
            agent_run: Agent run data
            is_starred: Whether the agent run is starred
        """
        self.agent_run = agent_run
        
        if is_starred is not None:
            self.is_starred = is_starred
        
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate widgets
        self._create_widgets()

