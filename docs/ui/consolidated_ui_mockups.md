# Consolidated Codegen UI Mockups

Based on the functionality analysis, I've redesigned the UI mockups to provide a more consistent, intuitive interface with proper naming conventions and reduced redundancy.

## Main Application Layout

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|   NAVIGATION     |                MAIN CONTENT               |
|                  |                                           |
|   • Dashboard    |                                           |
|   • Agents       |                                           |
|   • Repositories |                                           |
|   • Settings     |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Ready                    Organization: MyOrg        |
+--------------------------------------------------------------+
```

## Dashboard View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  DASHBOARD                                |
|                  |                                           |
|                  |  +------------------+  +------------------+
|                  |  |                  |  |                  |
|   NAVIGATION     |  |   AGENT METRICS  |  |  RECENT ACTIVITY |
|                  |  |                  |  |                  |
|   • Dashboard    |  |  12 Running      |  |  • Agent run-123 |
|   • Agents       |  |  3 Pending       |  |    completed     |
|   • Repositories |  |  24 Completed    |  |    2 minutes ago |
|   • Settings     |  |  2 Failed        |  |                  |
|                  |  |                  |  |  • New repository|
|                  |  |  [View All]      |  |    added         |
|                  |  |                  |  |    5 minutes ago |
|                  |  +------------------+  +------------------+
|                  |                                           |
|                  |  +------------------+  +------------------+
|                  |  |                  |  |                  |
|                  |  |  REPOSITORIES    |  |  SYSTEM STATUS   |
|                  |  |                  |  |                  |
|                  |  |  8 Active        |  |  API: Connected  |
|                  |  |  2 Archived      |  |  Models: 4 Avail.|
|                  |  |                  |  |  Last Update:    |
|                  |  |  [View All]      |  |  2 minutes ago   |
|                  |  |                  |  |                  |
|                  |  +------------------+  +------------------+
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Ready                    Organization: MyOrg        |
+--------------------------------------------------------------+
```

## Agent Management View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  AGENTS                      [+ CREATE]   |
|                  |                                           |
|                  |  +----------------------------------------+
|                  |  |                                        |
|   NAVIGATION     |  |  FILTERS:                              |
|                  |  |  Status: [All ▼]  Date: [Last 7 days ▼]|
|   • Dashboard    |  |  Search: [                      ]      |
|   • Agents       |  |                                        |
|   • Repositories |  +----------------------------------------+
|   • Settings     |                                           |
|                  |  +----------------------------------------+
|                  |  | ID      | PROMPT    | STATUS  | ACTIONS|
|                  |  +----------------------------------------+
|                  |  | run-123 | Create... | Running | [⋮]    |
|                  |  | run-122 | Fix th... | Complete| [⋮]    |
|                  |  | run-121 | Analyze...| Failed  | [⋮]    |
|                  |  | run-120 | Generate..| Complete| [⋮]    |
|                  |  | run-119 | Debug t...| Complete| [⋮]    |
|                  |  | run-118 | Impleme...| Complete| [⋮]    |
|                  |  | run-117 | Create... | Complete| [⋮]    |
|                  |  | run-116 | Optimiz...| Complete| [⋮]    |
|                  |  | run-115 | Review... | Complete| [⋮]    |
|                  |  | run-114 | Test th...| Complete| [⋮]    |
|                  |  +----------------------------------------+
|                  |                                           |
|                  |  Showing 10 of 24 agents       [1 2 3 >]  |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Ready                    Organization: MyOrg        |
+--------------------------------------------------------------+
```

## Agent Detail View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  AGENT: run-123                [REFRESH]  |
|                  |                                           |
|                  |  [Details] [Logs] [Output]                |
|                  |                                           |
|   NAVIGATION     |  +----------------------------------------+
|                  |  |                                        |
|   • Dashboard    |  |  OVERVIEW                              |
|   • Agents       |  |                                        |
|   • Repositories |  |  Status: Running                       |
|   • Settings     |  |  Created: 2023-08-22 08:12:14          |
|                  |  |  Updated: 2023-08-22 08:14:22          |
|                  |  |  Model: gpt-4                          |
|                  |  |  Repository: my-project                |
|                  |  |                                        |
|                  |  |  PROMPT                                |
|                  |  |  Create a new feature that allows      |
|                  |  |  users to filter agent runs by status  |
|                  |  |  and date range.                       |
|                  |  |                                        |
|                  |  |  PROGRESS                              |
|                  |  |  [●●●○○○] 50% Complete                 |
|                  |  |  • Initialization ✓                    |
|                  |  |  • Fetching ✓                          |
|                  |  |  • Planning ✓                          |
|                  |  |  • Execution ○                         |
|                  |  |  • Review ○                            |
|                  |  |  • Completion ○                        |
|                  |  |                                        |
|                  |  +----------------------------------------+
|                  |                                           |
|                  |  [RESUME] [CANCEL] [CLONE] [EXPORT]       |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Agent run-123 is running       Organization: MyOrg  |
+--------------------------------------------------------------+
```

## Agent Logs View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  AGENT: run-123                [REFRESH]  |
|                  |                                           |
|                  |  [Details] [Logs] [Output]                |
|                  |                                           |
|   NAVIGATION     |  +----------------------------------------+
|                  |  |                                        |
|   • Dashboard    |  |  LOGS                                  |
|   • Agents       |  |                                        |
|   • Repositories |  |  Filter: [All Levels ▼] [          ]   |
|   • Settings     |  |                                        |
|                  |  |  2023-08-22 08:12:14 [INFO]            |
|                  |  |  Agent run initialized with model gpt-4 |
|                  |  |                                        |
|                  |  |  2023-08-22 08:12:15 [INFO]            |
|                  |  |  Fetching repository my-project        |
|                  |  |                                        |
|                  |  |  2023-08-22 08:12:18 [INFO]            |
|                  |  |  Repository fetched successfully       |
|                  |  |                                        |
|                  |  |  2023-08-22 08:12:20 [INFO]            |
|                  |  |  Planning task execution               |
|                  |  |                                        |
|                  |  |  2023-08-22 08:12:25 [INFO]            |
|                  |  |  Plan created with 5 steps             |
|                  |  |                                        |
|                  |  |  2023-08-22 08:12:30 [INFO]            |
|                  |  |  Executing step 1: Analyze requirements|
|                  |  |                                        |
|                  |  +----------------------------------------+
|                  |                                           |
|                  |  [RESUME] [CANCEL] [EXPORT LOGS]          |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Agent run-123 is running       Organization: MyOrg  |
+--------------------------------------------------------------+
```

## Create Agent Dialog

```
+--------------------------------------------------------------+
|                                                              |
|  CREATE AGENT                                       [X]      |
|                                                              |
+--------------------------------------------------------------+
|                                                              |
|  REPOSITORY                                                  |
|  [my-project (123)                                      ▼]   |
|                                                              |
|  MODEL                                                       |
|  [gpt-4                                                 ▼]   |
|                                                              |
|  PARAMETERS                                                  |
|  Temperature: [------O------] 0.7                            |
|                                                              |
|  PROMPT                                                      |
|  +----------------------------------------------------------+|
|  | Create a new feature that allows users to filter agent   ||
|  | runs by status and date range.                           ||
|  |                                                          ||
|  |                                                          ||
|  +----------------------------------------------------------+|
|                                                              |
|  ADVANCED OPTIONS                                            |
|  [+] Show advanced options                                   |
|                                                              |
|                                                              |
|                                      [CANCEL] [CREATE AGENT] |
|                                                              |
+--------------------------------------------------------------+
```

## Repository View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  REPOSITORIES                  [REFRESH]  |
|                  |                                           |
|                  |  +----------------------------------------+
|                  |  |                                        |
|   NAVIGATION     |  |  FILTERS:                              |
|                  |  |  Status: [All ▼]                       |
|   • Dashboard    |  |  Search: [                      ]      |
|   • Agents       |  |                                        |
|   • Repositories |  +----------------------------------------+
|   • Settings     |                                           |
|                  |  +----------------------------------------+
|                  |  | ID  | NAME       | DESCRIPTION   | ACTS|
|                  |  +----------------------------------------+
|                  |  | 123 | my-project | A project for | [⋮] |
|                  |  | 124 | api        | API service   | [⋮] |
|                  |  | 125 | frontend   | UI components | [⋮] |
|                  |  | 126 | backend    | Backend servi | [⋮] |
|                  |  | 127 | docs       | Documentation | [⋮] |
|                  |  | 128 | tools      | Development t | [⋮] |
|                  |  | 129 | mobile     | Mobile app    | [⋮] |
|                  |  | 130 | desktop    | Desktop app   | [⋮] |
|                  |  | 131 | cli        | Command line  | [⋮] |
|                  |  | 132 | sdk        | Software deve| [⋮] |
|                  |  +----------------------------------------+
|                  |                                           |
|                  |  Showing 10 of 15 repositories  [1 2 >]   |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Ready                    Organization: MyOrg        |
+--------------------------------------------------------------+
```

## Settings View

```
+--------------------------------------------------------------+
|                                                              |
|  CODEGEN                       [Search...]    [User ▼] [?]   |
|                                                              |
+--------------------------------------------------------------+
|                  |                                           |
|                  |  SETTINGS                                 |
|                  |                                           |
|                  |  [General] [API] [UI] [Logging]           |
|                  |                                           |
|   NAVIGATION     |  +----------------------------------------+
|                  |  |                                        |
|   • Dashboard    |  |  GENERAL SETTINGS                      |
|   • Agents       |  |                                        |
|   • Repositories |  |  Organization                          |
|   • Settings     |  |  [MyOrg                           ▼]   |
|                  |  |                                        |
|                  |  |  Theme                                 |
|                  |  |  (○) Light  (○) Dark  (○) System       |
|                  |  |                                        |
|                  |  |  Language                              |
|                  |  |  [English                          ▼]  |
|                  |  |                                        |
|                  |  |  Date Format                           |
|                  |  |  [YYYY-MM-DD HH:MM:SS              ▼]  |
|                  |  |                                        |
|                  |  |  Auto-refresh Interval                 |
|                  |  |  [30                             ] sec |
|                  |  |                                        |
|                  |  |  Default View                          |
|                  |  |  [Dashboard                        ▼]  |
|                  |  |                                        |
|                  |  +----------------------------------------+
|                  |                                           |
|                  |                          [SAVE] [CANCEL]  |
|                  |                                           |
+--------------------------------------------------------------+
|  Status: Ready                    Organization: MyOrg        |
+--------------------------------------------------------------+
```

## Mobile View - Agent List

```
+---------------------------+
|                           |
|  CODEGEN       [≡] [👤]  |
|                           |
+---------------------------+
|                           |
|  AGENTS         [+ NEW]   |
|                           |
|  Status: [All ▼]          |
|  Search: [          ]     |
|                           |
|  +---------------------+  |
|  | run-123             |  |
|  | Create a new feat...|  |
|  | Status: Running     |  |
|  | 2 minutes ago       |  |
|  | [View] [Cancel]     |  |
|  +---------------------+  |
|                           |
|  +---------------------+  |
|  | run-122             |  |
|  | Fix the bug in th...|  |
|  | Status: Completed   |  |
|  | 5 minutes ago       |  |
|  | [View] [Clone]      |  |
|  +---------------------+  |
|                           |
|  +---------------------+  |
|  | run-121             |  |
|  | Analyze the perfo...|  |
|  | Status: Failed      |  |
|  | 10 minutes ago      |  |
|  | [View] [Clone]      |  |
|  +---------------------+  |
|                           |
|  [1] [2] [3] [>]          |
|                           |
+---------------------------+
```

## Component Library

### 1. Navigation Sidebar
- Consistent across all views
- Highlights current section
- Collapsible on smaller screens

### 2. SearchFilterBar
- Standardized search and filter controls
- Consistent appearance and behavior
- Used in Agents and Repositories views

### 3. ActionButton
- Primary action button (blue)
- Secondary action button (gray)
- Destructive action button (red)
- Icon button with tooltip

### 4. StatusIndicator
- Success (green)
- Warning (yellow)
- Error (red)
- Info (blue)
- Neutral (gray)

### 5. ProgressIndicator
- Linear progress bar
- Step indicator with checkmarks
- Percentage display

### 6. DataTable
- Sortable columns
- Pagination controls
- Row actions menu
- Selectable rows

### 7. TabContainer
- Horizontal tabs
- Content area
- Active tab indicator

### 8. Modal Dialog
- Title bar with close button
- Content area
- Action buttons

### 9. FormControls
- Text input
- Dropdown select
- Slider
- Checkbox
- Radio button
- Text area

### 10. Card
- Header
- Content area
- Footer with actions
- Hover effects

