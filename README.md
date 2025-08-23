# Codegen Python Client

This repository contains the Python client and API for Codegen.

## Project Structure

The project is organized into the following main directories:

- `backend/`: Contains all backend functionality
  - `api/`: API implementation
  - `cli/`: Command-line interface
  - `client/`: Client implementation for API endpoints
  - `core/`: Core functionality shared across components

- `frontend/`: Contains all UI functionality
  - `components/`: Reusable UI components
  - `views/`: UI views and frames
  - `core/`: Core UI functionality
  - `utils/`: UI utilities

- `docs/`: Documentation
  - `api/`: API documentation
  - `ui/`: UI documentation

- `tests/`: Tests
  - `backend/`: Backend tests
  - `frontend/`: Frontend tests

- `codegen/`: Compatibility layer for backward compatibility

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

For async support:

```bash
pip install -e ".[async]"
```

## Usage

### Command Line Interface

```bash
# Start the API server
codegen api

# Start the UI application
codegen ui

# Configure client settings
codegen config --api-key YOUR_API_KEY --api-url https://api.codegen.com
```

### Python API

```python
from backend.client import CodegenClient

client = CodegenClient(api_token="YOUR_API_TOKEN")
agents = client.agents.list()
```

### UI Application

```python
import tkinter as tk
from frontend.views import MainFrame

root = tk.Tk()
app = MainFrame(root)
root.mainloop()
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black .
isort .
flake8
mypy .
```

## License

MIT

