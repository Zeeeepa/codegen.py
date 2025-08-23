"""
Tests for the SearchFilterBar component.

This module contains tests for the SearchFilterBar component,
verifying its search and filter functionality.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from enhanced_codegen_ui.ui.components.search_filter_bar import SearchFilterBar
from enhanced_codegen_ui.utils.constants import COLORS


class TestSearchFilterBar:
    """Tests for the SearchFilterBar component."""
    
    def test_init(self, root, mock_controller):
        """Test component initialization."""
        # Create mock callbacks
        on_search = MagicMock()
        on_filter = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            on_filter=on_filter,
            filter_options=["all", "option1", "option2"],
            filter_label="Test Filter:",
            search_label="Test Search:",
            placeholder="Test Placeholder",
            search_button_text="Test Search"
        )
        
        # Verify initialization
        assert component.on_search == on_search
        assert component.on_filter == on_filter
        assert component.filter_options == ["all", "option1", "option2"]
        assert component.filter_label == "Test Filter:"
        assert component.search_label == "Test Search:"
        assert component.placeholder == "Test Placeholder"
        assert component.search_button_text == "Test Search"
        assert component.search_var.get() == "Test Placeholder"
        assert component.filter_var.get() == "all"
        
    def test_init_without_filter(self, root, mock_controller):
        """Test component initialization without filter."""
        # Create mock callback
        on_search = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search
        )
        
        # Verify initialization
        assert component.on_search == on_search
        assert component.on_filter is None
        assert component.filter_options is None
        assert component.search_var.get() == "Search..."
        assert component.filter_var.get() == "all"
        
    def test_search(self, root, mock_controller):
        """Test search functionality."""
        # Create mock callback
        on_search = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search
        )
        
        # Set search text
        component.search_var.set("test search")
        
        # Trigger search
        component._on_search()
        
        # Verify callback called
        on_search.assert_called_once_with("test search")
        
    def test_search_with_placeholder(self, root, mock_controller):
        """Test search with placeholder text."""
        # Create mock callback
        on_search = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            placeholder="Test Placeholder"
        )
        
        # Verify search text is placeholder
        assert component.search_var.get() == "Test Placeholder"
        
        # Trigger search
        component._on_search()
        
        # Verify callback not called
        on_search.assert_not_called()
        
    def test_filter(self, root, mock_controller):
        """Test filter functionality."""
        # Create mock callbacks
        on_search = MagicMock()
        on_filter = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            on_filter=on_filter,
            filter_options=["all", "option1", "option2"]
        )
        
        # Set filter value
        component.filter_var.set("option1")
        
        # Trigger filter
        component._on_filter_changed()
        
        # Verify callback called
        on_filter.assert_called_once_with("option1")
        
    def test_entry_focus(self, root, mock_controller):
        """Test entry focus events."""
        # Create mock callback
        on_search = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            placeholder="Test Placeholder"
        )
        
        # Verify initial state
        assert component.search_var.get() == "Test Placeholder"
        
        # Create mock event
        event = MagicMock()
        
        # Trigger focus in
        component._on_entry_focus_in(event)
        
        # Verify placeholder cleared
        assert component.search_var.get() == ""
        
        # Set search text
        component.search_var.set("test search")
        
        # Trigger focus out
        component._on_entry_focus_out(event)
        
        # Verify search text preserved
        assert component.search_var.get() == "test search"
        
        # Clear search text
        component.search_var.set("")
        
        # Trigger focus out
        component._on_entry_focus_out(event)
        
        # Verify placeholder restored
        assert component.search_var.get() == "Test Placeholder"
        
    def test_get_search_text(self, root, mock_controller):
        """Test getting search text."""
        # Create mock callback
        on_search = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            placeholder="Test Placeholder"
        )
        
        # Verify initial state
        assert component.get_search_text() == ""
        
        # Set search text
        component.search_var.set("test search")
        
        # Verify search text
        assert component.get_search_text() == "test search"
        
        # Set placeholder
        component.search_var.set("Test Placeholder")
        
        # Verify search text
        assert component.get_search_text() == ""
        
    def test_get_filter_value(self, root, mock_controller):
        """Test getting filter value."""
        # Create mock callbacks
        on_search = MagicMock()
        on_filter = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            on_filter=on_filter,
            filter_options=["all", "option1", "option2"]
        )
        
        # Verify initial state
        assert component.get_filter_value() == "all"
        
        # Set filter value
        component.filter_var.set("option1")
        
        # Verify filter value
        assert component.get_filter_value() == "option1"
        
    def test_clear(self, root, mock_controller):
        """Test clearing search and filter."""
        # Create mock callbacks
        on_search = MagicMock()
        on_filter = MagicMock()
        
        # Create component
        component = SearchFilterBar(
            root,
            mock_controller,
            on_search=on_search,
            on_filter=on_filter,
            filter_options=["all", "option1", "option2"],
            placeholder="Test Placeholder"
        )
        
        # Set search text and filter value
        component.search_var.set("test search")
        component.filter_var.set("option1")
        
        # Clear component
        component.clear()
        
        # Verify state
        assert component.search_var.get() == "Test Placeholder"
        assert component.filter_var.get() == "all"

