# Codegen API MCP Server

A Model Context Protocol (MCP) server that provides access to Codegen API functionality through four core commands.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mcp
uv sync
```

### 2. Configure API Token

```bash
# Set your API token
codegenapi config set api-token YOUR_TOKEN

# Optionally set organization ID
codegenapi config set org_id YOUR_ORG_ID
```

### 3. Run the Server

The server is designed to be run via uv with the following configuration:

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

## 📋 Available Commands

### `codegenapi_new` - Start New Agent Run

Create a new agent run with repository context.

**Parameters:**
- `repo` (required): Repository name (e.g., "Zeeeepa/codegen.py")
- `task` (required): Task type (e.g., "CREATE_PLAN", "FEATURE_IMPLEMENTATION", "BUG_FIX")
- `query` (required): Task description
- `branch` (optional): Branch name
- `pr` (optional): PR number

**Example:**
```json
{
  "repo": "Zeeeepa/codegen.py",
  "task": "CREATE_PLAN",
  "query": "Create a comprehensive plan to properly structure codebase",
  "branch": "codegen-bot/code-quality-analysis-plan-1754927688"
}
```

### `codegenapi_resume` - Resume Agent Run

Resume an existing agent run with additional instructions.

**Parameters:**
- `agent_run_id` (required): Agent run ID to resume
- `query` (required): Additional instructions
- `task` (optional): Task type for the resume operation

**Example:**
```json
{
  "agent_run_id": 11745,
  "query": "analyze frontend of the codebase",
  "task": "ANALYZE"
}
```

### `codegenapi_config` - Manage Configuration

Manage configuration settings for the API client.

**Parameters:**
- `action` (required): "set", "get", or "list"
- `key` (required for set/get): Configuration key
- `value` (required for set): Configuration value

**Examples:**
```json
// Set API token
{
  "action": "set",
  "key": "api-token",
  "value": "your_token_here"
}

// Get API token (masked)
{
  "action": "get",
  "key": "api-token"
}

// List all configuration
{
  "action": "list"
}
```

### `codegenapi_list` - List Agent Runs

List recent agent runs with optional filtering.

**Parameters:**
- `status` (optional): Filter by status ("pending", "running", "completed", "failed", "cancelled", "paused")
- `limit` (optional): Number of runs to return (default: 10)
- `repo` (optional): Filter by repository

**Example:**
```json
{
  "status": "running",
  "limit": 20,
  "repo": "user/repo"
}
```

## 🔧 Configuration

Configuration is stored in `~/.codegenapi/config.json`. Supported settings:

- `api_token`: Your Codegen API token
- `org_id`: Organization ID (optional, will auto-detect if not set)

You can also use environment variables:
- `CODEGEN_API_TOKEN`: API token
- `CODEGEN_ORG_ID`: Organization ID

## 🧪 Testing

Run the test script to verify everything is working:

```bash
cd mcp
python test_server.py
```

## 📁 File Structure

```
mcp/
├── server.py          # Main MCP server implementation
├── pyproject.toml      # Dependencies and project config
├── test_server.py      # Test script
└── README.md          # This file
```

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

## 🔍 Troubleshooting

### "API token not configured"
Set your API token using the config command:
```bash
codegenapi config set api-token YOUR_TOKEN
```

### "No organization found"
Either set your org_id explicitly or ensure your API token has access to at least one organization:
```bash
codegenapi config set org_id YOUR_ORG_ID
```

### Import errors
Make sure you're running from the correct directory and that the parent `codegen_api.py` file is accessible.

## 🔗 Integration

This MCP server integrates with the existing `codegen_api.py` in the parent directory. It provides a clean interface for AI clients to interact with the Codegen API through the Model Context Protocol.

The server handles:
- Authentication and configuration management
- Agent run creation and management
- Task resumption with additional context
- Listing and filtering of agent runs
- Parent-child relationship tracking and orchestration
- Async completion handling with auto-resume
- Error handling and user-friendly responses

All responses are returned as JSON for easy parsing by AI clients.
