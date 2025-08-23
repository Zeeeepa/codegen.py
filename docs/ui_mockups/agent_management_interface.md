# Agent Management Interface UI Mockups

## Main Dashboard Layout

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               |                                       |
|               |                                       |
|  Navigation   |  Main Content Area                    |
|  Sidebar      |                                       |
|               |                                       |
|               |                                       |
|               |                                       |
|               |                                       |
+---------------+---------------------------------------+
|                  Status Bar                           |
+-------------------------------------------------------+
```

The main dashboard provides a central hub for managing all agent-related activities:

- **Header**: Contains organization selector, user profile, theme toggle, and global actions
- **Navigation Sidebar**: Quick access to all main sections of the application
- **Main Content Area**: Dynamic content based on the selected section
- **Status Bar**: Shows current status, API connection info, and notifications

## Navigation Sidebar

```
+-----------------------------------+
| CODEGEN                           |
+-----------------------------------+
| 📊 Dashboard                      |
| 🤖 Agent Runs                     |
| ⭐ Starred Runs                   |
| 🔄 Multi-Run Agent                |
| 📁 Projects                       |
| ⚙️ Settings                       |
+-----------------------------------+
|                                   |
| Organization: [Dropdown ▼]        |
|                                   |
+-----------------------------------+
```

## Agent Runs List View

```
+-------------------------------------------------------+
| Agent Runs                                    [+ New] |
+-------------------------------------------------------+
| Search: [                    ]  Filter: [Status ▼]    |
+-------------------------------------------------------+
|  +-------------------+  +-------------------+         |
|  | Agent Run #1234   |  | Agent Run #5678   |         |
|  | ✅ Completed      |  | ⏳ Running        |         |
|  | Created: 2h ago   |  | Created: 10m ago  |         |
|  | Repo: example-repo|  | Repo: test-repo   |         |
|  | [View] [Resume]   |  | [View] [Cancel]   |         |
|  +-------------------+  +-------------------+         |
|                                                       |
|  +-------------------+  +-------------------+         |
|  | Agent Run #9012   |  | Agent Run #3456   |         |
|  | ❌ Failed         |  | ✅ Completed      |         |
|  | Created: 1d ago   |  | Created: 3h ago   |         |
|  | Repo: demo-repo   |  | Repo: sample-repo |         |
|  | [View] [Resume]   |  | [View] [Resume]   |         |
|  +-------------------+  +-------------------+         |
|                                                       |
| [< Prev]                                    [Next >]  |
+-------------------------------------------------------+
```

The Agent Runs list view displays all agent runs with key information:
- Status indicators (Completed, Running, Failed)
- Creation time
- Associated repository
- Quick actions (View, Resume, Cancel)
- Pagination controls
- Search and filter capabilities

## Agent Run Detail View

```
+-------------------------------------------------------+
| Agent Run #1234                            [⭐ Star]  |
+-------------------------------------------------------+
| Status: ✅ Completed | Created: 2023-08-22 10:30 AM   |
| Repository: example-repo | Model: gpt-4               |
+-------------------------------------------------------+
| [Logs] [Results] [Pull Requests] [Settings]           |
+-------------------------------------------------------+
|                                                       |
|                                                       |
|                 Selected Tab Content                  |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
+-------------------------------------------------------+
| [Resume Run] [Copy Result] [Export Logs]              |
+-------------------------------------------------------+
```

The Agent Run Detail view provides comprehensive information about a specific agent run:
- Tabbed interface for different types of information (Logs, Results, PRs)
- Status information and metadata
- Actions for interacting with the run (Resume, Copy, Export)
- Star button for adding to starred runs

### Logs Tab

```
+-------------------------------------------------------+
| Logs                                    [Auto-scroll] |
+-------------------------------------------------------+
| [All] [Actions] [Errors] [Thoughts] [Final Answer]    |
+-------------------------------------------------------+
|                                                       |
| [10:30:15] ACTION: ripgrep_search                     |
| Thought: I need to search for the user's function     |
| Tool Input: { "query": "getUserData" }                |
| Tool Output: { "matches": 3, "files": ["src/user.js"] }|
|                                                       |
| [10:30:18] THOUGHT: I found the function in user.js   |
| I need to examine it to understand its structure.     |
|                                                       |
| [10:30:20] ACTION: file_read                          |
| Tool Input: { "path": "src/user.js" }                 |
| Tool Output: { "content": "function getUserData..." } |
|                                                       |
+-------------------------------------------------------+
```

The Logs tab shows a chronological view of the agent's execution:
- Timestamped entries
- Color-coded by type (Action, Thought, Error)
- Expandable details for tool inputs/outputs
- Filtering options
- Auto-scroll toggle for live updates

## Multi-Run Agent Interface

```
+-------------------------------------------------------+
| Multi-Run Agent                                       |
+-------------------------------------------------------+
| Prompt:                                               |
| [                                                   ] |
| [                                                   ] |
| [                                                   ] |
+-------------------------------------------------------+
| Repository: [Select Repository ▼]                     |
| Model: [Select Model ▼]                               |
+-------------------------------------------------------+
| Concurrency: [1] [2] [3] [4] [5] [6] [7] [8] [9] [10] |
| Temperature: [0.0 ----O---- 1.0]                      |
+-------------------------------------------------------+
| [Advanced Settings ▼]                                 |
+-------------------------------------------------------+
|                                                       |
| [Run Multi-Agent]                                     |
+-------------------------------------------------------+
```

When expanded:

```
+-------------------------------------------------------+
| [Advanced Settings ▲]                                 |
+-------------------------------------------------------+
| Synthesis Temperature: [0.0 --O------ 1.0]            |
| [✓] Use Custom Synthesis Prompt                       |
|                                                       |
| Custom Synthesis Prompt:                              |
| [                                                   ] |
| [                                                   ] |
+-------------------------------------------------------+
```

The Multi-Run Agent interface allows running multiple agent instances concurrently:
- Prompt input
- Repository and model selection
- Concurrency control (1-20)
- Temperature settings
- Advanced options for synthesis customization

### Multi-Run Results View

```
+-------------------------------------------------------+
| Results                                               |
+-------------------------------------------------------+
| Final Synthesized Output:                     [Copy]  |
| +---------------------------------------------------+ |
| |                                                   | |
| |                                                   | |
| |                                                   | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
| Candidate Outputs (3):                                |
| +---------------------------------------------------+ |
| | Candidate 1                                [Copy] | |
| | ...                                               | |
| +---------------------------------------------------+ |
| +---------------------------------------------------+ |
| | Candidate 2                                [Copy] | |
| | ...                                               | |
| +---------------------------------------------------+ |
| +---------------------------------------------------+ |
| | Candidate 3                                [Copy] | |
| | ...                                               | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
| Agent Runs:                                           |
| +-------------+ +-------------+ +-------------+       |
| | Run #1      | | Run #2      | | Run #3      |       |
| | ✅ Completed | | ✅ Completed | | ✅ Completed |       |
| | [View]      | | [View]      | | [View]      |       |
| +-------------+ +-------------+ +-------------+       |
+-------------------------------------------------------+
```

The Multi-Run Results view displays the synthesized output and individual results:
- Final synthesized output with copy button
- Expandable candidate outputs from each run
- Links to individual agent runs for detailed inspection

## Starred Runs View

```
+-------------------------------------------------------+
| ⭐ Starred Runs                                       |
+-------------------------------------------------------+
| Search: [                    ]  Filter: [Status ▼]    |
+-------------------------------------------------------+
|  +-------------------+  +-------------------+         |
|  | Agent Run #1234 ⭐ |  | Agent Run #5678 ⭐ |         |
|  | ✅ Completed      |  | ⏳ Running        |         |
|  | Created: 2h ago   |  | Created: 10m ago  |         |
|  | Repo: example-repo|  | Repo: test-repo   |         |
|  | [View] [Resume]   |  | [View] [Cancel]   |         |
|  +-------------------+  +-------------------+         |
|                                                       |
|  +-------------------+  +-------------------+         |
|  | Agent Run #9012 ⭐ |  | Agent Run #3456 ⭐ |         |
|  | ❌ Failed         |  | ✅ Completed      |         |
|  | Created: 1d ago   |  | Created: 3h ago   |         |
|  | Repo: demo-repo   |  | Repo: sample-repo |         |
|  | [View] [Resume]   |  | [View] [Resume]   |         |
|  +-------------------+  +-------------------+         |
+-------------------------------------------------------+
```

The Starred Runs view shows all agent runs that have been starred for quick access:
- Similar layout to the main Agent Runs view
- Star indicator on each card
- Ability to unstar runs
- Search and filter capabilities

## Create Agent Run View

```
+-------------------------------------------------------+
| Create Agent Run                                      |
+-------------------------------------------------------+
| Prompt:                                               |
| [                                                   ] |
| [                                                   ] |
| [                                                   ] |
+-------------------------------------------------------+
| Repository: [Select Repository ▼]                     |
| Model: [Select Model ▼]                               |
+-------------------------------------------------------+
| Temperature: [0.0 ----O---- 1.0]                      |
+-------------------------------------------------------+
| [Advanced Settings ▼]                                 |
+-------------------------------------------------------+
|                                                       |
| [Create Agent Run]                                    |
+-------------------------------------------------------+
```

The Create Agent Run view provides a form for creating a new agent run:
- Prompt input
- Repository and model selection
- Temperature setting
- Advanced options
- Create button

## Mobile View

On mobile devices, the layout adapts to a more compact format:

```
+-------------------------------------------------------+
| CODEGEN                                  [≡] [👤]     |
+-------------------------------------------------------+
| [Dashboard] [Agents] [Starred] [Multi] [More ▼]       |
+-------------------------------------------------------+
|                                                       |
|                                                       |
|                                                       |
|                                                       |
|                 Current Tab Content                   |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
+-------------------------------------------------------+
```

The mobile view features:
- Collapsible header with hamburger menu
- Horizontal navigation tabs for main sections
- Responsive content area that adapts to screen size
- Touch-friendly controls and card layouts

## Dark Mode

All UI components support both light and dark modes:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|  Navigation   |  Main Content Area                    |
|  Sidebar      |  (Dark Background)                    |
|  (Dark)       |                                       |
|               |                                       |
+---------------+---------------------------------------+
```

Dark mode features:
- Dark backgrounds with light text
- Adjusted color palette for better contrast
- Preserved status color indicators (green for success, red for error)
- Automatic switching based on system preferences or manual toggle

