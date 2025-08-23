"""
Create agent frame for the Codegen UI.

This module provides a create agent frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class CreateAgentFrame(BaseComponent):
    """Create agent frame for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the create agent frame.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create frame for prompt
        prompt_frame = ttk.LabelFrame(self.frame, text="Agent Prompt", padding=PADDING)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create prompt text area
        self.prompt_text = scrolledtext.ScrolledText(
            prompt_frame, wrap=tk.WORD, height=10
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create model frame
        model_frame = ttk.Frame(self.frame, padding=PADDING)
        model_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create model label and combobox
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            model_frame, textvariable=self.model_var, state="readonly", width=30
        )
        self.model_combobox.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create button frame
        button_frame = ttk.Frame(self.frame, padding=PADDING)
        button_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create run button
        run_button = ttk.Button(
            button_frame, text="Run Agent", command=self._run_agent
        )
        run_button.pack(side=tk.RIGHT, padx=PADDING)
        
        # Create clear button
        clear_button = ttk.Button(
            button_frame, text="Clear", command=lambda: self.prompt_text.delete(1.0, tk.END)
        )
        clear_button.pack(side=tk.RIGHT, padx=PADDING)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        self.event_bus.subscribe(EventType.AGENT_RUN_COMPLETED, self._handle_agent_run_completed)
        self.event_bus.subscribe(EventType.AGENT_RUN_FAILED, self._handle_agent_run_failed)
    
    def load_models(self):
        """Load models."""
        # Set models
        models = ["gpt-4", "gpt-3.5-turbo", "claude-2", "claude-instant"]
        self.model_combobox["values"] = models
        
        # Set default model
        if models:
            self.model_var.set(models[0])
    
    def clear(self):
        """Clear the create agent form."""
        self.prompt_text.delete(1.0, tk.END)
    
    def _run_agent(self):
        """Run the agent."""
        # Get prompt
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            self.event_bus.publish(
                Event(
                    EventType.UI_ERROR,
                    {"error": "Prompt cannot be empty"}
                )
            )
            return
        
        # Get model
        model = self.model_var.get()
        if not model:
            self.event_bus.publish(
                Event(
                    EventType.UI_ERROR,
                    {"error": "Model must be selected"}
                )
            )
            return
        
        # Publish agent run created event
        self.event_bus.publish(
            Event(
                EventType.AGENT_RUN_CREATED,
                {
                    "prompt": prompt,
                    "model": model,
                }
            )
        )
        
        # Show success message
        self.event_bus.publish(
            Event(
                EventType.UI_SUCCESS,
                {"message": "Agent run created successfully"}
            )
        )
    
    def _handle_agent_run_completed(self, event: Event):
        """
        Handle agent run completed event.
        
        Args:
            event: The agent run completed event.
        """
        run = event.data.get("run")
        if run:
            self.event_bus.publish(
                Event(
                    EventType.UI_SUCCESS,
                    {"message": f"Agent run #{run.id} completed successfully"}
                )
            )
    
    def _handle_agent_run_failed(self, event: Event):
        """
        Handle agent run failed event.
        
        Args:
            event: The agent run failed event.
        """
        error = event.data.get("error", "Unknown error")
        self.event_bus.publish(
            Event(
                EventType.UI_ERROR,
                {"error": f"Agent run failed: {error}"}
            )
        )

