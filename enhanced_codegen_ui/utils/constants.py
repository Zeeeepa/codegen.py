"""
Constants for the Enhanced Codegen UI.

This module provides constants for the Enhanced Codegen UI,
including UI settings, colors, and default values.
"""

# UI constants
PADDING = 10
THEME = "clam"  # Available themes: 'clam', 'alt', 'default', 'classic'

# Window settings
DEFAULT_WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (800, 600)

# Colors
COLORS = {
    "primary": "#2196F3",  # Blue
    "secondary": "#4CAF50",  # Green
    "accent": "#FFC107",  # Amber
    "error": "#F44336",  # Red
    "warning": "#FF9800",  # Orange
    "info": "#2196F3",  # Blue
    "success": "#4CAF50",  # Green
    "background": "#FFFFFF",  # White
    "surface": "#F5F5F5",  # Light Grey
    "text": "#212121",  # Dark Grey
    "text_secondary": "#757575",  # Medium Grey
    "divider": "#BDBDBD",  # Light Grey
}

# Status colors
STATUS_COLORS = {
    "pending": COLORS["warning"],
    "running": COLORS["info"],
    "completed": COLORS["success"],
    "failed": COLORS["error"],
    "cancelled": COLORS["text_secondary"],
}

# Agent run steps
AGENT_RUN_STEPS = [
    "initialization",
    "fetching",
    "planning",
    "execution",
    "review",
    "completion",
]

# Default models
DEFAULT_MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-2",
    "claude-instant",
]

# Refresh intervals (in milliseconds)
REFRESH_INTERVAL = {
    "agent_list": 10000,  # 10 seconds
    "agent_detail": 2000,  # 2 seconds
    "agent_logs": 5000,  # 5 seconds
}

# Max items to display
MAX_ITEMS = {
    "agent_list": 50,
    "project_list": 50,
    "logs": 1000,
}

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Font settings
FONTS = {
    "header": ("Helvetica", 16, "bold"),
    "subheader": ("Helvetica", 12, "bold"),
    "body": ("Helvetica", 10),
    "small": ("Helvetica", 8),
    "code": ("Courier", 10),
}

# Icon paths
ICON_PATHS = {
    "app": "icons/app.png",
    "refresh": "icons/refresh.png",
    "add": "icons/add.png",
    "delete": "icons/delete.png",
    "edit": "icons/edit.png",
    "search": "icons/search.png",
    "settings": "icons/settings.png",
    "logout": "icons/logout.png",
    "login": "icons/login.png",
    "agent": "icons/agent.png",
    "project": "icons/project.png",
    "organization": "icons/organization.png",
    "model": "icons/model.png",
    "run": "icons/run.png",
    "cancel": "icons/cancel.png",
    "continue": "icons/continue.png",
    "logs": "icons/logs.png",
    "output": "icons/output.png",
    "details": "icons/details.png",
    "back": "icons/back.png",
}

# Keyboard shortcuts
SHORTCUTS = {
    "refresh": "<F5>",
    "new_agent_run": "<Control-n>",
    "cancel_agent_run": "<Control-c>",
    "continue_agent_run": "<Control-r>",
    "view_agent_run": "<Control-o>",
    "view_agent_runs": "<Control-1>",
    "view_repositories": "<Control-2>",
    "view_create_agent": "<Control-3>",
    "logout": "<Control-l>",
    "settings": "<Control-s>",
    "help": "<F1>",
    "quit": "<Control-q>",
}

# Command line arguments
CLI_COMMANDS = {
    "agent": {
        "description": "Create a new agent run with a prompt, fetch an existing agent run by ID, or pull PR branch.",
        "options": [
            {"name": "--prompt", "short": "-p", "type": "str", "help": "The prompt to send to the agent"},
            {"name": "--id", "type": "int", "help": "Agent run ID to fetch or pull"},
            {"name": "--json", "type": "flag", "help": "Output raw JSON response when fetching"},
            {"name": "--org-id", "type": "int", "help": "Organization ID"},
            {"name": "--model", "type": "str", "help": "Model to use for this agent run"},
            {"name": "--repo-id", "type": "int", "help": "Repository ID to use for this agent run"},
        ],
        "actions": ["pull"],
    },
    "agents": {
        "description": "List and manage agent runs.",
        "options": [
            {"name": "--org-id", "type": "int", "help": "Organization ID"},
            {"name": "--limit", "type": "int", "help": "Maximum number of runs to return"},
            {"name": "--json", "type": "flag", "help": "Output raw JSON response"},
        ],
        "subcommands": ["list", "get"],
    },
    "login": {
        "description": "Store authentication token.",
        "options": [
            {"name": "--token", "type": "str", "help": "API token to store"},
            {"name": "--no-verify", "type": "flag", "help": "Skip token verification"},
        ],
    },
    "logout": {
        "description": "Clear stored authentication token.",
    },
    "org": {
        "description": "Manage and switch between organizations.",
        "options": [
            {"name": "--json", "type": "flag", "help": "Output raw JSON response"},
        ],
        "subcommands": ["list", "switch", "current"],
    },
    "repo": {
        "description": "Manage repository configuration and environment variables.",
        "options": [
            {"name": "--org-id", "type": "int", "help": "Organization ID"},
            {"name": "--json", "type": "flag", "help": "Output raw JSON response"},
        ],
        "subcommands": ["list", "config", "get"],
    },
}

