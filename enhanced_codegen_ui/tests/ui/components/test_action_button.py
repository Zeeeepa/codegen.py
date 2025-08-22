"""
Tests for the ActionButton component.

This module contains tests for the ActionButton component,
verifying its button functionality and tooltip behavior.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from enhanced_codegen_ui.ui.components.action_button import ActionButton
from enhanced_codegen_ui.utils.constants import COLORS


class TestActionButton:
    """Tests for the ActionButton component."""
    
    def test_init(self, root, mock_controller):
        """Test component initialization."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            button_type="primary",
            icon="test-icon",
            tooltip="Test Tooltip",
            enabled=True,
            width=10
        )
        
        # Verify initialization
        assert component.text == "Test Button"
        assert component.command == command
        assert component.button_type == "primary"
        assert component.icon == "test-icon"
        assert component.tooltip == "Test Tooltip"
        assert component.enabled is True
        assert component.width == 10
        
    def test_init_minimal(self, root, mock_controller):
        """Test component initialization with minimal parameters."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command
        )
        
        # Verify initialization
        assert component.text == "Test Button"
        assert component.command == command
        assert component.button_type == "primary"
        assert component.icon is None
        assert component.tooltip is None
        assert component.enabled is True
        assert component.width is None
        
    def test_set_enabled(self, root, mock_controller):
        """Test setting button enabled state."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            enabled=True
        )
        
        # Mock button
        component.button = MagicMock()
        
        # Disable button
        component.set_enabled(False)
        
        # Verify state
        assert component.enabled is False
        component.button.state.assert_called_once_with(["disabled"])
        
        # Reset mock
        component.button.reset_mock()
        
        # Enable button
        component.set_enabled(True)
        
        # Verify state
        assert component.enabled is True
        component.button.state.assert_called_once_with(["!disabled"])
        
    def test_set_text(self, root, mock_controller):
        """Test setting button text."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command
        )
        
        # Mock button
        component.button = MagicMock()
        
        # Set text
        component.set_text("New Text")
        
        # Verify text
        assert component.text == "New Text"
        component.button.config.assert_called_once_with(text="New Text")
        
    def test_set_command(self, root, mock_controller):
        """Test setting button command."""
        # Create mock commands
        command1 = MagicMock()
        command2 = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command1
        )
        
        # Mock button
        component.button = MagicMock()
        
        # Set command
        component.set_command(command2)
        
        # Verify command
        assert component.command == command2
        component.button.config.assert_called_once_with(command=command2)
        
    def test_tooltip_creation(self, root, mock_controller):
        """Test tooltip creation."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            tooltip="Test Tooltip"
        )
        
        # Verify tooltip setup
        assert component.tooltip == "Test Tooltip"
        assert not hasattr(component, "tooltip_window") or component.tooltip_window is None
        
    def test_show_tooltip(self, root, mock_controller):
        """Test showing tooltip."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            tooltip="Test Tooltip"
        )
        
        # Mock button and toplevel
        component.button = MagicMock()
        component.button.bbox.return_value = (10, 20, 30, 40)
        component.button.winfo_rootx.return_value = 100
        component.button.winfo_rooty.return_value = 200
        
        # Mock toplevel
        mock_toplevel = MagicMock()
        with patch("tkinter.Toplevel", return_value=mock_toplevel) as mock_toplevel_class:
            # Show tooltip
            component._show_tooltip(MagicMock())
            
            # Verify toplevel created
            mock_toplevel_class.assert_called_once_with(component.button)
            mock_toplevel.wm_overrideredirect.assert_called_once_with(True)
            mock_toplevel.wm_geometry.assert_called_once()
            
            # Verify tooltip window set
            assert component.tooltip_window == mock_toplevel
            
    def test_hide_tooltip(self, root, mock_controller):
        """Test hiding tooltip."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            tooltip="Test Tooltip"
        )
        
        # Create mock tooltip window
        component.tooltip_window = MagicMock()
        
        # Hide tooltip
        component._hide_tooltip(MagicMock())
        
        # Verify tooltip window destroyed
        component.tooltip_window.destroy.assert_called_once()
        assert component.tooltip_window is None
        
    def test_set_tooltip(self, root, mock_controller):
        """Test setting tooltip."""
        # Create mock command
        command = MagicMock()
        
        # Create component
        component = ActionButton(
            root,
            mock_controller,
            text="Test Button",
            command=command,
            tooltip="Test Tooltip"
        )
        
        # Set tooltip
        component.set_tooltip("New Tooltip")
        
        # Verify tooltip
        assert component.tooltip == "New Tooltip"
        
        # Create mock tooltip window
        component.tooltip_window = MagicMock()
        
        # Set tooltip again
        component.set_tooltip("Another Tooltip")
        
        # Verify tooltip window destroyed
        component.tooltip_window.destroy.assert_called_once()
        assert component.tooltip == "Another Tooltip"

