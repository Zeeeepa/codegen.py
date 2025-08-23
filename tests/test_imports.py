"""
Test imports from the restructured project.
"""

import pytest


def test_backend_imports():
    """Test importing backend modules."""
    from backend import ClientConfig, ConfigPresets, APIError
    from backend.client import AgentEndpoint, RunEndpoint, WebhookEndpoint
    from backend.core import ClientConfig, ConfigPresets
    from backend.api import app, app_complete, MultiRunProcessor, WebSocketManager
    
    assert ClientConfig is not None
    assert ConfigPresets is not None
    assert APIError is not None
    assert AgentEndpoint is not None
    assert RunEndpoint is not None
    assert WebhookEndpoint is not None
    assert app is not None
    assert app_complete is not None
    assert MultiRunProcessor is not None
    assert WebSocketManager is not None


def test_frontend_imports():
    """Test importing frontend modules."""
    from frontend import EventBus, StateManager
    from frontend.components import Button, InputField, OutputDisplay
    from frontend.views import MainFrame, AgentFrame, RunFrame
    from frontend.utils import theme, validation
    
    assert EventBus is not None
    assert StateManager is not None
    assert Button is not None
    assert InputField is not None
    assert OutputDisplay is not None
    assert MainFrame is not None
    assert AgentFrame is not None
    assert RunFrame is not None
    assert theme is not None
    assert validation is not None

