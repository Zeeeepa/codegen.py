# Codegen.py

A Python client and API for Codegen, providing both a command-line interface and a graphical user interface.

## Project Structure

The project is organized into the following main components:

```
codegen.py/
├── app.py                  # Main entry point
├── backend/                # Backend components
│   ├── api/                # API implementation
│   ├── client/             # Client implementation
│   └── core/               # Core functionality
├── frontend/               # Frontend components
│   ├── components/         # UI components
│   ├── core/               # Core UI functionality
│   ├── utils/              # UI utilities
│   └── views/              # UI views/frames
└── docs/                   # Documentation
    ├── api/                # API documentation
    ├── ui/                 # UI documentation
    └── mockups/            # UI mockups
```

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
from backend import ClientConfig, ConfigPresets
from backend.client import AgentEndpoint

# Configure the client
config = ClientConfig()
config.load_preset(ConfigPresets.DEVELOPMENT)
config.api_token = "YOUR_API_KEY"

# Create an agent endpoint
agent_endpoint = AgentEndpoint(config)

# Get all agents
agents = agent_endpoint.list_agents()
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

