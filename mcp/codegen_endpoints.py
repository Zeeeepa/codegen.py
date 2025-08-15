#!/usr/bin/env python3
"""
Codegen API Endpoints Implementation

This module implements the 9 API endpoints for the Codegen API MCP server:
1. Users
   - GET Get Users
   - GET Get User
   - GET Get Current User Info

2. Agents
   - POST Create Agent Run
   - GET Get Agent Run
   - GET List Agent Runs
   - POST Resume Agent Run

3. Organizations
   - GET Get Organizations

4. Agents-Alpha
   - GET Get Agent Run Logs
"""

import json
import sys
from typing import Any, Dict, List, Optional

from mcp_types import CallToolResponse, TextContent, Tool

# Import the codegen API
try:
    from codegen_api import Agent, CodegenClient, ClientConfig
except ImportError as e:
    print(f"Error importing codegen_api: {e}", file=sys.stderr)
    sys.exit(1)

class CodegenEndpoints:
    """Implementation of Codegen API endpoints for MCP server"""
    
    def __init__(self, api_token: str, org_id: Optional[int] = None):
        """Initialize the endpoints with API token and optional org ID"""
        self.config = ClientConfig(api_token=api_token)
        if org_id:
            self.config.org_id = str(org_id)
        
        self.client = CodegenClient(self.config)
        self.agent = Agent(token=api_token, org_id=str(org_id) if org_id else None)
    
    def register_tools(self) -> List[Tool]:
        """Register all endpoint tools"""
        return [
            # Users endpoints
            Tool(
                name="codegen_get_users",
                description="Get a list of users",
                parameters={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number (1-indexed)",
                            "default": 1
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of users per page",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="codegen_get_user",
                description="Get a specific user by ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID to retrieve"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            Tool(
                name="codegen_get_current_user",
                description="Get information about the current authenticated user",
                parameters={
                    "type": "object",
                    "properties": {}
                }
            ),
            
            # Agents endpoints
            Tool(
                name="codegen_create_agent_run",
                description="Create a new agent run",
                parameters={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to send to the agent"
                        },
                        "images": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Optional list of image URLs to include with the prompt"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata to associate with the agent run"
                        },
                        "wait_for_completion": {
                            "type": "boolean",
                            "description": "Whether to wait for the agent run to complete",
                            "default": False
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Timeout in seconds when waiting for completion",
                            "default": 300
                        }
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="codegen_get_agent_run",
                description="Get details of a specific agent run",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_run_id": {
                            "type": "integer",
                            "description": "Agent run ID to retrieve"
                        }
                    },
                    "required": ["agent_run_id"]
                }
            ),
            Tool(
                name="codegen_list_agent_runs",
                description="List agent runs with optional filtering",
                parameters={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number (1-indexed)",
                            "default": 1
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of agent runs per page",
                            "default": 10
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status (pending, running, completed, failed, cancelled, paused)",
                            "enum": ["pending", "running", "completed", "failed", "cancelled", "paused"]
                        }
                    }
                }
            ),
            Tool(
                name="codegen_resume_agent_run",
                description="Resume a paused agent run",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_run_id": {
                            "type": "integer",
                            "description": "Agent run ID to resume"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to send to the agent"
                        },
                        "images": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Optional list of image URLs to include with the prompt"
                        },
                        "wait_for_completion": {
                            "type": "boolean",
                            "description": "Whether to wait for the agent run to complete",
                            "default": False
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Timeout in seconds when waiting for completion",
                            "default": 300
                        }
                    },
                    "required": ["agent_run_id", "prompt"]
                }
            ),
            
            # Organizations endpoint
            Tool(
                name="codegen_get_organizations",
                description="Get a list of organizations",
                parameters={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number (1-indexed)",
                            "default": 1
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of organizations per page",
                            "default": 10
                        }
                    }
                }
            ),
            
            # Agents-Alpha endpoint
            Tool(
                name="codegen_get_agent_run_logs",
                description="Get logs for a specific agent run",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_run_id": {
                            "type": "integer",
                            "description": "Agent run ID to get logs for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of logs to return",
                            "default": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (1-indexed)",
                            "default": 1
                        }
                    },
                    "required": ["agent_run_id"]
                }
            )
        ]
    
    async def handle_get_users(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET Users endpoint"""
        # Note: Pagination parameters are kept in the API but not used
        # as the client API doesn't support them yet
        
        try:
            # The API requires org_id parameter
            users = self.client.get_users(org_id=int(self.agent.org_id))
            
            result = {
                "total": users.total,
                "page": users.page,
                "size": users.size,
                "pages": users.pages,
                "items": [
                    {
                        "id": user.id,
                        "email": user.email,
                        "github_username": user.github_username,
                        "github_user_id": user.github_user_id,
                        "avatar_url": user.avatar_url,
                        "full_name": user.full_name
                    }
                    for user in users.items
                ]
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting users: {str(e)}")]
            )
    
    async def handle_get_user(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET User endpoint"""
        user_id = args.get("user_id")
        
        if not user_id:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: user_id is required")]
            )
        
        try:
            # The API requires org_id parameter
            user = self.client.get_user(org_id=int(self.agent.org_id), user_id=user_id)
            
            result = {
                "id": user.id,
                "email": user.email,
                "github_username": user.github_username,
                "github_user_id": user.github_user_id,
                "avatar_url": user.avatar_url,
                "full_name": user.full_name
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting user: {str(e)}")]
            )
    
    async def handle_get_current_user(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET Current User Info endpoint"""
        try:
            user = self.client.get_current_user()
            
            result = {
                "id": user.id,
                "email": user.email,
                "github_username": user.github_username,
                "github_user_id": user.github_user_id,
                "avatar_url": user.avatar_url,
                "full_name": user.full_name
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting current user: {str(e)}")]
            )
    
    async def handle_create_agent_run(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle POST Create Agent Run endpoint"""
        prompt = args.get("prompt")
        images = args.get("images")
        metadata = args.get("metadata")
        wait_for_completion = args.get("wait_for_completion", False)
        timeout = args.get("timeout", 300)
        
        if not prompt:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: prompt is required")]
            )
        
        try:
            # Create the agent run
            agent_run = self.client.create_agent_run(
                org_id=int(self.agent.org_id),
                prompt=prompt,
                images=images,
                metadata=metadata
            )
            
            # Create a Task object for easier handling
            task = self.agent.get_task(agent_run.id)
            
            result = {
                "id": agent_run.id,
                "status": agent_run.status,
                "web_url": agent_run.web_url,
                "created_at": agent_run.created_at
            }
            
            # Wait for completion if requested
            if wait_for_completion:
                try:
                    completed_task = task.wait_for_completion(timeout=timeout)
                    result["status"] = completed_task.status
                    
                    if completed_task.result:
                        result["result"] = completed_task.result
                    
                    if completed_task.github_pull_requests:
                        result["github_pull_requests"] = [
                            {
                                "id": pr.id,
                                "title": pr.title,
                                "url": pr.url,
                                "created_at": pr.created_at
                            }
                            for pr in completed_task.github_pull_requests
                        ]
                except Exception as e:
                    result["wait_error"] = str(e)
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error creating agent run: {str(e)}")]
            )
    
    async def handle_get_agent_run(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET Agent Run endpoint"""
        agent_run_id = args.get("agent_run_id")
        
        if not agent_run_id:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: agent_run_id is required")]
            )
        
        try:
            agent_run = self.client.get_agent_run(int(self.agent.org_id), agent_run_id)
            
            result = {
                "id": agent_run.id,
                "organization_id": agent_run.organization_id,
                "status": agent_run.status,
                "created_at": agent_run.created_at,
                "web_url": agent_run.web_url,
                "result": agent_run.result,
                "source_type": agent_run.source_type.value if agent_run.source_type else None,
                "metadata": agent_run.metadata
            }
            
            if agent_run.github_pull_requests:
                result["github_pull_requests"] = [
                    {
                        "id": pr.id,
                        "title": pr.title,
                        "url": pr.url,
                        "created_at": pr.created_at
                    }
                    for pr in agent_run.github_pull_requests
                ]
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting agent run: {str(e)}")]
            )
    
    async def handle_list_agent_runs(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET List Agent Runs endpoint"""
        # Note: Pagination and status parameters are kept in the API but not used
        # as the client API doesn't support them yet
        
        try:
            # The API doesn't support status parameter
            agent_runs = self.client.list_agent_runs(
                org_id=int(self.agent.org_id)
            )
            
            result = {
                "total": agent_runs.total,
                "page": agent_runs.page,
                "size": agent_runs.size,
                "pages": agent_runs.pages,
                "items": [
                    {
                        "id": run.id,
                        "status": run.status,
                        "created_at": run.created_at,
                        "web_url": run.web_url,
                        "source_type": run.source_type.value if run.source_type else None,
                        "metadata": run.metadata
                    }
                    for run in agent_runs.items
                ]
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error listing agent runs: {str(e)}")]
            )
    
    async def handle_resume_agent_run(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle POST Resume Agent Run endpoint"""
        agent_run_id = args.get("agent_run_id")
        prompt = args.get("prompt")
        images = args.get("images")
        wait_for_completion = args.get("wait_for_completion", False)
        timeout = args.get("timeout", 300)
        
        if not agent_run_id:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: agent_run_id is required")]
            )
        
        if not prompt:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: prompt is required")]
            )
        
        try:
            # Get the task object
            task = self.agent.get_task(agent_run_id)
            
            # Resume the task
            agent_run = task.resume(prompt=prompt, images=images)
            
            result = {
                "id": agent_run.id,
                "status": agent_run.status,
                "web_url": agent_run.web_url
            }
            
            # Wait for completion if requested
            if wait_for_completion:
                try:
                    completed_task = task.wait_for_completion(timeout=timeout)
                    result["status"] = completed_task.status
                    
                    if completed_task.result:
                        result["result"] = completed_task.result
                    
                    if completed_task.github_pull_requests:
                        result["github_pull_requests"] = [
                            {
                                "id": pr.id,
                                "title": pr.title,
                                "url": pr.url,
                                "created_at": pr.created_at
                            }
                            for pr in completed_task.github_pull_requests
                        ]
                except Exception as e:
                    result["wait_error"] = str(e)
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error resuming agent run: {str(e)}")]
            )
    
    async def handle_get_organizations(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET Organizations endpoint"""
        # Note: Pagination parameters are kept in the API but not used
        # as the client API doesn't support them yet
        
        try:
            # Note: The API might not support pagination parameters
            organizations = self.client.get_organizations()
            
            result = {
                "total": organizations.total,
                "page": organizations.page,
                "size": organizations.size,
                "pages": organizations.pages,
                "items": [
                    {
                        "id": org.id,
                        "name": org.name,
                        "settings": {
                            "enable_pr_creation": org.settings.enable_pr_creation,
                            "enable_rules_detection": org.settings.enable_rules_detection
                        }
                    }
                    for org in organizations.items
                ]
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting organizations: {str(e)}")]
            )
    
    async def handle_get_agent_run_logs(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle GET Agent Run Logs endpoint"""
        agent_run_id = args.get("agent_run_id")
        limit = args.get("limit", 100)
        # Note: page parameter is currently not used by the get_logs method
        # but is kept for future pagination support
        
        if not agent_run_id:
            return CallToolResponse(
                content=[TextContent(type="text", text="Error: agent_run_id is required")]
            )
        
        try:
            # Get the task object
            task = self.agent.get_task(agent_run_id)
            
            # Get the logs
            logs_response = task.get_logs(limit=limit)
            
            result = {
                "id": logs_response.id,
                "organization_id": logs_response.organization_id,
                "status": logs_response.status,
                "created_at": logs_response.created_at,
                "web_url": logs_response.web_url,
                "result": logs_response.result,
                "total_logs": logs_response.total_logs,
                "page": logs_response.page,
                "size": logs_response.size,
                "pages": logs_response.pages,
                "logs": [
                    {
                        "agent_run_id": log.agent_run_id,
                        "created_at": log.created_at,
                        "message_type": log.message_type,
                        "thought": log.thought,
                        "tool_name": log.tool_name,
                        "tool_input": log.tool_input,
                        "observation": log.observation
                    }
                    for log in logs_response.logs
                ]
            }
            
            return CallToolResponse(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error getting agent run logs: {str(e)}")]
            )
