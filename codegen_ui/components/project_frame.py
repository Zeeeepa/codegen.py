"""
Project frame for the Codegen UI.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Any, Dict, List, Optional

from codegen_client import CodegenApiError
from codegen_ui.utils.constants import PADDING, MAX_ITEMS


class ProjectFrame(ttk.Frame):
    """
    Project frame for the Codegen UI.
    
    This frame displays a list of repositories/projects and allows users to manage them.
    """
    
    def __init__(self, parent: Any, app: Any):
        """
        Initialize the project frame.
        
        Args:
            parent: Parent widget
            app: Application instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create variables
        self.projects = []
        self.loading = False
        
        # Create widgets
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the project frame widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create header frame
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create header
        header = ttk.Label(
            header_frame, 
            text="Projects", 
            style="Header.TLabel"
        )
        header.pack(side=tk.LEFT)
        
        # Create refresh button
        refresh_button = ttk.Button(
            header_frame, 
            text="Refresh", 
            command=self.load_projects
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Create filter frame
        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create search entry
        search_label = ttk.Label(filter_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, PADDING))
        search_entry.bind("<Return>", lambda e: self.load_projects())
        
        search_button = ttk.Button(
            filter_frame, 
            text="Search", 
            command=self.load_projects
        )
        search_button.pack(side=tk.LEFT)
        
        # Create treeview
        columns = ("id", "name", "full_name", "description")
        self.treeview = ttk.Treeview(
            container, 
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.treeview.heading("id", text="ID")
        self.treeview.heading("name", text="Name")
        self.treeview.heading("full_name", text="Full Name")
        self.treeview.heading("description", text="Description")
        
        self.treeview.column("id", width=80, anchor=tk.W)
        self.treeview.column("name", width=150, anchor=tk.W)
        self.treeview.column("full_name", width=200, anchor=tk.W)
        self.treeview.column("description", width=400, anchor=tk.W)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create status label
        self.status_label = ttk.Label(container, text="")
        self.status_label.pack(fill=tk.X, pady=(PADDING, 0))
        
    def load_projects(self):
        """Load projects from the API."""
        if not self.app.client or not self.app.current_org_id or self.loading:
            return
            
        self.loading = True
        self.app.set_status("Loading projects...")
        
        def _load_thread():
            try:
                # Get search filter
                search_filter = self.search_var.get().strip()
                
                # Get repositories
                repositories = self.app.client.repositories.get_repositories(
                    org_id=self.app.current_org_id,
                    limit=MAX_ITEMS["project_list"]
                )
                
                # Filter by search if needed
                if search_filter:
                    search_filter = search_filter.lower()
                    self.projects = [
                        repo for repo in repositories.items
                        if (
                            search_filter in (repo.name or "").lower() or
                            search_filter in (repo.full_name or "").lower() or
                            search_filter in (repo.description or "").lower()
                        )
                    ]
                else:
                    self.projects = repositories.items
                
                # Update UI in main thread
                self.after(0, self._update_treeview)
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            finally:
                self.loading = False
        
        # Start load thread
        threading.Thread(target=_load_thread, daemon=True).start()
        
    def _update_treeview(self):
        """Update the treeview with projects."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Add projects to treeview
        for project in self.projects:
            # Add to treeview
            self.treeview.insert(
                "", 
                tk.END, 
                values=(
                    project.id,
                    project.name,
                    project.full_name,
                    project.description[:50] + "..." if project.description and len(project.description) > 50 else project.description
                )
            )
                
        # Update status label
        self.status_label.config(text=f"Showing {len(self.projects)} projects")
        
        # Update app status
        self.app.set_status(f"Loaded {len(self.projects)} projects")
        
    def _show_error(self, error_message: str):
        """
        Show an error message.
        
        Args:
            error_message: Error message to display
        """
        self.status_label.config(text=f"Error: {error_message}")
        self.app.set_status(f"Error loading projects: {error_message}")
        
    def clear(self):
        """Clear the project list."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Clear variables
        self.projects = []
        self.status_label.config(text="")

