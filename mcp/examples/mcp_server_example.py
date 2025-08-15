#!/usr/bin/env python3
"""
Example script demonstrating how to use the Codegen API MCP Server
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Set environment variables for the MCP server
os.environ["CODEGEN_API_TOKEN"] = "your_api_token"  # Replace with your actual token
os.environ["CODEGEN_ORG_ID"] = "your_org_id"  # Replace with your actual org ID

# Path to the MCP server
SERVER_PATH = Path(__file__).parent.parent / "server.py"

def send_jsonrpc_request(method, params=None):
    """Send a JSON-RPC request to the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, str(SERVER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the request
    request_str = json.dumps(request) + "\n"
    process.stdin.write(request_str)
    process.stdin.flush()
    
    # Read the response
    response_str = process.stdout.readline()
    process.terminate()
    
    # Parse the response
    response = json.loads(response_str)
    return response

def list_tools():
    """List all available tools"""
    response = send_jsonrpc_request("listTools")
    print("Available tools:")
    for tool in response["result"]["tools"]:
        print(f"- {tool['name']}: {tool['description']}")
    print()

def create_new_agent_run():
    """Create a new agent run"""
    params = {
        "name": "codegenapi_new",
        "arguments": {
            "repo": "Zeeeepa/codegen.py",
            "task": "FEATURE_IMPLEMENTATION",
            "query": "Implement a new feature to improve code quality",
            "branch": "feature/code-quality-improvements"
        }
    }
    
    response = send_jsonrpc_request("callTool", params)
    content = json.loads(response["result"]["content"][0]["text"])
    
    print("Created new agent run:")
    print(f"- Agent Run ID: {content.get('agent_run_id')}")
    print(f"- Status: {content.get('status')}")
    print(f"- Web URL: {content.get('web_url')}")
    print(f"- Message: {content.get('message')}")
    print()
    
    return content.get("agent_run_id")

def resume_agent_run(agent_run_id):
    """Resume an existing agent run"""
    params = {
        "name": "codegenapi_resume",
        "arguments": {
            "agent_run_id": agent_run_id,
            "query": "Please also add comprehensive error handling"
        }
    }
    
    response = send_jsonrpc_request("callTool", params)
    content = json.loads(response["result"]["content"][0]["text"])
    
    print("Resumed agent run:")
    print(f"- Agent Run ID: {content.get('agent_run_id')}")
    print(f"- Status: {content.get('status')}")
    print(f"- Message: {content.get('message')}")
    print()

def list_agent_runs():
    """List recent agent runs"""
    params = {
        "name": "codegenapi_list",
        "arguments": {
            "status": "running",
            "limit": 5
        }
    }
    
    response = send_jsonrpc_request("callTool", params)
    content = json.loads(response["result"]["content"][0]["text"])
    
    print("Recent agent runs:")
    for run in content.get("runs", []):
        print(f"- ID: {run.get('id')}, Status: {run.get('status')}, Task: {run.get('task')}")
    print()

def main():
    """Main function"""
    print("Codegen API MCP Server Example\n")
    
    # List available tools
    list_tools()
    
    # Create a new agent run
    agent_run_id = create_new_agent_run()
    
    # Resume the agent run
    if agent_run_id:
        resume_agent_run(agent_run_id)
    
    # List recent agent runs
    list_agent_runs()

if __name__ == "__main__":
    main()
