# CodegenAPI - Agent Orchestration Tool

A comprehensive Python SDK and CLI tool for AI agents to orchestrate and delegate tasks to other Codegen agents efficiently.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py
cd codegen.py

# Install in development mode
pip install -e .
```

### Configuration

Set up your environment variables:

```bash
export CODEGEN_API_TOKEN="your_api_token"
export CODEGEN_ORG_ID="your_org_id"
export CODEGEN_BASE_URL="https://codegen-sh-rest-api.modal.run"  # optional
```

### Basic Usage

```bash
# Run the CLI
python main.py --help

# Or use the installed command
codegenapi --help
```

## 🤖 Agent Orchestration Features

### Core Task Management

```bash
# Create a new task
codegenapi new --repo https://github.com/user/repo \
  --task FEATURE_IMPLEMENTATION \
  --query "Implement OAuth2 authentication" \
  --priority high

# Monitor task progress
codegenapi status 12345 --watch

# Resume a paused task
codegenapi resume --task-id 12345 \
  --message "Also add password reset functionality"

# List and filter tasks
codegenapi list --status running --priority high --limit 20
```

### Workflow Orchestration

```bash
# Execute multi-task workflows
codegenapi workflow --file workflow.yaml --mode parallel --max-concurrent 3

# Manage task dependencies
codegenapi deps --task-id 12345 --depends-on 12344,12343 --show

# Multi-agent collaboration
codegenapi collaborate --tasks 12345,12346 --strategy divide-and-conquer
```

### Monitoring & Analytics

```bash
# Real-time monitoring
codegenapi monitor --dashboard --refresh 5 --alerts

# Performance analytics
codegenapi analytics --period day --metrics success-rate --export report.json

# View execution logs
codegenapi logs 12345 --follow --level info
```

### Configuration & Management

```bash
# Manage configuration
codegenapi config --show
codegenapi config --set api.timeout 300

# Template management
codegenapi templates --list
codegenapi templates --show FEATURE_IMPLEMENTATION

# Resource cleanup
codegenapi cleanup --completed --older-than 7d --dry-run
```

## 📁 Project Structure

```
codegen.py/
├── README.md                    # This file
├── main.py                      # Main entry point
├── setup.py                     # Package configuration
├── requirements.txt             # Dependencies
├── tests/                       # All test files
│   ├── __init__.py
│   ├── test_codegenapi.py      # Main test suite
│   ├── test_sdk.py             # SDK tests
│   └── ...
├── codegenapi/                  # Main package
│   ├── __init__.py             # Package exports
│   ├── models.py               # Data models
│   ├── config.py               # Configuration
│   ├── task_manager.py         # Core functionality
│   ├── state_store.py          # Persistence
│   ├── template_loader.py      # Templates
│   ├── codegen_client.py       # API client
│   ├── cli.py                  # CLI parsing
│   ├── main.py                 # CLI entry point
│   └── commands/               # CLI commands
│       ├── new.py              # Task creation
│       ├── status.py           # Status checking
│       ├── workflow.py         # Workflow orchestration
│       ├── collaborate.py      # Multi-agent coordination
│       ├── monitor.py          # Real-time monitoring
│       ├── analytics.py        # Performance analytics
│       └── ...
├── TASKS/                       # Task templates
│   ├── FEATURE_IMPLEMENTATION.md
│   ├── BUG_FIX.md
│   ├── CODE_RESTRUCTURE.md
│   └── ...
└── examples/                    # Usage examples
    ├── basic_usage.py
    └── cli_examples.sh
```

## 🛠️ Python SDK Usage

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

# Monitor progress
while task.status in ["pending", "running"]:
    task.refresh()
    print(f"Status: {task.status}")
    time.sleep(5)

# Get results
if task.status == "completed":
    print(f"Task completed: {task.result}")
```

## 🎯 Agent Orchestration Capabilities

### Task Types
- **FEATURE_IMPLEMENTATION**: New feature development
- **BUG_FIX**: Bug fixing and patches
- **CODE_RESTRUCTURE**: Refactoring and optimization
- **CODEBASE_ANALYSIS**: Code analysis and documentation
- **TEST_GENERATION**: Test creation and validation
- **PLAN_CREATION**: Development planning

### Orchestration Features
- **Sequential Workflows**: Execute tasks in order
- **Parallel Execution**: Run multiple tasks simultaneously
- **Dependency Management**: Handle task dependencies
- **Multi-Agent Collaboration**: Coordinate multiple agents
- **Real-Time Monitoring**: Track progress and performance
- **Resource Management**: Optimize resource usage

### Advanced Features
- **Priority Queuing**: High-priority task execution
- **Agent Specialization**: Route tasks to specialized agents
- **Failure Recovery**: Automatic retry and recovery
- **State Persistence**: Resume interrupted workflows
- **Performance Analytics**: Track and optimize performance
- **Custom Templates**: Create reusable task templates

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_codegenapi.py -v

# Run with coverage
python -m pytest tests/ --cov=codegenapi --cov-report=html
```

## 📚 Documentation

### CLI Help
```bash
# Main help
codegenapi --help

# Command-specific help
codegenapi new --help
codegenapi workflow --help
codegenapi monitor --help
```

### Configuration
Create a `config.yaml` file:

```yaml
api:
  token: your_api_token
  org_id: your_org_id
  base_url: https://codegen-sh-rest-api.modal.run

storage:
  tasks_dir: ~/.codegenapi/tasks
  logs_dir: ~/.codegenapi/logs

defaults:
  timeout: 3600
  priority: medium
  agent_type: fullstack
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Codegen API Documentation](https://docs.codegen.com)
- [GitHub Repository](https://github.com/Zeeeepa/codegen.py)
- [Issue Tracker](https://github.com/Zeeeepa/codegen.py/issues)

---

**Built for AI agents, by AI agents** 🤖✨

