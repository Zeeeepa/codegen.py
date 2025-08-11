"""
Codegen API client
"""

import requests
import time
from typing import Dict, Any, Optional
from .exceptions import APIError
from .config import Config


class CodegenClient:
    """HTTP client for Codegen API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get("api.base_url")
        self.token = config.get("api.token")
        self.org_id = config.get("api.org_id")
        self.timeout = config.get("api.timeout", 300)
        
        if not self.token:
            raise APIError("API token is required")
        if not self.org_id:
            raise APIError("Organization ID is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
    
    def create_agent_run(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new agent run"""
        url = f"{self.base_url}/v1/organizations/{self.org_id}/agent/run"
        
        payload = {
            "prompt": prompt,
            "metadata": metadata or {}
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create agent run: {e}")
    
    def get_agent_run(self, run_id: str) -> Dict[str, Any]:
        """Get agent run status and result"""
        url = f"{self.base_url}/v1/organizations/{self.org_id}/agent/run/{run_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get agent run: {e}")
    
    def resume_agent_run(self, run_id: str, prompt: str) -> Dict[str, Any]:
        """Resume an agent run with additional prompt"""
        url = f"{self.base_url}/v1/organizations/{self.org_id}/agent/run/resume"
        
        payload = {
            "agent_run_id": int(run_id),
            "prompt": prompt
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to resume agent run: {e}")
    
    def wait_for_completion(self, run_id: str, timeout: int = None) -> Dict[str, Any]:
        """Wait for agent run to complete"""
        timeout = timeout or self.timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            run_data = self.get_agent_run(run_id)
            status = run_data.get("status", "").lower()
            
            if status in ["completed", "failed", "cancelled"]:
                return run_data
            
            time.sleep(5)  # Poll every 5 seconds
        
        raise APIError(f"Agent run {run_id} did not complete within {timeout} seconds")
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()

