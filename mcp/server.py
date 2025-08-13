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
from typing import Dict, Any, Optional, List, Union, TypedDict, cast
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if MCP library is available
try:
    import mcp
    HAS_MCP = True
    logger.info("MCP library found. Using MCP server implementation.")
except ImportError:
    HAS_MCP = False
    logger.warning("MCP library not found. Using fallback implementation.")

# Import MCP server components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codegen_client import CodegenClient
from config import Config
from state_manager import StateManager
from async_handler import AsyncHandler

# Define MCP server types
@dataclass
class MCPToolParameter:
    """MCP tool parameter definition"""
    name: str
    description: str
    required: bool = False
    type: str = "string"
    default: Optional[Any] = None
    enum: Optional[List[str]] = None

@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    parameters: List[MCPToolParameter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": param.name,
                    "description": param.description,
                    "required": param.required,
                    "type": param.type,
                    **({"default": param.default} if param.default is not None else {}),
                    **({"enum": param.enum} if param.enum is not None else {})
                }
                for param in self.parameters
            ]
        }

@dataclass
class MCPServer:
    """MCP server definition"""
    name: str
    description: str
    tools: List[MCPTool] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.to_dict() for tool in self.tools]
        }

# ============================================================================
# MCP TOOL IMPLEMENTATIONS
# ============================================================================

# USER ENDPOINTS

def codegenapi_get_users(
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """Get all users in an organization"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get users
        result = client.get_users(
            skip=skip,
            limit=limit
        )
        
        # Return result
        return {
            "status": "success",
            "users": result.get("items", []),
            "total": result.get("total", 0)
        }
    
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return {
            "status": "error",
            "message": f"Error getting users: {str(e)}"
        }

def codegenapi_get_user(
    user_id: str
) -> Dict[str, Any]:
    """Get a specific user by ID"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get user
        result = client.get_user(user_id=user_id)
        
        # Return result
        return {
            "status": "success",
            "user": result
        }
    
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return {
            "status": "error",
            "message": f"Error getting user: {str(e)}"
        }

def codegenapi_get_current_user() -> Dict[str, Any]:
    """Get information about the currently authenticated user"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get current user
        result = client.get_current_user()
        
        # Return result
        return {
            "status": "success",
            "user": result
        }
    
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return {
            "status": "error",
            "message": f"Error getting current user: {str(e)}"
        }

# ORGANIZATION ENDPOINTS

def codegenapi_get_organizations(
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """Get organizations for the authenticated user"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get organizations
        result = client.get_organizations(
            skip=skip,
            limit=limit
        )
        
        # Return result
        return {
            "status": "success",
            "organizations": result.get("items", []),
            "total": result.get("total", 0)
        }
    
    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return {
            "status": "error",
            "message": f"Error getting organizations: {str(e)}"
        }

# AGENT ENDPOINTS

def codegenapi_new(
    repo: Optional[str] = None,
    branch: Optional[str] = None,
    pr: Optional[int] = None,
    task: Optional[str] = None,
    query: str = ""
) -> Dict[str, Any]:
    """Create a new agent run"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Create metadata
        metadata = {
            "repo": repo,
            "branch": branch,
            "pr": pr,
            "task": task,
            "mcp_tool": "codegenapi_new"
        }
        
        # Create agent run
        result = client.create_agent_run(
            prompt=query,
            repo=repo,
            branch=branch,
            pr=pr,
            task=task,
            metadata=metadata
        )
        
        # Return result
        return {
            "status": "success",
            "agent_run_id": result.get("id"),
            "web_url": result.get("web_url"),
            "message": f"Agent run created successfully. ID: {result.get('id')}"
        }
    
    except Exception as e:
        logger.error(f"Error creating agent run: {e}")
        return {
            "status": "error",
            "message": f"Error creating agent run: {str(e)}"
        }

def codegenapi_get_agent_run(
    agent_run_id: Union[str, int]
) -> Dict[str, Any]:
    """Get agent run details"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get agent run
        result = client.get_agent_run(agent_run_id=agent_run_id)
        
        # Return result
        return {
            "status": "success",
            "agent_run": result
        }
    
    except Exception as e:
        logger.error(f"Error getting agent run: {e}")
        return {
            "status": "error",
            "message": f"Error getting agent run: {str(e)}"
        }

def codegenapi_resume(
    agent_run_id: Union[str, int],
    task: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """Resume an agent run"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get agent run
        run = client.get_agent_run(agent_run_id=agent_run_id)
        
        # If query is provided, resume the agent run
        if query:
            # Create metadata
            metadata = {
                "task": task,
                "mcp_tool": "codegenapi_resume"
            }
            
            # Resume agent run
            result = client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt=query,
                task=task
            )
            
            # Return result
            return {
                "status": "success",
                "agent_run_id": result.get("id"),
                "web_url": result.get("web_url"),
                "message": f"Agent run resumed successfully. ID: {result.get('id')}"
            }
        
        # Otherwise, just return the agent run
        return {
            "status": "success",
            "agent_run_id": run.get("id"),
            "web_url": run.get("web_url"),
            "status": run.get("status"),
            "result": run.get("result"),
            "message": f"Agent run status: {run.get('status')}"
        }
    
    except Exception as e:
        logger.error(f"Error resuming agent run: {e}")
        return {
            "status": "error",
            "message": f"Error resuming agent run: {str(e)}"
        }

def codegenapi_list(
    status: Optional[str] = None,
    limit: int = 100,
    repo: Optional[str] = None
) -> Dict[str, Any]:
    """List agent runs"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # List agent runs
        result = client.list_agent_runs(
            status=status,
            limit=limit,
            repo=repo
        )
        
        # Format runs
        runs = []
        for run in result.get("items", []):
            runs.append({
                "id": run.get("id"),
                "status": run.get("status"),
                "created_at": run.get("created_at"),
                "web_url": run.get("web_url"),
                "repo": run.get("metadata", {}).get("repo"),
                "task": run.get("metadata", {}).get("task")
            })
        
        # Return result
        return {
            "status": "success",
            "runs": runs,
            "total": len(runs)
        }
    
    except Exception as e:
        logger.error(f"Error listing agent runs: {e}")
        return {
            "status": "error",
            "message": f"Error listing agent runs: {str(e)}"
        }

def codegenapi_get_agent_run_logs(
    agent_run_id: Union[str, int],
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """Get logs for an agent run"""
    try:
        # Get configuration
        config = Config()
        if not config.validate():
            return {
                "status": "error",
                "message": "Configuration not valid. Please set org_id and api_token."
            }
        
        # Create client
        client = CodegenClient(
            org_id=config.get("org_id"),
            api_token=config.get("api_token")
        )
        
        # Get agent run logs
        result = client.get_agent_run_logs(
            agent_run_id=agent_run_id,
            skip=skip,
            limit=limit
        )
        
        # Return result
        return {
            "status": "success",
            "logs": result.get("items", []),
            "total": result.get("total", 0)
        }
    
    except Exception as e:
        logger.error(f"Error getting agent run logs: {e}")
        return {
            "status": "error",
            "message": f"Error getting agent run logs: {str(e)}"
        }

def codegenapi_config(
    action: str = "list",
    key: Optional[str] = None,
    value: Optional[str] = None
) -> Dict[str, Any]:
    """Manage configuration"""
    try:
        # Get configuration
        config = Config()
        
        # Handle action
        if action == "list":
            # List all configuration
            return {
                "status": "success",
                "config": config.get_config()
            }
        
        elif action == "get":
            # Get a specific configuration value
            if not key:
                return {
                    "status": "error",
                    "message": "Key is required for get action."
                }
            
            return {
                "status": "success",
                "key": key,
                "value": config.get(key)
            }
        
        elif action == "set":
            # Set a specific configuration value
            if not key:
                return {
                    "status": "error",
                    "message": "Key is required for set action."
                }
            
            if value is None:
                return {
                    "status": "error",
                    "message": "Value is required for set action."
                }
            
            config.set(key, value)
            
            return {
                "status": "success",
                "message": f"Configuration {key} set successfully."
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    except Exception as e:
        logger.error(f"Error managing configuration: {e}")
        return {
            "status": "error",
            "message": f"Error managing configuration: {str(e)}"
        }

# Define MCP request handler
class MCPRequestHandler(BaseHTTPRequestHandler):
    """MCP request handler"""
    
    def __init__(self, *args, **kwargs):
        # Initialize components
        self.config = Config()
        self.client = CodegenClient(
            org_id=self.config.get("org_id"),
            api_token=self.config.get("api_token")
        )
        self.state_manager = StateManager()
        self.async_handler = AsyncHandler(self.client, self.state_manager)
        
        # Start async handler
        self.async_handler.start()
        
        # Initialize server
        super().__init__(*args, **kwargs)
    
    def _send_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send a JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
    
    def do_OPTIONS(self) -> None:
        """Handle OPTIONS requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self) -> None:
        """Handle GET requests"""
        # Parse URL
        url = urlparse(self.path)
        
        # Handle root path
        if url.path == "/":
            self._send_response(200, {"status": "ok", "message": "Codegen MCP Server"})
            return
        
        # Handle MCP manifest
        if url.path == "/mcp/manifest":
            # Create MCP server definition
            server = MCPServer(
                name="Codegen MCP Server",
                description="MCP server for Codegen API",
                tools=[
                    # User endpoints
                    MCPTool(
                        name="codegenapi_get_users",
                        description="Get all users in an organization",
                        parameters=[
                            MCPToolParameter(
                                name="skip",
                                description="Number of users to skip (for pagination)",
                                required=False,
                                type="integer",
                                default=0
                            ),
                            MCPToolParameter(
                                name="limit",
                                description="Maximum number of users to return",
                                required=False,
                                type="integer",
                                default=100
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_get_user",
                        description="Get a specific user by ID",
                        parameters=[
                            MCPToolParameter(
                                name="user_id",
                                description="User ID",
                                required=True,
                                type="string"
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_get_current_user",
                        description="Get information about the currently authenticated user",
                        parameters=[]
                    ),
                    
                    # Organization endpoints
                    MCPTool(
                        name="codegenapi_get_organizations",
                        description="Get organizations for the authenticated user",
                        parameters=[
                            MCPToolParameter(
                                name="skip",
                                description="Number of organizations to skip (for pagination)",
                                required=False,
                                type="integer",
                                default=0
                            ),
                            MCPToolParameter(
                                name="limit",
                                description="Maximum number of organizations to return",
                                required=False,
                                type="integer",
                                default=100
                            )
                        ]
                    ),
                    
                    # Agent endpoints
                    MCPTool(
                        name="codegenapi_new",
                        description="Start a new agent run",
                        parameters=[
                            MCPToolParameter(
                                name="repo",
                                description="Repository name (e.g. 'user/repo')",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="branch",
                                description="Branch name",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="pr",
                                description="Pull request number",
                                required=False,
                                type="integer"
                            ),
                            MCPToolParameter(
                                name="task",
                                description="Task type",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="query",
                                description="Query or prompt for the agent",
                                required=True,
                                type="string"
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_get_agent_run",
                        description="Get agent run details",
                        parameters=[
                            MCPToolParameter(
                                name="agent_run_id",
                                description="Agent run ID",
                                required=True,
                                type="string"
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_resume",
                        description="Resume an agent run",
                        parameters=[
                            MCPToolParameter(
                                name="agent_run_id",
                                description="Agent run ID",
                                required=True,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="task",
                                description="Task type",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="query",
                                description="Query or prompt for the agent",
                                required=False,
                                type="string"
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_list",
                        description="List agent runs",
                        parameters=[
                            MCPToolParameter(
                                name="status",
                                description="Filter by status",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="limit",
                                description="Maximum number of runs to return",
                                required=False,
                                type="integer",
                                default=100
                            ),
                            MCPToolParameter(
                                name="repo",
                                description="Filter by repository",
                                required=False,
                                type="string"
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_get_agent_run_logs",
                        description="Get logs for an agent run",
                        parameters=[
                            MCPToolParameter(
                                name="agent_run_id",
                                description="Agent run ID",
                                required=True,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="skip",
                                description="Number of logs to skip (for pagination)",
                                required=False,
                                type="integer",
                                default=0
                            ),
                            MCPToolParameter(
                                name="limit",
                                description="Maximum number of logs to return",
                                required=False,
                                type="integer",
                                default=100
                            )
                        ]
                    ),
                    MCPTool(
                        name="codegenapi_config",
                        description="Manage configuration",
                        parameters=[
                            MCPToolParameter(
                                name="action",
                                description="Action to perform",
                                required=False,
                                type="string",
                                default="list",
                                enum=["list", "get", "set"]
                            ),
                            MCPToolParameter(
                                name="key",
                                description="Configuration key",
                                required=False,
                                type="string"
                            ),
                            MCPToolParameter(
                                name="value",
                                description="Configuration value",
                                required=False,
                                type="string"
                            )
                        ]
                    )
                ]
            )
            
            # Send response
            self._send_response(200, server.to_dict())
            return
        
        # Handle unknown paths
        self._send_response(404, {"status": "error", "message": "Not found"})
    
    def do_POST(self) -> None:
        """Handle POST requests"""
        # Parse URL
        url = urlparse(self.path)
        
        # Handle MCP invoke
        if url.path == "/mcp/invoke":
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                # Parse request body
                data = json.loads(body)
                
                # Get tool name and parameters
                tool_name = data.get("name")
                parameters = data.get("parameters", {})
                
                # Handle tool invocation
                if tool_name == "codegenapi_get_users":
                    result = codegenapi_get_users(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_get_user":
                    result = codegenapi_get_user(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_get_current_user":
                    result = codegenapi_get_current_user()
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_get_organizations":
                    result = codegenapi_get_organizations(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_new":
                    result = codegenapi_new(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_get_agent_run":
                    result = codegenapi_get_agent_run(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_resume":
                    result = codegenapi_resume(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_list":
                    result = codegenapi_list(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_get_agent_run_logs":
                    result = codegenapi_get_agent_run_logs(**parameters)
                    self._send_response(200, result)
                    return
                
                elif tool_name == "codegenapi_config":
                    result = codegenapi_config(**parameters)
                    self._send_response(200, result)
                    return
                
                else:
                    self._send_response(400, {
                        "status": "error",
                        "message": f"Unknown tool: {tool_name}"
                    })
                    return
            
            except json.JSONDecodeError:
                self._send_response(400, {
                    "status": "error",
                    "message": "Invalid JSON"
                })
                return
            
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                self._send_response(500, {
                    "status": "error",
                    "message": f"Error handling request: {str(e)}"
                })
                return
        
        # Handle unknown paths
        self._send_response(404, {"status": "error", "message": "Not found"})

def main() -> None:
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Codegen MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize components
    config = Config()
    state_manager = StateManager()
    client = CodegenClient(
        org_id=config.get("org_id"),
        api_token=config.get("api_token")
    )
    async_handler = AsyncHandler(client, state_manager)
    
    # Start async handler
    async_handler.start()
    
    # Print server information
    print("=" * 80)
    print("Codegen MCP Server")
    print("=" * 80)
    print(f"Starting server on {args.host}:{args.port}")
    print("Available tools:")
    print("  - codegenapi_get_users")
    print("  - codegenapi_get_user")
    print("  - codegenapi_get_current_user")
    print("  - codegenapi_get_organizations")
    print("  - codegenapi_new")
    print("  - codegenapi_get_agent_run")
    print("  - codegenapi_resume")
    print("  - codegenapi_list")
    print("  - codegenapi_get_agent_run_logs")
    print("  - codegenapi_config")
    print("=" * 80)
    
    # Start server
    server = HTTPServer((args.host, args.port), MCPRequestHandler)
    print(f"Starting MCP server on {args.host}:{args.port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        # Stop async handler
        async_handler.stop()
        
        # Stop server
        server.server_close()

if __name__ == "__main__":
    main()

