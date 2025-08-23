"""
Projects frame for the Codegen UI.

This module provides a frame for displaying projects.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable

from ui.components.project_card import ProjectCard
from ui.utils.constants import PADDING, COLORS, EVENT_TYPES

logger = logging.getLogger(__name__)

class ProjectsFrame(ttk.Frame):
    """
    Frame for displaying projects.
    
    This frame displays a list of projects with filtering and pagination.
    """
    
    def __init__(self, parent, controller):
        """
        Initialize the projects frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        
        self.controller = controller
        self.projects = []
        self.starred_projects = []
        self.setup_commands = {}
        self.current_page = 1
        self.items_per_page = 10
        self.filter_text = ""
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_events()
    
    def _create_widgets(self):
        """Create widgets for the projects frame."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=PADDING)
        
        # Create title
        title = ttk.Label(
            header_frame,
            text="Projects",
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
        
        # Create starred filter
        self.starred_var = tk.BooleanVar(value=False)
        self.starred_var.trace_add("write", self._on_starred_change)
        
        starred_check = ttk.Checkbutton(
            filter_frame,
            text="Starred Only",
            variable=self.starred_var
        )
        starred_check.pack(side=tk.LEFT, padx=(PADDING * 2, 0))
        
        # Create setup commands filter
        self.setup_var = tk.BooleanVar(value=False)
        self.setup_var.trace_add("write", self._on_setup_change)
        
        setup_check = ttk.Checkbutton(
            filter_frame,
            text="With Setup Commands",
            variable=self.setup_var
        )
        setup_check.pack(side=tk.LEFT, padx=(PADDING, 0))
        
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
            text="No projects found",
            style="Large.TLabel"
        )
    
    def _register_events(self):
        """Register event handlers."""
        self.controller.event_bus.subscribe(EVENT_TYPES["PROJECT_STARRED"], self._on_project_starred)
        self.controller.event_bus.subscribe(EVENT_TYPES["PROJECT_UNSTARRED"], self._on_project_unstarred)
        self.controller.event_bus.subscribe(EVENT_TYPES["REFRESH_REQUESTED"], self._on_refresh_requested)
    
    def _on_project_starred(self, event):
        """
        Handle project starred event.
        
        Args:
            event: Event data
        """
        project_id = event.get("project_id")
        if project_id and project_id not in self.starred_projects:
            self.starred_projects.append(project_id)
            self._update_project_cards()
    
    def _on_project_unstarred(self, event):
        """
        Handle project unstarred event.
        
        Args:
            event: Event data
        """
        project_id = event.get("project_id")
        if project_id and project_id in self.starred_projects:
            self.starred_projects.remove(project_id)
            self._update_project_cards()
    
    def _on_refresh_requested(self, event):
        """
        Handle refresh requested event.
        
        Args:
            event: Event data
        """
        self.load_projects()
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        self.load_projects()
    
    def _on_search_change(self, *args):
        """Handle search entry change."""
        self.filter_text = self.search_var.get().lower()
        self._update_project_cards()
    
    def _on_starred_change(self, *args):
        """Handle starred filter change."""
        self._update_project_cards()
    
    def _on_setup_change(self, *args):
        """Handle setup commands filter change."""
        self._update_project_cards()
    
    def _on_prev_click(self):
        """Handle previous button click."""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_project_cards()
    
    def _on_next_click(self):
        """Handle next button click."""
        total_pages = self._get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_project_cards()
    
    def _get_total_pages(self):
        """
        Get total number of pages.
        
        Returns:
            Total number of pages
        """
        filtered_projects = self._get_filtered_projects()
        return max(1, (len(filtered_projects) + self.items_per_page - 1) // self.items_per_page)
    
    def _get_filtered_projects(self):
        """
        Get filtered projects.
        
        Returns:
            Filtered projects
        """
        filtered_projects = []
        
        for project in self.projects:
            # Apply text filter
            if self.filter_text:
                name = project.get("name", "").lower()
                description = project.get("description", "").lower()
                
                if self.filter_text not in name and self.filter_text not in description:
                    continue
            
            # Apply starred filter
            if self.starred_var.get() and project.get("id") not in self.starred_projects:
                continue
            
            # Apply setup commands filter
            if self.setup_var.get() and project.get("id") not in self.setup_commands:
                continue
            
            filtered_projects.append(project)
        
        return filtered_projects
    
    def _update_project_cards(self):
        """Update project cards."""
        # Clear scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get filtered projects
        filtered_projects = self._get_filtered_projects()
        
        # Update pagination
        total_pages = self._get_total_pages()
        self.current_page = min(self.current_page, total_pages)
        
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)
        
        # Get paginated projects
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_projects = filtered_projects[start_idx:end_idx]
        
        # Show empty state if no projects
        if not paginated_projects:
            self.empty_label.pack(pady=PADDING * 2)
            return
        
        # Create project cards
        for project in paginated_projects:
            is_starred = project.get("id") in self.starred_projects
            has_setup_commands = project.get("id") in self.setup_commands
            
            card = ProjectCard(
                self.scrollable_frame,
                project,
                on_view=self._on_view_project,
                on_star=self._on_star_project,
                on_create_run=self._on_create_run,
                is_starred=is_starred,
                has_setup_commands=has_setup_commands
            )
            card.pack(fill=tk.X, expand=False, pady=(0, PADDING))
    
    def _on_view_project(self, project_id):
        """
        Handle view project.
        
        Args:
            project_id: Project ID
        """
        self.controller.show_project_detail(project_id)
    
    def _on_star_project(self, project_id, is_starred):
        """
        Handle star project.
        
        Args:
            project_id: Project ID
            is_starred: Whether the project is starred
        """
        if is_starred:
            self.controller.star_project(project_id)
        else:
            self.controller.unstar_project(project_id)
    
    def _on_create_run(self, project_id):
        """
        Handle create run.
        
        Args:
            project_id: Project ID
        """
        self.controller.show_create_agent_run_dialog(project_id)
    
    def load_projects(self):
        """Load projects."""
        try:
            # Show loading state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            loading_label = ttk.Label(
                self.scrollable_frame,
                text="Loading projects...",
                style="Large.TLabel"
            )
            loading_label.pack(pady=PADDING * 2)
            
            self.update_idletasks()
            
            # Get projects
            self.projects = self.controller.get_projects()
            
            # Get starred projects
            self.starred_projects = self.controller.get_starred_projects()
            
            # Get setup commands
            self.setup_commands = self.controller.get_setup_commands()
            
            # Update project cards
            self._update_project_cards()
            
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
            
            # Show error state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            error_label = ttk.Label(
                self.scrollable_frame,
                text=f"Error loading projects: {str(e)}",
                style="Error.TLabel"
            )
            error_label.pack(pady=PADDING * 2)
    
    def show(self):
        """Show the projects frame."""
        self.pack(fill=tk.BOTH, expand=True)
        self.load_projects()
    
    def hide(self):
        """Hide the projects frame."""
        self.pack_forget()

