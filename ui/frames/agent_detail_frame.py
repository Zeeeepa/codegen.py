"""
Agent detail frame for the Codegen UI.

This module provides an agent detail frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Callable

from ui.core.base_component import BaseComponent
from ui.core.events import EventType, Event
from ui.utils.constants import PADDING

logger = logging.getLogger(__name__)


class AgentDetailFrame(BaseComponent):
    """Agent detail frame for the Codegen UI."""
    
    def __init__(self, parent: Any, controller: Any):
        """
        Initialize the agent detail frame.
        
        Args:
            parent: The parent widget.
            controller: The controller.
        """
        super().__init__(parent, controller)
        
        # Initialize state
        self.run_id = None
        self.logs_seen_count = 0
        self.running = False
        self.thread = None
    
    def _init_ui(self):
        """Initialize the UI."""
        # Create header frame
        header_frame = ttk.Frame(self.frame, padding=PADDING)
        header_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create title label
        self.title_var = tk.StringVar()
        self.title_var.set("Agent Run Details")
        title_label = ttk.Label(
            header_frame, textvariable=self.title_var, style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Create back button
        back_button = ttk.Button(
            header_frame, text="Back", command=self._back
        )
        back_button.pack(side=tk.RIGHT)
        
        # Create status frame
        status_frame = ttk.Frame(self.frame, padding=PADDING)
        status_frame.pack(fill=tk.X, padx=PADDING, pady=(0, PADDING))
        
        # Create status label
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar()
        self.status_var.set("N/A")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create follow checkbox
        self.follow_var = tk.BooleanVar(value=True)
        follow_check = ttk.Checkbutton(
            status_frame, text="Follow", variable=self.follow_var
        )
        follow_check.pack(side=tk.RIGHT)
        
        # Create logs frame
        logs_frame = ttk.LabelFrame(self.frame, text="Logs", padding=PADDING)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create logs text area
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, wrap=tk.WORD, height=20, state=tk.DISABLED
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create result frame
        result_frame = ttk.LabelFrame(self.frame, text="Result", padding=PADDING)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create result text area
        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, height=10, state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
    
    def _register_event_handlers(self):
        """Register event handlers."""
        pass
    
    def load_agent_run(self, run_id: int):
        """
        Load agent run.
        
        Args:
            run_id: The agent run ID.
        """
        # Update state
        self.run_id = run_id
        self.logs_seen_count = 0
        
        # Update title
        self.title_var.set(f"Agent Run #{run_id}")
        
        # Clear logs
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
        
        # Clear result
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Start logs thread
        self.running = True
        self.thread = threading.Thread(
            target=self._fetch_logs_thread, daemon=True
        )
        self.thread.start()
    
    def _fetch_logs_thread(self):
        """Fetch logs in a separate thread."""
        try:
            follow = self.follow_var.get()
            
            while self.running:
                run_with_logs = self.controller.get_agent_run_logs(
                    self.run_id, skip=self.logs_seen_count, limit=100
                )
                
                if run_with_logs:
                    # Update status
                    self.status_var.set(run_with_logs.status or "N/A")
                    
                    # Update result
                    if run_with_logs.result:
                        self.result_text.config(state=tk.NORMAL)
                        self.result_text.delete(1.0, tk.END)
                        self.result_text.insert(tk.END, run_with_logs.result)
                        self.result_text.config(state=tk.DISABLED)
                    
                    # Update logs
                    new_logs = run_with_logs.logs
                    if new_logs:
                        self.logs_text.config(state=tk.NORMAL)
                        
                        for log in new_logs:
                            self.logs_text.insert(
                                tk.END,
                                f"{log.created_at} - {log.message_type}\n",
                            )
                            
                            if log.thought:
                                self.logs_text.insert(tk.END, f"Thought: {log.thought}\n")
                            
                            if log.tool_name:
                                self.logs_text.insert(
                                    tk.END,
                                    f"Tool: {log.tool_name}\n"
                                    f"Input: {log.tool_input}\n"
                                    f"Output: {log.tool_output}\n",
                                )
                            
                            if log.observation:
                                self.logs_text.insert(
                                    tk.END, f"Observation: {log.observation}\n"
                                )
                            
                            self.logs_text.insert(tk.END, "\n")
                        
                        self.logs_text.see(tk.END)
                        self.logs_text.config(state=tk.DISABLED)
                        
                        self.logs_seen_count += len(new_logs)
                    
                    # Check if we should stop following
                    status = run_with_logs.status
                    if not follow or status not in ["running", "pending", "active"]:
                        break
                
                time.sleep(2)
        
        except Exception as e:
            logger.exception(f"Failed to fetch logs: {e}")
            
            # Publish error event
            self.event_bus.publish(
                Event(
                    EventType.UI_ERROR,
                    {"error": f"Failed to fetch logs: {str(e)}"}
                )
            )
        
        finally:
            self.running = False
    
    def _back(self):
        """Go back to the previous screen."""
        # Stop logs thread
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        
        # Get parent main window
        main_window = self.parent.master
        main_window.hide_agent_detail()

