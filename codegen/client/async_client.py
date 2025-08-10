"""
Asynchronous Codegen API client
"""

import asyncio
import time
import uuid
import logging
from typing import Optional, Dict, Any, List, AsyncGenerator

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from ..config import ClientConfig
from ..models import AgentRunResponse, UserResponse
from ..exceptions import (
    CodegenAPIError, ValidationError, RateLimitError, AuthenticationError,
    NotFoundError, ServerError, TimeoutError, NetworkError
)
from ..utils import RateLimiter, CacheManager, MetricsCollector

logger = logging.getLogger(__name__)


class AsyncCodegenClient:
    """
    Asynchronous Codegen API client with full feature parity.
    
    Note: Requires aiohttp to be installed.
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for AsyncCodegenClient. "
                "Install with: pip install aiohttp"
            )
        
        self.config = config or ClientConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize components (similar to sync client)
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
        
        logger.info(f"Initialized AsyncCodegenClient with base URL: {self.config.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_token}",
                "User-Agent": self.config.user_agent,
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    async def _make_request(
        self, method: str, endpoint: str, use_cache: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Make async HTTP request with rate limiting, caching, and metrics"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
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
        
        # Make request
        start_time = time.time()
        url = f"{self.config.base_url}{endpoint}"
        
        if self.config.log_requests:
            logger.info(f"Making async {method} request to {endpoint} (request_id: {request_id})")
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                duration = time.time() - start_time
                
                if self.config.log_requests:
                    logger.info(
                        f"Async request completed in {duration:.2f}s - Status: {response.status} (request_id: {request_id})"
                    )
                
                # Record metrics
                if self.metrics:
                    self.metrics.record_request(
                        method, endpoint, duration, response.status, request_id
                    )
                
                # Handle response
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError(retry_after, request_id)
                elif response.status == 401:
                    raise AuthenticationError(
                        "Invalid API token or insufficient permissions", request_id
                    )
                elif response.status == 404:
                    raise NotFoundError("Requested resource not found", request_id)
                elif response.status >= 500:
                    raise ServerError(
                        f"Server error: {response.status}",
                        response.status,
                        request_id,
                    )
                elif not response.ok:
                    try:
                        error_data = await response.json()
                        message = error_data.get(
                            "message", f"API request failed: {response.status}"
                        )
                    except:
                        message = f"API request failed: {response.status}"
                        error_data = None
                    raise CodegenAPIError(
                        message,
                        response.status,
                        error_data,
                        request_id,
                    )
                
                result = await response.json()
                
                # Cache successful GET requests
                if cache_key and response.ok:
                    self.cache.set(cache_key, result)
                
                return result
        
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(method, endpoint, duration, 408, request_id)
            raise TimeoutError(f"Request timed out after {self.config.timeout}s", request_id)
        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.record_request(method, endpoint, duration, 0, request_id)
            raise NetworkError(f"Network error: {str(e)}", request_id)
    
    # Async versions of main methods
    async def get_current_user(self) -> UserResponse:
        """Get current user information from API token"""
        response = await self._make_request("GET", "/users/me", use_cache=True)
        return UserResponse(
            id=response.get("id", 0),
            email=response.get("email"),
            github_user_id=response.get("github_user_id", ""),
            github_username=response.get("github_username", ""),
            avatar_url=response.get("avatar_url"),
            full_name=response.get("full_name"),
        )
    
    async def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRunResponse:
        """Create a new agent run"""
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        
        data = {"prompt": prompt, "images": images, "metadata": metadata}
        response = await self._make_request(
            "POST", f"/organizations/{org_id}/agent/run", json=data
        )
        
        return AgentRunResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            source_type=None,  # Parse if needed
            github_pull_requests=None,  # Parse if needed
            metadata=response.get("metadata"),
        )
    
    async def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRunResponse:
        """Retrieve the status and result of an agent run"""
        response = await self._make_request(
            "GET",
            f"/organizations/{org_id}/agent/run/{agent_run_id}",
            use_cache=True,
        )
        
        return AgentRunResponse(
            id=response["id"],
            organization_id=response["organization_id"],
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            source_type=None,  # Parse if needed
            github_pull_requests=None,  # Parse if needed
            metadata=response.get("metadata"),
        )
    
    async def wait_for_completion(
        self,
        org_id: int,
        agent_run_id: int,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> AgentRunResponse:
        """Wait for an agent run to complete with polling"""
        start_time = time.time()
        
        while True:
            run = await self.get_agent_run(org_id, agent_run_id)
            
            if run.status in ["completed", "failed", "cancelled"]:
                return run
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Agent run {agent_run_id} did not complete within {timeout} seconds"
                )
            
            await asyncio.sleep(poll_interval)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive client statistics"""
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

