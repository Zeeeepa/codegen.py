"""
Logging configuration for the Enhanced Codegen UI.

This module provides logging configuration for the Enhanced Codegen UI,
setting up logging to file and console with appropriate formatting.
"""

import os
import logging
import logging.handlers
from typing import Optional


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: int = logging.INFO,
    console_level: int = logging.INFO,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5
):
    """
    Set up logging for the Enhanced Codegen UI.
    
    Args:
        log_dir: Directory to store log files (default: ~/.codegen/logs)
        log_level: Log level for file logging (default: INFO)
        console_level: Log level for console logging (default: INFO)
        max_bytes: Maximum log file size in bytes (default: 10 MB)
        backup_count: Number of backup log files to keep (default: 5)
    """
    # Set log directory
    log_dir = log_dir or os.path.expanduser("~/.codegen/logs")
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log file path
    log_file = os.path.join(log_dir, "codegen_ui.log")
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log setup complete
    logger.info(f"Logging setup complete, logging to {log_file}")
    
    return logger

