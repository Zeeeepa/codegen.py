"""
Exception classes for CodegenAPI
"""


class CodegenAPIError(Exception):
    """Base exception for CodegenAPI"""
    pass


class TaskError(CodegenAPIError):
    """Task-related errors"""
    pass


class ConfigError(CodegenAPIError):
    """Configuration-related errors"""
    pass


class APIError(CodegenAPIError):
    """API communication errors"""
    pass


class TemplateError(CodegenAPIError):
    """Template processing errors"""
    pass

