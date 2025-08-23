"""
Base models for the Codegen API client.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# Type variable for the item type in paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Base model for paginated API responses.

    Attributes:
        items: List of items in the current page
        total: Total number of items across all pages
        page: Current page number
        size: Number of items per page
        pages: Total number of pages
    """

    items: List[T] = Field(default_factory=list)
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def parse_response(cls, response_data: Dict[str, Any], item_model: type) -> "PaginatedResponse":
        """
        Parse a paginated response from the API.

        Args:
            response_data: Raw response data from the API
            item_model: Pydantic model for the items in the response

        Returns:
            PaginatedResponse: Parsed paginated response
        """
        items_data = response_data.get("items", [])
        items = [item_model.parse_obj(item) for item in items_data]
        
        return cls(
            items=items,
            total=response_data.get("total", 0),
            page=response_data.get("page", 1),
            size=response_data.get("size", len(items)),
            pages=response_data.get("pages", 1),
        )

