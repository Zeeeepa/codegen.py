"""
Mock Codegen API for testing purposes.
"""

import time
import enum
import logging
from typing import Dict, Any, Optional, List

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentRunStatus(enum.Enum):
    """Agent run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ClientConfig:
    """Client configuration."""
    
    def __init__(self, api_token: str, base_url: str = "https://api.codegen.com"):
        """Initialize client configuration."""
        self.api_token = api_token
        self.base_url = base_url

class CodegenClient:
    """Codegen API client."""
    
    def __init__(self, config: ClientConfig):
        """Initialize client."""
        self.config = config
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }

class Task:
    """Agent task."""
    
    def __init__(self, id: int, agent: 'Agent', status: str = "pending", result: Optional[str] = None, web_url: Optional[str] = None):
        """Initialize task."""
        self.id = id
        self.agent = agent
        self.status = status
        self.result = result
        self.web_url = web_url
    
    def refresh(self) -> 'Task':
        """Refresh task status."""
        # Simulate API call
        logger.info(f"Refreshing task {self.id}")
        return self
    
    def wait_for_completion(self, timeout: int = 3600) -> 'Task':
        """Wait for task completion."""
        # Simulate waiting
        logger.info(f"Waiting for task {self.id} completion (timeout: {timeout}s)")
        time.sleep(1)
        self.status = AgentRunStatus.COMPLETED.value
        self.result = f"Mock result for task {self.id}"
        return self
    
    def resume(self, prompt: str) -> 'Task':
        """Resume task."""
        # Simulate API call
        logger.info(f"Resuming task {self.id} with prompt: {prompt}")
        return self

class Agent:
    """Codegen agent."""
    
    def __init__(self, org_id: str, token: str, base_url: str = "https://api.codegen.com"):
        """Initialize agent."""
        self.org_id = org_id
        self.token = token
        self.base_url = base_url
        self.client = CodegenClient(ClientConfig(token, base_url))
        self.next_task_id = 1000
    
    def run(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Task:
        """Run agent."""
        # Simulate API call
        logger.info(f"Running agent with prompt: {prompt}")
        task_id = self.next_task_id
        self.next_task_id += 1
        return Task(
            id=task_id,
            agent=self,
            status=AgentRunStatus.RUNNING.value,
            web_url=f"https://app.codegen.com/agent/trace/{task_id}"
        )
    
    def get_task(self, task_id: int) -> Task:
        """Get task by ID."""
        # Simulate API call
        logger.info(f"Getting task {task_id}")
        return Task(
            id=task_id,
            agent=self,
            status=AgentRunStatus.RUNNING.value,
            web_url=f"https://app.codegen.com/agent/trace/{task_id}"
        )

