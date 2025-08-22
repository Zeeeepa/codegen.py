"""
Base client for the Codegen API.
"""

import os
from typing import Any, Dict, Optional

import httpx

from codegen_client.config import CodegenConfig
from codegen_client.exceptions import (
    CodegenApiError,
    CodegenAuthError,
    CodegenRateLimitError,
    CodegenResourceNotFoundError,
    CodegenValidationError,
)
from codegen_client.endpoints.agents import AgentsClient
from codegen_client.endpoints.agents_alpha import AgentsAlphaClient
from codegen_client.endpoints.integrations import IntegrationsClient
from codegen_client.endpoints.multi_run_agent import MultiRunAgentClient
from codegen_client.endpoints.organizations import OrganizationsClient
from codegen_client.endpoints.repositories import RepositoriesClient
from codegen_client.endpoints.sandbox import SandboxClient
from codegen_client.endpoints.setup_commands import SetupCommandsClient
from codegen_client.endpoints.users import UsersClient


class CodegenClient:
    """
    Base client for the Codegen API.

    This client provides access to all Codegen API endpoints and handles
    authentication, error handling, and request formatting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize the Codegen API client.

        Args:
            api_key: API key for authentication (defaults to CODEGEN_API_KEY env var)
            base_url: Base URL for the API (defaults to CODEGEN_BASE_URL env var or https://api.codegen.com/v1)
            timeout: Request timeout in seconds (defaults to CODEGEN_TIMEOUT env var or 30)
            max_retries: Maximum number of retries for failed requests (defaults to CODEGEN_MAX_RETRIES env var or 3)
            user_agent: User agent string (defaults to CODEGEN_USER_AGENT env var or codegen-python-client)
        """
        self.config = CodegenConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent,
        )

        # Initialize endpoint clients
        self.users = UsersClient(self)
        self.agents = AgentsClient(self)
        self.organizations = OrganizationsClient(self)
        self.repositories = RepositoriesClient(self)
        self.integrations = IntegrationsClient(self)
        self.setup_commands = SetupCommandsClient(self)
        self.sandbox = SandboxClient(self)
        self.agents_alpha = AgentsAlphaClient(self)
        self.multi_run_agent = MultiRunAgentClient(self)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.

        Returns:
            Dict[str, str]: Headers for API requests
        """
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response

        Returns:
            Any: Response data

        Raises:
            CodegenAuthError: If authentication fails
            CodegenRateLimitError: If rate limit is exceeded
            CodegenResourceNotFoundError: If resource is not found
            CodegenValidationError: If request validation fails
            CodegenApiError: For other API errors
        """
        if response.status_code == 200:
            return response.json()

        error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
        error_message = error_data.get("message", response.text)

        if response.status_code == 401:
            raise CodegenAuthError(f"Authentication failed: {error_message}")
        elif response.status_code == 403:
            raise CodegenAuthError(f"Permission denied: {error_message}")
        elif response.status_code == 404:
            raise CodegenResourceNotFoundError(f"Resource not found: {error_message}")
        elif response.status_code == 422:
            raise CodegenValidationError(f"Validation error: {error_message}")
        elif response.status_code == 429:
            raise CodegenRateLimitError(f"Rate limit exceeded: {error_message}")
        else:
            raise CodegenApiError(f"API error ({response.status_code}): {error_message}")

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a GET request to the API.

        Args:
            path: API path (without base URL)
            params: Query parameters

        Returns:
            Any: Response data

        Raises:
            CodegenApiError: If the API request fails
        """
        url = f"{self.config.base_url}{path}"
        with httpx.Client() as client:
            response = client.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
            )
            return self._handle_response(response)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a POST request to the API.

        Args:
            path: API path (without base URL)
            data: Request data
            params: Query parameters

        Returns:
            Any: Response data

        Raises:
            CodegenApiError: If the API request fails
        """
        url = f"{self.config.base_url}{path}"
        with httpx.Client() as client:
            response = client.post(
                url,
                json=data,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
            )
            return self._handle_response(response)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a PUT request to the API.

        Args:
            path: API path (without base URL)
            data: Request data
            params: Query parameters

        Returns:
            Any: Response data

        Raises:
            CodegenApiError: If the API request fails
        """
        url = f"{self.config.base_url}{path}"
        with httpx.Client() as client:
            response = client.put(
                url,
                json=data,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
            )
            return self._handle_response(response)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a DELETE request to the API.

        Args:
            path: API path (without base URL)
            params: Query parameters

        Returns:
            Any: Response data

        Raises:
            CodegenApiError: If the API request fails
        """
        url = f"{self.config.base_url}{path}"
        with httpx.Client() as client:
            response = client.delete(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
            )
            return self._handle_response(response)

