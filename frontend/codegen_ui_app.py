#!/usr/bin/env python3
"""
Main script to run the Codegen UI application.
"""

import tkinter as tk
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codegen_ui.app import CodegenApp


def main():
    """Run the Codegen UI application."""
    root = tk.Tk()
    app = CodegenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

