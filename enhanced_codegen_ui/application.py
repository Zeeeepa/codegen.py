"""
Main application class for the Enhanced Codegen UI.

This module provides the main application class for the Enhanced Codegen UI,
coordinating between the UI components and the application controller.
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import sys
from typing import Any, Dict, List, Optional, Callable

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import EventBus, Event, EventType
from enhanced_codegen_ui.ui.main_window import MainWindow
from enhanced_codegen_ui.utils.constants import THEME, DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE


class CodegenApplication:
    """
    Main application class for the Enhanced Codegen UI.
    
    This class coordinates between the UI components and the application controller,
    handling application lifecycle and event routing.
    """
    
    def __init__(self):
        """Initialize the application."""
        # Initialize controller
        self.controller = Controller()
        
        # Initialize UI
        self.root = tk.Tk()
        self.root.title("Codegen UI")
        self.root.geometry(f"{DEFAULT_WINDOW_SIZE[0]}x{DEFAULT_WINDOW_SIZE[1]}")
        self.root.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use(THEME)
        
        # Configure styles
        self._configure_styles()
        
        # Create main window
        self.main_window = MainWindow(self.root, self.controller)
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _configure_styles(self):
        """Configure ttk styles."""
        # Configure header style
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 16, "bold")
        )
        
        # Configure subheader style
        self.style.configure(
            "Subheader.TLabel",
            font=("Helvetica", 12, "bold")
        )
        
        # Configure primary button style
        self.style.configure(
            "Primary.TButton",
            background="#2196F3",
            foreground="#FFFFFF"
        )
        
        # Configure secondary button style
        self.style.configure(
            "Secondary.TButton",
            background="#4CAF50",
            foreground="#FFFFFF"
        )
        
        # Configure error style
        self.style.configure(
            "Error.TLabel",
            foreground="#F44336"
        )
        
        # Configure success style
        self.style.configure(
            "Success.TLabel",
            foreground="#4CAF50"
        )
        
    def _setup_event_handlers(self):
        """Set up event handlers."""
        # Set up root window event handlers
        self.root.bind("<Control-q>", lambda e: self._on_close())
        self.root.bind("<F1>", lambda e: self._show_help())
        
    def _on_close(self):
        """Handle window close event."""
        # Clean up resources
        self.controller.event_bus.clear()
        
        # Destroy root window
        self.root.destroy()
        
        # Exit application
        sys.exit(0)
        
    def _show_help(self):
        """Show help dialog."""
        # Create help dialog
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Codegen UI Help")
        help_dialog.geometry("600x400")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Create help text
        help_text = tk.Text(help_dialog, wrap=tk.WORD, padx=10, pady=10)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Add help content
        help_text.insert(tk.END, "Codegen UI Help\n\n")
        help_text.insert(tk.END, "Keyboard Shortcuts:\n")
        help_text.insert(tk.END, "  Ctrl+Q: Quit application\n")
        help_text.insert(tk.END, "  F1: Show this help dialog\n")
        help_text.insert(tk.END, "  F5: Refresh current view\n")
        help_text.insert(tk.END, "  Ctrl+N: Create new agent run\n")
        help_text.insert(tk.END, "  Ctrl+1: View agent runs\n")
        help_text.insert(tk.END, "  Ctrl+2: View repositories\n")
        help_text.insert(tk.END, "  Ctrl+3: Create agent run\n")
        help_text.insert(tk.END, "\n")
        help_text.insert(tk.END, "For more information, visit https://docs.codegen.com\n")
        
        # Make text read-only
        help_text.config(state=tk.DISABLED)
        
        # Create close button
        close_button = ttk.Button(
            help_dialog,
            text="Close",
            command=help_dialog.destroy
        )
        close_button.pack(pady=10)
        
    def run(self):
        """Run the application."""
        self.root.mainloop()

