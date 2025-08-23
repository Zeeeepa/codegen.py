#!/usr/bin/env python3
"""
Unified Codegen UI - A Tkinter-based UI for the Codegen Agent API.

This module provides a unified implementation of the Codegen UI,
consolidating functionality from multiple existing implementations.
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import sys
import os
from typing import Dict, List, Any, Optional, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from enhanced_ui
try:
    from enhanced_ui.application import CodegenApplication
    logger.info("Using enhanced_ui implementation")
except ImportError:
    # Import from enhanced_codegen_ui
    try:
        from enhanced_codegen_ui.application import CodegenApplication
        logger.info("Using enhanced_codegen_ui implementation")
    except ImportError:
        # Import from ui
        try:
            from ui.application import CodegenApplication
            logger.info("Using ui implementation")
        except ImportError:
            # Import from codegen_ui
            try:
                from codegen_ui.app import CodegenApp as CodegenApplication
                logger.info("Using codegen_ui implementation")
            except ImportError:
                logger.error("No UI implementation found")
                sys.exit(1)

def main():
    """Run the Unified Codegen UI application."""
    try:
        # Create and run the application
        app = CodegenApplication()
        app.run()
    except Exception as e:
        logger.exception(f"Error running application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

