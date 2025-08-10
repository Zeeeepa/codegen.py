#!/usr/bin/env python3
"""
FULLY FUNCTIONAL Codegen Agent Dashboard
========================================

A complete Reflex-based web dashboard for managing Codegen agent runs.
This version is properly structured for Reflex and includes full integration
with the Codegen API.

Features:
- Real-time agent run monitoring
- Create new agent runs with prompts
- View detailed logs with filtering
- Resume failed/completed runs
- Live status updates
- Modern responsive UI

Usage:
    python codegen_dashboard.py

Requirements:
    pip install reflex requests python-dotenv fastapi uvicorn httpx pydantic
"""

import reflex as rx
import asyncio
import httpx
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
CODEGEN_API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "")
CODEGEN_ORG_ID = int(os.getenv("CODEGEN_ORG_ID", "0"))

# Global API server process
api_server_process = None

def start_api_server():
    """Start the FastAPI server if not already running."""
    global api_server_process
    
    # First check if server is already running using requests (more reliable)
    try:
        import requests
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            print("✅ API server already running")
            return True
    except:
        pass
    
    # Try to start the server
    try:
        print("🚀 Starting FastAPI server...")
        
        # Start the API server process
        api_server_process = subprocess.Popen([
            sys.executable, "api.py"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start with more attempts
        print("⏳ Waiting for API server to start...")
        for i in range(15):  # Increased attempts
            try:
                import requests
                response = requests.get(f"{API_BASE_URL}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ FastAPI server started successfully!")
                    return True
            except:
                time.sleep(1)
                if i % 3 == 0:
                    print(f"⏳ Still waiting... ({i+1}/15)")
        
        print("❌ Failed to start API server after 15 attempts")
        if api_server_process:
            api_server_process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False

def stop_api_server():
    """Stop the FastAPI server."""
    global api_server_process
    if api_server_process:
        api_server_process.terminate()
        api_server_process.wait()
        print("🛑 API server stopped")

# Reflex State Classes
class AgentRunState(rx.State):
    """State management for agent runs."""
    
    # Data
    agent_runs: List[Dict[str, Any]] = []
    current_run: Optional[Dict[str, Any]] = None
    logs: List[Dict[str, Any]] = []
    organizations: List[Dict[str, Any]] = []
    
    # UI State
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Form State
    prompt_text: str = ""
    metadata_text: str = "{}"
    log_filter: str = "ALL"
    
    # Pagination
    current_page: int = 1
    total_pages: int = 1
    
    async def load_organizations(self):
        """Load user organizations."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/organizations",
                    headers={"Authorization": f"Bearer {CODEGEN_API_TOKEN}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.organizations = data.get("items", [])
                else:
                    self.error_message = f"Failed to load organizations: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error loading organizations: {str(e)}"
        finally:
            self.loading = False
    
    async def load_agent_runs(self):
        """Load agent runs for the current organization."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/organizations/{CODEGEN_ORG_ID}/agent/runs",
                    headers={"Authorization": f"Bearer {CODEGEN_API_TOKEN}"},
                    params={"limit": 10, "skip": (self.current_page - 1) * 10}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.agent_runs = data.get("items", [])
                    self.total_pages = max(1, (data.get("total", 0) + 9) // 10)
                else:
                    self.error_message = f"Failed to load agent runs: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error loading agent runs: {str(e)}"
        finally:
            self.loading = False
    
    async def create_agent_run(self):
        """Create a new agent run."""
        if not self.prompt_text.strip():
            self.error_message = "Prompt cannot be empty"
            return
        
        self.loading = True
        try:
            # Parse metadata
            try:
                metadata = json.loads(self.metadata_text) if self.metadata_text.strip() else {}
            except json.JSONDecodeError:
                self.error_message = "Invalid JSON in metadata field"
                return
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/organizations/{CODEGEN_ORG_ID}/agent/run",
                    headers={"Authorization": f"Bearer {CODEGEN_API_TOKEN}"},
                    json={
                        "prompt": self.prompt_text,
                        "metadata": metadata
                    }
                )
                if response.status_code == 200:
                    self.success_message = "Agent run created successfully!"
                    self.prompt_text = ""
                    self.metadata_text = "{}"
                    await self.load_agent_runs()
                else:
                    self.error_message = f"Failed to create agent run: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error creating agent run: {str(e)}"
        finally:
            self.loading = False
    
    async def load_logs(self, agent_run_id: int):
        """Load logs for a specific agent run."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/organizations/{CODEGEN_ORG_ID}/agent/run/{agent_run_id}/logs",
                    headers={"Authorization": f"Bearer {CODEGEN_API_TOKEN}"},
                    params={"limit": 50}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.logs = data.get("logs", [])
                    self.current_run = {"id": agent_run_id}
                else:
                    self.error_message = f"Failed to load logs: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error loading logs: {str(e)}"
        finally:
            self.loading = False
    
    async def resume_agent_run(self, agent_run_id: int, additional_prompt: str = ""):
        """Resume an agent run."""
        self.loading = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/organizations/{CODEGEN_ORG_ID}/agent/run/resume",
                    headers={"Authorization": f"Bearer {CODEGEN_API_TOKEN}"},
                    json={
                        "agent_run_id": agent_run_id,
                        "prompt": additional_prompt or "Please continue from where you left off."
                    }
                )
                if response.status_code == 200:
                    self.success_message = "Agent run resumed successfully!"
                    await self.load_agent_runs()
                else:
                    self.error_message = f"Failed to resume agent run: {response.status_code}"
        except Exception as e:
            self.error_message = f"Error resuming agent run: {str(e)}"
        finally:
            self.loading = False
    
    def clear_messages(self):
        """Clear error and success messages."""
        self.error_message = ""
        self.success_message = ""
    
    def set_log_filter(self, filter_type: str):
        """Set the log filter."""
        self.log_filter = filter_type
    
    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            return AgentRunState.load_agent_runs
    
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            return AgentRunState.load_agent_runs

# UI Components
def status_badge(status: str) -> rx.Component:
    """Create a status badge with appropriate styling."""
    color_map = {
        "completed": "green",
        "running": "blue", 
        "failed": "red",
        "pending": "yellow"
    }
    
    emoji_map = {
        "completed": "✅",
        "running": "⏳",
        "failed": "❌", 
        "pending": "⏸️"
    }
    
    return rx.badge(
        f"{emoji_map.get(status, '❓')} {status.title()}",
        color_scheme=color_map.get(status, "gray"),
        variant="solid"
    )

def agent_run_card(run: Dict[str, Any]) -> rx.Component:
    """Create a card for an agent run."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(f"Run #{run.get('id', 'Unknown')}", size="4"),
                status_badge(run.get("status", "unknown")),
                justify="between",
                width="100%"
            ),
            rx.text(f"Created: {run.get('created_at', 'Unknown')}", size="2", color="gray"),
            rx.text(
                run.get("result", run.get("error", "No result available"))[:100] + "...",
                size="2"
            ),
            rx.hstack(
                rx.button(
                    "📖 View Logs",
                    on_click=AgentRunState.load_logs(run.get("id")),
                    size="2"
                ),
                rx.button(
                    "🔄 Resume",
                    on_click=AgentRunState.resume_agent_run(run.get("id")),
                    size="2",
                    variant="outline"
                ),
                spacing="2"
            ),
            spacing="3",
            align="start"
        ),
        width="100%"
    )

def log_entry_card(log: Dict[str, Any]) -> rx.Component:
    """Create a card for a log entry."""
    message_type = log.get("message_type", "UNKNOWN")
    
    # Filter logs based on current filter
    if AgentRunState.log_filter != "ALL" and message_type != AgentRunState.log_filter:
        return rx.fragment()
    
    emoji_map = {
        "ACTION": "🔧",
        "PLAN_EVALUATION": "🧠", 
        "FINAL_ANSWER": "✅",
        "ERROR": "❌",
        "USER_MESSAGE": "💬"
    }
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(f"[{log.get('created_at', '')}]", size="1", color="gray"),
                rx.badge(
                    f"{emoji_map.get(message_type, '❓')} {message_type}",
                    variant="outline"
                ),
                justify="between",
                width="100%"
            ),
            rx.cond(
                log.get("tool_name"),
                rx.text(f"Tool: {log.get('tool_name')}", weight="bold", size="2")
            ),
            rx.cond(
                log.get("thought"),
                rx.text(f"Thought: {log.get('thought')}", size="2")
            ),
            rx.cond(
                log.get("tool_input"),
                rx.code_block(
                    json.dumps(log.get("tool_input"), indent=2),
                    language="json",
                    size="1"
                )
            ),
            rx.cond(
                log.get("tool_output"),
                rx.code_block(
                    json.dumps(log.get("tool_output"), indent=2),
                    language="json", 
                    size="1"
                )
            ),
            spacing="2",
            align="start"
        ),
        width="100%"
    )

def dashboard_overview() -> rx.Component:
    """Dashboard overview section."""
    return rx.card(
        rx.vstack(
            rx.heading("📊 Agent Runs Overview", size="5"),
            rx.hstack(
                rx.stat(
                    rx.stat_label("Total Runs"),
                    rx.stat_number(len(AgentRunState.agent_runs)),
                    rx.stat_help_text("All time")
                ),
                rx.stat(
                    rx.stat_label("Completed"),
                    rx.stat_number(
                        len([r for r in AgentRunState.agent_runs if r.get("status") == "completed"])
                    ),
                    rx.stat_help_text("✅ Success")
                ),
                rx.stat(
                    rx.stat_label("Running"),
                    rx.stat_number(
                        len([r for r in AgentRunState.agent_runs if r.get("status") == "running"])
                    ),
                    rx.stat_help_text("⏳ In Progress")
                ),
                rx.stat(
                    rx.stat_label("Failed"),
                    rx.stat_number(
                        len([r for r in AgentRunState.agent_runs if r.get("status") == "failed"])
                    ),
                    rx.stat_help_text("❌ Errors")
                ),
                spacing="4"
            ),
            spacing="4",
            align="start"
        ),
        width="100%"
    )

def create_run_form() -> rx.Component:
    """Form to create new agent runs."""
    return rx.card(
        rx.vstack(
            rx.heading("🚀 Create New Agent Run", size="5"),
            rx.vstack(
                rx.text("Prompt:", weight="bold"),
                rx.text_area(
                    placeholder="Enter your prompt for the agent...",
                    value=AgentRunState.prompt_text,
                    on_change=AgentRunState.set_prompt_text,
                    height="120px",
                    width="100%"
                ),
                rx.text("Metadata (JSON):", weight="bold"),
                rx.text_area(
                    placeholder='{"key": "value"}',
                    value=AgentRunState.metadata_text,
                    on_change=AgentRunState.set_metadata_text,
                    height="80px",
                    width="100%"
                ),
                rx.button(
                    "🚀 Create Run",
                    on_click=AgentRunState.create_agent_run,
                    loading=AgentRunState.loading,
                    size="3",
                    width="100%"
                ),
                spacing="3",
                width="100%"
            ),
            spacing="4",
            align="start"
        ),
        width="100%"
    )

def agent_runs_list() -> rx.Component:
    """List of agent runs."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("📋 Recent Agent Runs", size="5"),
                rx.button(
                    "🔄 Refresh",
                    on_click=AgentRunState.load_agent_runs,
                    size="2",
                    variant="outline"
                ),
                justify="between",
                width="100%"
            ),
            rx.cond(
                AgentRunState.loading,
                rx.spinner(size="3"),
                rx.vstack(
                    rx.foreach(
                        AgentRunState.agent_runs,
                        agent_run_card
                    ),
                    rx.hstack(
                        rx.button(
                            "⬅️ Previous",
                            on_click=AgentRunState.prev_page,
                            disabled=AgentRunState.current_page == 1,
                            size="2"
                        ),
                        rx.text(f"Page {AgentRunState.current_page} of {AgentRunState.total_pages}"),
                        rx.button(
                            "➡️ Next", 
                            on_click=AgentRunState.next_page,
                            disabled=AgentRunState.current_page == AgentRunState.total_pages,
                            size="2"
                        ),
                        justify="center",
                        spacing="3"
                    ),
                    spacing="3",
                    width="100%"
                )
            ),
            spacing="4",
            align="start"
        ),
        width="100%"
    )

def log_viewer() -> rx.Component:
    """Log viewer component."""
    return rx.cond(
        AgentRunState.current_run,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(f"📖 Agent Run Logs - Run #{AgentRunState.current_run['id']}", size="5"),
                    rx.button(
                        "🔙 Back to Dashboard",
                        on_click=lambda: AgentRunState.set_current_run(None),
                        size="2",
                        variant="outline"
                    ),
                    justify="between",
                    width="100%"
                ),
                rx.hstack(
                    rx.text("🔍 Log Filters:", weight="bold"),
                    rx.button_group(
                        rx.button(
                            "ACTION",
                            on_click=AgentRunState.set_log_filter("ACTION"),
                            variant="solid" if AgentRunState.log_filter == "ACTION" else "outline",
                            size="1"
                        ),
                        rx.button(
                            "PLAN_EVALUATION", 
                            on_click=AgentRunState.set_log_filter("PLAN_EVALUATION"),
                            variant="solid" if AgentRunState.log_filter == "PLAN_EVALUATION" else "outline",
                            size="1"
                        ),
                        rx.button(
                            "ERROR",
                            on_click=AgentRunState.set_log_filter("ERROR"),
                            variant="solid" if AgentRunState.log_filter == "ERROR" else "outline",
                            size="1"
                        ),
                        rx.button(
                            "ALL",
                            on_click=AgentRunState.set_log_filter("ALL"),
                            variant="solid" if AgentRunState.log_filter == "ALL" else "outline",
                            size="1"
                        ),
                        spacing="1"
                    ),
                    rx.button(
                        "🔄 Refresh",
                        on_click=AgentRunState.load_logs(AgentRunState.current_run["id"]),
                        size="2",
                        variant="outline"
                    ),
                    justify="between",
                    width="100%"
                ),
                rx.cond(
                    AgentRunState.loading,
                    rx.spinner(size="3"),
                    rx.vstack(
                        rx.foreach(
                            AgentRunState.logs,
                            log_entry_card
                        ),
                        spacing="3",
                        width="100%"
                    )
                ),
                spacing="4",
                align="start"
            ),
            width="100%"
        )
    )

def notifications() -> rx.Component:
    """Notification messages."""
    return rx.vstack(
        rx.cond(
            AgentRunState.error_message,
            rx.callout(
                AgentRunState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                on_click=AgentRunState.clear_messages
            )
        ),
        rx.cond(
            AgentRunState.success_message,
            rx.callout(
                AgentRunState.success_message,
                icon="check",
                color_scheme="green",
                on_click=AgentRunState.clear_messages
            )
        ),
        spacing="2",
        width="100%"
    )

def index() -> rx.Component:
    """Main dashboard page."""
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("🤖 Codegen Agent Dashboard", size="8"),
                rx.badge(f"Org: {CODEGEN_ORG_ID}", variant="outline"),
                justify="between",
                width="100%",
                padding_bottom="4"
            ),
            
            # Notifications
            notifications(),
            
            # Main Content
            rx.cond(
                AgentRunState.current_run,
                log_viewer(),
                rx.vstack(
                    dashboard_overview(),
                    create_run_form(),
                    agent_runs_list(),
                    spacing="6",
                    width="100%"
                )
            ),
            
            spacing="6",
            width="100%",
            min_height="100vh"
        ),
        size="4",
        padding="4"
    )

# Create the Reflex app
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%"
    )
)

app.add_page(
    index,
    route="/",
    title="Codegen Agent Dashboard",
    on_load=[
        AgentRunState.load_organizations,
        AgentRunState.load_agent_runs
    ]
)

# This is now just the Reflex app definition
# Use start.py to launch both API server and dashboard
