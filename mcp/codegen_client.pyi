"""
Type stub file for codegen_client.py
"""

from typing import Dict, Any, Optional, Union

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
    
    def get_organizations(self) -> Dict[str, Any]: ...
    
    def list_agent_runs(
        self, 
        status: Optional[str] = None,
        limit: int = 100,
        page: int = 1,
        repo: Optional[str] = None
    ) -> Dict[str, Any]: ...
    
    def create_agent_run(
        self, 
        prompt: str,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        pr: Optional[int] = None,
        task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        orchestrator_id: Optional[str] = None
    ) -> Dict[str, Any]: ...
    
    def get_agent_run(self, agent_run_id: Union[str, int]) -> Dict[str, Any]: ...
    
    def resume_agent_run(
        self, 
        agent_run_id: Union[str, int],
        prompt: str,
        task: Optional[str] = None
    ) -> Dict[str, Any]: ...
    
    def wait_for_completion(
        self, 
        agent_run_id: Union[str, int],
        timeout: Optional[float] = None,
        poll_interval: float = 1.0
    ) -> Dict[str, Any]: ...
    
    def check_orchestrator_status(self, orchestrator_id: str) -> bool: ...

