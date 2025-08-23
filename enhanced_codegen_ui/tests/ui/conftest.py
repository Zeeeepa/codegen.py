"""
Conftest for UI tests.

This module provides fixtures for UI tests.
"""

import pytest
import os
from unittest.mock import MagicMock

# Import the skip decorator from the components conftest
from enhanced_codegen_ui.tests.ui.components.conftest import skip_ui_tests

# Create a fixture to skip all UI tests
@pytest.fixture(autouse=True)
def skip_ui_tests_fixture():
    """
    Skip UI tests in headless environments.
    
    This fixture is automatically used for all tests in this directory.
    """
    if "DISPLAY" not in os.environ or os.environ.get("CI") == "true":
        pytest.skip("UI tests require a display and cannot run in headless environments")

@pytest.fixture
def mock_frame():
    """
    Create a mock frame for UI tests.
    
    Returns:
        MagicMock: Mock frame
    """
    frame = MagicMock()
    frame.winfo_width = MagicMock(return_value=800)
    frame.winfo_height = MagicMock(return_value=600)
    return frame

@pytest.fixture
def mock_main_window():
    """
    Create a mock main window for UI tests.
    
    Returns:
        MagicMock: Mock main window
    """
    window = MagicMock()
    window.root = MagicMock()
    window.frames = {}
    window.current_frame = None
    window.show_frame = MagicMock()
    return window
