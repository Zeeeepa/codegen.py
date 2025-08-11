# Codegen Python SDK & CLI

[![PyPI version](https://badge.fury.io/py/codegen-py.svg)](https://badge.fury.io/py/codegen-py)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Zeeeepa/codegen.py/workflows/Tests/badge.svg)](https://github.com/Zeeeepa/codegen.py/actions)

A comprehensive Python SDK and CLI for the Codegen API, featuring enterprise-grade error handling, intelligent retry mechanisms, and sophisticated task management.

## 🚀 Quick Start

### Installation

```bash
pip install codegen-py
```

### Authentication

```bash
# Set up your API token
codegen config set api-token YOUR_TOKEN

# Verify authentication
codegen auth status
```

### Basic Usage

```bash
# Create a new coding task
codegenapi new --repo https://github.com/user/repo --task PLAN_CREATION --query "Create a plan to add user authentication system"

# Check task status
codegenapi status --task-id 12345

# List recent tasks
codegenapi list --limit 10
```

## 📋 Table of Contents

- [Installation & Setup](#installation--setup)
- [CLI Commands](#cli-commands)
- [Task Types & Examples](#task-types--examples)
- [Enhanced Architecture](#enhanced-architecture)
- [Task Management](#task-management)
- [Configuration](#configuration)
- [Python SDK](#python-sdk)
- [Error Handling](#error-handling)
- [Contributing](#contributing)

## 🛠 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Git (for repository operations)
- Valid Codegen API token

### Install from PyPI

```bash
pip install codegen-py
```

### Install from Source

```bash
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py
pip install -e .
```

### Initial Configuration

```bash
# Interactive setup
codegen config init

# Manual configuration
codegen config set api-token YOUR_TOKEN
codegen config set org-id YOUR_ORG_ID
codegen config set api.base-url https://api.codegen.com  # Optional

# Verify setup
codegen config validate
```

## 🎯 CLI Commands

### Core Commands

#### `codegenapi new` - Create New Task

```bash
# Basic syntax
codegenapi new --repo <URL> --task <TYPE> --query "<DESCRIPTION>" [OPTIONS]

# With branch targeting
codegenapi new --repo <URL> --branch <BRANCH> --task <TYPE> --query "<DESCRIPTION>"

# With PR targeting
codegenapi new --repo <URL> --pr <NUMBER> --task <TYPE> --query "<DESCRIPTION>"
```

#### `codegenapi status` - Check Task Status

```bash
# Check specific task
codegenapi status --task-id 12345

# Watch for updates
codegenapi status --task-id 12345 --watch

# Show detailed logs
codegenapi status --task-id 12345 --logs
```

#### `codegenapi list` - List Tasks

```bash
# List recent tasks
codegenapi list

# Filter by status
codegenapi list --status running --limit 20

# Filter by repository
codegenapi list --repo https://github.com/user/repo
```

#### `codegenapi resume` - Resume Task

```bash
# Resume with additional instructions
codegenapi resume --task-id 12345 --message "Please also include error handling"

# Resume from specific checkpoint
codegenapi resume --task-id 12345 --from-step 3
```

## 📝 Task Types & Examples

### 🎯 Planning Tasks

#### `PLAN_CREATION`
Create comprehensive development plans for features or projects.

```bash
# Feature planning
codegenapi new --repo https://github.com/user/repo \
  --task PLAN_CREATION \
  --query "Create a plan to add user authentication system with JWT tokens, password reset, and 2FA"

# Architecture planning
codegenapi new --repo https://github.com/user/repo \
  --task PLAN_CREATION \
  --query "Plan migration from monolithic to microservices architecture"
```

#### `PLAN_EVALUATION`
Evaluate and improve existing development plans.

```bash
codegenapi new --repo https://github.com/user/repo \
  --task PLAN_EVALUATION \
  --query "Review and optimize the current deployment strategy plan"
```

### 🔧 Implementation Tasks

#### `FEATURE_IMPLEMENTATION`
Implement new features on specific branches.

```bash
# JWT Authentication
codegenapi new --repo https://github.com/user/repo \
  --branch feature/auth \
  --task FEATURE_IMPLEMENTATION \
  --query "Implement JWT-based authentication with refresh tokens and role-based access control"

# API Endpoints
codegenapi new --repo https://github.com/user/repo \
  --branch api/v2 \
  --task API_CREATION \
  --query "Create REST API endpoints for user management with CRUD operations, validation, and pagination"
```

#### `BUG_FIX`
Fix bugs on specific branches or PRs.

```bash
# Fix on PR
codegenapi new --repo https://github.com/user/repo \
  --pr 456 \
  --task BUG_FIX \
  --query "Fix the memory leak in the data processing pipeline"

# Fix on branch
codegenapi new --repo https://github.com/user/repo \
  --branch hotfix/memory-leak \
  --task BUG_FIX \
  --query "Resolve race condition in concurrent user sessions"
```

### 📊 Analysis Tasks

#### `CODEBASE_ANALYSIS`
Analyze code quality, architecture, and technical debt.

```bash
# Quality analysis
codegenapi new --repo https://github.com/user/repo \
  --task CODEBASE_ANALYSIS \
  --query "Analyze code quality and identify technical debt in the authentication module"

# Security analysis
codegenapi new --repo https://github.com/user/repo \
  --task SECURITY_ANALYSIS \
  --query "Perform security audit of API endpoints and identify vulnerabilities"
```

#### `PERFORMANCE_ANALYSIS`
Analyze and optimize performance bottlenecks.

```bash
codegenapi new --repo https://github.com/user/repo \
  --task PERFORMANCE_ANALYSIS \
  --query "Identify and optimize database query performance issues"
```

### 🏗 Restructuring Tasks

#### `CODE_RESTRUCTURE`
Refactor and restructure existing code.

```bash
# Microservices migration
codegenapi new --repo https://github.com/user/repo \
  --branch refactor/services \
  --task CODE_RESTRUCTURE \
  --query "Refactor the monolithic service layer into microservices architecture"

# Clean architecture
codegenapi new --repo https://github.com/user/repo \
  --task CODE_RESTRUCTURE \
  --query "Restructure codebase to follow clean architecture principles"
```

### 📚 Documentation Tasks

#### `DOCUMENTATION_GENERATION`
Generate comprehensive documentation.

```bash
# API documentation
codegenapi new --repo https://github.com/user/repo \
  --task DOCUMENTATION_GENERATION \
  --query "Generate comprehensive API documentation for all REST endpoints with examples"

# Code documentation
codegenapi new --repo https://github.com/user/repo \
  --task DOCUMENTATION_GENERATION \
  --query "Generate inline documentation and README for the authentication module"
```

### 🧪 Testing Tasks

#### `TEST_GENERATION`
Generate comprehensive test suites.

```bash
# Unit tests
codegenapi new --repo https://github.com/user/repo \
  --task TEST_GENERATION \
  --query "Generate unit tests for the user service with 90% coverage"

# Integration tests
codegenapi new --repo https://github.com/user/repo \
  --task TEST_GENERATION \
  --query "Create integration tests for the payment processing workflow"
```

### ⚙️ DevOps Tasks

#### `GITHUB_WORKFLOW_CREATION`
Create CI/CD workflows and automation.

```bash
# CI/CD Pipeline
codegenapi new --repo https://github.com/user/repo \
  --task GITHUB_WORKFLOW_CREATION \
  --query "Create CI/CD workflow for Node.js app with testing, security scanning, and deployment"

# Release automation
codegenapi new --repo https://github.com/user/repo \
  --task GITHUB_WORKFLOW_CREATION \
  --query "Create automated release workflow with semantic versioning and changelog generation"
```

## 🏗 Enhanced Architecture

### Proposed Command Structure

```bash
# Enhanced syntax with context awareness
codegenapi create <TASK_TYPE> \
  --repo <URL> \
  [--target <branch|pr:number|commit:hash>] \
  [--context <file1,file2,dir/*>] \
  [--template <template_name>] \
  [--priority <low|medium|high|urgent>] \
  [--assignee <username>] \
  [--labels <label1,label2>] \
  [--dependencies <task_id1,task_id2>] \
  "<DESCRIPTION>"

# Examples with enhanced syntax
codegenapi create FEATURE_IMPLEMENTATION \
  --repo https://github.com/user/repo \
  --target branch:feature/auth \
  --context "src/auth/*,tests/auth/*" \
  --template jwt_auth \
  --priority high \
  --labels "authentication,security" \
  "Implement JWT authentication with refresh tokens"
```

### Task Management Commands

```bash
# Task lifecycle management
codegenapi task create <TYPE> [OPTIONS] "<DESCRIPTION>"
codegenapi task status <ID> [--watch] [--logs]
codegenapi task resume <ID> [--message "<MESSAGE>"]
codegenapi task pause <ID> [--reason "<REASON>"]
codegenapi task cancel <ID> [--reason "<REASON>"]
codegenapi task clone <ID> [--modifications "<CHANGES>"]

# Batch operations
codegenapi task list [--status <STATUS>] [--repo <URL>] [--assignee <USER>]
codegenapi task bulk-update --status <STATUS> --ids <ID1,ID2,ID3>
codegenapi task dependencies <ID> [--add <DEP_ID>] [--remove <DEP_ID>]

# Advanced querying
codegenapi task search --query "<SEARCH_TERMS>" [--filters "<FILTERS>"]
codegenapi task analytics --repo <URL> [--timeframe <DAYS>]
```

### Workspace Management

```bash
# Workspace operations
codegenapi workspace create <NAME> --repos <URL1,URL2>
codegenapi workspace switch <NAME>
codegenapi workspace list
codegenapi workspace sync [--workspace <NAME>]

# Template management
codegenapi template list [--category <CATEGORY>]
codegenapi template create <NAME> --from-task <TASK_ID>
codegenapi template apply <NAME> --to-repo <URL>
```

## 📁 Task Management System

### Directory Structure

```
TASKS/
├── config.yaml                 # Task configuration and templates
├── templates/                  # Task templates
│   ├── plan_creation.md
│   ├── feature_implementation.md
│   ├── bug_fix.md
│   └── ...
├── active/                     # Active tasks
│   ├── task_12345/
│   │   ├── metadata.json
│   │   ├── progress.log
│   │   └── artifacts/
│   └── ...
├── completed/                  # Completed tasks archive
├── templates/                  # Custom task templates
└── analytics/                  # Task analytics and reports
```

### Configuration System

The `TASKS/config.yaml` file defines task types, templates, and workflows:

```yaml
# Task type definitions and templates
task_types:
  PLAN_CREATION:
    template: "templates/plan_creation.md"
    estimated_duration: "30-60 minutes"
    required_context: ["repository_structure", "existing_docs"]
    output_format: "markdown"
    validation_rules:
      - "must_include_timeline"
      - "must_include_resources"
    
  FEATURE_IMPLEMENTATION:
    template: "templates/feature_implementation.md"
    estimated_duration: "2-8 hours"
    required_context: ["codebase", "tests", "documentation"]
    output_format: "code_changes"
    validation_rules:
      - "must_include_tests"
      - "must_update_docs"
    
  BUG_FIX:
    template: "templates/bug_fix.md"
    estimated_duration: "30 minutes - 4 hours"
    required_context: ["error_logs", "related_code", "test_cases"]
    output_format: "code_changes"
    validation_rules:
      - "must_include_root_cause"
      - "must_include_prevention"

# Workflow definitions
workflows:
  feature_development:
    steps:
      - type: "PLAN_CREATION"
        name: "Create implementation plan"
      - type: "FEATURE_IMPLEMENTATION"
        name: "Implement feature"
        depends_on: ["plan_creation"]
      - type: "TEST_GENERATION"
        name: "Generate tests"
        depends_on: ["feature_implementation"]
      - type: "DOCUMENTATION_GENERATION"
        name: "Update documentation"
        depends_on: ["feature_implementation"]

# Default settings
defaults:
  priority: "medium"
  timeout: "4 hours"
  retry_attempts: 3
  auto_assign: true
  notification_channels: ["email", "slack"]

# Integration settings
integrations:
  github:
    auto_create_branch: true
    auto_create_pr: true
    pr_template: "templates/pr_template.md"
  
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channels:
      - "#development"
      - "#notifications"
  
  jira:
    project_key: "DEV"
    auto_create_ticket: false
```

## 🔧 Configuration

### Configuration Files

The CLI supports multiple configuration sources with the following precedence:

1. Command-line arguments
2. Environment variables
3. Configuration files
4. Default values

#### Configuration File Locations

```bash
# Project-specific (highest priority)
./codegen.yaml
./.codegen.yaml

# User-specific
~/.codegen/config.yaml
~/.codegen.yaml

# System-wide (XDG compliant)
$XDG_CONFIG_HOME/codegen/config.yaml
```

#### Sample Configuration

```yaml
# API Configuration
api:
  base_url: "https://api.codegen.com"
  token: "${CODEGEN_API_TOKEN}"
  org_id: "${CODEGEN_ORG_ID}"
  timeout: 30
  max_retries: 3
  retry_delay: 1.0
  retry_backoff_factor: 2.0

# Output Configuration
output:
  format: "table"  # table, json, yaml
  color: true
  pager: true
  verbose: false

# CLI Behavior
cli:
  confirm_destructive: true
  progress_bars: true
  auto_update_check: true

# Logging
log:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: null
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Task Management
tasks:
  default_priority: "medium"
  auto_assign: true
  workspace_dir: "./TASKS"
  template_dir: "./TASKS/templates"
  max_concurrent: 5
```

### Environment Variables

```bash
# Authentication
export CODEGEN_API_TOKEN="your_token_here"
export CODEGEN_ORG_ID="your_org_id"

# API Configuration
export CODEGEN_API_BASE_URL="https://api.codegen.com"
export CODEGEN_API_TIMEOUT="30"
export CODEGEN_MAX_RETRIES="3"

# Output Configuration
export CODEGEN_OUTPUT_FORMAT="json"
export CODEGEN_LOG_LEVEL="DEBUG"

# Task Configuration
export CODEGEN_WORKSPACE_DIR="./TASKS"
export CODEGEN_MAX_CONCURRENT_TASKS="5"
```

## 🐍 Python SDK

### Basic Usage

```python
from codegen_api import CodegenClient, ClientConfig

# Initialize client
config = ClientConfig(
    api_token="your_token",
    org_id="your_org_id"
)

with CodegenClient(config) as client:
    # Create a new task
    task = client.create_task(
        repo_url="https://github.com/user/repo",
        task_type="FEATURE_IMPLEMENTATION",
        query="Implement user authentication",
        branch="feature/auth"
    )
    
    print(f"Task created: {task.id}")
    
    # Wait for completion
    completed_task = task.wait_for_completion(timeout=3600)
    print(f"Task completed with status: {completed_task.status}")
```

### Advanced Usage

```python
from codegen_api import Agent, TaskManager, WorkflowBuilder

# Advanced task management
task_manager = TaskManager(config)

# Create workflow
workflow = WorkflowBuilder() \
    .add_step("PLAN_CREATION", "Create implementation plan") \
    .add_step("FEATURE_IMPLEMENTATION", "Implement feature", depends_on=["plan"]) \
    .add_step("TEST_GENERATION", "Generate tests", depends_on=["implementation"]) \
    .build()

# Execute workflow
workflow_run = task_manager.execute_workflow(
    workflow=workflow,
    repo_url="https://github.com/user/repo",
    context={"feature": "authentication", "priority": "high"}
)

# Monitor progress
for step in workflow_run.monitor_progress():
    print(f"Step {step.name}: {step.status}")
```

### Error Handling

```python
from codegen_api import CodegenAPIError, RateLimitError, AuthenticationError

try:
    with CodegenClient(config) as client:
        task = client.create_task(...)
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Please check your API token")
    
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    
except CodegenAPIError as e:
    print(f"API error: {e}")
```

## 🛡 Error Handling

The CLI features enterprise-grade error handling with:

- **Comprehensive Error Classification**: 7+ specialized error types
- **Intelligent Retry Mechanisms**: Exponential backoff with rate limit handling
- **Rich Error Display**: Formatted error messages with actionable suggestions
- **Context-Aware Recovery**: Automatic recovery strategies for common issues

### Error Types

| Exit Code | Error Type | Description |
|-----------|------------|-------------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Unexpected error occurred |
| 2 | Configuration Error | Configuration problem |
| 3 | Authentication Error | Authentication failed |
| 4 | Validation Error | Input validation failed |
| 5 | Network Error | Network connectivity issue |
| 6 | Rate Limit Error | Rate limit exceeded |
| 7 | Not Found Error | Resource not found |
| 8 | Timeout Error | Request timed out |
| 9 | Server Error | Server-side error |
| 10 | API Error | Generic API error |

### Troubleshooting

For detailed troubleshooting information, see:
- [Error Handling Guide](docs/error_handling.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Developer Guide](docs/developer_guide.md)

## 🧪 Testing

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=cli --cov=codegen_api

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

### Performance Benchmarks

```bash
# Run error handling benchmarks
python tests/benchmarks/error_performance.py --iterations 1000

# Run retry effectiveness analysis
python tests/benchmarks/retry_effectiveness.py --optimize
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Quality

We maintain high code quality standards:

- **Type Hints**: All code must include type hints
- **Documentation**: Comprehensive docstrings required
- **Testing**: Minimum 90% test coverage
- **Linting**: Code must pass flake8, black, and mypy
- **Security**: Regular security audits with bandit

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: https://docs.codegen.com
- **API Reference**: https://api.codegen.com/docs
- **GitHub Issues**: https://github.com/Zeeeepa/codegen.py/issues
- **PyPI Package**: https://pypi.org/project/codegen-py/
- **Community Forum**: https://community.codegen.com

## 📊 Status

- ✅ **CLI Interface**: Complete with comprehensive error handling
- ✅ **Python SDK**: Full API coverage with async support
- ✅ **Error Handling**: Enterprise-grade with intelligent retry
- ✅ **Configuration**: Multi-source with validation
- ✅ **Testing**: Comprehensive test suite with benchmarks
- ✅ **Documentation**: Complete guides and API reference
- 🚧 **Task Templates**: In development
- 🚧 **Workflow Engine**: In development
- 📋 **Analytics Dashboard**: Planned

---

**Made with ❤️ by the Codegen Team**

