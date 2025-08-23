# Codegen API Client

A Python client for the Codegen Agent API, providing both synchronous and asynchronous interfaces, a command-line tool, and a Tkinter UI.

## Installation

### Basic Installation

```bash
pip install .
```

### With Async Support

```bash
pip install ".[async]"
```

### With UI Support

```bash
pip install ".[ui]"
```

### Development Installation

```bash
pip install ".[dev]"
```

## Usage

### Python API

#### Synchronous Client

```python
from codegen import CodegenClient, ClientConfig

# Initialize the client with default configuration
client = CodegenClient()

# Or with custom configuration
config = ClientConfig(api_token="your-token", org_id="your-org-id")
client = CodegenClient(config)

# Create an agent run
run = client.create_agent_run(
    org_id=123,
    prompt="Help me refactor this code for better performance"
)

# Get the run status
run_status = client.get_agent_run(org_id=123, agent_run_id=run.id)

# Get run logs
logs = client.get_agent_run_logs(org_id=123, agent_run_id=run.id)
```

#### Asynchronous Client

```python
import asyncio
from codegen import AsyncCodegenClient

async def main():
    async with AsyncCodegenClient() as client:
        # Get current user
        user = await client.get_current_user()
        print(f"Current user: {user.github_username}")
        
        # Create agent run
        run = await client.create_agent_run(
            org_id=123,
            prompt="Help me refactor this code for better performance"
        )
        
        # Wait for completion
        completed_run = await client.wait_for_completion(
            123, run.id, timeout=300
        )
        
        print(f"Run completed with status: {completed_run.status}")

# Run the async function
asyncio.run(main())
```

### Command-Line Interface

The package includes a command-line interface for interacting with the Codegen API.

```bash
# Run an agent
codegen run "Help me refactor this code for better performance"

# List recent agent runs
codegen list

# View logs for a specific run
codegen logs 12345

# Continue a paused or running agent
codegen continue 12345 "Add more details about the refactoring"
```

### Tkinter UI

The package also includes a Tkinter-based UI for interacting with the Codegen API.

```bash
# Run the UI
python codegen_ui.py
```

## Configuration

The client can be configured using environment variables:

- `CODEGEN_API_TOKEN`: API token for authentication
- `CODEGEN_ORG_ID`: Organization ID
- `CODEGEN_API_URL`: Base URL for the API (default: https://api.codegen.com/v1)
- `CODEGEN_LOG_LEVEL`: Logging level (default: INFO)

## API Reference

### Agent Run Logs API

This endpoint allows you to retrieve detailed execution logs for agent runs, providing insights into the agent's thought process, tool usage, and execution flow.

#### Endpoint

```
GET /v1/organizations/{org_id}/agent/run/{agent_run_id}/logs
```

#### Authentication

This endpoint requires API token authentication. Include your token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | integer | Yes | Your organization ID |
| agent_run_id | integer | Yes | The ID of the agent run to retrieve logs for |
| skip | integer | No | Number of logs to skip for pagination (default: 0) |
| limit | integer | No | Maximum number of logs to return (default: 100, max: 100) |

#### Response Structure

The endpoint returns an AgentRunWithLogsResponse object containing the agent run details and paginated logs:

```json
{
  "id": 12345,
  "organization_id": 67890,
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "web_url": "https://app.codegen.com/agent/trace/12345",
  "result": "Task completed successfully",
  "logs": [
    {
      "agent_run_id": 12345,
      "created_at": "2024-01-15T10:30:15Z",
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

#### Agent Run Log Fields

Each log entry in the logs array contains the following fields:

##### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| agent_run_id | integer | The ID of the agent run this log belongs to |
| created_at | string | ISO 8601 timestamp when the log entry was created |
| message_type | string | The type of log entry (see Log Types below) |

##### Agent Reasoning Fields

| Field | Type | Description |
|-------|------|-------------|
| thought | string \| null | The agent's internal reasoning or thought process for this step |

##### Tool Execution Fields

| Field | Type | Description |
|-------|------|-------------|
| tool_name | string \| null | Name of the tool being executed (e.g., "ripgrep_search", "file_write") |
| tool_input | object \| null | JSON object containing the parameters passed to the tool |
| tool_output | object \| null | JSON object containing the tool's execution results |
| observation | object \| string \| null | The agent's observation of the tool execution results or other contextual data |

#### Log Types

The message_type field indicates the type of log entry. Here are the possible values:

##### Plan Agent Types

| Type | Description |
|------|-------------|
| ACTION | The agent is executing a tool or taking an action |
| PLAN_EVALUATION | The agent is evaluating or updating its plan |
| FINAL_ANSWER | The agent is providing its final response or conclusion |
| ERROR | An error occurred during execution |
| USER_MESSAGE | A message from the user (e.g., interruptions or additional context) |
| USER_GITHUB_ISSUE_COMMENT | A comment from a GitHub issue that the agent is processing |

##### PR Agent Types

| Type | Description |
|------|-------------|
| INITIAL_PR_GENERATION | The agent is generating the initial pull request |
| DETECT_PR_ERRORS | The agent is detecting errors in a pull request |
| FIX_PR_ERRORS | The agent is fixing errors found in a pull request |
| PR_CREATION_FAILED | Pull request creation failed |
| PR_EVALUATION | The agent is evaluating a pull request |

##### Commit Agent Types

| Type | Description |
|------|-------------|
| COMMIT_EVALUATION | The agent is evaluating commits |

##### Link Types

| Type | Description |
|------|-------------|
| AGENT_RUN_LINK | A link to another related agent run |

## License

MIT

