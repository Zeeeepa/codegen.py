#!/usr/bin/env python3
"""
Codegen API GUI Application

This script launches a Tkinter-based GUI for interacting with the Codegen API.
"""

import sys
import tkinter as tk
from codegen.ui import CodegenTkApp

def main():
    """Main entry point for the GUI application."""
    try:
        root = tk.Tk()
        app = CodegenTkApp(root)
        app.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure you have tkinter installed. On most systems, you can install it with:")
        print("  - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - Fedora: sudo dnf install python3-tkinter")
        print("  - macOS: brew install python-tk")
        print("  - Windows: tkinter is included with standard Python installations")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

