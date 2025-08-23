"""
Pytest configuration for Enhanced Codegen UI tests.

This module provides fixtures and configuration for pytest tests.
"""

import os
import sys
import pytest
try:
    import tkinter as tk
except ImportError:
    # Mock tkinter for environments where it's not available
    from unittest.mock import MagicMock
    tk = MagicMock()
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Generator, Callable

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from enhanced_codegen_ui.core.controller import Controller
from enhanced_codegen_ui.core.events import EventBus, EventType, Event
from enhanced_codegen_ui.core.state import State


@pytest.fixture
def event_bus() -> EventBus:
    """
    Create a test event bus.
    
    Returns:
        EventBus: Test event bus
    """
    return EventBus()


@pytest.fixture
def state() -> State:
    """
    Create a test state.
    
    Returns:
        State: Test state
    """
    return State()


@pytest.fixture
def mock_controller() -> MagicMock:
    """
    Create a mock controller.
    
    Returns:
        MagicMock: Mock controller
    """
    controller = MagicMock(spec=Controller)
    
    # Create a mock event bus with the necessary methods
    event_bus = MagicMock()
    event_bus.subscribe = MagicMock(return_value="subscription-id")
    event_bus.unsubscribe = MagicMock(return_value=True)
    event_bus.publish = MagicMock()
    
    # Create a mock state
    state = MagicMock()
    
    # Assign to controller
    controller.event_bus = event_bus
    controller.state = state
    
    return controller


@pytest.fixture
def root() -> Generator[Any, None, None]:
    """
    Create a Tkinter root window for testing.
    
    Yields:
        tk.Tk or MagicMock: Tkinter root window or mock
    """
    try:
        # Try to create a real Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        yield root
        root.destroy()
    except (ImportError, tk.TclError):
        # If Tkinter is not available or fails, use a mock
        mock_root = MagicMock()
        # Add common methods that tests might use
        mock_root.after = MagicMock(return_value=1)  # Return an ID for after() calls
        mock_root.after_cancel = MagicMock()
        mock_root.destroy = MagicMock()
        mock_root.update = MagicMock()
        mock_root.update_idletasks = MagicMock()
        mock_root.winfo_width = MagicMock(return_value=800)
        mock_root.winfo_height = MagicMock(return_value=600)
        yield mock_root


@pytest.fixture
def event_callback() -> Callable[[Event], None]:
    """
    Create a callback function for events.
    
    Returns:
        Callable: Event callback function
    """
    def callback(event: Event) -> None:
        callback.called = True
        callback.event = event
        
    callback.called = False
    callback.event = None
    return callback


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """
    Create a mock API response.
    
    Returns:
        Dict[str, Any]: Mock API response
    """
    return {
        "id": "test-id",
        "status": "success",
        "data": {
            "key": "value"
        }
    }


@pytest.fixture
def patch_after() -> Generator[None, None, None]:
    """
    Patch the tkinter after method to prevent scheduling.
    
    Yields:
        None
    """
    with patch.object(tk.Misc, 'after', return_value=1):
        yield


@pytest.fixture
def patch_messagebox() -> Generator[MagicMock, None, None]:
    """
    Patch the tkinter messagebox to prevent showing dialogs.
    
    Yields:
        MagicMock: Mock messagebox
    """
    with patch('tkinter.messagebox.askyesno', return_value=True) as mock:
        yield mock
