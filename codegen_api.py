"""
Comprehensive Codegen API SDK
Enhanced Python client for the Codegen API with full feature support
"""

import os
import json
import time
import asyncio
import logging
import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Callable, AsyncGenerator, Iterator
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps, lru_cache
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# HTTP clients
import requests
from requests import exceptions as requests_exceptions

try:
    import aiohttp
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
    PLAN_EVALUATION = "PLAN_EVALUATION"
    FINAL_ANSWER = "FINAL_ANSWER"
    ERROR = "ERROR"
    USER_MESSAGE = "USER_MESSAGE"
    USER_GITHUB_ISSUE_COMMENT = "USER_GITHUB_ISSUE_COMMENT"
    INITIAL_PR_GENERATION = "INITIAL_PR_GENERATION"
    DETECT_PR_ERRORS = "DETECT_PR_ERRORS"
    FIX_PR_ERRORS = "FIX_PR_ERRORS"
    PR_CREATION_FAILED = "PR_CREATION_FAILED"
    PR_EVALUATION = "PR_EVALUATION"
    COMMIT_EVALUATION = "COMMIT_EVALUATION"
    AGENT_RUN_LINK = "AGENT_RUN_LINK"

class AgentRunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

# ============================================================================
# EXCEPTIONS
# ============================================================================

class CodegenAPIError(Exception):
    """Base exception for Codegen API errors"""
    def __init__(self, message: str, status_code: int = 0, response_data: Optional[Dict] = None, request_id: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id
        super().__init__(message)

class ValidationError(CodegenAPIError):
    """Validation error for request parameters"""
    def __init__(self, message: str, field_errors: Optional[Dict[str, List[str]]] = None):
        self.field_errors = field_errors or {}
        super().__init__(message, 400)

class RateLimitError(CodegenAPIError):
    """Rate limiting error with retry information"""
    def __init__(self, retry_after: int = 60, request_id: Optional[str] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds", 429, request_id=request_id)

class AuthenticationError(CodegenAPIError):
    """Authentication/authorization error"""
    def __init__(self, message: str = "Authentication failed", request_id: Optional[str] = None):
        super().__init__(message, 401, request_id=request_id)

class NotFoundError(CodegenAPIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", request_id: Optional[str] = None):
        super().__init__(message, 404, request_id=request_id)

class ServerError(CodegenAPIError):
    """Server-side error (5xx)"""
    def __init__(self, message: str = "Server error occurred", status_code: int = 500, request_id: Optional[str] = None):
        super().__init__(message, status_code, request_id=request_id)

class TimeoutError(CodegenAPIError):
    """Request timeout error"""
    def __init__(self, message: str = "Request timed out", request_id: Optional[str] = None):
        super().__init__(message, 408, request_id=request_id)

class NetworkError(CodegenAPIError):
    """Network connectivity error"""
    def __init__(self, message: str = "Network error occurred", request_id: Optional[str] = None):
        super().__init__(message, 0, request_id=request_id)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserResponse:
    id: int
    email: Optional[str]
    github_user_id: str
    github_username: str
    avatar_url: Optional[str]
    full_name: Optional[str]

@dataclass
class GithubPullRequestResponse:
    id: int
    title: str
    url: str
    created_at: str

@dataclass
class OrganizationSettings:
    enable_pr_creation: bool = True
    enable_rules_detection: bool = True

@dataclass
class OrganizationResponse:
    id: int
    name: str
    settings: OrganizationSettings

@dataclass
class AgentRunResponse:
    id: int
    organization_id: int
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    source_type: Optional[SourceType]
    github_pull_requests: Optional[List[GithubPullRequestResponse]]
    metadata: Optional[Dict[str, Any]]

@dataclass
class AgentRunLogResponse:
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Union[Dict[str, Any], str]] = None

@dataclass
class PaginatedResponse:
    total: int
    page: int
    size: int
    pages: int

@dataclass
class UsersResponse(PaginatedResponse):
    items: List[UserResponse]

@dataclass
class AgentRunsResponse(PaginatedResponse):
    items: List[AgentRunResponse]

@dataclass
class OrganizationsResponse(PaginatedResponse):
    items: List[OrganizationResponse]

@dataclass
class AgentRunWithLogsResponse:
    id: int
    organization_id: int
    logs: List[AgentRunLogResponse]
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    metadata: Optional[Dict[str, Any]]
    total_logs: Optional[int]
    page: Optional[int]
    size: Optional[int]
    pages: Optional[int]

@dataclass
class BulkOperationResult:
    """Result of a bulk operation"""
    total_items: int
    successful_items: int
    failed_items: int
    success_rate: float
    duration_seconds: float
    errors: List[Dict[str, Any]]
    results: List[Any]

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    method: str
    endpoint: str
    status_code: int
    duration_seconds: float
    timestamp: datetime
    request_id: str
    cached: bool = False

@dataclass
class ClientStats:
    """Comprehensive client statistics"""
    uptime_seconds: float
    total_requests: int
    total_errors: int
    error_rate: float
    requests_per_minute: float
    average_response_time: float
    cache_hit_rate: float
    status_code_distribution: Dict[int, int]
    recent_requests: List[RequestMetrics]

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ClientConfig:
    """Configuration for the Codegen client"""
    # Core settings
    api_token: str = field(default_factory=lambda: os.getenv("CODEGEN_API_TOKEN", ""))
    org_id: str = field(default_factory=lambda: os.getenv("CODEGEN_ORG_ID", ""))
    base_url: str = field(default_factory=lambda: os.getenv("CODEGEN_BASE_URL", "https://api.codegen.com/v1"))
    
    # Performance settings
    timeout: int = field(default_factory=lambda: int(os.getenv("CODEGEN_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("CODEGEN_MAX_RETRIES", "3")))
    retry_delay: float = field(default_factory=lambda: float(os.getenv("CODEGEN_RETRY_DELAY", "1.0")))
    retry_backoff_factor: float = field(default_factory=lambda: float(os.getenv("CODEGEN_RETRY_BACKOFF", "2.0")))
    
    # Rate limiting
    rate_limit_requests_per_period: int = field(default_factory=lambda: int(os.getenv("CODEGEN_RATE_LIMIT_REQUESTS", "60")))
    rate_limit_period_seconds: int = field(default_factory=lambda: int(os.getenv("CODEGEN_RATE_LIMIT_PERIOD", "60")))
    
    # Caching
    enable_caching: bool = field(default_factory=lambda: os.getenv("CODEGEN_ENABLE_CACHING", "true").lower() == "true")
    cache_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("CODEGEN_CACHE_TTL", "300")))
    cache_max_size: int = field(default_factory=lambda: int(os.getenv("CODEGEN_CACHE_MAX_SIZE", "128")))
    
    # Features
    enable_webhooks: bool = field(default_factory=lambda: os.getenv("CODEGEN_ENABLE_WEBHOOKS", "true").lower() == "true")
    enable_bulk_operations: bool = field(default_factory=lambda: os.getenv("CODEGEN_ENABLE_BULK_OPERATIONS", "true").lower() == "true")
    enable_streaming: bool = field(default_factory=lambda: os.getenv("CODEGEN_ENABLE_STREAMING", "true").lower() == "true")
    enable_metrics: bool = field(default_factory=lambda: os.getenv("CODEGEN_ENABLE_METRICS", "true").lower() == "true")
    
    # Bulk operations
    bulk_max_workers: int = field(default_factory=lambda: int(os.getenv("CODEGEN_BULK_MAX_WORKERS", "5")))
    bulk_batch_size: int = field(default_factory=lambda: int(os.getenv("CODEGEN_BULK_BATCH_SIZE", "100")))
    
    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("CODEGEN_LOG_LEVEL", "INFO"))
    log_requests: bool = field(default_factory=lambda: os.getenv("CODEGEN_LOG_REQUESTS", "true").lower() == "true")
    log_responses: bool = field(default_factory=lambda: os.getenv("CODEGEN_LOG_RESPONSES", "false").lower() == "true")
    
    # User agent
    user_agent: str = field(default_factory=lambda: "codegen-python-client/2.0.0")
    
    def __post_init__(self):
        if not self.api_token:
            raise ValueError("API token is required. Set CODEGEN_API_TOKEN environment variable or provide it directly.")
        # Set up logging
        logging.basicConfig(level=getattr(logging, self.log_level.upper()))

class ConfigPresets:
    """Predefined configuration presets"""
    
    @staticmethod
    def development() -> ClientConfig:
        """Development configuration with verbose logging and lower limits"""
        return ClientConfig(
            timeout=60,
            max_retries=1,
            rate_limit_requests_per_period=30,
            cache_ttl_seconds=60,
            log_level="DEBUG",
            log_requests=True,
            log_responses=True,
        )
    
    @staticmethod
    def production() -> ClientConfig:
        """Production configuration with optimized settings"""
        return ClientConfig(
            timeout=30,
            max_retries=3,
            rate_limit_requests_per_period=100,
            cache_ttl_seconds=300,
            log_level="INFO",
            log_requests=True,
            log_responses=False,
        )
    
    @staticmethod
    def testing() -> ClientConfig:
        """Testing configuration with minimal caching and retries"""
        return ClientConfig(
            timeout=10,
            max_retries=1,
            enable_caching=False,
            rate_limit_requests_per_period=10,
            log_level="DEBUG",
        )

# ============================================================================
# UTILITY CLASSES
# ============================================================================

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0, base_delay: float = 1.0):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries:
                        raise
                    logger.warning(f"Rate limited, waiting {e.retry_after} seconds")
                    time.sleep(e.retry_after)
                except (requests.RequestException, NetworkError) as e:
                    if attempt == max_retries:
                        raise CodegenAPIError(f"Request failed after {max_retries} retries: {str(e)}", 0)
                    sleep_time = base_delay * (backoff_factor ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {sleep_time}s: {str(e)}")
                    time.sleep(sleep_time)
            return None
        return wrapper
    return decorator

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
            self.requests = [req_time for req_time in self.requests if now - req_time < self.period_seconds]
            
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
            recent_requests = [req_time for req_time in self.requests if now - req_time < self.period_seconds]
            return {
                "current_requests": len(recent_requests),
                "max_requests": self.requests_per_period,
                "period_seconds": self.period_seconds,
                "usage_percentage": (len(recent_requests) / self.requests_per_period) * 100,
            }

class CacheManager:
    """Advanced in-memory cache with TTL support and statistics"""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                del self._access_counts[key]
                self._misses += 1
                return None
            
            self._hits += 1
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache with TTL"""
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                if self._timestamps:
                    oldest_key = min(self._timestamps, key=self._timestamps.get)
                    del self._cache[oldest_key]
                    del self._timestamps[oldest_key]
                    if oldest_key in self._access_counts:
                        del self._access_counts[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0)
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counts.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_percentage": hit_rate,
                "ttl_seconds": self.ttl_seconds,
            }

class BulkOperationManager:
    """Advanced manager for bulk operations with progress tracking"""
    
    def __init__(self, max_workers: int = 5, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
    
    def execute_bulk_operation(
        self,
        operation_func: Callable,
        items: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        *args,
        **kwargs
    ) -> BulkOperationResult:
        """Execute a bulk operation with error handling, metrics, and progress tracking"""
        start_time = time.time()
        results = []
        errors = []
        successful_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(operation_func, item, *args, **kwargs): (i, item)
                for i, item in enumerate(items)
            }
            
            # Collect results with progress tracking
            completed = 0
            for future in as_completed(future_to_item):
                i, item = future_to_item[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    successful_count += 1
                except Exception as e:
                    error_info = {
                        "index": i,
                        "item": str(item),
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    errors.append(error_info)
                    logger.error(f"Bulk operation failed for item {i}: {str(e)}")
                
                # Call progress callback
                if progress_callback:
                    progress_callback(completed, len(items))
        
        duration = time.time() - start_time
        success_rate = successful_count / len(items) if items else 0
        
        return BulkOperationResult(
            total_items=len(items),
            successful_items=successful_count,
            failed_items=len(errors),
            success_rate=success_rate,
            duration_seconds=duration,
            errors=errors,
            results=results,
        )

class MetricsCollector:
    """Advanced metrics collection and analysis"""
    
    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self.start_time = datetime.now()
        self._lock = Lock()
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        request_id: str,
        cached: bool = False,
    ):
        """Record a request with comprehensive metrics"""
        with self._lock:
            metric = RequestMetrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                timestamp=datetime.now(),
                request_id=request_id,
                cached=cached,
            )
            self.requests.append(metric)
            
            # Keep only recent requests (last 1000)
            if len(self.requests) > 1000:
                self.requests = self.requests[-1000:]
    
    def get_stats(self) -> ClientStats:
        """Get comprehensive client statistics"""
        with self._lock:
            if not self.requests:
                return ClientStats(
                    uptime_seconds=0,
                    total_requests=0,
                    total_errors=0,
                    error_rate=0,
                    requests_per_minute=0,
                    average_response_time=0,
                    cache_hit_rate=0,
                    status_code_distribution={},
                    recent_requests=[],
                )
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            total_requests = len(self.requests)
            error_requests = [r for r in self.requests if r.status_code >= 400]
            cached_requests = [r for r in self.requests if r.cached]
            
            avg_response_time = sum(r.duration_seconds for r in self.requests) / total_requests
            error_rate = len(error_requests) / total_requests if total_requests > 0 else 0
            cache_hit_rate = len(cached_requests) / total_requests if total_requests > 0 else 0
            requests_per_minute = total_requests / (uptime / 60) if uptime > 0 else 0
            
            # Status code distribution
            status_codes = {}
            for request in self.requests:
                status_codes[request.status_code] = status_codes.get(request.status_code, 0) + 1
            
            return ClientStats(
                uptime_seconds=uptime,
                total_requests=total_requests,
                total_errors=len(error_requests),
                error_rate=error_rate,
                requests_per_minute=requests_per_minute,
                average_response_time=avg_response_time,
                cache_hit_rate=cache_hit_rate,
                status_code_distribution=status_codes,
                recent_requests=self.requests[-10:],
            )
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.requests.clear()
            self.start_time = datetime.now()

# ============================================================================
# MAIN CLIENT CLASS
# ============================================================================

class CodegenClient:
    """Enhanced synchronous Codegen API client with comprehensive features"""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self.headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }
        
        # Initialize components
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests_per_period,
            self.config.rate_limit_period_seconds,
        )
        
        # Caching
        self.cache = (
            CacheManager(
                max_size=self.config.cache_max_size,
                ttl_seconds=self.config.cache_ttl_seconds,
            )
            if self.config.enable_caching
            else None
        )
        
        # Bulk operations
        self.bulk_manager = (
            BulkOperationManager(
                max_workers=self.config.bulk_max_workers,
                batch_size=self.config.bulk_batch_size,
            )
            if self.config.enable_bulk_operations
            else None
        )
        
        # Metrics
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
    
    def _handle_response(self, response: requests.Response, request_id: str) -> Dict[str, Any]:
        """Handle HTTP response with comprehensive error handling"""
        status_code: int = response.status_code
        
        if status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))
            raise RateLimitError(retry_after, request_id)
        
        if status_code == 401:
            raise AuthenticationError("Invalid API token or insufficient permissions", request_id)
        elif status_code == 404:
            raise NotFoundError("Requested resource not found", request_id)
        elif status_code >= 500:
            raise ServerError(f"Server error: {status_code}", status_code, request_id)
        elif not response.ok:
            try:
                error_data = response.json()
                message = error_data.get("message", f"API request failed: {status_code}")
            except Exception:
                message = f"API request failed: {status_code}"
                error_data = None
            raise CodegenAPIError(message, status_code, error_data, request_id)
        
        return response.json()
    
    def _make_request(self, method: str, endpoint: str, use_cache: bool = False, **kwargs) -> Dict[str, Any]:
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
                    self.metrics.record_request(method, endpoint, 0, 200, request_id, cached=True)
                return cached_result
        
        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
            base_delay=self.config.retry_delay,
        )
        def _execute_request():
            start_time = time.time()
            url = f"{self.config.base_url}{endpoint}"
            
            if self.config.log_requests:
                logger.info(f"Making {method} request to {endpoint} (request_id: {request_id})")
            
            try:
                response = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
                duration = time.time() - start_time
                
                if self.config.log_requests:
                    logger.info(f"Request completed in {duration:.2f}s - Status: {response.status_code} (request_id: {request_id})")
                
                if self.config.log_responses and response.ok:
                    logger.debug(f"Response: {response.text}")
                
                # Record metrics
                if self.metrics:
                    self.metrics.record_request(method, endpoint, duration, response.status_code, request_id)
                
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
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Request failed after {duration:.2f}s: {str(e)} (request_id: {request_id})")
                if self.metrics:
                    self.metrics.record_request(method, endpoint, duration, 0, request_id)
                raise
        
        return _execute_request()
    
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
        response = self._make_request("GET", f"/v1/organizations/{org_id}/users/{user_id}", use_cache=True)
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
                    settings=OrganizationSettings(
                        enable_pr_creation=org.get("settings", {}).get("enable_pr_creation", True),
                        enable_rules_detection=org.get("settings", {}).get("enable_rules_detection", True),
                    ),
                )
                for org in response["items"]
            ],
            total=response["total"],
            page=response["page"],
            size=response["size"],
            pages=response["pages"],
        )
    
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
        # Validate inputs
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationError("Prompt cannot be empty")
        if len(prompt) > 50000:  # Reasonable limit
            raise ValidationError("Prompt cannot exceed 50,000 characters")
        if images and len(images) > 10:
            raise ValidationError("Cannot include more than 10 images")
        
        data = {"prompt": prompt, "images": images, "metadata": metadata}
        
        response = self._make_request("POST", f"/v1/organizations/{org_id}/agent/run", json=data)
        
        return self._parse_agent_run_response(response)
    
    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRunResponse:
        """Retrieve the status and result of an agent run"""
        response = self._make_request("GET", f"/v1/organizations/{org_id}/agent/run/{agent_run_id}", use_cache=True)
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
        
        response = self._make_request("GET", f"/v1/organizations/{org_id}/agent/runs", params=params, use_cache=True)
        
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
        
        response = self._make_request("POST", f"/v1/organizations/{org_id}/agent/run/resume", json=data)
        
        return self._parse_agent_run_response(response)
    
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
    # ALPHA ENDPOINTS
    # ========================================================================
    
    def get_agent_run_logs(
        self, org_id: int, agent_run_id: int, skip: int = 0, limit: int = 100
    ) -> AgentRunWithLogsResponse:
        """Retrieve an agent run with its logs using pagination (ALPHA)"""
        self._validate_pagination(skip, limit)
        
        response = self._make_request(
            "GET",
            f"/alpha/organizations/{org_id}/agent/run/{agent_run_id}/logs",
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
    
    def get_agent_run_logs(self, org_id: int, agent_run_id: int, skip: int = 0, limit: int = 100) -> AgentRunWithLogsResponse:
        """Get logs for an agent run"""
        params = {
            "skip": skip,
            "limit": min(limit, 100)  # API max is 100
        }
        
        response = self._make_request("GET", f"/v1/organizations/{org_id}/agent/run/{agent_run_id}/logs", params=params, use_cache=True)
        
        # Parse the response according to the API documentation
        logs = []
        for log_data in response.get("logs", []):
            log = AgentRunLogResponse(
                agent_run_id=log_data.get("agent_run_id"),
                created_at=log_data.get("created_at"),
                message_type=log_data.get("message_type"),
                thought=log_data.get("thought"),
                tool_name=log_data.get("tool_name"),
                tool_input=log_data.get("tool_input"),
                tool_output=log_data.get("tool_output"),
                observation=log_data.get("observation")
            )
            logs.append(log)
        
        return AgentRunWithLogsResponse(
            id=response.get("id"),
            organization_id=response.get("organization_id"),
            status=response.get("status"),
            created_at=response.get("created_at"),
            web_url=response.get("web_url"),
            result=response.get("result"),
            logs=logs,
            total_logs=response.get("total_logs", 0),
            page=response.get("page", 1),
            size=response.get("size", limit),
            pages=response.get("pages", 1)
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
            
            if run.status in [
                AgentRunStatus.COMPLETED.value,
                AgentRunStatus.FAILED.value,
                AgentRunStatus.CANCELLED.value,
            ]:
                return run
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Agent run {agent_run_id} did not complete within {timeout} seconds")
            
            time.sleep(poll_interval)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive client statistics"""
        stats = {
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "rate_limit_requests_per_period": self.config.rate_limit_requests_per_period,
                "caching_enabled": self.config.enable_caching,
                "bulk_operations_enabled": self.config.enable_bulk_operations,
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
    
    def clear_cache(self):
        """Clear all cached data"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def reset_metrics(self):
        """Reset all metrics"""
        if self.metrics:
            self.metrics.reset()
            logger.info("Metrics reset")
    
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
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
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

# ============================================================================
# OFFICIAL SDK COMPATIBLE CLASSES
# ============================================================================

class Agent:
    """Official SDK compatible Agent class"""
    
    def __init__(self, token: str, org_id: Optional[int] = None, base_url: Optional[str] = None):
        """
        Initialize the Agent with your organization ID and API token
        
        Args:
            token (required): Your API authentication token
            org_id (optional): Your organization ID. If not provided, defaults to environment variable CODEGEN_ORG_ID or "1"
            base_url (optional): API base URL. Defaults to "https://codegen-sh-rest-api.modal.run"
        """
        # Set defaults matching official SDK
        if org_id is None:
            org_id = os.getenv("CODEGEN_ORG_ID", "1")
        if base_url is None:
            base_url = "https://api.codegen.com"
        
        # Create config for internal client
        config = ClientConfig(
            api_token=token,
            org_id=str(org_id),
            base_url=base_url
        )
        
        self.client = CodegenClient(config)
        self.org_id = int(org_id)
        self.token = token
        self.base_url = base_url
    
    def run(self, prompt: str, images: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> 'AgentTask':
        """
        Runs an agent with the given prompt.
        
        Args:
            prompt (required): The instruction for the agent to execute
            images (optional): List of image URLs to include with the prompt
            metadata (optional): Additional metadata to include with the request
            
        Returns:
            An AgentTask object representing the running task
        """
        agent_run = self.client.create_agent_run(
            org_id=self.org_id,
            prompt=prompt,
            images=images,
            metadata=metadata
        )
        return AgentTask(self.client, self.org_id, agent_run.id, agent_run)
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Gets the status of the current task.
        
        Returns:
            A dictionary containing task status information (id, status, result), or None if no task has been run
        """
        # This would need to track the last task - for now return None
        return None

class AgentTask:
    """Official SDK compatible AgentTask class"""
    
    def __init__(self, client: CodegenClient, org_id: int, task_id: int, initial_data: Optional[AgentRunResponse] = None):
        """
        Initialize AgentTask
        
        Attributes:
            id: The unique identifier for the task
            org_id: The organization ID
            status: Current status of the task (e.g., "queued", "in_progress", "completed", "failed")
            result: The task result (available when status is "completed")
        """
        self.client = client
        self.org_id = org_id
        self.id = task_id
        self._data = initial_data
    
    @property
    def status(self) -> Optional[str]:
        """Current status of the task (e.g., "queued", "in_progress", "completed", "failed")"""
        if not self._data or self._data.status in [AgentRunStatus.PENDING.value, AgentRunStatus.RUNNING.value]:
            self.refresh()
        return self._data.status if self._data else None
    
    @property
    def result(self) -> Optional[str]:
        """The task result (available when status is "completed")"""
        if not self._data:
            self.refresh()
        return self._data.result if self._data else None
    
    @property
    def web_url(self) -> Optional[str]:
        """Get the web URL to view the task"""
        if not self._data:
            self.refresh()
        return self._data.web_url if self._data else None
    
    @property
    def github_pull_requests(self) -> Optional[List[GithubPullRequestResponse]]:
        """Get any GitHub pull requests created by this task"""
        if not self._data:
            self.refresh()
        return self._data.github_pull_requests if self._data else None
    
    def refresh(self) -> None:
        """Refreshes the task status from the API."""
        self._data = self.client.get_agent_run(self.org_id, self.id)
    
    def wait_for_completion(self, timeout: Optional[float] = None, poll_interval: float = 5.0) -> AgentRunResponse:
        """Wait for the task to complete"""
        result = self.client.wait_for_completion(self.org_id, self.id, poll_interval, timeout)
        self._data = result
        return result
    
    def get_logs(self, limit: int = 100) -> AgentRunWithLogsResponse:
        """Get the logs for this task"""
        return self.client.get_agent_run_logs(self.org_id, self.id, limit=limit)
    
    def resume(self, prompt: str, images: Optional[List[str]] = None) -> AgentRunResponse:
        """Resume a paused task"""
        result = self.client.resume_agent_run(self.org_id, self.id, prompt, images)
        self._data = result
        return result
    
    def __str__(self):
        return f"AgentTask(id={self.id}, status={self.status})"
    
    def __repr__(self):
        return self.__str__()

# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Keep the old Task class as an alias for backward compatibility
Task = AgentTask

# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Example usage of the Codegen SDK"""
    print("=== Codegen SDK Example ===")
    
    # Example 1: Using the simplified Agent interface
    print("\n1. Using Agent interface:")
    try:
        with Agent() as agent:
            # Create a task
            task = agent.run("Help me write a Python function to calculate fibonacci numbers")
            print(f"Created task: {task.id}")
            print(f"Status: {task.status}")
            print(f"Web URL: {task.web_url}")
            
            # Wait for completion (with timeout)
            try:
                completed_task = task.wait_for_completion(timeout=300)
                print(f"Task completed with status: {completed_task.status}")
                if completed_task.result:
                    print(f"Result: {completed_task.result[:200]}...")
            except TimeoutError:
                print("Task did not complete within timeout")
    
    except Exception as e:
        print(f"Error with Agent interface: {e}")
    
    # Example 2: Using the full client
    print("\n2. Using full CodegenClient:")
    try:
        config = ConfigPresets.development()
        with CodegenClient(config) as client:
            # Health check
            health = client.health_check()
            print(f"Health check: {health['status']}")
            
            # Get current user
            user = client.get_current_user()
            print(f"Current user: {user.github_username}")
            
            # Get organizations
            orgs = client.get_organizations(limit=1)
            if orgs.items:
                org = orgs.items[0]
                print(f"Organization: {org.name}")
                
                # Create agent run
                agent_run = client.create_agent_run(
                    org_id=org.id,
                    prompt="Create a simple REST API endpoint",
                    metadata={"example": True, "priority": "low"}
                )
                print(f"Created agent run: {agent_run.id}")
                
                # Get stats
                stats = client.get_stats()
                print(f"Client stats: {stats['config']['base_url']}")
                if "metrics" in stats:
                    print(f"Total requests: {stats['metrics']['total_requests']}")
    
    except Exception as e:
        print(f"Error with CodegenClient: {e}")
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()
