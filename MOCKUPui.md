# Codegen Agent API UI Mockups

This document provides comprehensive UI mockups for the Codegen Agent API UI implementation. The mockups illustrate the visual design and user interaction patterns for all major features, with a focus on detailed agent run status displays and live streaming of actions.

## Table of Contents

1. [Main Application Layout](#main-application-layout)
2. [Navigation Structure](#navigation-structure)
3. [Agent Runs Tab](#agent-runs-tab)
4. [Agent Run Detail View](#agent-run-detail-view)
5. [Create New Run Dialog](#create-new-run-dialog)
6. [Starred Runs Dashboard](#starred-runs-dashboard)
7. [Projects Tab](#projects-tab)
8. [Prompt Templates Management](#prompt-templates-management)
9. [Settings Tab](#settings-tab)
10. [CLI Integration](#cli-integration)
11. [Function Flows](#function-flows)

## Main Application Layout

The main application layout consists of a header showing active agent runs with detailed status, a navigation sidebar, and a content area.

```
+--------------------------------------------------------------+
|                          Header                              |
| Active Runs: [run-123: ACTION: file_write ▶] [run-124 ✓] [+] |
| [Create New Run]                                             |
+---------------+--------------------------------------------+
|               |                                            |
| Navigation    |                                            |
| Sidebar       |                                            |
|               |                                            |
| [🤖 Agent Runs]|                                            |
| [📁 Projects] |                Content Area                |
| [⭐ Starred   |                                            |
|    Dashboard] |                                            |
| [📝 Templates]|                                            |
| [⚙️ Settings] |                                            |
|               |                                            |
|               |                                            |
+---------------+--------------------------------------------+
|  Status: Connected to API | Organization: Org1              |
+--------------------------------------------------------------+
```

## Navigation Structure

The navigation sidebar provides access to the main sections of the application.

```
+------------------------+
| 🤖 Agent Runs          |
| 📁 Projects            |
| ⭐ Starred Dashboard   |
| 📝 Templates           |
| ⚙️ Settings            |
+------------------------+
```

## Agent Runs Tab

The Agent Runs tab displays a list of agent runs with their detailed status and allows starring runs.

```
+--------------------------------------------------------------+
| Agent Runs                                [Create New Run]   |
+--------------------------------------------------------------+
| Filter: [All ▼] | Status: [All ▼] | Search: [          🔍]  |
+--------------------------------------------------------------+
| ID        | Prompt      | Status                | Actions    |
+--------------------------------------------------------------+
| run-123   | Fix bug in  | ACTION: file_write    | [⭐] [⏹️]  |
|           | login form  |                       | [👁️] [⋮]   |
+--------------------------------------------------------------+
| run-124   | Add feature | COMPLETED             | [☆] [▶️]   |
|           | to dashboard|                       | [👁️] [⋮]   |
+--------------------------------------------------------------+
| run-125   | Refactor    | ERROR: file_write     | [☆] [▶️]   |
|           | API client  |                       | [👁️] [⋮]   |
+--------------------------------------------------------------+
| run-126   | Create unit | PLAN_EVALUATION       | [☆] [⏹️]  |
|           | tests       |                       | [👁️] [⋮]   |
+--------------------------------------------------------------+
|                                                              |
|                      [Load More]                             |
+--------------------------------------------------------------+
```

## Agent Run Detail View

When clicking on the view (👁️) button for an agent run, a detailed view is shown with live streaming logs:

```
+--------------------------------------------------------------+
| ← Back to Agent Runs                           [Refresh]     |
+--------------------------------------------------------------+
| Agent Run: run-123 - Current Status: ACTION: file_write      |
+--------------------------------------------------------------+
| [Details] [Live Logs] [Output] [Tools Used] [Timeline]       |
+--------------------------------------------------------------+
|                                                              |
| Live Logs:                                                   |
|                                                              |
| 🔵 ACTION: ripgrep_search                                    |
| 💭 Thought: I need to search for the user's function         |
| ⚙️ Input: {"query": "function getUserData",                  |
|           "file_extensions": [".js", ".ts"]}                 |
| 📊 Output: {"matches": 3, "files": ["src/user.js"]}          |
|                                                              |
| 🟢 PLAN_EVALUATION                                           |
| 💭 Thought: I found the function in src/user.js. I need to   |
|            fix the password reset logic to handle special    |
|            characters properly.                              |
|                                                              |
| 🔵 ACTION: file_write                                        |
| 💭 Thought: I need to fix the password reset function        |
| ⚙️ Input: {"filepath": "src/user.js",                        |
|           "content": "...updated code..."}                   |
| 📊 Output: {"status": "success"}                             |
|                                                              |
| 🟢 PLAN_EVALUATION                                           |
| 💭 Thought: Now I need to test if the fix works properly     |
|                                                              |
| [LIVE] Waiting for next action...                            |
|                                                              |
+--------------------------------------------------------------+
| [Resume Run] [Stop Run] [Star Run] [Filter: All ▼]           |
+--------------------------------------------------------------+
```

### Tools Used Tab

The Tools Used tab shows a summary of all tools used in the agent run:

```
+--------------------------------------------------------------+
| ← Back to Agent Runs                           [Refresh]     |
+--------------------------------------------------------------+
| Agent Run: run-123 - Current Status: ACTION: file_write      |
+--------------------------------------------------------------+
| [Details] [Live Logs] [Output] [Tools Used] [Timeline]       |
+--------------------------------------------------------------+
|                                                              |
| Tools Used:                                                  |
|                                                              |
| Tool Name       | Count | Success | Failed                   |
| --------------- | ----- | ------- | ------                   |
| ripgrep_search  |   3   |    3    |   0                      |
| file_write      |   2   |    2    |   0                      |
| file_read       |   1   |    1    |   0                      |
| run_command     |   1   |    1    |   0                      |
|                                                              |
| Total Tools Used: 4                                          |
| Total Actions: 7                                             |
|                                                              |
+--------------------------------------------------------------+
| [Resume Run] [Stop Run] [Star Run]                           |
+--------------------------------------------------------------+
```

### Timeline Tab

The Timeline tab shows a visual timeline of the agent run:

```
+--------------------------------------------------------------+
| ← Back to Agent Runs                           [Refresh]     |
+--------------------------------------------------------------+
| Agent Run: run-123 - Current Status: ACTION: file_write      |
+--------------------------------------------------------------+
| [Details] [Live Logs] [Output] [Tools Used] [Timeline]       |
+--------------------------------------------------------------+
|                                                              |
| Timeline:                                                    |
|                                                              |
| |----------|----------|----------|----------|----------|     |
| ●          ●          ●●         ●          ●●         ●     |
| START    file_read  ripgrep   PLAN_EVAL  file_write  PLAN_EV |
|                                                              |
| Current Duration: 5m 10s                                     |
| Estimated Completion: ~2m remaining                          |
|                                                              |
+--------------------------------------------------------------+
| [Resume Run] [Stop Run] [Star Run]                           |
+--------------------------------------------------------------+
```

## Create New Run Dialog

When clicking on the "Create New Run" button, a dialog opens to create a new agent run:

```
+--------------------------------------------------------------+
|                     Create New Agent Run                     |
+--------------------------------------------------------------+
|                                                              |
| GitHub Project (Optional):                                   |
| [Select Project ▼]                                           |
|                                                              |
| Prompt Template (Optional):                                  |
| [Select Template ▼]                                          |
|                                                              |
| Model:                                                       |
| [Select Model ▼]                                             |
|   OpenAI:                                                    |
|   - GPT-5                                                    |
|   - GPT-4.1                                                  |
|   - O3                                                       |
|   - O4 Mini                                                  |
|                                                              |
|   ANTHROPIC:                                                 |
|   - CLAUDE SONNET 4                                          |
|   - CLAUDE SONNET 3.7                                        |
|   - CLAUDE SONNET 3.5                                        |
|                                                              |
|   Google:                                                    |
|   - Gemini 2.5                                               |
|                                                              |
| [✓] ProRun Mode                                              |
|                                                              |
| ProRun Saved Configuration: [Select Configuration ▼]         |
|                                                              |
| Generate multiple responses and synthesize best result       |
| Number of candidates: [10 ▼]                                 |
|                                                              |
| Agent 1: [CLAUDE SONNET 4 ▼]                                 |
| Agent 2: [GPT-5 ▼]                                           |
| Agent 3: [Gemini 2.5 ▼]                                      |
| Agent 4: [GPT-4.1 ▼]                                         |
| Agent 5: [CLAUDE SONNET 3.7 ▼]                               |
| Agent 6: [O3 ▼]                                              |
| Agent 7: [CLAUDE SONNET 3.5 ▼]                               |
| Agent 8: [O4 Mini ▼]                                         |
| Agent 9: [GPT-5 ▼]                                           |
| Agent 10: [CLAUDE SONNET 4 ▼]                                |
|                                                              |
| Synthesis Prompt Template: [Select Template ▼]               |
|                                                              |
| [Save ProRun Configuration]                                  |
|                                                              |
| Prompt:                                                      |
| +----------------------------------------------------------+ |
| |                                                          | |
| |                                                          | |
| |                                                          | |
| |                                                          | |
| +----------------------------------------------------------+ |
|                                                              |
+--------------------------------------------------------------+
| [Create Run] [Cancel] [CLI Command ▼]                        |
+--------------------------------------------------------------+
```

### Save ProRun Configuration Dialog

When clicking on the "Save ProRun Configuration" button, a dialog opens to save the current ProRun configuration:

```
+--------------------------------------------------------------+
|                  Save ProRun Configuration                   |
+--------------------------------------------------------------+
|                                                              |
| Configuration Name:                                          |
| [My Custom ProRun Config                               ]     |
|                                                              |
| Description (Optional):                                      |
| [Custom configuration with mixed models                ]     |
|                                                              |
| Configuration Details:                                       |
| - Number of candidates: 10                                   |
| - Agent models: CLAUDE SONNET 4, GPT-5, Gemini 2.5, ...      |
| - Synthesis template: Expert Synthesis                       |
|                                                              |
+--------------------------------------------------------------+
| [Save Configuration] [Cancel]                                |
+--------------------------------------------------------------+
```

### CLI Command Dropdown

When clicking on the "CLI Command" dropdown, it shows the equivalent CLI command:

```
+--------------------------------------------------------------+
| CLI Command:                                                 |
| codegen agent --prompt "Your prompt text" --prorun           |
| --candidates 10 --agent1 "claude-sonnet-4" --agent2 "gpt-5"  |
| --agent3 "gemini-2.5" --synthesis-template "expert-synthesis"|
+--------------------------------------------------------------+
| [Copy to Clipboard]                                          |
+--------------------------------------------------------------+
```

## Starred Runs Dashboard

The Starred Dashboard provides a view of all starred runs and projects, allowing you to manage and monitor them with detailed status information.

```
+--------------------------------------------------------------+
| Starred Dashboard                                            |
+--------------------------------------------------------------+
| [Starred Runs] [Starred Projects]                            |
+--------------------------------------------------------------+
|                                                              |
| +----------------------------------------------------------+ |
| | run-123                                                  | |
| | Prompt: Fix bug in login form                            | |
| | Status: ACTION: file_write                               | |
| | Project: repo-xyz                                        | |
| | Last Action: file_write to src/user.js                   | |
| | Progress: 4/7 steps completed                            | |
| |                                                          | |
| | [👁️ View Details] [⏹️ Stop Run] [☆ Unstar]               | |
| +----------------------------------------------------------+ |
|                                                              |
| +----------------------------------------------------------+ |
| | run-128                                                  | |
| | Prompt: Add dashboard feature                            | |
| | Status: COMPLETED                                        | |
| | Project: repo-abc                                        | |
| | Tools Used: 5 (ripgrep_search, file_write, run_command)  | |
| |                                                          | |
| | [👁️ View Details] [▶️ Resume Run] [☆ Unstar]             | |
| +----------------------------------------------------------+ |
|                                                              |
+--------------------------------------------------------------+
| [Assign to Project] [Resume Selected] [Stop Selected]        |
+--------------------------------------------------------------+
```

### Project Cards in Starred Dashboard

When viewing starred projects, each project card shows associated agent runs with detailed status:

```
+--------------------------------------------------------------+
| Starred Dashboard                                            |
+--------------------------------------------------------------+
| [Starred Runs] [Starred Projects]                            |
+--------------------------------------------------------------+
|                                                              |
| +----------------------------------------------------------+ |
| | Project: repo-xyz                                        | |
| | Description: Login API service                           | |
| | Setup Commands: ✓                                        | |
| |                                                          | |
| | Associated Agent Runs:                                   | |
| | • run-123: ACTION: file_write - Fix login bug            | |
| |   Last Action: file_write to src/user.js                 | |
| |                                                          | |
| | • run-128: COMPLETED - Add dashboard feature             | |
| |                                                          | |
| | [View Project] [Create New Run] [Unstar]                 | |
| +----------------------------------------------------------+ |
|                                                              |
+--------------------------------------------------------------+
| [Generate Setup Commands] [Create New Project]               |
+--------------------------------------------------------------+
```

## Projects Tab

The Projects tab displays a list of projects with indicators for those that have setup commands.

```
+--------------------------------------------------------------+
| Projects                                [Create New Run]     |
+--------------------------------------------------------------+
| Filter: [All ▼] | Setup Commands: [All ▼] | Search: [    🔍] |
+--------------------------------------------------------------+
| Name       | Description | Language | Setup Cmds | Actions   |
+--------------------------------------------------------------+
| repo-xyz   | Login API   | Python   | ✓          | [⭐] [👁️] |
|            | service     |          |            | [⚙️] [⋮]  |
+--------------------------------------------------------------+
| repo-abc   | User        | TypeScript| ✓          | [⭐] [👁️] |
|            | dashboard   |          |            | [⚙️] [⋮]  |
+--------------------------------------------------------------+
| repo-def   | Payment     | Go       | ✗          | [☆] [👁️] |
|            | processor   |          |            | [⚙️] [⋮]  |
+--------------------------------------------------------------+
| repo-ghi   | Analytics   | Python   | ✓          | [☆] [👁️] |
|            | service     |          |            | [⚙️] [⋮]  |
+--------------------------------------------------------------+
|                                                              |
|                      [Load More]                             |
+--------------------------------------------------------------+
```

### Project Detail View

When clicking on the view (👁️) button for a project, a detailed view is shown with associated agent runs and their detailed status:

```
+--------------------------------------------------------------+
| ← Back to Projects                             [Refresh]     |
+--------------------------------------------------------------+
| Project: repo-xyz                              [Create New Run]
+--------------------------------------------------------------+
| [Details] [Setup Commands] [Agent Runs]                      |
+--------------------------------------------------------------+
|                                                              |
| Name: repo-xyz                                               |
| Description: Login API service                               |
| Language: Python                                             |
| Visibility: Private                                          |
| Organization: Org1                                           |
|                                                              |
| Setup Commands:                                              |
| ```                                                          |
| pip install -r requirements.txt                              |
| python setup.py develop                                      |
| pre-commit install                                           |
| ```                                                          |
|                                                              |
| Associated Agent Runs:                                       |
| • run-123: ACTION: file_write - Fix login bug                |
|   Last Action: file_write to src/user.js                     |
|   [👁️ View Details] [⏹️ Stop Run]                            |
|                                                              |
| • run-128: COMPLETED - Add dashboard feature                 |
|   [👁️ View Details] [▶️ Resume Run]                          |
|                                                              |
+--------------------------------------------------------------+
| [Generate Setup Commands] [Create Agent Run] [Star Project]  |
+--------------------------------------------------------------+
```

## Prompt Templates Management

The Templates tab allows managing prompt templates for agent runs.

```
+--------------------------------------------------------------+
| Prompt Templates                                [+ Create]   |
+--------------------------------------------------------------+
| Filter: [All ▼] | Category: [All ▼] | Search: [        🔍]  |
+--------------------------------------------------------------+
| Name       | Description    | Category | Actions             |
+--------------------------------------------------------------+
| Bug Fix    | Template for   | Code     | [👁️] [✏️] [🗑️] [⋮]  |
|            | fixing bugs    |          |                     |
+--------------------------------------------------------------+
| Feature    | Template for   | Code     | [👁️] [✏️] [🗑️] [⋮]  |
| Addition   | adding features|          |                     |
+--------------------------------------------------------------+
| Code       | Template for   | Code     | [👁️] [✏️] [🗑️] [⋮]  |
| Review     | reviewing code |          |                     |
+--------------------------------------------------------------+
| Expert     | Template for   | Synthesis| [👁️] [✏️] [🗑️] [⋮]  |
| Synthesis  | ProRun synthesis|         |                     |
+--------------------------------------------------------------+
|                                                              |
|                      [Load More]                             |
+--------------------------------------------------------------+
```

### Template Editor

When creating or editing a template:

```
+--------------------------------------------------------------+
| ← Back to Templates                                          |
+--------------------------------------------------------------+
| Edit Template: Expert Synthesis                              |
+--------------------------------------------------------------+
|                                                              |
| Name: [Expert Synthesis                                 ]    |
| Category: [Synthesis ▼]                                      |
|                                                              |
| Description:                                                 |
| [Template for synthesizing multiple agent responses     ]    |
|                                                              |
| Template Content:                                            |
| +----------------------------------------------------------+ |
| | You are an expert editor. Synthesize ONE best answer     | |
| | from the candidate answers provided, merging strengths,  | |
| | correcting errors, and removing repetition.              | |
| |                                                          | |
| | {{agent_responses}}                                      | |
| |                                                          | |
| | Return the single best final answer.                     | |
| +----------------------------------------------------------+ |
|                                                              |
| Variables:                                                   |
| - agent_responses: The responses from all agents             |
|                                                              |
+--------------------------------------------------------------+
| [Save Template] [Cancel] [Test Template]                     |
+--------------------------------------------------------------+
```

## Settings Tab

The Settings tab allows configuring API tokens and other settings.

```
+--------------------------------------------------------------+
| Settings                                                     |
+--------------------------------------------------------------+
|                                                              |
| API Configuration:                                           |
|                                                              |
| CODEGEN_ORG_ID:                                              |
| [323                                                     ]   |
|                                                              |
| CODEGEN_API_TOKEN:                                           |
| [sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99                ]   |
|                                                              |
| GITHUB_TOKEN:                                                |
| [****************************************                ]   |
|                                                              |
| UI Settings:                                                 |
|                                                              |
| [✓] Auto-refresh agent runs                                  |
| [✓] Show notifications for completed runs                    |
| [✓] Show notifications for failed runs                       |
| [ ] Show timestamps in logs                                  |
|                                                              |
| Default Model:                                               |
| [CLAUDE SONNET 3.5 ▼]                                        |
|                                                              |
| ProRun Settings:                                             |
| [✓] Enable ProRun by default                                 |
| Default number of candidates: [10 ▼]                         |
| Default synthesis template: [Expert Synthesis ▼]             |
|                                                              |
| CLI Integration:                                             |
| [✓] Enable CLI integration                                   |
| CLI Path: [/usr/local/bin/codegen                       ]    |
|                                                              |
+--------------------------------------------------------------+
| [Save Settings] [Reset to Defaults]                          |
+--------------------------------------------------------------+
```

## CLI Integration

The UI provides integration with the Codegen CLI, allowing users to view and copy CLI commands for various actions.

### CLI Command Generation

When performing actions in the UI, equivalent CLI commands are displayed:

```
+--------------------------------------------------------------+
| Creating Agent Run                                           |
+--------------------------------------------------------------+
| Equivalent CLI Command:                                      |
| codegen agent --prompt "Fix the login form bug" --prorun     |
| --candidates 10 --agent1 "claude-sonnet-4" --agent2 "gpt-5"  |
| --synthesis-template "expert-synthesis"                      |
+--------------------------------------------------------------+
| [Copy to Clipboard] [Run in Terminal]                        |
+--------------------------------------------------------------+
```

### CLI Command Builder

A dedicated CLI command builder is available for advanced users:

```
+--------------------------------------------------------------+
| CLI Command Builder                                          |
+--------------------------------------------------------------+
|                                                              |
| Command: [agent ▼]                                           |
|                                                              |
| Options:                                                     |
| [✓] --prompt     ["Fix the login form bug"              ]    |
| [ ] --model      ["claude-sonnet-3.5"                   ]    |
| [✓] --repo-id    [123                                   ]    |
| [ ] --org-id     [                                      ]    |
| [✓] --prorun                                                 |
| [✓] --candidates [10                                    ]    |
| [✓] --agent1     ["claude-sonnet-4"                     ]    |
| [✓] --agent2     ["gpt-5"                               ]    |
| [✓] --synthesis-template ["expert-synthesis"            ]    |
|                                                              |
| Generated Command:                                           |
| codegen agent --prompt "Fix the login form bug" --repo-id 123|
| --prorun --candidates 10 --agent1 "claude-sonnet-4"          |
| --agent2 "gpt-5" --synthesis-template "expert-synthesis"     |
|                                                              |
+--------------------------------------------------------------+
| [Copy to Clipboard] [Run in Terminal] [Save as Alias]        |
+--------------------------------------------------------------+
```

## Function Flows

### Agent Run Creation Flow

```
+----------------+     +----------------+     +----------------+
| User clicks    |     | Create Agent   |     | User fills     |
| "Create New    |---->| Run dialog     |---->| form and       |
| Run" button    |     | opens          |     | submits        |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| API creates    |     | UI updates     |     | Agent run      |
| new agent run  |<----| to show        |<----| creation       |
| in backend     |     | progress       |     | request sent   |
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+     +----------------+
| Agent run      |     | UI streams     |     | User views     |
| executes in    |---->| logs in        |---->| detailed       |
| background     |     | real-time      |     | progress       |
+----------------+     +----------------+     +----------------+
```

### ProRun Mode Flow

```
+----------------+     +----------------+     +----------------+
| User enables   |     | Agent selector |     | User selects   |
| ProRun mode    |---->| fields appear  |---->| models for each|
| checkbox       |     | in the form    |     | agent          |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| User selects   |     | User submits   |     | System creates |
| synthesis      |---->| the form       |---->| multiple agent |
| template       |     |                |     | runs in parallel|
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+     +----------------+
| System waits   |     | System collects|     | System creates |
| for all agent  |---->| all agent     |---->| synthesis run   |
| runs to complete|    | responses     |     | with template   |
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+
| Final          |     | UI displays    |
| synthesized    |---->| final result   |
| result created |     | to user        |
+----------------+     +----------------+
```

### Save ProRun Configuration Flow

```
+----------------+     +----------------+     +----------------+
| User configures|     | User clicks    |     | Save dialog    |
| ProRun settings|---->| Save ProRun    |---->| opens          |
|                |     | Configuration  |     |                |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| User enters    |     | System saves   |     | Configuration  |
| name and       |---->| configuration  |---->| appears in     |
| description    |     | to database    |     | dropdown       |
+----------------+     +----------------+     +----------------+
```

### Live Log Streaming Flow

```
+----------------+     +----------------+     +----------------+
| Agent run      |     | Backend API    |     | UI polls logs  |
| executes       |---->| updates logs   |---->| endpoint with  |
| actions        |     | in real-time   |     | pagination     |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| UI displays    |     | UI updates     |     | UI shows       |
| logs with      |<----| status in      |<----| visual         |
| action details |     | header         |     | indicators     |
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+     +----------------+
| UI updates     |     | UI updates     |     | UI updates     |
| tools used     |---->| timeline       |---->| progress       |
| summary        |     | visualization  |     | indicators     |
+----------------+     +----------------+     +----------------+
```

### CLI Integration Flow

```
+----------------+     +----------------+     +----------------+
| User performs  |     | UI generates   |     | User copies    |
| action in UI   |---->| equivalent     |---->| CLI command    |
|                |     | CLI command    |     | to clipboard   |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| User pastes    |     | CLI executes   |     | UI detects     |
| command in     |---->| command and    |---->| CLI-initiated  |
| terminal       |     | calls API      |     | action         |
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+
| UI updates to  |     | UI and CLI     |
| reflect CLI    |---->| remain in      |
| action         |     | sync           |
+----------------+     +----------------+
```

### Project Setup Commands Flow

```
+----------------+     +----------------+     +----------------+
| User clicks    |     | UI sends       |     | Backend        |
| "Generate      |---->| generate       |---->| analyzes repo  |
| Setup Commands"|     | request to API |     | and generates  |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| UI displays    |     | Setup commands |     | Project is     |
| generated      |<----| are stored     |<----| marked as      |
| commands       |     | in backend     |     | having setup   |
+----------------+     +----------------+     +----------------+
```

### Template Management Flow

```
+----------------+     +----------------+     +----------------+
| User clicks    |     | Template       |     | User fills     |
| "Create        |---->| editor dialog  |---->| template form  |
| Template"      |     | opens          |     | and submits    |
+----------------+     +----------------+     +----------------+
        |                                             |
        v                                             v
+----------------+     +----------------+     +----------------+
| Template is    |     | UI updates to  |     | Template       |
| stored in      |<----| show new       |<----| creation       |
| backend        |     | template       |     | request sent   |
+----------------+     +----------------+     +----------------+
        |
        v
+----------------+     +----------------+
| Template       |     | Template       |
| appears in     |---->| available for  |
| templates list |     | agent runs     |
+----------------+     +----------------+
```

