"""
UI views for the Codegen API.

This module contains view classes for the Codegen API.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
from typing import Optional, Dict, Any, List, Callable

from codegen.client.sync import CodegenClient
from codegen.config.client_config import ClientConfig
from codegen.models.responses import AgentRunResponse, AgentRunLogResponse
from codegen.exceptions.api_exceptions import CodegenAPIError
from codegen.ui.components import LogViewer, RunsTable, SettingsForm


class AgentView(ttk.Frame):
    """View for creating and running agents."""
    
    def __init__(self, parent, client: CodegenClient, status_callback: Callable[[str], None], **kwargs):
        """Initialize the agent view.
        
        Args:
            parent: The parent widget.
            client: The CodegenClient instance.
            status_callback: Callback function for status updates.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store client and callback
        self.client = client
        self.status_callback = status_callback
        
        # Set up threading
        self.queue = queue.Queue()
        self.running = False
        self.thread = None
        
        # Create UI elements
        self._create_ui()
        
        # Set up periodic queue check
        self.after(100, self._process_queue)
    
    def _create_ui(self):
        """Create the UI elements."""
        # Create prompt frame
        prompt_frame = ttk.LabelFrame(self, text="Agent Prompt", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create prompt text area
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=10)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create button frame
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create run button
        run_button = ttk.Button(
            button_frame, text="Run Agent", command=self._run_agent
        )
        run_button.pack(side=tk.RIGHT, padx=5)
        
        # Create clear button
        clear_button = ttk.Button(
            button_frame, text="Clear", command=lambda: self.prompt_text.delete(1.0, tk.END)
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Create result frame
        result_frame = ttk.LabelFrame(self, text="Result", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create result text area
        self.result_text = tk.Text(
            result_frame, wrap=tk.WORD, height=10, state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _run_agent(self):
        """Run an agent with the provided prompt."""
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Prompt cannot be empty")
            return
        
        # Clear result
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_callback("Running agent...")
        
        # Start thread
        self.running = True
        self.thread = threading.Thread(
            target=self._run_agent_thread, args=(prompt,), daemon=True
        )
        self.thread.start()
    
    def _run_agent_thread(self, prompt: str):
        """Run an agent in a separate thread.
        
        Args:
            prompt: The prompt for the agent.
        """
        try:
            # Create agent run
            org_id = self.client.config.org_id
            if not org_id:
                self.queue.put(("error", "Organization ID is not set"))
                return
            
            run = self.client.create_agent_run(org_id=org_id, prompt=prompt)
            self.queue.put(("status", f"Agent run created: {run.id}"))
            
            # Wait for completion
            run = self.client.wait_for_completion(org_id, run.id, timeout=300)
            
            # Update result
            if run.result:
                self.queue.put(("result", run.result))
            else:
                self.queue.put(("result", "No result available"))
            
            # Update status
            self.queue.put(("status", f"Agent run completed: {run.id}"))
        
        except CodegenAPIError as e:
            self.queue.put(("error", f"API Error: {e.message}"))
        except Exception as e:
            self.queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.running = False
    
    def _process_queue(self):
        """Process the queue of UI updates."""
        try:
            while True:
                message_type, message = self.queue.get_nowait()
                
                if message_type == "status":
                    self.status_callback(message)
                
                elif message_type == "error":
                    messagebox.showerror("Error", message)
                    self.status_callback("Ready")
                
                elif message_type == "result":
                    self.result_text.config(state=tk.NORMAL)
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, message)
                    self.result_text.config(state=tk.DISABLED)
                
                self.queue.task_done()
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self._process_queue)


class RunsView(ttk.Frame):
    """View for listing and managing agent runs."""
    
    def __init__(
        self,
        parent,
        client: CodegenClient,
        status_callback: Callable[[str], None],
        on_view_logs: Callable[[int], None],
        **kwargs
    ):
        """Initialize the runs view.
        
        Args:
            parent: The parent widget.
            client: The CodegenClient instance.
            status_callback: Callback function for status updates.
            on_view_logs: Callback function when viewing logs.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store client and callbacks
        self.client = client
        self.status_callback = status_callback
        self.on_view_logs = on_view_logs
        
        # Set up threading
        self.queue = queue.Queue()
        self.thread = None
        
        # Create UI elements
        self._create_ui()
        
        # Set up periodic queue check
        self.after(100, self._process_queue)
        
        # Refresh runs on init
        self._refresh_runs()
    
    def _create_ui(self):
        """Create the UI elements."""
        # Create runs table
        self.runs_table = RunsTable(self)
        self.runs_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create button frame
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create refresh button
        refresh_button = ttk.Button(
            button_frame, text="Refresh", command=self._refresh_runs
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Create view logs button
        view_logs_button = ttk.Button(
            button_frame, text="View Logs", command=self._view_logs
        )
        view_logs_button.pack(side=tk.RIGHT, padx=5)
    
    def _refresh_runs(self):
        """Refresh the runs list."""
        # Update status
        self.status_callback("Refreshing runs...")
        
        # Start thread
        self.thread = threading.Thread(
            target=self._refresh_runs_thread, daemon=True
        )
        self.thread.start()
    
    def _refresh_runs_thread(self):
        """Refresh the runs list in a separate thread."""
        try:
            # Get runs
            org_id = self.client.config.org_id
            if not org_id:
                self.queue.put(("error", "Organization ID is not set"))
                return
            
            runs = self.client.list_agent_runs(org_id=org_id, limit=20)
            
            # Update runs list
            self.queue.put(("runs", runs.items))
            
            # Update status
            self.queue.put(("status", "Runs refreshed"))
        
        except CodegenAPIError as e:
            self.queue.put(("error", f"API Error: {e.message}"))
        except Exception as e:
            self.queue.put(("error", f"Error: {str(e)}"))
    
    def _view_logs(self):
        """View logs for the selected run."""
        # Get selected run
        selection = self.runs_table.tree.selection()
        if not selection:
            messagebox.showerror("Error", "No run selected")
            return
        
        # Get run ID
        run_id = self.runs_table.tree.item(selection[0], "values")[0]
        
        # Call callback
        self.on_view_logs(int(run_id))
    
    def _process_queue(self):
        """Process the queue of UI updates."""
        try:
            while True:
                message_type, message = self.queue.get_nowait()
                
                if message_type == "status":
                    self.status_callback(message)
                
                elif message_type == "error":
                    messagebox.showerror("Error", message)
                    self.status_callback("Ready")
                
                elif message_type == "runs":
                    # Clear runs table
                    self.runs_table.clear()
                    
                    # Add runs to table
                    for run in message:
                        self.runs_table.tree.insert(
                            "",
                            tk.END,
                            values=(
                                run.id,
                                run.status or "N/A",
                                run.created_at or "N/A",
                                (run.result or "")[:50] + "..." if run.result else "N/A",
                            ),
                        )
                
                self.queue.task_done()
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self._process_queue)


class LogsView(ttk.Frame):
    """View for viewing agent run logs."""
    
    def __init__(
        self,
        parent,
        client: CodegenClient,
        status_callback: Callable[[str], None],
        **kwargs
    ):
        """Initialize the logs view.
        
        Args:
            parent: The parent widget.
            client: The CodegenClient instance.
            status_callback: Callback function for status updates.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store client and callback
        self.client = client
        self.status_callback = status_callback
        
        # Set up threading
        self.queue = queue.Queue()
        self.running = False
        self.thread = None
        
        # Create UI elements
        self._create_ui()
        
        # Set up periodic queue check
        self.after(100, self._process_queue)
    
    def _create_ui(self):
        """Create the UI elements."""
        # Create input frame
        input_frame = ttk.Frame(self, padding=5)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create run ID label and entry
        ttk.Label(input_frame, text="Run ID:").pack(side=tk.LEFT, padx=5)
        self.run_id_entry = ttk.Entry(input_frame, width=10)
        self.run_id_entry.pack(side=tk.LEFT, padx=5)
        
        # Create fetch button
        fetch_button = ttk.Button(
            input_frame, text="Fetch Logs", command=self._fetch_logs
        )
        fetch_button.pack(side=tk.LEFT, padx=5)
        
        # Create follow checkbox
        self.follow_var = tk.BooleanVar(value=False)
        follow_check = ttk.Checkbutton(
            input_frame, text="Follow", variable=self.follow_var
        )
        follow_check.pack(side=tk.LEFT, padx=5)
        
        # Create log viewer
        self.log_viewer = LogViewer(self)
        self.log_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def set_run_id(self, run_id: int):
        """Set the run ID and fetch logs.
        
        Args:
            run_id: The agent run ID.
        """
        self.run_id_entry.delete(0, tk.END)
        self.run_id_entry.insert(0, str(run_id))
        self._fetch_logs()
    
    def _fetch_logs(self):
        """Fetch logs for the specified run."""
        # Get run ID
        run_id_str = self.run_id_entry.get().strip()
        if not run_id_str:
            messagebox.showerror("Error", "Run ID cannot be empty")
            return
        
        try:
            run_id = int(run_id_str)
        except ValueError:
            messagebox.showerror("Error", "Run ID must be an integer")
            return
        
        # Clear logs
        self.log_viewer.clear()
        
        # Update status
        self.status_callback(f"Fetching logs for run {run_id}...")
        
        # Start thread
        self.running = True
        self.thread = threading.Thread(
            target=self._fetch_logs_thread, args=(run_id,), daemon=True
        )
        self.thread.start()
    
    def _fetch_logs_thread(self, run_id: int):
        """Fetch logs in a separate thread.
        
        Args:
            run_id: The agent run ID.
        """
        try:
            # Get logs
            org_id = self.client.config.org_id
            if not org_id:
                self.queue.put(("error", "Organization ID is not set"))
                return
            
            logs_seen_count = 0
            follow = self.follow_var.get()
            
            while self.running:
                run_with_logs = self.client.get_agent_run_logs(
                    org_id, run_id, skip=logs_seen_count, limit=100
                )
                
                new_logs = run_with_logs.logs
                if new_logs:
                    for log in new_logs:
                        self.queue.put(("log", log))
                    logs_seen_count += len(new_logs)
                
                status = run_with_logs.status
                self.queue.put(("status", f"Run {run_id} status: {status}"))
                
                if not follow or status not in ["running", "pending", "active"]:
                    break
                
                time.sleep(2)
        
        except CodegenAPIError as e:
            self.queue.put(("error", f"API Error: {e.message}"))
        except Exception as e:
            self.queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.running = False
    
    def _process_queue(self):
        """Process the queue of UI updates."""
        try:
            while True:
                message_type, message = self.queue.get_nowait()
                
                if message_type == "status":
                    self.status_callback(message)
                
                elif message_type == "error":
                    messagebox.showerror("Error", message)
                    self.status_callback("Ready")
                
                elif message_type == "log":
                    self.log_viewer.add_log(message)
                
                self.queue.task_done()
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self._process_queue)


class SettingsView(ttk.Frame):
    """View for editing client settings."""
    
    def __init__(
        self,
        parent,
        client: CodegenClient,
        status_callback: Callable[[str], None],
        on_settings_changed: Callable[[ClientConfig], None],
        **kwargs
    ):
        """Initialize the settings view.
        
        Args:
            parent: The parent widget.
            client: The CodegenClient instance.
            status_callback: Callback function for status updates.
            on_settings_changed: Callback function when settings are changed.
            **kwargs: Additional keyword arguments for the frame.
        """
        super().__init__(parent, **kwargs)
        
        # Store client and callbacks
        self.client = client
        self.status_callback = status_callback
        self.on_settings_changed = on_settings_changed
        
        # Create UI elements
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI elements."""
        # Create settings form
        settings_frame = ttk.Frame(self, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create API token label and entry
        ttk.Label(settings_frame, text="API Token:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.api_token_entry = ttk.Entry(settings_frame, width=40, show="*")
        self.api_token_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        if self.client.config.api_token:
            self.api_token_entry.insert(0, self.client.config.api_token)
        
        # Create organization ID label and entry
        ttk.Label(settings_frame, text="Organization ID:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.org_id_entry = ttk.Entry(settings_frame, width=40)
        self.org_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        if self.client.config.org_id:
            self.org_id_entry.insert(0, self.client.config.org_id)
        
        # Create base URL label and entry
        ttk.Label(settings_frame, text="Base URL:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.base_url_entry = ttk.Entry(settings_frame, width=40)
        self.base_url_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.base_url_entry.insert(0, self.client.config.base_url)
        
        # Create save button
        save_button = ttk.Button(
            settings_frame, text="Save Settings", command=self._save_settings
        )
        save_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=10)
    
    def _save_settings(self):
        """Save the settings."""
        # Get settings
        api_token = self.api_token_entry.get().strip()
        org_id = self.org_id_entry.get().strip()
        base_url = self.base_url_entry.get().strip()
        
        # Validate settings
        if not base_url:
            messagebox.showerror("Error", "Base URL cannot be empty")
            return
        
        # Create new config
        config = ClientConfig(
            api_token=api_token,
            org_id=org_id,
            base_url=base_url,
        )
        
        # Call callback
        self.on_settings_changed(config)
        
        # Show success message
        messagebox.showinfo("Success", "Settings saved successfully")
        self.status_callback("Settings saved")

