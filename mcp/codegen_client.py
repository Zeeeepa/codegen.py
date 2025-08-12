"""
Simplified Codegen API client for MCP server
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

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
    def __init__(self, message: str, status_code: int = 0, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

class ValidationError(CodegenAPIError):
    """Validation error for request parameters"""
    pass

class RateLimitError(CodegenAPIError):
    """Rate limiting error"""
    pass

class AuthenticationError(CodegenAPIError):
    """Authentication/authorization error"""
    pass

class NotFoundError(CodegenAPIError):
    """Resource not found error"""
    pass

# ============================================================================
# API CLIENT
# ============================================================================

class CodegenClient:
    """
    Simplified Codegen API client for MCP server
    """
    def __init__(
        self, 
        org_id: Optional[str] = None, 
        api_token: Optional[str] = None,
        base_url: str = "https://api.codegen.com"
    ):
        self.org_id = org_id or os.environ.get("CODEGEN_ORG_ID")
        self.api_token = api_token or os.environ.get("CODEGEN_API_TOKEN")
        self.base_url = base_url
        
        if not self.org_id:
            logger.warning("Organization ID not provided. Set CODEGEN_ORG_ID environment variable or pass org_id parameter.")
        
        if not self.api_token:
            logger.warning("API token not provided. Set CODEGEN_API_TOKEN environment variable or pass api_token parameter.")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text}

        if response.status_code >= 400:
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Check your API token.")
            elif response.status_code == 403:
                raise AuthenticationError("Permission denied. Check your organization access.")
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {response.url}")
            elif response.status_code == 422:
                raise ValidationError(f"Validation error: {data.get('detail', 'Unknown validation error')}")
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds.")
            else:
                raise CodegenAPIError(
                    f"API error: {data.get('detail', 'Unknown error')}",
                    status_code=response.status_code,
                    response_data=data
                )
        
        return data

    def get_organizations(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get organizations for the authenticated user"""
        url = f"{self.base_url}/v1/organizations"
        params = {"skip": skip, "limit": limit}
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def create_agent_run(
        self, 
        prompt: str, 
        org_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        orchestrator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new agent run"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        
        url = f"{self.base_url}/v1/organizations/{org_id}/agent/run"
        
        payload = {
            "prompt": prompt,
            "images": images or [],
            "metadata": metadata or {}
        }
        
        # Add orchestrator ID to metadata if provided
        if orchestrator_id:
            if not payload["metadata"]:
                payload["metadata"] = {}
            payload["metadata"]["orchestrator_id"] = orchestrator_id
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        return self._handle_response(response)

    def get_agent_run(self, org_id: Optional[str] = None, agent_run_id: str = None) -> Dict[str, Any]:
        """Get agent run details"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        if not agent_run_id:
            raise ValidationError("Agent run ID is required")
        
        url = f"{self.base_url}/v1/organizations/{org_id}/agent/run/{agent_run_id}"
        
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def resume_agent_run(
        self, 
        agent_run_id: str, 
        prompt: str,
        org_id: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Resume a paused agent run"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        if not agent_run_id:
            raise ValidationError("Agent run ID is required")
        
        url = f"{self.base_url}/v1/organizations/{org_id}/agent/run/resume"
        
        payload = {
            "agent_run_id": agent_run_id,
            "prompt": prompt,
            "images": images or []
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        return self._handle_response(response)

    def list_agent_runs(
        self, 
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """List agent runs for an organization"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        
        url = f"{self.base_url}/v1/organizations/{org_id}/agent/runs"
        
        params = {
            "skip": skip,
            "limit": limit
        }
        
        if user_id:
            params["user_id"] = user_id
        if source_type:
            params["source_type"] = source_type
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def get_agent_run_logs(
        self, 
        agent_run_id: str, 
        org_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get logs for an agent run"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        if not agent_run_id:
            raise ValidationError("Agent run ID is required")
        
        url = f"{self.base_url}/v1/organizations/{org_id}/agent/run/{agent_run_id}/logs"
        
        params = {
            "skip": skip,
            "limit": limit
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def wait_for_completion(
        self, 
        agent_run_id: str, 
        org_id: Optional[str] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Wait for an agent run to complete"""
        org_id = org_id or self.org_id
        if not org_id:
            raise ValidationError("Organization ID is required")
        
        start_time = time.time()
        while True:
            # Check if timeout has been reached
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Agent run {agent_run_id} did not complete within timeout")
            
            # Get current status
            result = self.get_agent_run(org_id, agent_run_id)
            status = result.get("status")
            
            # Check if completed or failed
            if status in [AgentRunStatus.COMPLETED.value, AgentRunStatus.FAILED.value, AgentRunStatus.CANCELLED.value]:
                return result
            
            # Wait before polling again
            time.sleep(poll_interval)

    def check_orchestrator_status(self, orchestrator_id: str, org_id: Optional[str] = None) -> bool:
        """Check if an orchestrator agent is still running"""
        try:
            result = self.get_agent_run(org_id, orchestrator_id)
            status = result.get("status")
            return status == AgentRunStatus.RUNNING.value
        except Exception as e:
            logger.error(f"Error checking orchestrator status: {e}")
            return False

