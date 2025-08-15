# Error Handling System

The Codegen CLI features a sophisticated, enterprise-grade error handling system designed to provide users with clear, actionable feedback and automatic recovery capabilities.

## Overview

The error handling system consists of several interconnected components:

- **Error Classification**: Categorizes errors by type with specific handling strategies
- **SDK Error Translation**: Converts API errors into user-friendly CLI errors
- **Rich UI Formatting**: Displays errors with colors, suggestions, and structured information
- **Automatic Retry**: Handles transient failures with exponential backoff
- **Context Management**: Provides comprehensive error handling across the entire CLI

## Error Classification

### Error Types

The CLI uses a hierarchical error classification system:

#### 1. CLIError (Base Class)
- **Exit Code**: 1 (default)
- **Purpose**: Base class for all CLI-specific errors
- **Features**: Includes message, exit code, suggestions, and optional details

#### 2. ConfigurationError
- **Exit Code**: 2
- **Purpose**: Configuration-related issues
- **Common Causes**: Missing config files, invalid settings, environment variable issues
- **Default Suggestions**:
  - Run `codegen config init` to create a configuration file
  - Check environment variables (CODEGEN_API_TOKEN, CODEGEN_ORG_ID)
  - Use `codegen config show` to view current configuration

#### 3. AuthenticationCLIError
- **Exit Code**: 3
- **Purpose**: Authentication and authorization failures
- **Common Causes**: Invalid API tokens, expired credentials, insufficient permissions
- **Default Suggestions**:
  - Check your API token with `codegen auth status`
  - Set your token with `codegen config set api-token YOUR_TOKEN`
  - Visit https://codegen.com/settings to generate a new token

#### 4. ValidationCLIError
- **Exit Code**: 4
- **Purpose**: Input validation failures
- **Features**: Includes field-specific error details
- **Common Causes**: Invalid command arguments, malformed input data
- **Default Suggestions**:
  - Check the command syntax with `codegen COMMAND --help`
  - Verify your input parameters and try again

#### 5. NetworkCLIError
- **Exit Code**: 5
- **Purpose**: Network connectivity issues
- **Common Causes**: Internet connection problems, DNS failures, firewall blocks
- **Default Suggestions**:
  - Check your internet connection
  - Verify the API endpoint is accessible
  - Try again in a few moments
  - Use `--verbose` for more network details

### Additional Error Codes

- **Exit Code 6**: Rate limit exceeded
- **Exit Code 7**: Resource not found
- **Exit Code 8**: Request timeout
- **Exit Code 9**: Server error
- **Exit Code 10**: Generic API error
- **Exit Code 130**: Keyboard interrupt (Ctrl+C)

## SDK Error Translation

The CLI automatically translates SDK exceptions into user-friendly CLI errors:

```python
# SDK Error -> CLI Error Translation
AuthenticationError -> AuthenticationCLIError
ValidationError -> ValidationCLIError
RateLimitError -> CLIError (exit code 6)
NotFoundError -> CLIError (exit code 7)
TimeoutError -> CLIError (exit code 8)
NetworkError -> NetworkCLIError
ServerError -> CLIError (exit code 9)
```

### Translation Features

- **Contextual Messages**: Error messages are rewritten for CLI users
- **Actionable Suggestions**: Each error type includes specific suggestions
- **Field Error Mapping**: Validation errors include field-specific details
- **Rate Limit Information**: Rate limit errors include retry timing

## Rich UI Formatting

Errors are displayed using Rich formatting for better readability:

### Error Panel Structure

```
┌─ CLI Error ─────────────────────────────────────┐
│ Error: Authentication failed: Invalid API token │
│                                                 │
│ Suggestions:                                    │
│   • Verify your API token is correct and active│
│   • Check if your token has required permissions│
│   • Generate a new token at https://...        │
└─────────────────────────────────────────────────┘
```

### Features

- **Color Coding**: Errors in red, suggestions in green, details in yellow
- **Structured Layout**: Clear separation between error message, details, and suggestions
- **Field Errors**: Validation errors show field-specific issues
- **Rich Text**: Support for bold, italic, and colored text

## Automatic Retry System

The CLI includes sophisticated retry mechanisms for handling transient failures:

### Retry Configuration

```python
# Default retry settings
max_retries = 3
retry_delay = 1.0  # seconds
retry_backoff_factor = 2.0
```

### Retry Behavior

1. **Exponential Backoff**: Delays increase exponentially (1s, 2s, 4s, ...)
2. **Rate Limit Handling**: Respects `Retry-After` headers
3. **Error Type Filtering**: Only retries appropriate error types
4. **Circuit Breaking**: Prevents cascading failures

### Retryable Errors

- Network errors (connection failures, DNS issues)
- Timeout errors (request timeouts)
- Server errors (5xx HTTP status codes)
- Rate limit errors (with proper delay)

### Non-Retryable Errors

- Authentication errors (invalid credentials)
- Validation errors (malformed input)
- Authorization errors (insufficient permissions)
- Client errors (4xx HTTP status codes, except 429)

## Context Management

The `ErrorHandler` context manager provides comprehensive error handling:

```python
with ErrorHandler(verbose=False) as handler:
    # Your CLI command logic here
    result = api_call()
```

### Features

- **Automatic Translation**: Converts SDK errors to CLI errors
- **Proper Exit Codes**: Sets appropriate exit codes for different error types
- **Keyboard Interrupt Handling**: Graceful handling of Ctrl+C
- **Verbose Mode**: Detailed error information when requested

## Usage Examples

### Basic Error Handling

```python
from cli.core.errors import ErrorHandler, CLIError

def my_command():
    with ErrorHandler(verbose=False):
        # Command logic that might raise errors
        if not validate_input():
            raise ValidationCLIError("Invalid input provided")
        
        result = api.call_endpoint()
        return result
```

### Custom Error Creation

```python
from cli.core.errors import CLIError

# Create a custom error with suggestions
error = CLIError(
    message="Operation failed",
    exit_code=1,
    suggestions=[
        "Check your network connection",
        "Verify your API token",
        "Try again later"
    ],
    details="Additional context about the failure"
)
```

### Error Translation

```python
from cli.core.errors import translate_sdk_error
from codegen_api import AuthenticationError

try:
    api.authenticate()
except AuthenticationError as e:
    cli_error = translate_sdk_error(e)
    # cli_error is now an AuthenticationCLIError with user-friendly message
```

## Configuration

### Environment Variables

Control error handling behavior through environment variables:

```bash
# Retry configuration
export CODEGEN_MAX_RETRIES=5
export CODEGEN_RETRY_DELAY=2.0
export CODEGEN_RETRY_BACKOFF=3.0

# Logging configuration
export CODEGEN_LOG_LEVEL=DEBUG
export CODEGEN_LOG_FILE=/path/to/logfile
```

### Configuration File

```yaml
# codegen.yaml
api:
  max_retries: 5
  retry_delay: 2.0
  retry_backoff_factor: 3.0

log:
  level: DEBUG
  file: /path/to/logfile
```

## Best Practices

### For CLI Command Developers

1. **Use ErrorHandler**: Always wrap command logic in `ErrorHandler`
2. **Provide Context**: Include relevant details in error messages
3. **Actionable Suggestions**: Ensure suggestions are specific and helpful
4. **Appropriate Exit Codes**: Use the correct exit code for each error type
5. **Validate Early**: Check inputs before making API calls

### For Users

1. **Read Suggestions**: Error messages include specific guidance
2. **Use Verbose Mode**: Add `--verbose` for detailed error information
3. **Check Configuration**: Use `codegen config validate` to verify setup
4. **Monitor Logs**: Enable logging for troubleshooting persistent issues

### For Integrations

1. **Check Exit Codes**: Use exit codes to determine error types programmatically
2. **Parse JSON Output**: Use `--output json` for machine-readable error information
3. **Handle Retries**: Implement your own retry logic for non-retryable errors
4. **Monitor Rate Limits**: Respect rate limit information in error responses

## Troubleshooting

### Common Issues

#### "API token is required"
- **Cause**: Missing or invalid API token
- **Solution**: Set token with `codegen config set api-token YOUR_TOKEN`

#### "Network error: Connection failed"
- **Cause**: Network connectivity issues
- **Solution**: Check internet connection, verify API endpoint accessibility

#### "Rate limit exceeded"
- **Cause**: Too many requests in a short time
- **Solution**: Wait for the specified retry period, consider upgrading plan

#### "Resource not found"
- **Cause**: Invalid resource ID or insufficient permissions
- **Solution**: Verify resource ID, check access permissions

### Debug Mode

Enable verbose logging for detailed error information:

```bash
codegen --verbose command
# or
export CODEGEN_LOG_LEVEL=DEBUG
codegen command
```

### Log Analysis

Error logs include structured information for analysis:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "ERROR",
  "logger": "cli.commands.agent",
  "message": "API call failed",
  "error_type": "NetworkError",
  "exit_code": 5,
  "suggestions": ["Check internet connection", "Try again later"]
}
```

## Advanced Features

### Custom Error Handlers

Extend the error handling system for specific use cases:

```python
class CustomCLIError(CLIError):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            exit_code=11,  # Custom exit code
            suggestions=["Custom suggestion 1", "Custom suggestion 2"]
        )

# Register custom error translation
def translate_custom_error(error):
    if isinstance(error, MyCustomSDKError):
        return CustomCLIError(f"Custom error: {error.message}")
    return translate_sdk_error(error)
```

### Error Analytics

The error handling system supports optional analytics collection:

```python
# Enable error analytics (with user consent)
config.set("analytics.enabled", True)
config.set("analytics.error_reporting", True)
```

### Integration with Monitoring

Export error metrics for monitoring systems:

```python
from cli.core.errors import ErrorHandler

class MonitoringErrorHandler(ErrorHandler):
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Send metrics to monitoring system
            metrics.increment("cli.errors", tags={"type": exc_type.__name__})
        
        return super().__exit__(exc_type, exc_val, exc_tb)
```

## API Reference

### Classes

#### CLIError
Base class for CLI errors.

**Parameters:**
- `message` (str): Error message
- `exit_code` (int): Exit code (default: 1)
- `suggestions` (List[str]): List of suggestions (optional)
- `details` (str): Additional details (optional)

#### ErrorHandler
Context manager for error handling.

**Parameters:**
- `verbose` (bool): Enable verbose error reporting

### Functions

#### translate_sdk_error(error: Exception) -> CLIError
Translates SDK exceptions to CLI errors.

#### handle_cli_error(error: CLIError) -> None
Displays CLI error with Rich formatting.

#### handle_keyboard_interrupt() -> None
Handles keyboard interrupt gracefully.

#### handle_unexpected_error(error: Exception, verbose: bool = False) -> None
Handles unexpected errors with appropriate detail level.

---

For more information, see:
- [Configuration Guide](configuration.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Developer Guide](developer_guide.md)

