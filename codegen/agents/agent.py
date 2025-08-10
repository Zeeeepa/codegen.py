"""
Official Agent class matching documented SDK patterns
"""

from typing import Optional, List, Dict, Any

from ..client import CodegenClient
from ..config import ClientConfig
from .task import Task


class Agent:
    """
    Official Codegen Agent interface matching documented patterns.
    
    Usage:
        from codegen.agents.agent import Agent
        
        agent = Agent(org_id="323", token="your-token")
        task = agent.run("Create a Python function")
        print(task.status)
        task.refresh()
        if task.status == "completed":
            print(task.result)
    """
    
    def __init__(
        self, 
        org_id: str, 
        token: str, 
        base_url: str = "https://api.codegen.com/v1"
    ):
        """
        Initialize Agent with organization ID and API token.
        
        Args:
            org_id: Your organization ID
            token: Your API token
            base_url: API base URL (optional)
        """
        self.org_id = int(org_id)
        self.token = token
        self.base_url = base_url
        
        # Create internal client with configuration
        config = ClientConfig(
            api_token=token,
            org_id=org_id,
            base_url=base_url
        )
        self._client = CodegenClient(config)
    
    def run(
        self, 
        prompt: str, 
        images: Optional[List[str]] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Task':
        """
        Run an agent with a prompt and return a Task object.
        
        Args:
            prompt: The prompt to send to the agent
            images: Optional list of base64 encoded images
            metadata: Optional metadata dictionary
            
        Returns:
            Task object for monitoring and retrieving results
        """
        agent_run = self._client.create_agent_run(
            org_id=self.org_id,
            prompt=prompt,
            images=images,
            metadata=metadata,
        )
        return Task(self._client, self.org_id, agent_run.id, agent_run)
    
    def get_task(self, task_id: int) -> 'Task':
        """
        Get an existing task by ID.
        
        Args:
            task_id: The task ID to retrieve
            
        Returns:
            Task object
        """
        agent_run = self._client.get_agent_run(self.org_id, task_id)
        return Task(self._client, self.org_id, task_id, agent_run)
    
    def list_tasks(self, limit: int = 10) -> List['Task']:
        """
        List recent tasks.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of Task objects
        """
        runs = self._client.list_agent_runs(self.org_id, limit=limit)
        return [Task(self._client, self.org_id, run.id, run) for run in runs.items]
    
    def close(self):
        """Close the underlying client"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

