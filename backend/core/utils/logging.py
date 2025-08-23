"""
Logging utilities for the Codegen API client.

This module contains functions for configuring and using logging.
"""

import logging
import sys
from typing import Optional, Dict, Any

from backend.core.models.enums import LogLevel


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the Codegen API client.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_string: Custom format string for log messages.
        log_file: Path to log file. If None, logs to stderr.
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    
    # Set up format string
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure handlers
    handlers = []
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Add stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers.append(stderr_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name.
        
    Returns:
        A configured logger.
    """
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Any] = None,
    level: str = "DEBUG",
) -> None:
    """Log an API request.
    
    Args:
        logger: Logger to use.
        method: HTTP method.
        url: Request URL.
        params: Query parameters.
        headers: Request headers.
        data: Request body.
        level: Log level.
    """
    # Sanitize headers to remove sensitive information
    safe_headers = None
    if headers:
        safe_headers = headers.copy()
        if "Authorization" in safe_headers:
            safe_headers["Authorization"] = "***"
    
    # Log the request
    log_message = f"API Request: {method} {url}"
    if params:
        log_message += f"\nParams: {params}"
    if safe_headers:
        log_message += f"\nHeaders: {safe_headers}"
    if data:
        log_message += f"\nData: {data}"
    
    # Log at the specified level
    log_func = getattr(logger, level.lower())
    log_func(log_message)


def log_response(
    logger: logging.Logger,
    status_code: int,
    url: str,
    response_data: Optional[Any] = None,
    duration: Optional[float] = None,
    level: Optional[str] = None,
) -> None:
    """Log an API response.
    
    Args:
        logger: Logger to use.
        status_code: HTTP status code.
        url: Request URL.
        response_data: Response body.
        duration: Request duration in seconds.
        level: Log level. If None, level is determined by status code.
    """
    # Determine log level based on status code if not specified
    if level is None:
        if status_code < 400:
            level = "DEBUG"
        elif status_code < 500:
            level = "WARNING"
        else:
            level = "ERROR"
    
    # Log the response
    log_message = f"API Response: {status_code} {url}"
    if duration is not None:
        log_message += f" ({duration:.2f}s)"
    if response_data:
        log_message += f"\nData: {response_data}"
    
    # Log at the specified level
    log_func = getattr(logger, level.lower())
    log_func(log_message)
