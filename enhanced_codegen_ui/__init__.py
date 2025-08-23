"""
Backward compatibility module for the Enhanced Codegen UI.

This module provides backward compatibility for the Enhanced Codegen UI.
"""

import logging
import warnings

# Import from the new UI package
try:
    from ui.application import CodegenApplication
except ImportError:
    logging.warning("Failed to import from ui package. Using local implementation.")
    from enhanced_codegen_ui.app import EnhancedCodegenApp
else:
    # Create a compatibility class
    class EnhancedCodegenApp:
        """Backward compatibility class for the Enhanced Codegen UI."""
        
        def __init__(self, root):
            """
            Initialize the Enhanced Codegen UI.
            
            Args:
                root: The root Tkinter window.
            """
            warnings.warn(
                "EnhancedCodegenApp is deprecated. Use CodegenApplication instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.app = CodegenApplication()
        
        def run(self):
            """Run the application."""
            self.app.run()

__all__ = ["EnhancedCodegenApp"]

