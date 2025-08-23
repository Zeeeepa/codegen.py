"""
Integration tests for the Enhanced Codegen UI.

This module contains integration tests for the Enhanced Codegen UI,
verifying the interaction between components.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from enhanced_codegen_ui.core.base_component import BaseComponent
from enhanced_codegen_ui.core.enhanced_event_bus import EnhancedEventBus, TypedEvent
from enhanced_codegen_ui.core.events import EventType
from enhanced_codegen_ui.ui.components.search_filter_bar import SearchFilterBar
from enhanced_codegen_ui.ui.components.status_indicator import StatusIndicator
from enhanced_codegen_ui.ui.components.action_button import ActionButton
from enhanced_codegen_ui.ui.components.data_table import DataTable


class TestComponentInteraction:
    """Tests for component interaction."""
    
    def test_search_filter_table_integration(self, root, mock_controller):
        """Test integration between search filter and data table."""
        # Create columns
        columns = [
            {"id": "id", "title": "ID", "width": 50},
            {"id": "name", "title": "Name", "width": 150},
            {"id": "status", "title": "Status", "width": 100}
        ]
        
        # Create data
        data = [
            {"id": "1", "name": "Item 1", "status": "Active"},
            {"id": "2", "name": "Item 2", "status": "Inactive"},
            {"id": "3", "name": "Item 3", "status": "Active"}
        ]
        
        # Create data table
        table = DataTable(
            root,
            mock_controller,
            columns=columns,
            data=data
        )
        
        # Mock table methods
        table.set_data = MagicMock()
        
        # Create search filter
        search_filter = SearchFilterBar(
            root,
            mock_controller,
            on_search=lambda text: table.set_data([
                row for row in data
                if text.lower() in row["name"].lower()
            ]),
            on_filter=lambda value: table.set_data([
                row for row in data
                if value == "all" or row["status"].lower() == value.lower()
            ]),
            filter_options=["all", "active", "inactive"]
        )
        
        # Test search
        search_filter.search_var.set("item 2")
        search_filter._on_search()
        
        # Verify table data filtered
        table.set_data.assert_called_once()
        filtered_data = table.set_data.call_args[0][0]
        assert len(filtered_data) == 1
        assert filtered_data[0]["id"] == "2"
        
        # Reset mock
        table.set_data.reset_mock()
        
        # Test filter
        search_filter.filter_var.set("active")
        search_filter._on_filter_changed()
        
        # Verify table data filtered
        table.set_data.assert_called_once()
        filtered_data = table.set_data.call_args[0][0]
        assert len(filtered_data) == 2
        assert filtered_data[0]["id"] == "1"
        assert filtered_data[1]["id"] == "3"
        
    def test_button_status_integration(self, root, mock_controller):
        """Test integration between action button and status indicator."""
        # Create status indicator
        status = StatusIndicator(
            root,
            mock_controller,
            status="Ready",
            status_type="info"
        )
        
        # Create action button
        button = ActionButton(
            root,
            mock_controller,
            text="Test Action",
            command=lambda: status.set_status("Action completed", "success")
        )
        
        # Test button click
        button.command()
        
        # Verify status updated
        assert status.status_var.get() == "Action completed"
        assert status.status_type == "success"
        
    def test_event_based_integration(self, root):
        """Test integration using events."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock controller
        controller = MagicMock()
        controller.event_bus = event_bus
        
        # Create status indicator
        status = StatusIndicator(
            root,
            controller,
            status="Ready",
            status_type="info"
        )
        
        # Create action button
        button = ActionButton(
            root,
            controller,
            text="Test Action",
            command=lambda: event_bus.publish(
                TypedEvent(EventType.AGENT_RUN_REQUESTED, {"id": "test-id"})
            )
        )
        
        # Subscribe status to events
        status.subscribe(
            EventType.AGENT_RUN_REQUESTED,
            lambda event: status.set_status(f"Running agent {event.data['id']}", "running")
        )
        
        status.subscribe(
            EventType.AGENT_RUN_SUCCEEDED,
            lambda event: status.set_status(f"Agent {event.data['id']} completed", "success")
        )
        
        status.subscribe(
            EventType.AGENT_RUN_FAILED,
            lambda event: status.set_status(f"Agent {event.data['id']} failed", "error")
        )
        
        # Test button click
        button.command()
        
        # Verify status updated
        assert status.status_var.get() == "Running agent test-id"
        assert status.status_type == "running"
        
        # Publish success event
        event_bus.publish(
            TypedEvent(EventType.AGENT_RUN_SUCCEEDED, {"id": "test-id"})
        )
        
        # Verify status updated
        assert status.status_var.get() == "Agent test-id completed"
        assert status.status_type == "success"
        
    def test_component_lifecycle_integration(self, root, mock_controller):
        """Test component lifecycle integration."""
        # Create parent component
        parent = BaseComponent(root, mock_controller)
        
        # Create child components
        status = StatusIndicator(parent, mock_controller)
        button = ActionButton(
            parent,
            mock_controller,
            text="Test Action",
            command=lambda: status.set_status("Action completed", "success")
        )
        
        # Pack components
        status.pack()
        button.pack()
        
        # Verify components mounted
        assert status._mounted is True
        assert button._mounted is True
        
        # Destroy parent
        parent.destroy()
        
        # Verify parent destroyed
        assert not parent.winfo_exists()
        
        # Create new components
        parent = BaseComponent(root, mock_controller)
        
        # Create components with resource management
        status = StatusIndicator(parent, mock_controller)
        
        # Create mock resource and cleanup function
        resource = MagicMock()
        cleanup_func = MagicMock()
        
        # Register resource
        status.register_resource(resource, cleanup_func)
        
        # Destroy parent
        parent.destroy()
        
        # Verify resource cleaned up
        cleanup_func.assert_called_once_with(resource)
        
    def test_data_flow_integration(self, root):
        """Test data flow integration."""
        # Create event bus
        event_bus = EnhancedEventBus()
        
        # Create mock controller
        controller = MagicMock()
        controller.event_bus = event_bus
        
        # Create columns
        columns = [
            {"id": "id", "title": "ID", "width": 50},
            {"id": "name", "title": "Name", "width": 150},
            {"id": "status", "title": "Status", "width": 100}
        ]
        
        # Create data table
        table = DataTable(
            root,
            controller,
            columns=columns,
            data=[]
        )
        
        # Create action button
        button = ActionButton(
            root,
            controller,
            text="Load Data",
            command=lambda: event_bus.publish(
                TypedEvent(EventType.DATA_REQUESTED, {"type": "items"})
            )
        )
        
        # Create status indicator
        status = StatusIndicator(
            root,
            controller,
            status="Ready",
            status_type="info"
        )
        
        # Subscribe to events
        table.subscribe(
            EventType.DATA_LOADED,
            lambda event: table.set_data(event.data["items"])
        )
        
        status.subscribe(
            EventType.DATA_REQUESTED,
            lambda event: status.set_status(f"Loading {event.data['type']}...", "pending")
        )
        
        status.subscribe(
            EventType.DATA_LOADED,
            lambda event: status.set_status(
                f"Loaded {len(event.data['items'])} {event.data['type']}",
                "success"
            )
        )
        
        # Test data flow
        button.command()
        
        # Verify status updated
        assert status.status_var.get() == "Loading items..."
        assert status.status_type == "pending"
        
        # Publish data loaded event
        event_bus.publish(
            TypedEvent(EventType.DATA_LOADED, {
                "type": "items",
                "items": [
                    {"id": "1", "name": "Item 1", "status": "Active"},
                    {"id": "2", "name": "Item 2", "status": "Inactive"}
                ]
            })
        )
        
        # Verify status updated
        assert status.status_var.get() == "Loaded 2 items"
        assert status.status_type == "success"
        
        # Verify table data updated
        assert len(table.data) == 2
        assert table.data[0]["id"] == "1"
        assert table.data[1]["id"] == "2"

