"""
Output display component for the Codegen UI.

This module provides an output display component for the Codegen UI.
"""

import tkinter as tk
from typing import Callable, Optional


class OutputDisplay(tk.Text):
    """Output display component for the Codegen UI."""
    
    def __init__(
        self,
        master: tk.Widget,
        width: int = 40,
        height: int = 10,
        font: tuple = ("Arial", 10),
        bg: str = "white",
        fg: str = "black",
        **kwargs
    ):
        """Initialize the output display component.
        
        Args:
            master: The parent widget.
            width: The width of the output display.
            height: The height of the output display.
            font: The font of the output display.
            bg: The background color of the output display.
            fg: The foreground color of the output display.
            **kwargs: Additional keyword arguments to pass to the parent class.
        """
        super().__init__(
            master,
            width=width,
            height=height,
            font=font,
            bg=bg,
            fg=fg,
            **kwargs
        )
        
        # Make the output display read-only
        self.config(state=tk.DISABLED)
    
    def append_text(self, text: str):
        """Append text to the output display.
        
        Args:
            text: The text to append.
        """
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text)
        self.config(state=tk.DISABLED)
        self.see(tk.END)
    
    def clear(self):
        """Clear the output display."""
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)

