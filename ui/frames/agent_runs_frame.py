"""
Agent runs frame for the Codegen UI.

This module provides a frame for displaying agent runs.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable

from ui.components.agent_run_card import AgentRunCard
from ui.utils.constants import PADDING, COLORS, EVENT_TYPES

logger = logging.getLogger(__name__)

class AgentRunsFrame(ttk.Frame):
    """
    Frame for displaying agent runs.
    
    This frame displays a list of agent runs with filtering and pagination.
    """
    
    def __init__(self, parent, controller):
        """
        Initialize the agent runs frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        
        self.controller = controller
        self.agent_runs = []
        self.starred_runs = []
        self.current_page = 1
        self.items_per_page = 10
        self.filter_text = ""
        self.status_filter = "ALL"
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_events()
    
    def _create_widgets(self):
        """Create widgets for the agent runs frame."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=PADDING)
        
        # Create title
        title = ttk.Label(
            header_frame,
            text="Agent Runs",
            style="Header.TLabel"
        )
        title.pack(side=tk.LEFT)
        
        # Create refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            command=self._on_refresh_click
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create create button
        create_button = ttk.Button(
            header_frame,
            text="Create New Run",
            command=self._on_create_click
        )
        create_button.pack(side=tk.RIGHT, padx=(0, PADDING))
        
        # Create filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=(0, PADDING))
        
        # Create search entry
        search_label = ttk.Label(
            filter_frame,
            text="Search:"
        )
        search_label.pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_entry = ttk.Entry(
            filter_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create status filter
        status_label = ttk.Label(
            filter_frame,
            text="Status:"
        )
        status_label.pack(side=tk.LEFT, padx=(PADDING * 2, 0))
        
        self.status_var = tk.StringVar(value="ALL")
        self.status_var.trace_add("write", self._on_status_change)
        
        status_combobox = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["ALL", "RUNNING", "COMPLETED", "ERROR", "PAUSED"],
            state="readonly",
            width=15
        )
        status_combobox.pack(side=tk.LEFT, padx=(PADDING, 0))
        
        # Create content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=(0, PADDING))
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create pagination frame
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=(0, PADDING))
        
        # Create previous button
        self.prev_button = ttk.Button(
            pagination_frame,
            text="Previous",
            command=self._on_prev_click,
            state=tk.DISABLED
        )
        self.prev_button.pack(side=tk.LEFT)
        
        # Create next button
        self.next_button = ttk.Button(
            pagination_frame,
            text="Next",
            command=self._on_next_click,
            state=tk.DISABLED
        )
        self.next_button.pack(side=tk.RIGHT)
        
        # Create page label
        self.page_label = ttk.Label(
            pagination_frame,
            text="Page 1 of 1"
        )
        self.page_label.pack(side=tk.TOP)
        
        # Create empty state label
        self.empty_label = ttk.Label(
            self.scrollable_frame,
            text="No agent runs found",
            style="Large.TLabel"
        )
    
    def _register_events(self):
        """Register event handlers."""
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_CREATED"], self._on_agent_run_created)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_UPDATED"], self._on_agent_run_updated)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_COMPLETED"], self._on_agent_run_completed)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_ERROR"], self._on_agent_run_error)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_PAUSED"], self._on_agent_run_paused)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_RESUMED"], self._on_agent_run_resumed)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_STARRED"], self._on_agent_run_starred)
        self.controller.event_bus.subscribe(EVENT_TYPES["AGENT_RUN_UNSTARRED"], self._on_agent_run_unstarred)
        self.controller.event_bus.subscribe(EVENT_TYPES["REFRESH_REQUESTED"], self._on_refresh_requested)
    
    def _on_agent_run_created(self, event):
        """
        Handle agent run created event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_updated(self, event):
        """
        Handle agent run updated event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_completed(self, event):
        """
        Handle agent run completed event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_error(self, event):
        """
        Handle agent run error event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_paused(self, event):
        """
        Handle agent run paused event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_resumed(self, event):
        """
        Handle agent run resumed event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_agent_run_starred(self, event):
        """
        Handle agent run starred event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id and agent_run_id not in self.starred_runs:
            self.starred_runs.append(agent_run_id)
            self._update_agent_run_cards()
    
    def _on_agent_run_unstarred(self, event):
        """
        Handle agent run unstarred event.
        
        Args:
            event: Event data
        """
        agent_run_id = event.get("agent_run_id")
        if agent_run_id and agent_run_id in self.starred_runs:
            self.starred_runs.remove(agent_run_id)
            self._update_agent_run_cards()
    
    def _on_refresh_requested(self, event):
        """
        Handle refresh requested event.
        
        Args:
            event: Event data
        """
        self.load_agent_runs()
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        self.load_agent_runs()
    
    def _on_create_click(self):
        """Handle create button click."""
        self.controller.show_create_agent_run_dialog()
    
    def _on_search_change(self, *args):
        """Handle search entry change."""
        self.filter_text = self.search_var.get().lower()
        self._update_agent_run_cards()
    
    def _on_status_change(self, *args):
        """Handle status filter change."""
        self.status_filter = self.status_var.get()
        self._update_agent_run_cards()
    
    def _on_prev_click(self):
        """Handle previous button click."""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_agent_run_cards()
    
    def _on_next_click(self):
        """Handle next button click."""
        total_pages = self._get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_agent_run_cards()
    
    def _get_total_pages(self):
        """
        Get total number of pages.
        
        Returns:
            Total number of pages
        """
        filtered_runs = self._get_filtered_runs()
        return max(1, (len(filtered_runs) + self.items_per_page - 1) // self.items_per_page)
    
    def _get_filtered_runs(self):
        """
        Get filtered agent runs.
        
        Returns:
            Filtered agent runs
        """
        filtered_runs = []
        
        for run in self.agent_runs:
            # Apply text filter
            if self.filter_text:
                prompt = run.get("prompt", "").lower()
                run_id = str(run.get("id", "")).lower()
                
                if self.filter_text not in prompt and self.filter_text not in run_id:
                    continue
            
            # Apply status filter
            if self.status_filter != "ALL" and run.get("status") != self.status_filter:
                continue
            
            filtered_runs.append(run)
        
        return filtered_runs
    
    def _update_agent_run_cards(self):
        """Update agent run cards."""
        # Clear scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get filtered runs
        filtered_runs = self._get_filtered_runs()
        
        # Update pagination
        total_pages = self._get_total_pages()
        self.current_page = min(self.current_page, total_pages)
        
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)
        
        # Get paginated runs
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_runs = filtered_runs[start_idx:end_idx]
        
        # Show empty state if no runs
        if not paginated_runs:
            self.empty_label.pack(pady=PADDING * 2)
            return
        
        # Create agent run cards
        for run in paginated_runs:
            is_starred = run.get("id") in self.starred_runs
            
            card = AgentRunCard(
                self.scrollable_frame,
                run,
                on_view=self._on_view_agent_run,
                on_star=self._on_star_agent_run,
                on_resume=self._on_resume_agent_run,
                on_stop=self._on_stop_agent_run,
                is_starred=is_starred
            )
            card.pack(fill=tk.X, expand=False, pady=(0, PADDING))
    
    def _on_view_agent_run(self, agent_run_id):
        """
        Handle view agent run.
        
        Args:
            agent_run_id: Agent run ID
        """
        self.controller.show_agent_run_detail(agent_run_id)
    
    def _on_star_agent_run(self, agent_run_id, is_starred):
        """
        Handle star agent run.
        
        Args:
            agent_run_id: Agent run ID
            is_starred: Whether the agent run is starred
        """
        if is_starred:
            self.controller.star_agent_run(agent_run_id)
        else:
            self.controller.unstar_agent_run(agent_run_id)
    
    def _on_resume_agent_run(self, agent_run_id):
        """
        Handle resume agent run.
        
        Args:
            agent_run_id: Agent run ID
        """
        self.controller.resume_agent_run(agent_run_id)
    
    def _on_stop_agent_run(self, agent_run_id):
        """
        Handle stop agent run.
        
        Args:
            agent_run_id: Agent run ID
        """
        self.controller.stop_agent_run(agent_run_id)
    
    def load_agent_runs(self):
        """Load agent runs."""
        try:
            # Show loading state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            loading_label = ttk.Label(
                self.scrollable_frame,
                text="Loading agent runs...",
                style="Large.TLabel"
            )
            loading_label.pack(pady=PADDING * 2)
            
            self.update_idletasks()
            
            # Get agent runs
            self.agent_runs = self.controller.get_agent_runs()
            
            # Get starred runs
            self.starred_runs = self.controller.get_starred_agent_runs()
            
            # Update agent run cards
            self._update_agent_run_cards()
            
        except Exception as e:
            logger.error(f"Error loading agent runs: {e}")
            
            # Show error state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            error_label = ttk.Label(
                self.scrollable_frame,
                text=f"Error loading agent runs: {str(e)}",
                style="Error.TLabel"
            )
            error_label.pack(pady=PADDING * 2)
    
    def show(self):
        """Show the agent runs frame."""
        self.pack(fill=tk.BOTH, expand=True)
        self.load_agent_runs()
    
    def hide(self):
        """Hide the agent runs frame."""
        self.pack_forget()

