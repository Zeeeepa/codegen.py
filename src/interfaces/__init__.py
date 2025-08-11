"""
Core Architecture Interfaces

This module defines the abstract interfaces that separate concerns between
the three main architectural layers:
1. Codegen Integration Layer - API client and data access
2. Business Logic Layer - Workspace, templates, workflows
3. User Interface Layer - CLI, web dashboard, reporting

These interfaces ensure loose coupling and enable multiple implementations
of each layer without affecting others.
"""

from .codegen_integration import (
    ICodegenClient,
    IAuthManager,
    ICacheManager,
    IDataTransformer
)

from .business_logic import (
    IWorkspaceManager,
    ITemplateEngine,
    IWorkflowOrchestrator,
    IAnalyticsEngine,
    IAIFeatures
)

from .ui_layer import (
    ICommandParser,
    IOutputFormatter,
    IProgressDisplay,
    IInteractivePrompts,
    IUserInterface
)

from .events import (
    IEventBus,
    IEventHandler,
    Event,
    EventType
)

__all__ = [
    # Integration Layer
    'ICodegenClient',
    'IAuthManager', 
    'ICacheManager',
    'IDataTransformer',
    
    # Business Logic Layer
    'IWorkspaceManager',
    'ITemplateEngine',
    'IWorkflowOrchestrator',
    'IAnalyticsEngine',
    'IAIFeatures',
    
    # UI Layer
    'ICommandParser',
    'IOutputFormatter',
    'IProgressDisplay',
    'IInteractivePrompts',
    'IUserInterface',
    
    # Events
    'IEventBus',
    'IEventHandler',
    'Event',
    'EventType'
]

