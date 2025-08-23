"""
Tkinter-based UI for Codegen API.
"""

import os
import sys
import threading
import time
from typing import Optional, List, Dict, Any, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    from tkinter.font import Font
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from codegen_api import (
    CodegenClient, 
    ClientConfig, 
    CodegenAPIError, 
    ValidationError,
    AgentRunResponse
)
from codegen.config.client_config import ConfigPresets


class CodegenTkApp:
    """
    Tkinter-based GUI application for Codegen API.
    """
    
    def __init__(self, root=None):
        """
        Initialize the Tkinter application.
        
        Args:
            root: Optional Tkinter root window
        """
        if not TKINTER_AVAILABLE:
            raise ImportError(
                "Tkinter is not available. Please install tkinter to use the GUI."
            )
            
        # Initialize root window
        self.root = root or tk.Tk()
        self.root.title("Codegen API Client")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set up styles
        self.setup_styles()
        
        # Create client
        self.client = None
        self.config = None
        self.initialize_client()
        
        # Create UI components
        self.create_menu()
        self.create_main_frame()
        
        # State variables
        self.current_run_id = None
        self.is_following_logs = False
        self.log_thread = None
        
    def setup_styles(self):
        """Set up ttk styles for the application."""
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
    def initialize_client(self):
        """Initialize the Codegen API client."""
        try:
            # Try to create client with environment variables
            self.config = ClientConfig()
            self.client = CodegenClient(self.config)
        except (ValueError, CodegenAPIError) as e:
            # Will handle this in the UI
            self.config = None
            self.client = None
            
    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def create_main_frame(self):
        """Create the main application frame."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="Not Connected")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Update status
        self.update_connection_status()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_run_tab(notebook)
        self.create_logs_tab(notebook)
        self.create_list_tab(notebook)
        
    def create_run_tab(self, notebook):
        """Create the 'Run Agent' tab."""
        run_frame = ttk.Frame(notebook, padding=10)
        notebook.add(run_frame, text="Run Agent")
        
        # Prompt input
        ttk.Label(run_frame, text="Enter your prompt:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.prompt_text = scrolledtext.ScrolledText(run_frame, height=10, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(run_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.run_button = ttk.Button(button_frame, text="Run Agent", command=self.run_agent)
        self.run_button.pack(side=tk.LEFT)
        
        self.follow_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="Follow logs", variable=self.follow_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Results frame
        ttk.Label(run_frame, text="Results:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.result_text = scrolledtext.ScrolledText(run_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
    def create_logs_tab(self, notebook):
        """Create the 'View Logs' tab."""
        logs_frame = ttk.Frame(notebook, padding=10)
        notebook.add(logs_frame, text="View Logs")
        
        # Run ID input
        input_frame = ttk.Frame(logs_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Run ID:").pack(side=tk.LEFT)
        self.run_id_entry = ttk.Entry(input_frame, width=10)
        self.run_id_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.logs_follow_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Follow logs", variable=self.logs_follow_var).pack(side=tk.LEFT)
        
        ttk.Button(input_frame, text="View Logs", command=self.view_logs).pack(side=tk.LEFT, padx=(10, 0))
        
        # Logs display
        self.logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
    def create_list_tab(self, notebook):
        """Create the 'List Runs' tab."""
        list_frame = ttk.Frame(notebook, padding=10)
        notebook.add(list_frame, text="List Runs")
        
        # Controls frame
        controls_frame = ttk.Frame(list_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(controls_frame, text="Limit:").pack(side=tk.LEFT)
        self.limit_entry = ttk.Entry(controls_frame, width=5)
        self.limit_entry.insert(0, "20")
        self.limit_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(controls_frame, text="Status:").pack(side=tk.LEFT)
        self.status_combo = ttk.Combobox(controls_frame, values=["All", "running", "completed", "failed", "cancelled"])
        self.status_combo.current(0)
        self.status_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_runs).pack(side=tk.LEFT)
        
        # Runs table
        columns = ("id", "status", "created_at", "result", "url")
        self.runs_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.runs_tree.heading("id", text="ID")
        self.runs_tree.heading("status", text="Status")
        self.runs_tree.heading("created_at", text="Created At")
        self.runs_tree.heading("result", text="Result")
        self.runs_tree.heading("url", text="URL")
        
        # Define columns
        self.runs_tree.column("id", width=50)
        self.runs_tree.column("status", width=100)
        self.runs_tree.column("created_at", width=150)
        self.runs_tree.column("result", width=300)
        self.runs_tree.column("url", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.runs_tree.yview)
        self.runs_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.runs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view logs
        self.runs_tree.bind("<Double-1>", self.on_run_double_click)
        
    def update_connection_status(self):
        """Update the connection status display."""
        if self.client and self.config and self.config.api_key and self.config.org_id:
            self.status_label.config(text=f"Connected to {self.config.base_url} (Org: {self.config.org_id})")
        else:
            self.status_label.config(text="Not Connected - Configure API Key and Org ID in Settings")
            
    def show_settings(self):
        """Show the settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key
        ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        api_key_var = tk.StringVar(value=self.config.api_key if self.config else "")
        api_key_entry = ttk.Entry(frame, textvariable=api_key_var, width=40, show="*")
        api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Organization ID
        ttk.Label(frame, text="Organization ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        org_id_var = tk.StringVar(value=self.config.org_id if self.config else "")
        org_id_entry = ttk.Entry(frame, textvariable=org_id_var, width=40)
        org_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Base URL
        ttk.Label(frame, text="Base URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        base_url_var = tk.StringVar(value=self.config.base_url if self.config else ConfigPresets.PRODUCTION["base_url"])
        base_url_entry = ttk.Entry(frame, textvariable=base_url_var, width=40)
        base_url_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Timeout
        ttk.Label(frame, text="Timeout (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        timeout_var = tk.IntVar(value=self.config.timeout if self.config else ConfigPresets.PRODUCTION["timeout"])
        timeout_entry = ttk.Entry(frame, textvariable=timeout_var, width=10)
        timeout_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Presets
        ttk.Label(frame, text="Presets:").grid(row=4, column=0, sticky=tk.W, pady=5)
        preset_frame = ttk.Frame(frame)
        preset_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(preset_frame, text="Production", 
                  command=lambda: self.apply_preset(base_url_var, timeout_var, "PRODUCTION")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Development", 
                  command=lambda: self.apply_preset(base_url_var, timeout_var, "DEVELOPMENT")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Local", 
                  command=lambda: self.apply_preset(base_url_var, timeout_var, "LOCAL")).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", 
                  command=lambda: self.save_settings(
                      api_key_var.get(), 
                      org_id_var.get(), 
                      base_url_var.get(), 
                      timeout_var.get(),
                      settings_window
                  )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
                  
    def apply_preset(self, base_url_var, timeout_var, preset_name):
        """Apply a configuration preset."""
        preset = getattr(ConfigPresets, preset_name)
        base_url_var.set(preset["base_url"])
        timeout_var.set(preset["timeout"])
        
    def save_settings(self, api_key, org_id, base_url, timeout, window):
        """Save the settings and initialize the client."""
        try:
            self.config = ClientConfig(
                api_key=api_key,
                org_id=org_id,
                base_url=base_url,
                timeout=timeout
            )
            self.client = CodegenClient(self.config)
            self.update_connection_status()
            window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize client: {str(e)}")
            
    def show_about(self):
        """Show the about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Codegen API Client")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.grab_set()
        
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Codegen API Client", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(frame, text="A GUI client for the Codegen Agent API").pack(pady=(0, 20))
        
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X)
        
        ttk.Label(version_frame, text="Version:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(version_frame, text="0.1.0").grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Button(frame, text="Close", command=about_window.destroy).pack(pady=(20, 0))
        
    def run_agent(self):
        """Run a new agent with the provided prompt."""
        if not self.client:
            messagebox.showerror("Error", "Not connected. Please configure API key and organization ID in settings.")
            return
            
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Prompt cannot be empty.")
            return
            
        try:
            # Clear result text
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Starting agent run...\n")
            self.result_text.config(state=tk.DISABLED)
            
            # Create agent run
            org_id_int = int(self.config.org_id)
            run = self.client.create_agent_run(org_id=org_id_int, prompt=prompt)
            
            # Update result text
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"Agent run created successfully! Run ID: {run.id}\n")
            if run.web_url:
                self.result_text.insert(tk.END, f"View online: {run.web_url}\n")
            self.result_text.config(state=tk.DISABLED)
            
            # Follow logs if selected
            if self.follow_var.get():
                self.current_run_id = run.id
                self.start_log_streaming(run.id)
                
        except Exception as e:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")
            self.result_text.config(state=tk.DISABLED)
            
    def view_logs(self):
        """View logs for a specific run ID."""
        if not self.client:
            messagebox.showerror("Error", "Not connected. Please configure API key and organization ID in settings.")
            return
            
        try:
            run_id = int(self.run_id_entry.get().strip())
            self.current_run_id = run_id
            
            # Clear logs text
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.delete("1.0", tk.END)
            self.logs_text.insert(tk.END, f"Fetching logs for run {run_id}...\n")
            self.logs_text.config(state=tk.DISABLED)
            
            # Start log streaming
            self.start_log_streaming(run_id, target=self.logs_text)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid run ID. Please enter a valid integer.")
        except Exception as e:
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.insert(tk.END, f"Error: {str(e)}\n")
            self.logs_text.config(state=tk.DISABLED)
            
    def refresh_runs(self):
        """Refresh the list of runs."""
        if not self.client:
            messagebox.showerror("Error", "Not connected. Please configure API key and organization ID in settings.")
            return
            
        try:
            # Get parameters
            limit = int(self.limit_entry.get().strip())
            status = self.status_combo.get()
            if status == "All":
                status = None
                
            # Clear existing items
            for item in self.runs_tree.get_children():
                self.runs_tree.delete(item)
                
            # Fetch runs
            org_id_int = int(self.config.org_id)
            runs = self.client.list_agent_runs(org_id=org_id_int, limit=limit, source_type=status)
            
            # Add runs to tree
            for run in runs.items:
                self.runs_tree.insert(
                    "", 
                    tk.END, 
                    values=(
                        run.id,
                        run.status or "N/A",
                        run.created_at or "N/A",
                        (run.result or "")[:50] + "..." if run.result and len(run.result) > 50 else (run.result or "N/A"),
                        run.web_url or "N/A"
                    )
                )
                
        except ValueError:
            messagebox.showerror("Error", "Invalid limit. Please enter a valid integer.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch runs: {str(e)}")
            
    def on_run_double_click(self, event):
        """Handle double-click on a run in the list."""
        item = self.runs_tree.selection()[0]
        run_id = self.runs_tree.item(item, "values")[0]
        
        # Set the run ID in the logs tab
        self.run_id_entry.delete(0, tk.END)
        self.run_id_entry.insert(0, run_id)
        
        # Switch to logs tab
        self.root.nametowidget(".!frame.!notebook").select(1)  # Select logs tab
        
        # View logs
        self.view_logs()
        
    def start_log_streaming(self, run_id, target=None):
        """Start streaming logs for a run."""
        # Stop any existing log thread
        self.stop_log_streaming()
        
        # Set target text widget
        target = target or self.result_text
        
        # Start new log thread
        self.is_following_logs = True
        self.log_thread = threading.Thread(
            target=self.stream_logs_thread,
            args=(run_id, target),
            daemon=True
        )
        self.log_thread.start()
        
    def stop_log_streaming(self):
        """Stop streaming logs."""
        self.is_following_logs = False
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=1.0)
            
    def stream_logs_thread(self, run_id, target_widget):
        """Thread function for streaming logs."""
        if not self.client:
            return
            
        logs_seen_count = 0
        follow = self.logs_follow_var.get()
        
        try:
            while self.is_following_logs:
                try:
                    org_id_int = int(self.config.org_id)
                    run_with_logs = self.client.get_agent_run_logs(
                        org_id_int, run_id, limit=100, skip=logs_seen_count
                    )
                    
                    new_logs = run_with_logs.logs
                    if new_logs:
                        for log in new_logs:
                            log_text = self.format_log_entry(log.__dict__)
                            self.update_text_widget(target_widget, log_text + "\n")
                        logs_seen_count += len(new_logs)
                        
                    status = run_with_logs.status.upper() if run_with_logs.status else "UNKNOWN"
                    self.update_text_widget(
                        target_widget, 
                        f"\n--- Run ID: {run_id} | Status: {status} ---\n",
                        append=False
                    )
                    
                    if not follow or status not in ["RUNNING", "PENDING", "ACTIVE"]:
                        break
                        
                    time.sleep(2)
                    
                except Exception as e:
                    self.update_text_widget(target_widget, f"Error fetching logs: {str(e)}\n")
                    break
                    
        finally:
            self.is_following_logs = False
            
    def update_text_widget(self, widget, text, append=True):
        """Update a text widget from a background thread."""
        self.root.after(0, lambda: self._update_text_widget_impl(widget, text, append))
        
    def _update_text_widget_impl(self, widget, text, append):
        """Implementation of text widget update (called on main thread)."""
        widget.config(state=tk.NORMAL)
        if not append:
            # Find the last status line and replace it
            content = widget.get("1.0", tk.END)
            last_status_pos = content.rfind("--- Run ID:")
            if last_status_pos >= 0:
                end_pos = content.find("\n", last_status_pos)
                if end_pos >= 0:
                    widget.delete(f"1.0 + {last_status_pos}c", f"1.0 + {end_pos}c")
                    widget.insert(f"1.0 + {last_status_pos}c", text.strip())
            else:
                widget.insert(tk.END, text)
        else:
            widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)
        
    def format_log_entry(self, log: Dict[str, Any]) -> str:
        """Format a log entry for display."""
        log_type = log.get("message_type", "LOG")
        created_at = log.get("created_at", "")
        output = f"{created_at} {log_type:<15}"
        
        if thought := log.get("thought"):
            output += f" 🤔 {thought}"
        if tool_name := log.get("tool_name"):
            output += f"\n  => Tool: {tool_name} | Input: {log.get('tool_input')}"
        if observation := log.get("observation"):
            if log_type == "FINAL_ANSWER":
                return f"FINAL ANSWER: {observation}"
            if log_type == "ERROR":
                return f"ERROR: {observation}"
        return output
        
    def run(self):
        """Run the application."""
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing."""
        self.stop_log_streaming()
        self.root.destroy()

