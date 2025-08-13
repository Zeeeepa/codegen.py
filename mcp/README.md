# Codegen MCP Server

A Model Context Protocol (MCP) server for Codegen API integration.

## Overview

This MCP server provides a standardized interface for AI assistants to interact with the Codegen API, enabling:

- Creating new agent runs
- Resuming existing agent runs
- Managing configuration
- Listing agent runs

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py/mcp

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your Codegen API credentials using environment variables:

```bash
export CODEGEN_API_TOKEN=your_api_token
export CODEGEN_ORG_ID=your_org_id
```

Or configure using the MCP server:

```bash
# Using the MCP server directly
python server.py

# In another terminal
curl -X POST http://localhost:8080/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "codegenapi_config",
    "parameters": {
      "action": "set",
      "key": "api_token",
      "value": "your_api_token"
    }
  }'

curl -X POST http://localhost:8080/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "codegenapi_config",
    "parameters": {
      "action": "set",
      "key": "org_id",
      "value": "your_org_id"
    }
  }'
```

## Usage

### Starting the Server

```bash
# Start the MCP server
python server.py

# With custom host and port
python server.py --host 0.0.0.0 --port 8888

# With debug logging
python server.py --debug
```

### Available MCP Tools

#### `codegenapi_new` - Start new agent run

```json
{
  "name": "codegenapi_new",
  "parameters": {
    "repo": "Zeeeepa/codegen.py",
    "branch": "main",
    "pr": 9,
    "task": "CREATE_PLAN",
    "query": "Create a comprehensive plan to properly structure codebase"
  }
}
```

#### `codegenapi_resume` - Resume agent run

```json
{
  "name": "codegenapi_resume",
  "parameters": {
    "agent_run_id": 11745,
    "task": "ANALYZE",
    "query": "analyze frontend of the codebase"
  }
}
```

#### `codegenapi_config` - Manage configuration

```json
{
  "name": "codegenapi_config",
  "parameters": {
    "action": "set",
    "key": "api_token",
    "value": "your_api_token"
  }
}
```

#### `codegenapi_list` - List agent runs

```json
{
  "name": "codegenapi_list",
  "parameters": {
    "status": "running",
    "limit": 20,
    "repo": "user/repo"
  }
}
```

## Integration with AI Assistants

Configure your AI assistant to use this MCP server:

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

## Testing

Run the unit tests:

```bash
python -m unittest test_unit.py
```

Run the integration tests:

```bash
CODEGEN_API_TOKEN=your_api_token CODEGEN_ORG_ID=your_org_id python test_integration.py
```

Test the MCP tools:

```bash
CODEGEN_API_TOKEN=your_api_token CODEGEN_ORG_ID=your_org_id python test_mcp_tools.py
```

## Asynchronous Operation

The MCP server supports asynchronous operation for long-running agent tasks:

1. When an agent run is created, it returns immediately with the run ID
2. The async handler monitors the run in the background
3. When the run completes, the result is stored and can be retrieved

This allows for creating multiple agent runs without blocking.

## License

MIT

