# Codegen API CLI & Dashboard

Enhanced CLI and Dashboard for Codegen API with workspace management, template support, and comprehensive task lifecycle management.

## Features

### 🚀 Enhanced CLI
- **Template-based task creation** with predefined task types
- **Workspace management** for multi-repository projects  
- **Task lifecycle management** (create, resume, status, cancel)
- **Local state persistence** for offline access
- **Rich output formatting** with tables, JSON, and YAML
- **Live status monitoring** with watch mode

### 📊 Live Dashboard
- **Real-time task monitoring** with auto-refresh
- **Interactive task management** (create, resume, cancel)
- **Analytics and reporting** with charts and metrics
- **Task filtering and search** capabilities
- **Export/import functionality** for data management

### 🏗️ Clean Architecture
- **Separation of concerns** between UI and API integration
- **Modular design** with clear interfaces
- **Extensible template system** for custom task types
- **Comprehensive error handling** and logging
- **Type-safe data models** throughout

## Installation

```bash
# Install the package
pip install -e .

# Install with dashboard dependencies
pip install -e ".[dashboard]"

# Install with development dependencies
pip install -e ".[dev]"
```

## Configuration

Set your Codegen API credentials:

```bash
export CODEGEN_API_TOKEN="sk-your-token-here"
export CODEGEN_ORG_ID="your-org-id"
```

## CLI Usage

### Create a new task
```bash
# Create a feature implementation task
codegenapi new FEATURE_IMPLEMENTATION --repo https://github.com/user/repo

# Create with custom message and priority
codegenapi new BUG_FIX --repo my-repo --message "Fix login issue" --priority high

# Create with workspace and template variables
codegenapi new PLAN_CREATION --repo my-repo --workspace my-workspace --template-vars '{"key": "value"}'

# Dry run to preview
codegenapi new TEST_GENERATION --repo my-repo --dry-run
```

### Check task status
```bash
# List recent tasks
codegenapi status

# Check specific task
codegenapi status 12345

# Watch task with live updates
codegenapi status 12345 --watch

# Show task logs
codegenapi status 12345 --logs

# Filter by status and format
codegenapi status --filter-status ACTIVE --format json
```

### Resume a paused task
```bash
codegenapi resume 12345 --message "Continue with the implementation"
```

### Available Task Types
- `PLAN_CREATION` - Create comprehensive project plans
- `FEATURE_IMPLEMENTATION` - Implement new features
- `BUG_FIX` - Fix bugs and issues
- `CODE_RESTRUCTURE` - Refactor and restructure code
- `CODEBASE_ANALYSIS` - Analyze codebase structure and quality
- `TEST_GENERATION` - Generate comprehensive test suites

## Dashboard Usage

Launch the interactive dashboard:

```bash
# Start the dashboard
streamlit run DASHBOARD/Main.py

# Or with custom port
streamlit run DASHBOARD/Main.py --server.port 8502
```

### Dashboard Features
- **📋 Active Tasks**: View and manage all tasks with real-time updates
- **📈 Analytics**: Task performance metrics and trend analysis
- **➕ Create Task**: Interactive task creation with template support
- **⚙️ Settings**: Configuration and data management

## Project Structure

```
codegenapi/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point
├── main.py                     # CLI router
├── cli.py                      # Argument parsing
├── task_manager.py             # Task lifecycle management
├── state_store.py              # Local task storage
├── codegen_client.py           # Codegen API client
├── template_loader.py          # Template processing
├── config.py                   # Configuration management
├── models.py                   # Data structures
├── exceptions.py               # Error handling
└── commands/
    ├── new.py                  # Task creation
    ├── resume.py               # Task continuation
    └── status.py               # Progress checking

TASKS/                          # Task templates
├── PLAN_CREATION.md
├── CODE_RESTRUCTURE.md
├── FEATURE_IMPLEMENTATION.md
├── BUG_FIX.md
├── CODEBASE_ANALYSIS.md
└── TEST_GENERATION.md

DASHBOARD/                      # Dashboard application
└── Main.py                     # Streamlit dashboard
```

## Architecture

### Clean Separation of Concerns

**CLI Layer** (`cli.py`, `commands/`)
- Command parsing and validation
- User interaction and output formatting
- Progress display and status updates

**Task Management Layer** (`task_manager.py`, `template_loader.py`, `state_store.py`)
- Task lifecycle management
- Template processing and rendering
- Local state persistence and caching

**API Integration Layer** (`codegen_client.py`)
- Direct Codegen API communication
- Error handling and retry logic
- Data transformation and validation

### Key Benefits
- **UI-agnostic business logic** - Same logic powers both CLI and dashboard
- **Offline capabilities** - Local state storage for task metadata
- **Extensible templates** - Easy to add new task types
- **Comprehensive error handling** - Graceful failure handling throughout
- **Type safety** - Full type hints and validation

## Template System

Templates are Markdown files with variable substitution:

```markdown
<!-- TEMPLATE METADATA
Description: Create a comprehensive project plan
Variables: repository, workspace, priority, custom_message
-->

# Project Planning Task

You are tasked with creating a plan for: **{repository}**

## Context
- **Repository**: {repository}
- **Workspace**: {workspace}
- **Priority**: {priority}

## Additional Instructions
{custom_message}
```

### Template Variables
- `{repository}` - Repository URL or name
- `{workspace}` - Workspace name
- `{priority}` - Task priority level
- `{timestamp}` - Current timestamp
- `{custom_message}` - User-provided instructions

## Development

### Running Tests
```bash
pytest tests/
pytest tests/ --cov=codegenapi
```

### Code Formatting
```bash
black codegenapi/
flake8 codegenapi/
mypy codegenapi/
```

### Adding New Task Types
1. Add the task type to `TaskType` enum in `models.py`
2. Create a new template file in `TASKS/`
3. Update CLI argument choices in `cli.py`

### Adding New Commands
1. Create a new command handler in `commands/`
2. Add argument parsing in `cli.py`
3. Route the command in `main.py`

## API Validation Methodology

The implementation includes comprehensive validation to ensure real API functionality:

### 1. **Direct API Integration Testing**
- All API calls use real Codegen endpoints
- No mock functions - only actual API responses
- Comprehensive error handling for all API scenarios

### 2. **End-to-End Workflow Validation**
```bash
# Test complete task lifecycle
codegenapi new FEATURE_IMPLEMENTATION --repo test-repo
codegenapi status --limit 5
codegenapi resume <task-id> --message "Continue"
```

### 3. **Dashboard Real-Time Validation**
- Live API data integration
- Real-time status updates
- Actual task creation and management

### 4. **Error Scenario Testing**
- Invalid authentication handling
- Network failure recovery
- Rate limiting compliance
- Malformed request handling

### 5. **Performance Validation**
- API response time monitoring
- Caching effectiveness measurement
- Concurrent request handling
- Memory usage optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/Zeeeepa/codegen.py/issues)
- Documentation: See inline code documentation
- Examples: Check the `examples/` directory

