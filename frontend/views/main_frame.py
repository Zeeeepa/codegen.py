"""
Main frame for the Codegen UI.

This module provides the main frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from frontend.views.agent_frame import AgentFrame
from frontend.views.run_frame import RunFrame


class MainFrame(tk.Frame):
    """Main frame for the Codegen UI."""
    
    def __init__(self, master: tk.Tk):
        """Initialize the main frame.
        
        Args:
            master: The parent widget.
        """
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.agent_frame = AgentFrame(self.notebook)
        self.run_frame = RunFrame(self.notebook)
        
        # Add tabs to the notebook
        self.notebook.add(self.agent_frame, text="Agents")
        self.notebook.add(self.run_frame, text="Runs")
        
        # Create a status bar
        self.status_bar = tk.Label(
            self,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_status(self, text: str):
        """Set the status bar text.
        
        Args:
            text: The text to display in the status bar.
        """
        self.status_bar.config(text=text)

