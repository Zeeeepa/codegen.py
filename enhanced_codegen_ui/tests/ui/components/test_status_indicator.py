"""
Tests for the StatusIndicator component.

This module contains tests for the StatusIndicator component,
verifying its status display functionality.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from enhanced_codegen_ui.ui.components.status_indicator import StatusIndicator
from enhanced_codegen_ui.utils.constants import COLORS, STATUS_COLORS


class TestStatusIndicator:
    """Tests for the StatusIndicator component."""
    
    def test_init(self, root, mock_controller):
        """Test component initialization."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Test Status",
            status_type="info",
            show_icon=True
        )
        
        # Verify initialization
        assert component.status == "Test Status"
        assert component.status_type == "info"
        assert component.show_icon is True
        assert component.status_var.get() == "Test Status"
        
    def test_init_without_icon(self, root, mock_controller):
        """Test component initialization without icon."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Test Status",
            status_type="info",
            show_icon=False
        )
        
        # Verify initialization
        assert component.status == "Test Status"
        assert component.status_type == "info"
        assert component.show_icon is False
        assert component.status_var.get() == "Test Status"
        
    def test_get_icon_for_status(self, root, mock_controller):
        """Test getting icon for status."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller
        )
        
        # Verify icons
        assert component._get_icon_for_status("info") == "ℹ"
        assert component._get_icon_for_status("success") == "✓"
        assert component._get_icon_for_status("warning") == "⚠"
        assert component._get_icon_for_status("error") == "✗"
        assert component._get_icon_for_status("pending") == "⋯"
        assert component._get_icon_for_status("running") == "⟳"
        assert component._get_icon_for_status("completed") == "✓"
        assert component._get_icon_for_status("failed") == "✗"
        assert component._get_icon_for_status("cancelled") == "⊗"
        assert component._get_icon_for_status("unknown") == "•"
        
    def test_get_color_for_status(self, root, mock_controller):
        """Test getting color for status."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller
        )
        
        # Verify colors
        assert component._get_color_for_status("info") == COLORS["info"]
        assert component._get_color_for_status("success") == COLORS["success"]
        assert component._get_color_for_status("warning") == COLORS["warning"]
        assert component._get_color_for_status("error") == COLORS["error"]
        
        # Test with STATUS_COLORS
        if "running" in STATUS_COLORS:
            assert component._get_color_for_status("running") == STATUS_COLORS["running"]
            
        # Test unknown status
        assert component._get_color_for_status("unknown") == COLORS["text"]
        
    def test_set_status(self, root, mock_controller):
        """Test setting status."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Initial Status",
            status_type="info",
            show_icon=True
        )
        
        # Mock icon and status labels
        component.icon_label = MagicMock()
        component.status_label = MagicMock()
        
        # Set status
        component.set_status("New Status", "success")
        
        # Verify status updated
        assert component.status_var.get() == "New Status"
        assert component.status_type == "success"
        
        # Verify icon updated
        component.icon_label.config.assert_called_once()
        assert component.icon_label.config.call_args[1]["text"] == "✓"
        assert "foreground" in component.icon_label.config.call_args[1]
        
        # Verify status label updated
        component.status_label.config.assert_called_once()
        assert "foreground" in component.status_label.config.call_args[1]
        
    def test_set_status_without_type(self, root, mock_controller):
        """Test setting status without type."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Initial Status",
            status_type="info",
            show_icon=True
        )
        
        # Mock icon and status labels
        component.icon_label = MagicMock()
        component.status_label = MagicMock()
        
        # Set status without type
        component.set_status("New Status")
        
        # Verify status updated
        assert component.status_var.get() == "New Status"
        assert component.status_type == "info"
        
        # Verify icon and status label not updated
        component.icon_label.config.assert_not_called()
        component.status_label.config.assert_not_called()
        
    def test_set_status_without_icon(self, root, mock_controller):
        """Test setting status without icon."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Initial Status",
            status_type="info",
            show_icon=False
        )
        
        # Mock status label
        component.status_label = MagicMock()
        
        # Set status
        component.set_status("New Status", "success")
        
        # Verify status updated
        assert component.status_var.get() == "New Status"
        assert component.status_type == "success"
        
        # Verify status label updated
        component.status_label.config.assert_called_once()
        assert "foreground" in component.status_label.config.call_args[1]
        
    def test_clear(self, root, mock_controller):
        """Test clearing status."""
        # Create component
        component = StatusIndicator(
            root,
            mock_controller,
            status="Test Status",
            status_type="error",
            show_icon=True
        )
        
        # Mock set_status
        component.set_status = MagicMock()
        
        # Clear status
        component.clear()
        
        # Verify set_status called
        component.set_status.assert_called_once_with("", "info")

