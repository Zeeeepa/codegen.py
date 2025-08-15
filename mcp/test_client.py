#!/usr/bin/env python3
"""
Test client for the Codegen API MCP Server

This script demonstrates how to interact with the MCP server using the MCP client.
"""

import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path

# Import MCP client
try:
    from mcp.client import Client
except ImportError:
    print("Error: MCP package not installed. Run 'pip install mcp'", file=sys.stderr)
    sys.exit(1)

async def test_client():
    """Test the MCP client with various commands"""
    # Start the mock server in a separate process
    server_process = subprocess.Popen(
        ["python", "mock_server.py", "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    await asyncio.sleep(2)
    
    # Connect to the server
    client = Client(name="codegenapi")
    
    try:
        # Test codegenapi_new
        print("\n=== Testing codegenapi_new ===")
        response = await client.call_tool(
            "codegenapi_new",
            {
                "repo": "user/repo",
                "task": "FEATURE_IMPLEMENTATION",
                "query": "Implement JWT-based authentication with refresh tokens and role-based access control",
                "branch": "feature/auth"
            }
        )
        print(response.content[0].text)
        
        # Test codegenapi_resume
        print("\n=== Testing codegenapi_resume ===")
        response = await client.call_tool(
            "codegenapi_resume",
            {
                "agent_run_id": 12345,
                "query": "Please also include error handling"
            }
        )
        print(response.content[0].text)
        
        # Test codegenapi_list
        print("\n=== Testing codegenapi_list ===")
        response = await client.call_tool(
            "codegenapi_list",
            {
                "status": "running",
                "limit": 5
            }
        )
        print(response.content[0].text)
        
        # Test codegenapi_config
        print("\n=== Testing codegenapi_config ===")
        response = await client.call_tool(
            "codegenapi_config",
            {
                "action": "list"
            }
        )
        print(response.content[0].text)
        
    finally:
        # Terminate the server process
        server_process.terminate()
        stdout, stderr = server_process.communicate()
        
        if stderr:
            print("\nServer stderr output:")
            print(stderr)

if __name__ == "__main__":
    asyncio.run(test_client())
