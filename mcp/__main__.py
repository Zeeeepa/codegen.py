#!/usr/bin/env python3
"""
MCP Server CLI

This module provides a command-line interface for the MCP server.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, List

from .server import main as server_main

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Codegen MCP Server")
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # New command
    new_parser = subparsers.add_parser("new", help="Start a new agent run")
    new_parser.add_argument("--repo", help="Repository name (e.g., 'Zeeeepa/codegen.py')")
    new_parser.add_argument("--branch", help="Branch name")
    new_parser.add_argument("--pr", type=int, help="PR number")
    new_parser.add_argument("--task", help="Task type (e.g., 'CREATE_PLAN', 'ANALYZE')")
    new_parser.add_argument("--query", required=True, help="The prompt/description for the agent run")
    
    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume an existing agent run")
    resume_parser.add_argument("--agent_run_id", type=int, required=True, help="ID of the agent run to resume")
    resume_parser.add_argument("--task", help="Task type (e.g., 'ANALYZE')")
    resume_parser.add_argument("--query", required=True, help="The prompt/description for the resumed run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List agent runs")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of runs to return")
    list_parser.add_argument("--status", help="Filter by status (e.g., 'ACTIVE', 'COMPLETE', 'ERROR')")
    list_parser.add_argument("--repo", help="Filter by repository name")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Get or set configuration values")
    config_parser.add_argument("action", choices=["set", "get"], help="Action to perform")
    config_parser.add_argument("key", help="Configuration key (e.g., 'api_token', 'org_id')")
    config_parser.add_argument("value", nargs="?", help="Value to set (required for 'set' action)")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Get logs for an agent run")
    logs_parser.add_argument("--agent_run_id", type=int, required=True, help="ID of the agent run")
    logs_parser.add_argument("--skip", type=int, default=0, help="Number of logs to skip")
    logs_parser.add_argument("--limit", type=int, default=100, help="Maximum number of logs to return")
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified")
        sys.exit(1)
    
    # Convert args to dict
    args_dict = vars(args)
    command = args_dict.pop("command")
    
    # Remove None values
    args_dict = {k: v for k, v in args_dict.items() if v is not None}
    
    # Execute command
    result = server_main(command, args_dict)
    
    # Print result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
