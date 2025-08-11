"""
Codegen API CLI Package

Simple, effective CLI for Codegen API based on PR 8 and PR 9 analysis.
Clean separation between UI (CLI) and Codegen integration.
"""

from .codegen_client import CodegenClient
from .models import Task, TaskStatus, TaskType
from .exceptions import CodegenError, TaskError

__version__ = "2.0.0"
__all__ = ['CodegenClient', 'Task', 'TaskStatus', 'TaskType', 'CodegenError', 'TaskError']

