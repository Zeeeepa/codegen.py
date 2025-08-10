"""
Codegen SDK - Official Python Client for Codegen API

A comprehensive Python SDK for interacting with the Codegen API, providing
both simple and advanced interfaces for agent run management, real-time monitoring,
and comprehensive logging.

Official Usage:
    from codegen.agents.agent import Agent
    
    agent = Agent(org_id="323", token="your-token")
    task = agent.run("Create a Python function to calculate fibonacci numbers")
    print(task.result)

Advanced Usage:
    from codegen.client import CodegenClient
    from codegen.config import ClientConfig
    
    config = ClientConfig(api_token="your-token", org_id="323")
    with CodegenClient(config) as client:
        run = client.create_agent_run(323, "Your prompt here")
"""

__version__ = "2.0.0"
__author__ = "Codegen SDK Team"
__email__ = "support@codegen.com"
__url__ = "https://github.com/Zeeeepa/codegen.py"

# Main exports for convenience
from codegen.agents.agent import Agent
from codegen.client import CodegenClient
from codegen.config import ClientConfig, ConfigPresets

__all__ = [
    "Agent",
    "CodegenClient", 
    "ClientConfig",
    "ConfigPresets",
]

