# Codegen.py

A Python client and API for Codegen, providing both a command-line interface and a graphical user interface.

## Project Structure

The project is organized into the following main components:

```
codegen.py/
├── app.py                  # Main entry point
├── backend/                # Backend components
│   ├── api/                # API implementation
│   ├── cli/                # Command-line interface
│   ├── client/             # Client implementation
│   └── core/               # Core functionality
├── frontend/               # Frontend components
│   ├── components/         # UI components
│   ├── core/               # Core UI functionality
│   ├── ui/                 # UI module
│   ├── utils/              # UI utilities
│   └── views/              # UI views/frames
├── codegen/                # Legacy module (for backward compatibility)
└── docs/                   # Documentation
    ├── api/                # API documentation
    ├── ui/                 # UI documentation
    └── mockups/            # UI mockups
```

## Documentation

All documentation is located in the `docs/` directory:

- [API Documentation](docs/api/api_endpoints.md)
- [UI Documentation](docs/ui/codegen_ui_analysis.md)
- [UI Mockups](docs/mockups/agent_management_interface.md)

## Installation

### From PyPI

```bash
pip install codegen-api
```

### From Source

```bash
git clone https://github.com/codegen-sh/codegen.py.git
cd codegen.py
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### UI Installation

```bash
pip install -e ".[ui]"
```

### Async Installation

```bash
pip install -e ".[async]"
```

## Usage

### Command-Line Interface

```bash
# Start the UI
codegen

# Start the API server
codegen api

# Configure client settings
codegen config --api-key YOUR_API_KEY --api-url https://api.codegen.com/v1
```

### Python API

```python
from backend.core.config.client_config import ClientConfig
from backend.core.config.presets import ConfigPresets
from backend.client.endpoints.agents import CodegenClient

# Configure the client
config = ClientConfig()
config.load_preset(ConfigPresets.DEVELOPMENT)
config.api_token = "YOUR_API_KEY"

# Create a client
client = CodegenClient(config)

# Get all agents
agents = client.list_agents(org_id=123)
print(agents)
```

For backward compatibility, you can also use:

```python
from codegen import ClientConfig, ConfigPresets, CodegenClient

# Configure the client
config = ClientConfig()
config.load_preset(ConfigPresets.DEVELOPMENT)
config.api_token = "YOUR_API_KEY"

# Create a client
client = CodegenClient(config)

# Get all agents
agents = client.list_agents(org_id=123)
print(agents)
```

### UI

```bash
# Start the UI
codegen-ui
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
```

## License

MIT
