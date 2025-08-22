"""
Exceptions for the Codegen API client.
"""

from typing import Any, Dict, Optional


class CodegenApiError(Exception):
    """Base exception for all Codegen API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (Status code: {self.status_code})"
        return self.message


class CodegenAuthError(CodegenApiError):
    """Raised when there is an authentication error."""

    pass


class CodegenRateLimitError(CodegenApiError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 429,
        response_data: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_message = super().__str__()
        if self.retry_after:
            return f"{base_message} (Retry after: {self.retry_after} seconds)"
        return base_message


class CodegenResourceNotFoundError(CodegenApiError):
    """Raised when a requested resource is not found."""

    pass


class CodegenValidationError(CodegenApiError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 422,
        response_data: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.validation_errors = validation_errors or {}

    def __str__(self) -> str:
        base_message = super().__str__()
        if self.validation_errors:
            return f"{base_message} (Validation errors: {self.validation_errors})"
        return base_message

