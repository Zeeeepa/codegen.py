#!/usr/bin/env python3
"""
Real test script for the Codegen MCP Server.

This script tests the MCP server with the provided real credentials.
"""

import os
import sys
import json
import time
import argparse
import requests
from typing import Dict, Any, Optional

# Set real credentials
REAL_API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
REAL_ORG_ID = "323"

def send_request(url: str, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a request to the MCP server."""
    payload = {
        "command": command,
        "args": args
    }
    
    print(f"\nSending request: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    return response.json()

def test_with_real_credentials(url: str) -> None:
    """Test the MCP server with real credentials."""
    print("\n=== Testing with real credentials ===")
    
    # Set API token
    print("\nSetting API token...")
    response = send_request(url, "config", {
        "action": "set",
        "key": "api_token",
        "value": REAL_API_TOKEN
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Set org ID
    print("\nSetting org ID...")
    response = send_request(url, "config", {
        "action": "set",
        "key": "org_id",
        "value": REAL_ORG_ID
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Create a new agent run
    print("\nCreating new agent run...")
    response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "TEST",
        "query": "This is a test agent run using real credentials"
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success" or not response.get("task_id"):
        print("❌ Failed to create new agent run")
        return
    
    task_id = response["task_id"]
    agent_run_id = response["agent_run_id"]
    
    # Check task status
    print(f"\nChecking status of task {task_id}...")
    response = send_request(url, "task_status", {
        "task_id": task_id
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Create orchestrator agent run
    print("\nCreating orchestrator agent run...")
    orchestrator_response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "ORCHESTRATOR",
        "query": "This is an orchestrator agent run using real credentials"
    })
    print(f"Response: {json.dumps(orchestrator_response, indent=2)}")
    
    if orchestrator_response.get("status") != "success" or not orchestrator_response.get("task_id"):
        print("❌ Failed to create orchestrator agent run")
        return
    
    orchestrator_task_id = orchestrator_response["task_id"]
    orchestrator_run_id = orchestrator_response["agent_run_id"]
    
    # Create child agent run with orchestrator ID
    print("\nCreating child agent run with orchestrator ID...")
    child_response = send_request(url, "new", {
        "repo": "Zeeeepa/codegen.py",
        "task": "CHILD",
        "query": "This is a child agent run using real credentials",
        "orchestrator_run_id": orchestrator_run_id
    })
    print(f"Response: {json.dumps(child_response, indent=2)}")
    
    if child_response.get("status") != "success" or not child_response.get("task_id"):
        print("❌ Failed to create child agent run")
        return
    
    child_task_id = child_response["task_id"]
    
    # Check that orchestrator_run_id is included in the response
    if child_response.get("orchestrator_run_id") != orchestrator_run_id:
        print("❌ Orchestrator run ID not included in response")
    else:
        print("✅ Orchestrator run ID included in response")
    
    # List agent runs
    print("\nListing agent runs...")
    response = send_request(url, "list", {
        "limit": 5
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Resume agent run
    print("\nResuming agent run...")
    response = send_request(url, "resume", {
        "agent_run_id": agent_run_id,
        "task": "ANALYZE",
        "query": "Analyze the codebase using real credentials",
        "orchestrator_run_id": orchestrator_run_id
    })
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if response.get("status") != "success":
        print("❌ Failed to resume agent run")
    else:
        print("✅ Agent run resumed successfully")
        
        # Check that orchestrator_run_id is included in the response
        if response.get("orchestrator_run_id") != orchestrator_run_id:
            print("❌ Orchestrator run ID not included in response")
        else:
            print("✅ Orchestrator run ID included in response")
    
    print("\n=== Test completed ===")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the Codegen MCP Server with real credentials")
    parser.add_argument("--url", default="http://localhost:8080", help="MCP server URL")
    args = parser.parse_args()
    
    url = args.url
    
    print(f"Testing MCP server at {url}")
    print(f"Using real credentials: API token: {REAL_API_TOKEN}, Org ID: {REAL_ORG_ID}")
    
    test_with_real_credentials(url)

if __name__ == "__main__":
    main()

