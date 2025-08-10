"""
Codegen SDK - Python Client v2.0

A comprehensive Python SDK for interacting with the Codegen API, providing
both simple and advanced interfaces for agent run management, real-time monitoring,
and comprehensive logging.

🚀 Official SDK Usage (Recommended):
    from codegen.agents.agent import Agent
    
    agent = Agent(org_id="323", token="your-token")
    task = agent.run("Create a Python function")
    print(task.result)

🔄 Backward Compatibility (Still Supported):
    from backend.api import Agent, CodegenClient
    
    agent = Agent(org_id=323, token="your-token")
    task = agent.run("Create a function")

📦 Advanced Usage:
    from codegen.client import CodegenClient
    from codegen.config import ClientConfig, ConfigPresets
    
    config = ConfigPresets.production()
    config.api_token = "your-token"
    config.org_id = "323"
    
    with CodegenClient(config) as client:
        run = client.create_agent_run(323, "Your prompt")
        logs = client.get_agent_run_logs(323, run.id)
"""

__version__ = "2.0.0"
__author__ = "Codegen SDK Team"
__email__ = "support@codegen.com"
__url__ = "https://github.com/Zeeeepa/codegen.py"

# Official SDK exports (recommended)
try:
    from codegen.agents.agent import Agent
    from codegen.client import CodegenClient
    from codegen.config import ClientConfig, ConfigPresets
    OFFICIAL_SDK_AVAILABLE = True
except ImportError:
    OFFICIAL_SDK_AVAILABLE = False

# Backward compatibility exports
try:
    from backend.api import Agent as BackendAgent, CodegenClient as BackendClient
    BACKEND_API_AVAILABLE = True
except ImportError:
    BACKEND_API_AVAILABLE = False

# Export the available implementations
if OFFICIAL_SDK_AVAILABLE:
    # Prefer official SDK
    __all__ = ["Agent", "CodegenClient", "ClientConfig", "ConfigPresets"]
elif BACKEND_API_AVAILABLE:
    # Fall back to backend API
    from backend.api import Agent, CodegenClient, ClientConfig
    __all__ = ["Agent", "CodegenClient", "ClientConfig"]
else:
    # No implementation available
    __all__ = []
