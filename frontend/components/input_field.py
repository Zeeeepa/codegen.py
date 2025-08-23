"""
Input field component for the Codegen UI.

This module provides an input field component for the Codegen UI.
"""

import tkinter as tk
from typing import Callable, Optional


class InputField(tk.Entry):
    """Input field component for the Codegen UI."""
    
    def __init__(
        self,
        master: tk.Widget,
        width: int = 20,
        font: tuple = ("Arial", 10),
        bg: str = "white",
        fg: str = "black",
        **kwargs
    ):
        """Initialize the input field component.
        
        Args:
            master: The parent widget.
            width: The width of the input field.
            font: The font of the input field.
            bg: The background color of the input field.
            fg: The foreground color of the input field.
            **kwargs: Additional keyword arguments to pass to the parent class.
        """
        super().__init__(
            master,
            width=width,
            font=font,
            bg=bg,
            fg=fg,
            **kwargs
        )

