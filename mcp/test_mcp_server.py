#!/usr/bin/env python3
"""
Test script for the Codegen API MCP Server.

This script tests the MCP server by sending various commands and verifying the responses.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.stdio import stdio_client
from codegenapi_server import CodegenMCPServer

async def test_mcp_server():
    """Test the MCP server with various commands"""
    # Get API token and org ID from environment variables
    api_token = os.environ.get("CODEGEN_API_TOKEN")
    org_id = os.environ.get("CODEGEN_ORG_ID")
    
    if not api_token:
        print("Error: CODEGEN_API_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not org_id:
        print("Error: CODEGEN_ORG_ID environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        org_id = int(org_id)
    except ValueError:
        print(f"Error: CODEGEN_ORG_ID must be an integer, got '{org_id}'", file=sys.stderr)
        sys.exit(1)
    
    # Create a temporary directory for the server's stdin/stdout
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the server
        server = CodegenMCPServer(api_token=api_token, org_id=org_id, debug=True)
        
        # Start the server in a separate task
        server_task = asyncio.create_task(start_server(server, temp_dir))
        
        # Wait for the server to start
        await asyncio.sleep(1)
        
        # Connect to the server
        client = await connect_client(temp_dir)
        
        # Test list_tools
        print("\n=== Testing list_tools ===")
        response = await client.list_tools()
        print(f"Available tools: {len(response.tools)}")
        for tool in response.tools:
            print(f"- {tool.name}: {tool.description}")
        
        # Test codegenapi_list
        print("\n=== Testing codegenapi_list ===")
        response = await client.call_tool(
            "codegenapi_list",
            {"limit": 5}
        )
        print(response.content[0].text)
        
        # Test codegenapi_get_current_user
        print("\n=== Testing codegen_get_current_user ===")
        response = await client.call_tool(
            "codegen_get_current_user",
            {}
        )
        print(response.content[0].text)
        
        # Test codegen_get_organizations
        print("\n=== Testing codegen_get_organizations ===")
        response = await client.call_tool(
            "codegen_get_organizations",
            {}
        )
        print(response.content[0].text)
        
        # Cancel the server task
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

async def start_server(server, temp_dir):
    """Start the MCP server with stdin/stdout redirected to files"""
    # Create files for stdin/stdout
    stdin_path = Path(temp_dir) / "stdin"
    stdout_path = Path(temp_dir) / "stdout"
    
    # Create the files
    stdin_path.touch()
    stdout_path.touch()
    
    # Open the files
    with open(stdin_path, "rb") as stdin, open(stdout_path, "wb") as stdout:
        # Run the server
        await server.server.run(
            stdin,
            stdout,
            server.server.create_initialization_options()
        )

async def connect_client(temp_dir):
    """Connect to the MCP server using the stdio client"""
    # Create files for stdin/stdout
    stdin_path = Path(temp_dir) / "stdin"
    stdout_path = Path(temp_dir) / "stdout"
    
    # Open the files
    stdin = open(stdout_path, "rb")
    stdout = open(stdin_path, "wb")
    
    # Connect to the server
    client = await stdio_client(stdin, stdout)
    
    return client

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
