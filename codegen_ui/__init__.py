"""
Backward compatibility module for the Codegen UI.

This module provides backward compatibility for the Codegen UI.
DEPRECATED: Please use the 'frontend' module directly in new code.
"""

import logging
import warnings

warnings.warn(
    "The 'codegen_ui' module is deprecated. Please use 'frontend' module instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from the new frontend package
try:
    from frontend.views.main_frame import MainFrame as CodegenApplication
except ImportError:
    logging.warning("Failed to import from frontend package. Using local implementation.")
    from codegen_ui.app import CodegenApp
else:
    # Create a compatibility class
    class CodegenApp:
        """Backward compatibility class for the Codegen UI."""
        
        def __init__(self, root):
            """
            Initialize the Codegen UI.
            
            Args:
                root: The root Tkinter window.
            """
            warnings.warn(
                "CodegenApp is deprecated. Use frontend.views.main_frame.MainFrame instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.app = CodegenApplication(root)

__all__ = ["CodegenApp"]
