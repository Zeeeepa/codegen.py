"""
Tests for the DataTable component.

This module contains tests for the DataTable component,
verifying its table functionality, sorting, and pagination.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch, call

from enhanced_codegen_ui.ui.components.data_table import DataTable
from enhanced_codegen_ui.utils.constants import PADDING


class TestDataTable:
    """Tests for the DataTable component."""
    
    @pytest.fixture
    def columns(self):
        """Provide test columns."""
        return [
            {"id": "id", "title": "ID", "width": 50},
            {"id": "name", "title": "Name", "width": 150},
            {"id": "status", "title": "Status", "width": 100}
        ]
        
    @pytest.fixture
    def data(self):
        """Provide test data."""
        return [
            {"id": "1", "name": "Item 1", "status": "Active"},
            {"id": "2", "name": "Item 2", "status": "Inactive"},
            {"id": "3", "name": "Item 3", "status": "Active"}
        ]
        
    def test_init(self, root, mock_controller, columns, data):
        """Test component initialization."""
        # Create mock callbacks
        on_select = MagicMock()
        on_double_click = MagicMock()
        on_sort = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_select=on_select,
            on_double_click=on_double_click,
            on_sort=on_sort,
            selectable=True,
            show_header=True,
            height=10,
            pagination=True,
            page_size=2
        )
        
        # Verify initialization
        assert component.columns == columns
        assert component.data == data
        assert component.on_select == on_select
        assert component.on_double_click == on_double_click
        assert component.on_sort == on_sort
        assert component.selectable is True
        assert component.show_header is True
        assert component.height == 10
        assert component.pagination is True
        assert component.page_size == 2
        assert component.current_page == 1
        assert component.sort_column is None
        assert component.sort_ascending is True
        
    def test_init_minimal(self, root, mock_controller, columns):
        """Test component initialization with minimal parameters."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns
        )
        
        # Verify initialization
        assert component.columns == columns
        assert component.data == []
        assert component.on_select is None
        assert component.on_double_click is None
        assert component.on_sort is None
        assert component.selectable is True
        assert component.show_header is True
        assert component.height is None
        assert component.pagination is False
        assert component.page_size == 10
        assert component.current_page == 1
        assert component.sort_column is None
        assert component.sort_ascending is True
        
    def test_load_data(self, root, mock_controller, columns, data):
        """Test loading data into the treeview."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = ["item1", "item2"]
        
        # Mock status variable
        component.status_var = MagicMock()
        
        # Load data
        component._load_data()
        
        # Verify treeview cleared
        component.treeview.delete.assert_has_calls([call("item1"), call("item2")])
        
        # Verify data inserted
        assert component.treeview.insert.call_count == 3
        
        # Verify status updated
        component.status_var.set.assert_called_once_with("Showing 3 rows")
        
    def test_load_data_with_pagination(self, root, mock_controller, columns, data):
        """Test loading data with pagination."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            pagination=True,
            page_size=2
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = []
        
        # Mock status and page variables
        component.status_var = MagicMock()
        component.page_var = MagicMock()
        
        # Mock pagination buttons
        component.prev_button = MagicMock()
        component.next_button = MagicMock()
        
        # Load data
        component._load_data()
        
        # Verify data inserted (only first page)
        assert component.treeview.insert.call_count == 2
        
        # Verify status updated
        component.status_var.set.assert_called_once_with("Showing 2 of 3 rows")
        
        # Verify page updated
        component.page_var.set.assert_called_once_with("Page 1 of 2")
        
        # Verify pagination buttons updated
        component.prev_button.state.assert_called_once_with(["disabled"])
        component.next_button.state.assert_called_once_with(["!disabled"])
        
    def test_on_heading_click(self, root, mock_controller, columns, data):
        """Test column heading click."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = []
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Click heading
        component._on_heading_click("name")
        
        # Verify sort state
        assert component.sort_column == "name"
        assert component.sort_ascending is True
        
        # Verify headings updated
        component.treeview.heading.assert_has_calls([
            call("id", text="ID"),
            call("name", text="Name ▲"),
            call("status", text="Status")
        ])
        
        # Verify data reloaded
        component._load_data.assert_called_once()
        
        # Reset mock
        component._load_data.reset_mock()
        
        # Click same heading again
        component._on_heading_click("name")
        
        # Verify sort direction toggled
        assert component.sort_column == "name"
        assert component.sort_ascending is False
        
        # Verify headings updated
        component.treeview.heading.assert_has_calls([
            call("id", text="ID"),
            call("name", text="Name ▼"),
            call("status", text="Status")
        ])
        
        # Verify data reloaded
        component._load_data.assert_called_once()
        
    def test_on_heading_click_with_sort_callback(self, root, mock_controller, columns, data):
        """Test column heading click with sort callback."""
        # Create mock sort callback
        on_sort = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_sort=on_sort
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Click heading
        component._on_heading_click("name")
        
        # Verify sort callback called
        on_sort.assert_called_once_with("name", True)
        
        # Verify data not reloaded (callback should handle it)
        component._load_data.assert_not_called()
        
    def test_on_select(self, root, mock_controller, columns, data):
        """Test row selection."""
        # Create mock select callback
        on_select = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_select=on_select
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.selection.return_value = ["item1"]
        component.treeview.item.return_value = {"values": ["1", "Item 1", "Active"]}
        
        # Select row
        component._on_select(MagicMock())
        
        # Verify callback called
        on_select.assert_called_once_with({"id": "1", "name": "Item 1", "status": "Active"})
        
    def test_on_select_no_selection(self, root, mock_controller, columns, data):
        """Test row selection with no selection."""
        # Create mock select callback
        on_select = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_select=on_select
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.selection.return_value = []
        
        # Select row
        component._on_select(MagicMock())
        
        # Verify callback not called
        on_select.assert_not_called()
        
    def test_on_double_click(self, root, mock_controller, columns, data):
        """Test row double click."""
        # Create mock double click callback
        on_double_click = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_double_click=on_double_click
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.identify.return_value = "item1"
        component.treeview.item.return_value = {"values": ["1", "Item 1", "Active"]}
        
        # Create mock event
        event = MagicMock()
        event.x = 10
        event.y = 20
        
        # Double click row
        component._on_double_click(event)
        
        # Verify callback called
        on_double_click.assert_called_once_with({"id": "1", "name": "Item 1", "status": "Active"})
        
    def test_on_double_click_no_item(self, root, mock_controller, columns, data):
        """Test row double click with no item."""
        # Create mock double click callback
        on_double_click = MagicMock()
        
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            on_double_click=on_double_click
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.identify.return_value = ""
        
        # Create mock event
        event = MagicMock()
        event.x = 10
        event.y = 20
        
        # Double click row
        component._on_double_click(event)
        
        # Verify callback not called
        on_double_click.assert_not_called()
        
    def test_pagination(self, root, mock_controller, columns, data):
        """Test pagination."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            pagination=True,
            page_size=2
        )
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Test initial state
        assert component.current_page == 1
        
        # Test next page
        component._on_next_page()
        assert component.current_page == 2
        component._load_data.assert_called_once()
        
        # Reset mock
        component._load_data.reset_mock()
        
        # Test next page (already at last page)
        component._on_next_page()
        assert component.current_page == 2
        component._load_data.assert_not_called()
        
        # Test previous page
        component._on_prev_page()
        assert component.current_page == 1
        component._load_data.assert_called_once()
        
        # Reset mock
        component._load_data.reset_mock()
        
        # Test previous page (already at first page)
        component._on_prev_page()
        assert component.current_page == 1
        component._load_data.assert_not_called()
        
    def test_page_size_change(self, root, mock_controller, columns, data):
        """Test page size change."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            pagination=True,
            page_size=2
        )
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Mock page size variable
        component.page_size_var = MagicMock()
        component.page_size_var.get.return_value = "5"
        
        # Change page size
        component._on_page_size_changed(MagicMock())
        
        # Verify page size updated
        assert component.page_size == 5
        assert component.current_page == 1
        component._load_data.assert_called_once()
        
    def test_set_data(self, root, mock_controller, columns, data):
        """Test setting data."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns
        )
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Set data
        component.set_data(data)
        
        # Verify data updated
        assert component.data == data
        assert component.current_page == 1
        component._load_data.assert_called_once()
        
    def test_get_selected_row(self, root, mock_controller, columns, data):
        """Test getting selected row."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.selection.return_value = ["item1"]
        component.treeview.item.return_value = {"values": ["1", "Item 1", "Active"]}
        
        # Get selected row
        row = component.get_selected_row()
        
        # Verify row
        assert row == {"id": "1", "name": "Item 1", "status": "Active"}
        
    def test_get_selected_row_no_selection(self, root, mock_controller, columns, data):
        """Test getting selected row with no selection."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.selection.return_value = []
        
        # Get selected row
        row = component.get_selected_row()
        
        # Verify row
        assert row is None
        
    def test_add_row(self, root, mock_controller, columns, data):
        """Test adding a row."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = ["item1", "item2", "item3"]
        
        # Mock status variable
        component.status_var = MagicMock()
        
        # Add row
        new_row = {"id": "4", "name": "Item 4", "status": "Active"}
        component.add_row(new_row)
        
        # Verify data updated
        assert len(component.data) == 4
        assert component.data[3] == new_row
        
        # Verify row inserted
        component.treeview.insert.assert_called_once()
        
        # Verify status updated
        component.status_var.set.assert_called_once_with("Showing 4 rows")
        
    def test_add_row_with_pagination(self, root, mock_controller, columns, data):
        """Test adding a row with pagination."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data,
            pagination=True,
            page_size=2
        )
        
        # Mock _load_data
        component._load_data = MagicMock()
        
        # Add row
        new_row = {"id": "4", "name": "Item 4", "status": "Active"}
        component.add_row(new_row)
        
        # Verify data updated
        assert len(component.data) == 4
        assert component.data[3] == new_row
        
        # Verify data reloaded
        component._load_data.assert_called_once()
        
    def test_update_row(self, root, mock_controller, columns, data):
        """Test updating a row."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = ["item1", "item2", "item3"]
        component.treeview.item.side_effect = lambda item, **kwargs: {"values": ["1", "Item 1", "Active"]} if item == "item1" else {"values": ["2", "Item 2", "Inactive"]}
        
        # Update row
        updated_row = {"id": "1", "name": "Updated Item", "status": "Inactive"}
        component.update_row("1", updated_row)
        
        # Verify data updated
        assert component.data[0] == updated_row
        
        # Verify row updated
        component.treeview.item.assert_called_with("item1", values=["1", "Updated Item", "Inactive"])
        
    def test_remove_row(self, root, mock_controller, columns, data):
        """Test removing a row."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = ["item1", "item2", "item3"]
        component.treeview.item.side_effect = lambda item, **kwargs: {"values": ["1", "Item 1", "Active"]} if item == "item1" else {"values": ["2", "Item 2", "Inactive"]}
        
        # Mock status variable
        component.status_var = MagicMock()
        
        # Remove row
        component.remove_row("1")
        
        # Verify data updated
        assert len(component.data) == 2
        assert component.data[0]["id"] == "2"
        
        # Verify row removed
        component.treeview.delete.assert_called_once_with("item1")
        
        # Verify status updated
        component.status_var.set.assert_called_once()
        
    def test_clear(self, root, mock_controller, columns, data):
        """Test clearing the table."""
        # Create component
        component = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock treeview
        component.treeview = MagicMock()
        component.treeview.get_children.return_value = ["item1", "item2", "item3"]
        
        # Mock status variable
        component.status_var = MagicMock()
        
        # Clear table
        component.clear()
        
        # Verify data cleared
        assert component.data == []
        assert component.current_page == 1
        
        # Verify treeview cleared
        component.treeview.delete.assert_has_calls([call("item1"), call("item2"), call("item3")])
        
        # Verify status updated
        component.status_var.set.assert_called_once_with("Showing 0 rows")

