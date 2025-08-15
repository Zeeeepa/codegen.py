"""
Comprehensive Test Suite for CLI Error Handling

Tests the sophisticated error handling system including:
- Error classification and translation
- SDK error mapping
- Rich UI formatting
- Context management
- Exit codes and suggestions
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console
from io import StringIO

# Import the error handling system
sys.path.append('..')
from cli.core.errors import (
    CLIError,
    ConfigurationError,
    AuthenticationCLIError,
    ValidationCLIError,
    NetworkCLIError,
    translate_sdk_error,
    handle_cli_error,
    handle_keyboard_interrupt,
    handle_unexpected_error,
    ErrorHandler
)

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


class TestCLIErrorClasses:
    """Test the CLI error class hierarchy."""
    
    def test_cli_error_basic(self):
        """Test basic CLIError functionality."""
        error = CLIError("Test error", exit_code=5, suggestions=["Try again"])
        
        assert error.message == "Test error"
        assert error.exit_code == 5
        assert error.suggestions == ["Try again"]
        assert error.details is None
        assert str(error) == "Test error"
    
    def test_cli_error_with_details(self):
        """Test CLIError with details."""
        error = CLIError(
            "Test error", 
            exit_code=3, 
            suggestions=["Fix this", "Try that"],
            details="Additional context"
        )
        
        assert error.details == "Additional context"
        assert len(error.suggestions) == 2
    
    def test_configuration_error(self):
        """Test ConfigurationError with default suggestions."""
        error = ConfigurationError("Config missing")
        
        assert error.exit_code == 2
        assert "codegen config init" in error.suggestions[0]
        assert len(error.suggestions) >= 3
    
    def test_configuration_error_custom_suggestions(self):
        """Test ConfigurationError with custom suggestions."""
        custom_suggestions = ["Custom fix"]
        error = ConfigurationError("Config error", suggestions=custom_suggestions)
        
        assert error.suggestions == custom_suggestions
    
    def test_authentication_cli_error(self):
        """Test AuthenticationCLIError."""
        error = AuthenticationCLIError("Auth failed")
        
        assert error.exit_code == 3
        assert "API token" in error.suggestions[0]
        assert "https://codegen.com/settings" in error.suggestions[2]
    
    def test_validation_cli_error(self):
        """Test ValidationCLIError with field errors."""
        field_errors = {
            "email": ["Invalid format"],
            "age": ["Must be positive"]
        }
        error = ValidationCLIError("Validation failed", field_errors=field_errors)
        
        assert error.exit_code == 4
        assert error.field_errors == field_errors
        assert "--help" in error.suggestions[0]
    
    def test_network_cli_error(self):
        """Test NetworkCLIError."""
        error = NetworkCLIError("Connection failed")
        
        assert error.exit_code == 5
        assert "internet connection" in error.suggestions[0]
        assert "--verbose" in error.suggestions[3]


class TestSDKErrorTranslation:
    """Test translation of SDK errors to CLI errors."""
    
    def test_authentication_error_translation(self):
        """Test AuthenticationError translation."""
        sdk_error = AuthenticationError("Invalid token", 401)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, AuthenticationCLIError)
        assert "Authentication failed" in cli_error.message
        assert "Invalid token" in cli_error.message
        assert cli_error.exit_code == 3
        assert len(cli_error.suggestions) == 3
    
    def test_validation_error_translation(self):
        """Test ValidationError translation."""
        sdk_error = ValidationError("Invalid input", 400)
        sdk_error.field_errors = {"name": ["Required"]}
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, ValidationCLIError)
        assert "Input validation failed" in cli_error.message
        assert cli_error.exit_code == 4
        assert "Fix name: Required" in cli_error.suggestions
    
    def test_rate_limit_error_translation(self):
        """Test RateLimitError translation."""
        sdk_error = RateLimitError(retry_after=60)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "Rate limit exceeded" in cli_error.message
        assert cli_error.exit_code == 6
        assert "Wait 60 seconds" in cli_error.suggestions[0]
        assert "--wait" in cli_error.suggestions[2]
    
    def test_not_found_error_translation(self):
        """Test NotFoundError translation."""
        sdk_error = NotFoundError("Resource not found", 404)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "Resource not found" in cli_error.message
        assert cli_error.exit_code == 7
        assert "resource ID" in cli_error.suggestions[0]
    
    def test_timeout_error_translation(self):
        """Test TimeoutError translation."""
        sdk_error = TimeoutError("Request timeout", 408)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "Request timed out" in cli_error.message
        assert cli_error.exit_code == 8
        assert "--timeout" in cli_error.suggestions[0]
    
    def test_network_error_translation(self):
        """Test NetworkError translation."""
        sdk_error = NetworkError("Connection failed")
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, NetworkCLIError)
        assert "Network error" in cli_error.message
        assert cli_error.exit_code == 5
        assert "internet connection" in cli_error.suggestions[0]
    
    def test_server_error_translation(self):
        """Test ServerError translation."""
        sdk_error = ServerError("Internal error", 500)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "Server error" in cli_error.message
        assert cli_error.exit_code == 9
        assert "service is experiencing issues" in cli_error.suggestions[0]
    
    def test_generic_api_error_translation(self):
        """Test generic CodegenAPIError translation."""
        sdk_error = CodegenAPIError("Generic error", 400)
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "API error" in cli_error.message
        assert cli_error.exit_code == 10
        assert "API documentation" in cli_error.suggestions[0]
    
    def test_unexpected_error_translation(self):
        """Test unexpected error translation."""
        sdk_error = ValueError("Unexpected error")
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, CLIError)
        assert "Unexpected error" in cli_error.message
        assert cli_error.exit_code == 1
        assert "unexpected error, please report it" in cli_error.suggestions[0]


class TestErrorHandling:
    """Test error handling and display functions."""
    
    @patch('cli.core.errors.Console')
    def test_handle_cli_error_basic(self, mock_console_class):
        """Test basic CLI error handling."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        error = CLIError("Test error", suggestions=["Fix it"])
        handle_cli_error(error)
        
        mock_console.print.assert_called_once()
        # Verify the panel was created with error content
        call_args = mock_console.print.call_args[0][0]
        assert hasattr(call_args, 'title')
    
    @patch('cli.core.errors.Console')
    def test_handle_validation_error_with_fields(self, mock_console_class):
        """Test handling ValidationCLIError with field errors."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        field_errors = {"email": ["Invalid"], "name": ["Required"]}
        error = ValidationCLIError("Validation failed", field_errors=field_errors)
        handle_cli_error(error)
        
        mock_console.print.assert_called_once()
    
    @patch('cli.core.errors.Console')
    def test_handle_keyboard_interrupt(self, mock_console_class):
        """Test keyboard interrupt handling."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        handle_keyboard_interrupt()
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "cancelled by user" in call_args
    
    @patch('cli.core.errors.Console')
    def test_handle_unexpected_error_verbose(self, mock_console_class):
        """Test unexpected error handling in verbose mode."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        error = Exception("Unexpected")
        handle_unexpected_error(error, verbose=True)
        
        mock_console.print_exception.assert_called_once_with(show_locals=True)
    
    @patch('cli.core.errors.Console')
    def test_handle_unexpected_error_normal(self, mock_console_class):
        """Test unexpected error handling in normal mode."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        error = Exception("Unexpected")
        handle_unexpected_error(error, verbose=False)
        
        assert mock_console.print.call_count == 2  # Error message + verbose hint


class TestErrorHandlerContextManager:
    """Test the ErrorHandler context manager."""
    
    def test_error_handler_no_exception(self):
        """Test ErrorHandler when no exception occurs."""
        with ErrorHandler(verbose=False) as handler:
            pass  # No exception
        # Should complete normally
    
    @patch('cli.core.errors.handle_cli_error')
    @patch('sys.exit')
    def test_error_handler_cli_error(self, mock_exit, mock_handle):
        """Test ErrorHandler with CLIError."""
        error = CLIError("Test error", exit_code=5)
        
        with pytest.raises(SystemExit):
            with ErrorHandler(verbose=False):
                raise error
        
        mock_handle.assert_called_once_with(error)
        mock_exit.assert_called_once_with(5)
    
    @patch('cli.core.errors.handle_keyboard_interrupt')
    @patch('sys.exit')
    def test_error_handler_keyboard_interrupt(self, mock_exit, mock_handle):
        """Test ErrorHandler with KeyboardInterrupt."""
        with pytest.raises(SystemExit):
            with ErrorHandler(verbose=False):
                raise KeyboardInterrupt()
        
        mock_handle.assert_called_once()
        mock_exit.assert_called_once_with(130)
    
    @patch('cli.core.errors.translate_sdk_error')
    @patch('cli.core.errors.handle_cli_error')
    @patch('sys.exit')
    def test_error_handler_sdk_error(self, mock_exit, mock_handle, mock_translate):
        """Test ErrorHandler with SDK error."""
        sdk_error = AuthenticationError("Auth failed", 401)
        cli_error = AuthenticationCLIError("Translated error")
        mock_translate.return_value = cli_error
        
        with pytest.raises(SystemExit):
            with ErrorHandler(verbose=False):
                raise sdk_error
        
        mock_translate.assert_called_once_with(sdk_error)
        mock_handle.assert_called_once_with(cli_error)
        mock_exit.assert_called_once_with(3)
    
    @patch('cli.core.errors.handle_unexpected_error')
    @patch('sys.exit')
    def test_error_handler_unexpected_error(self, mock_exit, mock_handle):
        """Test ErrorHandler with unexpected error."""
        error = ValueError("Unexpected")
        
        with pytest.raises(SystemExit):
            with ErrorHandler(verbose=True):
                raise error
        
        mock_handle.assert_called_once_with(error, True)
        mock_exit.assert_called_once_with(1)


class TestErrorIntegration:
    """Integration tests for the complete error handling flow."""
    
    @patch('cli.core.errors.Console')
    @patch('sys.exit')
    def test_complete_error_flow(self, mock_exit, mock_console_class):
        """Test complete error handling flow from SDK to CLI display."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        # Simulate an authentication error from the SDK
        sdk_error = AuthenticationError("Invalid API token", 401)
        
        with pytest.raises(SystemExit):
            with ErrorHandler(verbose=False):
                raise sdk_error
        
        # Verify the error was translated and handled
        mock_console.print.assert_called_once()
        mock_exit.assert_called_once_with(3)
    
    def test_error_message_quality(self):
        """Test that error messages are helpful and actionable."""
        # Test various error types have quality messages
        errors_to_test = [
            (AuthenticationError("Bad token", 401), "API token"),
            (ValidationError("Bad input", 400), "input parameters"),
            (RateLimitError(60), "Wait 60 seconds"),
            (NotFoundError("Not found", 404), "resource ID"),
            (TimeoutError("Timeout", 408), "--timeout"),
            (NetworkError("No connection"), "internet connection"),
            (ServerError("Server down", 500), "service is experiencing"),
        ]
        
        for sdk_error, expected_text in errors_to_test:
            cli_error = translate_sdk_error(sdk_error)
            
            # Check that suggestions contain helpful text
            suggestions_text = " ".join(cli_error.suggestions)
            assert expected_text in suggestions_text.lower()
            
            # Check that exit codes are appropriate
            assert 1 <= cli_error.exit_code <= 10
            
            # Check that messages are informative
            assert len(cli_error.message) > 10
            assert cli_error.message != str(sdk_error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

