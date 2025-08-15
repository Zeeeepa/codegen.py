"""
Logging and Debugging System

This module provides comprehensive logging with multiple verbosity levels,
structured output, and integration with the existing SDK logging.
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

# Global logging configuration
_verbosity_level = 1  # Default: INFO level
_loggers: Dict[str, logging.Logger] = {}
_console = Console(stderr=True)


class CLIFormatter(logging.Formatter):
    """Custom formatter for CLI logging with color support."""
    
    COLORS = {
        'DEBUG': 'dim blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold red',
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and structure."""
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, 'white')
        
        # Create formatted message
        if _verbosity_level >= 3:  # -vvv: Show all details
            return f"[{level_color}]{record.levelname}[/{level_color}] {record.name}: {record.getMessage()}"
        elif _verbosity_level >= 2:  # -vv: Show logger name
            return f"[{level_color}]{record.levelname}[/{level_color}] {record.name}: {record.getMessage()}"
        else:  # -v: Simple format
            return f"[{level_color}]{record.levelname}[/{level_color}] {record.getMessage()}"


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info'):
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False,
    quiet: bool = False
) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_format: Use JSON formatting
        quiet: Suppress console output
    """
    # Determine log level
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        # Map verbosity to log levels
        level_map = {
            0: logging.WARNING,  # Quiet
            1: logging.INFO,     # Default
            2: logging.DEBUG,    # Verbose
            3: logging.DEBUG,    # Very verbose
        }
        log_level = level_map.get(_verbosity_level, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (unless quiet)
    if not quiet:
        if json_format:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler = RichHandler(
                console=_console,
                show_time=_verbosity_level >= 3,
                show_path=_verbosity_level >= 3,
                markup=True,
                rich_tracebacks=True,
            )
            console_handler.setFormatter(CLIFormatter())
        
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Ensure log directory exists
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            if json_format:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
            file_handler.setLevel(logging.DEBUG)  # Always debug level for files
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            # Don't fail if we can't set up file logging
            console = Console(stderr=True)
            console.print(f"[yellow]Warning: Could not set up file logging: {e}[/yellow]")


def set_verbosity_level(level: int) -> None:
    """
    Set the global verbosity level.
    
    Args:
        level: Verbosity level (0=quiet, 1=normal, 2=verbose, 3=very verbose)
    """
    global _verbosity_level
    _verbosity_level = max(0, min(3, level))
    
    # Reconfigure logging with new level
    setup_logging()


def get_verbosity_level() -> int:
    """Get the current verbosity level."""
    return _verbosity_level


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with CLI-specific configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]


class DebugContext:
    """Context manager for debug information collection."""
    
    def __init__(self, operation: str):
        self.operation = operation
        self.logger = get_logger(__name__)
        self.debug_info: Dict[str, Any] = {}
    
    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"Operation failed: {self.operation}", exc_info=True)
            if _verbosity_level >= 2:
                self._dump_debug_info()
        else:
            self.logger.debug(f"Operation completed: {self.operation}")
    
    def add_info(self, key: str, value: Any) -> None:
        """Add debug information."""
        self.debug_info[key] = value
        self.logger.debug(f"Debug info - {key}: {value}")
    
    def _dump_debug_info(self) -> None:
        """Dump collected debug information."""
        if self.debug_info:
            console = Console(stderr=True)
            console.print("\n[bold yellow]Debug Information:[/bold yellow]")
            for key, value in self.debug_info.items():
                console.print(f"  {key}: {value}")


def log_api_request(
    method: str,
    url: str,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log API request information.
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration in seconds
        request_id: Request ID for tracing
    """
    logger = get_logger("api")
    
    # Sanitize URL (remove sensitive info)
    sanitized_url = url
    if "token=" in url:
        sanitized_url = url.split("token=")[0] + "token=***"
    
    if status_code:
        level = logging.INFO if status_code < 400 else logging.WARNING
        message = f"{method} {sanitized_url} -> {status_code}"
        if duration:
            message += f" ({duration:.2f}s)"
        if request_id:
            message += f" [req_id: {request_id}]"
        logger.log(level, message)
    else:
        logger.debug(f"{method} {sanitized_url}")


def log_cli_command(command: str, args: Dict[str, Any]) -> None:
    """
    Log CLI command execution.
    
    Args:
        command: Command name
        args: Command arguments (sensitive values will be redacted)
    """
    logger = get_logger("cli")
    
    # Redact sensitive arguments
    safe_args = {}
    sensitive_keys = {'token', 'password', 'secret', 'key', 'auth'}
    
    for key, value in args.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_args[key] = "***"
        else:
            safe_args[key] = value
    
    logger.info(f"Command: {command}, Args: {safe_args}")


def create_debug_report() -> Dict[str, Any]:
    """
    Create a debug report with system and configuration information.
    
    Returns:
        Debug report dictionary
    """
    import platform
    import sys
    from ..core.config import get_config
    
    config = get_config()
    
    report = {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_executable": sys.executable,
        },
        "cli": {
            "verbosity_level": _verbosity_level,
            "config_file": config.config_file,
        },
        "environment": {
            k: "***" if "token" in k.lower() or "secret" in k.lower() else v
            for k, v in config.show()["environment_variables"].items()
        },
        "loggers": list(_loggers.keys()),
    }
    
    return report


def save_debug_report(file_path: Optional[str] = None) -> str:
    """
    Save debug report to file.
    
    Args:
        file_path: Optional file path, defaults to debug-report.json
        
    Returns:
        Path to saved report file
    """
    if not file_path:
        file_path = f"debug-report-{int(time.time())}.json"
    
    report = create_debug_report()
    
    with open(file_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger = get_logger(__name__)
    logger.info(f"Debug report saved to: {file_path}")
    
    return file_path


# Performance logging utilities
import time
from functools import wraps


def log_performance(func):
    """Decorator to log function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper
