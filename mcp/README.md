# Codegen API MCP Server

A Model Context Protocol (MCP) server for interacting with the Codegen API. This server provides a set of tools that allow AI assistants to create and manage agent runs, retrieve user and organization information, and more.

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py/mcp

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export CODEGEN_ORG_ID=your_organization_id
export CODEGEN_API_TOKEN=your_api_token
```

Or use the configuration tool:

```bash
python -c "from codegen_client import CodegenClient; client = CodegenClient(); client.manage_config(action='set', key='api-token', value='your_api_token'); client.manage_config(action='set', key='org_id', value='your_organization_id')"
```

## Usage

### Starting the Server

```bash
python server.py --host localhost --port 8080
```

### MCP Integration

Add the following to your MCP client configuration:

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

## Available Tools

### User Management

- `codegenapi_get_users` - Get all users in an organization
- `codegenapi_get_user` - Get a specific user by ID
- `codegenapi_get_current_user` - Get information about the currently authenticated user

### Organization Management

- `codegenapi_get_organizations` - Get organizations for the authenticated user

### Agent Management

- `codegenapi_new` - Create a new agent run
- `codegenapi_get_agent_run` - Get agent run details
- `codegenapi_resume` - Resume a paused agent run (only if status is COMPLETE)
- `codegenapi_list` - List agent runs for an organization
- `codegenapi_get_agent_run_logs` - Get logs for an agent run

### Configuration

- `codegenapi_config` - Manage configuration

## Command Line Examples

### Create a New Agent Run

```bash
# Create a new agent run
codegenapi new --repo Zeeeepa/codegen.py --task CREATE_PLAN --query "Create a comprehensive plan to properly structure codebase"

# Optional parameters
codegenapi new --repo Zeeeepa/codegen.py --branch codegen-bot/code-quality-analysis-plan-1754927688 --pr 9 --task CREATE_PLAN --query "Create a comprehensive plan to properly structure codebase"
```

### Resume an Agent Run

```bash
# Resume an agent run
codegenapi resume --agent_run_id 11745 --query "analyze frontend of the codebase"

# Optional parameters
codegenapi resume --agent_run_id 11745 --task ANALYZE --query "analyze frontend of the codebase"
```

### List Agent Runs

```bash
# List recent tasks and their run_ids + repos + statuses
codegenapi list

# Filter by status
codegenapi list --status running --limit 20

# Filter by repository
codegenapi list --repo user/repo
```

### Configuration

```bash
# Set API token
codegenapi config set api-token YOUR_TOKEN

# Set organization ID
codegenapi config set org_id YOUR_ORG_ID
```

## Asynchronous Operation

The MCP server supports asynchronous operation:

1. When an agent run is created, it returns immediately with the run ID
2. The async handler monitors the run in the background
3. When the run completes, the result is stored and can be retrieved

This allows for creating multiple agent runs without blocking, and clients can retrieve the results when they're ready.

## Important Notes

- Agent runs can take a long time to complete
- The `resume` command can only be used if the agent run status is "COMPLETE" (not "ACTIVE")
- The `get_agent_run_logs` endpoint uses the alpha API and may change in the future

