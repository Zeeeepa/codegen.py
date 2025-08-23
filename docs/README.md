# Codegen API Client

A Python client for interacting with the Codegen API.

## Installation

```bash
pip install codegen-client
```

## Usage

```python
from codegen_client import CodegenClient

# Initialize the client
client = CodegenClient(api_key="your-api-key")

# Get organizations
organizations = client.organizations.get_organizations()
print(f"Found {organizations.total} organizations")

# Get users in an organization
org_id = organizations.items[0].id
users = client.users.get_users(org_id=org_id)
print(f"Found {users.total} users in organization {org_id}")

# Create an agent run
agent_run = client.agents.create_agent_run(
    org_id=org_id,
    prompt="Create a Python function to calculate the Fibonacci sequence",
    repo_id=123,  # Optional repository ID
)
print(f"Created agent run with ID {agent_run.id}")

# Get agent run details
agent_run = client.agents.get_agent_run(org_id=org_id, agent_run_id=agent_run.id)
print(f"Agent run status: {agent_run.status}")

# Create a multi-run agent (run multiple agents and synthesize results)
result = client.multi_run_agent.create_multi_run(
    org_id=org_id,
    prompt="Create a Python function to calculate the Fibonacci sequence",
    concurrency=3,  # Run 3 agents in parallel
    repo_id=123,  # Optional repository ID
)
print(f"Final synthesized output: {result['final']}")
print(f"Number of candidate outputs: {len(result['candidates'])}")
```

## Command Line Interface

The package includes a command-line interface for common operations:

```bash
# List organizations
python cli.py organizations

# List repositories for an organization
python cli.py repositories 123

# List users for an organization
python cli.py users 123

# Create an agent run
python cli.py agent-run 123 "Create a Python function to calculate the Fibonacci sequence"

# Create a multi-run agent (run multiple agents and synthesize results)
python cli.py multi-run-agent 123 "Create a Python function to calculate the Fibonacci sequence" --concurrency 3
```

## Features

- Full support for all Codegen API endpoints
- Type hints and docstrings for better IDE integration
- Automatic pagination handling
- Proper error handling with specific exception types
- Configurable via environment variables or constructor parameters
- MultiRunAgent for running multiple agents concurrently and synthesizing results

## API Endpoints

The client provides access to the following API endpoints:

- Users: `client.users`
- Agents: `client.agents`
- Organizations: `client.organizations`
- Repositories: `client.repositories`
- Integrations: `client.integrations`
- Setup Commands: `client.setup_commands`
- Sandbox: `client.sandbox`
- Agents Alpha: `client.agents_alpha`
- MultiRunAgent: `client.multi_run_agent`

## MultiRunAgent

The MultiRunAgent feature allows you to run multiple agent instances concurrently and synthesize their outputs for better results:

```python
result = client.multi_run_agent.create_multi_run(
    org_id=org_id,
    prompt="Create a Python function to calculate the Fibonacci sequence",
    concurrency=3,  # Run 3 agents in parallel
    repo_id=123,  # Optional repository ID
    model="gpt-4",  # Optional model to use
    temperature=0.7,  # Temperature for generation (0.0-1.0)
    synthesis_temperature=0.2,  # Temperature for synthesis (0.0-1.0)
    synthesis_prompt=None,  # Optional custom prompt for synthesis
    timeout=600.0,  # Maximum seconds to wait for completion
)

# Access the final synthesized output
print(result["final"])

# Access all candidate outputs
for i, candidate in enumerate(result["candidates"]):
    print(f"Candidate {i+1}: {candidate}")

# Access details of all agent runs
for run in result["agent_runs"]:
    print(f"Run {run['id']}: {run['status']}")
```

## Configuration

The client can be configured using environment variables:

- `CODEGEN_API_KEY`: API key for authentication
- `CODEGEN_BASE_URL`: Base URL for the API (default: https://api.codegen.com/v1)
- `CODEGEN_TIMEOUT`: Request timeout in seconds (default: 30)
- `CODEGEN_MAX_RETRIES`: Maximum number of retries for failed requests (default: 3)
- `CODEGEN_USER_AGENT`: User agent string (default: codegen-python-client)

Alternatively, you can provide these values when initializing the client:

```python
client = CodegenClient(
    api_key="your-api-key",
    base_url="https://api.codegen.com/v1",
    timeout=30,
    max_retries=3,
    user_agent="your-app-name",
)
```

## Error Handling

The client provides specific exception types for different error scenarios:

- `CodegenApiError`: Base exception for all API errors
- `CodegenAuthError`: Authentication errors
- `CodegenRateLimitError`: Rate limit exceeded errors
- `CodegenResourceNotFoundError`: Resource not found errors
- `CodegenValidationError`: Request validation errors

Example:

```python
from codegen_client import CodegenClient, CodegenResourceNotFoundError

client = CodegenClient(api_key="your-api-key")

try:
    user = client.users.get_user(org_id=123, user_id=456)
except CodegenResourceNotFoundError:
    print("User not found")
except Exception as e:
    print(f"An error occurred: {str(e)}")
```

## License

MIT

