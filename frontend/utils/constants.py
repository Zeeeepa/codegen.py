"""
Constants for the Enhanced Codegen UI.

This module provides constants for the Enhanced Codegen UI,
including colors, padding, and other UI constants.
"""

# Padding
PADDING = 8

# Colors
COLORS = {
    "primary": "#007bff",
    "secondary": "#6c757d",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "text": "#212529",
    "text_secondary": "#6c757d",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "border": "#dee2e6"
}

# Status colors
STATUS_COLORS = {
    "info": COLORS["info"],
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["danger"],
    "pending": COLORS["warning"],
    "running": COLORS["primary"],
    "completed": COLORS["success"],
    "failed": COLORS["danger"],
    "cancelled": COLORS["secondary"]
}

# Refresh intervals (in milliseconds)
REFRESH_INTERVAL = {
    "agent_list": 5000,
    "agent_detail": 2000,
    "project_list": 10000
}

# API endpoints
API_ENDPOINTS = {
    "login": "/api/v1/auth/login",
    "agent_runs": "/api/v1/agent_runs",
    "agent_run": "/api/v1/agent_runs/{agent_run_id}",
    "agent_run_logs": "/api/v1/agent_runs/{agent_run_id}/logs",
    "agent_run_cancel": "/api/v1/agent_runs/{agent_run_id}/cancel",
    "agent_run_continue": "/api/v1/agent_runs/{agent_run_id}/continue",
    "repositories": "/api/v1/repositories",
    "repository": "/api/v1/repositories/{repository_id}",
    "organizations": "/api/v1/organizations",
    "organization": "/api/v1/organizations/{organization_id}"
}

# Default values
DEFAULTS = {
    "window_width": 1024,
    "window_height": 768,
    "font_family": "Helvetica",
    "font_size": 10,
    "log_level": "INFO",
    "config_file": "config.json",
    "api_url": "https://api.codegen.com",
    "timeout": 30
}

