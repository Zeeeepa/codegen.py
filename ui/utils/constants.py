"""
Constants for the Codegen UI.
"""

# Theme
THEME = "clam"  # Use a modern theme

# Padding
PADDING = 10

# Window sizes
DEFAULT_WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (800, 600)

# Colors
COLORS = {
    "PRIMARY": "#2196F3",
    "SECONDARY": "#4CAF50",
    "SUCCESS": "#4CAF50",
    "ERROR": "#F44336",
    "WARNING": "#FFC107",
    "INFO": "#2196F3",
    "RUNNING": "#2196F3",
    "COMPLETED": "#4CAF50",
    "ERROR": "#F44336",
    "PAUSED": "#FFC107",
    "UNKNOWN": "#9E9E9E",
    "SETUP": "#FF9800",
    "STAR": "#FFD700",
}

# Status colors
STATUS_COLORS = {
    "RUNNING": COLORS["RUNNING"],
    "COMPLETED": COLORS["COMPLETED"],
    "ERROR": COLORS["ERROR"],
    "PAUSED": COLORS["PAUSED"],
    "UNKNOWN": COLORS["UNKNOWN"],
}

# Font sizes
FONT_SIZES = {
    "SMALL": 10,
    "NORMAL": 12,
    "LARGE": 14,
    "HEADER": 16,
    "TITLE": 20,
}

# Tab indices
TAB_INDICES = {
    "LOGIN": 0,
    "AGENT_RUNS": 1,
    "STARRED_RUNS": 2,
    "PROJECTS": 3,
    "TEMPLATES": 4,
    "SETTINGS": 5,
}

# API endpoints
API_BASE_URL = "https://api.codegen.com/v1"

# Config keys
CONFIG_KEYS = {
    "API_TOKEN": "api_token",
    "ORG_ID": "org_id",
    "THEME": "theme",
    "WINDOW_SIZE": "window_size",
    "STARRED_RUNS": "starred_runs",
    "STARRED_PROJECTS": "starred_projects",
    "PRORUN_CONFIGS": "prorun_configs",
    "TEMPLATES": "templates",
}

# Event types
EVENT_TYPES = {
    "LOGIN": "login",
    "LOGOUT": "logout",
    "AGENT_RUN_CREATED": "agent_run_created",
    "AGENT_RUN_UPDATED": "agent_run_updated",
    "AGENT_RUN_COMPLETED": "agent_run_completed",
    "AGENT_RUN_ERROR": "agent_run_error",
    "AGENT_RUN_PAUSED": "agent_run_paused",
    "AGENT_RUN_RESUMED": "agent_run_resumed",
    "AGENT_RUN_STARRED": "agent_run_starred",
    "AGENT_RUN_UNSTARRED": "agent_run_unstarred",
    "PROJECT_STARRED": "project_starred",
    "PROJECT_UNSTARRED": "project_unstarred",
    "TEMPLATE_CREATED": "template_created",
    "TEMPLATE_UPDATED": "template_updated",
    "TEMPLATE_DELETED": "template_deleted",
    "PRORUN_CONFIG_CREATED": "prorun_config_created",
    "PRORUN_CONFIG_UPDATED": "prorun_config_updated",
    "PRORUN_CONFIG_DELETED": "prorun_config_deleted",
    "NOTIFICATION_RECEIVED": "notification_received",
    "REFRESH_REQUESTED": "refresh_requested",
}

# Notification types
NOTIFICATION_TYPES = {
    "AGENT_RUN_COMPLETED": "agent_run_completed",
    "AGENT_RUN_ERROR": "agent_run_error",
    "AGENT_RUN_PAUSED": "agent_run_paused",
    "FOLLOW_UP_ACTION_REQUIRED": "follow_up_action_required",
}

# Follow-up action types
FOLLOW_UP_ACTION_TYPES = {
    "REVIEW_PR": "review_pr",
    "APPROVE_PR": "approve_pr",
    "MERGE_PR": "merge_pr",
    "CLOSE_PR": "close_pr",
    "CREATE_ISSUE": "create_issue",
    "COMMENT_ON_ISSUE": "comment_on_issue",
    "CLOSE_ISSUE": "close_issue",
    "CUSTOM": "custom",
}

# ProRun models
PRORUN_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "gemini-pro",
    "gemini-ultra",
    "llama-3-70b",
    "llama-3-8b",
]

# Template categories
TEMPLATE_CATEGORIES = [
    "GENERAL",
    "DEVELOPMENT",
    "DOCUMENTATION",
    "TESTING",
    "DEVOPS",
    "CUSTOM",
]

