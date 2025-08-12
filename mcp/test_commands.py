#!/usr/bin/env python3
"""
Test script to run commands against the Codegen MCP Server
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# MCP client for testing
async def run_mcp_command(server_process, command, args):
    """Run a command against the MCP server"""
    # Format the request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "capabilities": {},
            "initializationOptions": {
                "server_name": "codegenapi",
                "server_version": "0.1.0"
            }
        }
    }
    
    # Send initialization request
    request_str = json.dumps(request)
    content_length = len(request_str)
    header = f"Content-Length: {content_length}\r\n\r\n"
    
    server_process.stdin.write(header.encode() + request_str.encode())
    await server_process.stdin.drain()
    
    # Read initialization response
    header = await server_process.stdout.readline()
    content_length = int(header.decode().strip().split(": ")[1])
    await server_process.stdout.readline()  # Empty line
    response_data = await server_process.stdout.read(content_length)
    response = json.loads(response_data.decode())
    
    # List tools
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "listTools",
        "params": {}
    }
    
    request_str = json.dumps(list_tools_request)
    content_length = len(request_str)
    header = f"Content-Length: {content_length}\r\n\r\n"
    
    server_process.stdin.write(header.encode() + request_str.encode())
    await server_process.stdin.drain()
    
    # Read list tools response
    header = await server_process.stdout.readline()
    content_length = int(header.decode().strip().split(": ")[1])
    await server_process.stdout.readline()  # Empty line
    response_data = await server_process.stdout.read(content_length)
    tools_response = json.loads(response_data.decode())
    
    # Call the tool
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "callTool",
        "params": {
            "name": command,
            "arguments": args
        }
    }
    
    request_str = json.dumps(call_tool_request)
    content_length = len(request_str)
    header = f"Content-Length: {content_length}\r\n\r\n"
    
    server_process.stdin.write(header.encode() + request_str.encode())
    await server_process.stdin.drain()
    
    # Read call tool response
    header = await server_process.stdout.readline()
    content_length = int(header.decode().strip().split(": ")[1])
    await server_process.stdout.readline()  # Empty line
    response_data = await server_process.stdout.read(content_length)
    call_response = json.loads(response_data.decode())
    
    return call_response

async def main():
    """Run test commands against the MCP server"""
    print("🧪 Testing Codegen MCP Server Commands\n")
    
    # Start the server process
    print("Starting MCP server...")
    server_process = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(Path(__file__).parent)
    )
    
    try:
        # Wait for server to start
        print("Waiting for server to initialize...")
        await asyncio.sleep(1)
        
        # Test config command
        print("\n📝 Testing codegenapi_config command:")
        config_args = {
            "action": "set",
            "key": "api-token",
            "value": "test_token_12345"
        }
        config_response = await run_mcp_command(server_process, "codegenapi_config", config_args)
        print(f"Response: {json.dumps(config_response, indent=2)}")
        
        # Test list config command
        print("\n📋 Testing codegenapi_config list command:")
        list_config_args = {
            "action": "list"
        }
        list_config_response = await run_mcp_command(server_process, "codegenapi_config", list_config_args)
        print(f"Response: {json.dumps(list_config_response, indent=2)}")
        
        # Test new command
        print("\n🆕 Testing codegenapi_new command:")
        new_args = {
            "repo": "Zeeeepa/codegen.py",
            "task": "CREATE_PLAN",
            "query": "Create a test plan for demonstration purposes"
        }
        new_response = await run_mcp_command(server_process, "codegenapi_new", new_args)
        print(f"Response: {json.dumps(new_response, indent=2)}")
        
        # Extract agent_run_id for resume test
        agent_run_id = None
        try:
            result_text = new_response.get("result", {}).get("content", [{}])[0].get("text", "{}")
            result_json = json.loads(result_text)
            agent_run_id = result_json.get("agent_run_id")
        except:
            print("Could not extract agent_run_id from response")
        
        if agent_run_id:
            # Test resume command
            print("\n▶️ Testing codegenapi_resume command:")
            resume_args = {
                "agent_run_id": agent_run_id,
                "query": "Please also include error handling"
            }
            resume_response = await run_mcp_command(server_process, "codegenapi_resume", resume_args)
            print(f"Response: {json.dumps(resume_response, indent=2)}")
        
        # Test list command
        print("\n📋 Testing codegenapi_list command:")
        list_args = {
            "limit": 5
        }
        list_response = await run_mcp_command(server_process, "codegenapi_list", list_args)
        print(f"Response: {json.dumps(list_response, indent=2)}")
        
        print("\n✅ All commands tested successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        # Terminate the server process
        print("\nTerminating server process...")
        server_process.terminate()
        await server_process.wait()

if __name__ == "__main__":
    asyncio.run(main())
