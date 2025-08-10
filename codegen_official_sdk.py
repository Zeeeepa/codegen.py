"""
Official Codegen SDK Implementation
Aligned with official documentation patterns
"""

import os
import requests
from typing import Any, Dict, Optional
from datetime import datetime

# Official base URL from documentation
CODEGEN_BASE_API_URL = "https://codegen-sh-rest-api.modal.run"

class AgentTask:
    """Represents a running or completed agent task."""
    
    def __init__(self, task_data: Dict[str, Any], agent_instance: 'Agent'):
        """Initialize an AgentTask.
        
        Args:
            task_data: Raw task data from API response
            agent_instance: Reference to the Agent that created this task
        """
        self.id = task_data.get('id')
        self.org_id = task_data.get('org_id') or task_data.get('organization_id')
        self.status = task_data.get('status')
        self.result = task_data.get('result')
        self.web_url = task_data.get('web_url')
        self.created_at = task_data.get('created_at')
        self.prompt = task_data.get('prompt')
        self._agent = agent_instance
        self._raw_data = task_data
    
    def refresh(self) -> None:
        """Refreshes the task status from the API."""
        if not self.id:
            return
        
        try:
            url = f"{self._agent.base_url}/organizations/{self.org_id}/agent/run/{self.id}"
            headers = {
                "Authorization": f"Bearer {self._agent.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            updated_data = response.json()
            
            # Update attributes from refreshed data
            self.status = updated_data.get('status', self.status)
            self.result = updated_data.get('result', self.result)
            self.web_url = updated_data.get('web_url', self.web_url)
            self._raw_data = updated_data
            
        except Exception as e:
            print(f"Warning: Failed to refresh task status: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            'id': self.id,
            'org_id': self.org_id,
            'status': self.status,
            'result': self.result,
            'web_url': self.web_url,
            'created_at': self.created_at,
            'prompt': self.prompt
        }


class Agent:
    """The Agent class is the main entry point for interacting with Codegen AI agents."""
    
    def __init__(
        self, 
        token: str, 
        org_id: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        """Initialize the Agent with your organization ID and API token.
        
        Args:
            token (required): Your API authentication token
            org_id (optional): Your organization ID. If not provided, defaults to 
                              environment variable CODEGEN_ORG_ID or "1"
            base_url (optional): API base URL. Defaults to official Codegen API URL
        """
        self.token = token
        self.org_id = org_id or os.environ.get("CODEGEN_ORG_ID", "1")
        self.base_url = base_url or CODEGEN_BASE_API_URL
        
        # Remove trailing slash if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        self.current_task: Optional[AgentTask] = None
        
        # Validate required parameters
        if not self.token:
            raise ValueError("API token is required")
        if not self.org_id:
            raise ValueError("Organization ID is required")
    
    def run(self, prompt: str) -> AgentTask:
        """Runs an agent with the given prompt.
        
        Args:
            prompt (required): The instruction for the agent to execute
            
        Returns:
            An AgentTask object representing the running task
        """
        if not prompt:
            raise ValueError("Prompt is required")
        
        url = f"{self.base_url}/organizations/{self.org_id}/agent/run"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            task_data = response.json()
            task = AgentTask(task_data, self)
            self.current_task = task
            
            return task
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create agent run: {e}")
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Gets the status of the current task.
        
        Returns:
            A dictionary containing task status information (id, status, result), 
            or None if no task has been run
        """
        if self.current_task:
            self.current_task.refresh()
            return self.current_task.to_dict()
        return None


# Compatibility functions for existing code
def create_agent(token: str, org_id: Optional[str] = None, base_url: Optional[str] = None) -> Agent:
    """Create an Agent instance with the official SDK pattern.
    
    Args:
        token: API authentication token
        org_id: Organization ID (optional)
        base_url: API base URL (optional)
        
    Returns:
        Agent instance
    """
    return Agent(token=token, org_id=org_id, base_url=base_url)


# Example usage function
def example_usage():
    """Example usage following official documentation patterns."""
    
    # Example from official docs
    agent = Agent(
        org_id="11",  # Your organization ID
        token="your_api_token_here",  # Your API authentication token
        base_url="https://codegen-sh-rest-api.modal.run",  # Optional - defaults to this URL
    )

    # Run an agent with a prompt
    task = agent.run(prompt="Which github repos can you currently access?")

    # Check the initial status
    print(task.status)  # Returns the current status of the task

    # Refresh the task to get updated status
    task.refresh()

    # Check the updated status
    print(task.status)

    # Once task is complete, you can access the result
    if task.status == "completed":
        print(task.result)


if __name__ == "__main__":
    # Test with environment variables if available
    token = os.environ.get("CODEGEN_API_TOKEN")
    org_id = os.environ.get("CODEGEN_ORG_ID")
    
    if token and org_id:
        print("🚀 Testing Official SDK Implementation")
        print("=" * 50)
        
        try:
            # Test with official base URL
            agent = Agent(
                token=token,
                org_id=org_id,
                base_url=CODEGEN_BASE_API_URL
            )
            
            print(f"✅ Agent created:")
            print(f"   Org ID: {agent.org_id}")
            print(f"   Base URL: {agent.base_url}")
            
            # Test creating a task
            task = agent.run(prompt="Test: Create a simple hello world function")
            print(f"✅ Task created: ID {task.id}, Status: {task.status}")
            
            # Test status check
            status = agent.get_status()
            if status:
                print(f"✅ Status check: {status['status']}")
            
            print("✅ Official SDK implementation test passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
            # Try with alternative base URL
            print("\n🔄 Trying with alternative base URL...")
            try:
                agent = Agent(
                    token=token,
                    org_id=org_id,
                    base_url="https://api.codegen.com/v1"
                )
                
                task = agent.run(prompt="Test: Create a simple hello world function")
                print(f"✅ Task created with alternative URL: ID {task.id}")
                
            except Exception as e2:
                print(f"❌ Alternative URL also failed: {e2}")
    else:
        print("⚠️  Set CODEGEN_API_TOKEN and CODEGEN_ORG_ID environment variables to test")
        print("Example usage:")
        example_usage()
