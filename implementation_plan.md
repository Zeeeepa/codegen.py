# Codegen UI Implementation Plan

## Overview

After analyzing the codebase, I've identified multiple UI implementations with overlapping functionality. This plan outlines the approach to consolidate these implementations into a single, comprehensive Tkinter UI that meets all requirements.

## Feature Matrix

| Feature | codegen_ui | enhanced_codegen_ui | enhanced_ui | ui |
|---------|------------|---------------------|-------------|-----|
| Agent Runs List | ✅ | ✅ | ✅ | ✅ |
| Agent Run Detail | ✅ | ✅ | ✅ | ✅ |
| Live Logs | ✅ | ✅ | ✅ | ✅ |
| Tools Used | ❌ | ✅ | ✅ | ✅ |
| Timeline | ❌ | ✅ | ✅ | ✅ |
| Create Agent Run | ✅ | ✅ | ✅ | ✅ |
| ProRun Mode | ❌ | ❌ | ✅ | ✅ |
| Starred Runs | ❌ | ✅ | ✅ | ✅ |
| Projects | ✅ | ✅ | ✅ | ✅ |
| Templates | ❌ | ❌ | ✅ | ✅ |
| Settings | ❌ | ✅ | ✅ | ✅ |
| CLI Integration | ❌ | ❌ | ✅ | ✅ |

## Consolidation Approach

Based on the feature matrix, I'll use the `enhanced_ui` implementation as the base since it has the most complete feature set and aligns best with the mockups. The consolidation will follow these steps:

1. **Create Unified API Client**
   - Use `codegen_ui_new/api_client.py` as the base
   - Ensure all required endpoints are supported
   - Implement robust error handling and authentication

2. **Consolidate Core Components**
   - Use `enhanced_ui/application.py` as the main application entry point
   - Consolidate event system from `enhanced_ui/core/events.py`
   - Consolidate state management from `enhanced_ui/core/state.py`

3. **Implement UI Components**
   - Create main window with navigation sidebar
   - Implement agent runs tab with list view and filtering
   - Implement agent run detail view with live logs, tools used, and timeline
   - Implement create new run dialog with ProRun mode
   - Implement starred runs dashboard
   - Implement projects tab with setup commands
   - Implement templates management
   - Implement settings tab

4. **Add ProRun Mode**
   - Implement ProRun configuration in create new run dialog
   - Add agent model selectors
   - Add synthesis template selection
   - Implement save/load ProRun configuration

5. **Implement CLI Integration**
   - Add CLI command generation
   - Add CLI command builder
   - Add copy to clipboard functionality

## Implementation Details

### Main Application Structure

```python
class CodegenApplication:
    def __init__(self):
        # Initialize controller and API client
        self.config = Config()
        self.api_client = APIClient(self.config)
        self.controller = Controller(self.api_client)
        
        # Initialize UI
        self.root = tk.Tk()
        self.root.title("Codegen Agent API")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set theme and styles
        self._configure_styles()
        
        # Create main window
        self.main_window = MainWindow(self.root, self.controller)
        
        # Set up event handlers
        self._setup_event_handlers()
```

### Navigation Structure

```python
class MainWindow:
    def __init__(self, root, controller):
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.header = Header(self.main_frame, controller)
        self.header.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create sidebar
        self.sidebar = Sidebar(self.content_frame, controller)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, PADDING))
        
        # Create main content area
        self.content_area = ttk.Frame(self.content_frame)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create frames
        self.agent_runs_frame = AgentRunsFrame(self.content_area, controller)
        self.agent_run_detail_frame = AgentRunDetailFrame(self.content_area, controller)
        self.starred_dashboard_frame = StarredDashboardFrame(self.content_area, controller)
        self.projects_frame = ProjectsFrame(self.content_area, controller)
        self.templates_frame = TemplatesFrame(self.content_area, controller)
        self.settings_frame = SettingsFrame(self.content_area, controller)
        
        # Create status bar
        self.status_bar = StatusBar(self.main_frame, controller)
        self.status_bar.pack(fill=tk.X, padx=PADDING, pady=PADDING)
```

### Agent Runs Tab

```python
class AgentRunsFrame:
    def __init__(self, parent, controller):
        # Create filter bar
        self.filter_bar = FilterBar(self, controller)
        self.filter_bar.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create agent runs list
        self.agent_runs_list = AgentRunsList(self, controller)
        self.agent_runs_list.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create pagination
        self.pagination = Pagination(self, controller)
        self.pagination.pack(fill=tk.X, padx=PADDING, pady=PADDING)
```

### Create New Run Dialog

```python
class CreateRunDialog:
    def __init__(self, parent, controller):
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Agent Run")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create project selection
        self.project_selection = ProjectSelection(self.dialog, controller)
        self.project_selection.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create template selection
        self.template_selection = TemplateSelection(self.dialog, controller)
        self.template_selection.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create model selection
        self.model_selection = ModelSelection(self.dialog, controller)
        self.model_selection.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create ProRun mode
        self.prorun_mode = ProRunMode(self.dialog, controller)
        self.prorun_mode.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Create prompt input
        self.prompt_input = PromptInput(self.dialog, controller)
        self.prompt_input.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Create buttons
        self.buttons = ButtonFrame(self.dialog, controller)
        self.buttons.pack(fill=tk.X, padx=PADDING, pady=PADDING)
```

## Testing Strategy

1. **Unit Tests**
   - Test API client functionality
   - Test event system
   - Test state management
   - Test UI components

2. **Integration Tests**
   - Test API client with mock server
   - Test UI components with mock controller
   - Test end-to-end workflows

3. **Manual Testing**
   - Test all UI components
   - Test all workflows
   - Test error handling
   - Test edge cases

## Timeline

1. **Phase 1: Core Infrastructure (1-2 days)**
   - Create unified API client
   - Implement event system
   - Implement state management

2. **Phase 2: Main UI Components (2-3 days)**
   - Implement main window
   - Implement navigation
   - Implement agent runs tab
   - Implement agent run detail view

3. **Phase 3: Advanced Features (2-3 days)**
   - Implement create new run dialog
   - Implement ProRun mode
   - Implement starred runs dashboard
   - Implement projects tab

4. **Phase 4: Additional Features (1-2 days)**
   - Implement templates management
   - Implement settings tab
   - Implement CLI integration

5. **Phase 5: Testing and Refinement (1-2 days)**
   - Test all functionality
   - Fix bugs
   - Refine UI
   - Add documentation

