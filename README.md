# Codegen API MCP Server

This repository contains a Model Context Protocol (MCP) server for the Codegen API, allowing AI assistants to interact with the Codegen API through a standardized interface.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Command-Line Interface](#command-line-interface)
- [MCP Server](#mcp-server)
- [Integration with AI Assistants](#integration-with-ai-assistants)
- [Asynchronous Operation](#asynchronous-operation)
- [Orchestrator Tracking](#orchestrator-tracking)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### System Dependencies (Debian/Ubuntu)

```bash
# Install required system packages
sudo apt update
sudo apt install -y python3-full python3-venv python3-dev build-essential python-is-python3 git curl
```

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

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
python -m codegenapi config set api_token your_api_token
python -m codegenapi config set org_id your_org_id

# Verify configuration
python -m codegenapi config get api_token
python -m codegenapi config get org_id
```

## Command-Line Interface

The package includes a command-line interface for interacting with the Codegen API:

### Start a new agent run

```bash
python -m codegenapi new --repo Zeeeepa/codegen.py --task CREATE_PLAN --query "Create a comprehensive plan to properly structure codebase"
```

Options:
- `--repo`: Repository name (e.g., 'Zeeeepa/codegen.py')
- `--branch`: Branch name (optional)
- `--pr`: PR number (optional)
- `--task`: Task type (optional)
- `--query`: Task description (required)
- `--metadata`: Additional metadata as JSON string (optional)

### Resume a completed agent run

```bash
python -m codegenapi resume --agent_run_id 11745 --task ANALYZE --query "Analyze frontend of the codebase"
```

Options:
- `--agent_run_id`: Agent run ID to resume (required)
- `--task`: Task type (optional)
- `--query`: Additional instructions (required)
- `--metadata`: Additional metadata as JSON string (optional)

**Note**: Only agent runs with status "COMPLETE" can be resumed. If the agent run is still "ACTIVE", this will fail.

### List agent runs

```bash
# List all agent runs
python -m codegenapi list

# Filter by status
python -m codegenapi list --status running --limit 20

# Filter by repository
python -m codegenapi list --repo Zeeeepa/codegen.py
```

Options:
- `--status`: Filter by status (optional)
- `--limit`: Maximum number of runs to return (default: 20)
- `--repo`: Filter by repository (optional)

### Get logs for an agent run

```bash
python -m codegenapi logs --agent_run_id 11745
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
python -m mcp.server --host localhost --port 8081
```

Options:
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 8080)

### Server Endpoint

The server exposes a single endpoint:

```
POST /mcp
```

All commands are sent to this endpoint as JSON objects with the following structure:

```json
{
  "command": "command_name",
  "args": {
    "arg1": "value1",
    "arg2": "value2"
  }
}
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
    "query": "Create a comprehensive plan to properly structure codebase",
    "metadata": {
      "custom_field": "custom_value"
    }
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
    "query": "Analyze frontend of the codebase",
    "metadata": {
      "custom_field": "custom_value"
    }
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

**Note**: Only agent runs with status "COMPLETE" can be resumed. If the agent run is still "ACTIVE", this will fail with an error response.

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

#### `config` - Get or set configuration values

```json
{
  "command": "config",
  "args": {
    "action": "set",
    "key": "api_token",
    "value": "your_api_token"
  }
}
```

Response:
```json
{
  "status": "success",
  "message": "Configuration value 'api_token' set successfully"
}
```

```json
{
  "command": "config",
  "args": {
    "action": "get",
    "key": "api_token"
  }
}
```

Response:
```json
{
  "status": "success",
  "key": "api_token",
  "value": "your_..."
}
```

## Integration with AI Assistants

### Cursor

Add to your `.cursor/settings.json`:

```json
{
  "ai.mcpServers": [
    {
      "name": "codegenapi",
      "command": "uv",
      "args": [
        "/path/to/codegen.py/mcp/server.py"
      ],
      "env": {
        "CODEGEN_ORG_ID": "323",
        "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
      }
    }
  ]
}
```

Alternatively, you can use this configuration:

```json
{
  "ai.mcpServers": [
    {
      "name": "codegenapi",
      "command": "python",
      "args": [
        "-m",
        "mcp.server",
        "--host",
        "localhost",
        "--port",
        "8081"
      ],
      "cwd": "/path/to/codegen.py",
      "env": {
        "CODEGEN_ORG_ID": "323",
        "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
      }
    }
  ]
}
```

### Claude Code

Add to your `.claude-code.json`:

```json
{
  "mcpServers": [
    {
      "name": "codegenapi",
      "command": "uv",
      "args": [
        "/path/to/codegen.py/mcp/server.py"
      ],
      "env": {
        "CODEGEN_ORG_ID": "323",
        "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
      }
    }
  ]
}
```

Alternatively, you can use this configuration:

```json
{
  "mcpServers": [
    {
      "name": "codegenapi",
      "command": "python",
      "args": [
        "-m",
        "mcp.server",
        "--host",
        "localhost",
        "--port",
        "8081"
      ],
      "cwd": "/path/to/codegen.py",
      "env": {
        "CODEGEN_ORG_ID": "323",
        "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
      }
    }
  ]
}
```

### Generic Configuration

For any AI assistant that supports MCP servers:

```json
{
  "codegenapi": {
    "command": "uv",
    "args": [
      "/path/to/codegen.py/mcp/server.py"
    ],
    "env": {
      "CODEGEN_ORG_ID": "323",
      "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    }
  }
}
```

Alternatively, you can use this configuration:

```json
{
  "codegenapi": {
    "command": "python",
    "args": [
      "-m",
      "mcp.server",
      "--host",
      "localhost",
      "--port",
      "8081"
    ],
    "cwd": "/path/to/codegen.py",
    "env": {
      "CODEGEN_ORG_ID": "323",
      "CODEGEN_API_TOKEN": "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    }
  }
}
```

## Asynchronous Operation

The MCP server handles agent runs asynchronously. When you start a new run or resume an existing one, the server returns immediately with a task ID. You can then use the `task_status` command to check the status of the task and retrieve the result when it's completed.

### Workflow

1. Start a new agent run with the `new` command
2. Receive a task ID in the response
3. Periodically check the status of the task with the `task_status` command
4. When the task is completed, retrieve the result from the `task_status` response

### Example

```javascript
// Start a new agent run
const newResponse = await fetch('http://localhost:8081/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    command: 'new',
    args: {
      repo: 'Zeeeepa/codegen.py',
      task: 'CREATE_PLAN',
      query: 'Create a comprehensive plan to properly structure codebase'
    }
  })
});

const newData = await newResponse.json();
const taskId = newData.task_id;

// Poll for task completion
let taskData;
do {
  await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
  
  const statusResponse = await fetch('http://localhost:8081/mcp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      command: 'task_status',
      args: { task_id: taskId }
    })
  });
  
  taskData = await statusResponse.json();
} while (taskData.state === 'active');

// Task is completed
console.log('Task result:', taskData.result);
```

## Server-Sent Events (SSE)

The MCP server also supports Server-Sent Events (SSE) for real-time updates on task status. This allows clients to receive updates without polling.

### SSE Endpoint

```
GET /sse?task_id=550e8400-e29b-41d4-a716-446655440000
```

### Event Types

- `task_update`: Sent when the task status changes
- `task_complete`: Sent when the task is completed
- `task_error`: Sent when the task encounters an error

### Example

```javascript
const eventSource = new EventSource('http://localhost:8081/sse?task_id=550e8400-e29b-41d4-a716-446655440000');

eventSource.addEventListener('task_update', (event) => {
  const data = JSON.parse(event.data);
  console.log('Task update:', data);
});

eventSource.addEventListener('task_complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Task completed:', data);
  eventSource.close();
});

eventSource.addEventListener('task_error', (event) => {
  const data = JSON.parse(event.data);
  console.log('Task error:', data);
  eventSource.close();
});
```

## Orchestrator Tracking

The MCP server supports orchestrator tracking, which allows you to create hierarchical agent runs. This is useful for creating complex workflows where one agent (the orchestrator) creates and manages multiple child agents.

### How It Works

1. Create an orchestrator agent run:
```bash
python -m codegenapi new --task ORCHESTRATOR --query "Orchestrate a complex workflow"
```

2. Create child agent runs with a reference to the orchestrator:
```bash
python -m codegenapi new --task CHILD --query "Perform a specific task" --metadata '{"orchestrator_run_id": 12345}'
```

3. The orchestrator can track the status of its child runs and coordinate their execution.

## Automatic Startup

### Systemd Service (Linux)

Create a systemd service file:

```bash
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/codegen-mcp.service <<EOF
[Unit]
Description=Codegen MCP Server
After=network.target

[Service]
Type=simple
ExecStart=${HOME}/codegen.py/venv/bin/python -m mcp.server --host localhost --port 8081
WorkingDirectory=${HOME}/codegen.py
Restart=on-failure
Environment="CODEGEN_API_TOKEN=your_api_token"
Environment="CODEGEN_ORG_ID=your_org_id"

[Install]
WantedBy=default.target
EOF

# Enable and start the service
systemctl --user daemon-reload
systemctl --user enable codegen-mcp.service
systemctl --user start codegen-mcp.service

# Check status
systemctl --user status codegen-mcp.service

# Enable lingering to allow the service to run even when you're not logged in
loginctl enable-linger $(whoami)
```

### Startup Application (Ubuntu Desktop)

```bash
mkdir -p ~/.config/autostart/
cat > ~/.config/autostart/codegen-mcp.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Codegen MCP Server
Exec=${HOME}/codegen.py/venv/bin/python -m mcp.server --host localhost --port 8081
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
```

## Validation

The package includes validation scripts for testing the API endpoints and MCP server:

```bash
# Test the API client
python validate_commands.py

# Test the MCP server
python test_mcp_server.py
```

## Troubleshooting

### Common Issues

#### "externally-managed-environment" Error

If you see this error when installing the package:

```
error: externally-managed-environment
```

This means you're trying to install packages directly in the system Python environment. Use a virtual environment instead:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

#### "Address already in use" Error

If you see this error when starting the MCP server:

```
OSError: [Errno 98] Address already in use
```

This means the port is already in use. Try a different port:

```bash
python -m mcp.server --host localhost --port 8082
```

#### Metadata Validation Error

If you see a validation error related to metadata:

```
validation errors for AgentRunsResponse
items -> 0 -> metadata
  none is not an allowed value (type=type_error.none.not_allowed)
```

This is fixed in the latest version of the package. Make sure you're using the latest version.

#### API Token or Org ID Not Configured

If you see this error:

```
API token not configured
```

Make sure you've set the API token and org ID:

```bash
python -m codegenapi config set api_token your_api_token
python -m codegenapi config set org_id your_org_id
```

### Debugging

To enable debug logging:

```bash
export CODEGEN_LOG_LEVEL=DEBUG
python -m mcp.server --host localhost --port 8081
```

## License

MIT
