#!/usr/bin/env python3
"""
Codegen UI Application

This is the main entry point for the Codegen UI application.
It launches the Tkinter-based user interface for interacting with the Codegen API.
"""

import sys
import logging
import tkinter as tk
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the Codegen UI application.
    
    This function initializes and runs the Codegen UI application.
    It handles any exceptions that might occur during startup.
    """
    try:
        # Import here to avoid circular imports
        from ui.application import CodegenApplication
        
        # Create and run the application
        app = CodegenApplication()
        app.run()
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print(f"Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("  pip install -e .")
        print("  pip install -e '.[ui]'")
        sys.exit(1)
        
    except Exception as e:
        logger.exception(f"Error running application: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

