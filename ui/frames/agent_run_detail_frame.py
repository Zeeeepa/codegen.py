"""
Agent run detail frame for the Codegen UI.

This module provides a frame for displaying agent run details.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import threading
import time

from ui.utils.constants import PADDING, COLORS, EVENT_TYPES

logger = logging.getLogger(__name__)

class AgentRunDetailFrame(ttk.Frame):
    """
    Frame for displaying agent run details.
    
    This frame displays details for a specific agent run, including
    logs, tools used, and timeline.
    """
    
    def __init__(self, parent, controller):
        """
        Initialize the agent run detail frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        
        self.controller = controller
        self.agent_run = None
        self.agent_run_id = None
        self.logs = []
        self.tools_used = []
        self.timeline = []
        self.is_starred = False
        self.is_polling = False
        self.polling_interval = 5  # seconds
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_events()
    
    def _create_widgets(self):
        """Create widgets for the agent run detail frame."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=PADDING)
        
        # Create back button
        back_button = ttk.Button(
            header_frame,
            text="← Back",
            command=self._on_back_click
        )
        back_button.pack(side=tk.LEFT)
        
        # Create title
        self.title_label = ttk.Label(
            header_frame,
            text="Agent Run Details",
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            command=self._on_refresh_click
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create star button
        self.star_button = ttk.Button(
            header_frame,
            text="☆",
            style="Unstar.TButton",
            width=3,
            command=self._on_star_click
        )
        self.star_button.pack(side=tk.RIGHT, padx=(0, PADDING))
        
        # Create info frame
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=(0, PADDING))
        
        # Create status label
        status_label = ttk.Label(
            info_frame,
            text="Status:"
        )
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.status_value = ttk.Label(
            info_frame,
            text="Unknown",
            style="Status.TLabel"
        )
        self.status_value.grid(row=0, column=1, sticky=tk.W, padx=(PADDING, 0))
        
        # Create created at label
        created_label = ttk.Label(
            info_frame,
            text="Created:"
        )
        created_label.grid(row=1, column=0, sticky=tk.W)
        
        self.created_value = ttk.Label(
            info_frame,
            text="Unknown"
        )
        self.created_value.grid(row=1, column=1, sticky=tk.W, padx=(PADDING, 0))
        
        # Create updated at label
        updated_label = ttk.Label(
            info_frame,
            text="Updated:"
        )
        updated_label.grid(row=2, column=0, sticky=tk.W)
        
        self.updated_value = ttk.Label(
            info_frame,
            text="Unknown"
        )
        self.updated_value.grid(row=2, column=1, sticky=tk.W, padx=(PADDING, 0))
        
        # Create prompt label
        prompt_label = ttk.Label(
            info_frame,
            text="Prompt:"
        )
        prompt_label.grid(row=3, column=0, sticky=tk.W)
        
        self.prompt_value = ttk.Label(
            info_frame,
            text="No prompt",
            wraplength=600
        )
        self.prompt_value.grid(row=3, column=1, sticky=tk.W, padx=(PADDING, 0))
        
        # Create action buttons frame
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=(0, PADDING))
        
        # Create resume button
        self.resume_button = ttk.Button(
            action_frame,
            text="Resume",
            command=self._on_resume_click,
            state=tk.DISABLED
        )
        self.resume_button.pack(side=tk.LEFT)
        
        # Create stop button
        self.stop_button = ttk.Button(
            action_frame,
            text="Stop",
            command=self._on_stop_click,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create ban checks button
        self.ban_checks_button = ttk.Button(
            action_frame,
            text="Ban Checks",
            command=self._on_ban_checks_click,
            state=tk.DISABLED
        )
        self.ban_checks_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create unban checks button
        self.unban_checks_button = ttk.Button(
            action_frame,
            text="Unban Checks",
            command=self._on_unban_checks_click,
            state=tk.DISABLED
        )
        self.unban_checks_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create remove from PR button
        self.remove_pr_button = ttk.Button(
            action_frame,
            text="Remove from PR",
            command=self._on_remove_pr_click,
            state=tk.DISABLED
        )
        self.remove_pr_button.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=(0, PADDING))
        
        # Create logs frame
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Create logs text
        self.logs_text = tk.Text(
            self.logs_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        logs_scrollbar = ttk.Scrollbar(
            self.logs_frame,
            orient=tk.VERTICAL,
            command=self.logs_text.yview
        )
        self.logs_text.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create tools frame
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="Tools Used")
        
        # Create tools text
        self.tools_text = tk.Text(
            self.tools_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        tools_scrollbar = ttk.Scrollbar(
            self.tools_frame,
            orient=tk.VERTICAL,
            command=self.tools_text.yview
        )
        self.tools_text.configure(yscrollcommand=tools_scrollbar.set)
        
        self.tools_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tools_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create timeline frame
        self.timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.timeline_frame, text="Timeline")
        
        # Create timeline text
        self.timeline_text = tk.Text(
            self.timeline_frame,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        timeline_scrollbar = ttk.Scrollbar(
            self.timeline_frame,
            orient=tk.VERTICAL,
            command=self.timeline_text.yview
        )
        self.timeline_text.configure(yscrollcommand=timeline_scrollbar.set)
        
        self.timeline_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        timeline_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _register_events(self):
        """Register event handlers."""
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_UPDATED"], self._on_agent_run_updated)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_COMPLETED"], self._on_agent_run_completed)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_ERROR"], self._on_agent_run_error)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_PAUSED"], self._on_agent_run_paused)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_RESUMED"], self._on_agent_run_resumed)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_STARRED"], self._on_agent_run_starred)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_UNSTARRED"], self._on_agent_run_unstarred)
    
    def _on_agent_run_updated(self, event):
        """
        Handle agent run updated event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.load_agent_run(agent_run_id)
    
    def _on_agent_run_completed(self, event):
        """
        Handle agent run completed event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.load_agent_run(agent_run_id)
    
    def _on_agent_run_error(self, event):
        """
        Handle agent run error event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.load_agent_run(agent_run_id)
    
    def _on_agent_run_paused(self, event):
        """
        Handle agent run paused event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.load_agent_run(agent_run_id)
    
    def _on_agent_run_resumed(self, event):
        """
        Handle agent run resumed event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.load_agent_run(agent_run_id)
    
    def _on_agent_run_starred(self, event):
        """
        Handle agent run starred event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.is_starred = True
            self._update_star_button()
    
    def _on_agent_run_unstarred(self, event):
        """
        Handle agent run unstarred event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id == self.agent_run_id:
            self.is_starred = False
            self._update_star_button()
    
    def _on_back_click(self):
        """Handle back button click."""
        self.controller.show_agent_runs()
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        if self.agent_run_id:
            self.load_agent_run(self.agent_run_id)
    
    def _on_star_click(self):
        """Handle star button click."""
        if not self.agent_run_id:
            return
        
        if self.is_starred:
            self.controller.unstar_agent_run(self.agent_run_id)
        else:
            self.controller.star_agent_run(self.agent_run_id)
    
    def _on_resume_click(self):
        """Handle resume button click."""
        if self.agent_run_id:
            self.controller.resume_agent_run(self.agent_run_id)
    
    def _on_stop_click(self):
        """Handle stop button click."""
        if self.agent_run_id:
            self.controller.stop_agent_run(self.agent_run_id)
    
    def _on_ban_checks_click(self):
        """Handle ban checks button click."""
        if self.agent_run_id:
            self.controller.ban_all_checks_for_agent_run(self.agent_run_id)
    
    def _on_unban_checks_click(self):
        """Handle unban checks button click."""
        if self.agent_run_id:
            self.controller.unban_all_checks_for_agent_run(self.agent_run_id)
    
    def _on_remove_pr_click(self):
        """Handle remove from PR button click."""
        if self.agent_run_id:
            self.controller.remove_codegen_from_pr(self.agent_run_id)
    
    def _update_star_button(self):
        """Update star button."""
        star_text = "★" if self.is_starred else "☆"
        star_style = "Star.TButton" if self.is_starred else "Unstar.TButton"
        self.star_button.configure(text=star_text, style=star_style)
    
    def _update_action_buttons(self):
        """Update action buttons."""
        if not self.agent_run:
            self.resume_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.DISABLED)
            self.ban_checks_button.configure(state=tk.DISABLED)
            self.unban_checks_button.configure(state=tk.DISABLED)
            self.remove_pr_button.configure(state=tk.DISABLED)
            return
        
        status = self.agent_run.get("status", "UNKNOWN")
        
        # Resume button
        if status == "PAUSED":
            self.resume_button.configure(state=tk.NORMAL)
        else:
            self.resume_button.configure(state=tk.DISABLED)
        
        # Stop button
        if status == "RUNNING":
            self.stop_button.configure(state=tk.NORMAL)
        else:
            self.stop_button.configure(state=tk.DISABLED)
        
        # Ban checks button
        if status in ["RUNNING", "PAUSED"]:
            self.ban_checks_button.configure(state=tk.NORMAL)
        else:
            self.ban_checks_button.configure(state=tk.DISABLED)
        
        # Unban checks button
        if status in ["RUNNING", "PAUSED"]:
            self.unban_checks_button.configure(state=tk.NORMAL)
        else:
            self.unban_checks_button.configure(state=tk.DISABLED)
        
        # Remove from PR button
        if status in ["COMPLETED", "ERROR"]:
            self.remove_pr_button.configure(state=tk.NORMAL)
        else:
            self.remove_pr_button.configure(state=tk.DISABLED)
    
    def _start_polling(self):
        """Start polling for agent run updates."""
        if self.is_polling or not self.agent_run_id:
            return
        
        self.is_polling = True
        
        def _poll_thread():
            while self.is_polling and self.agent_run_id:
                try:
                    # Get agent run
                    agent_run = self.controller.get_agent_run(self.agent_run_id)
                    
                    # Update agent run
                    if agent_run != self.agent_run:
                        self.agent_run = agent_run
                        
                        # Update UI
                        self.after(0, self._update_ui)
                    
                    # Get logs
                    logs = self.controller.get_agent_run_logs(self.agent_run_id)
                    
                    # Update logs
                    if logs != self.logs:
                        self.logs = logs
                        
                        # Update logs text
                        self.after(0, self._update_logs_text)
                    
                    # Check if polling should stop
                    status = agent_run.get("status", "UNKNOWN")
                    if status in ["COMPLETED", "ERROR"]:
                        self.is_polling = False
                        break
                    
                    # Sleep
                    time.sleep(self.polling_interval)
                    
                except Exception as e:
                    logger.error(f"Error polling agent run: {e}")
                    self.is_polling = False
                    break
        
        # Start polling thread
        threading.Thread(target=_poll_thread, daemon=True).start()
    
    def _stop_polling(self):
        """Stop polling for agent run updates."""
        self.is_polling = False
    
    def _update_ui(self):
        """Update UI with agent run data."""
        if not self.agent_run:
            return
        
        # Update title
        self.title_label.configure(text=f"Agent Run #{self.agent_run.get('id', 'Unknown')}")
        
        # Update status
        status = self.agent_run.get("status", "UNKNOWN")
        status_color = COLORS.get(status, COLORS["UNKNOWN"])
        self.status_value.configure(text=status, foreground=status_color)
        
        # Update created at
        created_at = self.agent_run.get("created_at", "Unknown")
        self.created_value.configure(text=created_at)
        
        # Update updated at
        updated_at = self.agent_run.get("updated_at", "Unknown")
        self.updated_value.configure(text=updated_at)
        
        # Update prompt
        prompt = self.agent_run.get("prompt", "No prompt")
        self.prompt_value.configure(text=prompt)
        
        # Update action buttons
        self._update_action_buttons()
        
        # Update tools used
        self._update_tools_text()
        
        # Update timeline
        self._update_timeline_text()
    
    def _update_logs_text(self):
        """Update logs text."""
        # Clear logs text
        self.logs_text.configure(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        
        # Add logs
        for log in self.logs:
            timestamp = log.get("timestamp", "")
            message = log.get("message", "")
            level = log.get("level", "INFO")
            
            # Add timestamp
            self.logs_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Add level
            level_tag = f"level_{level.lower()}"
            self.logs_text.insert(tk.END, f"[{level}] ", level_tag)
            
            # Add message
            self.logs_text.insert(tk.END, f"{message}\n", "message")
        
        # Configure tags
        self.logs_text.tag_configure("timestamp", foreground=COLORS["INFO"])
        self.logs_text.tag_configure("level_info", foreground=COLORS["INFO"])
        self.logs_text.tag_configure("level_warning", foreground=COLORS["WARNING"])
        self.logs_text.tag_configure("level_error", foreground=COLORS["ERROR"])
        self.logs_text.tag_configure("message")
        
        # Disable logs text
        self.logs_text.configure(state=tk.DISABLED)
        
        # Scroll to end
        self.logs_text.see(tk.END)
    
    def _update_tools_text(self):
        """Update tools used text."""
        # Clear tools text
        self.tools_text.configure(state=tk.NORMAL)
        self.tools_text.delete(1.0, tk.END)
        
        # Add tools used
        if not self.tools_used:
            self.tools_text.insert(tk.END, "No tools used")
        else:
            for tool in self.tools_used:
                name = tool.get("name", "Unknown")
                timestamp = tool.get("timestamp", "")
                parameters = tool.get("parameters", {})
                result = tool.get("result", "")
                
                # Add tool name
                self.tools_text.insert(tk.END, f"Tool: {name}\n", "tool_name")
                
                # Add timestamp
                self.tools_text.insert(tk.END, f"Timestamp: {timestamp}\n", "timestamp")
                
                # Add parameters
                self.tools_text.insert(tk.END, "Parameters:\n", "parameters_header")
                for key, value in parameters.items():
                    self.tools_text.insert(tk.END, f"  {key}: {value}\n", "parameter")
                
                # Add result
                self.tools_text.insert(tk.END, "Result:\n", "result_header")
                self.tools_text.insert(tk.END, f"{result}\n\n", "result")
        
        # Configure tags
        self.tools_text.tag_configure("tool_name", font=("Helvetica", 12, "bold"))
        self.tools_text.tag_configure("timestamp", foreground=COLORS["INFO"])
        self.tools_text.tag_configure("parameters_header", font=("Helvetica", 10, "bold"))
        self.tools_text.tag_configure("parameter")
        self.tools_text.tag_configure("result_header", font=("Helvetica", 10, "bold"))
        self.tools_text.tag_configure("result")
        
        # Disable tools text
        self.tools_text.configure(state=tk.DISABLED)
    
    def _update_timeline_text(self):
        """Update timeline text."""
        # Clear timeline text
        self.timeline_text.configure(state=tk.NORMAL)
        self.timeline_text.delete(1.0, tk.END)
        
        # Add timeline
        if not self.timeline:
            self.timeline_text.insert(tk.END, "No timeline events")
        else:
            for event in self.timeline:
                timestamp = event.get("timestamp", "")
                event_type = event.get("type", "Unknown")
                description = event.get("description", "")
                
                # Add timestamp
                self.timeline_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
                
                # Add event type
                self.timeline_text.insert(tk.END, f"{event_type}: ", "event_type")
                
                # Add description
                self.timeline_text.insert(tk.END, f"{description}\n", "description")
        
        # Configure tags
        self.timeline_text.tag_configure("timestamp", foreground=COLORS["INFO"])
        self.timeline_text.tag_configure("event_type", font=("Helvetica", 10, "bold"))
        self.timeline_text.tag_configure("description")
        
        # Disable timeline text
        self.timeline_text.configure(state=tk.DISABLED)
    
    def load_agent_run(self, agent_run_id):
        """
        Load agent run.
        
        Args:
            agent_run_id: Agent run ID
        """
        try:
            # Stop polling
            self._stop_polling()
            
            # Set agent run ID
            self.agent_run_id = agent_run_id
            
            # Get agent run
            self.agent_run = self.controller.get_agent_run(agent_run_id)
            
            # Get logs
            self.logs = self.controller.get_agent_run_logs(agent_run_id)
            
            # Get tools used
            self.tools_used = self.controller.get_agent_run_tools_used(agent_run_id)
            
            # Get timeline
            self.timeline = self.controller.get_agent_run_timeline(agent_run_id)
            
            # Check if starred
            self.is_starred = agent_run_id in self.controller.get_starred_agent_runs()
            
            # Update UI
            self._update_ui()
            self._update_logs_text()
            self._update_star_button()
            
            # Start polling if agent run is not completed
            status = self.agent_run.get("status", "UNKNOWN")
            if status not in ["COMPLETED", "ERROR"]:
                self._start_polling()
            
        except Exception as e:
            logger.error(f"Error loading agent run: {e}")
            
            # Show error
            tk.messagebox.showerror("Error", f"Error loading agent run: {str(e)}")
    
    def show(self):
        """Show the agent run detail frame."""
        self.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the agent run detail frame."""
        self._stop_polling()
        self.pack_forget()

