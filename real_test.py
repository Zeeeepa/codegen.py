#!/usr/bin/env python3
"""
Real Test Script for Codegen API Client

This script tests the Codegen API client with real credentials.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional, List

from codegen_api_client import CodegenClient, ClientConfig, Agent, AgentRunStatus, SourceType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test credentials
API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
ORG_ID = "323"
BASE_URL = "https://api.codegen.com/v1"

def test_api_client():
    """Test the Codegen API client with real credentials."""
    logger.info("Testing Codegen API client with real credentials")
    
    # Initialize client
    config = ClientConfig(
        api_token=API_TOKEN,
        org_id=ORG_ID,
        base_url=BASE_URL
    )
    client = CodegenClient(config)
    
    # Test Users endpoints
    logger.info("Testing Users endpoints")
    try:
        # Get users
        users = client.get_users(limit=5)
        logger.info(f"Got {len(users.items)} users")
        
        # Get current user
        current_user = client.get_current_user()
        logger.info(f"Current user: {current_user.email}")
        
        # Get user by ID
        if users.items:
            user = client.get_user(users.items[0].id)
            logger.info(f"Got user: {user.email}")
    except Exception as e:
        logger.error(f"Error testing Users endpoints: {e}")
    
    # Test Organizations endpoint
    logger.info("Testing Organizations endpoint")
    try:
        orgs = client.get_organizations(limit=5)
        logger.info(f"Got {len(orgs.items)} organizations")
    except Exception as e:
        logger.error(f"Error testing Organizations endpoint: {e}")
    
    # Test Agents endpoints
    logger.info("Testing Agents endpoints")
    try:
        # Create agent run
        agent_run = client.create_agent_run(
            prompt="Test agent run from real_test.py",
            metadata={"test": True, "source": "real_test.py"}
        )
        logger.info(f"Created agent run: {agent_run.id}")
        
        # Get agent run
        run = client.get_agent_run(agent_run.id)
        logger.info(f"Got agent run: {run.id}, status: {run.status}")
        
        # List agent runs
        runs = client.list_agent_runs(limit=5)
        logger.info(f"Got {len(runs.items)} agent runs")
        
        # Resume agent run
        resumed_run = client.resume_agent_run(
            agent_run_id=agent_run.id,
            prompt="Resuming test agent run from real_test.py",
            metadata={"test": True, "source": "real_test.py", "resumed": True}
        )
        logger.info(f"Resumed agent run: {resumed_run.id}")
        
        # Get agent run logs
        try:
            logs = client.get_agent_run_logs(agent_run.id, limit=5)
            logger.info(f"Got {len(logs.logs)} logs for agent run {agent_run.id}")
        except Exception as e:
            logger.error(f"Error getting agent run logs: {e}")
    except Exception as e:
        logger.error(f"Error testing Agents endpoints: {e}")

def test_orchestrator_tracking():
    """Test orchestrator tracking functionality."""
    logger.info("Testing orchestrator tracking")
    
    # Initialize agent
    agent = Agent(org_id=ORG_ID, token=API_TOKEN, base_url=BASE_URL)
    
    # Create orchestrator run
    orchestrator_run = agent.run(
        prompt="Orchestrator run from real_test.py",
        metadata={"test": True, "source": "real_test.py", "role": "orchestrator"}
    )
    logger.info(f"Created orchestrator run: {orchestrator_run.id}")
    
    # Create child run
    child_run = agent.run(
        prompt=f"Child run from real_test.py, orchestrator: {orchestrator_run.id}",
        metadata={
            "test": True, 
            "source": "real_test.py", 
            "role": "child",
            "orchestrator_run_id": orchestrator_run.id
        }
    )
    logger.info(f"Created child run: {child_run.id}")
    
    # Wait for child run to complete
    logger.info(f"Waiting for child run {child_run.id} to complete")
    try:
        child_run.wait_for_completion(timeout=60)
        logger.info(f"Child run {child_run.id} completed")
    except TimeoutError:
        logger.warning(f"Child run {child_run.id} did not complete within timeout")
    
    # Check if orchestrator was notified
    orchestrator_run.refresh()
    logger.info(f"Orchestrator run {orchestrator_run.id} status: {orchestrator_run.status}")
    
    # Resume orchestrator with result
    orchestrator_run.resume(f"Result from child run {child_run.id}")
    logger.info(f"Resumed orchestrator run {orchestrator_run.id}")

def main():
    """Main function."""
    # Test API client
    test_api_client()
    
    # Test orchestrator tracking
    test_orchestrator_tracking()
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()

