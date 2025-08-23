"""
Agent detail frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from codegen_client import CodegenApiError
from codegen_ui.utils.constants import PADDING, STATUS_COLORS, DATE_FORMAT, REFRESH_INTERVAL, AGENT_RUN_STEPS, MAX_ITEMS


class AgentDetailFrame(ttk.Frame):
    """
    Agent detail frame for the Codegen UI.
    
    This frame displays detailed information about an agent run.
    """
    
    def __init__(self, parent: Any, app: Any):
        """
        Initialize the agent detail frame.
        
        Args:
            parent: Parent widget
            app: Application instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create variables
        self.agent_run_id = None
        self.agent_run = None
        self.agent_logs = []
        self.loading = False
        self.after_id = None
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the agent detail frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create header frame
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create back button
        back_button = ttk.Button(
            header_frame, 
            text="← Back", 
            command=self.app.hide_agent_detail
        )
        back_button.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create header
        self.header_label = ttk.Label(
            header_frame, 
            text="Agent Run Details", 
            style="Header.TLabel"
        )
        self.header_label.pack(side=tk.LEFT)
        
        # Create refresh button
        refresh_button = ttk.Button(
            header_frame, 
            text="Refresh", 
            command=self._refresh
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING))
        
        # Create details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Details")
        
        # Create logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Create output tab
        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")
        
        # Create details tab content
        self._create_details_tab()
        
        # Create logs tab content
        self._create_logs_tab()
        
        # Create output tab content
        self._create_output_tab()
        
        # Create action frame
        action_frame = ttk.Frame(container)
        action_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create continue button
        self.continue_button = ttk.Button(
            action_frame, 
            text="Continue Agent Run", 
            command=self._continue_agent_run,
            state=tk.DISABLED
        )
        self.continue_button.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create cancel button
        self.cancel_button = ttk.Button(
            action_frame, 
            text="Cancel Agent Run", 
            command=self._cancel_agent_run,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT)
        
        # Create status label
        self.status_label = ttk.Label(container, text="")
        self.status_label.pack(fill=tk.X, pady=(PADDING, 0))
        
    def _create_details_tab(self):
        """Create the details tab content."""
        # Create details frame
        details_frame = ttk.Frame(self.details_frame, padding=PADDING)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create details grid
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill=tk.BOTH, expand=True)
        
        # Create labels and values
        labels = [
            "ID:", "Status:", "Created At:", "Updated At:", 
            "Model:", "Repository:", "Organization:", "Prompt:"
        ]
        
        self.detail_values = {}
        
        for i, label_text in enumerate(labels):
            # Create label
            label = ttk.Label(details_grid, text=label_text, style="Subheader.TLabel")
            label.grid(row=i, column=0, sticky=tk.W, padx=(0, PADDING), pady=PADDING/2)
            
            # Create value label
            value_var = tk.StringVar(value="Loading...")
            value_label = ttk.Label(details_grid, textvariable=value_var)
            value_label.grid(row=i, column=1, sticky=tk.W, pady=PADDING/2)
            
            # Store value variable
            self.detail_values[label_text.lower().replace(":", "")] = value_var
            
        # Configure grid
        details_grid.columnconfigure(1, weight=1)
        
        # Create progress frame
        progress_frame = ttk.LabelFrame(details_frame, text="Progress")
        progress_frame.pack(fill=tk.X, pady=PADDING)
        
        # Create progress indicators
        self.progress_indicators = {}
        
        for i, step in enumerate(AGENT_RUN_STEPS):
            # Create frame for step
            step_frame = ttk.Frame(progress_frame)
            step_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING/2)
            
            # Create step label
            step_label = ttk.Label(step_frame, text=step.capitalize())
            step_label.pack(side=tk.LEFT)
            
            # Create step indicator
            indicator_var = tk.StringVar(value="○")
            indicator_label = ttk.Label(
                step_frame, 
                textvariable=indicator_var, 
                width=2
            )
            indicator_label.pack(side=tk.RIGHT)
            
            # Store indicator variable
            self.progress_indicators[step] = indicator_var
            
    def _create_logs_tab(self):
        """Create the logs tab content."""
        # Create logs frame
        logs_frame = ttk.Frame(self.logs_frame, padding=PADDING)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create logs text
        self.logs_text = tk.Text(
            logs_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            state=tk.DISABLED
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack logs text and scrollbar
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_output_tab(self):
        """Create the output tab content."""
        # Create output frame
        output_frame = ttk.Frame(self.output_frame, padding=PADDING)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create output text
        self.output_text = tk.Text(
            output_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            state=tk.DISABLED
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack output text and scrollbar
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_agent_run(self, agent_run_id: str):
        """
        Load an agent run from the API.
        
        Args:
            agent_run_id: ID of the agent run to load
        """
        if not self.app.client or not self.app.current_org_id or self.loading:
            return
            
        self.agent_run_id = agent_run_id
        self.loading = True
        self.app.set_status(f"Loading agent run {agent_run_id}...")
        
        # Update header
        self.header_label.config(text=f"Agent Run: {agent_run_id}")
        
        # Cancel existing refresh timer
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        
        def _load_thread():
            try:
                # Get agent run
                self.agent_run = self.app.client.agents.get_agent_run(
                    org_id=self.app.current_org_id,
                    agent_run_id=agent_run_id
                )
                
                # Get agent logs
                self._load_agent_logs()
                
                # Update UI in main thread
                self.after(0, self._update_details)
                
                # Schedule next refresh if agent run is not completed
                if self.agent_run.status in ["pending", "running"]:
                    self.after_id = self.after(
                        REFRESH_INTERVAL["agent_detail"], 
                        lambda: self.load_agent_run(agent_run_id)
                    )
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            finally:
                self.loading = False
        
        # Start load thread
        threading.Thread(target=_load_thread, daemon=True).start()
        
    def _load_agent_logs(self):
        """Load agent logs from the API."""
        try:
            # Get agent logs
            logs = self.app.client.agents_alpha.get_agent_run_logs(
                org_id=self.app.current_org_id,
                agent_run_id=self.agent_run_id
            )
            
            # Store logs
            self.agent_logs = logs.get("logs", [])
            
            # Update UI in main thread
            self.after(0, self._update_logs)
            
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Error loading logs: {str(e)}"))
        
    def _update_details(self):
        """Update the details tab with agent run information."""
        if not self.agent_run:
            return
            
        # Update detail values
        self.detail_values["id"].set(self.agent_run.id)
        self.detail_values["status"].set(self.agent_run.status)
        
        # Format dates
        if self.agent_run.created_at:
            created_at = datetime.fromisoformat(self.agent_run.created_at.replace("Z", "+00:00"))
            self.detail_values["created at"].set(created_at.strftime(DATE_FORMAT))
            
        if self.agent_run.updated_at:
            updated_at = datetime.fromisoformat(self.agent_run.updated_at.replace("Z", "+00:00"))
            self.detail_values["updated at"].set(updated_at.strftime(DATE_FORMAT))
            
        # Set other values
        self.detail_values["model"].set(self.agent_run.model or "default")
        self.detail_values["repository"].set(self.agent_run.repo_id or "N/A")
        self.detail_values["organization"].set(self.app.current_org_id)
        self.detail_values["prompt"].set(self.agent_run.prompt or "")
        
        # Update progress indicators
        for step in self.progress_indicators:
            if step in (self.agent_run.steps or []):
                self.progress_indicators[step].set("●")
            else:
                self.progress_indicators[step].set("○")
                
        # Update output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        if self.agent_run.output:
            self.output_text.insert(tk.END, self.agent_run.output)
        self.output_text.config(state=tk.DISABLED)
        
        # Update buttons
        if self.agent_run.status == "completed":
            self.continue_button.config(state=tk.NORMAL)
        else:
            self.continue_button.config(state=tk.DISABLED)
            
        if self.agent_run.status in ["pending", "running"]:
            self.cancel_button.config(state=tk.NORMAL)
        else:
            self.cancel_button.config(state=tk.DISABLED)
            
        # Update status
        self.status_label.config(text=f"Agent run status: {self.agent_run.status}")
        self.app.set_status(f"Loaded agent run {self.agent_run_id}")
        
    def _update_logs(self):
        """Update the logs tab with agent logs."""
        # Clear logs text
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        
        # Add logs
        for log in self.agent_logs[:MAX_ITEMS["logs"]]:
            # Format timestamp
            timestamp = datetime.fromisoformat(log.get("timestamp", "").replace("Z", "+00:00"))
            timestamp_str = timestamp.strftime(DATE_FORMAT)
            
            # Format log entry
            log_entry = f"[{timestamp_str}] {log.get('level', 'INFO')}: {log.get('message', '')}\n"
            
            # Add to logs text
            self.logs_text.insert(tk.END, log_entry)
            
        self.logs_text.config(state=tk.DISABLED)
        
        # Scroll to end
        self.logs_text.see(tk.END)
        
    def _refresh(self):
        """Refresh the agent run details."""
        if self.agent_run_id:
            self.load_agent_run(self.agent_run_id)
        
    def _continue_agent_run(self):
        """Continue the agent run."""
        if not self.agent_run_id or not self.agent_run or self.agent_run.status != "completed":
            return
            
        if messagebox.askyesno("Continue Agent Run", "Are you sure you want to continue this agent run?"):
            self.app.set_status(f"Continuing agent run {self.agent_run_id}...")
            
            def _continue_thread():
                try:
                    # Continue agent run
                    continued_run = self.app.client.agents.resume_agent_run(
                        org_id=self.app.current_org_id,
                        agent_run_id=self.agent_run_id,
                        prompt="Continue from previous output"
                    )
                    
                    # Load new agent run
                    self.after(0, lambda: self.load_agent_run(continued_run.id))
                    
                except Exception as e:
                    self.after(0, lambda: self._show_error(f"Error continuing agent run: {str(e)}"))
            
            # Start continue thread
            threading.Thread(target=_continue_thread, daemon=True).start()
        
    def _cancel_agent_run(self):
        """Cancel the agent run."""
        if not self.agent_run_id or not self.agent_run or self.agent_run.status not in ["pending", "running"]:
            return
            
        if messagebox.askyesno("Cancel Agent Run", "Are you sure you want to cancel this agent run?"):
            self.app.set_status(f"Cancelling agent run {self.agent_run_id}...")
            
            def _cancel_thread():
                try:
                    # Cancel agent run
                    self.app.client.agents.cancel_agent_run(
                        org_id=self.app.current_org_id,
                        agent_run_id=self.agent_run_id
                    )
                    
                    # Refresh agent run
                    self.after(0, self._refresh)
                    
                except Exception as e:
                    self.after(0, lambda: self._show_error(f"Error cancelling agent run: {str(e)}"))
            
            # Start cancel thread
            threading.Thread(target=_cancel_thread, daemon=True).start()
        
    def _show_error(self, error_message: str):
        """
        Show an error message.
        
        Args:
            error_message: Error message to display
        """
        self.status_label.config(text=f"Error: {error_message}")
        self.app.set_status(f"Error: {error_message}")

