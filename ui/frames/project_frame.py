"""
Project frame for the Codegen UI.

This module provides a project frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class ProjectFrame(BaseComponent):
    """Project frame for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the project frame.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create frame for projects
        projects_frame = ttk.Frame(self.frame, padding=PADDING)
        projects_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create projects treeview
        columns = ("id", "name", "description", "created_at")
        self.projects_tree = ttk.Treeview(
            projects_frame, columns=columns, show="headings", selectmode="browse"
        )
        
        # Define headings
        self.projects_tree.heading("id", text="ID")
        self.projects_tree.heading("name", text="Name")
        self.projects_tree.heading("description", text="Description")
        self.projects_tree.heading("created_at", text="Created At")
        
        # Define columns
        self.projects_tree.column("id", width=50)
        self.projects_tree.column("name", width=150)
        self.projects_tree.column("description", width=400)
        self.projects_tree.column("created_at", width=150)
        
        # Add scrollbar
        projects_scrollbar = ttk.Scrollbar(
            projects_frame, orient=tk.VERTICAL, command=self.projects_tree.yview
        )
        self.projects_tree.configure(yscrollcommand=projects_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        projects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create button frame
        button_frame = ttk.Frame(self.frame, padding=PADDING)
        button_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create refresh button
        refresh_button = ttk.Button(
            button_frame, text="Refresh", command=self.load_projects
        )
        refresh_button.pack(side=tk.RIGHT, padx=PADDING)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        pass
    
    def load_projects(self):
        """Load projects."""
        # Clear projects tree
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        # Add placeholder projects
        self.projects_tree.insert(
            "",
            tk.END,
            values=(
                "1",
                "Project 1",
                "This is a placeholder project",
                "2023-01-01",
            ),
        )
        self.projects_tree.insert(
            "",
            tk.END,
            values=(
                "2",
                "Project 2",
                "This is another placeholder project",
                "2023-01-02",
            ),
        )
    
    def clear(self):
        """Clear the project list."""
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)

