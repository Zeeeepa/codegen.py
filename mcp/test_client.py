#!/usr/bin/env python3
"""
Test client for MCP server
"""

import sys
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mcp_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Test the MCP server"""
    base_url = f"http://{host}:{port}"
    
    logger.info(f"Testing MCP server at {base_url}")
    
    # Test codegenapi_config
    logger.info("Testing codegenapi_config...")
    response = requests.post(
        f"{base_url}/mcp/invoke",
        json={
            "name": "codegenapi_config",
            "parameters": {
                "action": "set",
                "key": "api_token",
                "value": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
            }
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Error setting API token: {response.text}")
        return
    
    logger.info(f"Set API token response: {response.json()}")
    
    # Set org ID
    response = requests.post(
        f"{base_url}/mcp/invoke",
        json={
            "name": "codegenapi_config",
            "parameters": {
                "action": "set",
                "key": "org_id",
                "value": "323"
            }
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Error setting org ID: {response.text}")
        return
    
    logger.info(f"Set org ID response: {response.json()}")
    
    # Test codegenapi_list
    logger.info("Testing codegenapi_list...")
    response = requests.post(
        f"{base_url}/mcp/invoke",
        json={
            "name": "codegenapi_list",
            "parameters": {
                "limit": 5
            }
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Error listing agent runs: {response.text}")
        return
    
    logger.info(f"List agent runs response: {response.json()}")
    
    # Test codegenapi_new
    logger.info("Testing codegenapi_new...")
    response = requests.post(
        f"{base_url}/mcp/invoke",
        json={
            "name": "codegenapi_new",
            "parameters": {
                "repo": "Zeeeepa/codegen.py",
                "task": "TEST",
                "query": "Test agent run from MCP client test"
            }
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Error creating agent run: {response.text}")
        return
    
    result = response.json()
    logger.info(f"Create agent run response: {result}")
    
    agent_run_id = result.get("agent_run_id")
    if not agent_run_id:
        logger.error("Failed to get agent run ID from response")
        return
    
    # Test codegenapi_resume
    logger.info("Testing codegenapi_resume...")
    response = requests.post(
        f"{base_url}/mcp/invoke",
        json={
            "name": "codegenapi_resume",
            "parameters": {
                "agent_run_id": agent_run_id,
                "query": "Resumed agent run from MCP client test"
            }
        }
    )
    
    if response.status_code != 200:
        logger.error(f"Error resuming agent run: {response.text}")
        return
    
    logger.info(f"Resume agent run response: {response.json()}")
    
    logger.info("All MCP server tests completed successfully!")

if __name__ == "__main__":
    # Get host and port from command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    test_mcp_server(host, port)

