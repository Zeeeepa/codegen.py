"""
Project frame for the Enhanced Codegen UI.

This module provides the project frame for the Enhanced Codegen UI,
displaying a list of repositories and allowing users to search them.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType
from enhanced_codegen_ui.utils.constants import PADDING


class ProjectFrame(ttk.Frame):
    """
    Project frame for the Enhanced Codegen UI.
    
    This class provides a project frame for the Enhanced Codegen UI,
    displaying a list of repositories and allowing users to search them.
    """
    
    def __init__(self, parent: Any, controller: Controller):
        """
        Initialize the project frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.logger = logging.getLogger(__name__)
        
        # Create variables
        self.repositories = []
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _create_widgets(self):
        """Create the project frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create header
        header = ttk.Label(
            header_frame,
            text="Projects",
            style="Header.TLabel"
        )
        header.pack(side=tk.LEFT)
        
        # Create refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            command=self._refresh
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create filter frame
        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create search entry
        search_label = ttk.Label(filter_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        search_entry = ttk.Entry(
            filter_frame,
            textvariable=self.search_var,
            width=20
        )
        search_entry.pack(side=tk.LEFT, padx=(0, PADDING))
        search_entry.bind("<Return>", lambda e: self._refresh())
        
        search_button = ttk.Button(
            filter_frame,
            text="Search",
            command=self._refresh
        )
        search_button.pack(side=tk.LEFT)
        
        # Create treeview
        columns = ("id", "name", "full_name", "description")
        self.treeview = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.treeview.heading("id", text="ID")
        self.treeview.heading("name", text="Name")
        self.treeview.heading("full_name", text="Full Name")
        self.treeview.heading("description", text="Description")
        
        self.treeview.column("id", width=80, anchor=tk.W)
        self.treeview.column("name", width=150, anchor=tk.W)
        self.treeview.column("full_name", width=200, anchor=tk.W)
        self.treeview.column("description", width=400, anchor=tk.W)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create status bar
        status_bar = ttk.Frame(container)
        status_bar.pack(fill=tk.X, pady=(PADDING, 0))
        
        status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var
        )
        status_label.pack(side=tk.LEFT)
        
    def _register_event_handlers(self):
        """Register event handlers."""
        # Register repository events
        self.controller.event_bus.subscribe(
            EventType.REPOSITORIES_LOADED,
            self._on_repositories_loaded
        )
        
        self.controller.event_bus.subscribe(
            EventType.LOAD_ERROR,
            self._on_load_error
        )
        
    def _refresh(self):
        """Refresh the project list."""
        # Publish refresh requested event
        self.controller.event_bus.publish(
            Event(EventType.REFRESH_REQUESTED, {"type": "repositories"})
        )
        
    def _on_repositories_loaded(self, event: Event):
        """
        Handle repositories loaded event.
        
        Args:
            event: Event object with repositories in data
        """
        repositories = event.data.get("repositories", [])
        
        # Filter by search if needed
        search_filter = self.search_var.get().strip().lower()
        if search_filter:
            repositories = [
                repo for repo in repositories
                if (
                    search_filter in (repo.name or "").lower() or
                    search_filter in (repo.full_name or "").lower() or
                    search_filter in (repo.description or "").lower()
                )
            ]
            
        # Store repositories
        self.repositories = repositories
        
        # Update treeview
        self._update_treeview()
        
    def _on_load_error(self, event: Event):
        """
        Handle load error event.
        
        Args:
            event: Event object with error and type in data
        """
        error_type = event.data.get("type")
        if error_type == "repositories":
            error = event.data.get("error", "Error loading repositories")
            self.status_var.set(f"Error: {error}")
            
    def _update_treeview(self):
        """Update the treeview with repositories."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Add repositories to treeview
        for repo in self.repositories:
            # Add to treeview
            self.treeview.insert(
                "",
                tk.END,
                values=(
                    repo.id,
                    repo.name,
                    repo.full_name,
                    repo.description[:50] + "..." if repo.description and len(repo.description) > 50 else repo.description
                )
            )
                
        # Update status text
        self.status_var.set(f"Showing {len(self.repositories)} repositories")
        
    def pack(self, **kwargs):
        """
        Pack the frame and refresh the project list.
        
        Args:
            **kwargs: Pack options
        """
        super().pack(**kwargs)
        self._refresh()

