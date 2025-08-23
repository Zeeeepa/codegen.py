"""
Data table component for the Enhanced Codegen UI.

This module provides a data table component for the Enhanced Codegen UI,
with support for sorting, pagination, and row selection.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Any, Dict, List, Optional, Callable, Tuple

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.utils.constants import PADDING, COLORS


class DataTable(BaseComponent):
    """
    Data table component for the Enhanced Codegen UI.
    
    This class provides a data table component for the Enhanced Codegen UI,
    with support for sorting, pagination, and row selection.
    """
    
    def __init__(
        self,
        parent: Any,
        controller: Controller,
        columns: List[Dict[str, Any]],
        data: Optional[List[Dict[str, Any]]] = None,
        on_select: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_double_click: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_sort: Optional[Callable[[str, bool], None]] = None,
        selectable: bool = True,
        show_header: bool = True,
        height: Optional[int] = None,
        pagination: bool = False,
        page_size: int = 10
    ):
        """
        Initialize the data table.
        
        Args:
            parent: Parent widget
            controller: Application controller
            columns: Column definitions
            data: Table data
            on_select: Row selection callback
            on_double_click: Row double click callback
            on_sort: Column sort callback
            selectable: Whether rows are selectable
            show_header: Whether to show column headers
            height: Table height in rows
            pagination: Whether to show pagination controls
            page_size: Number of rows per page
        """
        self.columns = columns
        self.data = data or []
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.on_sort = on_sort
        self.selectable = selectable
        self.show_header = show_header
        self.height = height
        self.pagination = pagination
        self.page_size = page_size
        self.current_page = 1
        self.sort_column = None
        self.sort_ascending = True
        
        super().__init__(parent, controller)
        
    def _create_variables(self):
        """Create component variables."""
        self.status_var = tk.StringVar()
        
    def _create_widgets(self):
        """Create component widgets."""
        # Create container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        treeview_args = {
            "columns": [col["id"] for col in self.columns],
            "show": "headings" if self.show_header else "",
            "selectmode": "browse" if self.selectable else "none"
        }
        
        if self.height:
            treeview_args["height"] = self.height
            
        self.treeview = ttk.Treeview(container, **treeview_args)
        
        # Configure columns
        for col in self.columns:
            self.treeview.heading(
                col["id"],
                text=col.get("title", col["id"]),
                command=lambda c=col["id"]: self._on_heading_click(c)
            )
            
            width = col.get("width", 100)
            anchor = col.get("anchor", tk.W)
            
            self.treeview.column(
                col["id"],
                width=width,
                anchor=anchor,
                stretch=col.get("stretch", False)
            )
            
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create pagination controls if enabled
        if self.pagination:
            self._create_pagination_controls()
            
        # Create status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill=tk.X, pady=(PADDING, 0))
        
        status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var
        )
        status_label.pack(side=tk.LEFT)
        
        # Bind events
        if self.selectable:
            self.treeview.bind("<<TreeviewSelect>>", self._on_select)
            
        if self.on_double_click:
            self.treeview.bind("<Double-1>", self._on_double_click)
            
        # Load data
        self._load_data()
        
    def _create_pagination_controls(self):
        """Create pagination controls."""
        # Create pagination frame
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill=tk.X, pady=(PADDING, 0))
        
        # Create previous page button
        self.prev_button = ttk.Button(
            pagination_frame,
            text="<",
            command=self._on_prev_page,
            width=2
        )
        self.prev_button.pack(side=tk.LEFT)
        
        # Create page indicator
        self.page_var = tk.StringVar(value="Page 1")
        page_label = ttk.Label(
            pagination_frame,
            textvariable=self.page_var,
            width=10
        )
        page_label.pack(side=tk.LEFT, padx=PADDING)
        
        # Create next page button
        self.next_button = ttk.Button(
            pagination_frame,
            text=">",
            command=self._on_next_page,
            width=2
        )
        self.next_button.pack(side=tk.LEFT)
        
        # Create page size selector
        page_size_label = ttk.Label(
            pagination_frame,
            text="Rows per page:"
        )
        page_size_label.pack(side=tk.LEFT, padx=(PADDING*2, PADDING))
        
        self.page_size_var = tk.StringVar(value=str(self.page_size))
        page_size_combobox = ttk.Combobox(
            pagination_frame,
            textvariable=self.page_size_var,
            values=["10", "25", "50", "100"],
            width=5,
            state="readonly"
        )
        page_size_combobox.pack(side=tk.LEFT)
        page_size_combobox.bind("<<ComboboxSelected>>", self._on_page_size_changed)
        
    def _load_data(self):
        """Load data into the treeview."""
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Sort data if needed
        if self.sort_column:
            self.data.sort(
                key=lambda x: x.get(self.sort_column, ""),
                reverse=not self.sort_ascending
            )
            
        # Get paginated data if pagination enabled
        if self.pagination:
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            page_data = self.data[start_idx:end_idx]
        else:
            page_data = self.data
            
        # Add data to treeview
        for row in page_data:
            values = [row.get(col["id"], "") for col in self.columns]
            item_id = self.treeview.insert("", tk.END, values=values)
            
            # Set row tags if provided
            if "tags" in row:
                self.treeview.item(item_id, tags=row["tags"])
                
        # Update status
        if self.pagination:
            total_pages = max(1, (len(self.data) + self.page_size - 1) // self.page_size)
            self.page_var.set(f"Page {self.current_page} of {total_pages}")
            
            # Update pagination buttons
            self.prev_button.state(["disabled" if self.current_page <= 1 else "!disabled"])
            self.next_button.state(["disabled" if self.current_page >= total_pages else "!disabled"])
            
            self.status_var.set(f"Showing {len(page_data)} of {len(self.data)} rows")
        else:
            self.status_var.set(f"Showing {len(page_data)} rows")
            
    def _on_heading_click(self, column):
        """
        Handle column heading click.
        
        Args:
            column: Column ID
        """
        # Toggle sort direction if same column
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
            
        # Update headings
        for col in self.columns:
            if col["id"] == column:
                direction = "▲" if self.sort_ascending else "▼"
                self.treeview.heading(col["id"], text=f"{col.get('title', col['id'])} {direction}")
            else:
                self.treeview.heading(col["id"], text=col.get("title", col["id"]))
                
        # Call sort callback if provided
        if self.on_sort:
            self.on_sort(column, self.sort_ascending)
        else:
            # Sort data locally
            self._load_data()
            
    def _on_select(self, event):
        """
        Handle row selection.
        
        Args:
            event: Event object
        """
        if not self.on_select:
            return
            
        selection = self.treeview.selection()
        if not selection:
            return
            
        # Get selected row data
        item = self.treeview.item(selection[0])
        values = item["values"]
        
        # Create row data dict
        row_data = {
            col["id"]: values[i]
            for i, col in enumerate(self.columns)
            if i < len(values)
        }
        
        # Call selection callback
        self.on_select(row_data)
        
    def _on_double_click(self, event):
        """
        Handle row double click.
        
        Args:
            event: Event object
        """
        if not self.on_double_click:
            return
            
        # Get clicked item
        item = self.treeview.identify("item", event.x, event.y)
        if not item:
            return
            
        # Get row data
        item_data = self.treeview.item(item)
        values = item_data["values"]
        
        # Create row data dict
        row_data = {
            col["id"]: values[i]
            for i, col in enumerate(self.columns)
            if i < len(values)
        }
        
        # Call double click callback
        self.on_double_click(row_data)
        
    def _on_prev_page(self):
        """Handle previous page button click."""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data()
            
    def _on_next_page(self):
        """Handle next page button click."""
        total_pages = max(1, (len(self.data) + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self._load_data()
            
    def _on_page_size_changed(self, event):
        """
        Handle page size change.
        
        Args:
            event: Event object
        """
        try:
            new_page_size = int(self.page_size_var.get())
            if new_page_size != self.page_size:
                self.page_size = new_page_size
                self.current_page = 1
                self._load_data()
        except ValueError:
            pass
            
    def set_data(self, data: List[Dict[str, Any]]):
        """
        Set the table data.
        
        Args:
            data: Table data
        """
        self.data = data
        self.current_page = 1
        self._load_data()
        
    def get_selected_row(self) -> Optional[Dict[str, Any]]:
        """
        Get the selected row data.
        
        Returns:
            Selected row data or None if no row is selected
        """
        selection = self.treeview.selection()
        if not selection:
            return None
            
        # Get selected row data
        item = self.treeview.item(selection[0])
        values = item["values"]
        
        # Create row data dict
        row_data = {
            col["id"]: values[i]
            for i, col in enumerate(self.columns)
            if i < len(values)
        }
        
        return row_data
        
    def add_row(self, row_data: Dict[str, Any]):
        """
        Add a row to the table.
        
        Args:
            row_data: Row data
        """
        self.data.append(row_data)
        
        # Add to treeview if on last page or not paginated
        if not self.pagination or self.current_page == max(1, (len(self.data) + self.page_size - 1) // self.page_size):
            values = [row_data.get(col["id"], "") for col in self.columns]
            item_id = self.treeview.insert("", tk.END, values=values)
            
            # Set row tags if provided
            if "tags" in row_data:
                self.treeview.item(item_id, tags=row_data["tags"])
                
            # Update status
            if self.pagination:
                self.status_var.set(f"Showing {len(self.treeview.get_children())} of {len(self.data)} rows")
            else:
                self.status_var.set(f"Showing {len(self.data)} rows")
        else:
            # Reload data to update pagination
            self._load_data()
            
    def update_row(self, row_id: str, row_data: Dict[str, Any]):
        """
        Update a row in the table.
        
        Args:
            row_id: Row ID column value
            row_data: Row data
        """
        # Find row in data
        for i, row in enumerate(self.data):
            if str(row.get(self.columns[0]["id"], "")) == str(row_id):
                self.data[i] = row_data
                break
                
        # Update treeview
        for item in self.treeview.get_children():
            item_data = self.treeview.item(item)
            if str(item_data["values"][0]) == str(row_id):
                values = [row_data.get(col["id"], "") for col in self.columns]
                self.treeview.item(item, values=values)
                
                # Set row tags if provided
                if "tags" in row_data:
                    self.treeview.item(item, tags=row_data["tags"])
                    
                break
                
    def remove_row(self, row_id: str):
        """
        Remove a row from the table.
        
        Args:
            row_id: Row ID column value
        """
        # Find row in data
        for i, row in enumerate(self.data):
            if str(row.get(self.columns[0]["id"], "")) == str(row_id):
                self.data.pop(i)
                break
                
        # Remove from treeview
        for item in self.treeview.get_children():
            item_data = self.treeview.item(item)
            if str(item_data["values"][0]) == str(row_id):
                self.treeview.delete(item)
                break
                
        # Update status
        if self.pagination:
            self.status_var.set(f"Showing {len(self.treeview.get_children())} of {len(self.data)} rows")
        else:
            self.status_var.set(f"Showing {len(self.data)} rows")
            
    def clear(self):
        """Clear the table."""
        self.data = []
        self.current_page = 1
        
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Update status
        self.status_var.set("Showing 0 rows")

