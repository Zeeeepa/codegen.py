#!/usr/bin/env python3
"""
Main script to run the Enhanced Codegen UI application.

This script creates and runs the Enhanced Codegen UI application,
providing a comprehensive Tkinter-based GUI for the Codegen API.
"""

import sys
import os
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_codegen_ui import CodegenApplication


def main():
    """Run the Enhanced Codegen UI application."""
    try:
        # Create and run the application
        app = CodegenApplication()
        app.run()
    except Exception as e:
        logging.exception(f"Error running application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

