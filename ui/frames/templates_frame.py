"""
Templates frame for the Codegen UI.

This module provides a frame for displaying templates.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable

from ui.components.template_card import TemplateCard
from ui.utils.constants import PADDING, COLORS, EVENT_TYPES, TEMPLATE_CATEGORIES

logger = logging.getLogger(__name__)

class TemplatesFrame(ttk.Frame):
    """
    Frame for displaying templates.
    
    This frame displays a list of templates with filtering and pagination.
    """
    
    def __init__(self, parent, controller):
        """
        Initialize the templates frame.
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        super().__init__(parent)
        
        self.controller = controller
        self.templates = []
        self.current_page = 1
        self.items_per_page = 10
        self.filter_text = ""
        self.category_filter = "ALL"
        
        # Create widgets
        self._create_widgets()
        
        # Register event handlers
        self._register_events()
    
    def _create_widgets(self):
        """Create widgets for the templates frame."""
        # Create header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False, padx=PADDING, pady=PADDING)
        
        # Create title
        title = ttk.Label(
            header_frame,
            text="Templates",
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
            text="Create Template",
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
        
        # Create category filter
        category_label = ttk.Label(
            filter_frame,
            text="Category:"
        )
        category_label.pack(side=tk.LEFT, padx=(PADDING * 2, 0))
        
        self.category_var = tk.StringVar(value="ALL")
        self.category_var.trace_add("write", self._on_category_change)
        
        category_values = ["ALL"] + TEMPLATE_CATEGORIES
        
        category_combobox = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=category_values,
            state="readonly",
            width=15
        )
        category_combobox.pack(side=tk.LEFT, padx=(PADDING, 0))
        
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
            text="No templates found",
            style="Large.TLabel"
        )
    
    def _register_events(self):
        """Register event handlers."""
        self.controller.event_bus.subscribe(EVENT_TYPES["TEMPLATE_CREATED"], self._on_template_created)
        self.controller.event_bus.subscribe(EVENT_TYPES["TEMPLATE_UPDATED"], self._on_template_updated)
        self.controller.event_bus.subscribe(EVENT_TYPES["TEMPLATE_DELETED"], self._on_template_deleted)
        self.controller.event_bus.subscribe(EVENT_TYPES["REFRESH_REQUESTED"], self._on_refresh_requested)
    
    def _on_template_created(self, event):
        """
        Handle template created event.
        
        Args:
            event: Event data
        """
        self.load_templates()
    
    def _on_template_updated(self, event):
        """
        Handle template updated event.
        
        Args:
            event: Event data
        """
        self.load_templates()
    
    def _on_template_deleted(self, event):
        """
        Handle template deleted event.
        
        Args:
            event: Event data
        """
        self.load_templates()
    
    def _on_refresh_requested(self, event):
        """
        Handle refresh requested event.
        
        Args:
            event: Event data
        """
        self.load_templates()
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        self.load_templates()
    
    def _on_create_click(self):
        """Handle create button click."""
        self.controller.show_create_template_dialog()
    
    def _on_search_change(self, *args):
        """Handle search entry change."""
        self.filter_text = self.search_var.get().lower()
        self._update_template_cards()
    
    def _on_category_change(self, *args):
        """Handle category filter change."""
        self.category_filter = self.category_var.get()
        self._update_template_cards()
    
    def _on_prev_click(self):
        """Handle previous button click."""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_template_cards()
    
    def _on_next_click(self):
        """Handle next button click."""
        total_pages = self._get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_template_cards()
    
    def _get_total_pages(self):
        """
        Get total number of pages.
        
        Returns:
            Total number of pages
        """
        filtered_templates = self._get_filtered_templates()
        return max(1, (len(filtered_templates) + self.items_per_page - 1) // self.items_per_page)
    
    def _get_filtered_templates(self):
        """
        Get filtered templates.
        
        Returns:
            Filtered templates
        """
        filtered_templates = []
        
        for template in self.templates:
            # Apply text filter
            if self.filter_text:
                name = template.get("name", "").lower()
                description = template.get("description", "").lower()
                content = template.get("content", "").lower()
                
                if (self.filter_text not in name and 
                    self.filter_text not in description and 
                    self.filter_text not in content):
                    continue
            
            # Apply category filter
            if self.category_filter != "ALL" and template.get("category") != self.category_filter:
                continue
            
            filtered_templates.append(template)
        
        return filtered_templates
    
    def _update_template_cards(self):
        """Update template cards."""
        # Clear scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get filtered templates
        filtered_templates = self._get_filtered_templates()
        
        # Update pagination
        total_pages = self._get_total_pages()
        self.current_page = min(self.current_page, total_pages)
        
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)
        
        # Get paginated templates
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_templates = filtered_templates[start_idx:end_idx]
        
        # Show empty state if no templates
        if not paginated_templates:
            self.empty_label.pack(pady=PADDING * 2)
            return
        
        # Create template cards
        for template in paginated_templates:
            card = TemplateCard(
                self.scrollable_frame,
                template,
                on_view=self._on_view_template,
                on_edit=self._on_edit_template,
                on_delete=self._on_delete_template,
                on_use=self._on_use_template
            )
            card.pack(fill=tk.X, expand=False, pady=(0, PADDING))
    
    def _on_view_template(self, template_id):
        """
        Handle view template.
        
        Args:
            template_id: Template ID
        """
        self.controller.show_template_detail(template_id)
    
    def _on_edit_template(self, template_id):
        """
        Handle edit template.
        
        Args:
            template_id: Template ID
        """
        self.controller.show_edit_template_dialog(template_id)
    
    def _on_delete_template(self, template_id):
        """
        Handle delete template.
        
        Args:
            template_id: Template ID
        """
        self.controller.delete_template(template_id)
    
    def _on_use_template(self, template_id):
        """
        Handle use template.
        
        Args:
            template_id: Template ID
        """
        self.controller.show_create_agent_run_dialog(template_id=template_id)
    
    def load_templates(self):
        """Load templates."""
        try:
            # Show loading state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            loading_label = ttk.Label(
                self.scrollable_frame,
                text="Loading templates...",
                style="Large.TLabel"
            )
            loading_label.pack(pady=PADDING * 2)
            
            self.update_idletasks()
            
            # Get templates
            self.templates = self.controller.get_templates()
            
            # Update template cards
            self._update_template_cards()
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            
            # Show error state
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            error_label = ttk.Label(
                self.scrollable_frame,
                text=f"Error loading templates: {str(e)}",
                style="Error.TLabel"
            )
            error_label.pack(pady=PADDING * 2)
    
    def show(self):
        """Show the templates frame."""
        self.pack(fill=tk.BOTH, expand=True)
        self.load_templates()
    
    def hide(self):
        """Hide the templates frame."""
        self.pack_forget()

