"""
Agent list frame for the Enhanced Codegen UI.

This module provides the agent list frame for the Enhanced Codegen UI,
displaying a list of agent runs and allowing users to filter and search them.
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType
from enhanced_codegen_ui.utils.constants import PADDING, STATUS_COLORS, DATE_FORMAT, REFRESH_INTERVAL


class AgentListFrame(ttk.Frame):
    """
    Agent list frame for the Enhanced Codegen UI.
    
    This class provides an agent list frame for the Enhanced Codegen UI,
    displaying a list of agent runs and allowing users to filter and search them.
    """
    
    def __init__(self, parent: Any, controller: Controller):
        """
        Initialize the agent list frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.logger = logging.getLogger(__name__)
        
        # Create variables
        self.agent_runs = []
        self.status_var = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.status_text_var = tk.StringVar()
        self.after_id = None
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _create_widgets(self):
        """Create the agent list frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create header
        header = ttk.Label(
            header_frame,
            text="Agent Runs",
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
        
        # Create status filter
        status_label = ttk.Label(filter_frame, text="Status:")
        status_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        status_combobox = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["all", "pending", "running", "completed", "failed", "cancelled"],
            width=10,
            state="readonly"
        )
        status_combobox.pack(side=tk.LEFT, padx=(0, PADDING*2))
        status_combobox.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        
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
        columns = ("id", "prompt", "status", "created_at", "model")
        self.treeview = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.treeview.heading("id", text="ID")
        self.treeview.heading("prompt", text="Prompt")
        self.treeview.heading("status", text="Status")
        self.treeview.heading("created_at", text="Created At")
        self.treeview.heading("model", text="Model")
        
        self.treeview.column("id", width=80, anchor=tk.W)
        self.treeview.column("prompt", width=400, anchor=tk.W)
        self.treeview.column("status", width=100, anchor=tk.CENTER)
        self.treeview.column("created_at", width=150, anchor=tk.W)
        self.treeview.column("model", width=100, anchor=tk.W)
        
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
            textvariable=self.status_text_var
        )
        status_label.pack(side=tk.LEFT)
        
        # Bind treeview events
        self.treeview.bind("<Double-1>", self._on_treeview_double_click)
        self.treeview.bind("<Return>", self._on_treeview_double_click)
        
    def _register_event_handlers(self):
        """Register event handlers."""
        # Register agent run events
        self.controller.event_bus.subscribe(
            EventType.AGENT_RUNS_LOADED,
            self._on_agent_runs_loaded
        )
        
        self.controller.event_bus.subscribe(
            EventType.AGENT_RUN_SUCCEEDED,
            lambda e: self._refresh()
        )
        
        self.controller.event_bus.subscribe(
            EventType.AGENT_RUN_CANCEL_SUCCEEDED,
            lambda e: self._refresh()
        )
        
        self.controller.event_bus.subscribe(
            EventType.LOAD_ERROR,
            self._on_load_error
        )
        
    def _refresh(self):
        """Refresh the agent list."""
        # Cancel existing refresh timer
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            
        # Get filter values
        status_filter = self.status_var.get()
        status = status_filter if status_filter != "all" else None
        
        # Publish refresh requested event
        self.controller.event_bus.publish(
            Event(EventType.REFRESH_REQUESTED, {"type": "agent_runs", "status": status})
        )
        
        # Schedule next refresh
        self.after_id = self.after(
            REFRESH_INTERVAL["agent_list"],
            self._refresh
        )
        
    def _on_agent_runs_loaded(self, event: Event):
        """
        Handle agent runs loaded event.
        
        Args:
            event: Event object with agent_runs in data
        """
        agent_runs = event.data.get("agent_runs", [])
        
        # Filter by search if needed
        search_filter = self.search_var.get().strip().lower()
        if search_filter:
            agent_runs = [
                run for run in agent_runs
                if (
                    search_filter in (run.prompt or "").lower() or
                    search_filter in (run.id or "").lower() or
                    search_filter in (run.model or "").lower()
                )
            ]
            
        # Store agent runs
        self.agent_runs = agent_runs
        
        # Update treeview
        self._update_treeview()
        
    def _on_load_error(self, event: Event):
        """
        Handle load error event.
        
        Args:
            event: Event object with error and type in data
        """
        error_type = event.data.get("type")
        if error_type == "agent_runs":
            error = event.data.get("error", "Error loading agent runs")
            self.status_text_var.set(f"Error: {error}")
            
    def _update_treeview(self):
        """Update the treeview with agent runs."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Add agent runs to treeview
        for run in self.agent_runs:
            # Format created_at
            created_at = datetime.fromisoformat(run.created_at.replace("Z", "+00:00"))
            created_at_str = created_at.strftime(DATE_FORMAT)
            
            # Add to treeview
            item_id = self.treeview.insert(
                "",
                tk.END,
                values=(
                    run.id,
                    run.prompt[:50] + "..." if run.prompt and len(run.prompt) > 50 else run.prompt,
                    run.status,
                    created_at_str,
                    run.model or "default"
                )
            )
            
            # Set tag for status color
            if run.status in STATUS_COLORS:
                self.treeview.tag_configure(run.status, foreground=STATUS_COLORS[run.status])
                self.treeview.item(item_id, tags=(run.status,))
                
        # Update status text
        self.status_text_var.set(f"Showing {len(self.agent_runs)} agent runs")
        
    def _on_treeview_double_click(self, event):
        """
        Handle double click on treeview.
        
        Args:
            event: Event object
        """
        # Get selected item
        selection = self.treeview.selection()
        if not selection:
            return
            
        # Get agent run ID
        item = self.treeview.item(selection[0])
        agent_run_id = item["values"][0]
        
        # Publish view agent run requested event
        self.controller.event_bus.publish(
            Event(EventType.VIEW_AGENT_RUN_REQUESTED, {"agent_run_id": agent_run_id})
        )
        
    def pack(self, **kwargs):
        """
        Pack the frame and refresh the agent list.
        
        Args:
            **kwargs: Pack options
        """
        super().pack(**kwargs)
        self._refresh()

