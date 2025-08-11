# CodegenAPI

A comprehensive Python SDK and CLI tool for agent-to-agent task execution using the Codegen API. This tool is specifically designed for AI agents to efficiently delegate tasks to other Codegen agents.

## Features

- **Agent-Centric Design**: Built specifically for AI agents to call other agents
- **Task Templates**: Pre-built templates for common development tasks
- **State Management**: Persistent task tracking and resumption
- **CLI Interface**: Simple command-line interface for task execution
- **Comprehensive SDK**: Full Python SDK for programmatic access

## Installation

```bash
pip install codegenapi
```

Or install from source:

```bash
git clone https://github.com/Zeeeepa/codegen.py
cd codegen.py
pip install -e .
```

## Quick Start

### 1. Configuration

Set your API credentials:

```bash
export CODEGEN_API_TOKEN="your_api_token"
export CODEGEN_ORG_ID="your_org_id"
```

### 2. CLI Usage

```bash
# Create a new task
codegenapi new --repo https://github.com/user/repo --task FEATURE_IMPLEMENTATION --query "Add user authentication system"

# Check task status
codegenapi status <task_id>

# Resume a task with additional instructions
codegenapi resume --task-id <task_id> --message "Please also add password reset functionality"

# List recent tasks
codegenapi list
```

### 3. Python SDK Usage

```python
from codegenapi import TaskManager, Config

# Initialize
config = Config()
task_manager = TaskManager(config)

# Create a task
task = task_manager.create_task(
    repo_url="https://github.com/user/repo",
    task_type="FEATURE_IMPLEMENTATION",
    query="Add user authentication system"
)

print(f"Task created: {task.id}")

# Check status
task = task_manager.get_task_status(task.id)
print(f"Status: {task.status}")

# Wait for completion
completed_task = task_manager.wait_for_completion(task.id)
print(f"Result: {completed_task.result}")
```

## Available Task Types

The tool includes pre-built templates for common development tasks:

- **PLAN_CREATION**: Create comprehensive development plans
- **CODE_RESTRUCTURE**: Restructure and reorganize codebases
- **FEATURE_IMPLEMENTATION**: Implement new features
- **BUG_FIX**: Fix bugs and issues
- **CODEBASE_ANALYSIS**: Analyze code quality and architecture
- **TEST_GENERATION**: Generate comprehensive test suites

## CLI Commands

### `new` - Create a new task

```bash
codegenapi new --repo <repo_url> --task <task_type> --query "<description>" [options]
```

Options:
- `--pr <number>`: PR number to work on
- `--branch <name>`: Branch name to work on
- `--wait`: Wait for task completion
- `--timeout <seconds>`: Timeout for waiting (default: 300)

### `status` - Check task status

```bash
codegenapi status <task_id> [options]
```

Options:
- `--watch`: Watch for status changes
- `--interval <seconds>`: Watch interval (default: 5)

### `resume` - Resume a task

```bash
codegenapi resume --task-id <task_id> [options]
```

Options:
- `--repo <url>`: Updated repository URL
- `--pr <number>`: Updated PR number
- `--message <text>`: Additional instructions
- `--wait`: Wait for completion
- `--timeout <seconds>`: Timeout for waiting

### `list` - List recent tasks

```bash
codegenapi list [options]
```

Options:
- `--limit <number>`: Number of tasks to show (default: 10)
- `--status <status>`: Filter by status

## Configuration

### Environment Variables

- `CODEGEN_API_TOKEN`: Your Codegen API token (required)
- `CODEGEN_ORG_ID`: Your organization ID (optional, defaults to "1")
- `CODEGEN_BASE_URL`: API base URL (optional)

### Configuration File

Create a `config.yaml` file to customize task templates and settings:

```yaml
# Task type mappings
tasks:
  CUSTOM_TASK: path/to/custom_template.md

# API configuration
api:
  base_url: https://codegen-sh-rest-api.modal.run
  timeout: 300

# Storage configuration
storage:
  tasks_dir: ~/.codegenapi/tasks
  logs_dir: ~/.codegenapi/logs
```

## Task Templates

Task templates are Markdown files that provide structured prompts for different types of development work. Templates support variable substitution:

- `{{repo_url}}`: Repository URL
- `{{query}}`: Task description
- `{{pr_number}}`: PR number
- `{{branch}}`: Branch name
- `{{task_type}}`: Task type

### Creating Custom Templates

1. Create a Markdown template file in the `TASKS/` directory
2. Add variable placeholders using `{{variable_name}}` syntax
3. Update `config.yaml` to map your task type to the template

## Python SDK Reference

### Core Classes

#### `TaskManager`
Main class for managing task lifecycle:

```python
task_manager = TaskManager(config)

# Create task
task = task_manager.create_task(repo_url, task_type, query, pr_number, branch)

# Get status
task = task_manager.get_task_status(task_id)

# Resume task
task = task_manager.resume_task(task_id, additional_prompt)

# Wait for completion
task = task_manager.wait_for_completion(task_id, timeout)
```

#### `Config`
Configuration management:

```python
config = Config()
errors = config.validate()  # Check configuration
```

#### `Task`
Task data model:

```python
task.id          # Task ID
task.status      # TaskStatus enum
task.repo_url    # Repository URL
task.task_type   # Task type
task.query       # Task description
task.result      # Task result (when completed)
task.error_message  # Error message (if failed)
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from codegenapi.exceptions import CodegenAPIError, TaskError, APIError

try:
    task = task_manager.create_task(...)
except TaskError as e:
    print(f"Task error: {e}")
except APIError as e:
    print(f"API error: {e}")
except CodegenAPIError as e:
    print(f"General error: {e}")
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/Zeeeepa/codegen.py
cd codegen.py
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black codegenapi/
flake8 codegenapi/
```

## Examples

### Example 1: Feature Implementation

```bash
codegenapi new \
  --repo https://github.com/myorg/myapp \
  --task FEATURE_IMPLEMENTATION \
  --query "Add OAuth2 authentication with Google and GitHub providers" \
  --wait
```

### Example 2: Bug Fix with PR

```bash
codegenapi new \
  --repo https://github.com/myorg/myapp \
  --task BUG_FIX \
  --pr 123 \
  --query "Fix memory leak in user session management"
```

### Example 3: Code Analysis

```bash
codegenapi new \
  --repo https://github.com/myorg/myapp \
  --task CODEBASE_ANALYSIS \
  --query "Analyze security vulnerabilities and performance bottlenecks"
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- Documentation: [https://docs.codegen.com](https://docs.codegen.com)
- Issues: [GitHub Issues](https://github.com/Zeeeepa/codegen.py/issues)
- API Reference: [https://docs.codegen.com/introduction/api](https://docs.codegen.com/introduction/api)

