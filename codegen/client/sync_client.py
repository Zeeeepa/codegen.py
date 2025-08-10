"""
Synchronous Codegen API client
"""

import time
import uuid
import logging
from typing import Optional, Dict, Any, List, Iterator

import requests
from requests import exceptions as requests_exceptions

from ..config import ClientConfig
from ..models import (
    AgentRunResponse, AgentRunWithLogsResponse, AgentRunsResponse,
    UsersResponse, OrganizationsResponse, UserResponse, OrganizationResponse,
    AgentRunLogResponse, GithubPullRequestResponse, SourceType
)
from ..exceptions import (
    CodegenAPIError, ValidationError, RateLimitError, AuthenticationError,
    NotFoundError, ServerError, TimeoutError, NetworkError
)
from ..utils import RateLimiter, CacheManager, MetricsCollector

logger = logging.getLogger(__name__)


class CodegenClient:
    """
    Synchronous Codegen API client with comprehensive features.
    
    Features:
    - Rate limiting and retry logic
    - Response caching
    - Request metrics
    - Comprehensive error handling
    - Streaming support for large datasets
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        
        # Validate configuration for actual use
        self.config.validate_for_use()
        
        self.headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }
        
        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Initialize components
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests_per_period,
            self.config.rate_limit_period_seconds,
        )
        
        self.cache = (
            CacheManager(
                max_size=self.config.cache_max_size,
                ttl_seconds=self.config.cache_ttl_seconds,
            )
            if self.config.enable_caching
            else None
        )
        
        self.metrics = MetricsCollector() if self.config.enable_metrics else None
        
        logger.info(f"Initialized CodegenClient with base URL: {self.config.base_url}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    def _validate_pagination(self, skip: int, limit: int):
        """Validate pagination parameters"""
        if skip < 0:
            raise ValidationError("skip must be >= 0")
        if not (1 <= limit <= 100):
            raise ValidationError("limit must be between 1 and 100")
    
    def _parse_error_response(
        self, response: requests.Response, status_code: int, request_id: str
    ) -> CodegenAPIError:
        """Extract error information from response"""
        try:
            error_data = response.json()
            message = error_data.get("message", f"API request failed: {status_code}")
            return CodegenAPIError(message, status_code, error_data, request_id)
        except Exception:
            message = f"API request failed: {status_code}"
            return CodegenAPIError(message, status_code, None, request_id)
    
    def _handle_response(self, response: requests.Response, request_id: str) -> Dict[str, Any]:
        """Handle HTTP response with comprehensive error handling"""
        status_code = response.status_code
        
        if status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))
            raise RateLimitError(retry_after, request_id)
        elif status_code == 401:
            raise AuthenticationError(
                "Invalid API token or insufficient permissions", request_id
            )
        elif status_code == 404:
            raise NotFoundError("Requested resource not found", request_id)
        elif status_code >= 500:
            raise ServerError(f"Server error: {status_code}", status_code, request_id)
        elif not response.ok:
            raise self._parse_error_response(response, status_code, request_id)
        
        return response.json()
    
    def _make_request(
        self, method: str, endpoint: str, use_cache: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting, caching, and metrics"""
        request_id = self._generate_request_id()
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Check cache
        cache_key = None
        if use_cache and self.cache and method.upper() == "GET":
            cache_key = f"{method}:{endpoint}:{hash(str(kwargs))}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {endpoint} (request_id: {request_id})")
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, 0, 200, request_id, cached=True
                    )
                return cached_result
        
        # Make request with retry logic
        start_time = time.time()
        url = f"{self.config.base_url}{endpoint}"
        
        if self.config.log_requests:
            logger.info(f"Making {method} request to {endpoint} (request_id: {request_id})")
        
        try:
            response = self.session.request(
                method, url, timeout=self.config.timeout, **kwargs
            )
            duration = time.time() - start_time
            
            if self.config.log_requests:
                logger.info(
                    f"Request completed in {duration:.2f}s - Status: {response.status_code} (request_id: {request_id})"
                )
            
            # Record metrics
            if self.metrics:
                self.metrics.record_request(
                    method, endpoint, duration, response.status_code, request_id
                )
            
            result = self._handle_response(response, request_id)
            
            # Cache successful GET requests
            if cache_key and response.ok:
                self.cache.set(cache_key, result)
            
            return result
            
        except requests_exceptions.Timeout:
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(method, endpoint, duration, 408, request_id)
            raise TimeoutError(f"Request timed out after {self.config.timeout}s", request_id)
        except requests_exceptions.ConnectionError as e:
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(method, endpoint, duration, 0, request_id)
            raise NetworkError(f"Network error: {str(e)}", request_id)
    
    # ========================================================================
    # AGENT ENDPOINTS
    # ========================================================================
    
    def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRunResponse:
        """Create a new agent run"""
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        if len(prompt) > 50000:
            raise ValidationError("Prompt cannot exceed 50,000 characters")
        if images and len(images) > 10:
            raise ValidationError("Cannot include more than 10 images")
        
        data = {"prompt": prompt, "images": images, "metadata": metadata}
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run", json=data)
        return self._parse_agent_run_response(response)
    
    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRunResponse:
        """Retrieve the status and result of an agent run"""
        response = self._make_request(
            "GET", f"/organizations/{org_id}/agent/run/{agent_run_id}", use_cache=True
        )
        return self._parse_agent_run_response(response)
    
    def list_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> AgentRunsResponse:
        """List agent runs for an organization with optional filtering"""
        self._validate_pagination(skip, limit)
        
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        if source_type:
            params["source_type"] = source_type.value
        
        response = self._make_request(
            "GET", f"/organizations/{org_id}/agent/runs", params=params, use_cache=True
        )
        
        return AgentRunsResponse(
            items=[self._parse_agent_run_response(run) for run in response["items"]],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )
    
    def resume_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
    ) -> AgentRunResponse:
        """Resume a paused agent run"""
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        
        data = {"agent_run_id": agent_run_id, "prompt": prompt, "images": images}
        response = self._make_request(
            "POST", f"/organizations/{org_id}/agent/run/resume", json=data
        )
        return self._parse_agent_run_response(response)
    
    def get_agent_run_logs(
        self, org_id: int, agent_run_id: int, skip: int = 0, limit: int = 100
    ) -> AgentRunWithLogsResponse:
        """Retrieve an agent run with its logs using pagination (ALPHA)"""
        self._validate_pagination(skip, limit)
        
        response = self._make_request(
            "GET",
            f"/organizations/{org_id}/agent/run/{agent_run_id}/logs",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )
        
        return AgentRunWithLogsResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            logs=[
                AgentRunLogResponse(
                    agent_run_id=log.get("agent_run_id", 0),
                    created_at=log.get("created_at", ""),
                    message_type=log.get("message_type", ""),
                    thought=log.get("thought"),
                    tool_name=log.get("tool_name"),
                    tool_input=log.get("tool_input"),
                    tool_output=log.get("tool_output"),
                    observation=log.get("observation"),
                )
                for log in response["logs"]
            ],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            metadata=response.get("metadata"),
            total_logs=response.get("total_logs"),
            page=response.get("page"),
            size=response.get("size"),
            pages=response.get("pages"),
        )
    
    def _parse_agent_run_response(self, data: Dict[str, Any]) -> AgentRunResponse:
        """Parse agent run response data into AgentRunResponse object"""
        return AgentRunResponse(
            id=data["id"],
            organization_id=data["organization_id"],
            status=data.get("status"),
            created_at=data.get("created_at"),
            web_url=data.get("web_url"),
            result=data.get("result"),
            source_type=SourceType(data["source_type"]) if data.get("source_type") else None,
            github_pull_requests=[
                GithubPullRequestResponse(
                    id=pr.get("id", 0),
                    title=pr.get("title", ""),
                    url=pr.get("url", ""),
                    created_at=pr.get("created_at", ""),
                )
                for pr in data.get("github_pull_requests", [])
                if all(key in pr for key in ["id", "title", "url", "created_at"])
            ],
            metadata=data.get("metadata"),
        )
    
    # ========================================================================
    # USER ENDPOINTS
    # ========================================================================
    
    def get_current_user(self) -> UserResponse:
        """Get current user information from API token"""
        response = self._make_request("GET", "/users/me", use_cache=True)
        return UserResponse(
            id=response.get("id", 0),
            email=response.get("email"),
            github_user_id=response.get("github_user_id", ""),
            github_username=response.get("github_username", ""),
            avatar_url=response.get("avatar_url"),
            full_name=response.get("full_name"),
        )
    
    def get_users(self, org_id: str, skip: int = 0, limit: int = 100) -> UsersResponse:
        """Get paginated list of users for a specific organization"""
        self._validate_pagination(skip, limit)
        
        response = self._make_request(
            "GET",
            f"/organizations/{org_id}/users",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )
        
        return UsersResponse(
            items=[
                UserResponse(
                    id=user.get("id", 0),
                    email=user.get("email"),
                    github_user_id=user.get("github_user_id", ""),
                    github_username=user.get("github_username", ""),
                    avatar_url=user.get("avatar_url"),
                    full_name=user.get("full_name"),
                )
                for user in response["items"]
                if user.get("id") and user.get("github_user_id") and user.get("github_username")
            ],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )
    
    def get_user(self, org_id: str, user_id: str) -> UserResponse:
        """Get details for a specific user in an organization"""
        response = self._make_request(
            "GET", f"/organizations/{org_id}/users/{user_id}", use_cache=True
        )
        return UserResponse(
            id=response.get("id", 0),
            email=response.get("email"),
            github_user_id=response.get("github_user_id", ""),
            github_username=response.get("github_username", ""),
            avatar_url=response.get("avatar_url"),
            full_name=response.get("full_name"),
        )
    
    # ========================================================================
    # ORGANIZATION ENDPOINTS
    # ========================================================================
    
    def get_organizations(self, skip: int = 0, limit: int = 100) -> OrganizationsResponse:
        """Get organizations for the authenticated user"""
        self._validate_pagination(skip, limit)
        
        response = self._make_request(
            "GET",
            "/organizations",
            params={"skip": skip, "limit": limit},
            use_cache=True,
        )
        
        return OrganizationsResponse(
            items=[
                OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    settings=org.get("settings", {}),
                )
                for org in response["items"]
            ],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def wait_for_completion(
        self,
        org_id: int,
        agent_run_id: int,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> AgentRunResponse:
        """Wait for an agent run to complete with polling"""
        start_time = time.time()
        
        while True:
            run = self.get_agent_run(org_id, agent_run_id)
            
            if run.status in ["completed", "failed", "cancelled"]:
                return run
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Agent run {agent_run_id} did not complete within {timeout} seconds"
                )
            
            time.sleep(poll_interval)
    
    def stream_all_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
    ) -> Iterator[AgentRunResponse]:
        """Stream all agent runs with automatic pagination"""
        if not self.config.enable_streaming:
            raise ValidationError("Streaming is disabled")
        
        skip = 0
        while True:
            response = self.list_agent_runs(
                org_id, user_id=user_id, source_type=source_type, skip=skip, limit=100
            )
            for run in response.items:
                yield run
            
            if len(response.items) < 100:
                break
            skip += 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive client statistics"""
        stats = {
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "rate_limit_requests_per_period": self.config.rate_limit_requests_per_period,
                "caching_enabled": self.config.enable_caching,
                "streaming_enabled": self.config.enable_streaming,
                "metrics_enabled": self.config.enable_metrics,
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
        
        if self.cache:
            stats["cache"] = self.cache.get_stats()
        
        if hasattr(self, "rate_limiter"):
            stats["rate_limiter"] = self.rate_limiter.get_current_usage()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the API"""
        try:
            start_time = time.time()
            user = self.get_current_user()
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_seconds": duration,
                "user_id": user.id,
                "timestamp": time.time(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            }
    
    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()
        logger.info("Client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
