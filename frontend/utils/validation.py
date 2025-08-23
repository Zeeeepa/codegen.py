"""
Validation utilities for the Codegen UI.

This module provides utility functions for validating input in the Codegen UI.
"""

import re
from typing import Optional


def validate_input(value: str, min_length: int = 0, max_length: int = 100) -> bool:
    """Validate an input value.
    
    Args:
        value: The value to validate.
        min_length: The minimum length of the value.
        max_length: The maximum length of the value.
    
    Returns:
        True if the value is valid, False otherwise.
    """
    if not value:
        return min_length == 0
    
    return min_length <= len(value) <= max_length


def validate_email(email: str) -> bool:
    """Validate an email address.
    
    Args:
        email: The email address to validate.
    
    Returns:
        True if the email address is valid, False otherwise.
    """
    if not email:
        return False
    
    # Simple email validation regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

