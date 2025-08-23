# Codegen UI

A comprehensive Tkinter-based UI for the Codegen Agent API.

## Features

- **Agent Runs Management**: View, create, and manage agent runs with live status updates
- **Starred Runs Dashboard**: Star important agent runs and view them in a dedicated dashboard
- **Projects Management**: View projects and their setup commands
- **Templates Management**: Create, edit, and use templates for agent runs
- **ProRun Mode Support**: Configure and use ProRun mode for agent runs
- **CLI Integration**: Use the UI from the command line

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/codegen.py.git
cd codegen.py

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the UI
python main.py
```

## Architecture

The Codegen UI is built with a modular architecture:

- **Unified Backend**: A comprehensive API client with support for all required endpoints
- **UI Components**: Reusable UI components for displaying agent runs, projects, and templates
- **UI Frames**: Main UI frames for different views
- **Application Controller**: Handles communication between the UI and the API client
- **Event System**: Enables communication between UI components

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific tests
python -m unittest tests.test_unified_backend
python -m unittest tests.test_ui_components
```

### Project Structure

```
codegen.py/
├── main.py                  # Main entry point
├── unified_backend/         # Unified backend package
│   ├── __init__.py
│   ├── client.py            # API client
│   ├── endpoints/           # API endpoints
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── ui/                      # UI package
│   ├── __init__.py
│   ├── application.py       # Main application class
│   ├── components/          # UI components
│   ├── core/                # Core functionality
│   ├── frames/              # UI frames
│   └── utils/               # UI utilities
└── tests/                   # Tests
    ├── test_unified_backend.py
    └── test_ui_components.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

