#!/usr/bin/env python3
"""
Codegen Agent Run Management Dashboard
A comprehensive web interface for managing and monitoring Codegen agent runs.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import sys
import os

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
from mock_api_service import get_mock_api, AgentRunStatus

# Page configuration
st.set_page_config(
    page_title="Codegen Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-running {
        color: #ff7f0e;
        font-weight: bold;
    }
    .status-completed {
        color: #2ca02c;
        font-weight: bold;
    }
    .status-failed {
        color: #d62728;
        font-weight: bold;
    }
    .status-pending {
        color: #9467bd;
        font-weight: bold;
    }
    .status-cancelled {
        color: #8c564b;
        font-weight: bold;
    }
    .status-paused {
        color: #e377c2;
        font-weight: bold;
    }
    .run-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api' not in st.session_state:
    st.session_state.api = get_mock_api()
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 5

def get_status_color(status):
    """Get color for status display"""
    colors = {
        'running': '#ff7f0e',
        'completed': '#2ca02c',
        'failed': '#d62728',
        'pending': '#9467bd',
        'cancelled': '#8c564b',
        'paused': '#e377c2'
    }
    return colors.get(status, '#1f77b4')

def format_status(status):
    """Format status with color"""
    color = get_status_color(status)
    return f'<span style="color: {color}; font-weight: bold;">{status.upper()}</span>'

def format_datetime(dt_str):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_str

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Codegen Agent Run Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Auto-refresh controls
        st.subheader("Auto Refresh")
        auto_refresh = st.checkbox("Enable Auto Refresh", value=st.session_state.auto_refresh)
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider("Refresh Interval (seconds)", 1, 30, st.session_state.refresh_interval)
            st.session_state.refresh_interval = refresh_interval
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        
        # Status filter
        status_options = ['All'] + [status.value for status in AgentRunStatus]
        selected_status = st.selectbox("Status", status_options)
        
        # Project filter
        projects = st.session_state.api.get_projects(323)
        project_options = ['All'] + [f"{p.name} ({p.id})" for p in projects]
        selected_project = st.selectbox("Project", project_options)
        
        # Date range filter
        date_range = st.selectbox("Date Range", [
            "Last 24 hours",
            "Last 7 days", 
            "Last 30 days",
            "All time"
        ], index=1)
        
        # Search
        search_query = st.text_input("🔍 Search runs", placeholder="Search prompts, results...")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("➕ Create New Run"):
            st.session_state.show_create_modal = True
        
        if st.button("📊 View Analytics"):
            st.session_state.current_tab = "Analytics"
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Dashboard", "🏃 Active Runs", "📊 Analytics", "⚙️ Management"])
    
    with tab1:
        show_dashboard_overview()
    
    with tab2:
        show_active_runs(selected_status, selected_project, search_query)
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_management_tools()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.rerun()

def show_dashboard_overview():
    """Show main dashboard overview"""
    
    api = st.session_state.api
    
    # Get statistics
    stats = api.get_run_statistics(323, days=7)
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Runs (7d)",
            value=stats['total_runs'],
            delta=f"+{stats['total_runs'] - stats.get('previous_total', 0)}"
        )
    
    with col2:
        st.metric(
            label="Success Rate",
            value=f"{stats['success_rate']}%",
            delta=f"+{stats['success_rate'] - 85:.1f}%"  # Mock comparison
        )
    
    with col3:
        st.metric(
            label="Total Cost",
            value=f"${stats['total_cost']}",
            delta=f"+${stats['total_cost'] - 15.50:.2f}"  # Mock comparison
        )
    
    with col4:
        st.metric(
            label="Avg Cost/Run",
            value=f"${stats['average_cost_per_run']}",
            delta=f"-${0.05:.2f}"  # Mock improvement
        )
    
    with col5:
        st.metric(
            label="Total Tokens",
            value=f"{stats['total_tokens']:,}",
            delta=f"+{stats['total_tokens'] - 45000:,}"  # Mock comparison
        )
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution pie chart
        status_data = stats['status_breakdown']
        fig_pie = px.pie(
            values=list(status_data.values()),
            names=list(status_data.keys()),
            title="Run Status Distribution (Last 7 Days)",
            color_discrete_map={
                'completed': '#2ca02c',
                'running': '#ff7f0e',
                'failed': '#d62728',
                'pending': '#9467bd',
                'cancelled': '#8c564b',
                'paused': '#e377c2'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Recent runs timeline
        runs_data = api.list_agent_runs(323, limit=20)
        df_runs = pd.DataFrame(runs_data['items'])
        
        if not df_runs.empty:
            df_runs['created_at'] = pd.to_datetime(df_runs['created_at'])
            df_runs['hour'] = df_runs['created_at'].dt.floor('H')
            
            hourly_counts = df_runs.groupby(['hour', 'status']).size().reset_index(name='count')
            
            fig_timeline = px.bar(
                hourly_counts,
                x='hour',
                y='count',
                color='status',
                title="Runs Created Over Time (Last 20 Runs)",
                color_discrete_map={
                    'completed': '#2ca02c',
                    'running': '#ff7f0e',
                    'failed': '#d62728',
                    'pending': '#9467bd',
                    'cancelled': '#8c564b',
                    'paused': '#e377c2'
                }
            )
            fig_timeline.update_layout(xaxis_title="Time", yaxis_title="Number of Runs")
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.divider()
    
    # Recent runs table
    st.subheader("📋 Recent Runs")
    
    runs_data = api.list_agent_runs(323, limit=10)
    if runs_data['items']:
        df_recent = pd.DataFrame(runs_data['items'])
        
        # Format the dataframe for display
        display_df = df_recent[['id', 'status', 'prompt', 'project_name', 'created_at', 'progress', 'cost']].copy()
        display_df['prompt'] = display_df['prompt'].str[:60] + '...'
        display_df['created_at'] = display_df['created_at'].apply(format_datetime)
        display_df['progress'] = display_df['progress'].astype(str) + '%'
        display_df['cost'] = '$' + display_df['cost'].astype(str)
        
        # Rename columns for display
        display_df.columns = ['ID', 'Status', 'Prompt', 'Project', 'Created', 'Progress', 'Cost']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current run status"
                ),
                "Progress": st.column_config.ProgressColumn(
                    "Progress",
                    help="Completion percentage",
                    min_value=0,
                    max_value=100,
                    format="%d%%"
                )
            }
        )

def show_active_runs(status_filter, project_filter, search_query):
    """Show active runs with filtering"""
    
    api = st.session_state.api
    
    # Apply filters
    filter_status = None if status_filter == 'All' else status_filter
    filter_project_id = None
    if project_filter != 'All':
        # Extract project ID from "Name (ID)" format
        filter_project_id = int(project_filter.split('(')[-1].rstrip(')'))
    
    # Get filtered runs
    runs_data = api.list_agent_runs(
        323, 
        limit=50, 
        status=filter_status,
        project_id=filter_project_id
    )
    
    # Apply search filter
    filtered_runs = runs_data['items']
    if search_query:
        filtered_runs = [
            run for run in filtered_runs
            if search_query.lower() in run['prompt'].lower() or
               search_query.lower() in (run.get('result', '') or '').lower()
        ]
    
    st.subheader(f"🏃 Active Runs ({len(filtered_runs)} found)")
    
    if not filtered_runs:
        st.info("No runs found matching the current filters.")
        return
    
    # Bulk actions
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Bulk Actions:**")
    with col2:
        if st.button("⏸️ Pause Selected"):
            st.info("Bulk pause functionality would be implemented here")
    with col3:
        if st.button("❌ Cancel Selected"):
            st.info("Bulk cancel functionality would be implemented here")
    
    st.divider()
    
    # Display runs
    for run in filtered_runs:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**Run #{run['id']}** - {run['project_name']}")
                st.markdown(f"*{run['prompt'][:100]}...*")
                st.markdown(f"Created: {format_datetime(run['created_at'])}")
            
            with col2:
                status_html = format_status(run['status'])
                st.markdown(status_html, unsafe_allow_html=True)
                st.progress(run['progress'] / 100)
                st.caption(f"{run['progress']}% complete")
            
            with col3:
                st.metric("Cost", f"${run['cost']}")
                st.metric("Tokens", f"{run['tokens_used']:,}")
            
            with col4:
                if st.button(f"👁️ View", key=f"view_{run['id']}"):
                    show_run_details(run)
                
                if run['status'] in ['running', 'pending']:
                    if st.button(f"⏸️ Pause", key=f"pause_{run['id']}"):
                        api.pause_agent_run(323, run['id'])
                        st.success(f"Paused run #{run['id']}")
                        st.rerun()
                
                if run['status'] == 'paused':
                    if st.button(f"▶️ Resume", key=f"resume_{run['id']}"):
                        resume_prompt = st.text_input(f"Resume prompt for #{run['id']}", key=f"resume_prompt_{run['id']}")
                        if resume_prompt:
                            api.resume_agent_run(323, run['id'], resume_prompt)
                            st.success(f"Resumed run #{run['id']}")
                            st.rerun()
                
                if run['status'] in ['running', 'pending', 'paused']:
                    if st.button(f"❌ Cancel", key=f"cancel_{run['id']}"):
                        api.cancel_agent_run(323, run['id'])
                        st.success(f"Cancelled run #{run['id']}")
                        st.rerun()
            
            st.divider()

def show_run_details(run):
    """Show detailed view of a specific run"""
    
    api = st.session_state.api
    
    with st.expander(f"📋 Run #{run['id']} Details", expanded=True):
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Status:** {format_status(run['status'])}", unsafe_allow_html=True)
            st.markdown(f"**Project:** {run['project_name']}")
            st.markdown(f"**Created:** {format_datetime(run['created_at'])}")
            st.markdown(f"**Updated:** {format_datetime(run['updated_at'])}")
        
        with col2:
            st.markdown(f"**Progress:** {run['progress']}%")
            st.markdown(f"**Cost:** ${run['cost']}")
            st.markdown(f"**Tokens:** {run['tokens_used']:,}")
            if run.get('estimated_completion'):
                st.markdown(f"**ETA:** {format_datetime(run['estimated_completion'])}")
        
        # Prompt
        st.markdown("**Prompt:**")
        st.text_area("", value=run['prompt'], height=100, disabled=True, key=f"prompt_{run['id']}")
        
        # Result (if completed)
        if run.get('result'):
            st.markdown("**Result:**")
            st.text_area("", value=run['result'], height=150, disabled=True, key=f"result_{run['id']}")
        
        # Metadata
        if run.get('metadata'):
            st.markdown("**Metadata:**")
            st.json(run['metadata'])
        
        # Logs
        st.markdown("**Recent Logs:**")
        logs = api.get_agent_run_logs(323, run['id'], limit=10)
        if logs:
            for log in logs[-5:]:  # Show last 5 logs
                timestamp = format_datetime(log.timestamp)
                st.markdown(f"`{timestamp}` **{log.level}**: {log.message}")
        else:
            st.info("No logs available")
        
        # Web URL
        if run.get('web_url'):
            st.markdown(f"**Web URL:** [View in Codegen]({run['web_url']})")

def show_analytics():
    """Show analytics and reporting"""
    
    api = st.session_state.api
    
    st.subheader("📊 Analytics & Reporting")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        period = st.selectbox("Time Period", [7, 14, 30, 90], format_func=lambda x: f"Last {x} days")
    
    # Get statistics
    stats = api.get_run_statistics(323, days=period)
    
    # Performance metrics
    st.subheader("📈 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Runs", stats['total_runs'])
    with col2:
        st.metric("Success Rate", f"{stats['success_rate']}%")
    with col3:
        st.metric("Total Cost", f"${stats['total_cost']}")
    with col4:
        st.metric("Avg Cost/Run", f"${stats['average_cost_per_run']}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Project breakdown
        projects = api.get_projects(323)
        project_stats = []
        for project in projects:
            project_runs = api.list_agent_runs(323, limit=100, project_id=project.id)
            project_stats.append({
                'project': project.name,
                'runs': len(project_runs['items']),
                'cost': sum(run['cost'] for run in project_runs['items'])
            })
        
        if project_stats:
            df_projects = pd.DataFrame(project_stats)
            fig_projects = px.bar(
                df_projects,
                x='project',
                y='runs',
                title="Runs by Project",
                color='cost',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_projects, use_container_width=True)
    
    with col2:
        # Cost over time (simulated)
        dates = pd.date_range(end=datetime.now(), periods=period, freq='D')
        daily_costs = [stats['total_cost'] / period * (1 + 0.1 * (i % 3 - 1)) for i in range(period)]
        
        fig_cost = px.line(
            x=dates,
            y=daily_costs,
            title="Daily Cost Trend",
            labels={'x': 'Date', 'y': 'Cost ($)'}
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Detailed breakdown
    st.subheader("📋 Detailed Breakdown")
    
    # Status breakdown table
    status_df = pd.DataFrame([
        {'Status': status, 'Count': count, 'Percentage': f"{(count/stats['total_runs']*100):.1f}%"}
        for status, count in stats['status_breakdown'].items()
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Status Breakdown:**")
        st.dataframe(status_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**Export Options:**")
        if st.button("📥 Export CSV"):
            st.info("CSV export functionality would be implemented here")
        if st.button("📊 Generate Report"):
            st.info("Report generation functionality would be implemented here")

def show_management_tools():
    """Show management and administration tools"""
    
    api = st.session_state.api
    
    st.subheader("⚙️ Management Tools")
    
    # Create new run
    with st.expander("➕ Create New Run", expanded=False):
        with st.form("create_run_form"):
            prompt = st.text_area("Prompt", height=100, placeholder="Describe the task for the agent...")
            
            col1, col2 = st.columns(2)
            with col1:
                projects = api.get_projects(323)
                project_options = {f"{p.name}": p.id for p in projects}
                selected_project = st.selectbox("Project", list(project_options.keys()))
            
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high"])
            
            # Metadata
            st.markdown("**Metadata (Optional):**")
            col1, col2 = st.columns(2)
            with col1:
                tags = st.text_input("Tags (comma-separated)", placeholder="frontend, api, testing")
            with col2:
                complexity = st.selectbox("Complexity", ["simple", "medium", "complex"])
            
            submitted = st.form_submit_button("🚀 Create Run")
            
            if submitted and prompt:
                metadata = {
                    "priority": priority,
                    "complexity": complexity,
                    "source": "dashboard"
                }
                if tags:
                    metadata["tags"] = [tag.strip() for tag in tags.split(",")]
                
                new_run = api.create_agent_run(
                    323, 
                    prompt, 
                    metadata=metadata,
                    project_id=project_options[selected_project]
                )
                
                st.success(f"✅ Created new run #{new_run.id}")
                st.markdown(f"**Web URL:** [View Run]({new_run.web_url})")
    
    st.divider()
    
    # Bulk operations
    st.subheader("🔧 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Cancel Multiple Runs:**")
        run_ids_text = st.text_area("Run IDs (comma-separated)", placeholder="1001, 1002, 1003")
        if st.button("❌ Cancel Selected Runs"):
            if run_ids_text:
                try:
                    run_ids = [int(id.strip()) for id in run_ids_text.split(",")]
                    result = api.bulk_cancel_runs(323, run_ids)
                    st.success(f"✅ Cancelled {len(result['cancelled'])} runs")
                    if result['failed']:
                        st.warning(f"⚠️ Failed to cancel {len(result['failed'])} runs")
                except ValueError:
                    st.error("❌ Invalid run IDs format")
    
    with col2:
        st.markdown("**System Information:**")
        st.info(f"**Organization ID:** 323")
        st.info(f"**Total Runs:** {len(api.agent_runs)}")
        st.info(f"**Active Projects:** {len(api.projects)}")
        st.info(f"**API Status:** ✅ Connected (Mock)")
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Dashboard Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Display Settings:**")
        items_per_page = st.slider("Items per page", 10, 100, 20)
        show_timestamps = st.checkbox("Show full timestamps", value=True)
        dark_mode = st.checkbox("Dark mode", value=False)
    
    with col2:
        st.markdown("**Notification Settings:**")
        notify_completion = st.checkbox("Notify on completion", value=True)
        notify_failures = st.checkbox("Notify on failures", value=True)
        email_reports = st.checkbox("Email daily reports", value=False)
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved successfully")

if __name__ == "__main__":
    main()

