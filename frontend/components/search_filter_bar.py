"""
Search filter bar component for the Enhanced Codegen UI.

This module provides a search filter bar component for the Enhanced Codegen UI,
allowing users to search and filter data.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.utils.constants import PADDING, COLORS


class SearchFilterBar(BaseComponent):
    """
    Search filter bar component for the Enhanced Codegen UI.
    
    This class provides a search filter bar component for the Enhanced Codegen UI,
    allowing users to search and filter data.
    """
    
    def __init__(
        self,
        parent: Any,
        controller: Controller,
        on_search: Callable[[str], None],
        on_filter: Optional[Callable[[str], None]] = None,
        filter_options: Optional[List[str]] = None,
        filter_label: str = "Filter:",
        search_label: str = "Search:",
        placeholder: str = "Search...",
        search_button_text: str = "Search"
    ):
        """
        Initialize the search filter bar.
        
        Args:
            parent: Parent widget
            controller: Application controller
            on_search: Callback for search
            on_filter: Callback for filter
            filter_options: Filter options
            filter_label: Filter label
            search_label: Search label
            placeholder: Search placeholder
            search_button_text: Search button text
        """
        self.on_search = on_search
        self.on_filter = on_filter
        self.filter_options = filter_options
        self.filter_label = filter_label
        self.search_label = search_label
        self.placeholder = placeholder
        self.search_button_text = search_button_text
        
        super().__init__(parent, controller)
        
    def _create_variables(self):
        """Create component variables."""
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="all")
        
    def _create_widgets(self):
        """Create component widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.X, pady=(0, PADDING))
        
        # Create filter if options provided
        if self.filter_options:
            # Create filter label
            filter_label = ttk.Label(container, text=self.filter_label)
            filter_label.pack(side=tk.LEFT, padx=(0, PADDING))
            
            # Create filter combobox
            filter_combobox = ttk.Combobox(
                container,
                textvariable=self.filter_var,
                values=self.filter_options,
                width=15,
                state="readonly"
            )
            filter_combobox.pack(side=tk.LEFT, padx=(0, PADDING*2))
            filter_combobox.bind("<<ComboboxSelected>>", self._on_filter_changed)
            
        # Create search label
        search_label = ttk.Label(container, text=self.search_label)
        search_label.pack(side=tk.LEFT, padx=(0, PADDING))
        
        # Create search entry
        self.search_entry = ttk.Entry(
            container,
            textvariable=self.search_var,
            width=20
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, PADDING))
        self.search_entry.bind("<Return>", self._on_search)
        
        # Set placeholder
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(foreground=COLORS["text_secondary"])
        self.search_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_entry_focus_out)
        
        # Create search button
        search_button = ttk.Button(
            container,
            text=self.search_button_text,
            command=self._on_search
        )
        search_button.pack(side=tk.LEFT)
        
    def _on_entry_focus_in(self, event):
        """
        Handle entry focus in event.
        
        Args:
            event: Event object
        """
        if self.search_var.get() == self.placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground=COLORS["text"])
            
    def _on_entry_focus_out(self, event):
        """
        Handle entry focus out event.
        
        Args:
            event: Event object
        """
        if not self.search_var.get():
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.config(foreground=COLORS["text_secondary"])
            
    def _on_search(self, event=None):
        """
        Handle search button click or Enter key.
        
        Args:
            event: Event object
        """
        search_text = self.search_var.get()
        if search_text and search_text != self.placeholder:
            self.on_search(search_text)
            
    def _on_filter_changed(self, event=None):
        """
        Handle filter combobox selection.
        
        Args:
            event: Event object
        """
        if self.on_filter:
            self.on_filter(self.filter_var.get())
            
    def get_search_text(self) -> str:
        """
        Get the search text.
        
        Returns:
            Search text
        """
        search_text = self.search_var.get()
        if search_text == self.placeholder:
            return ""
        return search_text
        
    def get_filter_value(self) -> str:
        """
        Get the filter value.
        
        Returns:
            Filter value
        """
        return self.filter_var.get()
        
    def clear(self):
        """Clear the search and filter."""
        self.search_var.set(self.placeholder)
        self.search_entry.config(foreground=COLORS["text_secondary"])
        if self.filter_options:
            self.filter_var.set("all")

