"""
Task class for managing agent runs
"""

from typing import Optional, List, TYPE_CHECKING

from ..models import AgentRunResponse, AgentRunLogResponse, GithubPullRequestResponse

if TYPE_CHECKING:
    from ..client import CodegenClient


class Task:
    """
    Represents an agent run task with status monitoring and result retrieval.
    
    Usage:
        task = agent.run("Create a function")
        print(task.status)
        task.refresh()
        if task.status == "completed":
            print(task.result)
    """
    
    def __init__(
        self, 
        client: 'CodegenClient', 
        org_id: int, 
        task_id: int, 
        initial_data: Optional[AgentRunResponse] = None
    ):
        self._client = client
        self._org_id = org_id
        self._task_id = task_id
        self._data = initial_data
    
    @property
    def id(self) -> int:
        """Task ID"""
        return self._task_id
    
    @property
    def status(self) -> Optional[str]:
        """Current task status"""
        if self._data:
            return self._data.status
        return None
    
    @property
    def result(self) -> Optional[str]:
        """Task result (available when completed)"""
        if self._data:
            return self._data.result
        return None
    
    @property
    def web_url(self) -> Optional[str]:
        """Web URL to view the task in the Codegen dashboard"""
        if self._data:
            return self._data.web_url
        return None
    
    @property
    def created_at(self) -> Optional[str]:
        """Task creation timestamp"""
        if self._data:
            return self._data.created_at
        return None
    
    @property
    def github_pull_requests(self) -> Optional[List[GithubPullRequestResponse]]:
        """GitHub pull requests created by this task"""
        if self._data:
            return self._data.github_pull_requests
        return None
    
    def refresh(self):
        """Refresh task status and data from the API"""
        self._data = self._client.get_agent_run(self._org_id, self._task_id)
    
    def get_logs(self, limit: int = 100) -> List[AgentRunLogResponse]:
        """
        Get task execution logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        logs_response = self._client.get_agent_run_logs(
            self._org_id, self._task_id, limit=limit
        )
        return logs_response.logs
    
    def wait_for_completion(self, poll_interval: float = 5.0, timeout: Optional[float] = None):
        """
        Wait for the task to complete.
        
        Args:
            poll_interval: How often to check status (seconds)
            timeout: Maximum time to wait (seconds)
        """
        self._data = self._client.wait_for_completion(
            self._org_id, self._task_id, poll_interval, timeout
        )
    
    def resume(self, prompt: str, images: Optional[List[str]] = None):
        """
        Resume a paused task with additional input.
        
        Args:
            prompt: Additional prompt to continue the task
            images: Optional images to include
        """
        self._data = self._client.resume_agent_run(
            self._org_id, self._task_id, prompt, images
        )
    
    def __str__(self) -> str:
        return f"Task(id={self.id}, status={self.status})"
    
    def __repr__(self) -> str:
        return f"Task(id={self.id}, status={self.status}, org_id={self._org_id})"

