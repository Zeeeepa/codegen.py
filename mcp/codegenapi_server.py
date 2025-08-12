#!/usr/bin/env python3
"""
Codegen API MCP Server

A Model Context Protocol server that provides access to Codegen API functionality.
Supports core commands: new, resume, config, list
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource,
)

# Import the codegen API
try:
    from codegen_api import Agent, CodegenAPIError, ClientConfig
except ImportError as e:
    print(f"Error importing codegen_api: {e}", file=sys.stderr)
    sys.exit(1)

# Configuration file path
CONFIG_FILE = Path.home() / ".codegenapi" / "config.json"

class CodegenMCPServer:
    """MCP Server for Codegen API"""
    
    def __init__(self):
        self.server = Server("codegenapi")
        self.config = self._load_config()
        
        # Register tools
        self._register_tools()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config: {e}", file=sys.stderr)
        return {}
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise Exception(f"Could not save config: {e}")
    
    def _get_agent(self) -> Agent:
        """Get configured Agent instance"""
        api_token = self.config.get('api_token') or os.getenv('CODEGEN_API_TOKEN')
        org_id = self.config.get('org_id') or os.getenv('CODEGEN_ORG_ID')
        
        if not api_token:
            raise Exception("API token not configured. Use 'codegenapi config set api-token YOUR_TOKEN'")
        
        return Agent(org_id=org_id, token=api_token)
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="codegenapi_new",
                        description="Start a new agent run",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "repo": {
                                    "type": "string",
                                    "description": "Repository name (e.g., 'user/repo' or 'Zeeeepa/codegen.py')"
                                },
                                "branch": {
                                    "type": "string",
                                    "description": "Branch name (optional)"
                                },
                                "pr": {
                                    "type": "integer",
                                    "description": "PR number (optional)"
                                },
                                "task": {
                                    "type": "string",
                                    "description": "Task type (e.g., 'CREATE_PLAN', 'FEATURE_IMPLEMENTATION', 'BUG_FIX')"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Task description/query"
                                }
                            },
                            "required": ["repo", "task", "query"]
                        }
                    ),
                    Tool(
                        name="codegenapi_resume",
                        description="Resume an existing agent run",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "agent_run_id": {
                                    "type": "integer",
                                    "description": "Agent run ID to resume"
                                },
                                "task": {
                                    "type": "string",
                                    "description": "Optional task type for the resume operation"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Additional instructions for resuming"
                                }
                            },
                            "required": ["agent_run_id", "query"]
                        }
                    ),
                    Tool(
                        name="codegenapi_config",
                        description="Manage configuration settings",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["set", "get", "list"],
                                    "description": "Configuration action"
                                },
                                "key": {
                                    "type": "string",
                                    "description": "Configuration key (for set/get actions)"
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Configuration value (for set action)"
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="codegenapi_list",
                        description="List agent runs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "running", "completed", "failed", "cancelled", "paused"],
                                    "description": "Filter by status (optional)"
                                },
                                "limit": {
                                    "type": "integer",
                                    "default": 10,
                                    "description": "Number of runs to return (default: 10)"
                                },
                                "repo": {
                                    "type": "string",
                                    "description": "Filter by repository (optional)"
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                if name == "codegenapi_new":
                    return await self._handle_new(arguments)
                elif name == "codegenapi_resume":
                    return await self._handle_resume(arguments)
                elif name == "codegenapi_config":
                    return await self._handle_config(arguments)
                elif name == "codegenapi_list":
                    return await self._handle_list(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _handle_new(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle new agent run creation"""
        repo = args["repo"]
        branch = args.get("branch")
        pr = args.get("pr")
        task = args["task"]
        query = args["query"]
        
        # Build the prompt with context
        prompt_parts = [f"Task: {task}", f"Repository: {repo}"]
        
        if branch:
            prompt_parts.append(f"Branch: {branch}")
        if pr:
            prompt_parts.append(f"PR: #{pr}")
        
        prompt_parts.append(f"Description: {query}")
        prompt = "\n".join(prompt_parts)
        
        # Create metadata
        metadata = {
            "repo": repo,
            "task_type": task,
            "original_query": query
        }
        if branch:
            metadata["branch"] = branch
        if pr:
            metadata["pr"] = pr
        
        try:
            with self._get_agent() as agent:
                task_obj = agent.run(prompt=prompt, metadata=metadata)
                
                result = {
                    "success": True,
                    "agent_run_id": task_obj.id,
                    "status": task_obj.status,
                    "web_url": task_obj.web_url,
                    "message": f"Created new agent run {task_obj.id}"
                }
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating agent run: {str(e)}")]
            )
    
    async def _handle_resume(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle resuming an agent run"""
        agent_run_id = args["agent_run_id"]
        task = args.get("task")
        query = args["query"]
        
        # Build resume prompt
        prompt_parts = [f"Resume with: {query}"]
        if task:
            prompt_parts.insert(0, f"Task: {task}")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            with self._get_agent() as agent:
                task_obj = agent.get_task(agent_run_id)
                result_data = task_obj.resume(prompt=prompt)
                
                result = {
                    "success": True,
                    "agent_run_id": agent_run_id,
                    "status": result_data.status,
                    "web_url": task_obj.web_url,
                    "message": f"Resumed agent run {agent_run_id}"
                }
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error resuming agent run: {str(e)}")]
            )
    
    async def _handle_config(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle configuration management"""
        action = args["action"]
        
        if action == "set":
            key = args.get("key")
            value = args.get("value")
            
            if not key or not value:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Both 'key' and 'value' are required for set action")]
                )
            
            # Handle special keys
            if key == "api-token":
                key = "api_token"
            elif key == "org_id":
                try:
                    value = int(value)
                except ValueError:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Error: org_id must be a number")]
                    )
            
            self.config[key] = value
            self._save_config(self.config)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Set {key} = {value}")]
            )
        
        elif action == "get":
            key = args.get("key")
            if not key:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: 'key' is required for get action")]
                )
            
            if key == "api-token":
                key = "api_token"
            
            value = self.config.get(key, "Not set")
            
            # Mask sensitive values
            if key == "api_token" and value != "Not set":
                value = f"{value[:8]}...{value[-4:]}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"{key} = {value}")]
            )
        
        elif action == "list":
            config_display = {}
            for key, value in self.config.items():
                if key == "api_token" and value:
                    config_display[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    config_display[key] = value
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(config_display, indent=2))]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown config action: {action}")]
            )
    
    async def _handle_list(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle listing agent runs"""
        status_filter = args.get("status")
        limit = args.get("limit", 10)
        repo_filter = args.get("repo")
        
        try:
            with self._get_agent() as agent:
                tasks = agent.list_tasks(limit=limit)
                
                results = []
                for task in tasks:
                    task_info = {
                        "agent_run_id": task.id,
                        "status": task.status,
                        "web_url": task.web_url
                    }
                    
                    # Get metadata if available
                    try:
                        task.refresh()
                        if hasattr(task._data, 'metadata') and task._data.metadata:
                            metadata = task._data.metadata
                            if isinstance(metadata, str):
                                try:
                                    metadata = json.loads(metadata)
                                except:
                                    pass
                            
                            if isinstance(metadata, dict):
                                task_info["repo"] = metadata.get("repo")
                                task_info["task_type"] = metadata.get("task_type")
                                task_info["branch"] = metadata.get("branch")
                                task_info["pr"] = metadata.get("pr")
                    except:
                        pass
                    
                    # Apply filters
                    if status_filter and task_info["status"] != status_filter:
                        continue
                    if repo_filter and task_info.get("repo") != repo_filter:
                        continue
                    
                    results.append(task_info)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(results, indent=2))]
                )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing agent runs: {str(e)}")]
            )

async def main():
    """Main entry point for the MCP server"""
    server_instance = CodegenMCPServer()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
