"""
Codegen API Client Implementation

Enhanced implementation based on PR 8's SDK architecture with proper
error handling, logging, caching, and type safety.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid

from ..interfaces.codegen_integration import (
    ICodegenClient, IAuthManager, ICacheManager, IDataTransformer,
    AgentRun, Organization, User, AgentRunLog, PaginatedResponse,
    SourceType, RunStatus
)
from .error_handling import CodegenAPIError, CodegenConnectionError, CodegenAuthError
from .auth_manager import AuthManager
from .cache_manager import CacheManager
from .data_transformer import DataTransformer

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """Configuration for the Codegen client"""
    base_url: str = field(default_factory=lambda: os.getenv("CODEGEN_BASE_URL", "https://api.codegen.com/v1"))
    timeout: int = 30
    max_retries: int = 3
    rate_limit_requests_per_period: int = 100
    rate_limit_period_seconds: int = 60
    cache_ttl_seconds: int = 300
    log_level: str = "INFO"
    log_requests: bool = False
    log_responses: bool = False
    verify_ssl: bool = True


class CodegenClient(ICodegenClient):
    """
    Enhanced Codegen API client with comprehensive error handling,
    caching, logging, and type safety.
    
    Based on PR 8's architecture with improvements for the new layered system.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        org_id: Optional[int] = None,
        config: Optional[ClientConfig] = None
    ):
        """Initialize the Codegen client"""
        self.config = config or ClientConfig()
        
        # Initialize managers
        self.auth_manager = AuthManager(token)
        self.cache_manager = CacheManager(ttl_seconds=self.config.cache_ttl_seconds)
        self.data_transformer = DataTransformer()
        
        # Set organization ID
        self.org_id = org_id or int(os.getenv("CODEGEN_ORG_ID", "0"))
        
        # Configure session
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        
        # Rate limiting
        self._request_times: List[float] = []
        
        # Request tracking
        self._request_id = 0
        
        logger.info(f"Initialized CodegenClient with base URL: {self.config.base_url}")
    
    def _get_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        self._request_id += 1
        return f"{uuid.uuid4().hex[:8]}-{self._request_id}"
    
    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        now = time.time()
        
        # Remove old requests outside the rate limit window
        cutoff_time = now - self.config.rate_limit_period_seconds
        self._request_times = [t for t in self._request_times if t > cutoff_time]
        
        # Check if we're at the limit
        if len(self._request_times) >= self.config.rate_limit_requests_per_period:
            sleep_time = self._request_times[0] + self.config.rate_limit_period_seconds - now
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        # Record this request
        self._request_times.append(now)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling, caching, and logging"""
        
        # Check authentication
        if not self.auth_manager.is_authenticated():
            raise CodegenAuthError("No valid authentication token")
        
        # Generate request ID for tracking
        request_id = self._get_request_id()
        
        # Check rate limiting
        self._check_rate_limit()
        
        # Build URL
        url = f"{self.config.base_url}{endpoint}"
        
        # Check cache for GET requests
        cache_key = None
        if method == "GET" and use_cache:
            cache_key = f"{method}:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
            cached_response = self.cache_manager.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_response
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.auth_manager.get_current_token()}",
            "Content-Type": "application/json",
            "User-Agent": "CodegenSDK/2.0"
        }
        
        # Log request
        if self.config.log_requests:
            logger.info(f"Making {method} request to {endpoint} (request_id: {request_id})")
            if data and self.config.log_level == "DEBUG":
                logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        # Make request with retries
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = self.session.get(url, headers=headers, params=params, timeout=self.config.timeout)
                elif method == "POST":
                    response = self.session.post(url, headers=headers, json=data, timeout=self.config.timeout)
                elif method == "PUT":
                    response = self.session.put(url, headers=headers, json=data, timeout=self.config.timeout)
                elif method == "DELETE":
                    response = self.session.delete(url, headers=headers, timeout=self.config.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                duration = time.time() - start_time
                
                # Log response
                if self.config.log_requests:
                    logger.info(f"Request completed in {duration:.2f}s - Status: {response.status_code} (request_id: {request_id})")
                
                # Handle response
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # Log response data
                        if self.config.log_responses and self.config.log_level == "DEBUG":
                            logger.debug(f"Response data: {json.dumps(result, indent=2)}")
                        
                        # Cache successful GET responses
                        if method == "GET" and use_cache and cache_key:
                            self.cache_manager.set(cache_key, result)
                        
                        return result
                        
                    except json.JSONDecodeError as e:
                        raise CodegenAPIError(f"Invalid JSON response: {e}")
                
                elif response.status_code == 401:
                    raise CodegenAuthError("Authentication failed - invalid token")
                
                elif response.status_code == 403:
                    raise CodegenAuthError("Access forbidden - insufficient permissions")
                
                elif response.status_code == 404:
                    raise CodegenAPIError("Requested resource not found")
                
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise CodegenAPIError("Rate limit exceeded")
                
                else:
                    # Try to get error details from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("detail", f"HTTP {response.status_code}")
                    except:
                        error_message = f"HTTP {response.status_code}"
                    
                    raise CodegenAPIError(f"API request failed: {response.status_code} - {error_message}")
            
            except requests.exceptions.ConnectionError as e:
                last_exception = CodegenConnectionError(f"Connection failed: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection failed, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
            
            except requests.exceptions.Timeout as e:
                last_exception = CodegenConnectionError(f"Request timeout: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
            
            except (CodegenAPIError, CodegenAuthError):
                # Don't retry API errors
                raise
            
            except Exception as e:
                last_exception = CodegenAPIError(f"Unexpected error: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Unexpected error, retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
        
        # All retries failed
        logger.error(f"Request failed after {self.config.max_retries + 1} attempts (request_id: {request_id})")
        raise last_exception or CodegenAPIError("Request failed after all retries")
    
    # ICodegenClient implementation
    
    def get_current_user(self) -> User:
        """Get current authenticated user information"""
        try:
            data = self._make_request("GET", "/users/me")
            return self.data_transformer.transform_user(data)
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise
    
    def get_organizations(self, skip: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get organizations for the authenticated user"""
        try:
            params = {"skip": skip, "limit": limit}
            data = self._make_request("GET", "/organizations", params=params)
            return self.data_transformer.transform_paginated_response(
                data, self.data_transformer.transform_organization
            )
        except Exception as e:
            logger.error(f"Failed to get organizations: {e}")
            raise
    
    def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentRun:
        """Create a new agent run"""
        try:
            data = {
                "prompt": prompt,
                "images": images or [],
                "metadata": metadata or {}
            }
            response = self._make_request("POST", f"/organizations/{org_id}/agent/run", data=data, use_cache=False)
            return self.data_transformer.transform_agent_run(response)
        except Exception as e:
            logger.error(f"Failed to create agent run: {e}")
            raise
    
    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRun:
        """Get details of a specific agent run"""
        try:
            data = self._make_request("GET", f"/organizations/{org_id}/agent/run/{agent_run_id}")
            return self.data_transformer.transform_agent_run(data)
        except Exception as e:
            logger.error(f"Failed to get agent run {agent_run_id}: {e}")
            raise
    
    def list_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse:
        """List agent runs for an organization"""
        try:
            params = {"skip": skip, "limit": limit}
            if user_id:
                params["user_id"] = user_id
            if source_type:
                params["source_type"] = source_type.value
            
            data = self._make_request("GET", f"/organizations/{org_id}/agent/runs", params=params)
            return self.data_transformer.transform_paginated_response(
                data, self.data_transformer.transform_agent_run
            )
        except Exception as e:
            logger.error(f"Failed to list agent runs: {e}")
            raise
    
    def resume_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None
    ) -> AgentRun:
        """Resume a paused agent run"""
        try:
            data = {
                "agent_run_id": agent_run_id,
                "prompt": prompt,
                "images": images or []
            }
            response = self._make_request("POST", f"/organizations/{org_id}/agent/run/resume", data=data, use_cache=False)
            return self.data_transformer.transform_agent_run(response)
        except Exception as e:
            logger.error(f"Failed to resume agent run {agent_run_id}: {e}")
            raise
    
    def get_agent_run_logs(
        self,
        org_id: int,
        agent_run_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse:
        """Get logs for an agent run"""
        try:
            params = {"skip": skip, "limit": limit}
            data = self._make_request("GET", f"/alpha/organizations/{org_id}/agent/run/{agent_run_id}/logs", params=params)
            
            # Transform the logs from the response
            logs = [self.data_transformer.transform_agent_run_log(log) for log in data.get("logs", [])]
            
            return PaginatedResponse(
                items=logs,
                total=data.get("total_logs", len(logs)),
                page=data.get("page", 1),
                size=data.get("size", limit),
                pages=data.get("pages", 1)
            )
        except Exception as e:
            logger.error(f"Failed to get logs for agent run {agent_run_id}: {e}")
            raise
    
    def cancel_agent_run(self, org_id: int, agent_run_id: int) -> bool:
        """Cancel an active agent run"""
        try:
            # Try different cancel endpoints as the exact endpoint may vary
            cancel_endpoints = [
                f"/organizations/{org_id}/agent/run/{agent_run_id}/cancel",
                f"/organizations/{org_id}/agent/runs/{agent_run_id}/cancel",
                f"/organizations/{org_id}/agent/run/cancel"
            ]
            
            for endpoint in cancel_endpoints:
                try:
                    if "run/cancel" in endpoint and not endpoint.endswith(f"/{agent_run_id}/cancel"):
                        # For endpoints that expect the ID in the body
                        data = {"agent_run_id": agent_run_id}
                        self._make_request("POST", endpoint, data=data, use_cache=False)
                    else:
                        # For endpoints that expect the ID in the URL
                        self._make_request("POST", endpoint, use_cache=False)
                    return True
                except CodegenAPIError as e:
                    if "404" in str(e) or "405" in str(e):
                        continue  # Try next endpoint
                    raise
            
            logger.warning(f"No working cancel endpoint found for agent run {agent_run_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel agent run {agent_run_id}: {e}")
            return False
    
    def pause_agent_run(self, org_id: int, agent_run_id: int) -> bool:
        """Pause an active agent run"""
        try:
            # Try different pause endpoints
            pause_endpoints = [
                f"/organizations/{org_id}/agent/run/{agent_run_id}/pause",
                f"/organizations/{org_id}/agent/runs/{agent_run_id}/pause"
            ]
            
            for endpoint in pause_endpoints:
                try:
                    self._make_request("POST", endpoint, use_cache=False)
                    return True
                except CodegenAPIError as e:
                    if "404" in str(e) or "405" in str(e):
                        continue  # Try next endpoint
                    raise
            
            logger.warning(f"No working pause endpoint found for agent run {agent_run_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause agent run {agent_run_id}: {e}")
            return False

