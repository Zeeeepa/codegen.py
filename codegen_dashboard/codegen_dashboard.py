"""Codegen Agent Run Management Dashboard"""

import reflex as rx
import requests
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("CODEGEN_API_BASE_URL", "https://api.codegen.com/v1")

class DashboardState(rx.State):
    """Dashboard state management"""
    
    # Agent runs data
    agent_runs: List[Dict[str, Any]] = []
    selected_run_id: Optional[int] = None
    selected_run_logs: str = ""
    loading: bool = False
    error_message: str = ""
    
    # Settings
    api_url: str = API_BASE_URL
    show_settings: bool = False
    
    def load_agent_runs(self):
        """Load agent runs from API"""
        self.loading = True
        self.error_message = ""
        try:
            # Get auth headers
            headers = self._get_auth_headers()
            response = requests.get(f"{self.api_url}/agent_runs", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.agent_runs = data.get("runs", [])
            else:
                self.error_message = f"Failed to load runs: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error loading runs: {str(e)}"
        finally:
            self.loading = False
    
    def _get_auth_headers(self):
        """Get authentication headers for API requests"""
        token = os.getenv("CODEGEN_API_TOKEN")
        org_id = os.getenv("CODEGEN_ORG_ID")
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if org_id:
            headers["X-Organization-ID"] = org_id
        return headers
    
    def create_agent_run(self, prompt: str):
        """Create a new agent run"""
        if not prompt.strip():
            self.error_message = "Prompt cannot be empty"
            return
            
        self.loading = True
        self.error_message = ""
        try:
            headers = self._get_auth_headers()
            payload = {"prompt": prompt, "metadata": {"source": "dashboard"}}
            response = requests.post(f"{self.api_url}/agent_runs", json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                self.load_agent_runs()  # Refresh the list
            else:
                self.error_message = f"Failed to create run: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error creating run: {str(e)}"
        finally:
            self.loading = False
    
    def load_run_logs(self, run_id: int):
        """Load logs for a specific run"""
        self.selected_run_id = run_id
        self.loading = True
        try:
            headers = self._get_auth_headers()
            response = requests.get(f"{self.api_url}/agent_runs/{run_id}/logs", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.selected_run_logs = data.get("logs", "No logs available")
            else:
                self.selected_run_logs = f"Failed to load logs: {response.status_code}"
        except Exception as e:
            self.selected_run_logs = f"Error loading logs: {str(e)}"
        finally:
            self.loading = False
    
    def toggle_settings(self):
        """Toggle settings panel"""
        self.show_settings = not self.show_settings
    
    def update_api_url(self, new_url: str):
        """Update API URL"""
        self.api_url = new_url.strip()

def agent_run_card(run: Dict[str, Any]) -> rx.Component:
    """Component for displaying an agent run card"""
    status_color = {
        "ACTIVE": "green",
        "COMPLETED": "blue", 
        "FAILED": "red",
        "PENDING": "yellow"
    }.get(run.get("status", "UNKNOWN"), "gray")
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(f"Run #{run.get('id', 'N/A')}", size="4"),
                rx.badge(run.get("status", "UNKNOWN"), color_scheme=status_color),
                justify="between",
                width="100%"
            ),
            rx.text(f"Created: {run.get('created_at', 'Unknown')}", size="2", color="gray"),
            rx.hstack(
                rx.button(
                    "View Logs",
                    on_click=DashboardState.load_run_logs(run.get("id")),
                    size="2"
                ),
                rx.cond(
                    run.get("web_url"),
                    rx.link(
                        rx.button("Open in Codegen", size="2", variant="outline"),
                        href=run.get("web_url", ""),
                        is_external=True
                    )
                ),
                spacing="2"
            ),
            spacing="3",
            align="start",
            width="100%"
        ),
        width="100%",
        max_width="400px"
    )

def create_run_form() -> rx.Component:
    """Form for creating new agent runs"""
    return rx.card(
        rx.vstack(
            rx.heading("Create New Agent Run", size="4"),
            rx.text_area(
                placeholder="Enter your prompt here...",
                id="prompt_input",
                width="100%",
                height="100px"
            ),
            rx.button(
                "Create Run",
                on_click=DashboardState.create_agent_run("Test prompt from dashboard"),
                width="100%",
                loading=DashboardState.loading
            ),
            spacing="3",
            width="100%"
        ),
        width="100%",
        max_width="500px"
    )

def settings_panel() -> rx.Component:
    """Settings panel component"""
    return rx.cond(
        DashboardState.show_settings,
        rx.card(
            rx.vstack(
                rx.heading("Settings", size="4"),
                rx.text("API Base URL:", size="2", weight="bold"),
                rx.input(
                    value=DashboardState.api_url,
                    on_change=DashboardState.update_api_url,
                    width="100%"
                ),
                rx.button(
                    "Test Connection",
                    on_click=DashboardState.load_agent_runs,
                    size="2"
                ),
                spacing="3",
                width="100%"
            ),
            width="100%",
            max_width="400px"
        )
    )

def logs_viewer() -> rx.Component:
    """Logs viewer component"""
    return rx.cond(
        DashboardState.selected_run_id,
        rx.card(
            rx.vstack(
                rx.heading(f"Logs for Run #{DashboardState.selected_run_id}", size="4"),
                rx.text_area(
                    value=DashboardState.selected_run_logs,
                    width="100%",
                    height="300px",
                    is_read_only=True,
                    font_family="monospace"
                ),
                rx.button(
                    "Close Logs",
                    on_click=DashboardState.set_selected_run_id(None),
                    variant="outline"
                ),
                spacing="3",
                width="100%"
            ),
            width="100%"
        )
    )

def index() -> rx.Component:
    """Main dashboard page"""
    return rx.container(
        # Header
        rx.hstack(
            rx.heading("🚀 Codegen Agent Dashboard", size="6"),
            rx.spacer(),
            rx.button(
                "⚙️ Settings",
                on_click=DashboardState.toggle_settings,
                variant="outline"
            ),
            rx.button(
                "🔄 Refresh",
                on_click=DashboardState.load_agent_runs,
                loading=DashboardState.loading
            ),
            width="100%",
            padding_bottom="4"
        ),
        
        # Error message
        rx.cond(
            DashboardState.error_message,
            rx.callout(
                DashboardState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                margin_bottom="4"
            )
        ),
        
        # Settings panel
        settings_panel(),
        
        # Main content
        rx.grid(
            # Left column - Create run form
            rx.vstack(
                create_run_form(),
                spacing="4",
                align="start"
            ),
            
            # Right column - Agent runs list
            rx.vstack(
                rx.heading("Recent Agent Runs", size="4"),
                rx.cond(
                    DashboardState.loading,
                    rx.spinner(),
                    rx.cond(
                        DashboardState.agent_runs,
                        rx.vstack(
                            rx.foreach(
                                DashboardState.agent_runs,
                                agent_run_card
                            ),
                            spacing="3",
                            width="100%"
                        ),
                        rx.text("No agent runs found. Create one to get started!", color="gray")
                    )
                ),
                spacing="4",
                align="start",
                width="100%"
            ),
            
            columns="2",
            spacing="6",
            width="100%"
        ),
        
        # Logs viewer (full width at bottom)
        logs_viewer(),
        
        padding="4",
        max_width="1200px"
    )

# Initialize app
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="blue"
    )
)

app.add_page(index, route="/")

# Auto-load runs on startup
app.add_page(
    index,
    route="/",
    on_load=DashboardState.load_agent_runs
)
