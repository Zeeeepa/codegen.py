# Codegen API MCP Server

This repository contains a Model Context Protocol (MCP) server implementation for the Codegen API. It allows AI assistants to interact with the Codegen API through MCP tools.

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install -e .
```

## Configuration

Create a `.claude.json` file in your project root:

```json
{
  "codegenapi": {
    "command": "uv",
    "args": [
      "run",
      "mcp/server.py"
    ],
    "env": {
      "CODEGEN_ORG_ID": "YOUR_ORG_ID",
      "CODEGEN_API_TOKEN": "YOUR_API_TOKEN",
      "CODEGEN_DEBUG": "true"
    }
  }
}
```

## Available MCP Tools

The MCP server exposes the following tools:

### 1. Create New Task

```
codegenapi_new
Parameters:
- repo: "https://github.com/user/repo"
- task: "FEATURE_IMPLEMENTATION"
- query: "Implement JWT-based authentication"
- branch: "feature/auth" (optional)
- pr: "123" (optional)
```

### 2. Resume Task

```
codegenapi_resume
Parameters:
- task_id: "12345"
- message: "Please also include error handling" (optional)
```

### 3. List Tasks

```
codegenapi_list
Parameters:
- status: "running" (optional)
- repo: "https://github.com/user/repo" (optional)
- limit: 20 (optional)
```

### 4. Get Task Details

```
codegenapi_get
Parameters:
- task_id: "12345"
- verbose: true (optional)
```

### 5. Cancel Task

```
codegenapi_cancel
Parameters:
- task_id: "12345"
- reason: "Requirements changed" (optional)
```

## CLI Command Reference

For reference, here are the equivalent CLI commands:

```bash
# Create a new task
codegenapi new --repo <URL> --task <TYPE> --query "<DESCRIPTION>"

# With branch targeting
codegenapi new --repo <URL> --branch <BRANCH> --task <TYPE> --query "<DESCRIPTION>"

# With PR targeting
codegenapi new --repo <URL> --pr <NUMBER> --task <TYPE> --query "<DESCRIPTION>"

# Resume a task
codegenapi resume --task-id <ID> --message "Additional instructions"

# List tasks
codegenapi list --status running --repo <URL> --limit 20

# Get task details
codegenapi get --task-id <ID> --verbose

# Cancel a task
codegenapi cancel --task-id <ID> --reason "Requirements changed"
```

## Development

The MCP server is implemented as a Python module that:
1. Registers tools that map directly to Codegen API functions
2. Executes these functions when called by an AI assistant
3. Returns results in the proper MCP format

The main components are:
- `mcp/server.py` - The MCP server implementation
- `mcp/mcp_types.py` - Type definitions for MCP
- `mcp/codegenapi.py` - Codegen API client

