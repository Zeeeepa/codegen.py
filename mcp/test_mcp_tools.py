#!/usr/bin/env python3
"""
Test script for MCP tools
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import server components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from codegen_client import CodegenClient

def test_config():
    """Test config tool"""
    logger.info("Testing config tool...")
    
    # Initialize config
    config = Config()
    
    # Set API token
    config.set("api_token", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    logger.info(f"Set API token")
    
    # Set org ID
    config.set("org_id", "323")
    logger.info(f"Set org ID")
    
    # Get API token
    api_token = config.get("api_token")
    logger.info(f"API token: {api_token[:4]}...{api_token[-4:]}")
    
    # Get org ID
    org_id = config.get("org_id")
    logger.info(f"Org ID: {org_id}")
    
    # Validate config
    is_valid = config.validate()
    logger.info(f"Config validation: {is_valid}")

def test_client():
    """Test Codegen client"""
    logger.info("Testing Codegen client...")
    
    # Initialize client
    client = CodegenClient(
        org_id="323",
        api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    )
    
    # Get organizations
    orgs = client.get_organizations()
    logger.info(f"Organizations: {orgs}")
    
    # List agent runs
    runs = client.list_agent_runs(limit=5)
    logger.info(f"Agent runs: {runs}")
    
    # Create agent run
    result = client.create_agent_run(
        prompt="Test agent run from MCP tools test",
        metadata={"test": True, "source": "mcp_tools_test"}
    )
    logger.info(f"Created agent run: {result}")
    
    run_id = result.get("id")
    
    # Get agent run
    run = client.get_agent_run(agent_run_id=run_id)
    logger.info(f"Agent run: {run}")
    
    # Resume agent run
    resume_result = client.resume_agent_run(
        agent_run_id=run_id,
        prompt="Resumed agent run from MCP tools test"
    )
    logger.info(f"Resumed agent run: {resume_result}")
    
    return run_id

def main():
    """Main test function"""
    logger.info("Starting MCP tools tests...")
    
    try:
        # Test config
        test_config()
        
        # Test client
        run_id = test_client()
        
        logger.info(f"All MCP tools tests completed successfully! Created agent run: {run_id}")
    
    except Exception as e:
        logger.error(f"Error in MCP tools tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

