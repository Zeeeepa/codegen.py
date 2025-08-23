#!/usr/bin/env python3
"""
Tkinter UI for the Codegen API.

This script provides a Tkinter-based UI for interacting with the Codegen API.
"""

import tkinter as tk
from codegen.ui import CodegenTkApp

if __name__ == "__main__":
    root = tk.Tk()
    app = CodegenTkApp(root)
    root.mainloop()

