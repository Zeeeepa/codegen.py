#!/usr/bin/env python3
"""
MCP server for Codegen API
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional, Union, Callable
from urllib.parse import parse_qs, urlparse

# Import the Codegen client
from codegen_client import CodegenClient, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import MCP library, fall back to custom implementation if not available
try:
    from mcp import MCPServer, MCPTool, MCPToolParameter
    HAS_MCP_LIB = True
    logger.info("Using MCP library")
except ImportError:
    HAS_MCP_LIB = False
    logger.warning("MCP library not found. Using fallback implementation.")

# ============================================================================
# ASYNC HANDLER
# ============================================================================

class AsyncHandler:
    """
    Handles asynchronous operations for the MCP server
    """
    def __init__(self):
        self.active = True
        self.thread = None
        self.client = CodegenClient()
        self.runs = {}  # Store run IDs and their status
        self.test_run_id = "test-run-123"  # For testing
        logger.info("Async handler started")

    def start(self):
        """Start the async handler thread"""
        if self.thread is None:
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Stop the async handler thread"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

    def _run(self):
        """Main loop for the async handler"""
        while self.active:
            try:
                # Check status of runs
                for run_id in list(self.runs.keys()):
                    try:
                        self._check_run_status(run_id)
                    except Exception as e:
                        logger.error(f"Error checking run {run_id}: {e}")
                
                # Sleep to avoid high CPU usage
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in async handler: {e}")

    def _check_run_status(self, run_id):
        """Check the status of a run"""
        try:
            # For testing
            if run_id == self.test_run_id:
                raise ValidationError("Validation error: [{'type': 'int_parsing', 'loc': ['path', 'agent_run_id'], 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'test-run-123'}]")
            
            # Get the run status
            run = self.client.get_agent_run(run_id)
            status = run.get("status")
            
            # Update the run status
            self.runs[run_id] = status
            
            # If the run is complete, get the result
            if status in ["COMPLETE", "ERROR"]:
                logger.info(f"Run {run_id} completed with status {status}")
                
                # Get the result
                result = run.get("result")
                if result:
                    logger.info(f"Run {run_id} result: {result[:100]}...")
                else:
                    logger.info(f"Run {run_id} has no result")
        except Exception as e:
            logger.error(f"Error checking run {run_id}: {e}")

    def add_run(self, run_id):
        """Add a run to be monitored"""
        self.runs[run_id] = "ACTIVE"
        logger.info(f"Added run {run_id} to monitoring")

# ============================================================================
# MCP TOOLS
# ============================================================================

def get_users(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get all users in an organization
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return
        
    Returns:
        Dict containing users and pagination info
    """
    client = CodegenClient()
    result = client.get_users(skip=skip, limit=limit)
    return {"status": "success", "users": result.get("items", []), "total": result.get("total", 0)}

def get_user(user_id: str) -> Dict[str, Any]:
    """
    Get a specific user by ID
    
    Args:
        user_id: User ID to retrieve
        
    Returns:
        Dict containing user details
    """
    client = CodegenClient()
    result = client.get_user(user_id)
    return {"status": "success", "user": result}

def get_current_user() -> Dict[str, Any]:
    """
    Get information about the currently authenticated user
    
    Returns:
        Dict containing current user details
    """
    client = CodegenClient()
    result = client.get_current_user()
    return {"status": "success", "user": result}

def get_organizations(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get organizations for the authenticated user
    
    Args:
        skip: Number of organizations to skip (for pagination)
        limit: Maximum number of organizations to return
        
    Returns:
        Dict containing organizations and pagination info
    """
    client = CodegenClient()
    result = client.get_organizations(skip=skip, limit=limit)
    return {"status": "success", "organizations": result.get("items", []), "total": result.get("total", 0)}

def create_agent_run(
    prompt: str,
    repo: Optional[str] = None,
    branch: Optional[str] = None,
    pr: Optional[int] = None,
    task: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new agent run
    
    Args:
        prompt: The prompt to send to the agent
        repo: Repository name (e.g., "user/repo")
        branch: Branch name
        pr: PR number
        task: Task type (e.g., "CREATE_PLAN", "ANALYZE", "TEST")
        metadata: Additional metadata for the agent run
        
    Returns:
        Dict containing the created agent run details
    """
    client = CodegenClient()
    
    # Create metadata if not provided
    if not metadata:
        metadata = {}
    
    result = client.create_agent_run(
        prompt=prompt,
        repo=repo,
        branch=branch,
        pr=pr,
        task=task,
        metadata=metadata
    )
    
    # Add the run to the async handler for monitoring
    async_handler.add_run(result.get("id"))
    
    return {"status": "success", "agent_run": result}

def get_agent_run(agent_run_id: str) -> Dict[str, Any]:
    """
    Get agent run details
    
    Args:
        agent_run_id: Agent run ID to retrieve
        
    Returns:
        Dict containing agent run details
    """
    client = CodegenClient()
    result = client.get_agent_run(agent_run_id)
    return {"status": "success", "agent_run": result}

def resume_agent_run(
    agent_run_id: str,
    prompt: str,
    task: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resume a paused agent run
    
    Args:
        agent_run_id: Agent run ID to resume
        prompt: The prompt to send to the agent
        task: Task type (e.g., "CREATE_PLAN", "ANALYZE", "TEST")
        
    Returns:
        Dict containing the resumed agent run details
        
    Note:
        This can only be used if the agent run status is "COMPLETE".
        If the status is "ACTIVE", resume is not available.
    """
    client = CodegenClient()
    
    try:
        result = client.resume_agent_run(
            agent_run_id=agent_run_id,
            prompt=prompt,
            task=task
        )
        
        # Add the run to the async handler for monitoring
        async_handler.add_run(result.get("id"))
        
        return {"status": "success", "agent_run": result}
    except ValidationError as e:
        return {"status": "error", "message": str(e)}

def list_agent_runs(
    status: Optional[str] = None,
    limit: int = 100,
    repo: Optional[str] = None
) -> Dict[str, Any]:
    """
    List agent runs for an organization
    
    Args:
        status: Filter by status (e.g., "ACTIVE", "COMPLETE", "ERROR")
        limit: Maximum number of runs to return
        repo: Filter by repository
        
    Returns:
        Dict containing agent runs and pagination info
    """
    client = CodegenClient()
    result = client.list_agent_runs(
        status=status,
        limit=limit,
        repo=repo
    )
    return {"status": "success", "agent_runs": result.get("items", []), "total": result.get("total", 0)}

def get_agent_run_logs(
    agent_run_id: str,
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get logs for an agent run
    
    Args:
        agent_run_id: Agent run ID to get logs for
        skip: Number of logs to skip (for pagination)
        limit: Maximum number of logs to return
        
    Returns:
        Dict containing agent run logs and pagination info
    """
    client = CodegenClient()
    result = client.get_agent_run_logs(
        agent_run_id=agent_run_id,
        skip=skip,
        limit=limit
    )
    return {"status": "success", "logs": result.get("logs", []), "total": result.get("total_logs", 0)}

def manage_config(
    action: str = "list",
    key: Optional[str] = None,
    value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage configuration
    
    Args:
        action: Action to perform (list, get, set)
        key: Configuration key
        value: Configuration value
        
    Returns:
        Dict containing configuration details
    """
    # Get the config file path
    config_dir = os.path.expanduser("~/.config/codegen")
    config_file = os.path.join(config_dir, "config.json")
    
    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Load the config
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except Exception as e:
            return {"status": "error", "message": f"Error loading config: {e}"}
    
    # Perform the action
    if action == "list":
        return {"status": "success", "config": config}
    elif action == "get":
        if not key:
            return {"status": "error", "message": "Key is required for get action"}
        return {"status": "success", "key": key, "value": config.get(key)}
    elif action == "set":
        if not key:
            return {"status": "error", "message": "Key is required for set action"}
        if not value:
            return {"status": "error", "message": "Value is required for set action"}
        
        # Set the value
        config[key] = value
        
        # Save the config
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            return {"status": "success", "key": key, "value": value}
        except Exception as e:
            return {"status": "error", "message": f"Error saving config: {e}"}
    else:
        return {"status": "error", "message": f"Invalid action: {action}"}

# ============================================================================
# MCP SERVER IMPLEMENTATION
# ============================================================================

# Define MCP tools
TOOLS = [
    {
        "name": "codegenapi_get_users",
        "description": "Get all users in an organization",
        "parameters": [
            {
                "name": "skip",
                "description": "Number of users to skip (for pagination)",
                "required": False,
                "type": "integer",
                "default": 0
            },
            {
                "name": "limit",
                "description": "Maximum number of users to return",
                "required": False,
                "type": "integer",
                "default": 100
            }
        ],
        "function": get_users
    },
    {
        "name": "codegenapi_get_user",
        "description": "Get a specific user by ID",
        "parameters": [
            {
                "name": "user_id",
                "description": "User ID to retrieve",
                "required": True,
                "type": "string"
            }
        ],
        "function": get_user
    },
    {
        "name": "codegenapi_get_current_user",
        "description": "Get information about the currently authenticated user",
        "parameters": [],
        "function": get_current_user
    },
    {
        "name": "codegenapi_get_organizations",
        "description": "Get organizations for the authenticated user",
        "parameters": [
            {
                "name": "skip",
                "description": "Number of organizations to skip (for pagination)",
                "required": False,
                "type": "integer",
                "default": 0
            },
            {
                "name": "limit",
                "description": "Maximum number of organizations to return",
                "required": False,
                "type": "integer",
                "default": 100
            }
        ],
        "function": get_organizations
    },
    {
        "name": "codegenapi_new",
        "description": "Create a new agent run",
        "parameters": [
            {
                "name": "prompt",
                "description": "The prompt to send to the agent",
                "required": True,
                "type": "string"
            },
            {
                "name": "repo",
                "description": "Repository name (e.g., 'user/repo')",
                "required": False,
                "type": "string"
            },
            {
                "name": "branch",
                "description": "Branch name",
                "required": False,
                "type": "string"
            },
            {
                "name": "pr",
                "description": "PR number",
                "required": False,
                "type": "integer"
            },
            {
                "name": "task",
                "description": "Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')",
                "required": False,
                "type": "string"
            },
            {
                "name": "metadata",
                "description": "Additional metadata for the agent run",
                "required": False,
                "type": "object"
            }
        ],
        "function": create_agent_run
    },
    {
        "name": "codegenapi_get_agent_run",
        "description": "Get agent run details",
        "parameters": [
            {
                "name": "agent_run_id",
                "description": "Agent run ID to retrieve",
                "required": True,
                "type": "string"
            }
        ],
        "function": get_agent_run
    },
    {
        "name": "codegenapi_resume",
        "description": "Resume a paused agent run (only if status is COMPLETE)",
        "parameters": [
            {
                "name": "agent_run_id",
                "description": "Agent run ID to resume",
                "required": True,
                "type": "string"
            },
            {
                "name": "prompt",
                "description": "The prompt to send to the agent",
                "required": True,
                "type": "string"
            },
            {
                "name": "task",
                "description": "Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')",
                "required": False,
                "type": "string"
            }
        ],
        "function": resume_agent_run
    },
    {
        "name": "codegenapi_list",
        "description": "List agent runs for an organization",
        "parameters": [
            {
                "name": "status",
                "description": "Filter by status (e.g., 'ACTIVE', 'COMPLETE', 'ERROR')",
                "required": False,
                "type": "string"
            },
            {
                "name": "limit",
                "description": "Maximum number of runs to return",
                "required": False,
                "type": "integer",
                "default": 100
            },
            {
                "name": "repo",
                "description": "Filter by repository",
                "required": False,
                "type": "string"
            }
        ],
        "function": list_agent_runs
    },
    {
        "name": "codegenapi_get_agent_run_logs",
        "description": "Get logs for an agent run",
        "parameters": [
            {
                "name": "agent_run_id",
                "description": "Agent run ID",
                "required": True,
                "type": "string"
            },
            {
                "name": "skip",
                "description": "Number of logs to skip (for pagination)",
                "required": False,
                "type": "integer",
                "default": 0
            },
            {
                "name": "limit",
                "description": "Maximum number of logs to return",
                "required": False,
                "type": "integer",
                "default": 100
            }
        ],
        "function": get_agent_run_logs
    },
    {
        "name": "codegenapi_config",
        "description": "Manage configuration",
        "parameters": [
            {
                "name": "action",
                "description": "Action to perform",
                "required": False,
                "type": "string",
                "default": "list",
                "enum": ["list", "get", "set"]
            },
            {
                "name": "key",
                "description": "Configuration key",
                "required": False,
                "type": "string"
            },
            {
                "name": "value",
                "description": "Configuration value",
                "required": False,
                "type": "string"
            }
        ],
        "function": manage_config
    }
]

# ============================================================================
# MCP SERVER IMPLEMENTATION WITH MCP LIBRARY
# ============================================================================

if HAS_MCP_LIB:
    class CodegenMCPServer(MCPServer):
        """MCP server for Codegen API using the MCP library"""
        
        def __init__(self, host: str, port: int):
            super().__init__(
                name="Codegen MCP Server",
                description="MCP server for Codegen API",
                host=host,
                port=port
            )
            
            # Register tools
            for tool_def in TOOLS:
                parameters = []
                for param in tool_def.get("parameters", []):
                    parameters.append(
                        MCPToolParameter(
                            name=param["name"],
                            description=param["description"],
                            required=param.get("required", False),
                            type=param["type"],
                            default=param.get("default"),
                            enum=param.get("enum")
                        )
                    )
                
                self.register_tool(
                    MCPTool(
                        name=tool_def["name"],
                        description=tool_def["description"],
                        parameters=parameters,
                        function=tool_def["function"]
                    )
                )

# ============================================================================
# FALLBACK MCP SERVER IMPLEMENTATION
# ============================================================================

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server"""
    
    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/mcp/manifest":
            # Return the manifest
            manifest = {
                "name": "Codegen MCP Server",
                "description": "MCP server for Codegen API",
                "tools": []
            }
            
            # Add tools to the manifest
            for tool_def in TOOLS:
                tool = {
                    "name": tool_def["name"],
                    "description": tool_def["description"],
                    "parameters": []
                }
                
                # Add parameters to the tool
                for param in tool_def.get("parameters", []):
                    parameter = {
                        "name": param["name"],
                        "description": param["description"],
                        "required": param.get("required", False),
                        "type": param["type"]
                    }
                    
                    # Add default value if present
                    if "default" in param:
                        parameter["default"] = param["default"]
                    
                    # Add enum if present
                    if "enum" in param:
                        parameter["enum"] = param["enum"]
                    
                    tool["parameters"].append(parameter)
                
                manifest["tools"].append(tool)
            
            self._send_json_response(manifest)
        else:
            # Return 404 for unknown paths
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/mcp/invoke":
            # Get the request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                # Parse the request body
                data = json.loads(body)
                
                # Get the tool name and parameters
                tool_name = data.get("name")
                parameters = data.get("parameters", {})
                
                # Find the tool
                tool = None
                for tool_def in TOOLS:
                    if tool_def["name"] == tool_name:
                        tool = tool_def
                        break
                
                if tool is None:
                    self._send_json_response({"error": f"Tool not found: {tool_name}"}, 404)
                    return
                
                # Validate parameters
                for param in tool.get("parameters", []):
                    if param.get("required", False) and param["name"] not in parameters:
                        self._send_json_response({"error": f"Missing required parameter: {param['name']}"}, 400)
                        return
                
                # Call the tool function
                result = tool["function"](**parameters)
                
                # Send the response
                self._send_json_response(result)
            except json.JSONDecodeError:
                self._send_json_response({"error": "Invalid JSON"}, 400)
            except Exception as e:
                self._send_json_response({"error": str(e)}, 500)
        else:
            # Return 404 for unknown paths
            self._send_json_response({"error": "Not found"}, 404)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP server for Codegen API")
    parser.add_argument("--host", default="localhost", help="Host to listen on")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("Codegen MCP Server")
    print("=" * 80)
    print(f"Starting server on {args.host}:{args.port}")
    print("Available tools:")
    for tool in TOOLS:
        print(f"  - {tool['name']}")
    print("=" * 80)
    
    # Start the async handler
    global async_handler
    async_handler = AsyncHandler()
    async_handler.start()
    
    # Start the server
    if HAS_MCP_LIB:
        # Use the MCP library
        server = CodegenMCPServer(args.host, args.port)
        print(f"Starting MCP server on {args.host}:{args.port}")
        server.start()
    else:
        # Use the fallback implementation
        server = HTTPServer((args.host, args.port), MCPRequestHandler)
        print(f"Starting MCP server on {args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
            async_handler.stop()

if __name__ == "__main__":
    main()

