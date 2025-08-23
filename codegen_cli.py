"""
Compatibility module for backward compatibility with existing code.

This module provides a shim to maintain backward compatibility with code
that imports from the old codegen_cli.py module.
"""

import warnings

warnings.warn(
    "The codegen_cli module is deprecated. Please import from backend.cli instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export from new locations
from backend.cli.codegen_cli import *

