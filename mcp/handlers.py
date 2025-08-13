"""
Handlers for MCP server commands.

This module provides handlers for the MCP server commands.
"""

import os
import uuid
import logging
import traceback
from typing import Dict, Any, Optional, List

from .task_manager import TaskManager
from .config import get_api_token, get_org_id, get_base_url
from codegen_api_client import Agent, CodegenClient, ClientConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize task manager
task_manager = TaskManager()

def handle_new_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'new' command."""
    try:
        # Check required arguments
        if "query" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: query",
                "details": "The 'query' argument is required for the 'new' command."
            }
        
        # Get API token and org ID
        api_token = get_api_token()
        org_id = get_org_id()
        base_url = get_base_url()
        
        if not api_token:
            return {
                "status": "error",
                "error": "API token not configured",
                "details": "Set the CODEGEN_API_TOKEN environment variable or use the 'config' command."
            }
        
        if not org_id:
            return {
                "status": "error",
                "error": "Organization ID not configured",
                "details": "Set the CODEGEN_ORG_ID environment variable or use the 'config' command."
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
        
        # Include orchestrator run ID if provided
        if "orchestrator_run_id" in args:
            metadata["orchestrator_run_id"] = args["orchestrator_run_id"]
        
        # Run agent
        task = agent.run(
            prompt=args["query"],
            metadata=metadata
        )
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Store task in task manager
        task_manager.add_task(task_id, task)
        
        # Return response
        return {
            "status": "success",
            "task_id": task_id,
            "agent_run_id": task.id,
            "state": task.status,
            "web_url": task.web_url,
            "metadata": metadata,
            "orchestrator_run_id": args.get("orchestrator_run_id")
        }
    
    except Exception as e:
        logger.error(f"Error handling 'new' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
        }

def handle_resume_command(args: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Get API token and org ID
        api_token = get_api_token()
        org_id = get_org_id()
        base_url = get_base_url()
        
        if not api_token:
            return {
                "status": "error",
                "error": "API token not configured",
                "details": "Set the CODEGEN_API_TOKEN environment variable or use the 'config' command."
            }
        
        if not org_id:
            return {
                "status": "error",
                "error": "Organization ID not configured",
                "details": "Set the CODEGEN_ORG_ID environment variable or use the 'config' command."
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
            task.resume(args["query"])
            
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Store task in task manager
            task_manager.add_task(task_id, task)
            
            # Return response
            return {
                "status": "success",
                "task_id": task_id,
                "agent_run_id": task.id,
                "state": task.status,
                "web_url": task.web_url,
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
        logger.error(f"Error handling 'resume' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
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
        logger.error(f"Error handling 'config' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
        }

def handle_list_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'list' command."""
    try:
        # Get API token and org ID
        api_token = get_api_token()
        org_id = get_org_id()
        base_url = get_base_url()
        
        if not api_token:
            return {
                "status": "error",
                "error": "API token not configured",
                "details": "Set the CODEGEN_API_TOKEN environment variable or use the 'config' command."
            }
        
        if not org_id:
            return {
                "status": "error",
                "error": "Organization ID not configured",
                "details": "Set the CODEGEN_ORG_ID environment variable or use the 'config' command."
            }
        
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
        logger.error(f"Error handling 'list' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
        }

def handle_task_status_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'task_status' command."""
    try:
        # Check required arguments
        if "task_id" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: task_id",
                "details": "The 'task_id' argument is required for the 'task_status' command."
            }
        
        # Get task from task manager
        task_id = args["task_id"]
        task = task_manager.get_task(task_id)
        
        if not task:
            return {
                "status": "error",
                "error": f"Task {task_id} not found",
                "details": "The task may have expired or been removed."
            }
        
        # Refresh task status
        task.refresh()
        
        # Return response
        response = {
            "status": "success",
            "task_id": task_id,
            "agent_run_id": task.id,
            "state": task.status,
            "web_url": task.web_url
        }
        
        if task.result:
            response["result"] = task.result
        
        return response
    
    except Exception as e:
        logger.error(f"Error handling 'task_status' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
        }

def handle_logs_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'logs' command."""
    try:
        # Check required arguments
        if "agent_run_id" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: agent_run_id",
                "details": "The 'agent_run_id' argument is required for the 'logs' command."
            }
        
        # Get API token and org ID
        api_token = get_api_token()
        org_id = get_org_id()
        base_url = get_base_url()
        
        if not api_token:
            return {
                "status": "error",
                "error": "API token not configured",
                "details": "Set the CODEGEN_API_TOKEN environment variable or use the 'config' command."
            }
        
        if not org_id:
            return {
                "status": "error",
                "error": "Organization ID not configured",
                "details": "Set the CODEGEN_ORG_ID environment variable or use the 'config' command."
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
            "logs": logs
        }
    
    except Exception as e:
        logger.error(f"Error handling 'logs' command: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "details": traceback.format_exc()
        }

