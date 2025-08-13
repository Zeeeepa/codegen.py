#!/usr/bin/env python3
"""
Codegen API MCP Server

This module implements a Model Context Protocol (MCP) server for the Codegen API.
It exposes Codegen API functionality as MCP tools that can be called by AI assistants.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import MCP server components
from mcp.server import FastMCP
from mcp_types import CallToolResponse, TextContent

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Codegen API client
from codegenapi import CodegenClient

class CodegenMCPServer:
    """MCP server for Codegen API"""
    
    def __init__(self, api_token: str, org_id: int, debug: bool = False):
        """Initialize the Codegen MCP server"""
        # Initialize the Codegen API client
        self.client = CodegenClient(api_token=api_token, org_id=org_id)
        self.debug = debug
        
        # Initialize the MCP server
        self.server = FastMCP()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Codegen API tools with the MCP server"""
        # New task tool
        self.server.register_tool(
            name="codegenapi_new",
            func=self._handle_new,
            description="Create a new Codegen task",
            parameters={
                "repo": {"type": "string", "description": "Repository URL"},
                "task": {"type": "string", "description": "Task type (CODE_REVIEW, BUG_FIX, FEATURE_IMPLEMENTATION, etc.)"},
                "query": {"type": "string", "description": "Task description"},
                "branch": {"type": "string", "description": "Target branch (optional)"},
                "pr": {"type": "string", "description": "PR number (optional)"}
            }
        )
        
        # Resume task tool
        self.server.register_tool(
            name="codegenapi_resume",
            func=self._handle_resume,
            description="Resume an existing Codegen task",
            parameters={
                "task_id": {"type": "string", "description": "Task ID to resume"},
                "message": {"type": "string", "description": "Additional message (optional)"}
            }
        )
        
        # List tasks tool
        self.server.register_tool(
            name="codegenapi_list",
            func=self._handle_list,
            description="List Codegen tasks",
            parameters={
                "status": {"type": "string", "description": "Filter by status (running, completed, failed, etc.)"},
                "repo": {"type": "string", "description": "Filter by repository URL"},
                "limit": {"type": "integer", "description": "Maximum number of tasks to return"}
            }
        )
        
        # Get task details tool
        self.server.register_tool(
            name="codegenapi_get",
            func=self._handle_get,
            description="Get details of a Codegen task",
            parameters={
                "task_id": {"type": "string", "description": "Task ID to get details for"},
                "verbose": {"type": "boolean", "description": "Include verbose details"}
            }
        )
        
        # Cancel task tool
        self.server.register_tool(
            name="codegenapi_cancel",
            func=self._handle_cancel,
            description="Cancel a running Codegen task",
            parameters={
                "task_id": {"type": "string", "description": "Task ID to cancel"},
                "reason": {"type": "string", "description": "Reason for cancellation (optional)"}
            }
        )
    
    def _handle_new(self, params: Dict[str, Any]) -> CallToolResponse:
        """Handle the codegenapi_new tool"""
        try:
            # Extract parameters
            repo = params.get("repo")
            task_type = params.get("task")
            query = params.get("query")
            branch = params.get("branch")
            pr = params.get("pr")
            
            if self.debug:
                print(f"Creating task: repo={repo}, task={task_type}, query={query}, branch={branch}, pr={pr}", file=sys.stderr)
            
            # Call the Codegen API
            result = self.client.create_task(
                repo=repo,
                task_type=task_type,
                query=query,
                branch=branch,
                pr=pr
            )
            
            # Return the result
            return CallToolResponse(
                content=[TextContent(text=f"Created task: {result['task_id']}")]
            )
        except Exception as e:
            if self.debug:
                print(f"Error creating task: {str(e)}", file=sys.stderr)
            return CallToolResponse(
                content=[TextContent(text=f"Error creating task: {str(e)}")]
            )
    
    def _handle_resume(self, params: Dict[str, Any]) -> CallToolResponse:
        """Handle the codegenapi_resume tool"""
        try:
            # Extract parameters
            task_id = params.get("task_id")
            message = params.get("message")
            
            if self.debug:
                print(f"Resuming task: task_id={task_id}, message={message}", file=sys.stderr)
            
            # Call the Codegen API
            result = self.client.resume_task(
                task_id=task_id,
                message=message
            )
            
            # Return the result
            return CallToolResponse(
                content=[TextContent(text=f"Resumed task: {task_id}")]
            )
        except Exception as e:
            if self.debug:
                print(f"Error resuming task: {str(e)}", file=sys.stderr)
            return CallToolResponse(
                content=[TextContent(text=f"Error resuming task: {str(e)}")]
            )
    
    def _handle_list(self, params: Dict[str, Any]) -> CallToolResponse:
        """Handle the codegenapi_list tool"""
        try:
            # Extract parameters
            status = params.get("status")
            repo = params.get("repo")
            limit = params.get("limit", 10)
            
            if self.debug:
                print(f"Listing tasks: status={status}, repo={repo}, limit={limit}", file=sys.stderr)
            
            # Call the Codegen API
            result = self.client.list_tasks(
                status=status,
                repo=repo,
                limit=limit
            )
            
            # Format the result
            tasks_text = "\n".join([
                f"Task {task['task_id']}: {task['status']} - {task['query'][:50]}..."
                for task in result['tasks']
            ])
            
            # Return the result
            return CallToolResponse(
                content=[TextContent(text=f"Tasks:\n{tasks_text}")]
            )
        except Exception as e:
            if self.debug:
                print(f"Error listing tasks: {str(e)}", file=sys.stderr)
            return CallToolResponse(
                content=[TextContent(text=f"Error listing tasks: {str(e)}")]
            )
    
    def _handle_get(self, params: Dict[str, Any]) -> CallToolResponse:
        """Handle the codegenapi_get tool"""
        try:
            # Extract parameters
            task_id = params.get("task_id")
            verbose = params.get("verbose", False)
            
            if self.debug:
                print(f"Getting task details: task_id={task_id}, verbose={verbose}", file=sys.stderr)
            
            # Call the Codegen API
            result = self.client.get_task(
                task_id=task_id,
                verbose=verbose
            )
            
            # Format the result
            task_details = f"Task {result['task_id']}:\n"
            task_details += f"Status: {result['status']}\n"
            task_details += f"Query: {result['query']}\n"
            task_details += f"Created: {result['created_at']}\n"
            
            if verbose and 'details' in result:
                task_details += f"\nDetails: {result['details']}"
            
            # Return the result
            return CallToolResponse(
                content=[TextContent(text=task_details)]
            )
        except Exception as e:
            if self.debug:
                print(f"Error getting task details: {str(e)}", file=sys.stderr)
            return CallToolResponse(
                content=[TextContent(text=f"Error getting task details: {str(e)}")]
            )
    
    def _handle_cancel(self, params: Dict[str, Any]) -> CallToolResponse:
        """Handle the codegenapi_cancel tool"""
        try:
            # Extract parameters
            task_id = params.get("task_id")
            reason = params.get("reason")
            
            if self.debug:
                print(f"Cancelling task: task_id={task_id}, reason={reason}", file=sys.stderr)
            
            # Call the Codegen API
            result = self.client.cancel_task(
                task_id=task_id,
                reason=reason
            )
            
            # Return the result
            return CallToolResponse(
                content=[TextContent(text=f"Cancelled task: {task_id}")]
            )
        except Exception as e:
            if self.debug:
                print(f"Error cancelling task: {str(e)}", file=sys.stderr)
            return CallToolResponse(
                content=[TextContent(text=f"Error cancelling task: {str(e)}")]
            )
    
    def start(self):
        """Start the MCP server"""
        if self.debug:
            print("Starting Codegen API MCP server...", file=sys.stderr)
        self.server.start()


def main():
    """Main entry point for the MCP server"""
    # Get API token from environment
    api_token = os.environ.get("CODEGEN_API_TOKEN")
    if not api_token:
        print("Error: CODEGEN_API_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    # Get org ID from environment
    org_id_str = os.environ.get("CODEGEN_ORG_ID")
    if not org_id_str:
        print("Error: CODEGEN_ORG_ID environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    try:
        org_id = int(org_id_str)
    except ValueError:
        print(f"Error: CODEGEN_ORG_ID must be an integer, got '{org_id_str}'", file=sys.stderr)
        sys.exit(1)
    
    # Check for debug flag
    debug = os.environ.get("CODEGEN_DEBUG", "").lower() in ("1", "true", "yes")
    
    # Create and start the MCP server
    server = CodegenMCPServer(api_token=api_token, org_id=org_id, debug=debug)
    server.start()


if __name__ == "__main__":
    main()

