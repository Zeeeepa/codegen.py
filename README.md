# Codegen MCP Server

A Model Context Protocol (MCP) server for [Codegen](https://codegen.com) agent orchestration and automation.

## Features

- **🤖 Agent Orchestration**: Run and manage AI agents programmatically
- **🔄 Orchestrator Tracking**: Automatically handle agent run completion with parent-child relationships
- **⚡ Async Support**: Full async support for long-running agent operations
- **🔧 Simple Configuration**: Easy setup with environment variables or config commands
- **📋 Task Management**: List and monitor agent runs

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install -r mcp/requirements.txt
```

## Configuration

Set your Codegen API credentials using environment variables:

```bash
export CODEGEN_ORG_ID="your-organization-id"
export CODEGEN_API_TOKEN="your-api-token"
```

Or use the `codegenapi_config` tool:

```bash
# Using the MCP tool
codegenapi_config set org_id YOUR_ORG_ID
codegenapi_config set api_token YOUR_API_TOKEN
```

## Running the Server

Start the MCP server using:

```bash
# Using uv
uv --directory <Project'sRootDir>/mcp run server.py

# Or using Python directly
cd mcp
python server.py
```

The server will start on `localhost:8080` by default. You can customize the host and port:

```bash
python server.py --host 0.0.0.0 --port 9000
```

## MCP Tools

### 1. `codegenapi_new` - Start a new agent run

```bash
codegenapi_new --repo <REPO_NAME> --task <TYPE> --query "<DESCRIPTION>" [--branch <BRANCH_NAME>] [--pr <PR_NUMBER>]
```

**Parameters:**
- `repo`: Repository name (e.g., 'Zeeeepa/codegen.py')
- `task`: Task type (e.g., 'CREATE_PLAN', 'ANALYZE')
- `query`: Description of the task
- `branch` (optional): Branch name
- `pr` (optional): PR number
- `wait` (optional): Whether to wait for completion (default: false)
- `timeout` (optional): Timeout in seconds when waiting

**Example:**
```bash
codegenapi_new --repo Zeeeepa/codegen.py --task CREATE_PLAN --query "Create a comprehensive plan to properly structure codebase"
```

### 2. `codegenapi_resume` - Resume agent run

```bash
codegenapi_resume --agent_run_id <RUN_ID> [--query "<DESCRIPTION>"] [--task <TYPE>]
```

**Parameters:**
- `agent_run_id`: ID of the agent run to resume
- `query` (optional): New query to send to the agent
- `task` (optional): Task type
- `wait` (optional): Whether to wait for completion (default: false)
- `timeout` (optional): Timeout in seconds when waiting

**Example:**
```bash
codegenapi_resume --agent_run_id 11745 --query "analyze frontend of the codebase"
```

### 3. `codegenapi_config` - Configure settings

```bash
codegenapi_config <ACTION> [--key <KEY>] [--value <VALUE>]
```

**Parameters:**
- `action`: Action to perform (get, set, list)
- `key` (for get/set): Configuration key
- `value` (for set): Configuration value

**Examples:**
```bash
# Set API token
codegenapi_config set --key api_token --value YOUR_TOKEN

# Set organization ID
codegenapi_config set --key org_id --value YOUR_ORG_ID

# List all configuration
codegenapi_config list
```

### 4. `codegenapi_list` - List agent runs

```bash
codegenapi_list [--status <STATUS>] [--repo <REPO>] [--limit <LIMIT>]
```

**Parameters:**
- `status` (optional): Filter by status (running, completed, failed, cancelled)
- `repo` (optional): Filter by repository
- `limit` (optional): Maximum number of runs to return (default: 20)

**Example:**
```bash
codegenapi_list --status running --repo Zeeeepa/codegen.py --limit 10
```

## Orchestrator Tracking

The MCP server implements a parent-child relationship between agent runs to handle async completion:

1. When an agent run is created, it can specify an orchestrator ID (parent agent)
2. When a child agent run completes:
   - If the orchestrator is still running: The result is sent directly to the orchestrator
   - If the orchestrator is not running: The orchestrator is automatically resumed with the result

This ensures that long-running agent operations can complete even if the client disconnects, with results properly routed back to the parent agent when it reconnects.

## Testing with Real Credentials

You can test the MCP server with these credentials:

```
CODEGEN_ORG_ID=323
CODEGEN_API_TOKEN=sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99
```

## Integration with Claude Code

To use this MCP server with Claude Code, add the following configuration to your `.claude.json`:

```json
{
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
```

## License

MIT

