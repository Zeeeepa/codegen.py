# Codegen API MCP Server

This is an MCP (Model Context Protocol) server for the Codegen API. It allows AI assistants to interact with the Codegen API to create and manage agent runs.

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
export CODEGEN_ORG_ID=your_org_id
export CODEGEN_API_TOKEN=your_api_token
```

Alternatively, you can use the config command:

```bash
python -m mcp.codegenapi config set org_id your_org_id
python -m mcp.codegenapi config set api-token your_api_token
```

## MCP Integration

Add this to your MCP configuration:

```json
{
  "codegenapi": {
    "command": "python",
    "args": [
      "-m",
      "mcp.server"
    ],
    "env": {
      "CODEGEN_ORG_ID": "your_org_id",
      "CODEGEN_API_TOKEN": "your_api_token"
    }
  }
}
```

### For Cursor

Add to `.cursor/mcp_servers.json`:

```json
{
  "codegenapi": {
    "command": "python",
    "args": [
      "-m",
      "mcp.server"
    ],
    "env": {
      "CODEGEN_ORG_ID": "your_org_id",
      "CODEGEN_API_TOKEN": "your_api_token"
    }
  }
}
```

### For Claude Code

Add to your `.claude.json`:

```json
{
  "mcp_servers": {
    "codegenapi": {
      "command": "python",
      "args": [
        "-m",
        "mcp.server"
      ],
      "env": {
        "CODEGEN_ORG_ID": "your_org_id",
        "CODEGEN_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

## Available Tools

The MCP server provides the following tools:

- `codegenapi_get_users` - Get all users
- `codegenapi_get_user` - Get a specific user
- `codegenapi_get_current_user` - Get the current user
- `codegenapi_get_organizations` - Get all organizations
- `codegenapi_new` - Create a new agent run
- `codegenapi_get_agent_run` - Get an agent run
- `codegenapi_resume` - Resume a paused agent run
- `codegenapi_list` - List agent runs
- `codegenapi_get_agent_run_logs` - Get agent run logs
- `codegenapi_config` - Manage configuration

## Command Line Interface

The MCP server also includes a command line interface for interacting with the Codegen API:

```bash
# Create a new agent run
python -m mcp.codegenapi new --repo user/repo --task CREATE_PLAN --query "Create a plan"

# Resume an agent run
python -m mcp.codegenapi resume --agent_run_id 12345 --query "Continue analysis"

# List agent runs
python -m mcp.codegenapi list --limit 10 --status COMPLETE

# Get agent run details
python -m mcp.codegenapi get --agent_run_id 12345

# Get agent run logs
python -m mcp.codegenapi logs --agent_run_id 12345 --limit 10

# Manage configuration
python -m mcp.codegenapi config set api-token your_api_token
```

## Asynchronous Operation

Agent runs continue in the background on the Codegen servers even if the MCP server or client is stopped. You can retrieve the results later by calling `codegenapi_get_agent_run` with the run ID.

For a fully automated solution, you can use the `--wait` flag with the CLI:

```bash
python -m mcp.codegenapi new --repo user/repo --task TEST --query "Test" --wait
```

This will wait for the agent run to complete and then print the result.

