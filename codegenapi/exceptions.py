"""
Error Handling

Clean exception hierarchy for different types of errors.
Separates API errors from task management errors.
"""

from typing import Optional, Dict, Any


class CodegenError(Exception):
    """Base exception for Codegen-related errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class CodegenAPIError(CodegenError):
    """API-related errors"""
    pass


class CodegenAuthError(CodegenError):
    """Authentication errors"""
    pass


class CodegenConnectionError(CodegenError):
    """Connection errors"""
    pass


class TaskError(Exception):
    """Task management errors"""
    
    def __init__(self, message: str, task_id: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.task_id = task_id


class TaskNotFoundError(TaskError):
    """Task not found error"""
    pass


class TaskStateError(TaskError):
    """Invalid task state error"""
    pass


class TemplateError(Exception):
    """Template-related errors"""
    
    def __init__(self, message: str, template_name: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.template_name = template_name


class TemplateNotFoundError(TemplateError):
    """Template not found error"""
    pass


class TemplateRenderError(TemplateError):
    """Template rendering error"""
    pass


class ConfigError(Exception):
    """Configuration errors"""
    pass


class WorkspaceError(Exception):
    """Workspace-related errors"""
    
    def __init__(self, message: str, workspace_name: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.workspace_name = workspace_name

