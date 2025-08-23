"""
Main application class for the Codegen UI.

This module provides the main application class for the Codegen UI,
coordinating between the UI components and the application controller.
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import sys
from typing import Any, Dict, List, Optional, Callable

from ui.core.controller import Controller
from ui.core.events import EventBus, Event, EventType
from ui.frames.agent_runs_frame import AgentRunsFrame
from ui.frames.starred_runs_frame import StarredRunsFrame
from ui.frames.projects_frame import ProjectsFrame
from ui.frames.templates_frame import TemplatesFrame
from ui.frames.agent_run_detail_frame import AgentRunDetailFrame
from ui.utils.constants import THEME, DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE, PADDING, EVENT_TYPES

logger = logging.getLogger(__name__)

class Application:
    """
    Main application class for the Codegen UI.
    
    This class coordinates between the UI components and the application controller,
    handling application lifecycle and event routing.
    """
    
    def __init__(self):
        """Initialize the application."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize controller
        self.controller = Controller()
        
        # Initialize UI
        self.root = tk.Tk()
        self.root.title("Codegen UI")
        self.root.geometry(f"{DEFAULT_WINDOW_SIZE[0]}x{DEFAULT_WINDOW_SIZE[1]}")
        self.root.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use(THEME)
        
        # Configure styles
        self._configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=PADDING)
        
        # Create title
        self.title_label = ttk.Label(
            self.header_frame,
            text="Codegen UI",
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Create refresh button
        self.refresh_button = ttk.Button(
            self.header_frame,
            text="Refresh",
            command=self._on_refresh_click
        )
        self.refresh_button.pack(side=tk.RIGHT)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=(0, PADDING))
        
        # Create sidebar frame
        self.sidebar_frame = ttk.Frame(self.content_frame, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, PADDING))
        self.sidebar_frame.pack_propagate(False)
        
        # Create sidebar buttons
        self.agent_runs_button = ttk.Button(
            self.sidebar_frame,
            text="Agent Runs",
            command=self._on_agent_runs_click
        )
        self.agent_runs_button.pack(fill=tk.X, pady=(0, PADDING))
        
        self.starred_runs_button = ttk.Button(
            self.sidebar_frame,
            text="Starred Runs",
            command=self._on_starred_runs_click
        )
        self.starred_runs_button.pack(fill=tk.X, pady=(0, PADDING))
        
        self.projects_button = ttk.Button(
            self.sidebar_frame,
            text="Projects",
            command=self._on_projects_click
        )
        self.projects_button.pack(fill=tk.X, pady=(0, PADDING))
        
        self.templates_button = ttk.Button(
            self.sidebar_frame,
            text="Templates",
            command=self._on_templates_click
        )
        self.templates_button.pack(fill=tk.X, pady=(0, PADDING))
        
        self.settings_button = ttk.Button(
            self.sidebar_frame,
            text="Settings",
            command=self._on_settings_click
        )
        self.settings_button.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create main content frame
        self.main_content_frame = ttk.Frame(self.content_frame)
        self.main_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create frames
        self.agent_runs_frame = AgentRunsFrame(self.main_content_frame, self.controller)
        self.starred_runs_frame = StarredRunsFrame(self.main_content_frame, self.controller)
        self.projects_frame = ProjectsFrame(self.main_content_frame, self.controller)
        self.templates_frame = TemplatesFrame(self.main_content_frame, self.controller)
        self.agent_run_detail_frame = AgentRunDetailFrame(self.main_content_frame, self.controller)
        
        # Create status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=(0, PADDING))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Show initial view
        self._show_agent_runs()
    
    def _configure_styles(self):
        """Configure ttk styles."""
        # Configure header style
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 16, "bold")
        )
        
        # Configure subheader style
        self.style.configure(
            "Subheader.TLabel",
            font=("Helvetica", 12, "bold")
        )
        
        # Configure bold style
        self.style.configure(
            "Bold.TLabel",
            font=("Helvetica", 10, "bold")
        )
        
        # Configure small style
        self.style.configure(
            "Small.TLabel",
            font=("Helvetica", 8)
        )
        
        # Configure large style
        self.style.configure(
            "Large.TLabel",
            font=("Helvetica", 14)
        )
        
        # Configure primary button style
        self.style.configure(
            "Primary.TButton",
            background="#2196F3",
            foreground="#FFFFFF"
        )
        
        # Configure secondary button style
        self.style.configure(
            "Secondary.TButton",
            background="#4CAF50",
            foreground="#FFFFFF"
        )
        
        # Configure error style
        self.style.configure(
            "Error.TLabel",
            foreground="#F44336"
        )
        
        # Configure success style
        self.style.configure(
            "Success.TLabel",
            foreground="#4CAF50"
        )
        
        # Configure warning style
        self.style.configure(
            "Warning.TLabel",
            foreground="#FFC107"
        )
        
        # Configure info style
        self.style.configure(
            "Info.TLabel",
            foreground="#2196F3"
        )
        
        # Configure status styles
        self.style.configure(
            "RUNNING.TLabel",
            foreground="#2196F3"
        )
        
        self.style.configure(
            "COMPLETED.TLabel",
            foreground="#4CAF50"
        )
        
        self.style.configure(
            "ERROR.TLabel",
            foreground="#F44336"
        )
        
        self.style.configure(
            "PAUSED.TLabel",
            foreground="#FFC107"
        )
        
        self.style.configure(
            "UNKNOWN.TLabel",
            foreground="#9E9E9E"
        )
        
        # Configure star button style
        self.style.configure(
            "Star.TButton",
            background="#FFD700",
            foreground="#000000"
        )
        
        # Configure unstar button style
        self.style.configure(
            "Unstar.TButton",
            background="#CCCCCC",
            foreground="#000000"
        )
        
        # Configure card style
        self.style.configure(
            "Card.TFrame",
            background="#F5F5F5",
            relief=tk.RAISED,
            borderwidth=1
        )
    
    def _setup_event_handlers(self):
        """Set up event handlers."""
        # Set up root window event handlers
        self.root.bind("<Control-q>", lambda e: self._on_close())
        self.root.bind("<F1>", lambda e: self._show_help())
        self.root.bind("<F5>", lambda e: self._on_refresh_click())
        
        # Set up controller event handlers
        self.controller.event_bus.subscribe(EVENT_TYPES["LOGIN"], self._on_login)
        self.controller.event_bus.subscribe(EVENT_TYPES["LOGOUT"], self._on_logout)
        self.controller.event_bus.subscribe(EVENT_TYPES["NOTIFICATION_RECEIVED"], self._on_notification_received)
    
    def _on_close(self):
        """Handle window close event."""
        # Clean up resources
        self.controller.event_bus.clear()
        
        # Destroy root window
        self.root.destroy()
        
        # Exit application
        sys.exit(0)
    
    def _show_help(self):
        """Show help dialog."""
        # Create help dialog
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Codegen UI Help")
        help_dialog.geometry("600x400")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Create help text
        help_text = tk.Text(help_dialog, wrap=tk.WORD, padx=10, pady=10)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Add help content
        help_text.insert(tk.END, "Codegen UI Help\\n\\n")
        help_text.insert(tk.END, "Keyboard Shortcuts:\\n")
        help_text.insert(tk.END, "  Ctrl+Q: Quit application\\n")
        help_text.insert(tk.END, "  F1: Show this help dialog\\n")
        help_text.insert(tk.END, "  F5: Refresh current view\\n")
        help_text.insert(tk.END, "\\n")
        help_text.insert(tk.END, "Views:\\n")
        help_text.insert(tk.END, "  Agent Runs: View and manage agent runs\\n")
        help_text.insert(tk.END, "  Starred Runs: View and manage starred agent runs\\n")
        help_text.insert(tk.END, "  Projects: View and manage projects\\n")
        help_text.insert(tk.END, "  Templates: View and manage templates\\n")
        help_text.insert(tk.END, "  Settings: Configure application settings\\n")
        help_text.insert(tk.END, "\\n")
        help_text.insert(tk.END, "For more information, visit https://docs.codegen.com\\n")
        
        # Make text read-only
        help_text.config(state=tk.DISABLED)
        
        # Create close button
        close_button = ttk.Button(
            help_dialog,
            text="Close",
            command=help_dialog.destroy
        )
        close_button.pack(pady=10)
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        self.controller.refresh()
    
    def _on_agent_runs_click(self):
        """Handle agent runs button click."""
        self._show_agent_runs()
    
    def _on_starred_runs_click(self):
        """Handle starred runs button click."""
        self._show_starred_runs()
    
    def _on_projects_click(self):
        """Handle projects button click."""
        self._show_projects()
    
    def _on_templates_click(self):
        """Handle templates button click."""
        self._show_templates()
    
    def _on_settings_click(self):
        """Handle settings button click."""
        self._show_settings()
    
    def _on_login(self, event):
        """
        Handle login event.
        
        Args:
            event: Event data
        """
        self.status_label.config(text="Logged in")
        self._show_agent_runs()
    
    def _on_logout(self, event):
        """
        Handle logout event.
        
        Args:
            event: Event data
        """
        self.status_label.config(text="Logged out")
        self._show_login()
    
    def _on_notification_received(self, event):
        """
        Handle notification received event.
        
        Args:
            event: Event data
        """
        notification = event.get("notification")
        if notification:
            notification_type = notification.get("type")
            if notification_type == "agent_run_completed":
                agent_run_id = notification.get("agent_run_id")
                self.status_label.config(text=f"Agent run {agent_run_id} completed")
            elif notification_type == "agent_run_error":
                agent_run_id = notification.get("agent_run_id")
                self.status_label.config(text=f"Agent run {agent_run_id} failed")
            elif notification_type == "agent_run_paused":
                agent_run_id = notification.get("agent_run_id")
                self.status_label.config(text=f"Agent run {agent_run_id} paused")
            elif notification_type == "follow_up_action_required":
                agent_run_id = notification.get("agent_run_id")
                self.status_label.config(text=f"Follow-up action required for agent run {agent_run_id}")
    
    def _show_login(self):
        """Show login view."""
        # Hide all frames
        self._hide_all_frames()
        
        # TODO: Implement login frame
    
    def _show_agent_runs(self):
        """Show agent runs view."""
        # Hide all frames
        self._hide_all_frames()
        
        # Show agent runs frame
        self.agent_runs_frame.show()
        
        # Update controller
        self.controller.show_agent_runs()
        
        # Update title
        self.title_label.config(text="Agent Runs")
    
    def _show_starred_runs(self):
        """Show starred runs view."""
        # Hide all frames
        self._hide_all_frames()
        
        # Show starred runs frame
        self.starred_runs_frame.show()
        
        # Update controller
        self.controller.show_starred_runs()
        
        # Update title
        self.title_label.config(text="Starred Runs")
    
    def _show_projects(self):
        """Show projects view."""
        # Hide all frames
        self._hide_all_frames()
        
        # Show projects frame
        self.projects_frame.show()
        
        # Update controller
        self.controller.show_projects()
        
        # Update title
        self.title_label.config(text="Projects")
    
    def _show_templates(self):
        """Show templates view."""
        # Hide all frames
        self._hide_all_frames()
        
        # Show templates frame
        self.templates_frame.show()
        
        # Update controller
        self.controller.show_templates()
        
        # Update title
        self.title_label.config(text="Templates")
    
    def _show_settings(self):
        """Show settings view."""
        # Hide all frames
        self._hide_all_frames()
        
        # TODO: Implement settings frame
        
        # Update controller
        self.controller.show_settings()
        
        # Update title
        self.title_label.config(text="Settings")
    
    def _show_agent_run_detail(self, agent_run_id):
        """
        Show agent run detail view.
        
        Args:
            agent_run_id: Agent run ID
        """
        # Hide all frames
        self._hide_all_frames()
        
        # Show agent run detail frame
        self.agent_run_detail_frame.load_agent_run(agent_run_id)
        self.agent_run_detail_frame.show()
        
        # Update controller
        self.controller.show_agent_run_detail(agent_run_id)
        
        # Update title
        self.title_label.config(text=f"Agent Run #{agent_run_id}")
    
    def _hide_all_frames(self):
        """Hide all frames."""
        self.agent_runs_frame.hide()
        self.starred_runs_frame.hide()
        self.projects_frame.hide()
        self.templates_frame.hide()
        self.agent_run_detail_frame.hide()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

