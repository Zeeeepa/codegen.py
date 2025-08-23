"""
Backward compatibility module for the Codegen UI.

This module provides backward compatibility for the Codegen UI.
"""

import logging
import warnings

# Import from the new UI package
try:
    from ui.application import CodegenApplication
    from ui.core.main_window import MainWindow
except ImportError:
    logging.warning("Failed to import from ui package. Using local implementation.")
    from codegen.ui.tkinter_app import CodegenTkApp
else:
    # Create a compatibility class
    class CodegenTkApp:
        """Backward compatibility class for the Codegen UI."""
        
        def __init__(self, root):
            """
            Initialize the Codegen UI.
            
            Args:
                root: The root Tkinter window.
            """
            warnings.warn(
                "CodegenTkApp is deprecated. Use CodegenApplication instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.app = CodegenApplication()
        
        def run(self):
            """Run the application."""
            self.app.run()

__all__ = ["CodegenTkApp"]

