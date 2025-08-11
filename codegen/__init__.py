"""
Codegen Python SDK and CLI
A comprehensive toolkit for agent orchestration and API interaction
"""

from .agents import Agent
from .core import CodegenClient
from .tasks import Task, TaskStatus

__version__ = "1.0.0"
__author__ = "Codegen Team"
__email__ = "support@codegen.com"

# Main exports for SDK usage
__all__ = [
    "CodegenClient",
    "Agent",
    "Task",
    "TaskStatus",
]

# Backward compatibility - maintain existing API
