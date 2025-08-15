# Developer Guide: Error Handling System

This guide is for developers who want to extend, customize, or contribute to the Codegen CLI's error handling system. The system is designed to be modular, extensible, and maintainable.

## Architecture Overview

The error handling system consists of several key components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Commands  │───▶│  ErrorHandler    │───▶│  Rich Display   │
└─────────────────┘    │  Context Manager │    └─────────────────┘
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ SDK Error        │
                       │ Translation      │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ CLI Error        │
                       │ Classification   │
                       └──────────────────┘
```

### Core Components

1. **CLI Error Classes** (`cli/core/errors.py`): Hierarchical error types
2. **Error Translation** (`translate_sdk_error`): SDK to CLI error mapping
3. **Error Handler** (`ErrorHandler`): Context manager for error handling
4. **Rich Display** (`handle_cli_error`): User-friendly error formatting
5. **Retry System** (`codegen_api.py`): Automatic retry with backoff

## Extending Error Types

### Creating Custom Error Classes

```python
from cli.core.errors import CLIError

class CustomOperationError(CLIError):
    """Error for custom operations."""
    
    def __init__(self, message: str, operation: str, suggestions: Optional[List[str]] = None):
        self.operation = operation
        
        default_suggestions = [
            f"Verify the {operation} parameters",
            f"Check if {operation} is supported",
            "Use --verbose for more details"
        ]
        
        super().__init__(
            message=message,
            exit_code=20,  # Use unique exit codes > 10
            suggestions=suggestions or default_suggestions
        )
```

### Error Class Guidelines

1. **Inherit from appropriate base class:**
   - `CLIError` for general errors
   - `ConfigurationError` for config-related errors
   - `ValidationCLIError` for input validation errors

2. **Use unique exit codes:**
   - Codes 1-10 are reserved for system errors
   - Use codes 11+ for custom errors
   - Document exit codes in your module

3. **Provide helpful suggestions:**
   - Make suggestions specific and actionable
   - Include relevant command examples
   - Reference documentation when appropriate

4. **Include context information:**
   ```python
   class DatabaseError(CLIError):
       def __init__(self, message: str, query: str = None, table: str = None):
           self.query = query
           self.table = table
           
           suggestions = ["Check database connection"]
           if table:
               suggestions.append(f"Verify table '{table}' exists")
           if query:
               suggestions.append("Review query syntax")
           
           super().__init__(message, exit_code=15, suggestions=suggestions)
   ```

## Extending Error Translation

### Adding SDK Error Translation

```python
from cli.core.errors import translate_sdk_error, CLIError
from your_sdk import YourCustomSDKError

def translate_custom_sdk_error(error: Exception) -> CLIError:
    """Extend SDK error translation for custom errors."""
    
    if isinstance(error, YourCustomSDKError):
        return CLIError(
            f"Custom SDK error: {error.message}",
            exit_code=21,
            suggestions=[
                "Check custom SDK configuration",
                "Verify custom SDK version compatibility"
            ]
        )
    
    # Fall back to default translation
    return translate_sdk_error(error)

# Register custom translation
original_translate = translate_sdk_error
def enhanced_translate_sdk_error(error: Exception) -> CLIError:
    try:
        return translate_custom_sdk_error(error)
    except:
        return original_translate(error)

# Monkey patch (or use proper registration system)
import cli.core.errors
cli.core.errors.translate_sdk_error = enhanced_translate_sdk_error
```

### Translation Best Practices

1. **Preserve original error information:**
   ```python
   cli_error = CustomCLIError(f"Operation failed: {sdk_error.message}")
   cli_error.original_error = sdk_error  # Preserve for debugging
   ```

2. **Extract useful context:**
   ```python
   if hasattr(sdk_error, 'field_errors'):
       cli_error.field_errors = sdk_error.field_errors
   
   if hasattr(sdk_error, 'retry_after'):
       cli_error.suggestions.insert(0, f"Wait {sdk_error.retry_after} seconds")
   ```

3. **Map error codes appropriately:**
   ```python
   # Map SDK error codes to CLI exit codes
   SDK_TO_CLI_EXIT_CODES = {
       1001: 15,  # Custom operation error
       1002: 16,  # Custom validation error
       1003: 17,  # Custom permission error
   }
   
   exit_code = SDK_TO_CLI_EXIT_CODES.get(sdk_error.code, 1)
   ```

## Custom Error Handlers

### Creating Specialized Error Handlers

```python
from cli.core.errors import ErrorHandler
import logging

class LoggingErrorHandler(ErrorHandler):
    """Error handler that logs all errors to a file."""
    
    def __init__(self, verbose: bool = False, log_file: str = None):
        super().__init__(verbose)
        self.logger = logging.getLogger(__name__)
        if log_file:
            handler = logging.FileHandler(log_file)
            self.logger.addHandler(handler)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"CLI error: {exc_type.__name__}: {exc_val}")
        
        return super().__exit__(exc_type, exc_val, exc_tb)

class MetricsErrorHandler(ErrorHandler):
    """Error handler that sends metrics to monitoring system."""
    
    def __init__(self, verbose: bool = False, metrics_client=None):
        super().__init__(verbose)
        self.metrics = metrics_client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and self.metrics:
            self.metrics.increment('cli.errors', tags={
                'error_type': exc_type.__name__,
                'exit_code': getattr(exc_val, 'exit_code', 1)
            })
        
        return super().__exit__(exc_type, exc_val, exc_tb)
```

### Error Handler Composition

```python
class CompositeErrorHandler:
    """Compose multiple error handlers."""
    
    def __init__(self, handlers: List[ErrorHandler]):
        self.handlers = handlers
    
    def __enter__(self):
        for handler in self.handlers:
            handler.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Call all handlers, but only suppress if all suppress
        suppress_results = []
        for handler in self.handlers:
            result = handler.__exit__(exc_type, exc_val, exc_tb)
            suppress_results.append(result)
        
        # Only suppress if all handlers want to suppress
        return all(suppress_results)

# Usage
with CompositeErrorHandler([
    LoggingErrorHandler(log_file='errors.log'),
    MetricsErrorHandler(metrics_client=metrics),
    ErrorHandler(verbose=True)
]):
    # Command logic here
    pass
```

## Customizing Error Display

### Custom Rich Formatting

```python
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from cli.core.errors import CLIError

def custom_handle_cli_error(error: CLIError) -> None:
    """Custom error display with additional formatting."""
    console = Console(stderr=True)
    
    # Create custom error text with icons
    error_text = Text()
    error_text.append("🚨 ", style="red")
    error_text.append("Error: ", style="bold red")
    error_text.append(error.message, style="red")
    
    # Add custom sections
    panel_content = [error_text]
    
    # Add error code information
    if hasattr(error, 'error_code'):
        panel_content.append("")
        panel_content.append(Text(f"Error Code: {error.error_code}", style="dim"))
    
    # Add timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    panel_content.append("")
    panel_content.append(Text(f"Time: {timestamp}", style="dim"))
    
    # Add suggestions with custom formatting
    if error.suggestions:
        panel_content.append("")
        panel_content.append(Text("💡 Suggestions:", style="bold yellow"))
        for i, suggestion in enumerate(error.suggestions, 1):
            panel_content.append(Text(f"  {i}. {suggestion}", style="yellow"))
    
    # Custom panel styling
    console.print(Panel(
        "\n".join(str(item) for item in panel_content),
        title="[bold red]🔥 CLI Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))
```

### Conditional Error Display

```python
def smart_handle_cli_error(error: CLIError, context: dict = None) -> None:
    """Handle errors with context-aware display."""
    
    # Different display for different contexts
    if context and context.get('output_format') == 'json':
        # JSON output for machine consumption
        import json
        error_data = {
            'error': True,
            'message': error.message,
            'exit_code': error.exit_code,
            'suggestions': error.suggestions,
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_data, indent=2))
    
    elif context and context.get('quiet'):
        # Minimal output for quiet mode
        print(f"Error: {error.message}", file=sys.stderr)
    
    else:
        # Full rich display
        custom_handle_cli_error(error)
```

## Retry System Extensions

### Custom Retry Strategies

```python
import time
import random
from functools import wraps

def retry_with_jitter(max_retries: int = 3, base_delay: float = 1.0, 
                     max_jitter: float = 0.1):
    """Retry decorator with jitter to prevent thundering herd."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise
                    
                    # Calculate delay with jitter
                    delay = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, max_jitter)
                    total_delay = delay + jitter
                    
                    time.sleep(total_delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def retry_with_circuit_breaker(failure_threshold: int = 5, 
                              recovery_timeout: int = 60):
    """Retry with circuit breaker pattern."""
    
    class CircuitBreaker:
        def __init__(self):
            self.failure_count = 0
            self.last_failure_time = None
            self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    circuit_breaker = CircuitBreaker()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Check circuit breaker state
            if circuit_breaker.state == 'OPEN':
                if (now - circuit_breaker.last_failure_time) > recovery_timeout:
                    circuit_breaker.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker
                if circuit_breaker.state == 'HALF_OPEN':
                    circuit_breaker.state = 'CLOSED'
                    circuit_breaker.failure_count = 0
                
                return result
                
            except Exception as e:
                circuit_breaker.failure_count += 1
                circuit_breaker.last_failure_time = now
                
                if circuit_breaker.failure_count >= failure_threshold:
                    circuit_breaker.state = 'OPEN'
                
                raise
        
        return wrapper
    return decorator
```

### Retry Configuration

```python
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    jitter: bool = True
    retry_on: tuple = (NetworkError, TimeoutError, ServerError)
    stop_on: tuple = (AuthenticationError, ValidationError)

def configurable_retry(config: RetryConfig):
    """Highly configurable retry decorator."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should stop retrying
                    if isinstance(e, config.stop_on):
                        raise
                    
                    # Check if we should retry
                    if not isinstance(e, config.retry_on):
                        raise
                    
                    if attempt == config.max_retries:
                        raise
                    
                    # Calculate delay
                    delay = min(
                        config.base_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        delay += random.uniform(0, delay * 0.1)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
```

## Testing Error Handling

### Unit Testing Error Classes

```python
import pytest
from cli.core.errors import CLIError, ValidationCLIError

class TestCustomErrors:
    def test_cli_error_creation(self):
        error = CLIError("Test message", exit_code=5, suggestions=["Fix it"])
        
        assert error.message == "Test message"
        assert error.exit_code == 5
        assert error.suggestions == ["Fix it"]
        assert str(error) == "Test message"
    
    def test_validation_error_with_field_errors(self):
        field_errors = {"email": ["Invalid format"]}
        error = ValidationCLIError("Validation failed", field_errors=field_errors)
        
        assert error.field_errors == field_errors
        assert error.exit_code == 4
    
    def test_custom_error_class(self):
        class CustomError(CLIError):
            def __init__(self, message: str):
                super().__init__(message, exit_code=99)
        
        error = CustomError("Custom message")
        assert error.exit_code == 99
```

### Testing Error Translation

```python
from cli.core.errors import translate_sdk_error
from codegen_api import AuthenticationError, ValidationError

class TestErrorTranslation:
    def test_authentication_error_translation(self):
        sdk_error = AuthenticationError("Invalid token", 401)
        cli_error = translate_sdk_error(sdk_error)
        
        assert "Authentication failed" in cli_error.message
        assert cli_error.exit_code == 3
        assert len(cli_error.suggestions) > 0
    
    def test_validation_error_with_field_errors(self):
        sdk_error = ValidationError("Bad input", 400)
        sdk_error.field_errors = {"name": ["Required"]}
        
        cli_error = translate_sdk_error(sdk_error)
        
        assert isinstance(cli_error, ValidationCLIError)
        assert "Fix name: Required" in cli_error.suggestions
```

### Testing Error Handlers

```python
from cli.core.errors import ErrorHandler, CLIError
from unittest.mock import patch

class TestErrorHandler:
    @patch('sys.exit')
    @patch('cli.core.errors.handle_cli_error')
    def test_error_handler_with_cli_error(self, mock_handle, mock_exit):
        error = CLIError("Test error", exit_code=5)
        
        with pytest.raises(SystemExit):
            with ErrorHandler():
                raise error
        
        mock_handle.assert_called_once_with(error)
        mock_exit.assert_called_once_with(5)
    
    def test_error_handler_no_exception(self):
        with ErrorHandler() as handler:
            pass  # Should complete normally
```

### Integration Testing

```python
import subprocess
import json

class TestCLIErrorIntegration:
    def test_authentication_error_exit_code(self):
        """Test that authentication errors return correct exit code."""
        result = subprocess.run(
            ['codegen', 'agent', 'list'],
            env={'CODEGEN_API_TOKEN': 'invalid'},
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 3  # Authentication error
        assert "Authentication failed" in result.stderr
    
    def test_error_output_format(self):
        """Test error output in different formats."""
        result = subprocess.run(
            ['codegen', '--output', 'json', 'agent', 'list'],
            env={'CODEGEN_API_TOKEN': 'invalid'},
            capture_output=True,
            text=True
        )
        
        # Should still return error info even with JSON output
        assert result.returncode == 3
        
        # Try to parse as JSON (might be in stderr)
        try:
            error_data = json.loads(result.stderr)
            assert 'error' in error_data
        except json.JSONDecodeError:
            # Error might be in human-readable format
            assert "Authentication failed" in result.stderr
```

## Performance Considerations

### Efficient Error Handling

1. **Lazy error message formatting:**
   ```python
   class LazyErrorMessage:
       def __init__(self, template: str, **kwargs):
           self.template = template
           self.kwargs = kwargs
       
       def __str__(self):
           return self.template.format(**self.kwargs)
   
   # Usage
   error = CLIError(LazyErrorMessage("Error in {operation}: {details}", 
                                   operation="upload", details=details))
   ```

2. **Avoid expensive operations in error paths:**
   ```python
   def handle_error(error):
       # Don't do expensive operations like network calls in error handlers
       # unless absolutely necessary
       if verbose_mode:
           # Only do expensive debugging when needed
           debug_info = collect_debug_info()
   ```

3. **Cache error translations:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def cached_translate_sdk_error(error_type: type, error_message: str) -> CLIError:
       # Cache common error translations
       pass
   ```

### Memory Management

1. **Avoid circular references:**
   ```python
   class CLIError(Exception):
       def __init__(self, message: str):
           self.message = message
           # Don't store references to large objects
           # self.context = large_context_object  # Avoid this
   ```

2. **Clean up resources in error handlers:**
   ```python
   class ResourceErrorHandler(ErrorHandler):
       def __init__(self, resources: List):
           super().__init__()
           self.resources = resources
       
       def __exit__(self, exc_type, exc_val, exc_tb):
           # Clean up resources even if error occurs
           for resource in self.resources:
               try:
                   resource.close()
               except:
                   pass  # Ignore cleanup errors
           
           return super().__exit__(exc_type, exc_val, exc_tb)
   ```

## Contributing Guidelines

### Code Style

1. **Follow existing patterns:**
   - Use the same error class hierarchy
   - Follow naming conventions (CLIError suffix)
   - Include docstrings and type hints

2. **Error message guidelines:**
   - Start with capital letter
   - Be specific and actionable
   - Avoid technical jargon for user-facing messages
   - Include context when helpful

3. **Suggestion guidelines:**
   - Provide specific commands when possible
   - Order suggestions by likelihood of success
   - Include links to documentation
   - Keep suggestions concise

### Testing Requirements

1. **Unit tests for all error classes**
2. **Integration tests for error flows**
3. **Test error message quality**
4. **Test exit codes**
5. **Test error translation**

### Documentation Requirements

1. **Update error handling documentation**
2. **Document new exit codes**
3. **Include usage examples**
4. **Update troubleshooting guide**

### Pull Request Checklist

- [ ] Error classes follow naming conventions
- [ ] Unique exit codes assigned and documented
- [ ] Helpful error messages and suggestions
- [ ] Unit tests for new error types
- [ ] Integration tests for error flows
- [ ] Documentation updated
- [ ] Backward compatibility maintained
- [ ] Performance impact considered

## Advanced Topics

### Internationalization

```python
from typing import Dict
import gettext

class I18nCLIError(CLIError):
    """Internationalized CLI error."""
    
    def __init__(self, message_key: str, locale: str = 'en', **kwargs):
        self.message_key = message_key
        self.locale = locale
        
        # Load translations
        translation = gettext.translation('cli_errors', 
                                        localedir='locales', 
                                        languages=[locale],
                                        fallback=True)
        
        message = translation.gettext(message_key).format(**kwargs)
        super().__init__(message)
```

### Error Analytics

```python
import json
from datetime import datetime
from pathlib import Path

class ErrorAnalytics:
    """Collect error analytics for improvement."""
    
    def __init__(self, analytics_file: str = None):
        self.analytics_file = analytics_file or Path.home() / '.codegen' / 'error_analytics.json'
    
    def record_error(self, error: CLIError, context: dict = None):
        """Record error occurrence for analytics."""
        if not self.analytics_file.parent.exists():
            self.analytics_file.parent.mkdir(parents=True)
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'message': error.message,
            'exit_code': error.exit_code,
            'context': context or {}
        }
        
        # Append to analytics file
        try:
            with open(self.analytics_file, 'a') as f:
                f.write(json.dumps(error_data) + '\n')
        except Exception:
            pass  # Don't fail on analytics errors
```

### Error Recovery Strategies

```python
from abc import ABC, abstractmethod

class ErrorRecoveryStrategy(ABC):
    """Base class for error recovery strategies."""
    
    @abstractmethod
    def can_recover(self, error: Exception) -> bool:
        """Check if this strategy can recover from the error."""
        pass
    
    @abstractmethod
    def recover(self, error: Exception) -> bool:
        """Attempt to recover from the error. Return True if successful."""
        pass

class TokenRefreshRecovery(ErrorRecoveryStrategy):
    """Recovery strategy for expired tokens."""
    
    def can_recover(self, error: Exception) -> bool:
        return isinstance(error, AuthenticationError) and "expired" in str(error).lower()
    
    def recover(self, error: Exception) -> bool:
        try:
            # Attempt to refresh token
            new_token = refresh_api_token()
            update_config_token(new_token)
            return True
        except Exception:
            return False

class RecoverableErrorHandler(ErrorHandler):
    """Error handler with recovery strategies."""
    
    def __init__(self, recovery_strategies: List[ErrorRecoveryStrategy] = None):
        super().__init__()
        self.recovery_strategies = recovery_strategies or []
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Try recovery strategies
            for strategy in self.recovery_strategies:
                if strategy.can_recover(exc_val):
                    if strategy.recover(exc_val):
                        return True  # Suppress the exception
        
        return super().__exit__(exc_type, exc_val, exc_tb)
```

---

This developer guide provides comprehensive information for extending and customizing the error handling system. For more specific examples and advanced use cases, refer to the source code and existing implementations.

