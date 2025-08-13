#!/usr/bin/env python3
"""
Test script for Codegen MCP server integration
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import MCP server components
from codegen_client import CodegenClient
from config import Config
from state_manager import StateManager

def test_config():
    """Test configuration"""
    logger.info("Testing configuration...")
    
    # Set test credentials
    os.environ["CODEGEN_ORG_ID"] = "323"
    os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    
    # Initialize config
    config = Config()
    
    # Validate config
    assert config.get("org_id") == "323"
    assert config.get("api_token") == "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    
    logger.info("Configuration test passed!")

def test_client():
    """Test Codegen API client"""
    logger.info("Testing Codegen API client...")
    
    # Initialize client
    client = CodegenClient(
        org_id="323",
        api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    )
    
    # Test getting organizations
    try:
        orgs = client.get_organizations()
        logger.info(f"Found {len(orgs.get('items', []))} organizations")
        assert 'items' in orgs
        logger.info("Organizations test passed!")
    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        raise

def test_create_agent_run():
    """Test creating an agent run"""
    logger.info("Testing agent run creation...")
    
    # Initialize client
    client = CodegenClient(
        org_id="323",
        api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    )
    
    # Create a test agent run
    try:
        result = client.create_agent_run(
            prompt="Test agent run from MCP server integration test",
            metadata={"test": True, "source": "integration_test"}
        )
        
        run_id = result.get("id")
        logger.info(f"Created agent run: {run_id}")
        assert run_id is not None
        
        # Get the agent run
        run = client.get_agent_run(agent_run_id=run_id)
        logger.info(f"Agent run status: {run.get('status')}")
        
        logger.info("Agent run creation test passed!")
        return run_id
    except Exception as e:
        logger.error(f"Error creating agent run: {e}")
        raise

def test_orchestrator_tracking():
    """Test orchestrator tracking"""
    logger.info("Testing orchestrator tracking...")
    
    # Initialize components
    client = CodegenClient(
        org_id="323",
        api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    )
    state_manager = StateManager()
    
    # Create a test orchestrator
    try:
        orchestrator = client.create_agent_run(
            prompt="Test orchestrator from MCP server integration test",
            metadata={"test": True, "source": "integration_test", "is_orchestrator": True}
        )
        
        orchestrator_id = orchestrator.get("id")
        logger.info(f"Created orchestrator: {orchestrator_id}")
        
        # Register the orchestrator
        state_manager.register_orchestrator(str(orchestrator_id))
        
        # Create a child run
        child = client.create_agent_run(
            prompt="Test child run from MCP server integration test",
            metadata={"test": True, "source": "integration_test", "is_child": True},
            orchestrator_id=str(orchestrator_id)
        )
        
        child_id = child.get("id")
        logger.info(f"Created child run: {child_id}")
        
        # Register the child run
        state_manager.register_run(
            run_id=str(child_id),
            orchestrator_id=str(orchestrator_id),
            metadata={"test": True}
        )
        
        # Add the child to the orchestrator
        state_manager.add_child_to_orchestrator(
            orchestrator_id=str(orchestrator_id),
            child_run_id=str(child_id)
        )
        
        # Verify the relationship
        orchestrator_data = state_manager.get_orchestrator(str(orchestrator_id))
        assert str(child_id) in orchestrator_data.get("child_runs", [])
        
        # Verify the child's orchestrator
        child_data = state_manager.get_run(str(child_id))
        assert child_data.get("orchestrator_id") == str(orchestrator_id)
        
        logger.info("Orchestrator tracking test passed!")
        return orchestrator_id, child_id
    except Exception as e:
        logger.error(f"Error testing orchestrator tracking: {e}")
        raise

def main():
    """Main test function"""
    logger.info("Starting integration tests...")
    
    try:
        # Run tests
        test_config()
        test_client()
        run_id = test_create_agent_run()
        orchestrator_id, child_id = test_orchestrator_tracking()
        
        logger.info("All tests passed!")
        logger.info(f"Created agent run: {run_id}")
        logger.info(f"Created orchestrator: {orchestrator_id}")
        logger.info(f"Created child run: {child_id}")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

