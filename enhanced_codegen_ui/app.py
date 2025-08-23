"""
Enhanced Codegen UI Application.

This module provides the main application class for the Enhanced Codegen UI.
"""

import logging
import tkinter as tk
from tkinter import ttk

from enhanced_codegen_ui.ui.main_window import MainWindow
from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.enhanced_event_bus import EnhancedEventBus
from enhanced_codegen_ui.utils.logging_config import configure_logging


class EnhancedCodegenApp:
    """Enhanced Codegen UI Application."""

    def __init__(self, root=None):
        """
        Initialize the Enhanced Codegen UI Application.

        Args:
            root: The root Tkinter window. If None, a new window will be created.
        """
        configure_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Enhanced Codegen UI Application")

        self.root = root or tk.Tk()
        self.root.title("Enhanced Codegen UI")
        self.root.geometry("1024x768")

        # Set up the style
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a modern theme

        # Create the event bus
        self.event_bus = EnhancedEventBus()

        # Create the controller
        self.controller = Controller(self.event_bus)

        # Create the main window
        self.main_window = MainWindow(
            self.root, self.controller, self.event_bus
        )

        self.logger.info("Enhanced Codegen UI Application initialized")

    def run(self):
        """Run the application."""
        self.logger.info("Starting Enhanced Codegen UI Application")
        self.root.mainloop()
