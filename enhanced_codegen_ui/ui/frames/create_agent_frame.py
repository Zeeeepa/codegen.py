"""
Create agent frame for the Enhanced Codegen UI.

This module provides the create agent frame for the Enhanced Codegen UI,
allowing users to create new agent runs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import json
from typing import Any, Dict, List, Optional

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType
from enhanced_codegen_ui.utils.constants import PADDING, DEFAULT_MODELS


class CreateAgentFrame(ttk.Frame):
    """
    Create agent frame for the Enhanced Codegen UI.
    
    This class provides a create agent frame for the Enhanced Codegen UI,
    allowing users to create new agent runs.
    """
    
    def __init__(self, parent: Any, controller: Controller):
        """
        Initialize the create agent frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.logger = logging.getLogger(__name__)
        
        # Create variables
        self.repositories = []
        self.models = []
        self.repo_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.temp_var = tk.DoubleVar(value=0.7)
        self.status_var = tk.StringVar()
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _create_widgets(self):
        """Create the create agent frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
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
        
        self.model_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.model_var,
            width=40,
            state="readonly"
        )
        self.model_combobox.grid(row=1, column=1, sticky=tk.W, pady=PADDING)
        
        # Create temperature slider
        temp_label = ttk.Label(form_frame, text="Temperature:")
        temp_label.grid(row=2, column=0, sticky=tk.W, pady=PADDING)
        
        temp_frame = ttk.Frame(form_frame)
        temp_frame.grid(row=2, column=1, sticky=tk.W, pady=PADDING)
        
        temp_slider = ttk.Scale(
            temp_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.temp_var,
            length=200
        )
        temp_slider.pack(side=tk.LEFT)
        
        temp_value_label = ttk.Label(
            temp_frame,
            textvariable=self.temp_var,
            width=4
        )
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
            command=self._clear_form
        )
        clear_button.pack(side=tk.LEFT, padx=(0, PADDING))
        
        create_button = ttk.Button(
            button_frame,
            text="Create Agent Run",
            command=self._on_create,
            style="Primary.TButton"
        )
        create_button.pack(side=tk.LEFT)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
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
        
        # Register model events
        self.controller.event_bus.subscribe(
            EventType.MODELS_LOADED,
            self._on_models_loaded
        )
        
        # Register agent run events
        self.controller.event_bus.subscribe(
            EventType.AGENT_RUN_SUCCEEDED,
            self._on_agent_run_succeeded
        )
        
        self.controller.event_bus.subscribe(
            EventType.AGENT_RUN_FAILED,
            self._on_agent_run_failed
        )
        
        # Register load error events
        self.controller.event_bus.subscribe(
            EventType.LOAD_ERROR,
            self._on_load_error
        )
        
    def _on_repositories_loaded(self, event: Event):
        """
        Handle repositories loaded event.
        
        Args:
            event: Event object with repositories in data
        """
        repositories = event.data.get("repositories", [])
        
        # Store repositories
        self.repositories = repositories
        
        # Update repository combobox
        self._update_repository_combobox()
        
    def _on_models_loaded(self, event: Event):
        """
        Handle models loaded event.
        
        Args:
            event: Event object with models in data
        """
        models = event.data.get("models", DEFAULT_MODELS)
        
        # Store models
        self.models = models
        
        # Update model combobox
        self._update_model_combobox()
        
    def _on_agent_run_succeeded(self, event: Event):
        """
        Handle agent run succeeded event.
        
        Args:
            event: Event object with agent_run in data
        """
        agent_run = event.data.get("agent_run")
        if not agent_run:
            return
            
        # Clear form
        self._clear_form()
        
        # Set status
        self.status_var.set(f"Created agent run {agent_run.id}")
        
        # Show success message
        if messagebox.askyesno("Agent Run Created", f"Agent run {agent_run.id} created successfully. View it now?"):
            # Publish view agent run requested event
            self.controller.event_bus.publish(
                Event(EventType.VIEW_AGENT_RUN_REQUESTED, {"agent_run_id": agent_run.id})
            )
            
    def _on_agent_run_failed(self, event: Event):
        """
        Handle agent run failed event.
        
        Args:
            event: Event object with error in data
        """
        error = event.data.get("error", "Failed to create agent run")
        self.status_var.set(f"Error: {error}")
        
    def _on_load_error(self, event: Event):
        """
        Handle load error event.
        
        Args:
            event: Event object with error and type in data
        """
        error_type = event.data.get("type")
        if error_type in ["repositories", "models"]:
            error = event.data.get("error", f"Error loading {error_type}")
            self.status_var.set(f"Error: {error}")
            
    def _update_repository_combobox(self):
        """Update the repository combobox."""
        # Create repository values
        repo_values = [f"{repo.name} ({repo.id})" for repo in self.repositories]
        
        # Update combobox
        self.repo_combobox.config(values=repo_values)
        
        # Select first repository if available
        if repo_values:
            self.repo_var.set(repo_values[0])
            
    def _update_model_combobox(self):
        """Update the model combobox."""
        # Update combobox
        self.model_combobox.config(values=self.models)
        
        # Select first model if available
        if self.models:
            self.model_var.set(self.models[0])
            
    def _on_create(self):
        """Handle create button click."""
        # Get form values
        repo_value = self.repo_var.get()
        model = self.model_var.get()
        temperature = self.temp_var.get()
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        metadata_str = self.metadata_text.get(1.0, tk.END).strip()
        
        # Validate form
        if not prompt:
            self.status_var.set("Error: Prompt is required")
            return
            
        # Parse repository ID
        repo_id = None
        if repo_value:
            try:
                repo_id = int(repo_value.split("(")[-1].split(")")[0])
            except (ValueError, IndexError):
                self.status_var.set("Error: Invalid repository selection")
                return
                
        # Parse metadata
        metadata = None
        if metadata_str:
            try:
                metadata = json.loads(metadata_str)
            except json.JSONDecodeError:
                self.status_var.set("Error: Invalid metadata JSON")
                return
                
        # Set status
        self.status_var.set("Creating agent run...")
        
        # Publish agent run requested event
        self.controller.event_bus.publish(
            Event(EventType.AGENT_RUN_REQUESTED, {
                "prompt": prompt,
                "repo_id": repo_id,
                "model": model,
                "temperature": temperature,
                "metadata": metadata
            })
        )
        
    def _clear_form(self):
        """Clear the form."""
        self.prompt_text.delete(1.0, tk.END)
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(tk.END, "{}")
        self.temp_var.set(0.7)
        self.status_var.set("")
        
    def pack(self, **kwargs):
        """
        Pack the frame and refresh the data.
        
        Args:
            **kwargs: Pack options
        """
        super().pack(**kwargs)
        
        # Refresh repositories and models
        self.controller.event_bus.publish(
            Event(EventType.REFRESH_REQUESTED, {"type": "repositories"})
        )
        
        self.controller.event_bus.publish(
            Event(EventType.REFRESH_REQUESTED, {"type": "models"})
        )

