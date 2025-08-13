#!/usr/bin/env python3
"""
Validation script for Codegen API endpoints.

This script validates each command by making actual API calls to the Codegen API.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional, List

from codegen_api_client import CodegenClient, ClientConfig, Agent, AgentRunStatus, SourceType

# Set credentials
API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
ORG_ID = "323"
ORCHESTRATOR_ID = 72110
BASE_URL = "https://api.codegen.com/v1"

def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")

def validate_users_endpoints(client: CodegenClient):
    """Validate Users endpoints."""
    print("VALIDATING USERS ENDPOINTS")
    print_separator()
    
    # 1. Get Users
    print("1. GET /users - Get Users")
    try:
        users = client.get_users(limit=5)
        print(f"SUCCESS: Got {len(users.items)} users")
        print(f"Response: {users}")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()
    
    # 2. Get User
    print("2. GET /user/{id} - Get User")
    try:
        # Get the first user from the list
        if users.items:
            user_id = users.items[0].id
            user = client.get_user(user_id)
            print(f"SUCCESS: Got user with ID {user_id}")
            print(f"Response: {user}")
        else:
            print("SKIPPED: No users available to test Get User endpoint")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()
    
    # 3. Get Current User Info
    print("3. GET /user/current - Get Current User Info")
    try:
        current_user = client.get_current_user()
        print(f"SUCCESS: Got current user info")
        print(f"Response: {current_user}")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()

def validate_agents_endpoints(client: CodegenClient):
    """Validate Agents endpoints."""
    print("VALIDATING AGENTS ENDPOINTS")
    print_separator()
    
    # 4. Create Agent Run
    print("4. POST /agent/run - Create Agent Run")
    try:
        agent_run = client.create_agent_run(
            prompt="Validation test for Codegen API endpoints",
            metadata={
                "test": True,
                "source": "validate_commands.py",
                "orchestrator_run_id": ORCHESTRATOR_ID
            }
        )
        print(f"SUCCESS: Created agent run with ID {agent_run.id}")
        print(f"Response: {agent_run}")
        
        # Store agent run ID for other tests
        agent_run_id = agent_run.id
    except Exception as e:
        print(f"ERROR: {e}")
        agent_run_id = None
    print_separator()
    
    # 5. Get Agent Run
    print("5. GET /agent/run/{id} - Get Agent Run")
    if agent_run_id:
        try:
            run = client.get_agent_run(agent_run_id)
            print(f"SUCCESS: Got agent run with ID {agent_run_id}")
            print(f"Response: {run}")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print("SKIPPED: No agent run ID available to test Get Agent Run endpoint")
    print_separator()
    
    # 6. List Agent Runs
    print("6. GET /agent/runs - List Agent Runs")
    try:
        runs = client.list_agent_runs(limit=5)
        print(f"SUCCESS: Got {len(runs.items)} agent runs")
        print(f"Response: {runs}")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()
    
    # 7. Resume Agent Run
    print("7. POST /agent/run/{id}/resume - Resume Agent Run")
    if agent_run_id:
        try:
            resumed_run = client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt="Resuming validation test for Codegen API endpoints",
                metadata={
                    "test": True,
                    "source": "validate_commands.py",
                    "resumed": True,
                    "orchestrator_run_id": ORCHESTRATOR_ID
                }
            )
            print(f"SUCCESS: Resumed agent run with ID {agent_run_id}")
            print(f"Response: {resumed_run}")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print("SKIPPED: No agent run ID available to test Resume Agent Run endpoint")
    print_separator()

def validate_organizations_endpoints(client: CodegenClient):
    """Validate Organizations endpoints."""
    print("VALIDATING ORGANIZATIONS ENDPOINTS")
    print_separator()
    
    # 8. Get Organizations
    print("8. GET /organizations - Get Organizations")
    try:
        orgs = client.get_organizations(limit=5)
        print(f"SUCCESS: Got organizations")
        print(f"Response: {orgs}")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()

def validate_agents_alpha_endpoints(client: CodegenClient):
    """Validate Agents-Alpha endpoints."""
    print("VALIDATING AGENTS-ALPHA ENDPOINTS")
    print_separator()
    
    # 9. Get Agent Run Logs
    print("9. GET /agent/run/{id}/logs - Get Agent Run Logs")
    try:
        # Get the first agent run from the list
        runs = client.list_agent_runs(limit=1)
        if runs.items:
            agent_run_id = runs.items[0].id
            logs = client.get_agent_run_logs(agent_run_id, limit=5)
            print(f"SUCCESS: Got logs for agent run with ID {agent_run_id}")
            print(f"Response: {logs}")
        else:
            print("SKIPPED: No agent runs available to test Get Agent Run Logs endpoint")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()

def validate_orchestrator_tracking(client: CodegenClient):
    """Validate orchestrator tracking functionality."""
    print("VALIDATING ORCHESTRATOR TRACKING")
    print_separator()
    
    # Initialize agent
    agent = Agent(org_id=ORG_ID, token=API_TOKEN, base_url=BASE_URL)
    
    # Create child run with orchestrator ID
    try:
        child_run = agent.run(
            prompt=f"Child run from validate_commands.py, orchestrator: {ORCHESTRATOR_ID}",
            metadata={
                "test": True,
                "source": "validate_commands.py",
                "role": "child",
                "orchestrator_run_id": ORCHESTRATOR_ID
            }
        )
        print(f"SUCCESS: Created child run with ID {child_run.id} for orchestrator {ORCHESTRATOR_ID}")
        
        # Check child run status
        child_run.refresh()
        print(f"Child run status: {child_run.status}")
        
        print("Orchestrator tracking validation successful")
    except Exception as e:
        print(f"ERROR: {e}")
    print_separator()

def main():
    """Main function."""
    print(f"Validating Codegen API endpoints with credentials:")
    print(f"API Token: {API_TOKEN[:4]}...{API_TOKEN[-4:]}")
    print(f"Org ID: {ORG_ID}")
    print(f"Orchestrator ID: {ORCHESTRATOR_ID}")
    print_separator()
    
    # Initialize client
    config = ClientConfig(
        api_token=API_TOKEN,
        org_id=ORG_ID,
        base_url=BASE_URL
    )
    client = CodegenClient(config)
    
    # Validate endpoints
    validate_users_endpoints(client)
    validate_agents_endpoints(client)
    validate_organizations_endpoints(client)
    validate_agents_alpha_endpoints(client)
    validate_orchestrator_tracking(client)
    
    print("Validation complete!")

if __name__ == "__main__":
    main()

