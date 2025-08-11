"""
Business Logic Layer

This layer implements workspace management, templates, workflows, and AI-powered
features from PR 9. It uses the integration layer for API operations but remains
UI-agnostic, allowing multiple presentation interfaces to use the same logic.
"""

from .workspace_manager import WorkspaceManager
from .template_engine import TemplateEngine
from .workflow_orchestrator import WorkflowOrchestrator
from .analytics_engine import AnalyticsEngine
from .ai_features import AIFeatures

__all__ = [
    'WorkspaceManager',
    'TemplateEngine',
    'WorkflowOrchestrator', 
    'AnalyticsEngine',
    'AIFeatures'
]

