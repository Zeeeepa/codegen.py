#!/usr/bin/env python3
"""
Codegen API MCP Server

A Model Context Protocol server that provides access to Codegen API functionality.
Supports core commands: new, resume, config, list
Also provides direct API endpoints for users, agents, organizations, and logs
"""

import asyncio
import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Any, Dict, Optional, List
from threading import Thread

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp_types import (
    CallToolResponse,
    ListToolsResult,
    TextContent,
    Tool,
)

# Import the codegen API
try:
    from codegen_api import Agent, Task
    from codegen_endpoints import CodegenEndpoints
except ImportError as e:
    print(f"Error importing codegen_api or codegen_endpoints: {e}", file=sys.stderr)
    sys.exit(1)

# Configuration file path
CONFIG_FILE = Path.home() / ".codegenapi" / "config.json"

# Relationship tracking file path
RELATIONSHIPS_FILE = Path.home() / ".codegenapi" / "relationships.json"

class CodegenMCPServer:
    """MCP Server for Codegen API"""
    
    def __init__(self, api_token: Optional[str] = None, org_id: Optional[int] = None, debug: bool = False):
        self.server = Server("codegenapi")
        self.config = self._load_config()
        self.relationships = self._load_relationships()
        self.monitoring_thread: Optional[Thread] = None
        self.stop_monitoring = False
        self.endpoints: Optional[CodegenEndpoints] = None
        self.debug = debug
        
        # Get API token and org ID from parameters or environment variables
        self.api_token = api_token or self.config.get('api_token') or os.getenv('CODEGEN_API_TOKEN')
        self.org_id = org_id or self.config.get('org_id') or os.getenv('CODEGEN_ORG_ID')
        
        if self.org_id and isinstance(self.org_id, str):
            try:
                self.org_id = int(self.org_id)
            except ValueError:
                print(f"Warning: Invalid org_id: {self.org_id}", file=sys.stderr)
                self.org_id = None
        
        # Initialize endpoints
        if self.api_token:
            # Cast org_id to the correct type for CodegenEndpoints
            org_id_param = int(self.org_id) if self.org_id is not None and not isinstance(self.org_id, bool) else None
            self.endpoints = CodegenEndpoints(api_token=self.api_token, org_id=org_id_param)
        else:
            self.endpoints = None
        
        # Register tools
        self._register_tools()
        
        # Start the monitoring thread
        self._start_monitoring_thread()
    
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
    
    def _load_relationships(self) -> Dict[str, Any]:
        """Load agent relationships from file"""
        if RELATIONSHIPS_FILE.exists():
            try:
                with open(RELATIONSHIPS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load relationships: {e}", file=sys.stderr)
        return {
            "parent_child": {},  # parent_id -> [child_ids]
            "child_parent": {},  # child_id -> parent_id
            "active_runs": [],   # list of active run IDs
            "completed_runs": [] # list of completed run IDs
        }
    
    def _save_relationships(self) -> None:
        """Save agent relationships to file"""
        RELATIONSHIPS_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(RELATIONSHIPS_FILE, 'w') as f:
                json.dump(self.relationships, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save relationships: {e}", file=sys.stderr)
    
    def _register_parent_child(self, parent_id: int, child_id: int) -> None:
        """Register a parent-child relationship between agent runs"""
        # Convert to strings for JSON serialization
        parent_id_str = str(parent_id)
        child_id_str = str(child_id)
        
        # Initialize parent entry if it doesn't exist
        if parent_id_str not in self.relationships["parent_child"]:
            self.relationships["parent_child"][parent_id_str] = []
        
        # Add child to parent's list
        if child_id_str not in self.relationships["parent_child"][parent_id_str]:
            self.relationships["parent_child"][parent_id_str].append(child_id_str)
        
        # Register child's parent
        self.relationships["child_parent"][child_id_str] = parent_id_str
        
        # Add to active runs
        if child_id_str not in self.relationships["active_runs"]:
            self.relationships["active_runs"].append(child_id_str)
        
        # Save relationships
        self._save_relationships()
    
    def _mark_run_completed(self, run_id: int) -> None:
        """Mark an agent run as completed"""
        run_id_str = str(run_id)
        
        # Remove from active runs
        if run_id_str in self.relationships["active_runs"]:
            self.relationships["active_runs"].remove(run_id_str)
        
        # Add to completed runs
        if run_id_str not in self.relationships["completed_runs"]:
            self.relationships["completed_runs"].append(run_id_str)
        
        # Save relationships
        self._save_relationships()
    
    def _start_monitoring_thread(self) -> None:
        """Start a thread to monitor agent runs"""
        if self.monitoring_thread is None or (self.monitoring_thread and not self.monitoring_thread.is_alive()):
            self.stop_monitoring = False
            self.monitoring_thread = threading.Thread(target=self._monitor_agent_runs)
            if self.monitoring_thread:
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()
    
    def _monitor_agent_runs(self) -> None:
        """Monitor agent runs for completion and handle orchestration"""
        print("Starting agent run monitoring thread", file=sys.stderr)
        
        while not self.stop_monitoring:
            try:
                # Get a copy of active runs to avoid modification during iteration
                active_runs = self.relationships["active_runs"].copy()
                
                if active_runs:
                    with self._get_agent() as agent:
                        for run_id_str in active_runs:
                            try:
                                run_id = int(run_id_str)
                                task = agent.get_task(run_id)
                                task.refresh()
                                
                                # Check if the run is completed
                                if task.status in ["completed", "failed", "cancelled"]:
                                    self._handle_completed_run(task)
                            except Exception as e:
                                print(f"Error monitoring run {run_id_str}: {e}", file=sys.stderr)
            
            except Exception as e:
                print(f"Error in monitoring thread: {e}", file=sys.stderr)
            
            # Sleep before checking again
            time.sleep(10)
    
    def _handle_completed_run(self, task: Task) -> None:
        """Handle a completed agent run"""
        run_id_str = str(task.id)
        
        # Mark as completed
        self._mark_run_completed(task.id)
        
        # Check if this is a child run
        if run_id_str in self.relationships["child_parent"]:
            parent_id_str = self.relationships["child_parent"][run_id_str]
            parent_id = int(parent_id_str)
            
            # Get the response from the completed run
            response = f"Agent run {task.id} completed with status: {task.status}"
            if hasattr(task, 'response') and task.response:
                response = task.response
            
            # Check if parent is still active
            is_parent_active = parent_id_str in self.relationships["active_runs"]
            
            if is_parent_active:
                print(f"Parent run {parent_id} is active, sending response directly", file=sys.stderr)
                # TODO: In a real implementation, we would send the response directly
                # to the parent run through the appropriate channel
            else:
                print(f"Parent run {parent_id} is not active, resuming with response", file=sys.stderr)
                try:
                    # Resume the parent run with the response
                    with self._get_agent() as agent:
                        parent_task = agent.get_task(parent_id)
                        resume_prompt = f"Response from agent run {task.id}: {response}"
                        parent_task.resume(prompt=resume_prompt)
                except Exception as e:
                    print(f"Error resuming parent run {parent_id}: {e}", file=sys.stderr)
    
    def _get_agent(self) -> Agent:
        """Get configured Agent instance"""
        api_token = self.config.get('api_token') or os.getenv('CODEGEN_API_TOKEN')
        org_id = self.config.get('org_id') or os.getenv('CODEGEN_ORG_ID')
        
        if not api_token:
            raise Exception("API token not configured. Use 'codegenapi config set api-token YOUR_TOKEN'")
        
        return Agent(org_id=org_id, token=api_token)
    
    async def start(self):
        """Start the MCP server"""
        if self.debug:
            print("Starting Codegen API MCP server in debug mode", file=sys.stderr)
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def _register_tools(self) -> List[Tool]:
        """Register all MCP tools and return the list of tools"""
        
        # Register core tools
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            tools = [
                Tool(
                    name="codegenapi_new",
                    description="Start a new agent run",
                    parameters={
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
                            },
                            "parent_id": {
                                "type": "integer",
                                "description": "Optional parent agent run ID for orchestration"
                            },
                            "wait_for_completion": {
                                "type": "boolean",
                                "description": "Whether to wait for the run to complete before returning",
                                "default": False
                            }
                        },
                        "required": ["repo", "task", "query"]
                    }
                ),
                Tool(
                    name="codegenapi_resume",
                    description="Resume an existing agent run",
                    parameters={
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
                            },
                            "wait_for_completion": {
                                "type": "boolean",
                                "description": "Whether to wait for the run to complete before returning",
                                "default": False
                            }
                        },
                        "required": ["agent_run_id", "query"]
                    }
                ),
                Tool(
                    name="codegenapi_config",
                    description="Manage configuration settings",
                    parameters={
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
                    parameters={
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
            
            # Add API endpoint tools if endpoints are available
            if self.endpoints:
                tools.extend(self.endpoints.register_tools())
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResponse:
            try:
                # Handle core tools
                if name == "codegenapi_new":
                    return await self._handle_new(arguments)
                elif name == "codegenapi_resume":
                    return await self._handle_resume(arguments)
                elif name == "codegenapi_config":
                    return await self._handle_config(arguments)
                elif name == "codegenapi_list":
                    return await self._handle_list(arguments)
                
                # Handle API endpoint tools
                elif self.endpoints and name.startswith("codegen_"):
                    # Users endpoints
                    if name == "codegen_get_users":
                        return await self.endpoints.handle_get_users(arguments)
                    elif name == "codegen_get_user":
                        return await self.endpoints.handle_get_user(arguments)
                    elif name == "codegen_get_current_user":
                        return await self.endpoints.handle_get_current_user(arguments)
                    
                    # Agents endpoints
                    elif name == "codegen_create_agent_run":
                        return await self.endpoints.handle_create_agent_run(arguments)
                    elif name == "codegen_get_agent_run":
                        return await self.endpoints.handle_get_agent_run(arguments)
                    elif name == "codegen_list_agent_runs":
                        return await self.endpoints.handle_list_agent_runs(arguments)
                    elif name == "codegen_resume_agent_run":
                        return await self.endpoints.handle_resume_agent_run(arguments)
                    
                    # Organizations endpoint
                    elif name == "codegen_get_organizations":
                        return await self.endpoints.handle_get_organizations(arguments)
                    
                    # Agents-Alpha endpoint
                    elif name == "codegen_get_agent_run_logs":
                        return await self.endpoints.handle_get_agent_run_logs(arguments)
                
                # Unknown tool
                else:
                    return CallToolResponse(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                return CallToolResponse(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
        
        # Return the list of tools for type checking
        tools = []
        if self.endpoints:
            tools.extend(self.endpoints.register_tools())
        return tools
    
    async def _handle_new(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle new agent run creation"""
        repo = args["repo"]
        branch = args.get("branch")
        pr = args.get("pr")
        task = args["task"]
        query = args["query"]
        parent_id = args.get("parent_id")  # Optional parent agent run ID
        wait_for_completion = args.get("wait_for_completion", False)  # Whether to wait for completion
        
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
        if parent_id:
            metadata["parent_id"] = parent_id
        
        try:
            with self._get_agent() as agent:
                task_obj = agent.run(prompt=prompt, metadata=metadata)
                
                # Register the run as active
                if task_obj.id not in self.relationships["active_runs"]:
                    self.relationships["active_runs"].append(str(task_obj.id))
                    self._save_relationships()
                
                # Register parent-child relationship if parent_id is provided
                if parent_id:
                    self._register_parent_child(parent_id, task_obj.id)
                
                result = {
                    "success": True,
                    "agent_run_id": task_obj.id,
                    "status": task_obj.status,
                    "web_url": task_obj.web_url,
                    "message": f"Created new agent run {task_obj.id}"
                }
                
                # If wait_for_completion is True, wait for the run to complete
                if wait_for_completion:
                    result["message"] += " (waiting for completion)"
                    
                    # Poll until the run is complete
                    while task_obj.status not in ["completed", "failed", "cancelled"]:
                        time.sleep(5)
                        task_obj.refresh()
                    
                    # Update the result with the final status
                    result["status"] = task_obj.status
                    result["message"] = f"Agent run {task_obj.id} completed with status: {task_obj.status}"
                    
                    # Include the response if available
                    if hasattr(task_obj, 'response') and task_obj.response:
                        result["response"] = task_obj.response
                    
                    # Mark as completed
                    self._mark_run_completed(task_obj.id)
                
                return CallToolResponse(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error creating agent run: {str(e)}")]
            )
    
    async def _handle_resume(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle resuming an agent run"""
        agent_run_id = args["agent_run_id"]
        task = args.get("task")
        query = args["query"]
        wait_for_completion = args.get("wait_for_completion", False)  # Whether to wait for completion
        
        # Build resume prompt
        prompt_parts = [f"Resume with: {query}"]
        if task:
            prompt_parts.insert(0, f"Task: {task}")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            with self._get_agent() as agent:
                task_obj = agent.get_task(agent_run_id)
                
                # Register the run as active if it's not already
                if str(agent_run_id) not in self.relationships["active_runs"]:
                    self.relationships["active_runs"].append(str(agent_run_id))
                    self._save_relationships()
                
                # Resume the task
                result_data = task_obj.resume(prompt=prompt)
                
                result = {
                    "success": True,
                    "agent_run_id": agent_run_id,
                    "status": result_data.status,
                    "web_url": task_obj.web_url,
                    "message": f"Resumed agent run {agent_run_id}"
                }
                
                # If wait_for_completion is True, wait for the run to complete
                if wait_for_completion:
                    result["message"] += " (waiting for completion)"
                    
                    # Poll until the run is complete
                    while result_data.status not in ["completed", "failed", "cancelled"]:
                        time.sleep(5)
                        task_obj.refresh()
                        result_data = task_obj  # Update result_data with refreshed task
                    
                    # Update the result with the final status
                    result["status"] = result_data.status
                    result["message"] = f"Agent run {agent_run_id} completed with status: {result_data.status}"
                    
                    # Include the response if available
                    if hasattr(result_data, 'response') and result_data.response:
                        result["response"] = result_data.response
                    
                    # Mark as completed
                    self._mark_run_completed(agent_run_id)
                
                return CallToolResponse(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error resuming agent run: {str(e)}")]
            )
    
    async def _handle_config(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle configuration management"""
        action = args["action"]
        
        if action == "set":
            key = args.get("key")
            value = args.get("value")
            
            if not key or not value:
                return CallToolResponse(
                    content=[TextContent(type="text", text="Error: Both 'key' and 'value' are required for set action")]
                )
            
            # Handle special keys
            if key == "api-token":
                key = "api_token"
            elif key == "org_id":
                try:
                    value = int(value)
                except ValueError:
                    return CallToolResponse(
                        content=[TextContent(type="text", text="Error: org_id must be a number")]
                    )
            
            self.config[key] = value
            self._save_config(self.config)
            
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Set {key} = {value}")]
            )
        
        elif action == "get":
            key = args.get("key")
            if not key:
                return CallToolResponse(
                    content=[TextContent(type="text", text="Error: 'key' is required for get action")]
                )
            
            if key == "api-token":
                key = "api_token"
            
            value = self.config.get(key, "Not set")
            
            # Mask sensitive values
            if key == "api_token" and value != "Not set":
                value = f"{value[:8]}...{value[-4:]}"
            
            return CallToolResponse(
                content=[TextContent(type="text", text=f"{key} = {value}")]
            )
        
        elif action == "list":
            config_display = {}
            for key, value in self.config.items():
                if key == "api_token" and value:
                    config_display[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    config_display[key] = value
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(config_display, indent=2))]
            )
        
        else:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Unknown config action: {action}")]
            )
    
    async def _handle_list(self, args: Dict[str, Any]) -> CallToolResponse:
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
                                except Exception:
                                    pass
                            
                            if isinstance(metadata, dict):
                                task_info["repo"] = metadata.get("repo")
                                task_info["task_type"] = metadata.get("task_type")
                                task_info["branch"] = metadata.get("branch")
                                task_info["pr"] = metadata.get("pr")
                    except Exception:
                        pass
                    
                    # Apply filters
                    if status_filter and task_info["status"] != status_filter:
                        continue
                    if repo_filter and task_info.get("repo") != repo_filter:
                        continue
                    
                    results.append(task_info)
                
                return CallToolResponse(
                    content=[TextContent(type="text", text=json.dumps(results, indent=2))]
                )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error listing agent runs: {str(e)}")]
            )

async def main():
    """Main entry point for the MCP server"""
    server_instance = CodegenMCPServer()
    await server_instance.start()

if __name__ == "__main__":
    asyncio.run(main())
