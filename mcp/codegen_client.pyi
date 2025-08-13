"""
Type stub file for codegen_client.py
"""

from typing import Dict, Any, Optional, List, Union

class CodegenAPIError(Exception):
    """Exception raised for Codegen API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None) -> None: ...

class CodegenClient:
    """Client for interacting with the Codegen API"""
    def __init__(
        self, 
        org_id: Optional[str] = None, 
        api_token: Optional[str] = None,
        base_url: str = "https://api.codegen.com"
    ) -> None: ...
    
    # User endpoints
    def get_users(self, org_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> Dict[str, Any]: ...
    
    def get_user(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]: ...
    
    def get_current_user(self) -> Dict[str, Any]: ...
    
    # Organization endpoints
    def get_organizations(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]: ...
    
    # Agent endpoints
    def create_agent_run(
        self, 
        prompt: str, 
        org_id: Optional[str] = None,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        pr: Optional[int] = None,
        task: Optional[str] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        orchestrator_id: Optional[str] = None
    ) -> Dict[str, Any]: ...
    
    def get_agent_run(self, agent_run_id: Union[str, int], org_id: Optional[str] = None) -> Dict[str, Any]: ...
    
    def resume_agent_run(
        self, 
        agent_run_id: Union[str, int], 
        prompt: str,
        org_id: Optional[str] = None,
        task: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]: ...
    
    def list_agent_runs(
        self, 
        org_id: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        repo: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]: ...
    
    def get_agent_run_logs(
        self, 
        agent_run_id: Union[str, int], 
        org_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]: ...
    
    def wait_for_completion(
        self, 
        agent_run_id: Union[str, int], 
        org_id: Optional[str] = None,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]: ...
    
    def check_orchestrator_status(self, orchestrator_id: str, org_id: Optional[str] = None) -> bool: ...

