# CLI Reference

Complete reference for the Codegen command-line interface.

## Installation

After installing the package, the `codegen` command will be available:

```bash
pip install codegen-py
codegen --help
```

## Global Options

All commands support these global options:

- `--help`: Show help message and exit
- `--version`: Show version information

## Commands

### `codegen run`

Execute an agent with a prompt.

```bash
codegen run "Create a PR to fix the login bug"
codegen run "Add unit tests for the user service" --wait --timeout 600
```

**Options:**
- `--wait`: Wait for task completion before exiting
- `--timeout SECONDS`: Timeout in seconds when waiting (default: 300)
- `--poll-interval SECONDS`: Polling interval in seconds (default: 5.0)

### `codegen status`

Check task status or list recent tasks.

```bash
# List recent tasks
codegen status

# Check specific task
codegen status --task-id 123

# Show logs for a task
codegen status --task-id 123 --logs --log-limit 20
```

**Options:**
- `--task-id ID`: Specific task ID to check
- `--limit NUMBER`: Number of tasks to list (default: 10)
- `--logs`: Show recent logs for the task
- `--log-limit NUMBER`: Number of log entries to show (default: 10)

### `codegen config`

Manage configuration settings.

```bash
# Initialize configuration
codegen config init

# Show current configuration
codegen config show

# Set a configuration value
codegen config set --key timeout --value 600

# Set configuration preset
codegen config preset --preset production
```

**Actions:**
- `init`: Initialize configuration interactively
- `show`: Display current configuration
- `set`: Set a configuration value
- `preset`: Set configuration preset

**Options:**
- `--key KEY`: Configuration key (for 'set' action)
- `--value VALUE`: Configuration value (for 'set' action)
- `--preset PRESET`: Preset name (for 'preset' action)

### `codegen monitor`

Monitor running tasks in real-time.

```bash
# Monitor with default settings
codegen monitor

# Custom monitoring interval
codegen monitor --interval 5 --limit 50
```

**Options:**
- `--limit NUMBER`: Number of tasks to monitor (default: 20)
- `--interval SECONDS`: Monitoring interval in seconds (default: 10)

### `codegen logs`

View and follow task logs.

```bash
# Show recent logs
codegen logs 123

# Follow logs in real-time
codegen logs 123 --follow

# Show more logs with pagination
codegen logs 123 --limit 100 --skip 50
```

**Options:**
- `--skip NUMBER`: Number of logs to skip (default: 0)
- `--limit NUMBER`: Number of logs to show (default: 50)
- `--follow`: Follow logs in real-time

### `codegen stats`

Display client statistics and performance metrics.

```bash
codegen stats
```

## Configuration

### Configuration File

The CLI stores configuration in `~/.codegen/config.json`:

```json
{
  "org_id": "your-org-id",
  "token": "your-api-token",
  "preset": "production",
  "default_timeout": 300,
  "poll_interval": 5.0
}
```

### Environment Variables

You can also use environment variables:

```bash
export CODEGEN_ORG_ID="your-org-id"
export CODEGEN_API_TOKEN="your-api-token"
```

### Configuration Presets

Available presets:

- **development**: Fast feedback, minimal caching
- **production**: Balanced performance and reliability  
- **high_throughput**: Optimized for bulk operations
- **low_latency**: Minimal response times
- **batch_processing**: Large-scale batch operations

## Examples

### Basic Workflow

```bash
# Initialize configuration
codegen config init

# Run a simple task
codegen run "What is the current status of the project?"

# Check recent tasks
codegen status

# Monitor running tasks
codegen monitor
```

### Advanced Usage

```bash
# Run with custom timeout and wait for completion
codegen run "Refactor the authentication module" --wait --timeout 1800

# Check specific task with logs
codegen status --task-id 456 --logs --log-limit 50

# Follow logs in real-time
codegen logs 456 --follow

# Set custom configuration
codegen config set --key default_timeout --value 600
codegen config preset --preset high_throughput
```

