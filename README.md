# Codegen Dashboard

A simple, focused dashboard for creating and managing Codegen agent runs.

## Features

- **Single Entry Point**: Launch dashboard with one command
- **Simple Interface**: Clean, intuitive UI for agent run management
- **Core Functionality**:
  - Input repository URL
  - Optional PR name/number input
  - Query text (request) input
  - Run button to create agent runs
  - View agent run list with real-time updates
  - Cancel button for active runs

## Quick Start

### 1. Set Environment Variables

```bash
export CODEGEN_API_TOKEN="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
export CODEGEN_ORG_ID="323"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Usage

### Creating Agent Runs

1. **Repository URL**: Enter the GitHub repository URL (required)
2. **PR Name/Number**: Optionally specify a PR name, branch name, or PR number
3. **Request/Query**: Describe what you want the agent to do (required)
4. **Click Run**: Creates the agent run and adds it to the list

### Managing Runs

- **View Runs**: See all your agent runs with status, creation time, and prompt preview
- **Auto Refresh**: Automatically updates the run list every 10 seconds
- **Manual Refresh**: Click the refresh button to update immediately
- **Cancel Runs**: Cancel active runs with the cancel button
- **View Details**: Click the "View" link to see full run details on codegen.com

## Project Structure

```
codegen.py/
├── dashboard.py              # Single entry point dashboard
├── requirements.txt          # Dependencies
├── codegenapi/              # Simplified API client
│   ├── __init__.py          # Package exports
│   ├── codegen_client.py    # API client
│   ├── config.py            # Configuration
│   ├── exceptions.py        # Error handling
│   └── models.py            # Data models
└── README.md                # This file
```

## API Integration

The dashboard uses the Codegen API to:

- Create new agent runs with custom prompts
- List existing agent runs for your organization
- Cancel active agent runs
- Retrieve run status and details

All API calls include proper error handling and user feedback.

## Environment Variables

- `CODEGEN_API_TOKEN`: Your Codegen API token (required)
- `CODEGEN_ORG_ID`: Your organization ID (required)
- `CODEGEN_BASE_URL`: API base URL (optional, defaults to https://api.codegen.com/v1)

## Development

The codebase is intentionally simple and focused:

- **dashboard.py**: Single-file Streamlit application
- **codegenapi/**: Minimal API client with only essential functionality
- **No complex CLI**: Removed unnecessary command-line tools
- **No templates**: Simplified prompt creation
- **No state persistence**: Uses Streamlit session state only

This design prioritizes simplicity and ease of use over advanced features.

