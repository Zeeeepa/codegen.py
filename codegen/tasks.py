"""
Task management and monitoring
Handles agent task lifecycle and status tracking
"""

import time
from typing import Optional, List, TYPE_CHECKING
from .core import AgentRunResponse, AgentRunStatus, AgentRunWithLogsResponse, GithubPullRequestResponse

if TYPE_CHECKING:
    from .core import CodegenClient

class TaskStatus:
    """Task status constants"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """Represents an agent run task with convenient methods"""
    
    def __init__(self, client: 'CodegenClient', task_id: int, initial_data: Optional[AgentRunResponse] = None):
        self.client = client
        self.id = task_id
        self._data = initial_data
    
    @property
    def status(self) -> Optional[str]:
        """Get the current status of the task"""
        if not self._data or self._data.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            self.refresh()
        return self._data.status if self._data else None
    
    @property
    def result(self) -> Optional[str]:
        """Get the result of the task"""
        if not self._data:
            self.refresh()
        return self._data.result if self._data else None
    
    @property
    def error(self) -> Optional[str]:
        """Get any error message from the task"""
        if not self._data:
            self.refresh()
        return self._data.error if self._data else None
    
    @property
    def created_at(self) -> Optional[str]:
        """Get the task creation timestamp"""
        if not self._data:
            self.refresh()
        return self._data.created_at if self._data else None
    
    @property
    def updated_at(self) -> Optional[str]:
        """Get the task last update timestamp"""
        if not self._data:
            self.refresh()
        return self._data.updated_at if self._data else None
    
    @property
    def github_pull_request(self) -> Optional[GithubPullRequestResponse]:
        """Get any GitHub pull request created by this task"""
        if not self._data:
            self.refresh()
        return self._data.github_pull_request if self._data else None
    
    @property
    def is_completed(self) -> bool:
        """Check if the task is completed (successfully or with error)"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def is_running(self) -> bool:
        """Check if the task is currently running"""
        return self.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
    
    def refresh(self):
        """Refresh the task data from the API"""
        self._data = self.client.get_agent_run(self.id)
    
    def get_logs(self, skip: int = 0, limit: int = 100) -> AgentRunWithLogsResponse:
        """Get logs for this task"""
        return self.client.get_agent_run_logs(self.id, skip=skip, limit=limit)
    
    def wait_for_completion(self, timeout: Optional[float] = None, poll_interval: float = 5.0) -> AgentRunResponse:
        """
        Wait for the task to complete
        
        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)
            poll_interval: Time between status checks in seconds
            
        Returns:
            The final AgentRunResponse when completed
            
        Raises:
            TimeoutError: If timeout is reached before completion
        """
        start_time = time.time()
        
        while not self.is_completed:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self.id} did not complete within {timeout} seconds")
            
            time.sleep(poll_interval)
            self.refresh()
        
        return self._data
    
    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task(id={self.id}, status={self.status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the task"""
        return f"Task(id={self.id}, status={self.status}, created_at={self.created_at})"

