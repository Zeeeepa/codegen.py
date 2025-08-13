# Codegen API MCP Server

This repository contains a Model Context Protocol (MCP) server for the Codegen API, allowing AI assistants to interact with the Codegen API.

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install the package
pip install -e .
```

## Configuration

Set your Codegen API token and organization ID:

```bash
# Using environment variables
export CODEGEN_API_TOKEN=your_api_token
export CODEGEN_ORG_ID=your_org_id

# Or using the CLI
codegenapi config set api-token your_api_token
codegenapi config set org_id your_org_id
```

## Command-Line Interface

The package includes a command-line interface for interacting with the Codegen API:

### Start a new agent run

```bash
codegenapi new --repo Zeeeepa/codegen.py --task CREATE_PLAN --query "Create a comprehensive plan to properly structure codebase"
```

Options:
- `--repo`: Repository name (e.g., 'Zeeeepa/codegen.py')
- `--branch`: Branch name (optional)
- `--pr`: PR number (optional)
- `--task`: Task type (optional)
- `--query`: Task description (required)

### Resume a completed agent run

```bash
codegenapi resume --agent_run_id 11745 --task ANALYZE --query "Analyze frontend of the codebase"
```

Options:
- `--agent_run_id`: Agent run ID to resume (required)
- `--task`: Task type (optional)
- `--query`: Additional instructions (required)

**Note**: Only agent runs with status "COMPLETE" can be resumed. If the agent run is still "ACTIVE", this will fail.

### List agent runs

```bash
# List all agent runs
codegenapi list

# Filter by status
codegenapi list --status running --limit 20

# Filter by repository
codegenapi list --repo Zeeeepa/codegen.py
```

Options:
- `--status`: Filter by status (optional)
- `--limit`: Maximum number of runs to return (default: 20)
- `--repo`: Filter by repository (optional)

### Get logs for an agent run

```bash
codegenapi logs --agent_run_id 11745
```

Options:
- `--agent_run_id`: Agent run ID to get logs for (required)
- `--skip`: Number of logs to skip (default: 0)
- `--limit`: Maximum number of logs to return (default: 100)

## MCP Server

The MCP server provides a Model Context Protocol (MCP) interface for the Codegen API, allowing AI assistants to interact with the API.

### Starting the Server

```bash
# Start the server
codegen-mcp --host localhost --port 8080
```

### MCP Commands

The MCP server supports the following commands:

#### `new` - Start a new agent run

```json
{
  "command": "new",
  "args": {
    "repo": "Zeeeepa/codegen.py",
    "branch": "codegen-bot/code-quality-analysis-plan-1754927688",
    "pr": 9,
    "task": "CREATE_PLAN",
    "query": "Create a comprehensive plan to properly structure codebase"
  }
}
```

Response:
```json
{
  "status": "success",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_run_id": 12345,
  "state": "active",
  "web_url": "https://codegen.com/runs/12345",
  "metadata": {
    "command": "new",
    "repo": "Zeeeepa/codegen.py",
    "task_type": "CREATE_PLAN"
  }
}
```

#### `resume` - Resume a completed agent run

```json
{
  "command": "resume",
  "args": {
    "agent_run_id": 11745,
    "task": "ANALYZE",
    "query": "Analyze frontend of the codebase"
  }
}
```

Response:
```json
{
  "status": "success",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_run_id": 11745,
  "state": "active",
  "web_url": "https://codegen.com/runs/11745",
  "metadata": {
    "command": "resume",
    "task_type": "ANALYZE"
  }
}
```

**Note**: Only agent runs with status "COMPLETE" can be resumed. If the agent run is still "ACTIVE", this will fail.

#### `task_status` - Check the status of a task

```json
{
  "command": "task_status",
  "args": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

Response:
```json
{
  "status": "success",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_run_id": 12345,
  "state": "completed",
  "result": "The comprehensive plan has been created...",
  "error": null,
  "created_at": "2025-08-12T12:34:56.789Z",
  "completed_at": "2025-08-12T12:45:12.345Z",
  "web_url": "https://codegen.com/runs/12345",
  "metadata": {
    "command": "new",
    "repo": "Zeeeepa/codegen.py",
    "task_type": "CREATE_PLAN"
  }
}
```

#### `list` - List agent runs

```json
{
  "command": "list",
  "args": {
    "status": "running",
    "limit": 20,
    "repo": "Zeeeepa/codegen.py"
  }
}
```

Response:
```json
{
  "status": "success",
  "items": [
    {
      "id": 12345,
      "status": "ACTIVE",
      "created_at": "2025-08-12T12:34:56.789Z",
      "web_url": "https://codegen.com/runs/12345",
      "metadata": {
        "repo": "Zeeeepa/codegen.py",
        "task_type": "CREATE_PLAN"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### `logs` - Get logs for an agent run

```json
{
  "command": "logs",
  "args": {
    "agent_run_id": 12345,
    "skip": 0,
    "limit": 100
  }
}
```

Response:
```json
{
  "status": "success",
  "logs": [
    {
      "agent_run_id": 12345,
      "created_at": "2025-08-12T12:34:56.789Z",
      "tool_name": "ripgrep_search",
      "message_type": "ACTION",
      "thought": "I need to search for the user's function in the codebase",
      "observation": {
        "status": "success",
        "results": ["Found 3 matches..."]
      },
      "tool_input": {
        "query": "function getUserData",
        "file_extensions": [".js", ".ts"]
      },
      "tool_output": {
        "matches": 3,
        "files": ["src/user.js", "src/api.ts"]
      }
    }
  ],
  "total_logs": 25,
  "page": 1,
  "size": 100,
  "pages": 1
}
```

## Integration with AI Assistants

To use this MCP server with AI assistants, configure it as follows:

```json
"codegenapi": {
  "command": "uv",
  "args": [
    "--directory",
    "<Project'sRootDir>/mcp",
    "run",
    "server.py"
  ]
}
```

## Asynchronous Operation

The MCP server handles agent runs asynchronously. When you start a new run or resume an existing one, the server returns immediately with a task ID. You can then use the `task_status` command to check the status of the task and retrieve the result when it's completed.

## Orchestrator Tracking

The MCP server supports orchestrator tracking, which allows you to create hierarchical agent runs. This is useful for creating complex workflows where one agent (the orchestrator) creates and manages multiple child agents.

### How It Works

1. Create an orchestrator agent run:
```bash
codegenapi new --task ORCHESTRATOR --query "Orchestrate a complex workflow"
```

2. Create child agent runs with a reference to the orchestrator:
```bash
codegenapi new --task CHILD --query "Perform a specific task" --metadata '{"orchestrator_run_id": 12345}'
```

3. The orchestrator can track the status of its child runs and coordinate their execution.

## Validation

The package includes validation scripts for testing the API endpoints and MCP server:

```bash
# Test the API client
python validate_commands.py

# Test the MCP server
python test_mcp_server.py
```

## License

MIT

