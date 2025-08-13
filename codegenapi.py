#!/usr/bin/env python3
"""
Command-line interface for the Codegen API.

This module provides a command-line interface for interacting with the Codegen API.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional, List

from codegen_api_client import Agent, CodegenClient, ClientConfig, AgentRunStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables or config file."""
    config = {}
    
    # Check environment variables
    if "CODEGEN_API_TOKEN" in os.environ:
        config["api_token"] = os.environ["CODEGEN_API_TOKEN"]
    
    if "CODEGEN_ORG_ID" in os.environ:
        config["org_id"] = os.environ["CODEGEN_ORG_ID"]
    
    # Check config file
    config_dir = os.path.expanduser("~/.codegen")
    config_file = os.path.join(config_dir, "config.json")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                
                if "api_token" in file_config and "api_token" not in config:
                    config["api_token"] = file_config["api_token"]
                
                if "org_id" in file_config and "org_id" not in config:
                    config["org_id"] = file_config["org_id"]
        
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    return config

def save_config(key: str, value: str):
    """Save configuration to config file."""
    config_dir = os.path.expanduser("~/.codegen")
    config_file = os.path.join(config_dir, "config.json")
    
    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Load existing config
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    # Update config
    config[key] = value
    
    # Save config
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config file: {e}")

def handle_new_command(args):
    """Handle the 'new' command."""
    # Load config
    config = load_config()
    
    # Check required config
    if "api_token" not in config:
        logger.error("API token not configured. Use 'codegenapi config set api-token YOUR_TOKEN'")
        return 1
    
    if "org_id" not in config:
        logger.error("Organization ID not configured. Use 'codegenapi config set org_id YOUR_ORG_ID'")
        return 1
    
    # Check required arguments
    if not args.query:
        logger.error("Query is required")
        return 1
    
    # Initialize agent
    agent = Agent(
        org_id=config["org_id"],
        token=config["api_token"]
    )
    
    # Build metadata
    metadata = {}
    
    if args.repo:
        metadata["repo"] = args.repo
    
    if args.branch:
        metadata["branch"] = args.branch
    
    if args.pr:
        metadata["pr"] = args.pr
    
    if args.task:
        metadata["task_type"] = args.task
    
    # Run agent
    task = agent.run(
        prompt=args.query,
        metadata=metadata
    )
    
    # Print result
    print(f"Agent run started with ID: {task.id}")
    print(f"Status: {task.status}")
    print(f"Web URL: {task.web_url}")
    
    return 0

def handle_resume_command(args):
    """Handle the 'resume' command."""
    # Load config
    config = load_config()
    
    # Check required config
    if "api_token" not in config:
        logger.error("API token not configured. Use 'codegenapi config set api-token YOUR_TOKEN'")
        return 1
    
    if "org_id" not in config:
        logger.error("Organization ID not configured. Use 'codegenapi config set org_id YOUR_ORG_ID'")
        return 1
    
    # Check required arguments
    if not args.agent_run_id:
        logger.error("Agent run ID is required")
        return 1
    
    if not args.query:
        logger.error("Query is required")
        return 1
    
    # Initialize agent
    agent = Agent(
        org_id=config["org_id"],
        token=config["api_token"]
    )
    
    # Get task
    task = agent.get_task(int(args.agent_run_id))
    
    # Build metadata
    metadata = {}
    
    if args.task:
        metadata["task_type"] = args.task
    
    # Resume task
    try:
        task.resume(args.query)
        
        # Print result
        print(f"Agent run resumed with ID: {task.id}")
        print(f"Status: {task.status}")
        print(f"Web URL: {task.web_url}")
    
    except Exception as e:
        logger.error(f"Error resuming agent run: {e}")
        return 1
    
    return 0

def handle_config_command(args):
    """Handle the 'config' command."""
    if args.action == "set":
        # Check required arguments
        if not args.key:
            logger.error("Key is required")
            return 1
        
        if not args.value:
            logger.error("Value is required")
            return 1
        
        # Save config
        save_config(args.key, args.value)
        
        print(f"Configuration value '{args.key}' set successfully")
    
    elif args.action == "get":
        # Check required arguments
        if not args.key:
            logger.error("Key is required")
            return 1
        
        # Load config
        config = load_config()
        
        # Get config value
        value = config.get(args.key)
        
        if value:
            # Mask token for security
            if args.key == "api_token":
                value = value[:4] + "..." + value[-4:]
            
            print(f"{args.key}: {value}")
        else:
            print(f"Configuration value '{args.key}' not found")
    
    else:
        logger.error(f"Unknown action: {args.action}")
        return 1
    
    return 0

def handle_list_command(args):
    """Handle the 'list' command."""
    # Load config
    config = load_config()
    
    # Check required config
    if "api_token" not in config:
        logger.error("API token not configured. Use 'codegenapi config set api-token YOUR_TOKEN'")
        return 1
    
    if "org_id" not in config:
        logger.error("Organization ID not configured. Use 'codegenapi config set org_id YOUR_ORG_ID'")
        return 1
    
    # Initialize client
    client = CodegenClient(
        ClientConfig(
            api_token=config["api_token"],
            org_id=config["org_id"]
        )
    )
    
    # Get agent runs
    try:
        runs = client.list_agent_runs(limit=args.limit)
        
        # Filter by status if provided
        if args.status:
            filtered_runs = [run for run in runs.items if run.status == args.status]
        else:
            filtered_runs = runs.items
        
        # Filter by repository if provided
        if args.repo:
            filtered_runs = [
                run for run in filtered_runs 
                if run.metadata and run.metadata.get("repo") == args.repo
            ]
        
        # Print results
        print(f"Found {len(filtered_runs)} agent runs:")
        for run in filtered_runs:
            print(f"ID: {run.id}")
            print(f"Status: {run.status}")
            print(f"Created: {run.created_at}")
            print(f"Web URL: {run.web_url}")
            
            if run.metadata:
                repo = run.metadata.get("repo")
                if repo:
                    print(f"Repository: {repo}")
                
                task_type = run.metadata.get("task_type")
                if task_type:
                    print(f"Task: {task_type}")
            
            print()
    
    except Exception as e:
        logger.error(f"Error listing agent runs: {e}")
        return 1
    
    return 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Codegen API Command-Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # New command
    new_parser = subparsers.add_parser("new", help="Start a new agent run")
    new_parser.add_argument("--repo", help="Repository name (e.g., 'Zeeeepa/codegen.py')")
    new_parser.add_argument("--branch", help="Branch name")
    new_parser.add_argument("--pr", type=int, help="PR number")
    new_parser.add_argument("--task", help="Task type")
    new_parser.add_argument("--query", required=True, help="Task description")
    
    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume an agent run")
    resume_parser.add_argument("--agent_run_id", required=True, help="Agent run ID to resume")
    resume_parser.add_argument("--task", help="Task type")
    resume_parser.add_argument("--query", required=True, help="Additional instructions")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure API token and organization ID")
    config_parser.add_argument("action", choices=["set", "get"], help="Action to perform")
    config_parser.add_argument("key", help="Configuration key")
    config_parser.add_argument("value", nargs="?", help="Configuration value (for 'set' action)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List agent runs")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of runs to return")
    list_parser.add_argument("--repo", help="Filter by repository")
    
    args = parser.parse_args()
    
    if args.command == "new":
        return handle_new_command(args)
    
    elif args.command == "resume":
        return handle_resume_command(args)
    
    elif args.command == "config":
        return handle_config_command(args)
    
    elif args.command == "list":
        return handle_list_command(args)
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())

