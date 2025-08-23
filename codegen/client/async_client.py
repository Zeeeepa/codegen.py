"""
Asynchronous client for the Codegen API.

This module contains the asynchronous client implementation for the Codegen API.
"""

import time
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, AsyncGenerator

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from codegen.client.base import BaseCodegenClient
from codegen.config.client_config import ClientConfig
from codegen.models.responses import (
    UserResponse,
    GithubPullRequestResponse,
    AgentRunResponse,
    AgentRunLogResponse,
    OrganizationResponse,
    OrganizationsResponse,
    UsersResponse,
    AgentRunsResponse,
    AgentRunWithLogsResponse,
)
from codegen.models.enums import SourceType, AgentRunStatus
from codegen.exceptions.api_exceptions import (
    ValidationError,
    CodegenAPIError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    ServerError,
    TimeoutError,
    NetworkError,
)
from codegen.utils.logging import log_request, log_response

# Configure logging
logger = logging.getLogger(__name__)


class AsyncCodegenClient(BaseCodegenClient):
    """Asynchronous client for the Codegen API."""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """Initialize the asynchronous client.
        
        Args:
            config: Client configuration. If None, uses default configuration.
            
        Raises:
            ImportError: If aiohttp is not installed.
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for AsyncCodegenClient. "
                "Install it with 'pip install aiohttp'."
            )
        
        super().__init__(config)
        self.session = None
        logger.debug("Initialized AsyncCodegenClient")
    
    async def __aenter__(self):
        """Enter async context manager."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        await self.close()
    
    async def close(self):
        """Close the client and release resources."""
        if self.session is not None:
            await self.session.close()
            self.session = None
        logger.debug("Closed AsyncCodegenClient")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        use_cache: bool = False,
    ) -> Dict[str, Any]:
        """Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint.
            params: Query parameters.
            json: JSON request body.
            use_cache: Whether to use the cache for this request.
            
        Returns:
            The response data as a dictionary.
            
        Raises:
            RateLimitError: If the API rate limit is exceeded.
            AuthenticationError: If authentication fails.
            NotFoundError: If the requested resource is not found.
            ServerError: If a server error occurs.
            TimeoutError: If the request times out.
            NetworkError: If a network error occurs.
            CodegenAPIError: For other API errors.
        """
        # Create session if not exists
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Generate request ID for tracking
        request_id = self._generate_request_id()
        
        # Check cache if enabled and applicable
        cache_key = None
        if use_cache and self.cache and method.upper() == "GET":
            cache_key = self.cache._generate_key(method, endpoint, params, json)
            cached_result = self.cache.get(method, endpoint, params, json)
            if cached_result:
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, 0, 200, request_id, cached=True
                    )
                return cached_result
        
        # Build URL
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Get headers
        headers = self._get_headers()
        
        # Add request ID to headers for tracking
        headers["X-Request-ID"] = request_id
        
        # Log the request if enabled
        if self.config.log_requests:
            log_request(logger, method, url, params, headers, json)
        
        # Make the request with retries
        retries = 0
        start_time = time.time()
        
        while True:
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                    timeout=self.config.timeout,
                ) as response:
                    # Calculate request duration
                    duration = time.time() - start_time
                    
                    # Log the response if enabled
                    if self.config.log_requests:
                        response_text = await response.text()
                        log_response(
                            logger, response.status, url, response_text, duration
                        )
                    
                    # Record metrics
                    if self.metrics:
                        self.metrics.record_request(
                            method, endpoint, duration, response.status, request_id
                        )
                    
                    # Handle rate limiting
                    if response.status == 429:
                        raise RateLimitError(
                            int(response.headers.get("Retry-After", 60)), request_id
                        )
                    
                    # Handle authentication errors
                    elif response.status == 401:
                        raise AuthenticationError(
                            "Invalid API token or insufficient permissions", request_id
                        )
                    
                    # Handle not found errors
                    elif response.status == 404:
                        raise NotFoundError("Requested resource not found", request_id)
                    
                    # Handle server errors
                    elif response.status >= 500:
                        raise ServerError(
                            f"Server error: {response.status}",
                            response.status,
                            request_id,
                        )
                    
                    # Handle other errors
                    elif not response.ok:
                        try:
                            error_data = await response.json()
                            message = error_data.get(
                                "message", f"API request failed: {response.status}"
                            )
                        except:
                            message = f"API request failed: {response.status}"
                        
                        raise CodegenAPIError(
                            message,
                            response.status,
                            error_data if "error_data" in locals() else None,
                            request_id,
                        )
                    
                    # Parse response
                    result = await response.json()
                    
                    # Cache result if applicable
                    if cache_key and response.ok:
                        self.cache.set(method, endpoint, result, params, json)
                    
                    return result
            
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 408, request_id
                    )
                raise TimeoutError(
                    f"Request timed out after {self.config.timeout}s", request_id
                )
            
            except aiohttp.ClientError as e:
                duration = time.time() - start_time
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, 0, request_id
                    )
                
                # Handle retries for certain errors
                if (
                    isinstance(
                        e,
                        (
                            aiohttp.ClientConnectionError,
                            aiohttp.ClientPayloadError,
                        ),
                    )
                    and retries < self.config.max_retries
                ):
                    retries += 1
                    retry_delay = self.config.retry_delay * (
                        self.config.retry_backoff ** (retries - 1)
                    )
                    logger.warning(
                        f"Request failed, retrying in {retry_delay:.2f}s ({retries}/{self.config.max_retries})"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                
                raise NetworkError(f"Network error: {str(e)}", request_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the API.
        
        Returns:
            A dictionary with health status information.
        """
        return await self._make_request("GET", "/health", use_cache=True)
    
    async def get_current_user(self) -> UserResponse:
        """Get the current user.
        
        Returns:
            A UserResponse object with user information.
        """
        response = await self._make_request("GET", "/users/me", use_cache=True)
        return UserResponse(**response)
    
    async def get_user(self, user_id: int) -> UserResponse:
        """Get a user by ID.
        
        Args:
            user_id: The user ID.
            
        Returns:
            A UserResponse object with user information.
        """
        response = await self._make_request("GET", f"/users/{user_id}", use_cache=True)
        return UserResponse(**response)
    
    async def get_users(
        self, org_id: Union[int, str], skip: int = 0, limit: int = 100
    ) -> UsersResponse:
        """Get users for an organization.
        
        Args:
            org_id: The organization ID.
            skip: Number of users to skip.
            limit: Maximum number of users to return.
            
        Returns:
            A UsersResponse object with user information.
        """
        org_id_int = self._validate_org_id(org_id)
        response = await self._make_request(
            "GET",
            f"/organizations/{org_id_int}/users",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )
        return UsersResponse(
            items=[UserResponse(**user) for user in response["items"]],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )
    
    async def stream_users(self, org_id: Union[int, str]) -> AsyncGenerator[UserResponse, None]:
        """Stream all users for an organization.
        
        Args:
            org_id: The organization ID.
            
        Yields:
            UserResponse objects.
        """
        skip = 0
        while True:
            response = await self._make_request(
                "GET",
                f"/organizations/{org_id}/users",
                params={"skip": skip, "limit": 100},
                use_cache=True,
            )
            users_response = UsersResponse(
                items=[UserResponse(**user) for user in response["items"]],
                total=response["total"],
                page=response["page"],
                size=response["size"],
                pages=response["pages"],
            )
            for user in users_response.items:
                yield user
            
            if len(users_response.items) < 100:
                break
            
            skip += 100
    
    async def create_agent_run(
        self,
        org_id: Union[int, str],
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRunResponse:
        """Create an agent run.
        
        Args:
            org_id: The organization ID.
            prompt: The prompt for the agent.
            images: Optional list of image URLs.
            metadata: Optional metadata for the agent run.
            
        Returns:
            An AgentRunResponse object with run information.
            
        Raises:
            ValidationError: If the prompt is empty.
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        
        org_id_int = self._validate_org_id(org_id)
        data = {"prompt": prompt, "images": images, "metadata": metadata}
        response = await self._make_request(
            "POST", f"/organizations/{org_id_int}/agent/run", json=data
        )
        
        return AgentRunResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            source_type=SourceType(response["source_type"])
            if response.get("source_type")
            else None,
            github_pull_requests=[
                GithubPullRequestResponse(
                    id=pr.get("id", 0),
                    title=pr.get("title", ""),
                    url=pr.get("url", ""),
                    created_at=pr.get("created_at", ""),
                )
                for pr in response.get("github_pull_requests", [])
                if all(key in pr for key in ["id", "title", "url", "created_at"])
            ],
            metadata=response.get("metadata"),
        )
    
    async def get_agent_run(
        self, org_id: Union[int, str], agent_run_id: int
    ) -> AgentRunResponse:
        """Get an agent run by ID.
        
        Args:
            org_id: The organization ID.
            agent_run_id: The agent run ID.
            
        Returns:
            An AgentRunResponse object with run information.
        """
        org_id_int = self._validate_org_id(org_id)
        response = await self._make_request(
            "GET",
            f"/organizations/{org_id_int}/agent/run/{agent_run_id}",
            use_cache=True,
        )
        
        return AgentRunResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            source_type=SourceType(response["source_type"])
            if response.get("source_type")
            else None,
            github_pull_requests=[
                GithubPullRequestResponse(
                    id=pr.get("id", 0),
                    title=pr.get("title", ""),
                    url=pr.get("url", ""),
                    created_at=pr.get("created_at", ""),
                )
                for pr in response.get("github_pull_requests", [])
                if all(key in pr for key in ["id", "title", "url", "created_at"])
            ],
            metadata=response.get("metadata"),
        )
    
    async def wait_for_completion(
        self,
        org_id: Union[int, str],
        agent_run_id: int,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> AgentRunResponse:
        """Wait for an agent run to complete.
        
        Args:
            org_id: The organization ID.
            agent_run_id: The agent run ID.
            poll_interval: Interval in seconds between polls.
            timeout: Maximum time to wait in seconds.
            
        Returns:
            An AgentRunResponse object with run information.
            
        Raises:
            TimeoutError: If the run does not complete within the timeout.
        """
        start_time = time.time()
        
        while True:
            run = await self.get_agent_run(org_id, agent_run_id)
            
            if run.status in [
                AgentRunStatus.COMPLETED.value,
                AgentRunStatus.FAILED.value,
                AgentRunStatus.CANCELLED.value,
            ]:
                return run
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Agent run {agent_run_id} did not complete within {timeout} seconds"
                )
            
            await asyncio.sleep(poll_interval)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics.
        
        Returns:
            A dictionary with client statistics.
        """
        stats = {
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "async_client": True,
            }
        }
        
        if self.metrics:
            client_stats = self.metrics.get_stats()
            stats["metrics"] = {
                "uptime_seconds": client_stats.uptime_seconds,
                "total_requests": client_stats.total_requests,
                "total_errors": client_stats.total_errors,
                "error_rate": client_stats.error_rate,
                "requests_per_minute": client_stats.requests_per_minute,
                "average_response_time": client_stats.average_response_time,
                "cache_hit_rate": client_stats.cache_hit_rate,
                "status_code_distribution": client_stats.status_code_distribution,
            }
        
        return stats

