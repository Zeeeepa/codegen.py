"""
Agent list frame for the Codegen UI.

This module provides an agent list frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class AgentListFrame(BaseComponent):
    """Agent list frame for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the agent list frame.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create frame for runs
        runs_frame = ttk.Frame(self.frame, padding=PADDING)
        runs_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create runs treeview
        columns = ("id", "status", "created_at", "result")
        self.runs_tree = ttk.Treeview(
            runs_frame, columns=columns, show="headings", selectmode="browse"
        )
        
        # Define headings
        self.runs_tree.heading("id", text="ID")
        self.runs_tree.heading("status", text="Status")
        self.runs_tree.heading("created_at", text="Created At")
        self.runs_tree.heading("result", text="Result")
        
        # Define columns
        self.runs_tree.column("id", width=50)
        self.runs_tree.column("status", width=100)
        self.runs_tree.column("created_at", width=150)
        self.runs_tree.column("result", width=400)
        
        # Add scrollbar
        runs_scrollbar = ttk.Scrollbar(
            runs_frame, orient=tk.VERTICAL, command=self.runs_tree.yview
        )
        self.runs_tree.configure(yscrollcommand=runs_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.runs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        runs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create button frame
        button_frame = ttk.Frame(self.frame, padding=PADDING)
        button_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create refresh button
        refresh_button = ttk.Button(
            button_frame, text="Refresh", command=self.load_agent_runs
        )
        refresh_button.pack(side=tk.RIGHT, padx=PADDING)
        
        # Create view logs button
        view_logs_button = ttk.Button(
            button_frame, text="View Logs", command=self._view_logs
        )
        view_logs_button.pack(side=tk.RIGHT, padx=PADDING)
        
        # Set up double-click handler
        self.runs_tree.bind("<Double-1>", self._on_run_double_click)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        self.event_bus.subscribe(EventType.AGENT_RUN_UPDATED, self._handle_agent_run_updated)
        self.event_bus.subscribe(EventType.AGENT_RUN_COMPLETED, self._handle_agent_run_completed)
    
    def load_agent_runs(self):
        """Load agent runs."""
        # Clear runs tree
        for item in self.runs_tree.get_children():
            self.runs_tree.delete(item)
        
        # Get agent runs
        runs = self.controller.get_agent_runs(limit=20)
        
        # Add runs to tree
        for run in runs:
            self.runs_tree.insert(
                "",
                tk.END,
                values=(
                    run.id,
                    run.status or "N/A",
                    run.created_at or "N/A",
                    (run.result or "")[:50] + "..." if run.result else "N/A",
                ),
            )
    
    def clear(self):
        """Clear the agent list."""
        for item in self.runs_tree.get_children():
            self.runs_tree.delete(item)
    
    def _view_logs(self):
        """View logs for the selected run."""
        # Get selected run
        selection = self.runs_tree.selection()
        if not selection:
            self.event_bus.publish(
                Event(
                    EventType.UI_ERROR,
                    {"error": "No run selected"}
                )
            )
            return
        
        # Get run ID
        run_id = int(self.runs_tree.item(selection[0], "values")[0])
        
        # Show agent detail
        self.controller.state.current_agent_run_id = run_id
        
        # Get parent main window
        main_window = self.parent.master
        main_window.show_agent_detail(run_id)
    
    def _on_run_double_click(self, event):
        """
        Handle double-click on a run.
        
        Args:
            event: The event.
        """
        self._view_logs()
    
    def _handle_agent_run_updated(self, event: Event):
        """
        Handle agent run updated event.
        
        Args:
            event: The agent run updated event.
        """
        self.load_agent_runs()
    
    def _handle_agent_run_completed(self, event: Event):
        """
        Handle agent run completed event.
        
        Args:
            event: The agent run completed event.
        """
        self.load_agent_runs()

