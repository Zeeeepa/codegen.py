"""
Simplified Codegen API Client for Dashboard
"""

import os
import time
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import AgentRun
from .exceptions import CodegenError

logger = logging.getLogger(__name__)


class CodegenClient:
    """Simplified Codegen API client for dashboard use"""
    
    def __init__(
        self,
        token: Optional[str] = None,
        org_id: Optional[int] = None,
        base_url: str = "https://api.codegen.com/v1"
    ):
        """Initialize the Codegen client"""
        self.token = token or os.getenv("CODEGEN_API_TOKEN")
        self.org_id = org_id or int(os.getenv("CODEGEN_ORG_ID", "0"))
        self.base_url = base_url
        
        if not self.token:
            raise CodegenError("API token is required")
        
        if not self.org_id:
            raise CodegenError("Organization ID is required")
        
        # Configure session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "CodegenDashboard/1.0"
        })
        
        logger.info(f"Initialized CodegenClient for org {self.org_id}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle response
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise CodegenError("Authentication failed - invalid token")
            elif response.status_code == 403:
                raise CodegenError("Access forbidden - insufficient permissions")
            elif response.status_code == 404:
                raise CodegenError("Requested resource not found")
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_message = f"HTTP {response.status_code}"
                
                raise CodegenError(f"API request failed: {error_message}")
        
        except requests.exceptions.RequestException as e:
            raise CodegenError(f"Request failed: {e}")
    
    def create_agent_run(
        self,
        prompt: str,
        images: Optional[List[str]] = None
    ) -> AgentRun:
        """Create a new agent run"""
        data = {
            "prompt": prompt,
            "images": images or []
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
        limit: int = 50
    ) -> List[AgentRun]:
        """List agent runs for the organization"""
        params = {"skip": skip, "limit": limit}
        
        response = self._make_request("GET", f"/organizations/{self.org_id}/agent/runs", params=params)
        
        # Parse agent runs
        runs = [self._parse_agent_run(run_data) for run_data in response.get("items", [])]
        return runs
    
    def cancel_agent_run(self, agent_run_id: int) -> bool:
        """Cancel an active agent run"""
        try:
            data = {"agent_run_id": agent_run_id}
            self._make_request("POST", f"/organizations/{self.org_id}/agent/run/cancel", data=data)
            return True
        except CodegenError:
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

