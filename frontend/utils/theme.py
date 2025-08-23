"""
Theme utilities for the Codegen UI.

This module provides utility functions for managing themes in the Codegen UI.
"""

from typing import Dict, Any


# Default theme
DEFAULT_THEME = {
    "bg": "#FFFFFF",
    "fg": "#000000",
    "button_bg": "#4CAF50",
    "button_fg": "#FFFFFF",
    "input_bg": "#FFFFFF",
    "input_fg": "#000000",
    "output_bg": "#FFFFFF",
    "output_fg": "#000000",
    "font": ("Arial", 10),
}

# Dark theme
DARK_THEME = {
    "bg": "#2D2D2D",
    "fg": "#FFFFFF",
    "button_bg": "#4CAF50",
    "button_fg": "#FFFFFF",
    "input_bg": "#3D3D3D",
    "input_fg": "#FFFFFF",
    "output_bg": "#3D3D3D",
    "output_fg": "#FFFFFF",
    "font": ("Arial", 10),
}

# Current theme
current_theme = DEFAULT_THEME.copy()


def get_theme() -> Dict[str, Any]:
    """Get the current theme.
    
    Returns:
        The current theme.
    """
    return current_theme


def set_theme(theme: str):
    """Set the current theme.
    
    Args:
        theme: The name of the theme to set.
    """
    global current_theme
    
    if theme.lower() == "default":
        current_theme = DEFAULT_THEME.copy()
    elif theme.lower() == "dark":
        current_theme = DARK_THEME.copy()
    else:
        raise ValueError(f"Unknown theme: {theme}")

