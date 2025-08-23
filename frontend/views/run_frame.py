"""
Run frame for the Codegen UI.

This module provides a frame for managing runs in the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional

from frontend.components import Button, InputField, OutputDisplay


class RunFrame(tk.Frame):
    """Frame for managing runs in the Codegen UI."""
    
    def __init__(self, master: tk.Widget):
        """Initialize the run frame.
        
        Args:
            master: The parent widget.
        """
        super().__init__(master)
        
        # Create a frame for the run list
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a listbox for runs
        self.run_listbox = tk.Listbox(self.list_frame)
        self.run_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect the scrollbar to the listbox
        self.run_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.run_listbox.yview)
        
        # Create a frame for run details
        self.details_frame = tk.Frame(self)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create labels and entry fields for run details
        self.agent_label = tk.Label(self.details_frame, text="Agent:")
        self.agent_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.agent_entry = InputField(self.details_frame)
        self.agent_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.status_label = tk.Label(self.details_frame, text="Status:")
        self.status_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.status_entry = InputField(self.details_frame)
        self.status_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Create buttons for run actions
        self.button_frame = tk.Frame(self.details_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.create_button = Button(
            self.button_frame,
            text="Create",
            command=self.create_run
        )
        self.create_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = Button(
            self.button_frame,
            text="Cancel",
            command=self.cancel_run,
            bg="#F44336"
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the output display
        self.output_frame = tk.Frame(self.details_frame)
        self.output_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.output_display = OutputDisplay(
            self.output_frame,
            width=40,
            height=10
        )
        self.output_display.pack(fill=tk.BOTH, expand=True)
        
        # Populate the run list
        self.populate_run_list()
        
        # Bind the listbox selection event
        self.run_listbox.bind("<<ListboxSelect>>", self.on_run_select)
    
    def populate_run_list(self):
        """Populate the run list with sample data."""
        # Clear the listbox
        self.run_listbox.delete(0, tk.END)
        
        # Add sample runs
        self.run_listbox.insert(tk.END, "Run 1 (completed)")
        self.run_listbox.insert(tk.END, "Run 2 (running)")
    
    def on_run_select(self, event):
        """Handle run selection events.
        
        Args:
            event: The event object.
        """
        # Get the selected run
        selection = self.run_listbox.curselection()
        if not selection:
            return
        
        # Get the run name
        run_name = self.run_listbox.get(selection[0])
        
        # Update the entry fields
        if "Run 1" in run_name:
            self.agent_entry.delete(0, tk.END)
            self.agent_entry.insert(0, "Agent 1")
            
            self.status_entry.delete(0, tk.END)
            self.status_entry.insert(0, "completed")
        elif "Run 2" in run_name:
            self.agent_entry.delete(0, tk.END)
            self.agent_entry.insert(0, "Agent 2")
            
            self.status_entry.delete(0, tk.END)
            self.status_entry.insert(0, "running")
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Selected run: {run_name}\n")
    
    def create_run(self):
        """Create a new run."""
        # Get the run details
        agent = self.agent_entry.get()
        
        # Validate the input
        if not agent:
            self.output_display.clear()
            self.output_display.append_text("Error: Agent is required\n")
            return
        
        # Add the run to the listbox
        run_name = f"Run {self.run_listbox.size() + 1} (running)"
        self.run_listbox.insert(tk.END, run_name)
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Created run: {run_name}\n")
    
    def cancel_run(self):
        """Cancel an existing run."""
        # Get the selected run
        selection = self.run_listbox.curselection()
        if not selection:
            self.output_display.clear()
            self.output_display.append_text("Error: No run selected\n")
            return
        
        # Get the run name
        run_name = self.run_listbox.get(selection[0])
        
        # Check if the run is already completed
        if "completed" in run_name:
            self.output_display.clear()
            self.output_display.append_text("Error: Cannot cancel a completed run\n")
            return
        
        # Update the run in the listbox
        new_run_name = run_name.replace("running", "cancelled")
        self.run_listbox.delete(selection[0])
        self.run_listbox.insert(selection[0], new_run_name)
        
        # Update the status entry
        self.status_entry.delete(0, tk.END)
        self.status_entry.insert(0, "cancelled")
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Cancelled run: {run_name}\n")

