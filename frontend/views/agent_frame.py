"""
Agent frame for the Codegen UI.

This module provides a frame for managing agents in the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional

from frontend.components import Button, InputField, OutputDisplay


class AgentFrame(tk.Frame):
    """Frame for managing agents in the Codegen UI."""
    
    def __init__(self, master: tk.Widget):
        """Initialize the agent frame.
        
        Args:
            master: The parent widget.
        """
        super().__init__(master)
        
        # Create a frame for the agent list
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a listbox for agents
        self.agent_listbox = tk.Listbox(self.list_frame)
        self.agent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect the scrollbar to the listbox
        self.agent_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.agent_listbox.yview)
        
        # Create a frame for agent details
        self.details_frame = tk.Frame(self)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create labels and entry fields for agent details
        self.name_label = tk.Label(self.details_frame, text="Name:")
        self.name_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.name_entry = InputField(self.details_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.description_label = tk.Label(self.details_frame, text="Description:")
        self.description_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.description_entry = tk.Text(self.details_frame, width=30, height=5)
        self.description_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Create buttons for agent actions
        self.button_frame = tk.Frame(self.details_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.create_button = Button(
            self.button_frame,
            text="Create",
            command=self.create_agent
        )
        self.create_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = Button(
            self.button_frame,
            text="Update",
            command=self.update_agent
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = Button(
            self.button_frame,
            text="Delete",
            command=self.delete_agent,
            bg="#F44336"
        )
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the output display
        self.output_frame = tk.Frame(self.details_frame)
        self.output_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.output_display = OutputDisplay(
            self.output_frame,
            width=40,
            height=10
        )
        self.output_display.pack(fill=tk.BOTH, expand=True)
        
        # Populate the agent list
        self.populate_agent_list()
        
        # Bind the listbox selection event
        self.agent_listbox.bind("<<ListboxSelect>>", self.on_agent_select)
    
    def populate_agent_list(self):
        """Populate the agent list with sample data."""
        # Clear the listbox
        self.agent_listbox.delete(0, tk.END)
        
        # Add sample agents
        self.agent_listbox.insert(tk.END, "Agent 1")
        self.agent_listbox.insert(tk.END, "Agent 2")
    
    def on_agent_select(self, event):
        """Handle agent selection events.
        
        Args:
            event: The event object.
        """
        # Get the selected agent
        selection = self.agent_listbox.curselection()
        if not selection:
            return
        
        # Get the agent name
        agent_name = self.agent_listbox.get(selection[0])
        
        # Update the entry fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, agent_name)
        
        self.description_entry.delete(1.0, tk.END)
        self.description_entry.insert(tk.END, f"Description for {agent_name}")
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Selected agent: {agent_name}\n")
    
    def create_agent(self):
        """Create a new agent."""
        # Get the agent details
        name = self.name_entry.get()
        description = self.description_entry.get(1.0, tk.END).strip()
        
        # Validate the input
        if not name:
            self.output_display.clear()
            self.output_display.append_text("Error: Name is required\n")
            return
        
        # Add the agent to the listbox
        self.agent_listbox.insert(tk.END, name)
        
        # Clear the entry fields
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(1.0, tk.END)
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Created agent: {name}\n")
    
    def update_agent(self):
        """Update an existing agent."""
        # Get the selected agent
        selection = self.agent_listbox.curselection()
        if not selection:
            self.output_display.clear()
            self.output_display.append_text("Error: No agent selected\n")
            return
        
        # Get the agent details
        name = self.name_entry.get()
        description = self.description_entry.get(1.0, tk.END).strip()
        
        # Validate the input
        if not name:
            self.output_display.clear()
            self.output_display.append_text("Error: Name is required\n")
            return
        
        # Update the agent in the listbox
        self.agent_listbox.delete(selection[0])
        self.agent_listbox.insert(selection[0], name)
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Updated agent: {name}\n")
    
    def delete_agent(self):
        """Delete an existing agent."""
        # Get the selected agent
        selection = self.agent_listbox.curselection()
        if not selection:
            self.output_display.clear()
            self.output_display.append_text("Error: No agent selected\n")
            return
        
        # Get the agent name
        agent_name = self.agent_listbox.get(selection[0])
        
        # Delete the agent from the listbox
        self.agent_listbox.delete(selection[0])
        
        # Clear the entry fields
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(1.0, tk.END)
        
        # Update the output display
        self.output_display.clear()
        self.output_display.append_text(f"Deleted agent: {agent_name}\n")

