#!/usr/bin/env python3
"""
Demo script to run the Codegen MCP Server with example commands
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

def main():
    """Run the MCP server and demonstrate commands"""
    print("🚀 Codegen MCP Server Demo\n")
    
    # Create a config directory and file
    config_dir = Path.home() / ".codegenapi"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.json"
    
    # Create a sample config
    config = {
        "api_token": "demo_token_12345",
        "org_id": 123456
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created sample config at {config_file}")
    
    # Start the server in the background
    print("\n🔄 Starting MCP server in the background...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent)
    )
    
    # Wait for server to start
    time.sleep(1)
    
    # Create a JSON file with example commands
    examples_dir = Path(__file__).parent / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    # Example 1: Config command
    config_example = {
        "name": "codegenapi_config",
        "description": "Manage configuration settings",
        "examples": [
            {
                "title": "Set API token",
                "arguments": {
                    "action": "set",
                    "key": "api-token",
                    "value": "your_token_here"
                }
            },
            {
                "title": "Get API token (masked)",
                "arguments": {
                    "action": "get",
                    "key": "api-token"
                }
            },
            {
                "title": "List all configuration",
                "arguments": {
                    "action": "list"
                }
            }
        ]
    }
    
    with open(examples_dir / "config_examples.json", 'w') as f:
        json.dump(config_example, f, indent=2)
    
    # Example 2: New command
    new_example = {
        "name": "codegenapi_new",
        "description": "Start a new agent run",
        "examples": [
            {
                "title": "Basic new agent run",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "task": "CREATE_PLAN",
                    "query": "Create a comprehensive plan to properly structure codebase"
                }
            },
            {
                "title": "With branch targeting",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "branch": "feature/auth",
                    "task": "FEATURE_IMPLEMENTATION",
                    "query": "Implement JWT-based authentication with refresh tokens"
                }
            },
            {
                "title": "With PR targeting",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "pr": 123,
                    "task": "BUG_FIX",
                    "query": "Fix the authentication bug in the login form"
                }
            }
        ]
    }
    
    with open(examples_dir / "new_examples.json", 'w') as f:
        json.dump(new_example, f, indent=2)
    
    # Example 3: Resume command
    resume_example = {
        "name": "codegenapi_resume",
        "description": "Resume an existing agent run",
        "examples": [
            {
                "title": "Basic resume",
                "arguments": {
                    "agent_run_id": 12345,
                    "query": "Please also include error handling"
                }
            },
            {
                "title": "Resume with task context",
                "arguments": {
                    "agent_run_id": 12345,
                    "task": "ANALYZE",
                    "query": "Focus on security vulnerabilities in the authentication flow"
                }
            }
        ]
    }
    
    with open(examples_dir / "resume_examples.json", 'w') as f:
        json.dump(resume_example, f, indent=2)
    
    # Example 4: List command
    list_example = {
        "name": "codegenapi_list",
        "description": "List agent runs",
        "examples": [
            {
                "title": "List recent runs",
                "arguments": {
                    "limit": 10
                }
            },
            {
                "title": "Filter by status",
                "arguments": {
                    "status": "running",
                    "limit": 20
                }
            },
            {
                "title": "Filter by repository",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "limit": 5
                }
            }
        ]
    }
    
    with open(examples_dir / "list_examples.json", 'w') as f:
        json.dump(list_example, f, indent=2)
    
    # Example 5: Orchestration examples
    orchestration_example = {
        "name": "codegenapi_orchestration",
        "description": "Examples of agent orchestration patterns",
        "examples": [
            {
                "title": "Create orchestrator agent",
                "description": "First, create the main orchestrator agent that will coordinate other agents",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "task": "ORCHESTRATE",
                    "query": "Coordinate analysis of the entire codebase"
                }
            },
            {
                "title": "Create child agent with parent ID",
                "description": "Create a child agent that reports back to the orchestrator",
                "arguments": {
                    "repo": "Zeeeepa/codegen.py",
                    "task": "ANALYZE",
                    "query": "Analyze the authentication module",
                    "parent_id": 12345  # Replace with actual orchestrator ID
                }
            },
            {
                "title": "Auto-resume pattern",
                "description": "When child agents complete, they automatically resume the orchestrator with their results",
                "explanation": [
                    "1. The MCP server tracks parent-child relationships between agent runs",
                    "2. When a child agent completes, the server checks if the parent is still active",
                    "3. If the parent is active, the response is sent directly",
                    "4. If the parent is inactive, the server automatically resumes the parent with the child's response",
                    "5. This creates a seamless continuation of the conversation even if the client disconnects"
                ]
            }
        ]
    }
    
    with open(examples_dir / "orchestration_examples.json", 'w') as f:
        json.dump(orchestration_example, f, indent=2)
    
    print("\n✅ Created example command files in the examples directory:")
    print(f"  - {examples_dir / 'config_examples.json'}")
    print(f"  - {examples_dir / 'new_examples.json'}")
    print(f"  - {examples_dir / 'resume_examples.json'}")
    print(f"  - {examples_dir / 'list_examples.json'}")
    print(f"  - {examples_dir / 'orchestration_examples.json'}")
    
    # Create a README with instructions
    readme_content = """# Codegen MCP Server Demo

This directory contains example commands for the Codegen MCP Server.

## 🚀 Running the Server

```bash
cd mcp
uv run server.py
```

## 📋 Example Commands

The `examples` directory contains JSON files with example commands for each tool:

- `config_examples.json` - Configuration management
- `new_examples.json` - Starting new agent runs
- `resume_examples.json` - Resuming existing agent runs
- `list_examples.json` - Listing and filtering agent runs
- `orchestration_examples.json` - Agent orchestration patterns

## 🔄 Agent Orchestration

The MCP server supports advanced agent orchestration with parent-child relationships:

### Parent-Child Relationships

```json
{
  "repo": "Zeeeepa/codegen.py",
  "task": "ANALYZE",
  "query": "Analyze the authentication module",
  "parent_id": 12345  // ID of the orchestrator agent
}
```

### Async Completion Handling

When a child agent completes:
1. The server checks if the parent orchestrator is still running
2. If active: Sends the response directly to the orchestrator
3. If inactive: Automatically resumes the parent with the child's response

### Wait for Completion

Both `codegenapi_new` and `codegenapi_resume` support waiting for completion:

```json
{
  "repo": "Zeeeepa/codegen.py",
  "task": "CREATE_PLAN",
  "query": "Create a quick plan for the project",
  "wait_for_completion": true
}
```

This will block until the agent run completes and return the final result.

## 🔧 Using with MCP Clients

Configure your MCP client to use the server with:

```json
{
  "codegenapi": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/your/project/mcp",
      "run",
      "server.py"
    ],
    "env": {
      "CODEGEN_API_TOKEN": "your_api_token_here",
      "CODEGEN_ORG_ID": "your_org_id_here"
    }
  }
}
```

## 🧪 Testing the Server

You can test the server using the `test_server.py` script:

```bash
cd mcp
uv run python test_server.py
```

This will verify that the server can start up, load configuration, and has all required dependencies.
"""
    
    with open(examples_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"  - {examples_dir / 'README.md'}")
    
    # Terminate the server
    print("\n🛑 Terminating MCP server...")
    server_process.terminate()
    
    print("\n🎉 Demo setup complete! You can now run the server with:")
    print("cd mcp && uv run server.py")
    print("\nAnd use the example commands in the examples directory.")

if __name__ == "__main__":
    main()
