"""
CodegenAPI - Agent-to-Agent Task Execution Tool

A streamlined CLI tool for AI agents to execute coding tasks using the Codegen API.
"""

__version__ = "0.1.0"
__author__ = "Codegen Team"

from .models import Task, TaskStatus
from .exceptions import CodegenAPIError, TaskError, ConfigError, APIError
from .config import Config
from .task_manager import TaskManager

__all__ = [
    "Task", 
    "TaskStatus", 
    "CodegenAPIError", 
    "TaskError", 
    "ConfigError",
    "APIError",
    "Config",
    "TaskManager"
]
