"""
Reflex UI Dashboard for Codegen Agent Run Management
Complete dashboard with environment variable management and agent run monitoring
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

# Reflex imports
try:
    import reflex as rx
    from reflex import State
    REFLEX_AVAILABLE = True
except ImportError:
    REFLEX_AVAILABLE = False
    print("Reflex not available. Install with: pip install reflex")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

if REFLEX_AVAILABLE:
    class DashboardState(State):
        """Main dashboard state"""
        
        # Configuration
        api_token: str = os.getenv("CODEGEN_API_TOKEN", "")
        org_id: str = os.getenv("CODEGEN_ORG_ID", "")
        api_base_url: str = "http://localhost:8000"
        
        # UI State
        loading: bool = False
        error_message: str = ""
        success_message: str = ""
        
        # Agent Runs
        agent_runs: List[Dict[str, Any]] = []
        selected_run_id: Optional[int] = None
        selected_run_logs: List[Dict[str, Any]] = []
        
        # Pagination
        current_page: int = 1
        total_pages: int = 1
        total_runs: int = 0
        
        # Forms
        new_run_prompt: str = ""
        resume_run_prompt: str = ""
        
        # Settings
        show_settings: bool = False
        temp_api_token: str = ""
        temp_org_id: str = ""
        
        def set_api_token(self, token: str):
            """Set API token"""
            self.temp_api_token = token
        
        def set_org_id(self, org_id: str):
            """Set organization ID"""
            self.temp_org_id = org_id
        
        def save_settings(self):
            """Save settings to environment"""
            if self.temp_api_token:
                self.api_token = self.temp_api_token
                os.environ["CODEGEN_API_TOKEN"] = self.temp_api_token
            
            if self.temp_org_id:
                self.org_id = self.temp_org_id
                os.environ["CODEGEN_ORG_ID"] = self.temp_org_id
            
            # Save to .env file
            try:
                with open(".env", "w") as f:
                    f.write(f"CODEGEN_API_TOKEN={self.api_token}\n")
                    f.write(f"CODEGEN_ORG_ID={self.org_id}\n")
                
                self.success_message = "Settings saved successfully!"
                self.show_settings = False
                self.temp_api_token = ""
                self.temp_org_id = ""
            except Exception as e:
                self.error_message = f"Failed to save settings: {e}"
        
        def toggle_settings(self):
            """Toggle settings panel"""
            self.show_settings = not self.show_settings
            self.temp_api_token = self.api_token
            self.temp_org_id = self.org_id
        
        def clear_messages(self):
            """Clear error and success messages"""
            self.error_message = ""
            self.success_message = ""
        
        async def load_agent_runs(self, page: int = 1):
            """Load agent runs from API"""
            self.loading = True
            self.clear_messages()
            
            try:
                response = requests.get(
                    f"{self.api_base_url}/agent_runs",
                    params={"page": page, "limit": 10}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.agent_runs = data["items"]
                    self.current_page = data["page"]
                    self.total_runs = data["total"]
                    self.total_pages = (data["total"] + 9) // 10  # Ceiling division
                else:
                    self.error_message = f"Failed to load agent runs: {response.status_code}"
                    
            except Exception as e:
                self.error_message = f"Error loading agent runs: {e}"
            finally:
                self.loading = False
        
        async def create_agent_run(self):
            """Create a new agent run"""
            if not self.new_run_prompt.strip():
                self.error_message = "Please enter a prompt"
                return
            
            self.loading = True
            self.clear_messages()
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/agent_runs",
                    json={"prompt": self.new_run_prompt.strip()}
                )
                
                if response.status_code == 200:
                    self.success_message = "Agent run created successfully!"
                    self.new_run_prompt = ""
                    await self.load_agent_runs()
                else:
                    self.error_message = f"Failed to create agent run: {response.status_code}"
                    
            except Exception as e:
                self.error_message = f"Error creating agent run: {e}"
            finally:
                self.loading = False
        
        async def load_agent_run_logs(self, run_id: int):
            """Load logs for a specific agent run"""
            self.loading = True
            self.clear_messages()
            self.selected_run_id = run_id
            
            try:
                response = requests.get(f"{self.api_base_url}/agent_runs/{run_id}/logs")
                
                if response.status_code == 200:
                    data = response.json()
                    self.selected_run_logs = data["logs"]
                else:
                    self.error_message = f"Failed to load logs: {response.status_code}"
                    
            except Exception as e:
                self.error_message = f"Error loading logs: {e}"
            finally:
                self.loading = False
        
        async def resume_agent_run(self, run_id: int):
            """Resume an agent run"""
            if not self.resume_run_prompt.strip():
                self.error_message = "Please enter a prompt to resume"
                return
            
            self.loading = True
            self.clear_messages()
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/agent_runs/{run_id}/resume",
                    json={"prompt": self.resume_run_prompt.strip()}
                )
                
                if response.status_code == 200:
                    self.success_message = "Agent run resumed successfully!"
                    self.resume_run_prompt = ""
                    await self.load_agent_runs()
                else:
                    self.error_message = f"Failed to resume agent run: {response.status_code}"
                    
            except Exception as e:
                self.error_message = f"Error resuming agent run: {e}"
            finally:
                self.loading = False
        
        def set_new_run_prompt(self, prompt: str):
            """Set new run prompt"""
            self.new_run_prompt = prompt
        
        def set_resume_run_prompt(self, prompt: str):
            """Set resume run prompt"""
            self.resume_run_prompt = prompt
        
        def next_page(self):
            """Go to next page"""
            if self.current_page < self.total_pages:
                return self.load_agent_runs(self.current_page + 1)
        
        def prev_page(self):
            """Go to previous page"""
            if self.current_page > 1:
                return self.load_agent_runs(self.current_page - 1)

    # ========================================================================
    # UI COMPONENTS
    # ========================================================================

    def status_badge(status: str) -> rx.Component:
        """Status badge component"""
        color_map = {
            "ACTIVE": "blue",
            "COMPLETED": "green", 
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
        """Agent run card component"""
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(f"Run #{run['id']}", size="sm"),
                    status_badge(run["status"]),
                    rx.spacer(),
                    rx.button(
                        "View Logs",
                        size="sm",
                        on_click=lambda: DashboardState.load_agent_run_logs(run["id"])
                    ),
                    justify="space-between",
                    width="100%"
                ),
                rx.text(
                    run["prompt"][:100] + "..." if len(run["prompt"]) > 100 else run["prompt"],
                    color="gray.600"
                ),
                rx.hstack(
                    rx.text(f"Created: {run.get('created_at', 'Unknown')}", size="sm"),
                    rx.spacer(),
                    rx.cond(
                        run["web_url"],
                        rx.link("View in Codegen", href=run["web_url"], is_external=True, size="sm")
                    ),
                    width="100%"
                ),
                rx.cond(
                    run["status"] in ["COMPLETED", "FAILED", "CANCELLED"],
                    rx.hstack(
                        rx.input(
                            placeholder="Enter prompt to resume...",
                            value=DashboardState.resume_run_prompt,
                            on_change=DashboardState.set_resume_run_prompt,
                            flex="1"
                        ),
                        rx.button(
                            "Resume",
                            on_click=lambda: DashboardState.resume_agent_run(run["id"]),
                            size="sm"
                        ),
                        width="100%"
                    )
                ),
                spacing="2",
                align="start"
            ),
            width="100%",
            padding="4"
        )

    def log_entry(log: Dict[str, Any]) -> rx.Component:
        """Log entry component"""
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(log["message_type"], variant="outline"),
                    rx.text(log.get("created_at", ""), size="sm", color="gray.500"),
                    justify="space-between",
                    width="100%"
                ),
                rx.cond(
                    log.get("thought"),
                    rx.text(f"💭 {log['thought']}", color="blue.600")
                ),
                rx.cond(
                    log.get("tool_name"),
                    rx.text(f"🔧 Tool: {log['tool_name']}", color="green.600")
                ),
                rx.cond(
                    log.get("observation"),
                    rx.text(f"👁️ {str(log['observation'])[:200]}...", color="gray.700")
                ),
                spacing="2",
                align="start"
            ),
            width="100%",
            padding="3"
        )

    def settings_panel() -> rx.Component:
        """Settings panel component"""
        return rx.drawer(
            rx.drawer_overlay(
                rx.drawer_content(
                    rx.drawer_header("Settings"),
                    rx.drawer_body(
                        rx.vstack(
                            rx.form_control(
                                rx.form_label("API Token"),
                                rx.input(
                                    placeholder="sk-...",
                                    type_="password",
                                    value=DashboardState.temp_api_token,
                                    on_change=DashboardState.set_api_token
                                )
                            ),
                            rx.form_control(
                                rx.form_label("Organization ID"),
                                rx.input(
                                    placeholder="123",
                                    value=DashboardState.temp_org_id,
                                    on_change=DashboardState.set_org_id
                                )
                            ),
                            rx.button(
                                "Save Settings",
                                on_click=DashboardState.save_settings,
                                color_scheme="blue",
                                width="100%"
                            ),
                            spacing="4"
                        )
                    ),
                    rx.drawer_footer(
                        rx.button(
                            "Close",
                            on_click=DashboardState.toggle_settings
                        )
                    )
                )
            ),
            is_open=DashboardState.show_settings,
            placement="right",
            size="md"
        )

    # ========================================================================
    # MAIN PAGES
    # ========================================================================

    def dashboard_page() -> rx.Component:
        """Main dashboard page"""
        return rx.container(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.heading("Codegen Agent Run Dashboard", size="lg"),
                    rx.spacer(),
                    rx.button(
                        "Settings",
                        on_click=DashboardState.toggle_settings,
                        variant="outline"
                    ),
                    rx.button(
                        "Refresh",
                        on_click=DashboardState.load_agent_runs,
                        color_scheme="blue"
                    ),
                    width="100%",
                    padding_bottom="4"
                ),
                
                # Messages
                rx.cond(
                    DashboardState.error_message,
                    rx.alert(
                        rx.alert_icon(),
                        rx.alert_title(DashboardState.error_message),
                        status="error",
                        margin_bottom="4"
                    )
                ),
                rx.cond(
                    DashboardState.success_message,
                    rx.alert(
                        rx.alert_icon(),
                        rx.alert_title(DashboardState.success_message),
                        status="success",
                        margin_bottom="4"
                    )
                ),
                
                # Create New Run
                rx.card(
                    rx.vstack(
                        rx.heading("Create New Agent Run", size="md"),
                        rx.textarea(
                            placeholder="Enter your prompt here...",
                            value=DashboardState.new_run_prompt,
                            on_change=DashboardState.set_new_run_prompt,
                            width="100%",
                            height="100px"
                        ),
                        rx.button(
                            "Create Agent Run",
                            on_click=DashboardState.create_agent_run,
                            color_scheme="green",
                            width="100%",
                            loading=DashboardState.loading
                        ),
                        spacing="3"
                    ),
                    width="100%",
                    padding="4",
                    margin_bottom="6"
                ),
                
                # Agent Runs List
                rx.vstack(
                    rx.hstack(
                        rx.heading("Agent Runs", size="md"),
                        rx.spacer(),
                        rx.text(f"Total: {DashboardState.total_runs}"),
                        width="100%"
                    ),
                    
                    # Pagination
                    rx.hstack(
                        rx.button(
                            "Previous",
                            on_click=DashboardState.prev_page,
                            disabled=DashboardState.current_page <= 1
                        ),
                        rx.text(f"Page {DashboardState.current_page} of {DashboardState.total_pages}"),
                        rx.button(
                            "Next", 
                            on_click=DashboardState.next_page,
                            disabled=DashboardState.current_page >= DashboardState.total_pages
                        ),
                        justify="center",
                        spacing="4"
                    ),
                    
                    # Agent Run Cards
                    rx.cond(
                        DashboardState.loading,
                        rx.spinner(size="lg"),
                        rx.vstack(
                            rx.foreach(
                                DashboardState.agent_runs,
                                agent_run_card
                            ),
                            spacing="4",
                            width="100%"
                        )
                    ),
                    
                    spacing="4",
                    width="100%"
                ),
                
                spacing="6",
                width="100%"
            ),
            settings_panel(),
            max_width="1200px",
            padding="6"
        )

    def logs_page() -> rx.Component:
        """Logs viewing page"""
        return rx.container(
            rx.vstack(
                rx.hstack(
                    rx.button("← Back", on_click=lambda: setattr(DashboardState, 'selected_run_id', None)),
                    rx.heading(f"Logs for Run #{DashboardState.selected_run_id}", size="lg"),
                    width="100%"
                ),
                
                rx.cond(
                    DashboardState.loading,
                    rx.spinner(size="lg"),
                    rx.vstack(
                        rx.foreach(
                            DashboardState.selected_run_logs,
                            log_entry
                        ),
                        spacing="3",
                        width="100%"
                    )
                ),
                
                spacing="6",
                width="100%"
            ),
            max_width="1200px",
            padding="6"
        )

    def index() -> rx.Component:
        """Main index page"""
        return rx.cond(
            DashboardState.selected_run_id,
            logs_page(),
            dashboard_page()
        )

    # ========================================================================
    # APP CONFIGURATION
    # ========================================================================

    app = rx.App(
        state=DashboardState,
        style={
            "font_family": "Inter",
            "background_color": "gray.50"
        }
    )
    
    app.add_page(index, route="/")
    
    # Initialize data on startup
    app.add_custom_404_page(dashboard_page)

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run the dashboard"""
    if not REFLEX_AVAILABLE:
        print("❌ Reflex not available")
        print("📦 Install with: pip install reflex")
        return
    
    print("🚀 Starting Codegen Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:3000")
    print("💡 Make sure the API server is running at: http://localhost:8000")
    
    # Initialize and run
    app.compile()
    app.run(host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()
