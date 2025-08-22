"""
Base client for the Codegen API.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

import httpx

from codegen_client.config import CodegenConfig
from codegen_client.exceptions import (
    CodegenApiError,
    CodegenAuthError,
    CodegenRateLimitError,
    CodegenResourceNotFoundError,
    CodegenValidationError,
)

# Type variable for endpoint classes
T = TypeVar("T")

logger = logging.getLogger(__name__)


class CodegenClient:
    """
    Base client for the Codegen API.

    This class provides the foundation for all API endpoint clients, handling
    authentication, HTTP requests, error handling, and rate limiting.
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
            api_key: API key for authentication. If not provided, will look for
                CODEGEN_API_KEY environment variable.
            base_url: Base URL for the API. If not provided, will use the default
                or CODEGEN_BASE_URL environment variable.
            timeout: Request timeout in seconds. If not provided, will use the default
                or CODEGEN_TIMEOUT environment variable.
            max_retries: Maximum number of retries for failed requests. If not provided,
                will use the default or CODEGEN_MAX_RETRIES environment variable.
            user_agent: User agent string. If not provided, will use the default
                or CODEGEN_USER_AGENT environment variable.
        """
        # Load configuration from environment if not provided
        config = CodegenConfig.from_env()

        # Override with provided values
        self.api_key = api_key or config.api_key
        self.base_url = base_url or config.base_url
        self.timeout = timeout or config.timeout
        self.max_retries = max_retries or config.max_retries
        self.user_agent = user_agent or config.user_agent

        # Validate required configuration
        if not self.api_key:
            logger.warning(
                "No API key provided. Authentication will fail for endpoints requiring authentication."
            )

        # Initialize HTTP client
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self._get_default_headers(),
            base_url=self.base_url,
        )

        # Initialize endpoint clients
        self._init_endpoints()

    def _init_endpoints(self) -> None:
        """
        Initialize endpoint clients.

        This method is called during initialization to set up all endpoint clients.
        Each endpoint client is attached as an attribute to this client instance.
        """
        # Import here to avoid circular imports
        from codegen_client.endpoints.agents import AgentsClient
        from codegen_client.endpoints.agents_alpha import AgentsAlphaClient
        from codegen_client.endpoints.integrations import IntegrationsClient
        from codegen_client.endpoints.organizations import OrganizationsClient
        from codegen_client.endpoints.repositories import RepositoriesClient
        from codegen_client.endpoints.sandbox import SandboxClient
        from codegen_client.endpoints.setup_commands import SetupCommandsClient
        from codegen_client.endpoints.users import UsersClient

        # Attach endpoint clients
        self.users = self._create_endpoint_client(UsersClient)
        self.agents = self._create_endpoint_client(AgentsClient)
        self.agents_alpha = self._create_endpoint_client(AgentsAlphaClient)
        self.organizations = self._create_endpoint_client(OrganizationsClient)
        self.repositories = self._create_endpoint_client(RepositoriesClient)
        self.integrations = self._create_endpoint_client(IntegrationsClient)
        self.setup_commands = self._create_endpoint_client(SetupCommandsClient)
        self.sandbox = self._create_endpoint_client(SandboxClient)

    def _create_endpoint_client(self, endpoint_class: Type[T]) -> T:
        """
        Create an instance of an endpoint client.

        Args:
            endpoint_class: The endpoint client class to instantiate.

        Returns:
            An instance of the endpoint client.
        """
        return endpoint_class(self)

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Get default headers for API requests.

        Returns:
            Dict[str, str]: Default headers for API requests.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = self.api_key

        return headers

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Codegen API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path (without base URL)
            params: Query parameters
            data: Request body data
            headers: Additional headers
            files: Files to upload

        Returns:
            Dict[str, Any]: Response data as a dictionary

        Raises:
            CodegenAuthError: If authentication fails
            CodegenRateLimitError: If rate limits are exceeded
            CodegenResourceNotFoundError: If the requested resource is not found
            CodegenValidationError: If request validation fails
            CodegenApiError: For other API errors
        """
        # Combine default headers with provided headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        # Prepare request URL
        url = path

        # Prepare request data
        json_data = None
        if data:
            json_data = data

        # Make the request with retries
        response = None
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                    files=files,
                )
                break
            except httpx.RequestError as e:
                retry_count += 1
                if retry_count > self.max_retries:
                    raise CodegenApiError(f"Request failed: {str(e)}")
                logger.warning(
                    f"Request failed, retrying ({retry_count}/{self.max_retries}): {str(e)}"
                )

        if not response:
            raise CodegenApiError("Request failed with no response")

        # Handle response
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle the API response.

        Args:
            response: HTTP response object

        Returns:
            Dict[str, Any]: Response data as a dictionary

        Raises:
            CodegenAuthError: If authentication fails
            CodegenRateLimitError: If rate limits are exceeded
            CodegenResourceNotFoundError: If the requested resource is not found
            CodegenValidationError: If request validation fails
            CodegenApiError: For other API errors
        """
        try:
            response_data = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_data = {"raw_content": response.text}

        # Handle successful responses
        if response.is_success:
            return cast(Dict[str, Any], response_data)

        # Handle error responses
        error_message = response_data.get("detail", "Unknown error")
        if isinstance(error_message, list) and error_message:
            error_message = error_message[0].get("msg", "Unknown error")

        if response.status_code == 401 or response.status_code == 403:
            raise CodegenAuthError(
                f"Authentication failed: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise CodegenResourceNotFoundError(
                f"Resource not found: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 422:
            validation_errors = response_data.get("detail", {})
            raise CodegenValidationError(
                f"Validation failed: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
                validation_errors=validation_errors,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise CodegenRateLimitError(
                f"Rate limit exceeded: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
                retry_after=retry_after_seconds,
            )
        else:
            raise CodegenApiError(
                f"API error: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
            )

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request to the Codegen API.

        Args:
            path: API endpoint path (without base URL)
            params: Query parameters
            headers: Additional headers

        Returns:
            Dict[str, Any]: Response data as a dictionary
        """
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request to the Codegen API.

        Args:
            path: API endpoint path (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            files: Files to upload

        Returns:
            Dict[str, Any]: Response data as a dictionary
        """
        return self.request(
            "POST", path, params=params, data=data, headers=headers, files=files
        )

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the Codegen API.

        Args:
            path: API endpoint path (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Dict[str, Any]: Response data as a dictionary
        """
        return self.request("PUT", path, params=params, data=data, headers=headers)

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a DELETE request to the Codegen API.

        Args:
            path: API endpoint path (without base URL)
            params: Query parameters
            headers: Additional headers

        Returns:
            Dict[str, Any]: Response data as a dictionary
        """
        return self.request("DELETE", path, params=params, headers=headers)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> "CodegenClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close the client."""
        self.close()

