#!/usr/bin/env python3
"""
Codegen Agent Dashboard
======================

A beautiful Reflex UI dashboard for managing Codegen agent runs with real-time updates.
Automatically starts the FastAPI backend server when launched.

Features:
    • Agent run list with real-time status updates
    • Create new agent runs with custom prompts
    • View detailed agent run logs and progress
    • Resume completed/failed agent runs
    • Environment variable configuration
    • Real-time log streaming
    • Beautiful, responsive UI
    • Automatic API server startup

Usage:
    pip install reflex requests python-dotenv fastapi uvicorn httpx pydantic
    python dashboard.py
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import reflex as rx

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Install python-dotenv for .env file support: pip install python-dotenv")

# Configuration
API_BASE_URL = "http://localhost:8000"
ORG_ID = os.getenv("CODEGEN_ORG_ID", "323")
API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "your_api_token_here")

# Global variable to track API server process
api_server_process = None

# ============================================================================
# API SERVER MANAGEMENT
# ============================================================================

def start_api_server():
    """Start the FastAPI server in a separate process"""
    global api_server_process
    
    print("🚀 Starting FastAPI backend server...")
    
    try:
        # Start the API server
        api_server_process = subprocess.Popen(
            [sys.executable, "api.py", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get(f"{API_BASE_URL}/health", 
                                  headers={"Authorization": f"Bearer {API_TOKEN}"}, 
                                  timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI backend server started successfully!")
                return True
            else:
                print(f"⚠️ API server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print("⚠️ API server not responding yet, but process started")
            return True
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return False

def stop_api_server():
    """Stop the FastAPI server"""
    global api_server_process
    
    if api_server_process:
        print("🛑 Stopping FastAPI backend server...")
        api_server_process.terminate()
        api_server_process.wait()
        api_server_process = None
        print("✅ FastAPI backend server stopped")

def check_api_server():
    """Check if API server is running and start if needed"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"}, 
                              timeout=2)
        return response.status_code == 200
    except:
        return False

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AgentRunState(rx.State):
    """State management for agent runs"""
    
    # Configuration
    org_id: str = ORG_ID
    api_token: str = API_TOKEN
    api_base_url: str = API_BASE_URL
    
    # Agent runs data
    agent_runs: List[Dict[str, Any]] = []
    selected_run: Optional[Dict[str, Any]] = None
    selected_run_logs: List[Dict[str, Any]] = []
    
    # UI state
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Create run form
    new_prompt: str = ""
    new_metadata: str = "{}"
    
    # Resume run form
    resume_prompt: str = ""
    
    # Pagination
    current_page: int = 1
    total_pages: int = 1
    runs_per_page: int = 10
    
    # Auto-refresh
    auto_refresh: bool = True
    last_refresh: str = ""
    
    def get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def load_agent_runs(self):
        """Load agent runs from API"""
        if not self.api_token or self.api_token == "your_api_token_here":
            self.error_message = "Please set CODEGEN_API_TOKEN in .env file"
            return
        
        self.loading = True
        self.error_message = ""
        
        try:
            skip = (self.current_page - 1) * self.runs_per_page
            response = requests.get(
                f"{self.api_base_url}/agent-runs",
                headers=self.get_headers(),
                params={"skip": skip, "limit": self.runs_per_page},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_runs = data.get("items", [])
                self.total_pages = data.get("pages", 1)
                self.last_refresh = datetime.now().strftime("%H:%M:%S")
                self.success_message = f"Loaded {len(self.agent_runs)} agent runs"
            else:
                self.error_message = f"Failed to load agent runs: {response.status_code}"
                
        except Exception as e:
            self.error_message = f"Error loading agent runs: {str(e)}"
        finally:
            self.loading = False
    
    async def create_agent_run(self):
        """Create a new agent run"""
        if not self.new_prompt.strip():
            self.error_message = "Please enter a prompt"
            return
        
        self.loading = True
        self.error_message = ""
        
        try:
            # Parse metadata
            metadata = {}
            if self.new_metadata.strip():
                metadata = json.loads(self.new_metadata)
            
            payload = {
                "prompt": self.new_prompt,
                "metadata": metadata
            }
            
            response = requests.post(
                f"{self.api_base_url}/agent-runs",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.success_message = f"Created agent run {data['id']}"
                self.new_prompt = ""
                self.new_metadata = "{}"
                # Refresh the list
                await self.load_agent_runs()
            else:
                self.error_message = f"Failed to create agent run: {response.status_code}"
                
        except json.JSONDecodeError:
            self.error_message = "Invalid JSON in metadata field"
        except Exception as e:
            self.error_message = f"Error creating agent run: {str(e)}"
        finally:
            self.loading = False
    
    async def select_agent_run(self, run_id: int):
        """Select an agent run and load its details"""
        self.loading = True
        self.error_message = ""
        
        try:
            # Get agent run details
            response = requests.get(
                f"{self.api_base_url}/agent-runs/{run_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.selected_run = response.json()
                
                # Get logs
                logs_response = requests.get(
                    f"{self.api_base_url}/agent-runs/{run_id}/logs",
                    headers=self.get_headers(),
                    params={"limit": 50},
                    timeout=10
                )
                
                if logs_response.status_code == 200:
                    logs_data = logs_response.json()
                    self.selected_run_logs = logs_data.get("logs", [])
                else:
                    self.selected_run_logs = []
                    
            else:
                self.error_message = f"Failed to load agent run: {response.status_code}"
                
        except Exception as e:
            self.error_message = f"Error loading agent run: {str(e)}"
        finally:
            self.loading = False
    
    async def resume_agent_run(self, run_id: int):
        """Resume an agent run"""
        if not self.resume_prompt.strip():
            self.error_message = "Please enter a resume prompt"
            return
        
        self.loading = True
        self.error_message = ""
        
        try:
            payload = {"prompt": self.resume_prompt}
            
            response = requests.post(
                f"{self.api_base_url}/agent-runs/{run_id}/resume",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.success_message = f"Resumed agent run {run_id}"
                self.resume_prompt = ""
                # Refresh the selected run
                await self.select_agent_run(run_id)
                await self.load_agent_runs()
            else:
                self.error_message = f"Failed to resume agent run: {response.status_code}"
                
        except Exception as e:
            self.error_message = f"Error resuming agent run: {str(e)}"
        finally:
            self.loading = False
    
    def clear_messages(self):
        """Clear error and success messages"""
        self.error_message = ""
        self.success_message = ""
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
    
    def set_page(self, page: int):
        """Set specific page"""
        if 1 <= page <= self.total_pages:
            self.current_page = page

# ============================================================================
# UI COMPONENTS
# ============================================================================

def status_badge(status: str) -> rx.Component:
    """Create a status badge with appropriate color"""
    color_map = {
        "ACTIVE": "blue",
        "COMPLETE": "green", 
        "FAILED": "red",
        "CANCELLED": "gray",
        "QUEUED": "yellow"
    }
    
    return rx.badge(
        status,
        color_scheme=color_map.get(status, "gray"),
        variant="solid"
    )

def agent_run_card(run: Dict[str, Any]) -> rx.Component:
    """Create an agent run card"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(f"Run #{run['id']}", size="4"),
                status_badge(run["status"]),
                rx.spacer(),
                rx.text(
                    run["created_at"][:19].replace("T", " "),
                    size="2",
                    color="gray"
                ),
                width="100%",
                align="center"
            ),
            rx.text(
                run.get("result", "No result yet")[:100] + ("..." if len(run.get("result", "")) > 100 else ""),
                size="2",
                color="gray"
            ),
            rx.hstack(
                rx.button(
                    "View Details",
                    on_click=AgentRunState.select_agent_run(run["id"]),
                    size="2",
                    variant="soft"
                ),
                rx.cond(
                    run["status"].in_(["COMPLETE", "FAILED", "CANCELLED"]),
                    rx.button(
                        "Resume",
                        size="2",
                        variant="outline",
                        color_scheme="blue"
                    )
                ),
                rx.link(
                    rx.button(
                        "View on Web",
                        size="2",
                        variant="ghost"
                    ),
                    href=run["web_url"],
                    is_external=True
                ),
                width="100%",
                justify="start"
            ),
            spacing="3",
            align="start",
            width="100%"
        ),
        width="100%"
    )

def log_entry_card(log: Dict[str, Any]) -> rx.Component:
    """Create a log entry card"""
    message_type = log.get("message_type", "UNKNOWN")
    thought = log.get("thought", "")
    tool_name = log.get("tool_name", "")
    created_at = log.get("created_at", "")
    
    # Color scheme for different message types
    color_map = {
        "ACTION": "blue",
        "PLAN_EVALUATION": "purple",
        "FINAL_ANSWER": "green",
        "ERROR": "red",
        "USER_MESSAGE": "gray"
    }
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    message_type,
                    color_scheme=color_map.get(message_type, "gray"),
                    variant="soft"
                ),
                rx.cond(
                    tool_name,
                    rx.badge(tool_name, variant="outline")
                ),
                rx.spacer(),
                rx.text(
                    created_at[:19].replace("T", " "),
                    size="1",
                    color="gray"
                ),
                width="100%",
                align="center"
            ),
            rx.cond(
                thought,
                rx.text(thought, size="2")
            ),
            rx.cond(
                log.get("tool_input"),
                rx.details(
                    rx.summary("Tool Input"),
                    rx.code_block(
                        json.dumps(log["tool_input"], indent=2),
                        language="json",
                        size="1"
                    )
                )
            ),
            rx.cond(
                log.get("tool_output"),
                rx.details(
                    rx.summary("Tool Output"),
                    rx.code_block(
                        json.dumps(log["tool_output"], indent=2)[:500] + ("..." if len(json.dumps(log["tool_output"], indent=2)) > 500 else ""),
                        language="json",
                        size="1"
                    )
                )
            ),
            spacing="2",
            align="start",
            width="100%"
        ),
        width="100%"
    )

def create_run_form() -> rx.Component:
    """Create agent run form"""
    return rx.card(
        rx.vstack(
            rx.heading("Create New Agent Run", size="4"),
            rx.text_area(
                placeholder="Enter your prompt here...",
                value=AgentRunState.new_prompt,
                on_change=AgentRunState.set_new_prompt,
                rows=4,
                width="100%"
            ),
            rx.text_area(
                placeholder='{"key": "value"} - Optional metadata JSON',
                value=AgentRunState.new_metadata,
                on_change=AgentRunState.set_new_metadata,
                rows=2,
                width="100%"
            ),
            rx.button(
                "Create Agent Run",
                on_click=AgentRunState.create_agent_run,
                loading=AgentRunState.loading,
                width="100%",
                size="3"
            ),
            spacing="3",
            width="100%"
        ),
        width="100%"
    )

def agent_run_details() -> rx.Component:
    """Agent run details panel"""
    return rx.cond(
        AgentRunState.selected_run,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(f"Agent Run #{AgentRunState.selected_run['id']}", size="4"),
                    status_badge(AgentRunState.selected_run["status"]),
                    rx.spacer(),
                    rx.button(
                        "Close",
                        on_click=AgentRunState.set_selected_run(None),
                        variant="ghost",
                        size="2"
                    ),
                    width="100%",
                    align="center"
                ),
                rx.divider(),
                rx.text(f"Created: {AgentRunState.selected_run['created_at']}", size="2"),
                rx.text(f"Organization: {AgentRunState.selected_run['organization_id']}", size="2"),
                rx.cond(
                    AgentRunState.selected_run.get("result"),
                    rx.vstack(
                        rx.text("Result:", weight="bold", size="2"),
                        rx.text(AgentRunState.selected_run["result"], size="2"),
                        spacing="1"
                    )
                ),
                rx.cond(
                    AgentRunState.selected_run["status"].in_(["COMPLETE", "FAILED", "CANCELLED"]),
                    rx.vstack(
                        rx.text("Resume Agent Run:", weight="bold", size="3"),
                        rx.text_area(
                            placeholder="Enter additional instructions...",
                            value=AgentRunState.resume_prompt,
                            on_change=AgentRunState.set_resume_prompt,
                            rows=3,
                            width="100%"
                        ),
                        rx.button(
                            "Resume Run",
                            on_click=AgentRunState.resume_agent_run(AgentRunState.selected_run["id"]),
                            loading=AgentRunState.loading,
                            size="2"
                        ),
                        spacing="2",
                        width="100%"
                    )
                ),
                rx.divider(),
                rx.heading("Agent Logs", size="3"),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            AgentRunState.selected_run_logs,
                            log_entry_card
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    height="400px",
                    width="100%"
                ),
                spacing="3",
                width="100%"
            ),
            width="100%"
        )
    )

def pagination_controls() -> rx.Component:
    """Pagination controls"""
    return rx.hstack(
        rx.button(
            "Previous",
            on_click=AgentRunState.prev_page,
            disabled=AgentRunState.current_page == 1,
            variant="outline",
            size="2"
        ),
        rx.text(f"Page {AgentRunState.current_page} of {AgentRunState.total_pages}", size="2"),
        rx.button(
            "Next", 
            on_click=AgentRunState.next_page,
            disabled=AgentRunState.current_page == AgentRunState.total_pages,
            variant="outline",
            size="2"
        ),
        spacing="3",
        align="center"
    )

def message_alerts() -> rx.Component:
    """Message alerts"""
    return rx.vstack(
        rx.cond(
            AgentRunState.error_message,
            rx.callout(
                AgentRunState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                width="100%"
            )
        ),
        rx.cond(
            AgentRunState.success_message,
            rx.callout(
                AgentRunState.success_message,
                icon="check",
                color_scheme="green",
                width="100%"
            )
        ),
        spacing="2",
        width="100%"
    )

# ============================================================================
# MAIN LAYOUT
# ============================================================================

def index() -> rx.Component:
    """Main dashboard page"""
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("🤖 Codegen Agent Dashboard", size="6"),
                rx.spacer(),
                rx.hstack(
                    rx.switch(
                        checked=AgentRunState.auto_refresh,
                        on_change=AgentRunState.set_auto_refresh
                    ),
                    rx.text("Auto-refresh", size="2"),
                    rx.button(
                        "Refresh",
                        on_click=AgentRunState.load_agent_runs,
                        loading=AgentRunState.loading,
                        variant="outline",
                        size="2"
                    ),
                    spacing="2",
                    align="center"
                ),
                width="100%",
                align="center",
                padding_bottom="4"
            ),
            
            # Messages
            message_alerts(),
            
            # Main content
            rx.grid(
                # Left column - Agent runs list and create form
                rx.vstack(
                    create_run_form(),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Agent Runs", size="4"),
                                rx.spacer(),
                                rx.cond(
                                    AgentRunState.last_refresh,
                                    rx.text(f"Last refresh: {AgentRunState.last_refresh}", size="1", color="gray")
                                ),
                                width="100%",
                                align="center"
                            ),
                            rx.cond(
                                AgentRunState.loading,
                                rx.center(rx.spinner(size="3"), padding="4"),
                                rx.vstack(
                                    rx.foreach(
                                        AgentRunState.agent_runs,
                                        agent_run_card
                                    ),
                                    spacing="3",
                                    width="100%"
                                )
                            ),
                            pagination_controls(),
                            spacing="3",
                            width="100%"
                        ),
                        width="100%"
                    ),
                    spacing="4",
                    width="100%"
                ),
                
                # Right column - Agent run details
                agent_run_details(),
                
                columns="2",
                spacing="4",
                width="100%"
            ),
            
            spacing="4",
            width="100%",
            min_height="100vh"
        ),
        size="4",
        padding="4"
    )

# ============================================================================
# APP CONFIGURATION
# ============================================================================

def initialize_app():
    """Initialize the application and start API server if needed"""
    print("🤖 Codegen Agent Dashboard")
    print("=" * 30)
    
    # Check if API token is configured
    if not API_TOKEN or API_TOKEN == "your_api_token_here":
        print("❌ Error: CODEGEN_API_TOKEN not set in .env file")
        print("   Please create a .env file with:")
        print("   CODEGEN_API_TOKEN=your_actual_token")
        print("   CODEGEN_ORG_ID=your_org_id")
        sys.exit(1)
    
    # Check if API server is already running
    if not check_api_server():
        print("🔍 API server not detected, starting automatically...")
        if not start_api_server():
            print("❌ Failed to start API server. Please check api.py file exists.")
            sys.exit(1)
    else:
        print("✅ API server already running")
    
    print("🎨 Starting Reflex dashboard...")
    print("📖 Backend API: http://localhost:8000/docs")
    print("🎨 Dashboard UI: http://localhost:3000")
    print()

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
    on_load=AgentRunState.load_agent_runs
)

if __name__ == "__main__":
    try:
        # Initialize and start API server if needed
        initialize_app()
        
        # Start the dashboard
        app.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Clean up API server
        stop_api_server()
