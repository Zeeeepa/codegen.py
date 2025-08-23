"""
Compatibility module for backward compatibility with existing code.

This module provides a shim to maintain backward compatibility with code
that imports from the old codegen_ui.py module.
"""

import warnings
import tkinter as tk

warnings.warn(
    "The codegen_ui module is deprecated. Please import from frontend.views instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export from new locations
from frontend.views import MainFrame

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Codegen UI")
    app = MainFrame(root)
    root.mainloop()

