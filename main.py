#!/usr/bin/env python3
"""
Main script to run the Codegen UI application.

This script creates and runs the Codegen UI application,
providing a comprehensive Tkinter-based GUI for the Codegen API.
"""

import sys
import os
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import Application

def main():
    """Run the Codegen UI application."""
    try:
        # Create and run the application
        app = Application()
        app.run()
    except Exception as e:
        logging.exception(f"Error running application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

