"""
Compatibility module for backward compatibility with existing code.

This module provides shims and re-exports to maintain backward compatibility
with code that imports from the old module structure.
"""

# Import and re-export from new locations
from backend.core.config.client_config import ClientConfig
from backend.core.config.presets import ConfigPresets

