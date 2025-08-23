"""
Button component for the Codegen UI.

This module provides a button component for the Codegen UI.
"""

import tkinter as tk
from typing import Callable, Optional


class Button(tk.Button):
    """Button component for the Codegen UI."""
    
    def __init__(
        self,
        master: tk.Widget,
        text: str,
        command: Callable,
        width: int = 10,
        height: int = 1,
        bg: str = "#4CAF50",
        fg: str = "white",
        font: tuple = ("Arial", 10),
        **kwargs
    ):
        """Initialize the button component.
        
        Args:
            master: The parent widget.
            text: The text to display on the button.
            command: The function to call when the button is clicked.
            width: The width of the button.
            height: The height of the button.
            bg: The background color of the button.
            fg: The foreground color of the button.
            font: The font of the button.
            **kwargs: Additional keyword arguments to pass to the parent class.
        """
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            bg=bg,
            fg=fg,
            font=font,
            **kwargs
        )

