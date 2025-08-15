"""
Enhanced Error Handling for CLI

This module provides CLI-friendly error handling that translates SDK exceptions
into user-friendly messages with actionable suggestions.
"""

import sys
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import SDK exceptions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from codegen_api import (
    CodegenAPIError,
    ValidationError,
    RateLimitError, 
    AuthenticationError,
    NotFoundError,
    ServerError,
    TimeoutError,
    NetworkError,
)


class CLIError(Exception):
    """Base exception for CLI-specific errors."""
    
    def __init__(
        self, 
        message: str, 
        exit_code: int = 1,
        suggestions: Optional[List[str]] = None,
        details: Optional[str] = None
    ):
        self.message = message
        self.exit_code = exit_code
        self.suggestions = suggestions or []
        self.details = details
        super().__init__(message)


class ConfigurationError(CLIError):
    """Configuration-related error."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        default_suggestions = [
            "Run 'codegen config init' to create a configuration file",
            "Check your environment variables (CODEGEN_API_TOKEN, CODEGEN_ORG_ID)",
            "Use 'codegen config show' to view current configuration"
        ]
        super().__init__(
            message, 
            exit_code=2,
            suggestions=suggestions or default_suggestions
        )


class AuthenticationCLIError(CLIError):
    """Authentication-related CLI error."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        default_suggestions = [
            "Check your API token with 'codegen auth status'",
            "Set your token with 'codegen config set api-token YOUR_TOKEN'",
            "Visit https://codegen.com/settings to generate a new token"
        ]
        super().__init__(
            message,
            exit_code=3, 
            suggestions=suggestions or default_suggestions
        )


class ValidationCLIError(CLIError):
    """Input validation error."""
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, List[str]]] = None,
        suggestions: Optional[List[str]] = None
    ):
        self.field_errors = field_errors or {}
        default_suggestions = [
            "Check the command syntax with 'codegen COMMAND --help'",
            "Verify your input parameters and try again"
        ]
        super().__init__(
            message,
            exit_code=4,
            suggestions=suggestions or default_suggestions
        )


class NetworkCLIError(CLIError):
    """Network connectivity error."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        default_suggestions = [
            "Check your internet connection",
            "Verify the API endpoint is accessible",
            "Try again in a few moments",
            "Use --verbose for more network details"
        ]
        super().__init__(
            message,
            exit_code=5,
            suggestions=suggestions or default_suggestions
        )


def translate_sdk_error(error: Exception) -> CLIError:
    """
    Translate SDK exceptions into CLI-friendly errors.
    
    Args:
        error: The original SDK exception
        
    Returns:
        CLIError: A CLI-friendly error with suggestions
    """
    if isinstance(error, AuthenticationError):
        return AuthenticationCLIError(
            f"Authentication failed: {error.message}",
            suggestions=[
                "Verify your API token is correct and active",
                "Check if your token has the required permissions",
                "Generate a new token at https://codegen.com/settings"
            ]
        )
    
    elif isinstance(error, ValidationError):
        suggestions = []
        if hasattr(error, 'field_errors') and error.field_errors:
            for field, errors in error.field_errors.items():
                suggestions.extend([f"Fix {field}: {err}" for err in errors])
        
        return ValidationCLIError(
            f"Input validation failed: {error.message}",
            field_errors=getattr(error, 'field_errors', {}),
            suggestions=suggestions or [
                "Check your input parameters",
                "Use --help to see valid options"
            ]
        )
    
    elif isinstance(error, RateLimitError):
        return CLIError(
            f"Rate limit exceeded: {error.message}",
            exit_code=6,
            suggestions=[
                f"Wait {error.retry_after} seconds before retrying",
                "Consider upgrading your plan for higher rate limits",
                "Use --wait to automatically retry after rate limit"
            ]
        )
    
    elif isinstance(error, NotFoundError):
        return CLIError(
            f"Resource not found: {error.message}",
            exit_code=7,
            suggestions=[
                "Verify the resource ID or name is correct",
                "Check if you have access to this resource",
                "Use 'codegen org list' to see available organizations"
            ]
        )
    
    elif isinstance(error, TimeoutError):
        return CLIError(
            f"Request timed out: {error.message}",
            exit_code=8,
            suggestions=[
                "Try again with a longer timeout using --timeout",
                "Check your network connection",
                "The service might be experiencing high load"
            ]
        )
    
    elif isinstance(error, NetworkError):
        return NetworkCLIError(
            f"Network error: {error.message}",
            suggestions=[
                "Check your internet connection",
                "Verify DNS resolution is working",
                "Try using a different network or VPN"
            ]
        )
    
    elif isinstance(error, ServerError):
        return CLIError(
            f"Server error: {error.message}",
            exit_code=9,
            suggestions=[
                "The service is experiencing issues, try again later",
                "Check https://status.codegen.com for service status",
                "Contact support if the issue persists"
            ]
        )
    
    elif isinstance(error, CodegenAPIError):
        return CLIError(
            f"API error: {error.message}",
            exit_code=10,
            suggestions=[
                "Check the API documentation for this endpoint",
                "Verify your request parameters",
                "Use --verbose for more details"
            ]
        )
    
    else:
        # Handle unexpected errors
        return CLIError(
            f"Unexpected error: {str(error)}",
            exit_code=1,
            suggestions=[
                "This is an unexpected error, please report it",
                "Use --verbose for more details",
                "Try the operation again"
            ]
        )


def handle_cli_error(error: CLIError) -> None:
    """
    Display a CLI error in a user-friendly format.
    
    Args:
        error: The CLI error to display
    """
    console = Console(stderr=True)
    
    # Create error message
    error_text = Text()
    error_text.append("Error: ", style="bold red")
    error_text.append(error.message, style="red")
    
    # Create panel content
    panel_content = [error_text]
    
    # Add details if available
    if error.details:
        panel_content.append("")
        panel_content.append(Text(error.details, style="dim"))
    
    # Add field errors for validation errors
    if isinstance(error, ValidationCLIError) and error.field_errors:
        panel_content.append("")
        panel_content.append(Text("Field errors:", style="bold yellow"))
        for field, errors in error.field_errors.items():
            for err in errors:
                panel_content.append(Text(f"  • {field}: {err}", style="yellow"))
    
    # Add suggestions
    if error.suggestions:
        panel_content.append("")
        panel_content.append(Text("Suggestions:", style="bold green"))
        for suggestion in error.suggestions:
            panel_content.append(Text(f"  • {suggestion}", style="green"))
    
    # Display the error panel
    console.print(Panel(
        "\n".join(str(item) for item in panel_content),
        title="[bold red]CLI Error[/bold red]",
        border_style="red"
    ))


def handle_keyboard_interrupt() -> None:
    """Handle keyboard interrupt (Ctrl+C) gracefully."""
    console = Console(stderr=True)
    console.print("\n[yellow]Operation cancelled by user[/yellow]")


def handle_unexpected_error(error: Exception, verbose: bool = False) -> None:
    """
    Handle unexpected errors with appropriate detail level.
    
    Args:
        error: The unexpected error
        verbose: Whether to show full traceback
    """
    console = Console(stderr=True)
    
    if verbose:
        console.print_exception(show_locals=True)
    else:
        console.print(f"[red]Unexpected error: {error}[/red]")
        console.print("[dim]Use --verbose for more details[/dim]")


# Context manager for error handling
class ErrorHandler:
    """Context manager for handling errors in CLI commands."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        
        if isinstance(exc_val, CLIError):
            handle_cli_error(exc_val)
            sys.exit(exc_val.exit_code)
        
        elif isinstance(exc_val, KeyboardInterrupt):
            handle_keyboard_interrupt()
            sys.exit(130)
        
        elif isinstance(exc_val, (CodegenAPIError, ValidationError, RateLimitError, 
                                 AuthenticationError, NotFoundError, ServerError,
                                 TimeoutError, NetworkError)):
            cli_error = translate_sdk_error(exc_val)
            handle_cli_error(cli_error)
            sys.exit(cli_error.exit_code)
        
        else:
            handle_unexpected_error(exc_val, self.verbose)
            sys.exit(1)
        
        return True  # Suppress the exception
