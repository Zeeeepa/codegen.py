"""
Conftest for UI component tests.

This module provides fixtures for UI component tests.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Define a decorator to skip UI tests in headless environments
skip_ui_tests = pytest.mark.skipif(
    "DISPLAY" not in os.environ or os.environ.get("CI") == "true",
    reason="UI tests require a display and cannot run in headless environments"
)

# Create a fixture to skip all UI component tests
@pytest.fixture(autouse=True)
def skip_ui_component_tests():
    """
    Skip UI component tests in headless environments.
    
    This fixture is automatically used for all tests in this directory.
    """
    if "DISPLAY" not in os.environ or os.environ.get("CI") == "true":
        pytest.skip("UI tests require a display and cannot run in headless environments")
    
@pytest.fixture
def mock_parent():
    """
    Create a mock parent widget for UI tests.
    
    Returns:
        MagicMock: Mock parent widget
    """
    parent = MagicMock()
    parent.winfo_width = MagicMock(return_value=800)
    parent.winfo_height = MagicMock(return_value=600)
    return parent
