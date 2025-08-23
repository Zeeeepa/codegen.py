"""
Models for organization-related API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from codegen_client.models.base import PaginatedResponse


class OrganizationSettings(BaseModel):
    """
    Model representing organization settings.

    Attributes:
        enable_pr_creation: Whether PR creation is enabled for the organization
        enable_rules_detection: Whether rules detection is enabled for the organization
    """

    enable_pr_creation: bool = True
    enable_rules_detection: bool = True


class Organization(BaseModel):
    """
    Model representing an organization.

    Attributes:
        id: Organization ID
        name: Organization name
        settings: Organization settings
    """

    id: int
    name: Optional[str] = None
    settings: OrganizationSettings = Field(default_factory=OrganizationSettings)


class OrganizationResponse(PaginatedResponse[Organization]):
    """
    Paginated response for organization listings.
    """

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "OrganizationResponse":
        """
        Parse an organization response from the API.

        Args:
            obj: Raw response data from the API

        Returns:
            OrganizationResponse: Parsed organization response
        """
        return cls.parse_response(obj, Organization)

