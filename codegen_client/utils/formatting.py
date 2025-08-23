"""
Utilities for formatting data in the Codegen API client.
"""

import datetime
from typing import Any, Dict, Optional


def format_date(date_str: Optional[str]) -> Optional[datetime.datetime]:
    """
    Format a date string from the API into a datetime object.

    Args:
        date_str: Date string from the API

    Returns:
        Optional[datetime.datetime]: Formatted datetime object, or None if the input is None
    """
    if not date_str:
        return None
    
    try:
        return datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def format_error_message(error_data: Dict[str, Any]) -> str:
    """
    Format an error message from the API response.

    Args:
        error_data: Error data from the API response

    Returns:
        str: Formatted error message
    """
    if "detail" in error_data:
        detail = error_data["detail"]
        if isinstance(detail, list) and detail:
            # Handle validation errors
            messages = []
            for error in detail:
                loc = ".".join(str(l) for l in error.get("loc", []))
                msg = error.get("msg", "Unknown error")
                if loc:
                    messages.append(f"{loc}: {msg}")
                else:
                    messages.append(msg)
            return "; ".join(messages)
        elif isinstance(detail, str):
            return detail
    
    # Fallback to a generic error message
    return "An error occurred while processing the request."

