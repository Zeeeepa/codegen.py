#!/usr/bin/env python3
"""
Demonstration of Codegen API MCP Server commands

This script shows the available commands and their usage patterns.
"""

import json
import sys

def print_header(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_command(name, description, parameters, examples):
    """Print command details"""
    print(f"## {name}")
    print(f"\n{description}\n")
    
    print("Parameters:")
    for param, desc in parameters.items():
        print(f"- {param}: {desc}")
    
    print("\nExamples:")
    for example in examples:
        print(f"\n```\n{example}\n```")
    
    print("\n" + "-" * 80 + "\n")

def main():
    """Main function to demonstrate commands"""
    print_header("CODEGEN API MCP SERVER COMMANDS")
    
    print("The Codegen API MCP Server provides the following commands:\n")
    
    # codegenapi_new
    print_command(
        "codegenapi_new",
        "Start a new agent run with repository context.",
        {
            "repo": "Repository URL or name (required)",
            "task": "Task type (e.g., CREATE_PLAN, FEATURE_IMPLEMENTATION, BUG_FIX) (required)",
            "query": "Task description (required)",
            "branch": "Branch name (optional)",
            "pr": "PR number (optional)"
        },
        [
            "# Basic syntax\ncodegenapi new --repo <URL> --task <TYPE> --query \"<DESCRIPTION>\"",
            "# With branch targeting\ncodegenapi new --repo <URL> --branch <BRANCH> --task <TYPE> --query \"<DESCRIPTION>\"",
            "# With PR targeting\ncodegenapi new --repo <URL> --pr <NUMBER> --task <TYPE> --query \"<DESCRIPTION>\"",
            "# Complete example\ncodegenapi new --repo https://github.com/user/repo --branch feature/auth --task FEATURE_IMPLEMENTATION --query \"Implement JWT-based authentication with refresh tokens and role-based access control\""
        ]
    )
    
    # codegenapi_resume
    print_command(
        "codegenapi_resume",
        "Resume an existing agent run with additional instructions.",
        {
            "agent_run_id": "Agent run ID to resume (required)",
            "query": "Additional instructions (required)",
            "task": "Task type for the resume operation (optional)"
        },
        [
            "# Basic syntax\ncodegenapi resume --task-id <ID> --message \"<MESSAGE>\"",
            "# With task type\ncodegenapi resume --task-id <ID> --message \"<MESSAGE>\" --task <TYPE>",
            "# Complete example\ncodegenapi resume --task-id 12345 --message \"Please also include error handling\""
        ]
    )
    
    # codegenapi_list
    print_command(
        "codegenapi_list",
        "List recent agent runs with optional filtering.",
        {
            "status": "Filter by status (pending, running, completed, failed, cancelled, paused) (optional)",
            "limit": "Number of runs to return (default: 10) (optional)",
            "repo": "Filter by repository (optional)"
        },
        [
            "# List all recent tasks\ncodegenapi list",
            "# Filter by status\ncodegenapi list --status running --limit 20",
            "# Filter by repository\ncodegenapi list --repo https://github.com/user/repo"
        ]
    )
    
    # codegenapi_config
    print_command(
        "codegenapi_config",
        "Manage configuration settings for the API client.",
        {
            "action": "Action to perform (set, get, list) (required)",
            "key": "Configuration key (required for set/get)",
            "value": "Configuration value (required for set)"
        },
        [
            "# Set configuration values\ncodegenapi config set api-token YOUR_TOKEN",
            "# Get configuration value\ncodegenapi config get api-token",
            "# List all configuration\ncodegenapi config list"
        ]
    )
    
    print_header("CLAUDE CODE INTEGRATION")
    
    print("To use this MCP server with Claude Code, add the following to your `.claude.json` file:\n")
    
    claude_config = {
        "codegenapi": {
            "command": "uv",
            "args": [
                "--directory",
                "<Project'sRootDir>/mcp",
                "run",
                "server.py"
            ]
        }
    }
    
    print(f"```json\n{json.dumps(claude_config, indent=2)}\n```\n")
    
    print("This will allow Claude Code to use the MCP server to interact with the Codegen API.\n")
    
    print_header("EXAMPLE USAGE")
    
    print("Here are some example commands you can run with the MCP server:\n")
    
    examples = [
        {
            "title": "Create a new feature implementation task",
            "command": "codegenapi new --repo https://github.com/user/repo --branch feature/auth --task FEATURE_IMPLEMENTATION --query \"Implement JWT-based authentication with refresh tokens and role-based access control\"",
            "description": "This will create a new agent run to implement JWT authentication in the specified repository."
        },
        {
            "title": "Resume an existing task with additional instructions",
            "command": "codegenapi resume --task-id 12345 --message \"Please also include error handling\"",
            "description": "This will resume the agent run with ID 12345 and provide additional instructions."
        },
        {
            "title": "List running tasks",
            "command": "codegenapi list --status running --limit 5",
            "description": "This will list up to 5 running agent runs."
        },
        {
            "title": "Configure API token",
            "command": "codegenapi config set api-token YOUR_TOKEN",
            "description": "This will set the API token for the Codegen API client."
        }
    ]
    
    for example in examples:
        print(f"### {example['title']}\n")
        print(f"```\n{example['command']}\n```\n")
        print(f"{example['description']}\n")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    main()
