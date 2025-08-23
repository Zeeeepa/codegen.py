"""
UI components for the Codegen API.

This module contains reusable UI components for the Codegen API.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable, Dict, Any, List

from codegen.models.responses import AgentRunLogResponse


class LogViewer(ttk.Frame):
    """A component for viewing agent run logs."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the log viewer.
        
        Args:
            parent: The parent widget.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Create text area
        self.text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=20, state=tk.DISABLED
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def clear(self):
        """Clear the log viewer."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
    
    def add_log(self, log: AgentRunLogResponse):
        """Add a log entry to the viewer.
        
        Args:
            log: The log entry to add.
        """
        self.text.config(state=tk.NORMAL)
        
        # Add timestamp and message type
        self.text.insert(
            tk.END,
            f"{log.created_at} - {log.message_type}\n",
        )
        
        # Add thought if available
        if log.thought:
            self.text.insert(tk.END, f"Thought: {log.thought}\n")
        
        # Add tool information if available
        if log.tool_name:
            self.text.insert(
                tk.END,
                f"Tool: {log.tool_name}\n"
                f"Input: {log.tool_input}\n"
                f"Output: {log.tool_output}\n",
            )
        
        # Add observation if available
        if log.observation:
            self.text.insert(
                tk.END, f"Observation: {log.observation}\n"
            )
        
        # Add separator
        self.text.insert(tk.END, "\n")
        
        # Scroll to end
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)


class RunsTable(ttk.Frame):
    """A component for displaying agent runs."""
    
    def __init__(self, parent, on_select: Optional[Callable[[int], None]] = None, **kwargs):
        """Initialize the runs table.
        
        Args:
            parent: The parent widget.
            on_select: Callback function when a run is selected.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store callback
        self.on_select = on_select
        
        # Create treeview
        columns = ("id", "status", "created_at", "result")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", selectmode="browse"
        )
        
        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("status", text="Status")
        self.tree.heading("created_at", text="Created At")
        self.tree.heading("result", text="Result")
        
        # Define columns
        self.tree.column("id", width=50)
        self.tree.column("status", width=100)
        self.tree.column("created_at", width=150)
        self.tree.column("result", width=400)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
    
    def clear(self):
        """Clear the runs table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_runs(self, runs: List[Dict[str, Any]]):
        """Add runs to the table.
        
        Args:
            runs: List of run dictionaries.
        """
        for run in runs:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    run["id"],
                    run.get("status", "N/A"),
                    run.get("created_at", "N/A"),
                    (run.get("result", "") or "")[:50] + "..." if run.get("result") else "N/A",
                ),
            )
    
    def _on_select(self, event):
        """Handle selection event.
        
        Args:
            event: The selection event.
        """
        if self.on_select:
            selection = self.tree.selection()
            if selection:
                run_id = self.tree.item(selection[0], "values")[0]
                self.on_select(run_id)


class SettingsForm(ttk.Frame):
    """A component for editing client settings."""
    
    def __init__(self, parent, config: Dict[str, Any], on_save: Callable[[Dict[str, Any]], None], **kwargs):
        """Initialize the settings form.
        
        Args:
            parent: The parent widget.
            config: The current configuration.
            on_save: Callback function when settings are saved.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store callback
        self.on_save = on_save
        
        # Create form fields
        ttk.Label(self, text="API Token:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.api_token_entry = ttk.Entry(self, width=40, show="*")
        self.api_token_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        if config.get("api_token"):
            self.api_token_entry.insert(0, config["api_token"])
        
        ttk.Label(self, text="Organization ID:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.org_id_entry = ttk.Entry(self, width=40)
        self.org_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        if config.get("org_id"):
            self.org_id_entry.insert(0, config["org_id"])
        
        ttk.Label(self, text="Base URL:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.base_url_entry = ttk.Entry(self, width=40)
        self.base_url_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.base_url_entry.insert(0, config.get("base_url", "https://api.codegen.com/v1"))
        
        # Create save button
        save_button = ttk.Button(
            self, text="Save Settings", command=self._save_settings
        )
        save_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=10)
    
    def _save_settings(self):
        """Save the settings."""
        # Get settings
        config = {
            "api_token": self.api_token_entry.get().strip(),
            "org_id": self.org_id_entry.get().strip(),
            "base_url": self.base_url_entry.get().strip(),
        }
        
        # Call callback
        self.on_save(config)

