#!/usr/bin/env python3
"""
Mock Codegen API MCP Server for demonstration purposes

This is a simplified version of the server that doesn't require real API credentials.
It demonstrates the command structure and usage patterns.
"""

import argparse
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import MCP server components
try:
    from mcp.server import Server, Tool, CallToolResponse, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("Error: MCP package not installed. Run 'pip install mcp'", file=sys.stderr)
    sys.exit(1)

class MockCodegenServer:
    """Mock implementation of the Codegen API MCP server"""
    
    def __init__(self, debug: bool = False):
        """Initialize the mock server"""
        self.server = Server("codegenapi")
        self.debug = debug
        
        # Register tools
        for tool in self._register_tools():
            self.server.register_tool(tool)
    
    async def start(self):
        """Start the MCP server"""
        if self.debug:
            print("Starting Mock Codegen API MCP server in debug mode", file=sys.stderr)
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def _register_tools(self) -> List[Tool]:
        """Register all MCP tools and return the list of tools"""
        tools = [
            # Core commands
            Tool(
                name="codegenapi_new",
                description="Start a new agent run",
                parameters={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository URL or name"
                        },
                        "task": {
                            "type": "string",
                            "description": "Task type (e.g., CREATE_PLAN, FEATURE_IMPLEMENTATION, BUG_FIX)"
                        },
                        "query": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name (optional)"
                        },
                        "pr": {
                            "type": "integer",
                            "description": "PR number (optional)"
                        }
                    },
                    "required": ["repo", "task", "query"]
                },
                function=self.handle_new
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
                        "query": {
                            "type": "string",
                            "description": "Additional instructions"
                        },
                        "task": {
                            "type": "string",
                            "description": "Task type for the resume operation (optional)"
                        }
                    },
                    "required": ["agent_run_id", "query"]
                },
                function=self.handle_resume
            ),
            Tool(
                name="codegenapi_list",
                description="List agent runs",
                parameters={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status (pending, running, completed, failed, cancelled, paused)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of runs to return",
                            "default": 10
                        },
                        "repo": {
                            "type": "string",
                            "description": "Filter by repository"
                        }
                    }
                },
                function=self.handle_list
            ),
            Tool(
                name="codegenapi_config",
                description="Manage configuration settings",
                parameters={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform (set, get, list)",
                            "enum": ["set", "get", "list"]
                        },
                        "key": {
                            "type": "string",
                            "description": "Configuration key (required for set/get)"
                        },
                        "value": {
                            "type": "string",
                            "description": "Configuration value (required for set)"
                        }
                    },
                    "required": ["action"]
                },
                function=self.handle_config
            )
        ]
        
        return tools
    
    async def handle_new(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle codegenapi_new command"""
        repo = args.get("repo", "")
        task = args.get("task", "")
        query = args.get("query", "")
        branch = args.get("branch")
        pr = args.get("pr")
        
        if self.debug:
            print(f"DEBUG: New agent run: repo={repo}, task={task}, query={query}", file=sys.stderr)
        
        # Simulate creating a new agent run
        agent_run_id = 12345
        
        result = {
            "success": True,
            "agent_run_id": agent_run_id,
            "status": "running",
            "message": f"Started new agent run for {repo}",
            "details": {
                "repo": repo,
                "task": task,
                "query": query,
                "branch": branch,
                "pr": pr
            }
        }
        
        return CallToolResponse(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def handle_resume(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle codegenapi_resume command"""
        agent_run_id = args.get("agent_run_id")
        query = args.get("query", "")
        task = args.get("task")
        
        if self.debug:
            print(f"DEBUG: Resume agent run: id={agent_run_id}, query={query}", file=sys.stderr)
        
        # Simulate resuming an agent run
        result = {
            "success": True,
            "agent_run_id": agent_run_id,
            "status": "running",
            "message": f"Resumed agent run {agent_run_id}",
            "details": {
                "query": query,
                "task": task
            }
        }
        
        return CallToolResponse(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def handle_list(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle codegenapi_list command"""
        status = args.get("status")
        limit = args.get("limit", 10)
        repo = args.get("repo")
        
        if self.debug:
            print(f"DEBUG: List agent runs: status={status}, limit={limit}, repo={repo}", file=sys.stderr)
        
        # Simulate listing agent runs
        runs = [
            {
                "id": 12345,
                "status": "running",
                "repo": "user/repo",
                "task": "FEATURE_IMPLEMENTATION",
                "query": "Implement JWT-based authentication",
                "created_at": "2023-08-13T01:30:00Z"
            },
            {
                "id": 12344,
                "status": "completed",
                "repo": "user/repo",
                "task": "BUG_FIX",
                "query": "Fix login form validation",
                "created_at": "2023-08-12T22:15:00Z"
            },
            {
                "id": 12343,
                "status": "failed",
                "repo": "user/other-repo",
                "task": "CREATE_PLAN",
                "query": "Create a plan for refactoring",
                "created_at": "2023-08-12T18:45:00Z"
            }
        ]
        
        # Apply filters
        if status:
            runs = [run for run in runs if run["status"] == status]
        
        if repo:
            runs = [run for run in runs if run["repo"] == repo]
        
        # Apply limit
        runs = runs[:limit]
        
        result = {
            "success": True,
            "total": len(runs),
            "items": runs
        }
        
        return CallToolResponse(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def handle_config(self, args: Dict[str, Any]) -> CallToolResponse:
        """Handle codegenapi_config command"""
        action = args.get("action")
        key = args.get("key")
        value = args.get("value")
        
        if self.debug:
            print(f"DEBUG: Config: action={action}, key={key}, value={value}", file=sys.stderr)
        
        if action == "set":
            if not key or not value:
                return CallToolResponse(
                    content=[TextContent(type="text", text="Error: key and value are required for 'set' action")]
                )
            
            result = {
                "success": True,
                "message": f"Set {key} to {value}",
                "key": key,
                "value": value if key != "api-token" else "********"
            }
        
        elif action == "get":
            if not key:
                return CallToolResponse(
                    content=[TextContent(type="text", text="Error: key is required for 'get' action")]
                )
            
            result = {
                "success": True,
                "key": key,
                "value": "mock-value" if key != "api-token" else "********"
            }
        
        elif action == "list":
            result = {
                "success": True,
                "config": {
                    "api-token": "********",
                    "org-id": "12345",
                    "api.base-url": "https://api.codegen.com"
                }
            }
        
        else:
            return CallToolResponse(
                content=[TextContent(type="text", text=f"Error: Unknown action '{action}'")]
            )
        
        return CallToolResponse(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the Mock Codegen API MCP server")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging",
    )
    return parser.parse_args()

def main():
    """Main entry point for the mock MCP server"""
    args = parse_args()
    
    # Create the MCP server
    server = MockCodegenServer(debug=args.debug)
    
    # Start the server
    print("Starting Mock Codegen API MCP server...", file=sys.stderr)
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
