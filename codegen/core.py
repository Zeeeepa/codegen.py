"""
Core Codegen API functionality
Base classes, enums, exceptions, and the main client
"""

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional

# HTTP clients
import requests
from requests import exceptions as requests_exceptions

try:
    pass

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================


class SourceType(Enum):
    LOCAL = "LOCAL"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    GITHUB_CHECK_SUITE = "GITHUB_CHECK_SUITE"
    LINEAR = "LINEAR"
    API = "API"
    CHAT = "CHAT"
    JIRA = "JIRA"


class MessageType(Enum):
    ACTION = "ACTION"
    OBSERVATION = "OBSERVATION"
    THOUGHT = "THOUGHT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    WEBHOOK = "WEBHOOK"


class AgentRunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# EXCEPTIONS
# ============================================================================


class CodegenAPIError(Exception):
    """Base exception for all Codegen API errors"""

    def __init__(
        self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationError(CodegenAPIError):
    """Raised when request validation fails"""


class RateLimitError(CodegenAPIError):
    """Raised when rate limit is exceeded"""


class AuthenticationError(CodegenAPIError):
    """Raised when authentication fails"""


class NotFoundError(CodegenAPIError):
    """Raised when resource is not found"""


class ServerError(CodegenAPIError):
    """Raised when server returns 5xx error"""


class TimeoutError(CodegenAPIError):
    """Raised when request times out"""


class NetworkError(CodegenAPIError):
    """Raised when network error occurs"""


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class UserResponse:
    id: int
    name: str
    email: str
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class GithubPullRequestResponse:
    number: int
    title: str
    url: str
    state: str


@dataclass
class OrganizationSettings:
    github_pull_request_creation: bool = True
    linear_issue_creation: bool = True


@dataclass
class OrganizationResponse:
    id: int
    name: str
    settings: OrganizationSettings


@dataclass
class AgentRunResponse:
    id: int
    status: str
    created_at: str
    updated_at: str
    source_type: str
    message: str
    result: Optional[str] = None
    error: Optional[str] = None
    github_pull_request: Optional[GithubPullRequestResponse] = None


@dataclass
class AgentRunLogResponse:
    id: int
    agent_run_id: int
    message_type: str
    content: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaginatedResponse:
    total: int
    skip: int
    limit: int


@dataclass
class UsersResponse(PaginatedResponse):
    users: List[UserResponse]


@dataclass
class AgentRunsResponse(PaginatedResponse):
    agent_runs: List[AgentRunResponse]


@dataclass
class OrganizationsResponse(PaginatedResponse):
    organizations: List[OrganizationResponse]


@dataclass
class AgentRunWithLogsResponse:
    agent_run: AgentRunResponse
    logs: List[AgentRunLogResponse]
    total_logs: int
    skip: int
    limit: int


# ============================================================================
# UTILITY CLASSES
# ============================================================================


@dataclass
class BulkOperationResult:
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
    total_processed: int
    success_rate: float
    execution_time: float
    errors: List[str] = field(default_factory=list)


@dataclass
class RequestMetrics:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    request_size: int = 0
    response_size: int = 0


@dataclass
class ClientStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limit_hits: int = 0

    @property
    def success_rate(self) -> float:
        return (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0
            else 0.0
        )

    @property
    def average_response_time(self) -> float:
        return (self.total_response_time / self.total_requests) if self.total_requests > 0 else 0.0


@dataclass
class ClientConfig:
    """Configuration for the Codegen client"""

    base_url: str = "https://api.codegen.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    cache_ttl: int = 300
    cache_max_size: int = 1000
    enable_metrics: bool = True
    enable_caching: bool = True
    enable_rate_limiting: bool = True
    user_agent: str = "codegen-python-sdk/1.0.0"

    # Webhook settings
    webhook_secret: Optional[str] = None
    webhook_verify_signature: bool = True

    # Async settings
    async_timeout: int = 60
    async_max_connections: int = 100
    async_max_connections_per_host: int = 30

    # Bulk operation settings
    bulk_batch_size: int = 50
    bulk_max_workers: int = 5
    bulk_timeout: int = 300

    def __post_init__(self):
        # Validate configuration
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.rate_limit_requests <= 0:
            raise ValueError("rate_limit_requests must be positive")
        if self.rate_limit_window <= 0:
            raise ValueError("rate_limit_window must be positive")


class RateLimiter:
    """Thread-safe rate limiter with sliding window"""

    def __init__(self, requests_per_period: int, period_seconds: int):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.requests = []
        self.lock = Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove old requests
            self.requests = [
                req_time for req_time in self.requests if now - req_time < self.period_seconds
            ]

            if len(self.requests) >= self.requests_per_period:
                sleep_time = self.period_seconds - (now - self.requests[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)

            self.requests.append(now)

    def get_current_usage(self) -> Dict[str, Any]:
        """Get current rate limit usage"""
        with self.lock:
            now = time.time()
            recent_requests = [
                req_time for req_time in self.requests if now - req_time < self.period_seconds
            ]
            return {
                "current_requests": len(recent_requests),
                "max_requests": self.requests_per_period,
                "period_seconds": self.period_seconds,
                "usage_percentage": (len(recent_requests) / self.requests_per_period) * 100,
            }


class CacheManager:
    """Advanced in-memory cache with TTL support and statistics"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            # Check TTL
            if time.time() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                self.misses += 1
                return None

            self.hits += 1
            return self.cache[key]

    def set(self, key: str, value: Any):
        """Set value in cache"""
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = value
            self.access_times[key] = time.time()

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "cache_size": len(self.cache),
                "max_size": self.max_size,
            }


class ConfigPresets:
    """Predefined configuration presets for different use cases"""

    @staticmethod
    def development() -> ClientConfig:
        """Configuration optimized for development"""
        return ClientConfig(
            timeout=10,
            max_retries=1,
            rate_limit_requests=50,
            cache_ttl=60,
            enable_metrics=True,
            enable_caching=False,  # Disable caching in dev for fresh data
        )

    @staticmethod
    def production() -> ClientConfig:
        """Configuration optimized for production"""
        return ClientConfig(
            timeout=30,
            max_retries=3,
            rate_limit_requests=100,
            cache_ttl=300,
            enable_metrics=True,
            enable_caching=True,
            enable_rate_limiting=True,
        )

    @staticmethod
    def high_throughput() -> ClientConfig:
        """Configuration optimized for high throughput scenarios"""
        return ClientConfig(
            timeout=60,
            max_retries=5,
            rate_limit_requests=200,
            rate_limit_window=60,
            cache_ttl=600,
            bulk_batch_size=100,
            bulk_max_workers=10,
            async_max_connections=200,
            async_max_connections_per_host=50,
        )

    @staticmethod
    def low_latency() -> ClientConfig:
        """Configuration optimized for low latency"""
        return ClientConfig(
            timeout=5,
            max_retries=1,
            retry_delay=0.1,
            cache_ttl=30,
            enable_caching=True,
            rate_limit_requests=300,
        )

    @staticmethod
    def batch_processing() -> ClientConfig:
        """Configuration optimized for batch processing"""
        return ClientConfig(
            timeout=120,
            max_retries=5,
            retry_delay=2.0,
            bulk_batch_size=200,
            bulk_max_workers=20,
            bulk_timeout=600,
            rate_limit_requests=500,
            rate_limit_window=60,
        )


# ============================================================================
# MAIN CLIENT CLASS
# ============================================================================


class CodegenClient:
    """Enhanced synchronous Codegen API client with comprehensive features"""

    def __init__(
        self,
        org_id: Optional[str] = None,
        token: Optional[str] = None,
        config: Optional[ClientConfig] = None,
    ):
        self.org_id = org_id or os.getenv("CODEGEN_ORG_ID")
        self.token = token or os.getenv("CODEGEN_API_TOKEN")
        self.config = config or ClientConfig()

        if not self.org_id:
            raise ValueError(
                "Organization ID is required. Set CODEGEN_ORG_ID environment variable "
                "or pass org_id parameter."
            )
        if not self.token:
            raise ValueError(
                "API token is required. Set CODEGEN_API_TOKEN environment variable "
                "or pass token parameter."
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }

        # Initialize components
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Rate limiting
        if self.config.enable_rate_limiting:
            self.rate_limiter = RateLimiter(
                self.config.rate_limit_requests,
                self.config.rate_limit_window,
            )
        else:
            self.rate_limiter = None

        # Caching
        if self.config.enable_caching:
            self.cache = CacheManager(
                max_size=self.config.cache_max_size,
                ttl_seconds=self.config.cache_ttl,
            )
        else:
            self.cache = None

        # Metrics
        if self.config.enable_metrics:
            self.stats = ClientStats()
        else:
            self.stats = None

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and retries"""
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()

        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                response = self.session.request(
                    method=method, url=url, timeout=self.config.timeout, **kwargs
                )

                # Record metrics
                if self.stats:
                    self.stats.total_requests += 1
                    self.stats.total_response_time += time.time() - start_time

                    if response.status_code < 400:
                        self.stats.successful_requests += 1
                    else:
                        self.stats.failed_requests += 1

                # Handle different status codes
                if response.status_code == 200:
                    return response
                elif response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API token", response.status_code, response.json()
                    )
                elif response.status_code == 404:
                    raise NotFoundError("Resource not found", response.status_code, response.json())
                elif response.status_code == 429:
                    if self.stats:
                        self.stats.rate_limit_hits += 1
                    raise RateLimitError(
                        "Rate limit exceeded", response.status_code, response.json()
                    )
                elif response.status_code >= 500:
                    raise ServerError(
                        f"Server error: {response.status_code}",
                        response.status_code,
                        response.json(),
                    )
                else:
                    raise CodegenAPIError(
                        f"HTTP {response.status_code}", response.status_code, response.json()
                    )

            except (requests_exceptions.Timeout, requests_exceptions.ConnectionError) as e:
                if attempt == self.config.max_retries:
                    raise NetworkError(
                        f"Network error after {self.config.max_retries + 1} attempts: {str(e)}"
                    )

                wait_time = self.config.retry_delay * (self.config.retry_backoff**attempt)
                logger.warning(
                    f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}"
                )
                time.sleep(wait_time)

        raise CodegenAPIError("Max retries exceeded")

    def run_agent(self, prompt: str, **kwargs) -> AgentRunResponse:
        """Run an agent with the given prompt"""
        data = {"prompt": prompt, **kwargs}
        response = self._make_request(
            "POST", f"/v1/organizations/{self.org_id}/agent/run", json=data
        )
        return AgentRunResponse(**response.json())

    def get_agent_run(self, run_id: int) -> AgentRunResponse:
        """Get details of a specific agent run"""
        response = self._make_request("GET", f"/v1/organizations/{self.org_id}/agent/run/{run_id}")
        return AgentRunResponse(**response.json())

    def get_agent_run_logs(
        self, run_id: int, skip: int = 0, limit: int = 100
    ) -> AgentRunWithLogsResponse:
        """Get logs for a specific agent run"""
        params = {"skip": skip, "limit": limit}
        response = self._make_request(
            "GET", f"/v1/organizations/{self.org_id}/agent/run/{run_id}/logs", params=params
        )
        return AgentRunWithLogsResponse(**response.json())

    def list_agent_runs(self, skip: int = 0, limit: int = 100) -> AgentRunsResponse:
        """List agent runs for the organization"""
        params = {"skip": skip, "limit": limit}
        response = self._make_request(
            "GET", f"/v1/organizations/{self.org_id}/agent/runs", params=params
        )
        return AgentRunsResponse(**response.json())

    def get_stats(self) -> Optional[ClientStats]:
        """Get client statistics"""
        return self.stats

    def clear_cache(self):
        """Clear the client cache"""
        if self.cache:
            self.cache.clear()
