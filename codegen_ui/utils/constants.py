"""
Constants for the Codegen UI.
"""

# UI constants
PADDING = 10
THEME = "clam"  # Available themes: 'clam', 'alt', 'default', 'classic'

# Agent run status colors
STATUS_COLORS = {
    "pending": "#FFC107",  # Amber
    "running": "#2196F3",  # Blue
    "completed": "#4CAF50",  # Green
    "failed": "#F44336",  # Red
    "cancelled": "#9E9E9E",  # Grey
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

