# Codegen Python SDK

A comprehensive Python SDK for interacting with the Codegen AI agents API. This SDK provides both a programmatic interface and a command-line tool for managing AI agent tasks.

## 🚀 Features

- **Official SDK Interface**: Compatible with the official Codegen Python SDK
- **Full API Coverage**: Supports all Codegen API endpoints
- **Command Line Interface**: Rich CLI for task management
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive error handling with detailed messages
- **Logging**: Detailed request/response logging for debugging
- **Caching**: Smart caching for improved performance

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make the CLI available globally
chmod +x cli.py
ln -s $(pwd)/cli.py /usr/local/bin/codegenapi
```

## 🔧 Configuration

### Environment Variables

```bash
export CODEGEN_API_TOKEN="your_api_token_here"
export CODEGEN_ORG_ID="your_org_id"
```

### CLI Configuration

```bash
# Configure via CLI
codegenapi config --token your_api_token --org-id your_org_id

# Or specify custom base URL
codegenapi config --token your_api_token --org-id your_org_id --base-url https://api.codegen.com
```

## 💻 SDK Usage

### Basic Example

```python
from codegen_api import Agent

# Initialize the Agent
agent = Agent(
    token="your_api_token_here",
    org_id=323,  # Your organization ID
    base_url="https://api.codegen.com"  # Optional - defaults to this URL
)

# Run an agent with a prompt
task = agent.run(prompt="Which github repos can you currently access?")

# Check the initial status
print(task.status)  # Returns the current status (e.g., "ACTIVE", "COMPLETE", etc.)

# Refresh the task to get updated status
task.refresh()

# Once task is complete, you can access the result
if task.status == "COMPLETE":
    print(task.result)
    print(f"View details: {task.web_url}")
```

### Advanced Usage

```python
from codegen_api import Agent, CodegenAPIError
import time

# Initialize agent
agent = Agent(token="your_token", org_id=323)

try:
    # Create task with metadata
    task = agent.run(
        prompt="Analyze the codebase structure",
        metadata={"project": "my-project", "priority": "high"}
    )
    
    # Wait for completion with polling
    while task.status in ["ACTIVE", "PENDING"]:
        print(f"Status: {task.status}")
        time.sleep(5)
        task.refresh()
    
    # Handle completion
    if task.status == "COMPLETE":
        print("✅ Task completed!")
        print(f"Result: {task.result}")
        
        # Check for pull requests
        if task.github_pull_requests:
            for pr in task.github_pull_requests:
                print(f"PR created: {pr.title} - {pr.url}")
    
except CodegenAPIError as e:
    print(f"API Error: {e.message}")
```

## 🖥️ CLI Usage

### Configuration

```bash
# Set up your credentials
codegenapi config --token sk-your-token --org-id 323

# Verify configuration
codegenapi config --show
```

### Creating Tasks

```bash
# Create a new task
codegenapi new \
  --repo https://github.com/user/repo \
  --task FEATURE_IMPLEMENTATION \
  --query "Add user authentication system"

# With optional parameters
codegenapi new \
  --repo https://github.com/user/repo \
  --branch feature/auth \
  --pr 123 \
  --task BUG_FIX \
  --query "Fix login validation issue"
```

### Managing Tasks

```bash
# Check task status
codegenapi status --task-id 12345

# List recent tasks
codegenapi list

# View task logs (if available)
codegenapi logs --task-id 12345

# Resume a paused task
codegenapi resume --task-id 12345 --query "Continue with the implementation"
```

### Available Task Types

- **Planning & Analysis**: `PLAN_CREATION`, `PLAN_EVALUATION`, `CODEBASE_ANALYSIS`
- **Development**: `FEATURE_IMPLEMENTATION`, `BUG_FIX`, `CODE_RESTRUCTURE`
- **Testing**: `TEST_GENERATION`, `TEST_COVERAGE_IMPROVEMENT`
- **Documentation**: `DOCUMENTATION_GENERATION`, `CODE_COMMENTS`
- **DevOps**: `CI_CD_SETUP`, `GITHUB_WORKFLOW_CREATION`, `DOCKER_CONFIGURATION`
- **Integration**: `THIRD_PARTY_INTEGRATION`

## 🏗️ API Reference

### Agent Class

```python
class Agent:
    def __init__(self, token: str, org_id: Optional[int] = None, base_url: Optional[str] = None)
    def run(self, prompt: str) -> AgentTask
    def get_status(self) -> Optional[Dict[str, Any]]
```

### AgentTask Class

```python
class AgentTask:
    id: int
    org_id: int
    status: str
    result: Optional[str]
    web_url: Optional[str]
    github_pull_requests: Optional[List[GitHubPullRequest]]
    
    def refresh(self) -> None
```

### Error Handling

```python
from codegen_api import CodegenAPIError, ValidationError

try:
    task = agent.run(prompt="")  # Empty prompt
except ValidationError as e:
    print(f"Validation error: {e.message}")
except CodegenAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
```

## 🔍 Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all API requests will be logged with full details
agent = Agent(token="your_token", org_id=323)
```

### Test Mode

```bash
# Run CLI commands in test mode (no actual API calls)
codegenapi new --test-mode --repo test --task CODEBASE_ANALYSIS --query "test"
```

## 📊 Examples

### Example 1: Simple Code Analysis

```python
from codegen_api import Agent
import time

agent = Agent(token="your_token", org_id=323)
task = agent.run(prompt="Analyze the main.py file and suggest improvements")

# Wait for completion
while task.status == "ACTIVE":
    time.sleep(5)
    task.refresh()

print(f"Analysis complete: {task.result}")
```

### Example 2: Feature Implementation

```bash
codegenapi new \
  --repo https://github.com/myorg/myproject \
  --task FEATURE_IMPLEMENTATION \
  --query "Implement user registration with email verification"
```

### Example 3: Bug Fix with PR Context

```bash
codegenapi new \
  --repo https://github.com/myorg/myproject \
  --pr 456 \
  --task BUG_FIX \
  --query "Fix the memory leak in the data processing pipeline"
```

## 🛠️ Development

### Running Tests

```bash
# Run the comprehensive test suite
python3 comprehensive_test.py

# Test the SDK interface
python3 test_sdk.py

# Test CLI functionality
codegenapi --help
```

### Project Structure

```
├── codegen_api.py          # Main SDK implementation
├── cli.py                  # Command-line interface
├── comprehensive_test.py   # Full test suite
├── test_sdk.py            # SDK interface tests
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🔗 API Endpoints

The SDK covers all Codegen API endpoints:

- `POST /v1/organizations/{org_id}/agent/run` - Create agent run
- `GET /v1/organizations/{org_id}/agent/run/{agent_run_id}` - Get agent run
- `GET /v1/organizations/{org_id}/agent/runs` - List agent runs
- `POST /v1/organizations/{org_id}/agent/run/resume` - Resume agent run
- `GET /v1/organizations/{org_id}/agent/run/{agent_run_id}/logs` - Get agent run logs

## 🎯 Current Status

✅ **Working Features:**
- Agent initialization and configuration
- Task creation and status checking
- CLI commands (config, new, status, list, resume)
- Error handling and validation
- API connectivity with https://api.codegen.com
- Task polling and completion detection

⚠️ **Known Issues:**
- Logs endpoint may return 404 for some tasks (API limitation)
- Some task statuses use different casing (ACTIVE vs active)

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the [Codegen Documentation](https://docs.codegen.com)
- Open an issue on GitHub
- Contact support at support@codegen.com
