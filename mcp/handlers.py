"""
Command Handlers

This module provides handlers for the MCP server commands.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List, Tuple

# Add parent directory to path to import codegen_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codegen_api import Agent, CodegenClient, ClientConfig, AgentRunStatus

from .config import get_api_token, get_org_id, get_base_url, set_config_value
from .task_manager import get_task_manager, TaskInfo


def handle_new_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'new' command to start a new agent run.
    
    Args:
        args: Command arguments including:
            - repo: Repository name (e.g., "Zeeeepa/codegen.py")
            - branch: Branch name (optional)
            - pr: PR number (optional)
            - task: Task type (e.g., "CREATE_PLAN")
            - query: Task description
    
    Returns:
        Response dictionary with task information
    """
    # Validate required arguments
    if "query" not in args:
        return {
            "status": "error",
            "error": "Missing required argument: query",
            "details": "The query argument is required for the new command."
        }
    
    # Get API credentials
    api_token = get_api_token()
    org_id = get_org_id()
    
    if not api_token:
        return {
            "status": "error",
            "error": "API token not configured",
            "details": "Use 'codegenapi config set api-token YOUR_TOKEN' to configure your API token."
        }
    
    if not org_id:
        return {
            "status": "error",
            "error": "Organization ID not configured",
            "details": "Use 'codegenapi config set org_id YOUR_ORG_ID' to configure your organization ID."
        }
    
    # Create task
    task_manager = get_task_manager()
    task_id = task_manager.create_task(metadata={
        "command": "new",
        "repo": args.get("repo"),
        "branch": args.get("branch"),
        "pr": args.get("pr"),
        "task_type": args.get("task")
    })
    
    # Build prompt
    prompt_parts = []
    
    if args.get("repo"):
        prompt_parts.append(f"Repository: {args['repo']}")
    
    if args.get("branch"):
        prompt_parts.append(f"Branch: {args['branch']}")
    
    if args.get("pr"):
        prompt_parts.append(f"PR: #{args['pr']}")
    
    if args.get("task"):
        prompt_parts.append(f"Task: {args['task']}")
    
    prompt_parts.append(f"Query: {args['query']}")
    
    prompt = "\n".join(prompt_parts)
    
    # Run task asynchronously
    task_manager.run_agent_task(
        task_id=task_id,
        api_token=api_token,
        org_id=org_id,
        prompt=prompt,
        repo=args.get("repo"),
        branch=args.get("branch"),
        pr=args.get("pr"),
        task_type=args.get("task")
    )
    
    # Get task info
    task_info = task_manager.get_task(task_id)
    
    # Return response
    return {
        "status": "success",
        "task_id": task_id,
        "agent_run_id": task_info.agent_run_id,
        "state": task_info.status,
        "web_url": task_info.web_url,
        "message": "Agent run started successfully."
    }


def handle_resume_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'resume' command to resume an agent run.
    
    Args:
        args: Command arguments including:
            - agent_run_id: Agent run ID to resume
            - task: Task type (optional)
            - query: Additional instructions
    
    Returns:
        Response dictionary with task information
    """
    # Validate required arguments
    if "agent_run_id" not in args:
        return {
            "status": "error",
            "error": "Missing required argument: agent_run_id",
            "details": "The agent_run_id argument is required for the resume command."
        }
    
    if "query" not in args:
        return {
            "status": "error",
            "error": "Missing required argument: query",
            "details": "The query argument is required for the resume command."
        }
    
    # Get API credentials
    api_token = get_api_token()
    org_id = get_org_id()
    
    if not api_token:
        return {
            "status": "error",
            "error": "API token not configured",
            "details": "Use 'codegenapi config set api-token YOUR_TOKEN' to configure your API token."
        }
    
    if not org_id:
        return {
            "status": "error",
            "error": "Organization ID not configured",
            "details": "Use 'codegenapi config set org_id YOUR_ORG_ID' to configure your organization ID."
        }
    
    # Create task
    task_manager = get_task_manager()
    task_id = task_manager.create_task(metadata={
        "command": "resume",
        "agent_run_id": args["agent_run_id"],
        "task_type": args.get("task")
    })
    
    # Build prompt
    prompt_parts = []
    
    if args.get("task"):
        prompt_parts.append(f"Task: {args['task']}")
    
    prompt_parts.append(f"Query: {args['query']}")
    
    prompt = "\n".join(prompt_parts)
    
    # Run task asynchronously
    task_manager.resume_agent_task(
        task_id=task_id,
        api_token=api_token,
        org_id=org_id,
        agent_run_id=int(args["agent_run_id"]),
        prompt=prompt,
        task_type=args.get("task")
    )
    
    # Get task info
    task_info = task_manager.get_task(task_id)
    
    # Return response
    return {
        "status": "success",
        "task_id": task_id,
        "agent_run_id": args["agent_run_id"],
        "state": task_info.status,
        "web_url": task_info.web_url,
        "message": "Agent run resumed successfully."
    }


def handle_config_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'config' command to set or get configuration values.
    
    Args:
        args: Command arguments including:
            - action: "set" or "get"
            - key: Configuration key
            - value: Configuration value (for "set" action)
    
    Returns:
        Response dictionary with configuration information
    """
    action = args.get("action")
    
    if action == "set":
        # Validate required arguments
        if "key" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: key",
                "details": "The key argument is required for the config set command."
            }
        
        if "value" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: value",
                "details": "The value argument is required for the config set command."
            }
        
        # Set configuration value
        key = args["key"]
        value = args["value"]
        
        # Handle special keys
        if key == "api-token":
            key = "api_token"
        
        set_config_value(key, value)
        
        return {
            "status": "success",
            "key": key,
            "message": f"Configuration value '{key}' set successfully."
        }
    
    elif action == "get":
        # Validate required arguments
        if "key" not in args:
            return {
                "status": "error",
                "error": "Missing required argument: key",
                "details": "The key argument is required for the config get command."
            }
        
        # Get configuration value
        key = args["key"]
        
        # Handle special keys
        if key == "api-token":
            key = "api_token"
            value = get_api_token()
            # Mask token for security
            if value:
                value = value[:4] + "..." + value[-4:]
        elif key == "org_id":
            value = get_org_id()
        else:
            from .config import get_config_value
            value = get_config_value(key)
        
        return {
            "status": "success",
            "key": key,
            "value": value
        }
    
    else:
        return {
            "status": "error",
            "error": "Invalid action",
            "details": "The action must be 'set' or 'get'."
        }


def handle_list_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'list' command to list agent runs.
    
    Args:
        args: Command arguments including:
            - status: Filter by status (optional)
            - limit: Maximum number of runs to return (optional)
            - repo: Filter by repository (optional)
    
    Returns:
        Response dictionary with list of agent runs
    """
    # Get API credentials
    api_token = get_api_token()
    org_id = get_org_id()
    
    if not api_token:
        return {
            "status": "error",
            "error": "API token not configured",
            "details": "Use 'codegenapi config set api-token YOUR_TOKEN' to configure your API token."
        }
    
    if not org_id:
        return {
            "status": "error",
            "error": "Organization ID not configured",
            "details": "Use 'codegenapi config set org_id YOUR_ORG_ID' to configure your organization ID."
        }
    
    # Parse arguments
    status = args.get("status")
    limit = int(args.get("limit", 20))
    repo = args.get("repo")
    
    try:
        # Initialize client
        config = ClientConfig(
            api_token=api_token,
            org_id=org_id,
            base_url=get_base_url()
        )
        
        client = CodegenClient(config)
        
        # Get agent runs
        runs = client.list_agent_runs(int(org_id), limit=limit)
        
        # Filter by status if provided
        if status:
            filtered_runs = [run for run in runs.items if run.status == status]
        else:
            filtered_runs = runs.items
        
        # Filter by repository if provided
        if repo:
            filtered_runs = [
                run for run in filtered_runs 
                if run.metadata and run.metadata.get("repo") == repo
            ]
        
        # Format response
        runs_data = []
        for run in filtered_runs:
            run_data = {
                "id": run.id,
                "status": run.status,
                "created_at": run.created_at,
                "web_url": run.web_url,
                "metadata": run.metadata
            }
            runs_data.append(run_data)
        
        return {
            "status": "success",
            "runs": runs_data,
            "total": len(runs_data),
            "limit": limit
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": "Failed to list agent runs",
            "details": str(e)
        }


def handle_task_status_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'task_status' command to check the status of a task.
    
    Args:
        args: Command arguments including:
            - task_id: Task ID to check
    
    Returns:
        Response dictionary with task status information
    """
    # Validate required arguments
    if "task_id" not in args:
        return {
            "status": "error",
            "error": "Missing required argument: task_id",
            "details": "The task_id argument is required for the task_status command."
        }
    
    # Get task manager
    task_manager = get_task_manager()
    
    # Get task info
    task_info = task_manager.get_task(args["task_id"])
    
    if not task_info:
        return {
            "status": "error",
            "error": "Task not found",
            "details": f"No task found with ID: {args['task_id']}"
        }
    
    # Return response
    return {
        "status": "success",
        "task_id": task_info.task_id,
        "agent_run_id": task_info.agent_run_id,
        "state": task_info.status,
        "result": task_info.result,
        "error": task_info.error,
        "created_at": task_info.created_at,
        "completed_at": task_info.completed_at,
        "web_url": task_info.web_url,
        "metadata": task_info.metadata
    }

