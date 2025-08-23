#!/usr/bin/env python3
"""
Codegen UI Entry Point.

This module serves as the entry point for the Codegen UI.
"""

import tkinter as tk

from frontend import MainFrame


def main():
    """Run the Codegen UI."""
    root = tk.Tk()
    root.title("Codegen UI")
    root.geometry("800x600")
    app = MainFrame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

