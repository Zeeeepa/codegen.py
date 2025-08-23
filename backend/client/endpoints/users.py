"""
Client for the Users API endpoints.
"""

from typing import Any, Dict, List, Optional, cast

from codegen_client.models.users import User, UserResponse
from codegen_client.utils.pagination import get_paginated_results


class UsersClient:
    """
    Client for the Users API endpoints.

    This client provides methods for interacting with user-related endpoints,
    such as listing users, getting user details, and getting current user info.
    """

    def __init__(self, client: Any):
        """
        Initialize the Users API client.

        Args:
            client: The base API client
        """
        self.client = client

    def get_users(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> UserResponse:
        """
        Get a list of users in an organization.

        Args:
            org_id: Organization ID
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return (for pagination)

        Returns:
            UserResponse: Paginated response with user data

        Raises:
            CodegenApiError: If the API request fails
        """
        response_data = self.client.get(
            f"/organizations/{org_id}/users",
            params={"skip": skip, "limit": limit},
        )
        return UserResponse.parse_obj(response_data)

    def get_all_users(
        self,
        org_id: int,
        limit: Optional[int] = None,
    ) -> List[User]:
        """
        Get all users in an organization.

        This method automatically handles pagination to retrieve all users.

        Args:
            org_id: Organization ID
            limit: Maximum number of users to return (None for all)

        Returns:
            List[User]: List of all users in the organization

        Raises:
            CodegenApiError: If the API request fails
        """
        return get_paginated_results(
            lambda page, page_size: self.get_users(
                org_id=org_id,
                skip=(page - 1) * page_size,
                limit=page_size,
            ),
            User,
            limit=limit,
        )

    def get_user(self, org_id: int, user_id: int) -> User:
        """
        Get details for a specific user in an organization.

        Args:
            org_id: Organization ID
            user_id: User ID

        Returns:
            User: User details

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the user is not found
        """
        response_data = self.client.get(f"/organizations/{org_id}/users/{user_id}")
        return User.parse_obj(response_data)

    def get_current_user_info(self) -> Dict[str, Any]:
        """
        Get information about the current user.

        Returns:
            Dict[str, Any]: Current user information

        Raises:
            CodegenApiError: If the API request fails
            CodegenAuthError: If authentication fails
        """
        return self.client.get("/users/me")

