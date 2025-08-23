"""
Agent list frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from codegen_client import CodegenApiError
from codegen_ui.utils.constants import PADDING, STATUS_COLORS, DATE_FORMAT, REFRESH_INTERVAL, MAX_ITEMS


class AgentListFrame(ttk.Frame):
    """
    Agent list frame for the Codegen UI.
    
    This frame displays a list of agent runs and allows users to manage them.
    """
    
    def __init__(self, parent: Any, app: Any):
        """
        Initialize the agent list frame.
        
        Args:
            parent: Parent widget
            app: Application instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create variables
        self.agent_runs = []
        self.loading = False
        self.after_id = None
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the agent list frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
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
            command=self.load_agent_runs
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create filter frame
        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create status filter
        status_label = ttk.Label(filter_frame, text="Status:")
        status_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        self.status_var = tk.StringVar(value="all")
        status_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.status_var,
            values=["all", "pending", "running", "completed", "failed", "cancelled"],
            width=10,
            state="readonly"
        )
        status_combobox.pack(side=tk.LEFT, padx=(0, PADDING*2))
        status_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_agent_runs())
        
        # Create search entry
        search_label = ttk.Label(filter_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, PADDING))
        search_entry.bind("<Return>", lambda e: self.load_agent_runs())
        
        search_button = ttk.Button(
            filter_frame, 
            text="Search", 
            command=self.load_agent_runs
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
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind treeview events
        self.treeview.bind("<Double-1>", self._on_treeview_double_click)
        self.treeview.bind("<Return>", self._on_treeview_double_click)
        
        # Create status label
        self.status_label = ttk.Label(container, text="")
        self.status_label.pack(fill=tk.X, pady=(PADDING, 0))
        
    def load_agent_runs(self):
        """Load agent runs from the API."""
        if not self.app.client or not self.app.current_org_id or self.loading:
            return
            
        self.loading = True
        self.app.set_status("Loading agent runs...")
        
        # Cancel existing refresh timer
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        
        def _load_thread():
            try:
                # Get filter values
                status_filter = self.status_var.get()
                search_filter = self.search_var.get().strip()
                
                # Build query parameters
                params = {
                    "limit": MAX_ITEMS["agent_list"],
                }
                
                if status_filter != "all":
                    params["status"] = status_filter
                    
                # Get agent runs
                agent_runs = self.app.client.agents.get_agent_runs(
                    org_id=self.app.current_org_id,
                    **params
                )
                
                # Filter by search if needed
                if search_filter:
                    search_filter = search_filter.lower()
                    self.agent_runs = [
                        run for run in agent_runs.items
                        if (
                            search_filter in (run.prompt or "").lower() or
                            search_filter in (run.id or "").lower() or
                            search_filter in (run.model or "").lower()
                        )
                    ]
                else:
                    self.agent_runs = agent_runs.items
                
                # Update UI in main thread
                self.after(0, self._update_treeview)
                
                # Schedule next refresh
                self.after_id = self.after(
                    REFRESH_INTERVAL["agent_list"], 
                    self.load_agent_runs
                )
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            finally:
                self.loading = False
        
        # Start load thread
        threading.Thread(target=_load_thread, daemon=True).start()
        
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
                
        # Update status label
        self.status_label.config(text=f"Showing {len(self.agent_runs)} agent runs")
        
        # Update app status
        self.app.set_status(f"Loaded {len(self.agent_runs)} agent runs")
        
    def _show_error(self, error_message: str):
        """
        Show an error message.
        
        Args:
            error_message: Error message to display
        """
        self.status_label.config(text=f"Error: {error_message}")
        self.app.set_status(f"Error loading agent runs: {error_message}")
        
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
        
        # Show agent detail
        self.app.show_agent_detail(agent_run_id)
        
    def clear(self):
        """Clear the agent list."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Clear variables
        self.agent_runs = []
        self.status_label.config(text="")
        
        # Cancel refresh timer
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

