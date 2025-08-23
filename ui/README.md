# Codegen UI

This folder contains the Tkinter-based UI for the Codegen API client.

## Architecture

The UI is built using a component-based architecture with the following key components:

- **Core**: Contains the core components of the UI, including the controller, event bus, and base component classes.
- **Components**: Contains reusable UI components.
- **Frames**: Contains the main frames of the UI, such as the login frame, agent list frame, etc.
- **Utils**: Contains utility functions and constants.

## Running the UI

To run the UI, use the `app.py` script in the root directory:

```bash
python app.py
```

Or, if you have installed the package:

```bash
codegen-ui
```

## Development

To develop the UI, you can install the package in development mode:

```bash
pip install -e ".[ui,dev]"
```

This will install the package in development mode with the UI and development dependencies.

## Testing

To run the tests, use pytest:

```bash
pytest ui/tests
```

