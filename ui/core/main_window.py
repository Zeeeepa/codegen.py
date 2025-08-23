"""
Main window for the Codegen UI.

This module provides the main window for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.frames.login_frame import LoginFrame
from ui.frames.agent_list_frame import AgentListFrame
from ui.frames.project_frame import ProjectFrame
from ui.frames.agent_detail_frame import AgentDetailFrame
from ui.frames.create_agent_frame import CreateAgentFrame
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class MainWindow(BaseComponent):
    """Main window for the Codegen UI."""
    
    def __init__(self, parent: tk.Tk, controller: Any):
        """
        Initialize the main window.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
        
        # Pack the frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        self.event_bus.subscribe(EventType.LOGIN_SUCCESS, self._handle_login_success)
        self.event_bus.subscribe(EventType.LOGOUT, self._handle_logout)
        self.event_bus.subscribe(EventType.UI_ERROR, self._handle_ui_error)
        self.event_bus.subscribe(EventType.UI_SUCCESS, self._handle_ui_success)
        self.event_bus.subscribe(EventType.UI_WARNING, self._handle_ui_warning)
        self.event_bus.subscribe(EventType.UI_INFO, self._handle_ui_info)
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create the notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.frame)
        
        # Create frames for each tab
        self.login_frame = LoginFrame(self.notebook, self.controller)
        self.agent_list_frame = AgentListFrame(self.notebook, self.controller)
        self.project_frame = ProjectFrame(self.notebook, self.controller)
        self.create_agent_frame = CreateAgentFrame(self.notebook, self.controller)
        
        # Add frames to notebook
        self.notebook.add(self.login_frame.frame, text="Login")
        self.notebook.add(self.agent_list_frame.frame, text="Agent Runs")
        self.notebook.add(self.project_frame.frame, text="Projects")
        self.notebook.add(self.create_agent_frame.frame, text="Create Agent")
        
        # Disable tabs until logged in
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        
        # Pack the notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(PADDING, 0))
        
        # Create agent detail frame (not in notebook)
        self.agent_detail_frame = AgentDetailFrame(self.frame, self.controller)
        
        # Create menu
        self._create_menu()
    
    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.parent)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Login", command=self._show_login)
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Agent Runs", command=lambda: self._show_tab(1))
        view_menu.add_command(label="Projects", command=lambda: self._show_tab(2))
        view_menu.add_command(label="Create Agent", command=lambda: self._show_tab(3))
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self._refresh_current_tab)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._open_documentation)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.parent.config(menu=menubar)
    
    def _show_login(self):
        """Show the login tab."""
        self.notebook.select(0)
    
    def _logout(self):
        """Log out from the Codegen API."""
        self.event_bus.publish(Event(EventType.LOGOUT))
    
    def _show_tab(self, tab_index: int):
        """
        Show a specific tab.
        
        Args:
            tab_index: Index of the tab to show
        """
        if self.notebook.tab(tab_index, "state") != "disabled":
            self.notebook.select(tab_index)
    
    def _refresh_current_tab(self):
        """Refresh the current tab."""
        current_tab = self.notebook.index("current")
        
        if current_tab == 1:  # Agent Runs
            self.agent_list_frame.load_agent_runs()
        elif current_tab == 2:  # Projects
            self.project_frame.load_projects()
    
    def _show_about(self):
        """Show the about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Codegen UI",
            "Codegen UI v0.1.0\n\nA Tkinter-based GUI for the Codegen API."
        )
    
    def _open_documentation(self):
        """Open the documentation in a web browser."""
        import webbrowser
        webbrowser.open("https://docs.codegen.com/api-reference")
    
    def _handle_login_success(self, event: Event):
        """
        Handle login success event.
        
        Args:
            event: The login success event.
        """
        # Enable tabs
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.notebook.tab(3, state="normal")
        
        # Show Agent Runs tab
        self.notebook.select(1)
        
        # Update status
        self.status_var.set("Logged in successfully")
        
        # Load data
        self.agent_list_frame.load_agent_runs()
        self.project_frame.load_projects()
    
    def _handle_logout(self, event: Event):
        """
        Handle logout event.
        
        Args:
            event: The logout event.
        """
        # Disable tabs
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        
        # Show login tab
        self.notebook.select(0)
        
        # Update status
        self.status_var.set("Logged out")
        
        # Clear data
        self.agent_list_frame.clear()
        self.project_frame.clear()
        self.create_agent_frame.clear()
    
    def _handle_ui_error(self, event: Event):
        """
        Handle UI error event.
        
        Args:
            event: The UI error event.
        """
        error = event.data.get("error", "An error occurred")
        self.status_var.set(f"Error: {error}")
        
        # Show error dialog
        from tkinter import messagebox
        messagebox.showerror("Error", error)
    
    def _handle_ui_success(self, event: Event):
        """
        Handle UI success event.
        
        Args:
            event: The UI success event.
        """
        message = event.data.get("message", "Operation completed successfully")
        self.status_var.set(message)
    
    def _handle_ui_warning(self, event: Event):
        """
        Handle UI warning event.
        
        Args:
            event: The UI warning event.
        """
        warning = event.data.get("warning", "Warning")
        self.status_var.set(f"Warning: {warning}")
        
        # Show warning dialog
        from tkinter import messagebox
        messagebox.showwarning("Warning", warning)
    
    def _handle_ui_info(self, event: Event):
        """
        Handle UI info event.
        
        Args:
            event: The UI info event.
        """
        info = event.data.get("info", "Information")
        self.status_var.set(info)
        
        # Show info dialog
        from tkinter import messagebox
        messagebox.showinfo("Information", info)
    
    def show_agent_detail(self, agent_run_id: int):
        """
        Show the agent detail frame.
        
        Args:
            agent_run_id: ID of the agent run to display
        """
        # Hide notebook
        self.notebook.pack_forget()
        
        # Show agent detail frame
        self.agent_detail_frame.load_agent_run(agent_run_id)
        self.agent_detail_frame.pack(fill=tk.BOTH, expand=True)
    
    def hide_agent_detail(self):
        """Hide the agent detail frame and show the notebook."""
        # Hide agent detail frame
        self.agent_detail_frame.pack_forget()
        
        # Show notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)

