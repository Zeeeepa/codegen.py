#!/usr/bin/env python3
"""
MCP Server for Codegen API

This module provides a direct Python module that implements the Model Context Protocol (MCP)
for the Codegen API. It directly executes API calls when invoked by MCP clients.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List, Callable

from .config import get_api_token, get_org_id, get_base_url
from codegen_api_client import Agent, CodegenClient, ClientConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def handle_command(command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle MCP command directly.
    
    This is the main entry point for MCP clients to execute commands.
    
    Args:
        command: The command to execute
        args: The command arguments
        
    Returns:
        The command response
    """
    logger.info(f"Handling command: {command}")
    
    # Get API token and org ID
    api_token = get_api_token()
    org_id = get_org_id()
    base_url = get_base_url()
    
    if not api_token and command != "config":
        return {
            "status": "error",
            "error": "API token not configured",
            "details": "Set the CODEGEN_API_TOKEN environment variable or use the 'config' command."
        }
    
    if not org_id and command != "config":
        return {
            "status": "error",
            "error": "Organization ID not configured",
            "details": "Set the CODEGEN_ORG_ID environment variable or use the 'config' command."
        }
    
    # Handle commands
    if command == "new":
        return handle_new_command(args, api_token, org_id, base_url)
    
    elif command == "resume":
        return handle_resume_command(args, api_token, org_id, base_url)
    
    elif command == "config":
        return handle_config_command(args)
    
    elif command == "list":
        return handle_list_command(args, api_token, org_id, base_url)
    
    elif command == "logs":
        return handle_logs_command(args, api_token, org_id, base_url)
    
    else:
        return {
            "status": "error",
            "error": "Unknown command",
            "details": f"Command '{command}' is not supported."
        }

def handle_new_command(args: Dict[str, Any], api_token: str, org_id: str, base_url: str) -> Dict[str, Any]:
    """Handle the 'new' command."""
    try:
        # Check required arguments
        if "query" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: query",
                "details": "The 'query' argument is required for the 'new' command."
            }
        
        # Initialize agent
        agent = Agent(
            org_id=org_id,
            token=api_token,
            base_url=base_url
        )
        
        # Build metadata
        metadata = {}
        
        if "repo" in args:
            metadata["repo"] = args["repo"]
        
        if "branch" in args:
            metadata["branch"] = args["branch"]
        
        if "pr" in args:
            metadata["pr"] = args["pr"]
        
        if "task" in args:
            metadata["task_type"] = args["task"]
        
        # Run agent
        task = agent.run(
            prompt=args["query"],
            metadata=metadata
        )
        
        # Return response
        return {
            "status": "success",
            "agent_run_id": task.id,
            "state": task.status,
            "web_url": task.web_url,
            "metadata": metadata
        }
    
    except Exception as e:
        logger.exception(f"Error handling 'new' command: {e}")
        
        return {
            "status": "error",
            "error": str(e)
        }

def handle_resume_command(args: Dict[str, Any], api_token: str, org_id: str, base_url: str) -> Dict[str, Any]:
    """Handle the 'resume' command."""
    try:
        # Check required arguments
        if "agent_run_id" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: agent_run_id",
                "details": "The 'agent_run_id' argument is required for the 'resume' command."
            }
        
        if "query" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: query",
                "details": "The 'query' argument is required for the 'resume' command."
            }
        
        # Initialize agent
        agent = Agent(
            org_id=org_id,
            token=api_token,
            base_url=base_url
        )
        
        # Get task
        agent_run_id = int(args["agent_run_id"])
        task = agent.get_task(agent_run_id)
        
        # Check if task is in a resumable state
        if task.status != "COMPLETE":
            return {
                "status": "error",
                "error": f"Agent run {agent_run_id} is not in a resumable state",
                "details": f"Current status: {task.status}. Only agent runs with status 'COMPLETE' can be resumed."
            }
        
        # Build metadata
        metadata = {}
        
        if "task" in args:
            metadata["task_type"] = args["task"]
        
        # Resume task
        try:
            resumed_task = task.resume(args["query"])
            
            # Return response
            return {
                "status": "success",
                "agent_run_id": resumed_task.id,
                "state": resumed_task.status,
                "web_url": resumed_task.web_url,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error resuming task: {e}")
            
            return {
                "status": "error",
                "error": f"Error resuming agent run: {e}",
                "details": "The agent run may not be in a resumable state."
            }
    
    except Exception as e:
        logger.exception(f"Error handling 'resume' command: {e}")
        
        return {
            "status": "error",
            "error": str(e)
        }

def handle_config_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'config' command."""
    try:
        # Check required arguments
        if "action" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: action",
                "details": "The 'action' argument is required for the 'config' command."
            }
        
        if "key" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: key",
                "details": "The 'key' argument is required for the 'config' command."
            }
        
        # Handle 'set' action
        if args["action"] == "set":
            if "value" not in args:
                return {
                    "status": "error",
                    "error": "Missing required argument: value",
                    "details": "The 'value' argument is required for the 'config set' command."
                }
            
            # Set environment variable
            os.environ[f"CODEGEN_{args['key'].upper()}"] = args["value"]
            
            return {
                "status": "success",
                "message": f"Configuration value '{args['key']}' set successfully"
            }
        
        # Handle 'get' action
        elif args["action"] == "get":
            # Get environment variable
            value = os.environ.get(f"CODEGEN_{args['key'].upper()}")
            
            if value:
                # Mask token for security
                if args["key"] == "api_token":
                    value = value[:4] + "..." + value[-4:]
                
                return {
                    "status": "success",
                    "key": args["key"],
                    "value": value
                }
            else:
                return {
                    "status": "error",
                    "error": f"Configuration value '{args['key']}' not found",
                    "details": f"Set the CODEGEN_{args['key'].upper()} environment variable or use the 'config set' command."
                }
        
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {args['action']}",
                "details": "The 'action' argument must be 'set' or 'get'."
            }
    
    except Exception as e:
        logger.exception(f"Error handling 'config' command: {e}")
        
        return {
            "status": "error",
            "error": str(e)
        }

def handle_list_command(args: Dict[str, Any], api_token: str, org_id: str, base_url: str) -> Dict[str, Any]:
    """Handle the 'list' command."""
    try:
        # Initialize client
        client = CodegenClient(
            ClientConfig(
                api_token=api_token,
                org_id=org_id,
                base_url=base_url
            )
        )
        
        # Get agent runs
        limit = args.get("limit", 20)
        runs = client.list_agent_runs(limit=limit)
        
        # Filter by status if provided
        if "status" in args:
            filtered_runs = [run for run in runs.items if run.status == args["status"]]
        else:
            filtered_runs = runs.items
        
        # Filter by repository if provided
        if "repo" in args:
            filtered_runs = [
                run for run in filtered_runs 
                if run.metadata and run.metadata.get("repo") == args["repo"]
            ]
        
        # Convert to response format
        items = []
        for run in filtered_runs:
            item = {
                "id": run.id,
                "status": run.status,
                "created_at": run.created_at,
                "web_url": run.web_url,
                "metadata": run.metadata
            }
            
            if run.result:
                item["result"] = run.result
            
            items.append(item)
        
        # Return response
        return {
            "status": "success",
            "items": items,
            "total": len(items),
            "page": 1,
            "size": limit,
            "pages": 1
        }
    
    except Exception as e:
        logger.exception(f"Error handling 'list' command: {e}")
        
        return {
            "status": "error",
            "error": str(e)
        }

def handle_logs_command(args: Dict[str, Any], api_token: str, org_id: str, base_url: str) -> Dict[str, Any]:
    """Handle the 'logs' command."""
    try:
        # Check required arguments
        if "agent_run_id" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: agent_run_id",
                "details": "The 'agent_run_id' argument is required for the 'logs' command."
            }
        
        # Initialize client
        client = CodegenClient(
            ClientConfig(
                api_token=api_token,
                org_id=org_id,
                base_url=base_url
            )
        )
        
        # Get agent run logs
        agent_run_id = int(args["agent_run_id"])
        skip = args.get("skip", 0)
        limit = args.get("limit", 100)
        
        logs = client.get_agent_run_logs(
            agent_run_id=agent_run_id,
            skip=skip,
            limit=limit
        )
        
        # Return response
        return {
            "status": "success",
            "logs": logs.logs,
            "total_logs": logs.total,
            "page": 1,
            "size": limit,
            "pages": 1
        }
    
    except Exception as e:
        logger.exception(f"Error handling 'logs' command: {e}")
        
        return {
            "status": "error",
            "error": str(e)
        }

# Main entry point for MCP clients
def main(command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for MCP clients.
    
    Args:
        command: The command to execute
        args: The command arguments
        
    Returns:
        The command response
    """
    return handle_command(command, args)
