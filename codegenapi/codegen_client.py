"""
Codegen API Client

Clean, focused API client based on PR 8's architecture.
Handles all Codegen API interactions with proper error handling and logging.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .models import AgentRun
from .exceptions import CodegenAPIError, CodegenAuthError, CodegenConnectionError

logger = logging.getLogger(__name__)


@dataclass
class PaginatedResponse:
    """Paginated API response"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class CodegenClient:
    """
    Codegen API client with enhanced error handling and logging.
    
    Based on PR 8's architecture but simplified for the specific use case.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        org_id: Optional[int] = None,
        base_url: str = "https://api.codegen.com/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize the Codegen client"""
        self.token = token or os.getenv("CODEGEN_API_TOKEN")
        self.org_id = org_id or int(os.getenv("CODEGEN_ORG_ID", "0"))
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.token:
            raise CodegenAuthError("API token is required")
        
        if not self.org_id:
            raise CodegenAuthError("Organization ID is required")
        
        # Configure session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "CodegenAPI-CLI/2.0"
        })
        
        logger.info(f"Initialized CodegenClient for org {self.org_id}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method == "POST":
                    response = self.session.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle response
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise CodegenAuthError("Authentication failed - invalid token")
                elif response.status_code == 403:
                    raise CodegenAuthError("Access forbidden - insufficient permissions")
                elif response.status_code == 404:
                    raise CodegenAPIError("Requested resource not found")
                elif response.status_code == 429:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise CodegenAPIError("Rate limit exceeded")
                else:
                    try:
                        error_data = response.json()
                        error_message = error_data.get("detail", f"HTTP {response.status_code}")
                    except:
                        error_message = f"HTTP {response.status_code}"
                    
                    raise CodegenAPIError(f"API request failed: {error_message}")
            
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection failed, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise CodegenConnectionError(f"Connection failed: {e}")
            
            except requests.exceptions.Timeout as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request timeout, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise CodegenConnectionError(f"Request timeout: {e}")
        
        raise CodegenAPIError("Request failed after all retries")
    
    def create_agent_run(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentRun:
        """Create a new agent run"""
        data = {
            "prompt": prompt,
            "images": images or [],
            "metadata": metadata or {}
        }
        
        response = self._make_request("POST", f"/organizations/{self.org_id}/agent/run", data=data)
        return self._parse_agent_run(response)
    
    def get_agent_run(self, agent_run_id: int) -> AgentRun:
        """Get details of a specific agent run"""
        response = self._make_request("GET", f"/organizations/{self.org_id}/agent/run/{agent_run_id}")
        return self._parse_agent_run(response)
    
    def list_agent_runs(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> PaginatedResponse:
        """List agent runs for the organization"""
        params = {"skip": skip, "limit": limit}
        if status_filter:
            params["status"] = status_filter
        
        response = self._make_request("GET", f"/organizations/{self.org_id}/agent/runs", params=params)
        
        # Parse agent runs
        runs = [self._parse_agent_run(run_data) for run_data in response.get("items", [])]
        
        return PaginatedResponse(
            items=runs,
            total=response.get("total", len(runs)),
            page=response.get("page", 1),
            size=response.get("size", limit),
            pages=response.get("pages", 1)
        )
    
    def resume_agent_run(
        self,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None
    ) -> AgentRun:
        """Resume a paused agent run"""
        data = {
            "agent_run_id": agent_run_id,
            "prompt": prompt,
            "images": images or []
        }
        
        response = self._make_request("POST", f"/organizations/{self.org_id}/agent/run/resume", data=data)
        return self._parse_agent_run(response)
    
    def get_agent_run_logs(
        self,
        agent_run_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get logs for an agent run"""
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", f"/alpha/organizations/{self.org_id}/agent/run/{agent_run_id}/logs", params=params)
        return response.get("logs", [])
    
    def cancel_agent_run(self, agent_run_id: int) -> bool:
        """Cancel an active agent run"""
        try:
            # Try the most likely endpoint first
            data = {"agent_run_id": agent_run_id}
            self._make_request("POST", f"/organizations/{self.org_id}/agent/run/cancel", data=data)
            return True
        except CodegenAPIError:
            logger.warning(f"Failed to cancel agent run {agent_run_id}")
            return False
    
    def _parse_agent_run(self, data: Dict[str, Any]) -> AgentRun:
        """Parse agent run data from API response"""
        return AgentRun(
            id=data.get("id", 0),
            organization_id=data.get("organization_id", self.org_id),
            status=data.get("status"),
            prompt=data.get("prompt"),
            result=data.get("result"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
            completed_at=self._parse_datetime(data.get("completed_at")),
            web_url=data.get("web_url"),
            cost=float(data.get("cost", 0.0)) if data.get("cost") is not None else 0.0,
            tokens_used=int(data.get("tokens_used", 0)) if data.get("tokens_used") is not None else 0,
            metadata=data.get("metadata", {})
        )
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not date_str:
            return None
        
        try:
            # Handle different datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Unable to parse datetime: {date_str}")
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing datetime '{date_str}': {e}")
            return None

