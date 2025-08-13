#!/usr/bin/env python3
"""
MCP Server for Codegen API

This module provides MCP tools for interacting with the Codegen API.
It can be used directly by MCP clients without starting an HTTP server.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List, Callable

from codegen_client import CodegenClient, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("codegen_mcp")

# Global client instance
client = None


def get_client() -> CodegenClient:
    """Get the CodegenClient instance, creating it if necessary."""
    global client
    if client is None:
        client = CodegenClient()
    return client


def codegenapi_get_users(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get all users."""
    client = get_client()
    return client.get_users()


def codegenapi_get_user(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get a specific user."""
    client = get_client()
    user_id = parameters.get("user_id")
    if not user_id:
        raise ValidationError("user_id is required")
    return client.get_user(user_id)


def codegenapi_get_current_user(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get the current user."""
    client = get_client()
    return client.get_current_user()


def codegenapi_get_organizations(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get all organizations."""
    client = get_client()
    return client.get_organizations()


def codegenapi_new(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new agent run."""
    client = get_client()
    
    # Required parameters
    repo = parameters.get("repo")
    query = parameters.get("query")
    
    if not repo:
        raise ValidationError("repo is required")
    if not query:
        raise ValidationError("query is required")
    
    # Optional parameters
    branch = parameters.get("branch")
    pr = parameters.get("pr")
    task = parameters.get("task")
    metadata = parameters.get("metadata", {})
    
    return client.create_agent_run(
        prompt=query,
        repo=repo,
        branch=branch,
        pr=pr,
        task=task,
        metadata=metadata
    )


def codegenapi_resume(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Resume an agent run."""
    client = get_client()
    
    # Required parameters
    agent_run_id = parameters.get("agent_run_id")
    query = parameters.get("query")
    
    if not agent_run_id:
        raise ValidationError("agent_run_id is required")
    if not query:
        raise ValidationError("query is required")
    
    # Optional parameters
    task = parameters.get("task")
    
    # Get the agent run to check if it's in COMPLETE state
    agent_run = client.get_agent_run(agent_run_id)
    if agent_run.get("status") != "COMPLETE":
        raise ValidationError(f"Agent run {agent_run_id} is not in COMPLETE state, current state: {agent_run.get('status')}")
    
    return client.resume_agent_run(
        agent_run_id=agent_run_id,
        prompt=query,
        task=task
    )


def codegenapi_get_agent_run(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get an agent run."""
    client = get_client()
    
    # Required parameters
    agent_run_id = parameters.get("agent_run_id")
    
    if not agent_run_id:
        raise ValidationError("agent_run_id is required")
    
    return client.get_agent_run(agent_run_id)


def codegenapi_list(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """List agent runs."""
    client = get_client()
    
    # Optional parameters
    status = parameters.get("status")
    repo = parameters.get("repo")
    limit = parameters.get("limit", 10)
    
    return client.list_agent_runs(
        status=status,
        repo=repo,
        limit=limit
    )


def codegenapi_get_agent_run_logs(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get agent run logs."""
    client = get_client()
    
    # Required parameters
    agent_run_id = parameters.get("agent_run_id")
    
    if not agent_run_id:
        raise ValidationError("agent_run_id is required")
    
    # Optional parameters
    skip = parameters.get("skip", 0)
    limit = parameters.get("limit", 10)
    
    return client.get_agent_run_logs(
        agent_run_id=agent_run_id,
        skip=skip,
        limit=limit
    )


def codegenapi_config(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Manage configuration."""
    # Required parameters
    action = parameters.get("action")
    
    if not action:
        raise ValidationError("action is required")
    
    if action not in ["list", "get", "set"]:
        raise ValidationError(f"Invalid action: {action}")
    
    # Get the config file path
    config_dir = os.path.expanduser("~/.config/codegen")
    config_file = os.path.join(config_dir, "config.json")
    
    if action == "list":
        if not os.path.exists(config_file):
            return {"config": {}}
        
        with open(config_file, "r") as f:
            config = json.load(f)
        
        return {"config": config}
    
    elif action == "get":
        key = parameters.get("key")
        
        if not key:
            raise ValidationError("key is required for get action")
        
        if not os.path.exists(config_file):
            return {"value": None}
        
        with open(config_file, "r") as f:
            config = json.load(f)
        
        return {"value": config.get(key)}
    
    elif action == "set":
        key = parameters.get("key")
        value = parameters.get("value")
        
        if not key:
            raise ValidationError("key is required for set action")
        if value is None:
            raise ValidationError("value is required for set action")
        
        # Create the config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Load the config
        config = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
        
        # Set the value
        config[key] = value
        
        # Save the config
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return {"key": key, "value": value}


# Define the MCP tools
MCP_TOOLS = {
    "codegenapi_get_users": {
        "function": codegenapi_get_users,
        "description": "Get all users",
        "parameters": {},
    },
    "codegenapi_get_user": {
        "function": codegenapi_get_user,
        "description": "Get a specific user",
        "parameters": {
            "user_id": {
                "type": "string",
                "description": "The ID of the user to get",
            },
        },
    },
    "codegenapi_get_current_user": {
        "function": codegenapi_get_current_user,
        "description": "Get the current user",
        "parameters": {},
    },
    "codegenapi_get_organizations": {
        "function": codegenapi_get_organizations,
        "description": "Get all organizations",
        "parameters": {},
    },
    "codegenapi_new": {
        "function": codegenapi_new,
        "description": "Create a new agent run",
        "parameters": {
            "repo": {
                "type": "string",
                "description": "Repository name (e.g., 'user/repo')",
            },
            "branch": {
                "type": "string",
                "description": "Branch name",
                "optional": True,
            },
            "pr": {
                "type": "integer",
                "description": "PR number",
                "optional": True,
            },
            "task": {
                "type": "string",
                "description": "Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')",
                "optional": True,
            },
            "query": {
                "type": "string",
                "description": "The prompt to send to the agent",
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata for the agent run",
                "optional": True,
            },
        },
    },
    "codegenapi_get_agent_run": {
        "function": codegenapi_get_agent_run,
        "description": "Get an agent run",
        "parameters": {
            "agent_run_id": {
                "type": "string",
                "description": "Agent run ID to retrieve",
            },
        },
    },
    "codegenapi_resume": {
        "function": codegenapi_resume,
        "description": "Resume a paused agent run",
        "parameters": {
            "agent_run_id": {
                "type": "string",
                "description": "Agent run ID to resume",
            },
            "task": {
                "type": "string",
                "description": "Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')",
                "optional": True,
            },
            "query": {
                "type": "string",
                "description": "The prompt to send to the agent",
            },
        },
    },
    "codegenapi_list": {
        "function": codegenapi_list,
        "description": "List agent runs",
        "parameters": {
            "status": {
                "type": "string",
                "description": "Filter by status (e.g., 'ACTIVE', 'COMPLETE', 'ERROR')",
                "optional": True,
            },
            "repo": {
                "type": "string",
                "description": "Filter by repository",
                "optional": True,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of runs to return",
                "optional": True,
                "default": 10,
            },
        },
    },
    "codegenapi_get_agent_run_logs": {
        "function": codegenapi_get_agent_run_logs,
        "description": "Get agent run logs",
        "parameters": {
            "agent_run_id": {
                "type": "string",
                "description": "Agent run ID to get logs for",
            },
            "skip": {
                "type": "integer",
                "description": "Number of logs to skip (for pagination)",
                "optional": True,
                "default": 0,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of logs to return",
                "optional": True,
                "default": 10,
            },
        },
    },
    "codegenapi_config": {
        "function": codegenapi_config,
        "description": "Manage configuration",
        "parameters": {
            "action": {
                "type": "string",
                "description": "Action to perform",
                "enum": ["list", "get", "set"],
            },
            "key": {
                "type": "string",
                "description": "Configuration key",
                "optional": True,
            },
            "value": {
                "type": "string",
                "description": "Configuration value",
                "optional": True,
            },
        },
    },
}


def get_manifest() -> Dict[str, Any]:
    """Get the MCP manifest."""
    tools = []
    
    for name, tool in MCP_TOOLS.items():
        parameters = {}
        for param_name, param_info in tool.get("parameters", {}).items():
            parameter = {
                "type": param_info.get("type", "string"),
                "description": param_info.get("description", ""),
            }
            
            if param_info.get("enum"):
                parameter["enum"] = param_info.get("enum")
            
            if param_info.get("default") is not None:
                parameter["default"] = param_info.get("default")
            
            parameters[param_name] = parameter
        
        tools.append({
            "name": name,
            "description": tool.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": [
                    param_name
                    for param_name, param_info in tool.get("parameters", {}).items()
                    if not param_info.get("optional", False)
                ],
            },
        })
    
    return {
        "schema_version": "v1",
        "name_for_human": "Codegen API",
        "name_for_model": "codegenapi",
        "description_for_human": "Tools for interacting with the Codegen API",
        "description_for_model": "These tools allow you to interact with the Codegen API to create and manage agent runs.",
        "tools": tools,
    }


def invoke_tool(name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke an MCP tool."""
    if name not in MCP_TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    
    tool = MCP_TOOLS[name]
    function = tool["function"]
    
    try:
        result = function(parameters)
        return result
    except ValidationError as e:
        raise ValueError(str(e))
    except Exception as e:
        logger.exception(f"Error invoking tool {name}: {e}")
        raise ValueError(f"Error invoking tool {name}: {e}")


# MCP integration
try:
    import mcp
    
    # Register the MCP tools
    @mcp.expose
    def manifest():
        """Return the MCP manifest."""
        return get_manifest()
    
    @mcp.expose
    def invoke(name, parameters=None):
        """Invoke an MCP tool."""
        if parameters is None:
            parameters = {}
        
        return invoke_tool(name, parameters)
    
    # Log the available tools
    logger.info("Registered MCP tools:")
    for name in MCP_TOOLS:
        logger.info(f"  - {name}")
    
except ImportError:
    logger.warning("MCP library not found, running in standalone mode")
    
    # If this script is run directly, print the manifest
    if __name__ == "__main__":
        print("=" * 80)
        print("Codegen MCP Server")
        print("=" * 80)
        print("Available tools:")
        for name in MCP_TOOLS:
            print(f"  - {name}")
        print("=" * 80)
        print("MCP manifest:")
        print(json.dumps(get_manifest(), indent=2))
        print("=" * 80)

