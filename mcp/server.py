#!/usr/bin/env python3
"""
Codegen MCP Server

A Model Context Protocol (MCP) server for Codegen API integration.
Provides tools for creating and managing agent runs with orchestrator tracking.

Usage:
    uv --directory <Project'sRootDir>/mcp run server.py
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

# Create log directory if it doesn't exist
log_dir = Path.home() / ".codegen"
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / "mcp_server.log")
    ]
)
logger = logging.getLogger(__name__)

# Import MCP server components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codegen_client import CodegenClient, CodegenAPIError
from config import Config
from state_manager import StateManager
from async_handler import AsyncHandler

# Try to import MCP library
try:
    import mcp
    from mcp import MCPServer, MCPTool, MCPToolParameter
    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP library not found. Using fallback implementation.")
    MCP_AVAILABLE = False

# Fallback MCP implementation if library not available
if not MCP_AVAILABLE:
    class MCPServer:
        def __init__(self, name=None):
            self.name = name or "CodegenMCPServer"
            self.tools = {}
            
        def tool(self, name=None, description=None):
            def decorator(func):
                tool_name = name or func.__name__
                self.tools[tool_name] = {
                    "function": func,
                    "description": description or func.__doc__
                }
                return func
            return decorator
        
        def run(self, host="127.0.0.1", port=8080):
            import http.server
            import socketserver
            import json
            
            class MCPHandler(http.server.BaseHTTPRequestHandler):
                def do_POST(self):
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    request = json.loads(post_data.decode('utf-8'))
                    
                    tool_name = request.get("name")
                    parameters = request.get("parameters", {})
                    
                    if tool_name not in self.server.mcp_server.tools:
                        self.send_response(404)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {"error": f"Tool {tool_name} not found"}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        return
                    
                    try:
                        tool = self.server.mcp_server.tools[tool_name]
                        result = tool["function"](**parameters)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {"result": result}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {"error": str(e)}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
            
            class MCPServer(socketserver.TCPServer):
                def __init__(self, server_address, RequestHandlerClass, mcp_server):
                    self.mcp_server = mcp_server
                    super().__init__(server_address, RequestHandlerClass)
            
            httpd = MCPServer((host, port), MCPHandler, self)
            print(f"Starting MCP server on {host}:{port}")
            httpd.serve_forever()

    class MCPTool:
        def __init__(self, name, description=None):
            self.name = name
            self.description = description
            self.parameters = {}
        
        def parameter(self, name, description=None, required=False):
            def decorator(func):
                self.parameters[name] = {
                    "description": description,
                    "required": required
                }
                return func
            return decorator

    class MCPToolParameter:
        def __init__(self, name, description=None, required=False):
            self.name = name
            self.description = description
            self.required = required

# Create MCP server
server = MCPServer(name="CodegenMCPServer")

# Initialize components
config = Config()
client = CodegenClient(
    org_id=config.get("org_id"),
    api_token=config.get("api_token")
)
state_manager = StateManager()
async_handler = AsyncHandler(client, state_manager)

# Start async handler
async_handler.start()

# ============================================================================
# MCP TOOLS
# ============================================================================

@server.tool(
    name="codegenapi_new",
    description="Start a new Codegen agent run"
)
def codegenapi_new(
    repo: str,
    task: str,
    query: str,
    branch: Optional[str] = None,
    pr: Optional[str] = None,
    wait: bool = False,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Start a new Codegen agent run
    
    Args:
        repo: Repository name (e.g., 'Zeeeepa/codegen.py')
        task: Task type (e.g., 'CREATE_PLAN', 'ANALYZE')
        query: Description of the task
        branch: Optional branch name
        pr: Optional PR number
        wait: Whether to wait for completion
        timeout: Optional timeout in seconds
    
    Returns:
        Dict with agent run details
    """
    try:
        # Validate configuration
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Format the prompt
        prompt_parts = [
            f"Repository: {repo}",
            f"Task: {task}",
            f"Query: {query}"
        ]
        
        if branch:
            prompt_parts.append(f"Branch: {branch}")
        
        if pr:
            prompt_parts.append(f"PR: {pr}")
        
        prompt = "\n".join(prompt_parts)
        
        # Create metadata
        metadata = {
            "repo": repo,
            "task": task,
            "branch": branch,
            "pr": pr,
            "mcp_tool": "codegenapi_new"
        }
        
        # Get the orchestrator ID from the MCP context
        orchestrator_id = os.environ.get("MCP_AGENT_RUN_ID")
        
        if wait:
            # Create the run synchronously and wait for completion
            result = async_handler.create_run_sync(
                prompt=prompt,
                orchestrator_id=orchestrator_id,
                metadata=metadata,
                wait_for_completion=True,
                timeout=timeout
            )
            
            return {
                "status": "success",
                "agent_run_id": result.get("id"),
                "web_url": result.get("web_url"),
                "result": result.get("result"),
                "completed": True
            }
        else:
            # Create the run asynchronously
            result = client.create_agent_run(
                prompt=prompt,
                metadata=metadata,
                orchestrator_id=orchestrator_id
            )
            
            run_id = result.get("id")
            
            # Register the run with the state manager
            state_manager.register_run(
                run_id=str(run_id),
                orchestrator_id=orchestrator_id,
                metadata=metadata
            )
            
            # If this run has an orchestrator, add it as a child
            if orchestrator_id:
                state_manager.add_child_to_orchestrator(
                    orchestrator_id=orchestrator_id,
                    child_run_id=str(run_id)
                )
            
            return {
                "status": "success",
                "agent_run_id": run_id,
                "web_url": result.get("web_url"),
                "message": "Agent run started successfully. Use 'codegenapi_resume' to check status or resume.",
                "completed": False
            }
    
    except Exception as e:
        logger.error(f"Error in codegenapi_new: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(
    name="codegenapi_resume",
    description="Resume a Codegen agent run or check its status"
)
def codegenapi_resume(
    agent_run_id: str,
    query: Optional[str] = None,
    task: Optional[str] = None,
    wait: bool = False,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Resume a Codegen agent run or check its status
    
    Args:
        agent_run_id: ID of the agent run to resume
        query: Optional query to send to the agent
        task: Optional task type
        wait: Whether to wait for completion
        timeout: Optional timeout in seconds
    
    Returns:
        Dict with agent run details
    """
    try:
        # Validate configuration
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Check if we need to resume or just get status
        if query:
            # Resume the agent run
            prompt = query
            if task:
                prompt = f"Task: {task}\nQuery: {query}"
            
            result = client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt=prompt
            )
            
            # If wait is True, wait for completion
            if wait:
                result = client.wait_for_completion(
                    agent_run_id=agent_run_id,
                    timeout=timeout
                )
                
                return {
                    "status": "success",
                    "agent_run_id": result.get("id"),
                    "web_url": result.get("web_url"),
                    "result": result.get("result"),
                    "completed": True
                }
            else:
                return {
                    "status": "success",
                    "agent_run_id": result.get("id"),
                    "web_url": result.get("web_url"),
                    "message": "Agent run resumed successfully.",
                    "completed": False
                }
        else:
            # Just get the status
            result = client.get_agent_run(agent_run_id=agent_run_id)
            
            status = result.get("status")
            is_completed = status in ["completed", "failed", "cancelled"]
            
            return {
                "status": "success",
                "agent_run_id": result.get("id"),
                "web_url": result.get("web_url"),
                "agent_status": status,
                "result": result.get("result") if is_completed else None,
                "completed": is_completed
            }
    
    except Exception as e:
        logger.error(f"Error in codegenapi_resume: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(
    name="codegenapi_config",
    description="Configure Codegen API settings"
)
def codegenapi_config(
    action: str,
    key: Optional[str] = None,
    value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure Codegen API settings
    
    Args:
        action: Action to perform (get, set, list)
        key: Configuration key (for get/set)
        value: Configuration value (for set)
    
    Returns:
        Dict with configuration details
    """
    try:
        if action == "set":
            if not key or not value:
                return {
                    "status": "error",
                    "message": "Both key and value are required for 'set' action."
                }
            
            config.set(key, value)
            return {
                "status": "success",
                "message": f"Configuration {key} set successfully."
            }
        
        elif action == "get":
            if not key:
                return {
                    "status": "error",
                    "message": "Key is required for 'get' action."
                }
            
            value = config.get(key)
            return {
                "status": "success",
                "key": key,
                "value": value
            }
        
        elif action == "list":
            # Get all configuration
            config_data = {}
            for key in ["org_id", "api_token", "base_url"]:
                value = config.get(key)
                if key == "api_token" and value:
                    value = value[:4] + "..." + value[-4:]  # Mask the token
                config_data[key] = value
            
            return {
                "status": "success",
                "config": config_data
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Valid actions are: get, set, list."
            }
    
    except Exception as e:
        logger.error(f"Error in codegenapi_config: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@server.tool(
    name="codegenapi_list",
    description="List Codegen agent runs"
)
def codegenapi_list(
    status: Optional[str] = None,
    repo: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    List Codegen agent runs
    
    Args:
        status: Optional status filter (running, completed, failed, cancelled)
        repo: Optional repository filter
        limit: Maximum number of runs to return
    
    Returns:
        Dict with list of agent runs
    """
    try:
        # Validate configuration
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Get agent runs
        result = client.list_agent_runs(limit=limit)
        
        # Filter by status and repo if provided
        runs = result.get("items", [])
        filtered_runs = []
        
        for run in runs:
            # Get metadata
            metadata = run.get("metadata", {})
            run_repo = metadata.get("repo")
            
            # Apply filters
            if status and run.get("status") != status:
                continue
            
            if repo and run_repo != repo:
                continue
            
            # Add to filtered runs
            filtered_runs.append({
                "id": run.get("id"),
                "status": run.get("status"),
                "created_at": run.get("created_at"),
                "web_url": run.get("web_url"),
                "repo": run_repo,
                "task": metadata.get("task")
            })
        
        return {
            "status": "success",
            "runs": filtered_runs,
            "total": len(filtered_runs)
        }
    
    except Exception as e:
        logger.error(f"Error in codegenapi_list: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="Codegen MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print("=" * 80)
    print("Codegen MCP Server")
    print("=" * 80)
    print(f"Starting server on {args.host}:{args.port}")
    print("Available tools:")
    for tool_name in server.tools:
        print(f"  - {tool_name}")
    print("=" * 80)
    
    # Start the server
    try:
        server.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        async_handler.stop()
        print("Server stopped.")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        async_handler.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()

