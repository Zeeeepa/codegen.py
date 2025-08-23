"""
Main window for the Enhanced Codegen UI.

This module provides the main window for the Enhanced Codegen UI,
containing the main menu, status bar, and content area.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import Event, EventType
from enhanced_codegen_ui.ui.frames.login_frame import LoginFrame
from enhanced_codegen_ui.ui.frames.agent_list_frame import AgentListFrame
from enhanced_codegen_ui.ui.frames.agent_detail_frame import AgentDetailFrame
from enhanced_codegen_ui.ui.frames.project_frame import ProjectFrame
from enhanced_codegen_ui.ui.frames.create_agent_frame import CreateAgentFrame
from enhanced_codegen_ui.utils.constants import PADDING


class MainWindow:
    """
    Main window for the Enhanced Codegen UI.
    
    This class provides the main window for the Enhanced Codegen UI,
    containing the main menu, status bar, and content area.
    """
    
    def __init__(self, root: tk.Tk, controller: Controller):
        """
        Initialize the main window.
        
        Args:
            root: Root Tk instance
            controller: Application controller
        """
        self.root = root
        self.controller = controller
        self.logger = logging.getLogger(__name__)
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu
        self._create_menu()
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create status bar
        self._create_status_bar()
        
        # Create frames
        self.frames = {}
        self._create_frames()
        
        # Register event handlers
        self._register_event_handlers()
        
        # Show initial frame
        self._show_frame("login")
        
    def _create_menu(self):
        """Create the main menu."""
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        
        # Create file menu
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="New Agent Run", command=self._on_new_agent_run, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self._on_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self._on_logout, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        self.menu.add_cascade(label="File", menu=file_menu)
        
        # Create view menu
        view_menu = tk.Menu(self.menu, tearoff=0)
        view_menu.add_command(label="Agent Runs", command=lambda: self._show_frame("agent_list"), accelerator="Ctrl+1")
        view_menu.add_command(label="Projects", command=lambda: self._show_frame("project"), accelerator="Ctrl+2")
        view_menu.add_command(label="Create Agent Run", command=lambda: self._show_frame("create_agent"), accelerator="Ctrl+3")
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self._on_refresh, accelerator="F5")
        self.menu.add_cascade(label="View", menu=view_menu)
        
        # Create help menu
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="Help", command=self._on_help, accelerator="F1")
        help_menu.add_command(label="About", command=self._on_about)
        self.menu.add_cascade(label="Help", menu=help_menu)
        
        # Disable menus initially
        file_menu.entryconfig("New Agent Run", state=tk.DISABLED)
        file_menu.entryconfig("Settings", state=tk.DISABLED)
        file_menu.entryconfig("Logout", state=tk.DISABLED)
        view_menu.entryconfig("Agent Runs", state=tk.DISABLED)
        view_menu.entryconfig("Projects", state=tk.DISABLED)
        view_menu.entryconfig("Create Agent Run", state=tk.DISABLED)
        view_menu.entryconfig("Refresh", state=tk.DISABLED)
        
        # Store menu references
        self.file_menu = file_menu
        self.view_menu = view_menu
        
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.main_frame, relief=tk.SUNKEN, padding=(PADDING, PADDING/2))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Create status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.status_bar, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Create organization label
        self.org_var = tk.StringVar(value="")
        org_label = ttk.Label(self.status_bar, textvariable=self.org_var)
        org_label.pack(side=tk.RIGHT)
        
    def _create_frames(self):
        """Create the content frames."""
        # Create login frame
        self.frames["login"] = LoginFrame(self.content_frame, self.controller)
        
        # Create agent list frame
        self.frames["agent_list"] = AgentListFrame(self.content_frame, self.controller)
        
        # Create agent detail frame
        self.frames["agent_detail"] = AgentDetailFrame(self.content_frame, self.controller)
        
        # Create project frame
        self.frames["project"] = ProjectFrame(self.content_frame, self.controller)
        
        # Create create agent frame
        self.frames["create_agent"] = CreateAgentFrame(self.content_frame, self.controller)
        
    def _register_event_handlers(self):
        """Register event handlers."""
        # Register login events
        self.controller.event_bus.subscribe(
            EventType.LOGIN_SUCCEEDED,
            self._on_login_succeeded
        )
        
        # Register logout events
        self.controller.event_bus.subscribe(
            EventType.LOGOUT_SUCCEEDED,
            self._on_logout_succeeded
        )
        
        # Register view events
        self.controller.event_bus.subscribe(
            EventType.VIEW_AGENT_RUN_REQUESTED,
            self._on_view_agent_run_requested
        )
        
        self.controller.event_bus.subscribe(
            EventType.VIEW_AGENT_RUNS_REQUESTED,
            lambda e: self._show_frame("agent_list")
        )
        
        self.controller.event_bus.subscribe(
            EventType.VIEW_REPOSITORIES_REQUESTED,
            lambda e: self._show_frame("project")
        )
        
        self.controller.event_bus.subscribe(
            EventType.VIEW_CREATE_AGENT_REQUESTED,
            lambda e: self._show_frame("create_agent")
        )
        
        # Register organization events
        self.controller.event_bus.subscribe(
            EventType.ORGANIZATION_CHANGED,
            self._on_organization_changed
        )
        
    def _show_frame(self, frame_name: str):
        """
        Show a specific frame.
        
        Args:
            frame_name: Name of the frame to show
        """
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
            
        # Show requested frame
        if frame_name in self.frames:
            self.frames[frame_name].pack(fill=tk.BOTH, expand=True)
            self.controller.state.current_view = frame_name
            self.logger.info(f"Showing frame: {frame_name}")
            
    def _on_login_succeeded(self, event: Event):
        """
        Handle login succeeded event.
        
        Args:
            event: Event object
        """
        # Enable menus
        self.file_menu.entryconfig("New Agent Run", state=tk.NORMAL)
        self.file_menu.entryconfig("Settings", state=tk.NORMAL)
        self.file_menu.entryconfig("Logout", state=tk.NORMAL)
        self.view_menu.entryconfig("Agent Runs", state=tk.NORMAL)
        self.view_menu.entryconfig("Projects", state=tk.NORMAL)
        self.view_menu.entryconfig("Create Agent Run", state=tk.NORMAL)
        self.view_menu.entryconfig("Refresh", state=tk.NORMAL)
        
        # Update organization label
        org_id = event.data.get("org_id")
        if org_id:
            self.org_var.set(f"Organization: {org_id}")
            
        # Show agent list frame
        self._show_frame("agent_list")
        
        # Set status
        self.status_var.set("Logged in successfully")
        
    def _on_logout_succeeded(self, event: Event):
        """
        Handle logout succeeded event.
        
        Args:
            event: Event object
        """
        # Disable menus
        self.file_menu.entryconfig("New Agent Run", state=tk.DISABLED)
        self.file_menu.entryconfig("Settings", state=tk.DISABLED)
        self.file_menu.entryconfig("Logout", state=tk.DISABLED)
        self.view_menu.entryconfig("Agent Runs", state=tk.DISABLED)
        self.view_menu.entryconfig("Projects", state=tk.DISABLED)
        self.view_menu.entryconfig("Create Agent Run", state=tk.DISABLED)
        self.view_menu.entryconfig("Refresh", state=tk.DISABLED)
        
        # Clear organization label
        self.org_var.set("")
        
        # Show login frame
        self._show_frame("login")
        
        # Set status
        self.status_var.set("Logged out")
        
    def _on_view_agent_run_requested(self, event: Event):
        """
        Handle view agent run requested event.
        
        Args:
            event: Event object with agent_run_id in data
        """
        agent_run_id = event.data.get("agent_run_id")
        if agent_run_id:
            # Set agent run ID in agent detail frame
            self.frames["agent_detail"].set_agent_run_id(agent_run_id)
            
            # Show agent detail frame
            self._show_frame("agent_detail")
            
    def _on_organization_changed(self, event: Event):
        """
        Handle organization changed event.
        
        Args:
            event: Event object with org_id in data
        """
        org_id = event.data.get("org_id")
        if org_id:
            self.org_var.set(f"Organization: {org_id}")
            
    def _on_new_agent_run(self):
        """Handle new agent run menu item."""
        self._show_frame("create_agent")
        
    def _on_settings(self):
        """Handle settings menu item."""
        # Create settings dialog
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("400x300")
        settings_dialog.transient(self.root)
        settings_dialog.grab_set()
        
        # Create settings content
        settings_frame = ttk.Frame(settings_dialog, padding=PADDING)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create settings tabs
        settings_notebook = ttk.Notebook(settings_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create general settings tab
        general_frame = ttk.Frame(settings_notebook, padding=PADDING)
        settings_notebook.add(general_frame, text="General")
        
        # Create API settings tab
        api_frame = ttk.Frame(settings_notebook, padding=PADDING)
        settings_notebook.add(api_frame, text="API")
        
        # Create UI settings tab
        ui_frame = ttk.Frame(settings_notebook, padding=PADDING)
        settings_notebook.add(ui_frame, text="UI")
        
        # Create buttons
        button_frame = ttk.Frame(settings_dialog)
        button_frame.pack(fill=tk.X, pady=PADDING)
        
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=settings_dialog.destroy
        )
        save_button.pack(side=tk.RIGHT, padx=(0, PADDING))
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=settings_dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, PADDING))
        
    def _on_logout(self):
        """Handle logout menu item."""
        self.controller.event_bus.publish(Event(EventType.LOGOUT_REQUESTED, {}))
        
    def _on_refresh(self):
        """Handle refresh menu item."""
        current_view = self.controller.state.current_view
        
        if current_view == "agent_list":
            self.controller.event_bus.publish(
                Event(EventType.REFRESH_REQUESTED, {"type": "agent_runs"})
            )
        elif current_view == "project":
            self.controller.event_bus.publish(
                Event(EventType.REFRESH_REQUESTED, {"type": "repositories"})
            )
        elif current_view == "agent_detail":
            self.frames["agent_detail"].refresh()
        elif current_view == "create_agent":
            self.controller.event_bus.publish(
                Event(EventType.REFRESH_REQUESTED, {"type": "models"})
            )
            
    def _on_help(self):
        """Handle help menu item."""
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
        help_text.insert(tk.END, "Codegen UI Help\n\n")
        help_text.insert(tk.END, "Keyboard Shortcuts:\n")
        help_text.insert(tk.END, "  Ctrl+Q: Quit application\n")
        help_text.insert(tk.END, "  F1: Show this help dialog\n")
        help_text.insert(tk.END, "  F5: Refresh current view\n")
        help_text.insert(tk.END, "  Ctrl+N: Create new agent run\n")
        help_text.insert(tk.END, "  Ctrl+1: View agent runs\n")
        help_text.insert(tk.END, "  Ctrl+2: View repositories\n")
        help_text.insert(tk.END, "  Ctrl+3: Create agent run\n")
        help_text.insert(tk.END, "\n")
        help_text.insert(tk.END, "For more information, visit https://docs.codegen.com\n")
        
        # Make text read-only
        help_text.config(state=tk.DISABLED)
        
        # Create close button
        close_button = ttk.Button(
            help_dialog,
            text="Close",
            command=help_dialog.destroy
        )
        close_button.pack(pady=10)
        
    def _on_about(self):
        """Handle about menu item."""
        # Create about dialog
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Codegen UI")
        about_dialog.geometry("400x300")
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Create about content
        about_frame = ttk.Frame(about_dialog, padding=PADDING)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create about text
        about_text = tk.Text(about_frame, wrap=tk.WORD, padx=10, pady=10)
        about_text.pack(fill=tk.BOTH, expand=True)
        
        # Add about content
        about_text.insert(tk.END, "Codegen UI\n\n")
        about_text.insert(tk.END, "Version: 0.2.0\n\n")
        about_text.insert(tk.END, "A comprehensive Tkinter-based GUI for the Codegen API.\n\n")
        about_text.insert(tk.END, "© 2023 Codegen\n")
        about_text.insert(tk.END, "https://codegen.com\n")
        
        # Make text read-only
        about_text.config(state=tk.DISABLED)
        
        # Create close button
        close_button = ttk.Button(
            about_dialog,
            text="Close",
            command=about_dialog.destroy
        )
        close_button.pack(pady=10)
        
    def set_status(self, status: str):
        """
        Set the status bar text.
        
        Args:
            status: Status text
        """
        self.status_var.set(status)

