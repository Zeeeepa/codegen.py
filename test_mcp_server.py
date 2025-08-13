#!/usr/bin/env python3
"""
Test script for the Codegen MCP Server.

This script tests the MCP server by making direct HTTP requests to it.
"""

import os
import sys
import json
import time
import argparse
import requests
import subprocess
import threading
from typing import Dict, Any, Optional, List

# Set test credentials
TEST_API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
TEST_ORG_ID = "323"

def start_mcp_server(host: str, port: int) -> subprocess.Popen:
    """Start the MCP server in a separate process."""
    print(f"Starting MCP server on {host}:{port}")
    
    # Set environment variables for the server
    env = os.environ.copy()
    env["CODEGEN_API_TOKEN"] = TEST_API_TOKEN
    env["CODEGEN_ORG_ID"] = TEST_ORG_ID
    
    # Start the server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mcp.server", "--host", host, "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    return server_process

def stop_mcp_server(server_process: subprocess.Popen):
    """Stop the MCP server."""
    print("Stopping MCP server")
    server_process.terminate()
    server_process.wait()
    
    # Print server output
    stdout, stderr = server_process.communicate()
    if stdout:
        print(f"Server stdout: {stdout.decode()}")
    if stderr:
        print(f"Server stderr: {stderr.decode()}")

def send_request(url: str, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a request to the MCP server."""
    payload = {
        "command": command,
        "args": args
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def test_config(url: str) -> bool:
    """Test the config command."""
    print("\n=== Testing config command ===")
    
    # Set API token
    print("Setting API token...")
    response = send_request(url, "config", {
        "action": "set",
        "key": "api_token",
        "value": TEST_API_TOKEN
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success":
        print("❌ Failed to set API token")
        return False
    
    # Set org ID
    print("\nSetting org ID...")
    response = send_request(url, "config", {
        "action": "set",
        "key": "org_id",
        "value": TEST_ORG_ID
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success":
        print("❌ Failed to set org ID")
        return False
    
    # Get API token
    print("\nGetting API token...")
    response = send_request(url, "config", {
        "action": "get",
        "key": "api_token"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or not response.get("value"):
        print("❌ Failed to get API token")
        return False
    
    # Get org ID
    print("\nGetting org ID...")
    response = send_request(url, "config", {
        "action": "get",
        "key": "org_id"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or response.get("value") != TEST_ORG_ID:
        print("❌ Failed to get org ID")
        return False
    
    print("\n✅ Config command test passed")
    return True

def test_new_command(url: str) -> Optional[str]:
    """Test the new command."""
    print("\n=== Testing new command ===")
    
    print("Creating new agent run...")
    response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "TEST",
        "query": "This is a test agent run from MCP server"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or not response.get("task_id"):
        print("❌ Failed to create new agent run")
        return None
    
    task_id = response["task_id"]
    print(f"\n✅ New command test passed. Task ID: {task_id}")
    return task_id

def test_task_status(url: str, task_id: str) -> bool:
    """Test the task_status command."""
    print("\n=== Testing task_status command ===")
    
    print(f"Checking status of task {task_id}...")
    response = send_request(url, "task_status", {
        "task_id": task_id
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success":
        print("❌ Failed to get task status")
        return False
    
    print("\n✅ Task status command test passed")
    return True

def test_orchestrator_tracking(url: str) -> bool:
    """Test the orchestrator tracking functionality."""
    print("\n=== Testing orchestrator tracking ===")
    
    # Create orchestrator agent run
    print("Creating orchestrator agent run...")
    orchestrator_response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "ORCHESTRATOR",
        "query": "This is an orchestrator agent run from MCP server"
    })
    print(f"Response: {json.dumps(orchestrator_response, indent=2)}")
    
    if orchestrator_response.get("status") != "success" or not orchestrator_response.get("task_id"):
        print("❌ Failed to create orchestrator agent run")
        return False
    
    orchestrator_task_id = orchestrator_response["task_id"]
    orchestrator_run_id = orchestrator_response["agent_run_id"]
    
    # Create child agent run
    print("\nCreating child agent run...")
    child_response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "CHILD",
        "query": "This is a child agent run from MCP server",
        "orchestrator_run_id": orchestrator_run_id
    })
    print(f"Response: {json.dumps(child_response, indent=2)}")
    
    if child_response.get("status") != "success" or not child_response.get("task_id"):
        print("❌ Failed to create child agent run")
        return False
    
    child_task_id = child_response["task_id"]
    
    # Check that orchestrator_run_id is included in the response
    if child_response.get("orchestrator_run_id") != orchestrator_run_id:
        print("❌ Orchestrator run ID not included in response")
        return False
    
    print("\n✅ Orchestrator tracking test passed")
    return True

def test_list_command(url: str) -> bool:
    """Test the list command."""
    print("\n=== Testing list command ===")
    
    print("Listing agent runs...")
    response = send_request(url, "list", {
        "limit": 5
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success":
        print("❌ Failed to list agent runs")
        return False
    
    print("\n✅ List command test passed")
    return True

def test_resume_command(url: str) -> bool:
    """Test the resume command."""
    print("\n=== Testing resume command ===")
    
    # Create a new agent run first
    print("Creating new agent run for resume test...")
    response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "RESUME_TEST",
        "query": "This is a test agent run for resume test from MCP server"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or not response.get("agent_run_id"):
        print("❌ Failed to create new agent run for resume test")
        return False
    
    agent_run_id = response["agent_run_id"]
    
    # Resume the agent run
    print(f"\nResuming agent run {agent_run_id}...")
    resume_response = send_request(url, "resume", {
        "agent_run_id": agent_run_id,
        "task": "RESUMED",
        "query": "This is a resumed agent run from MCP server"
    })
    print(f"Response: {json.dumps(resume_response, indent=2)}")
    
    # Note: We expect this to fail since the agent run is not in a resumable state
    if resume_response.get("status") == "error" and "not in a resumable state" in resume_response.get("error", ""):
        print("✅ Resume command test passed (expected error about resumable state)")
        return True
    elif resume_response.get("status") == "success":
        print("✅ Resume command test passed (unexpected success)")
        return True
    else:
        print("❌ Resume command test failed (unexpected error)")
        return False

def test_logs_command(url: str) -> bool:
    """Test the logs command."""
    print("\n=== Testing logs command ===")
    
    # Create a new agent run first
    print("Creating new agent run for logs test...")
    response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "LOGS_TEST",
        "query": "This is a test agent run for logs test from MCP server"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or not response.get("agent_run_id"):
        print("❌ Failed to create new agent run for logs test")
        return False
    
    agent_run_id = response["agent_run_id"]
    
    # Get logs for the agent run
    print(f"\nGetting logs for agent run {agent_run_id}...")
    logs_response = send_request(url, "logs", {
        "agent_run_id": agent_run_id,
        "skip": 0,
        "limit": 10
    })
    print(f"Response: {json.dumps(logs_response, indent=2)}")
    
    if logs_response.get("status") == "success":
        print("✅ Logs command test passed")
        return True
    else:
        print("❌ Logs command test failed")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the Codegen MCP Server")
    parser.add_argument("--host", default="localhost", help="MCP server host")
    parser.add_argument("--port", type=int, default=8080, help="MCP server port")
    parser.add_argument("--no-server", action="store_true", help="Don't start the server (assume it's already running)")
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    url = f"http://{host}:{port}"
    
    print(f"Testing MCP server at {url}")
    print(f"Using test credentials: API token: {TEST_API_TOKEN[:4]}...{TEST_API_TOKEN[-4:]}, Org ID: {TEST_ORG_ID}")
    
    server_process = None
    if not args.no_server:
        server_process = start_mcp_server(host, port)
    
    try:
        # Test config command
        if not test_config(url):
            print("\n❌ Config command test failed")
            return
        
        # Test new command
        task_id = test_new_command(url)
        if not task_id:
            print("\n❌ New command test failed")
            return
        
        # Test task_status command
        if not test_task_status(url, task_id):
            print("\n❌ Task status command test failed")
            return
        
        # Test orchestrator tracking
        if not test_orchestrator_tracking(url):
            print("\n❌ Orchestrator tracking test failed")
            return
        
        # Test list command
        if not test_list_command(url):
            print("\n❌ List command test failed")
            return
        
        # Test resume command
        if not test_resume_command(url):
            print("\n❌ Resume command test failed")
            return
        
        # Test logs command
        if not test_logs_command(url):
            print("\n❌ Logs command test failed")
            return
        
        print("\n✅ All tests passed!")
    
    finally:
        if server_process:
            stop_mcp_server(server_process)

if __name__ == "__main__":
    main()
