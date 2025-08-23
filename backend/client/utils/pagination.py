"""
Utilities for handling pagination in API responses.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from codegen_client.models.base import PaginatedResponse

# Type variable for the item type in paginated responses
T = TypeVar("T")
# Type variable for the response type
R = TypeVar("R", bound=PaginatedResponse)

logger = logging.getLogger(__name__)


def get_paginated_results(
    fetch_page_func: Callable[[int, int], R],
    item_type: type,
    limit: Optional[int] = None,
    page_size: int = 100,
) -> List[T]:
    """
    Fetch all pages of paginated results.

    Args:
        fetch_page_func: Function that fetches a page of results
        item_type: Type of the items in the response
        limit: Maximum number of items to fetch (None for all)
        page_size: Number of items per page

    Returns:
        List[T]: All items from all pages
    """
    all_items: List[T] = []
    page = 1
    total_pages = 1  # Will be updated after first request

    while page <= total_pages:
        # Fetch the current page
        response = fetch_page_func(page, page_size)
        
        # Add items to the result list
        all_items.extend(cast(List[T], response.items))
        
        # Update total pages
        total_pages = response.pages
        
        # Check if we've reached the limit
        if limit and len(all_items) >= limit:
            all_items = all_items[:limit]
            break
        
        # Move to the next page
        page += 1
    
    return all_items

