"""
Tkinter UI for the Codegen API.

This module contains a Tkinter-based UI for the Codegen API.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from typing import Optional, Dict, Any, List

from codegen.client.sync import CodegenClient
from codegen.config.client_config import ClientConfig
from codegen.models.responses import AgentRunResponse, AgentRunLogResponse
from codegen.exceptions.api_exceptions import CodegenAPIError


class CodegenTkApp:
    """Tkinter application for the Codegen API."""
    
    def __init__(self, root: tk.Tk, config: Optional[ClientConfig] = None):
        """Initialize the Tkinter application.
        
        Args:
            root: The Tkinter root window.
            config: Optional client configuration.
        """
        self.root = root
        self.root.title("Codegen API Client")
        self.root.geometry("800x600")
        
        # Initialize client
        self.config = config or ClientConfig()
        self.client = CodegenClient(self.config)
        
        # Create UI elements
        self._create_ui()
        
        # Set up threading
        self.queue = queue.Queue()
        self.running = False
        self.thread = None
        
        # Set up periodic queue check
        self.root.after(100, self._process_queue)
    
    def _create_ui(self):
        """Create the UI elements."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.agent_tab = ttk.Frame(self.notebook)
        self.runs_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.agent_tab, text="Agent")
        self.notebook.add(self.runs_tab, text="Runs")
        self.notebook.add(self.logs_tab, text="Logs")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Create Agent tab
        self._create_agent_tab()
        
        # Create Runs tab
        self._create_runs_tab()
        
        # Create Logs tab
        self._create_logs_tab()
        
        # Create Settings tab
        self._create_settings_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_agent_tab(self):
        """Create the Agent tab."""
        # Create frame for prompt
        prompt_frame = ttk.LabelFrame(self.agent_tab, text="Agent Prompt", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create prompt text area
        self.prompt_text = scrolledtext.ScrolledText(
            prompt_frame, wrap=tk.WORD, height=10
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create button frame
        button_frame = ttk.Frame(self.agent_tab, padding=10)
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
        result_frame = ttk.LabelFrame(self.agent_tab, text="Result", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create result text area
        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, height=10, state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_runs_tab(self):
        """Create the Runs tab."""
        # Create frame for runs
        runs_frame = ttk.Frame(self.runs_tab, padding=10)
        runs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        button_frame = ttk.Frame(self.runs_tab, padding=10)
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
    
    def _create_logs_tab(self):
        """Create the Logs tab."""
        # Create frame for logs
        logs_frame = ttk.LabelFrame(self.logs_tab, text="Agent Run Logs", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create input frame
        input_frame = ttk.Frame(logs_frame, padding=5)
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
        
        # Create logs text area
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, wrap=tk.WORD, height=20, state=tk.DISABLED
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_settings_tab(self):
        """Create the Settings tab."""
        # Create frame for settings
        settings_frame = ttk.Frame(self.settings_tab, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create API token label and entry
        ttk.Label(settings_frame, text="API Token:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.api_token_entry = ttk.Entry(settings_frame, width=40, show="*")
        self.api_token_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        if self.config.api_token:
            self.api_token_entry.insert(0, self.config.api_token)
        
        # Create organization ID label and entry
        ttk.Label(settings_frame, text="Organization ID:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.org_id_entry = ttk.Entry(settings_frame, width=40)
        self.org_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        if self.config.org_id:
            self.org_id_entry.insert(0, self.config.org_id)
        
        # Create base URL label and entry
        ttk.Label(settings_frame, text="Base URL:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.base_url_entry = ttk.Entry(settings_frame, width=40)
        self.base_url_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.base_url_entry.insert(0, self.config.base_url)
        
        # Create save button
        save_button = ttk.Button(
            settings_frame, text="Save Settings", command=self._save_settings
        )
        save_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=10)
    
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
        self.status_var.set("Running agent...")
        
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
            org_id = self.config.org_id
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
            
            # Refresh runs
            self.queue.put(("refresh_runs", None))
        
        except CodegenAPIError as e:
            self.queue.put(("error", f"API Error: {e.message}"))
        except Exception as e:
            self.queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.running = False
    
    def _refresh_runs(self):
        """Refresh the runs list."""
        # Update status
        self.status_var.set("Refreshing runs...")
        
        # Start thread
        self.thread = threading.Thread(
            target=self._refresh_runs_thread, daemon=True
        )
        self.thread.start()
    
    def _refresh_runs_thread(self):
        """Refresh the runs list in a separate thread."""
        try:
            # Get runs
            org_id = self.config.org_id
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
        selection = self.runs_tree.selection()
        if not selection:
            messagebox.showerror("Error", "No run selected")
            return
        
        # Get run ID
        run_id = self.runs_tree.item(selection[0], "values")[0]
        
        # Set run ID in logs tab
        self.run_id_entry.delete(0, tk.END)
        self.run_id_entry.insert(0, run_id)
        
        # Switch to logs tab
        self.notebook.select(self.logs_tab)
        
        # Fetch logs
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
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set(f"Fetching logs for run {run_id}...")
        
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
            org_id = self.config.org_id
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
        
        # Update config
        self.config.api_token = api_token
        self.config.org_id = org_id
        self.config.base_url = base_url
        
        # Update client
        self.client = CodegenClient(self.config)
        
        # Show success message
        messagebox.showinfo("Success", "Settings saved successfully")
    
    def _process_queue(self):
        """Process the queue of UI updates."""
        try:
            while True:
                message_type, message = self.queue.get_nowait()
                
                if message_type == "status":
                    self.status_var.set(message)
                
                elif message_type == "error":
                    messagebox.showerror("Error", message)
                    self.status_var.set("Ready")
                
                elif message_type == "result":
                    self.result_text.config(state=tk.NORMAL)
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, message)
                    self.result_text.config(state=tk.DISABLED)
                
                elif message_type == "runs":
                    # Clear runs tree
                    for item in self.runs_tree.get_children():
                        self.runs_tree.delete(item)
                    
                    # Add runs to tree
                    for run in message:
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
                
                elif message_type == "log":
                    log: AgentRunLogResponse = message
                    self.logs_text.config(state=tk.NORMAL)
                    self.logs_text.insert(
                        tk.END,
                        f"{log.created_at} - {log.message_type}\n",
                    )
                    
                    if log.thought:
                        self.logs_text.insert(tk.END, f"Thought: {log.thought}\n")
                    
                    if log.tool_name:
                        self.logs_text.insert(
                            tk.END,
                            f"Tool: {log.tool_name}\n"
                            f"Input: {log.tool_input}\n"
                            f"Output: {log.tool_output}\n",
                        )
                    
                    if log.observation:
                        self.logs_text.insert(
                            tk.END, f"Observation: {log.observation}\n"
                        )
                    
                    self.logs_text.insert(tk.END, "\n")
                    self.logs_text.see(tk.END)
                    self.logs_text.config(state=tk.DISABLED)
                
                elif message_type == "refresh_runs":
                    self._refresh_runs()
                
                self.queue.task_done()
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._process_queue)


def run_app():
    """Run the Tkinter application."""
    root = tk.Tk()
    app = CodegenTkApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()

