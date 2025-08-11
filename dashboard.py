#!/usr/bin/env python3
"""
Codegen Dashboard - Single Entry Point

Simple dashboard for creating and managing Codegen agent runs.
Features:
- Input repo URL
- Optional PR name/number input  
- Query text (request) input
- Run button to create agent run
- View agent run list with real-time updates
- Cancel button for active runs
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Optional

import streamlit as st
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codegenapi import CodegenClient, CodegenError
from codegenapi.models import AgentRun

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Codegen Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .run-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .status-active { color: #28a745; font-weight: bold; }
    .status-complete { color: #17a2b8; font-weight: bold; }
    .status-failed { color: #dc3545; font-weight: bold; }
    .status-pending { color: #ffc107; font-weight: bold; }
    .status-cancelled { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


class Dashboard:
    """Main dashboard application"""
    
    def __init__(self):
        """Initialize dashboard"""
        self.client = None
        self._initialize_session_state()
        self._setup_client()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'runs' not in st.session_state:
            st.session_state.runs = []
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = None
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
    
    def _setup_client(self):
        """Setup Codegen API client"""
        try:
            # Check for environment variables
            api_token = os.getenv("CODEGEN_API_TOKEN")
            org_id = os.getenv("CODEGEN_ORG_ID")
            
            if not api_token or not org_id:
                st.error("⚠️ Please set environment variables:")
                st.code("""
export CODEGEN_API_TOKEN="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
export CODEGEN_ORG_ID="323"
                """)
                st.stop()
            
            self.client = CodegenClient(token=api_token, org_id=int(org_id))
            
        except Exception as e:
            st.error(f"❌ Failed to initialize Codegen client: {e}")
            st.stop()
    
    def run(self):
        """Run the dashboard"""
        # Header
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.title("🤖 Codegen Dashboard")
        st.markdown("Create and manage agent runs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Main layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_create_run_form()
        
        with col2:
            self._render_runs_list()
    
    def _render_create_run_form(self):
        """Render the create run form"""
        st.subheader("🚀 Create New Run")
        
        with st.form("create_run_form", clear_on_submit=False):
            # Repository URL input
            repo_url = st.text_input(
                "Repository URL *",
                placeholder="https://github.com/user/repo",
                help="GitHub repository URL"
            )
            
            # Optional PR input
            pr_input = st.text_input(
                "PR Name/Number (Optional)",
                placeholder="feature-branch or #123",
                help="Pull request name, branch name, or PR number"
            )
            
            # Query text input
            query_text = st.text_area(
                "Request/Query *",
                placeholder="Describe what you want the agent to do...",
                height=150,
                help="Detailed description of the task for the agent"
            )
            
            # Submit button
            submitted = st.form_submit_button("▶️ Run", use_container_width=True)
            
            if submitted:
                if not repo_url or not query_text:
                    st.error("Repository URL and Request are required!")
                else:
                    self._create_agent_run(repo_url, pr_input, query_text)
    
    def _render_runs_list(self):
        """Render the agent runs list"""
        st.subheader("📋 Agent Runs")
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                self._refresh_runs()
        
        with col2:
            auto_refresh = st.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
            st.session_state.auto_refresh = auto_refresh
        
        with col3:
            if st.button("🧹 Clear List", use_container_width=True):
                st.session_state.runs = []
                st.rerun()
        
        # Auto-refresh logic
        if st.session_state.auto_refresh:
            if (st.session_state.last_refresh is None or 
                (datetime.now() - st.session_state.last_refresh).seconds > 10):
                self._refresh_runs()
        
        # Display runs
        if not st.session_state.runs:
            st.info("No agent runs found. Create a new run to get started!")
        else:
            self._display_runs_table()
    
    def _create_agent_run(self, repo_url: str, pr_input: str, query_text: str):
        """Create a new agent run"""
        try:
            # Build the prompt
            prompt_parts = [f"Repository: {repo_url}"]
            
            if pr_input:
                prompt_parts.append(f"PR/Branch: {pr_input}")
            
            prompt_parts.append(f"Request: {query_text}")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            with st.spinner("Creating agent run..."):
                run = self.client.create_agent_run(prompt=full_prompt)
            
            st.success(f"✅ Created agent run {run.id}")
            
            # Add to session state
            st.session_state.runs.insert(0, run)
            
            # Refresh the display
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to create agent run: {e}")
            logger.error(f"Failed to create agent run: {e}")
    
    def _refresh_runs(self):
        """Refresh the runs list from API"""
        try:
            with st.spinner("Refreshing runs..."):
                runs = self.client.list_agent_runs(limit=20)
                st.session_state.runs = runs
                st.session_state.last_refresh = datetime.now()
            
            st.success(f"Refreshed {len(runs)} runs")
            
        except Exception as e:
            st.error(f"❌ Failed to refresh runs: {e}")
            logger.error(f"Failed to refresh runs: {e}")
    
    def _display_runs_table(self):
        """Display runs in a table format"""
        # Prepare data for display
        table_data = []
        
        for run in st.session_state.runs:
            # Format status with emoji
            status_display = self._format_status(run.status)
            
            # Truncate prompt for display
            prompt_preview = (run.prompt[:100] + "...") if run.prompt and len(run.prompt) > 100 else (run.prompt or "")
            
            # Format created time
            created_str = run.created_at.strftime("%m/%d %H:%M") if run.created_at else "Unknown"
            
            table_data.append({
                "ID": run.id,
                "Status": status_display,
                "Created": created_str,
                "Prompt": prompt_preview,
                "Actions": run.id  # Used for action buttons
            })
        
        # Display as dataframe
        df = pd.DataFrame(table_data)
        
        # Show table
        st.dataframe(
            df[["ID", "Status", "Created", "Prompt"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons for each run
        st.subheader("🎛️ Actions")
        
        for run in st.session_state.runs[:5]:  # Show actions for first 5 runs
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            
            with col1:
                st.write(f"**{run.id}**")
            
            with col2:
                if run.can_cancel:
                    if st.button(f"❌ Cancel", key=f"cancel_{run.id}"):
                        self._cancel_run(run.id)
            
            with col3:
                if run.web_url:
                    st.link_button("🔗 View", run.web_url, use_container_width=True)
                else:
                    st.link_button("🔗 View", f"https://codegen.com/runs/{run.id}", use_container_width=True)
            
            with col4:
                status_class = f"status-{run.status.lower()}" if run.status else ""
                st.markdown(f'<span class="{status_class}">{self._format_status(run.status)}</span>', 
                           unsafe_allow_html=True)
    
    def _cancel_run(self, run_id: int):
        """Cancel a specific run"""
        try:
            with st.spinner(f"Cancelling run {run_id}..."):
                success = self.client.cancel_agent_run(run_id)
            
            if success:
                st.success(f"✅ Cancelled run {run_id}")
                # Update the run status in session state
                for run in st.session_state.runs:
                    if run.id == run_id:
                        run.status = "CANCELLED"
                        break
                st.rerun()
            else:
                st.error(f"❌ Failed to cancel run {run_id}")
                
        except Exception as e:
            st.error(f"❌ Error cancelling run {run_id}: {e}")
            logger.error(f"Error cancelling run {run_id}: {e}")
    
    def _format_status(self, status: Optional[str]) -> str:
        """Format status with emoji"""
        if not status:
            return "❓ Unknown"
        
        status_map = {
            "ACTIVE": "🔄 Active",
            "PENDING": "⏳ Pending", 
            "COMPLETE": "✅ Complete",
            "COMPLETED": "✅ Complete",
            "FAILED": "❌ Failed",
            "CANCELLED": "⏹️ Cancelled"
        }
        
        return status_map.get(status.upper(), f"❓ {status}")


def main():
    """Main entry point"""
    try:
        dashboard = Dashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Dashboard error: {e}")
        logger.error(f"Dashboard error: {e}")


if __name__ == "__main__":
    main()

