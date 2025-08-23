"""
Compatibility module for backward compatibility with existing code.

This module provides a shim to maintain backward compatibility with code
that imports from the old codegen_api.py module.
"""

import warnings

warnings.warn(
    "The codegen_api module is deprecated. Please import from backend.api instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export from new locations
from backend.api.codegen_api import *

