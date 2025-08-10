"""
Backward compatibility layer for existing backend.api imports
"""

# Import from the new modular structure
from codegen.agents.agent import Agent
from codegen.client import CodegenClient
from codegen.config import ClientConfig, ConfigPresets
from codegen.models import *
from codegen.exceptions import *

# Maintain backward compatibility
__all__ = [
    "Agent",
    "CodegenClient", 
    "ClientConfig",
    "ConfigPresets",
]

