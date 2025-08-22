"""
Create agent frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Any, Dict, List, Optional

from codegen_client import CodegenApiError
from codegen_ui.utils.constants import PADDING, DEFAULT_MODELS


class CreateAgentFrame(ttk.Frame):
    """
    Create agent frame for the Codegen UI.
    
    This frame allows users to create new agent runs.
    """
    
    def __init__(self, parent: Any, app: Any):
        """
        Initialize the create agent frame.
        
        Args:
            parent: Parent widget
            app: Application instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create variables
        self.repositories = []
        self.models = DEFAULT_MODELS
        self.loading = False
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the create agent frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create header
        header = ttk.Label(
            container, 
            text="Create Agent Run", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, PADDING*2))
        
        # Create form frame
        form_frame = ttk.Frame(container)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create repository selection
        repo_label = ttk.Label(form_frame, text="Repository:")
        repo_label.grid(row=0, column=0, sticky=tk.W, pady=PADDING)
        
        self.repo_var = tk.StringVar()
        self.repo_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.repo_var,
            width=40,
            state="readonly"
        )
        self.repo_combobox.grid(row=0, column=1, sticky=tk.W, pady=PADDING)
        
        # Create model selection
        model_label = ttk.Label(form_frame, text="Model:")
        model_label.grid(row=1, column=0, sticky=tk.W, pady=PADDING)
        
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.model_var,
            values=self.models,
            width=40,
            state="readonly"
        )
        self.model_combobox.grid(row=1, column=1, sticky=tk.W, pady=PADDING)
        
        # Create temperature slider
        temp_label = ttk.Label(form_frame, text="Temperature:")
        temp_label.grid(row=2, column=0, sticky=tk.W, pady=PADDING)
        
        temp_frame = ttk.Frame(form_frame)
        temp_frame.grid(row=2, column=1, sticky=tk.W, pady=PADDING)
        
        self.temp_var = tk.DoubleVar(value=0.7)
        temp_slider = ttk.Scale(
            temp_frame, 
            from_=0.0, 
            to=1.0, 
            orient=tk.HORIZONTAL, 
            variable=self.temp_var,
            length=200
        )
        temp_slider.pack(side=tk.LEFT)
        
        temp_value_label = ttk.Label(temp_frame, textvariable=self.temp_var, width=4)
        temp_value_label.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create prompt entry
        prompt_label = ttk.Label(form_frame, text="Prompt:")
        prompt_label.grid(row=3, column=0, sticky=tk.NW, pady=PADDING)
        
        self.prompt_text = tk.Text(form_frame, width=50, height=10)
        self.prompt_text.grid(row=3, column=1, sticky=tk.W, pady=PADDING)
        
        # Create metadata entry
        metadata_label = ttk.Label(form_frame, text="Metadata (JSON):")
        metadata_label.grid(row=4, column=0, sticky=tk.NW, pady=PADDING)
        
        self.metadata_text = tk.Text(form_frame, width=50, height=5)
        self.metadata_text.grid(row=4, column=1, sticky=tk.W, pady=PADDING)
        self.metadata_text.insert(tk.END, "{}")
        
        # Create buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=1, sticky=tk.E, pady=PADDING*2)
        
        clear_button = ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_form
        )
        clear_button.pack(side=tk.LEFT, padx=(0, PADDING))
        
        create_button = ttk.Button(
            button_frame, 
            text="Create Agent Run", 
            command=self._create_agent_run
        )
        create_button.pack(side=tk.LEFT)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create status label
        self.status_label = ttk.Label(container, text="")
        self.status_label.pack(fill=tk.X, pady=(PADDING, 0))
        
    def load_models(self):
        """Load available models."""
        # For now, just use the default models
        # In a real implementation, this would fetch models from the API
        self.model_combobox.config(values=self.models)
        if self.models:
            self.model_var.set(self.models[0])
            
        # Load repositories
        self.load_repositories()
        
    def load_repositories(self):
        """Load repositories from the API."""
        if not self.app.client or not self.app.current_org_id or self.loading:
            return
            
        self.loading = True
        self.app.set_status("Loading repositories...")
        
        def _load_thread():
            try:
                # Get repositories
                repositories = self.app.client.repositories.get_repositories(
                    org_id=self.app.current_org_id
                )
                
                # Store repositories
                self.repositories = repositories.items
                
                # Update UI in main thread
                self.after(0, self._update_repositories)
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            finally:
                self.loading = False
        
        # Start load thread
        threading.Thread(target=_load_thread, daemon=True).start()
        
    def _update_repositories(self):
        """Update the repository combobox with repositories."""
        # Create repository values
        repo_values = [f"{repo.name} ({repo.id})" for repo in self.repositories]
        
        # Update combobox
        self.repo_combobox.config(values=repo_values)
        
        # Select first repository if available
        if repo_values:
            self.repo_var.set(repo_values[0])
            
        # Update status
        self.app.set_status(f"Loaded {len(self.repositories)} repositories")
        
    def _create_agent_run(self):
        """Create a new agent run."""
        if not self.app.client or not self.app.current_org_id:
            self._show_error("Not logged in")
            return
            
        # Get form values
        repo_value = self.repo_var.get()
        model = self.model_var.get()
        temperature = self.temp_var.get()
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        metadata_str = self.metadata_text.get(1.0, tk.END).strip()
        
        # Validate form
        if not prompt:
            self._show_error("Prompt is required")
            return
            
        # Parse repository ID
        repo_id = None
        if repo_value:
            try:
                repo_id = int(repo_value.split("(")[-1].split(")")[0])
            except (ValueError, IndexError):
                self._show_error("Invalid repository selection")
                return
                
        # Parse metadata
        metadata = None
        if metadata_str:
            try:
                metadata = json.loads(metadata_str)
            except json.JSONDecodeError:
                self._show_error("Invalid metadata JSON")
                return
                
        # Create agent run
        self.app.set_status("Creating agent run...")
        
        def _create_thread():
            try:
                # Create agent run
                agent_run = self.app.client.agents.create_agent_run(
                    org_id=self.app.current_org_id,
                    prompt=prompt,
                    repo_id=repo_id,
                    model=model if model else None,
                    temperature=temperature,
                    metadata=metadata
                )
                
                # Show success message
                self.after(0, lambda: self._show_success(agent_run.id))
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
        
        # Start create thread
        threading.Thread(target=_create_thread, daemon=True).start()
        
    def _show_success(self, agent_run_id: str):
        """
        Show a success message and offer to view the agent run.
        
        Args:
            agent_run_id: ID of the created agent run
        """
        self.status_label.config(text=f"Created agent run {agent_run_id}")
        self.app.set_status(f"Created agent run {agent_run_id}")
        
        if messagebox.askyesno("Agent Run Created", f"Agent run {agent_run_id} created successfully. View it now?"):
            self.app.show_agent_detail(agent_run_id)
        
    def _show_error(self, error_message: str):
        """
        Show an error message.
        
        Args:
            error_message: Error message to display
        """
        self.status_label.config(text=f"Error: {error_message}")
        self.app.set_status(f"Error creating agent run: {error_message}")
        
    def clear_form(self):
        """Clear the form."""
        self.prompt_text.delete(1.0, tk.END)
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(tk.END, "{}")
        self.temp_var.set(0.7)
        
    def clear(self):
        """Clear the form and reset variables."""
        self.clear_form()
        self.repositories = []
        self.repo_combobox.config(values=[])

