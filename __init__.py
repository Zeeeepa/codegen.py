"""
Codegen SDK - Python Client for Codegen API

A comprehensive Python SDK for interacting with the Codegen API, providing
both simple and advanced interfaces for agent run management, real-time monitoring,
and comprehensive logging.

Quick Start:
    Simple Agent Interface:
        from backend.api import Agent
        
        agent = Agent(org_id=323, token="your-token")
        task = agent.run("Create a Python function to calculate fibonacci numbers")
        print(task.result)
    
    Advanced Client Interface:
        from backend.api import CodegenClient, ClientConfig
        
        config = ClientConfig(api_token="your-token", org_id="323")
        with CodegenClient(config) as client:
            run = client.create_agent_run(323, "Your prompt here")
            # Real-time monitoring and advanced features available

Modules:
    backend.api: Core SDK implementation
    tests: Comprehensive test suite
    examples: Usage examples and demonstrations
"""

__version__ = "2.0.0"
__author__ = "Codegen SDK Team"
__email__ = "support@codegen.com"
__url__ = "https://github.com/Zeeeepa/codegen.py"

# Re-export main classes for convenience
try:
    from backend.api import (
        Agent,
        CodegenClient,
        ClientConfig,
        ConfigPresets,
        Task,
    )
    
    __all__ = [
        "Agent",
        "CodegenClient", 
        "ClientConfig",
        "ConfigPresets",
        "Task",
    ]
    
except ImportError:
    # Handle case where backend module isn't available
    __all__ = []

