"""
Codegen API Client

This module provides a client for the Codegen API.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List


class CodegenClient:
    """Client for the Codegen API"""
    
    def __init__(self, api_token: str, org_id: int, base_url: str = "https://api.codegen.com/v1"):
        """Initialize the Codegen API client"""
        self.api_token = api_token
        self.org_id = org_id
        self.base_url = base_url
        
        # Set up logging
        self.logger = logging.getLogger("codegen_api")
        self.logger.setLevel(logging.INFO)
        
        # Log initialization
        self.logger.info(f"Initialized CodegenClient with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-Organization-ID": str(self.org_id)
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Codegen API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data
            )
            
            # Raise an exception for HTTP errors
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {url}: {str(e)}")
            raise
    
    def create_task(self, repo: str, task_type: str, query: str, branch: Optional[str] = None, pr: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task"""
        data = {
            "repo": repo,
            "task_type": task_type,
            "query": query
        }
        
        if branch:
            data["branch"] = branch
        
        if pr:
            data["pr"] = pr
        
        return self._make_request("POST", "tasks", data)
    
    def resume_task(self, task_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        """Resume an existing task"""
        data = {"task_id": task_id}
        
        if message:
            data["message"] = message
        
        return self._make_request("POST", f"tasks/{task_id}/resume", data)
    
    def list_tasks(self, status: Optional[str] = None, repo: Optional[str] = None, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """List tasks"""
        params = {}
        
        if status:
            params["status"] = status
        
        if repo:
            params["repo"] = repo
        
        params["limit"] = limit
        
        return self._make_request("GET", "tasks", params)
    
    def get_task(self, task_id: str, verbose: bool = False) -> Dict[str, Any]:
        """Get task details"""
        params = {}
        
        if verbose:
            params["verbose"] = "true"
        
        return self._make_request("GET", f"tasks/{task_id}", params)
    
    def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a task"""
        data = {}
        
        if reason:
            data["reason"] = reason
        
        return self._make_request("POST", f"tasks/{task_id}/cancel", data)

