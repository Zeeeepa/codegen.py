"""
Dashboard Main Application

Live agent run management interface allowing to view active runs, past runs,
statuses of runs, projects set in runs, to be able to cancel runs, resume runs,
create new runs, and all other features to be fully accessible.

Integrates with the codegenapi package for clean separation of concerns.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the parent directory to the path to import codegenapi
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegenapi import CodegenClient, Task, TaskStatus, TaskType, Priority
from codegenapi.config import Config
from codegenapi.task_manager import TaskManager
from codegenapi.exceptions import CodegenError, TaskError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Codegen Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-active { color: #28a745; }
    .status-complete { color: #17a2b8; }
    .status-failed { color: #dc3545; }
    .status-pending { color: #ffc107; }
    .status-cancelled { color: #6c757d; }
    .status-paused { color: #fd7e14; }
</style>
""", unsafe_allow_html=True)


class DashboardApp:
    """Main dashboard application class"""
    
    def __init__(self):
        """Initialize the dashboard"""
        self.config = None
        self.client = None
        self.task_manager = None
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
            st.session_state.tasks = []
            st.session_state.last_refresh = None
            st.session_state.auto_refresh = True
            st.session_state.refresh_interval = 30
    
    def _setup_clients(self) -> bool:
        """Setup Codegen client and task manager"""
        try:
            # Get configuration from environment or user input
            api_token = os.getenv("CODEGEN_API_TOKEN")
            org_id = os.getenv("CODEGEN_ORG_ID")
            
            if not api_token or not org_id:
                st.error("Please set CODEGEN_API_TOKEN and CODEGEN_ORG_ID environment variables")
                return False
            
            # Initialize configuration
            self.config = Config()
            
            # Initialize client
            self.client = CodegenClient(
                token=api_token,
                org_id=int(org_id)
            )
            
            # Initialize task manager
            self.task_manager = TaskManager(self.client, self.config)
            
            st.session_state.initialized = True
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize Codegen client: {e}")
            logger.error(f"Client initialization error: {e}")
            return False
    
    def run(self):
        """Run the dashboard application"""
        st.title("🤖 Codegen Dashboard")
        st.markdown("Live agent run management interface")
        
        # Setup clients if not initialized
        if not st.session_state.initialized:
            if not self._setup_clients():
                return
        
        # Sidebar configuration
        self._render_sidebar()
        
        # Main content
        self._render_main_content()
    
    def _render_sidebar(self):
        """Render sidebar with controls and filters"""
        st.sidebar.header("Dashboard Controls")
        
        # Refresh controls
        st.sidebar.subheader("Refresh Settings")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🔄 Refresh Now"):
                self._refresh_data()
        
        with col2:
            st.session_state.auto_refresh = st.checkbox(
                "Auto Refresh", 
                value=st.session_state.auto_refresh
            )
        
        if st.session_state.auto_refresh:
            st.session_state.refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=10,
                max_value=300,
                value=st.session_state.refresh_interval,
                step=10
            )
        
        # Filters
        st.sidebar.subheader("Filters")
        
        status_filter = st.sidebar.multiselect(
            "Status Filter",
            options=[status.value for status in TaskStatus],
            default=[]
        )
        
        type_filter = st.sidebar.multiselect(
            "Task Type Filter",
            options=[task_type.value for task_type in TaskType],
            default=[]
        )
        
        # Store filters in session state
        st.session_state.status_filter = status_filter
        st.session_state.type_filter = type_filter
        
        # Quick actions
        st.sidebar.subheader("Quick Actions")
        
        if st.sidebar.button("📊 Generate Report"):
            self._generate_report()
        
        if st.sidebar.button("🧹 Cleanup Old Tasks"):
            self._cleanup_old_tasks()
    
    def _render_main_content(self):
        """Render main dashboard content"""
        
        # Auto-refresh logic
        if st.session_state.auto_refresh:
            if (st.session_state.last_refresh is None or 
                datetime.now() - st.session_state.last_refresh > timedelta(seconds=st.session_state.refresh_interval)):
                self._refresh_data()
        
        # Metrics overview
        self._render_metrics()
        
        # Task management tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Tasks", "📈 Analytics", "➕ Create Task", "⚙️ Settings"])
        
        with tab1:
            self._render_tasks_tab()
        
        with tab2:
            self._render_analytics_tab()
        
        with tab3:
            self._render_create_task_tab()
        
        with tab4:
            self._render_settings_tab()
    
    def _render_metrics(self):
        """Render key metrics overview"""
        st.subheader("📊 Overview")
        
        if not st.session_state.tasks:
            st.info("No tasks found. Create a new task to get started.")
            return
        
        # Calculate metrics
        total_tasks = len(st.session_state.tasks)
        active_tasks = len([t for t in st.session_state.tasks if t.status == TaskStatus.ACTIVE])
        completed_tasks = len([t for t in st.session_state.tasks if t.status == TaskStatus.COMPLETE])
        failed_tasks = len([t for t in st.session_state.tasks if t.status == TaskStatus.FAILED])
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            st.metric("Active", active_tasks, delta=None)
        
        with col3:
            st.metric("Completed", completed_tasks)
        
        with col4:
            st.metric("Failed", failed_tasks)
        
        # Status distribution chart
        if st.session_state.tasks:
            status_counts = {}
            for task in st.session_state.tasks:
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Task Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_tasks_tab(self):
        """Render tasks management tab"""
        st.subheader("📋 Task Management")
        
        if not st.session_state.tasks:
            st.info("No tasks found.")
            return
        
        # Apply filters
        filtered_tasks = self._apply_filters(st.session_state.tasks)
        
        if not filtered_tasks:
            st.warning("No tasks match the current filters.")
            return
        
        # Tasks table
        self._render_tasks_table(filtered_tasks)
        
        # Task details
        if st.session_state.get('selected_task_id'):
            self._render_task_details(st.session_state.selected_task_id)
    
    def _render_tasks_table(self, tasks: List[Task]):
        """Render tasks table with actions"""
        
        # Prepare data for table
        table_data = []
        for task in tasks:
            table_data.append({
                "ID": task.id,
                "Type": task.task_type.value,
                "Status": task.status.value,
                "Repository": task.repository[:50] + "..." if len(task.repository) > 50 else task.repository,
                "Priority": task.priority.value,
                "Created": task.created_at.strftime("%Y-%m-%d %H:%M"),
                "Actions": task.id  # Will be used for action buttons
            })
        
        df = pd.DataFrame(table_data)
        
        # Display table with selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle row selection
        if event.selection.rows:
            selected_row = event.selection.rows[0]
            selected_task_id = df.iloc[selected_row]["ID"]
            st.session_state.selected_task_id = selected_task_id
        
        # Action buttons for selected task
        if st.session_state.get('selected_task_id'):
            selected_task = next((t for t in tasks if t.id == st.session_state.selected_task_id), None)
            if selected_task:
                self._render_task_actions(selected_task)
    
    def _render_task_actions(self, task: Task):
        """Render action buttons for a task"""
        st.subheader(f"Actions for Task {task.id}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if task.status == TaskStatus.ACTIVE and st.button("⏸️ Pause", key=f"pause_{task.id}"):
                # Note: Pause functionality would need to be implemented in the API
                st.warning("Pause functionality not yet implemented in API")
        
        with col2:
            if task.can_resume and st.button("▶️ Resume", key=f"resume_{task.id}"):
                self._show_resume_dialog(task)
        
        with col3:
            if task.is_active and st.button("❌ Cancel", key=f"cancel_{task.id}"):
                self._cancel_task(task)
        
        with col4:
            if st.button("📋 View Details", key=f"details_{task.id}"):
                st.session_state.show_task_details = task.id
    
    def _render_task_details(self, task_id: int):
        """Render detailed task information"""
        task = next((t for t in st.session_state.tasks if t.id == task_id), None)
        if not task:
            return
        
        st.subheader(f"Task {task.id} Details")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Type:** {task.task_type.value}")
            st.write(f"**Status:** {task.status.value}")
            st.write(f"**Priority:** {task.priority.value}")
            st.write(f"**Repository:** {task.repository}")
        
        with col2:
            st.write(f"**Created:** {task.created_at}")
            if task.updated_at:
                st.write(f"**Updated:** {task.updated_at}")
            if task.completed_at:
                st.write(f"**Completed:** {task.completed_at}")
            if task.workspace:
                st.write(f"**Workspace:** {task.workspace}")
        
        # Prompt
        if task.prompt:
            st.subheader("Prompt")
            st.text_area("Task Prompt", value=task.prompt, height=200, disabled=True)
        
        # Result
        if task.result:
            st.subheader("Result")
            st.text_area("Task Result", value=task.result, height=200, disabled=True)
        
        # Error message
        if task.error_message:
            st.subheader("Error")
            st.error(task.error_message)
        
        # Logs
        if st.button("📜 Load Logs", key=f"logs_{task.id}"):
            self._load_task_logs(task.id)
    
    def _render_analytics_tab(self):
        """Render analytics and reporting tab"""
        st.subheader("📈 Analytics")
        
        if not st.session_state.tasks:
            st.info("No data available for analytics.")
            return
        
        # Time-based analysis
        self._render_time_analysis()
        
        # Task type analysis
        self._render_type_analysis()
        
        # Performance metrics
        self._render_performance_metrics()
    
    def _render_time_analysis(self):
        """Render time-based task analysis"""
        st.subheader("📅 Task Timeline")
        
        # Prepare data
        timeline_data = []
        for task in st.session_state.tasks:
            timeline_data.append({
                "Date": task.created_at.date(),
                "Status": task.status.value,
                "Type": task.task_type.value,
                "Count": 1
            })
        
        df = pd.DataFrame(timeline_data)
        
        if not df.empty:
            # Group by date and status
            daily_counts = df.groupby(["Date", "Status"]).sum().reset_index()
            
            # Create timeline chart
            fig = px.line(
                daily_counts,
                x="Date",
                y="Count",
                color="Status",
                title="Daily Task Creation"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_type_analysis(self):
        """Render task type analysis"""
        st.subheader("🏷️ Task Type Distribution")
        
        type_counts = {}
        for task in st.session_state.tasks:
            task_type = task.task_type.value
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
        
        if type_counts:
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Tasks by Type"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_metrics(self):
        """Render performance metrics"""
        st.subheader("⚡ Performance Metrics")
        
        # Calculate completion times for completed tasks
        completion_times = []
        for task in st.session_state.tasks:
            if task.completed_at and task.created_at:
                duration = (task.completed_at - task.created_at).total_seconds() / 60  # minutes
                completion_times.append({
                    "Task ID": task.id,
                    "Type": task.task_type.value,
                    "Duration (minutes)": duration,
                    "Status": task.status.value
                })
        
        if completion_times:
            df = pd.DataFrame(completion_times)
            
            # Average completion time by type
            avg_times = df.groupby("Type")["Duration (minutes)"].mean().reset_index()
            
            fig = px.bar(
                avg_times,
                x="Type",
                y="Duration (minutes)",
                title="Average Completion Time by Task Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No completed tasks available for performance analysis.")
    
    def _render_create_task_tab(self):
        """Render create new task tab"""
        st.subheader("➕ Create New Task")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                task_type = st.selectbox(
                    "Task Type",
                    options=[t.value for t in TaskType],
                    help="Select the type of task to create"
                )
                
                repository = st.text_input(
                    "Repository",
                    placeholder="https://github.com/user/repo or repo-name",
                    help="Repository URL or name"
                )
                
                priority = st.selectbox(
                    "Priority",
                    options=[p.value for p in Priority],
                    index=1,  # Default to MEDIUM
                    help="Task priority level"
                )
            
            with col2:
                workspace = st.text_input(
                    "Workspace (Optional)",
                    placeholder="workspace-name",
                    help="Workspace name if using workspaces"
                )
                
                custom_message = st.text_area(
                    "Custom Instructions (Optional)",
                    placeholder="Additional instructions for the task...",
                    help="Custom message to include with the task"
                )
            
            # Template variables (advanced)
            with st.expander("Advanced: Template Variables"):
                template_vars_json = st.text_area(
                    "Template Variables (JSON)",
                    placeholder='{"key": "value"}',
                    help="Additional template variables as JSON"
                )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Create Task")
            
            if submitted:
                self._create_new_task(
                    task_type=TaskType(task_type),
                    repository=repository,
                    priority=Priority(priority),
                    workspace=workspace or None,
                    custom_message=custom_message or None,
                    template_vars_json=template_vars_json or None
                )
    
    def _render_settings_tab(self):
        """Render settings and configuration tab"""
        st.subheader("⚙️ Settings")
        
        # API Configuration
        st.subheader("API Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "API Token",
                value="***" if os.getenv("CODEGEN_API_TOKEN") else "",
                disabled=True,
                help="Set via CODEGEN_API_TOKEN environment variable"
            )
        
        with col2:
            st.text_input(
                "Organization ID",
                value=os.getenv("CODEGEN_ORG_ID", ""),
                disabled=True,
                help="Set via CODEGEN_ORG_ID environment variable"
            )
        
        # Dashboard Settings
        st.subheader("Dashboard Settings")
        
        # Theme selection
        theme = st.selectbox(
            "Theme",
            options=["Light", "Dark", "Auto"],
            index=0
        )
        
        # Data retention
        retention_days = st.slider(
            "Local Data Retention (days)",
            min_value=1,
            max_value=365,
            value=30,
            help="How long to keep task data locally"
        )
        
        # Export/Import
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Data"):
                self._export_data()
        
        with col2:
            uploaded_file = st.file_uploader("📥 Import Data", type=['json'])
            if uploaded_file:
                self._import_data(uploaded_file)
    
    def _refresh_data(self):
        """Refresh task data from API"""
        try:
            with st.spinner("Refreshing data..."):
                # Get tasks from task manager
                tasks = self.task_manager.list_tasks(limit=100)
                st.session_state.tasks = tasks
                st.session_state.last_refresh = datetime.now()
                
                st.success(f"Refreshed {len(tasks)} tasks")
                
        except Exception as e:
            st.error(f"Failed to refresh data: {e}")
            logger.error(f"Data refresh error: {e}")
    
    def _apply_filters(self, tasks: List[Task]) -> List[Task]:
        """Apply filters to task list"""
        filtered = tasks
        
        # Status filter
        if st.session_state.get('status_filter'):
            filtered = [t for t in filtered if t.status.value in st.session_state.status_filter]
        
        # Type filter
        if st.session_state.get('type_filter'):
            filtered = [t for t in filtered if t.task_type.value in st.session_state.type_filter]
        
        return filtered
    
    def _create_new_task(
        self,
        task_type: TaskType,
        repository: str,
        priority: Priority,
        workspace: Optional[str] = None,
        custom_message: Optional[str] = None,
        template_vars_json: Optional[str] = None
    ):
        """Create a new task"""
        
        if not repository:
            st.error("Repository is required")
            return
        
        try:
            # Parse template variables
            template_vars = {}
            if template_vars_json:
                template_vars = json.loads(template_vars_json)
            
            # Create task
            with st.spinner("Creating task..."):
                task = self.task_manager.create_task(
                    task_type=task_type,
                    repository=repository,
                    message=custom_message,
                    template_vars=template_vars,
                    workspace=workspace,
                    priority=priority
                )
            
            st.success(f"✅ Created task {task.id}")
            
            # Refresh data
            self._refresh_data()
            
        except json.JSONDecodeError:
            st.error("Invalid JSON in template variables")
        except Exception as e:
            st.error(f"Failed to create task: {e}")
            logger.error(f"Task creation error: {e}")
    
    def _show_resume_dialog(self, task: Task):
        """Show resume task dialog"""
        st.subheader(f"Resume Task {task.id}")
        
        with st.form(f"resume_form_{task.id}"):
            message = st.text_area(
                "Resume Message",
                placeholder="Enter message to continue with...",
                help="Message to resume the task with"
            )
            
            submitted = st.form_submit_button("▶️ Resume Task")
            
            if submitted and message:
                try:
                    with st.spinner("Resuming task..."):
                        updated_task = self.task_manager.resume_task(task.id, message)
                    
                    st.success(f"✅ Resumed task {task.id}")
                    self._refresh_data()
                    
                except Exception as e:
                    st.error(f"Failed to resume task: {e}")
    
    def _cancel_task(self, task: Task):
        """Cancel a task"""
        try:
            with st.spinner("Cancelling task..."):
                success = self.task_manager.cancel_task(task.id)
            
            if success:
                st.success(f"✅ Cancelled task {task.id}")
                self._refresh_data()
            else:
                st.error("Failed to cancel task")
                
        except Exception as e:
            st.error(f"Failed to cancel task: {e}")
    
    def _load_task_logs(self, task_id: int):
        """Load and display task logs"""
        try:
            with st.spinner("Loading logs..."):
                logs = self.task_manager.get_task_logs(task_id, limit=50)
            
            if logs:
                st.subheader(f"Logs for Task {task_id}")
                
                for log in logs:
                    timestamp = log.get('created_at', 'Unknown')
                    message_type = log.get('message_type', 'info')
                    content = log.get('thought') or log.get('observation', 'No content')
                    
                    with st.expander(f"[{timestamp}] {message_type}"):
                        st.text(content)
            else:
                st.info("No logs available for this task")
                
        except Exception as e:
            st.error(f"Failed to load logs: {e}")
    
    def _generate_report(self):
        """Generate and download report"""
        try:
            # Create report data
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "total_tasks": len(st.session_state.tasks),
                "tasks": []
            }
            
            for task in st.session_state.tasks:
                report_data["tasks"].append({
                    "id": task.id,
                    "type": task.task_type.value,
                    "status": task.status.value,
                    "repository": task.repository,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                })
            
            # Convert to JSON
            report_json = json.dumps(report_data, indent=2)
            
            # Provide download
            st.download_button(
                label="📥 Download Report",
                data=report_json,
                file_name=f"codegen_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Failed to generate report: {e}")
    
    def _cleanup_old_tasks(self):
        """Cleanup old completed tasks"""
        try:
            # This would use the state store cleanup functionality
            if hasattr(self.task_manager, 'state_store'):
                cleaned = self.task_manager.state_store.clear_completed_tasks(older_than_days=30)
                st.success(f"Cleaned up {cleaned} old tasks")
            else:
                st.info("Cleanup functionality not available")
                
        except Exception as e:
            st.error(f"Failed to cleanup tasks: {e}")
    
    def _export_data(self):
        """Export dashboard data"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "tasks": [
                    {
                        "id": task.id,
                        "type": task.task_type.value,
                        "status": task.status.value,
                        "repository": task.repository,
                        "workspace": task.workspace,
                        "priority": task.priority.value,
                        "created_at": task.created_at.isoformat(),
                        "metadata": task.metadata
                    }
                    for task in st.session_state.tasks
                ]
            }
            
            export_json = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download Export",
                data=export_json,
                file_name=f"codegen_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Failed to export data: {e}")
    
    def _import_data(self, uploaded_file):
        """Import dashboard data"""
        try:
            import_data = json.load(uploaded_file)
            
            # Validate import data structure
            if "tasks" not in import_data:
                st.error("Invalid import file format")
                return
            
            st.success(f"Imported {len(import_data['tasks'])} tasks")
            
            # Note: In a real implementation, you'd want to merge this with existing data
            # and handle conflicts appropriately
            
        except Exception as e:
            st.error(f"Failed to import data: {e}")


def main():
    """Main application entry point"""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()

