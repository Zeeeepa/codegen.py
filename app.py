#!/usr/bin/env python3
"""
Codegen UI Application

This script launches the Codegen UI application.
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the Codegen UI.
    
    This function initializes and runs the Codegen UI application.
    It handles any exceptions that might occur during startup.
    """
    try:
        # Import here to avoid circular imports
        from codegen.ui import CodegenTkApp
        import tkinter as tk
        
        # Create the root window
        root = tk.Tk()
        root.title("Codegen UI")
        
        # Create and run the application
        app = CodegenTkApp(root)
        root.mainloop()
        
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

