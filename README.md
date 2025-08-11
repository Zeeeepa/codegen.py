# Codegen Python SDK & CLI

A comprehensive Python SDK and command-line interface for [Codegen](https://codegen.com) agent orchestration and automation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/codegen-py.svg)](https://badge.fury.io/py/codegen-py)

## 🚀 Features

- **🤖 Agent Orchestration**: Run and manage AI agents programmatically
- **📋 Task Management**: Monitor task status, logs, and results
- **⚡ CLI Interface**: Comprehensive command-line tools for agent operations
- **🔧 Configuration Management**: Flexible configuration with presets
- **📊 Monitoring & Stats**: Built-in metrics and performance tracking
- **🔄 Async Support**: Full async/await support for high-performance applications
- **🛡️ Error Handling**: Robust error handling with retries and rate limiting
- **💾 Caching**: Intelligent caching for improved performance

## 📦 Installation

```bash
# Install from PyPI
pip install codegen-py

# Install with async support
pip install codegen-py[async]

# Install for development
pip install -e .
```

## 🏃 Quick Start

### Python SDK

```python
from codegen import Agent

# Initialize the agent
agent = Agent(org_id="your-org-id", token="your-api-token")

# Run an agent with a prompt
task = agent.run("Create a PR to fix the login bug")

# Check the status
print(f"Task {task.id}: {task.status}")

# Wait for completion
result = task.wait_for_completion()
if result.github_pull_request:
    print(f"PR created: {result.github_pull_request.url}")
```

### Command Line Interface

```bash
# Initialize configuration
codegen config init

# Run an agent
codegen run "Add unit tests for the user service" --wait

# Check task status
codegen status --task-id 123

# Monitor running tasks
codegen monitor

# View task logs
codegen logs 123 --follow

# Show statistics
codegen stats
```

## 🔧 Configuration

### Environment Variables

```bash
export CODEGEN_ORG_ID="your-organization-id"
export CODEGEN_API_TOKEN="your-api-token"
```

### Configuration File

The CLI automatically creates a config file at `~/.codegen/config.json`:

```json
{
  "org_id": "your-org-id",
  "token": "your-api-token",
  "preset": "production",
  "default_timeout": 300,
  "poll_interval": 5.0
}
```

### Configuration Presets

Choose from optimized presets for different use cases:

- **`development`**: Fast feedback, minimal caching
- **`production`**: Balanced performance and reliability
- **`high_throughput`**: Optimized for bulk operations
- **`low_latency`**: Minimal response times
- **`batch_processing`**: Large-scale batch operations

```python
from codegen.core import ConfigPresets

# Use a preset
config = ConfigPresets.production()
agent = Agent(config=config)
```

## 📚 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `run` | Execute an agent with a prompt | `codegen run "Fix the bug in auth.py"` |
| `status` | Check task status or list tasks | `codegen status --task-id 123` |
| `config` | Manage configuration | `codegen config set --key timeout --value 600` |
| `monitor` | Monitor running tasks | `codegen monitor --interval 10` |
| `logs` | View task logs | `codegen logs 123 --follow` |
| `stats` | Show client statistics | `codegen stats` |

## 🏗️ Project Structure

```
codegen/
├── __init__.py          # Main package exports
├── core.py              # Core client and utilities
├── agents.py            # Agent management
├── tasks.py             # Task handling and monitoring
├── cli.py               # Command-line interface
└── commands/            # CLI command implementations
    ├── __init__.py
    ├── run.py
    ├── status.py
    └── config.py

tests/                   # Comprehensive test suite
├── test_core.py
├── test_agents.py
├── test_tasks.py
├── test_cli.py
└── integration/         # Integration tests
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=codegen --cov-report=html

# Run only unit tests
pytest -m "not integration"

# Run integration tests (requires API credentials)
pytest -m integration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://docs.codegen.com](https://docs.codegen.com)
- **API Reference**: [https://api.codegen.com/docs](https://api.codegen.com/docs)
- **GitHub**: [https://github.com/Zeeeepa/codegen.py](https://github.com/Zeeeepa/codegen.py)
- **PyPI**: [https://pypi.org/project/codegen-py/](https://pypi.org/project/codegen-py/)
- **Issues**: [https://github.com/Zeeeepa/codegen.py/issues](https://github.com/Zeeeepa/codegen.py/issues)

## 🆘 Support

- 📧 Email: [support@codegen.com](mailto:support@codegen.com)
- 💬 Discord: [Join our community](https://discord.gg/codegen)
- 📖 Documentation: [docs.codegen.com](https://docs.codegen.com)

---

Made with ❤️ by the [Codegen](https://codegen.com) team

