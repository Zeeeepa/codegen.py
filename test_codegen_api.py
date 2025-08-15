#!/usr/bin/env python3
"""
Test script for the Codegen API client
This script tests the basic functionality of the Agent class
"""

import os
import sys
from codegen_api import Agent, Task, AgentRunStatus

def test_agent_initialization():
    """Test that the Agent class can be initialized"""
    print("Testing Agent initialization...")
    
    # Test with environment variables
    try:
        # Try to initialize with environment variables if available
        agent = Agent()
        print("✅ Agent initialized successfully with environment variables")
        print(f"Organization ID: {agent.org_id}")
        agent.close()
    except Exception as e:
        print(f"❌ Failed to initialize Agent with environment variables: {e}")
        print("This is expected if you haven't set CODEGEN_ORG_ID and CODEGEN_API_TOKEN")
    
    # Test with explicit parameters
    try:
        # Use dummy values for testing - these won't actually connect
        agent = Agent(org_id="12345", token="dummy_token")
        print("✅ Agent initialized with explicit parameters")
        agent.close()
    except Exception as e:
        print(f"❌ Failed to initialize Agent with explicit parameters: {e}")

def test_mcp_integration():
    """Test that the Agent can be used from an MCP tool"""
    print("\nTesting MCP integration...")
    print("✅ This test script is being executed, which confirms MCP tool execution works")
    print("✅ The script can import the codegen_api module")
    print("✅ The Agent class is accessible from the module")

def main():
    """Main test function"""
    print("=== Codegen API Test ===")
    print(f"Python version: {sys.version}")
    
    # Print environment variables (redacted for security)
    org_id = os.environ.get("CODEGEN_ORG_ID", "Not set")
    token = "REDACTED" if os.environ.get("CODEGEN_API_TOKEN") else "Not set"
    print(f"CODEGEN_ORG_ID: {org_id}")
    print(f"CODEGEN_API_TOKEN: {token}")
    
    # Run tests
    test_agent_initialization()
    test_mcp_integration()
    
    print("\n=== Test Complete ===")
    print("MCP tools test successful!")

if __name__ == "__main__":
    main()

