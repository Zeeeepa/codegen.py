"""
Agent management and orchestration
High-level interface for working with Codegen agents
"""

from typing import Optional, List, Dict, Any
from .core import CodegenClient, ClientConfig, AgentRunResponse
from .tasks import Task

class Agent:
    """Simplified agent interface for easy usage"""
    
    def __init__(self, org_id: Optional[str] = None, token: Optional[str] = None, config: Optional[ClientConfig] = None):
        self.client = CodegenClient(org_id=org_id, token=token, config=config)
        self.org_id = self.client.org_id
    
    def run(self, prompt: str, **kwargs) -> Task:
        """Run an agent with a prompt and return a Task object"""
        agent_run = self.client.run_agent(prompt=prompt, **kwargs)
        return Task(self.client, agent_run.id, agent_run)
    
    def get_task(self, task_id: int) -> Task:
        """Get an existing task by ID"""
        agent_run = self.client.get_agent_run(task_id)
        return Task(self.client, task_id, agent_run)
    
    def list_tasks(self, limit: int = 10) -> List[Task]:
        """List recent tasks"""
        runs = self.client.list_agent_runs(limit=limit)
        return [Task(self.client, run.id, run) for run in runs.agent_runs]
    
    def get_stats(self):
        """Get client statistics"""
        return self.client.get_stats()
    
    def clear_cache(self):
        """Clear the client cache"""
        self.client.clear_cache()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

