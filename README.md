# Codegen MCP Server

A Model Context Protocol (MCP) server for the Codegen API that enables AI assistants to create and manage agent runs.

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install -e .
```

## Configuration

Before using the MCP server, you need to configure your API token and organization ID:

```bash
# Set API token
export CODEGEN_API_TOKEN=your_api_token

# Set organization ID
export CODEGEN_ORG_ID=your_org_id
```

Alternatively, you can use the `config` command to set these values:

```bash
# Using the MCP server
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{
  "command": "config",
  "args": {
    "action": "set",
    "key": "api_token",
    "value": "your_api_token"
  }
}'

curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{
  "command": "config",
  "args": {
    "action": "set",
    "key": "org_id",
    "value": "your_org_id"
  }
}'
```

## Running the MCP Server

```bash
# Start the MCP server
python -m mcp.server --host localhost --port 8080
```

## MCP Commands

The MCP server supports the following commands:

### 1. Start a New Agent Run

```json
{
  "command": "new",
  "args": {
    "repo": "Zeeeepa/codegen.py",
    "branch": "codegen-bot/code-quality-analysis-plan-1754927688",
    "pr": 9,
    "task": "CREATE_PLAN",
    "query": "Create a comprehensive plan to properly structure codebase",
    "orchestrator_run_id": 12345
  }
}
```

Parameters:
- `repo`: Repository name (required)
- `branch`: Branch name (optional)
- `pr`: PR number (optional)
- `task`: Task type (optional)
- `query`: Task description (required)
- `orchestrator_run_id`: ID of the orchestrator agent run (optional)

### 2. Resume an Agent Run

```json
{
  "command": "resume",
  "args": {
    "agent_run_id": 11745,
    "task": "ANALYZE",
    "query": "Analyze frontend of the codebase",
    "orchestrator_run_id": 12345
  }
}
```

Parameters:
- `agent_run_id`: Agent run ID to resume (required)
- `task`: Task type (optional)
- `query`: Additional instructions (required)
- `orchestrator_run_id`: ID of the orchestrator agent run (optional)

### 3. Configure API Token and Organization ID

```json
{
  "command": "config",
  "args": {
    "action": "set",
    "key": "api-token",
    "value": "YOUR_TOKEN"
  }
}
```

```json
{
  "command": "config",
  "args": {
    "action": "set",
    "key": "org_id",
    "value": "YOUR_ORG_ID"
  }
}
```

Parameters:
- `action`: "set" or "get" (required)
- `key`: Configuration key (required)
- `value`: Configuration value (required for "set" action)

### 4. List Agent Runs

```json
{
  "command": "list",
  "args": {
    "status": "running",
    "limit": 20,
    "repo": "user/repo"
  }
}
```

Parameters:
- `status`: Filter by status (optional)
- `limit`: Maximum number of runs to return (optional, default: 20)
- `repo`: Filter by repository (optional)

### 5. Check Task Status

```json
{
  "command": "task_status",
  "args": {
    "task_id": "task_12345"
  }
}
```

Parameters:
- `task_id`: Task ID to check (required)

## Example Usage

### Start a New Agent Run

```bash
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{
  "command": "new",
  "args": {
    "repo": "Zeeeepa/codegen.py",
    "task": "CREATE_PLAN",
    "query": "Create a comprehensive plan to properly structure codebase"
  }
}'
```

Response:
```json
{
  "status": "success",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_run_id": 12345,
  "state": "running",
  "web_url": "https://codegen.com/runs/12345",
  "message": "Agent run started successfully."
}
```

### Check Task Status

```bash
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{
  "command": "task_status",
  "args": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}'
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

1. When creating a new agent run, you can specify an `orchestrator_run_id` parameter to indicate that this run is a child of another agent run.
2. When a child agent run completes, the MCP server will:
   - If the orchestrator is still running: Send the result directly to the orchestrator (future enhancement)
   - If the orchestrator is not running: Automatically resume the orchestrator with the result

### Example Usage

```json
{
  "command": "new",
  "args": {
    "repo": "Zeeeepa/codegen.py",
    "task": "CREATE_PLAN",
    "query": "Create a comprehensive plan to properly structure codebase",
    "orchestrator_run_id": 12345
  }
}
```

This creates a new agent run that is a child of agent run 12345. When this run completes, the result will be automatically sent to the orchestrator.

## License

MIT
