# Agent Management Interface - Agent Monitoring Mockup

The agent monitoring interface allows users to view and manage active and completed agent runs.

## Agent Runs List View

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Agent Runs                    [+] | |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | | Filters:                           | |
|               | | Status: [All ▼] Repo: [All ▼] ⟳   | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | ID    | Status  | Repository  | | |
|               | | |-------+---------+-------------| | |
|               | | | #125  | 🔵 Running | repo-name | | |
|               | | | #124  | ⚪ Pending | repo-name | | |
|               | | | #123  | ✅ Success | repo-name | | |
|               | | | #122  | ❌ Failed  | repo-name | | |
|               | | | #121  | ✅ Success | repo-name | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Showing 1-5 of 42 runs           | |
|               | | [< Prev]  Page 1 of 9  [Next >]  | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Agent Run Detail View

When a user clicks on an agent run, they see the detailed view:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Agent Run #125                 [↩] | |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Status: 🔵 Running                 | |
|               | | Created: 2023-08-22 14:30:45 UTC  | |
|               | | Repository: repository-name       | |
|               | | Model: GPT-4                      | |
|               | |                                   | |
|               | | +---------------------------+     | |
|               | | | Progress                  |     | |
|               | | | ●───●───●───○───○         |     | |
|               | | | Init Fetch Plan Execute Review  | |
|               | | +---------------------------+     | |
|               | |                                   | |
|               | | Prompt:                           | |
|               | | +---------------------------+     | |
|               | | | Create a Python function to    | |
|               | | | calculate the Fibonacci        | |
|               | | | sequence.                      | |
|               | | +---------------------------+     | |
|               | |                                   | |
|               | | Actions:                          | |
|               | | [Resume] [Cancel] [View Logs]     | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
|               | +-----------------------------------+ |
|               | | Pull Requests                     | |
|               | +-----------------------------------+ |
|               | | No pull requests created yet.      | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Agent Run Logs View

When a user clicks "View Logs", they see the logs panel:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Agent Run #125 > Logs          [↩] | |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Filters: [All Levels ▼] [Search]  | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Time     | Level | Message    | | |
|               | | |---------+-------+------------| | |
|               | | | 14:30:45 | INFO  | Agent init| | |
|               | | | 14:30:47 | INFO  | Fetching..| | |
|               | | | 14:30:52 | DEBUG | Repo data | | |
|               | | | 14:31:05 | INFO  | Planning..| | |
|               | | | 14:31:20 | DEBUG | Plan comp.| | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Auto-refresh: [✓] Every 5s        | |
|               | | [Download Logs]                   | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Log Entry Detail View

When a user clicks on a log entry, they see the detailed view:

```
+-------------------------------------------------------+
| Log Entry Detail                                    ✕ |
+-------------------------------------------------------+
| Time: 2023-08-22 14:31:05 UTC                         |
| Level: INFO                                           |
| Message: Planning implementation strategy              |
|                                                       |
| Tool: planning                                        |
| Thought: "I need to determine the best approach for   |
| implementing the Fibonacci sequence function. I'll    |
| consider both recursive and iterative approaches."    |
|                                                       |
| Tool Input:                                           |
| +---------------------------------------------------+ |
| | {                                                 | |
| |   "prompt": "Create a Python function to         | |
| |   calculate the Fibonacci sequence."             | |
| | }                                                | |
| +---------------------------------------------------+ |
|                                                       |
| Tool Output:                                          |
| +---------------------------------------------------+ |
| | {                                                 | |
| |   "plan": [                                       | |
| |     "Implement iterative Fibonacci function",     | |
| |     "Add docstring with explanation",             | |
| |     "Add type hints",                             | |
| |     "Add error handling for negative inputs"      | |
| |   ]                                               | |
| | }                                                 | |
| +---------------------------------------------------+ |
|                                                       |
| [Close]                                               |
+-------------------------------------------------------+
```

## Agent Run Cancellation Confirmation

When a user clicks "Cancel" on a running agent:

```
+-------------------------------------------------------+
| Confirm Cancellation                                ✕ |
+-------------------------------------------------------+
| Are you sure you want to cancel Agent Run #125?       |
|                                                       |
| This action cannot be undone. The agent will stop     |
| processing and any in-progress work will be lost.     |
|                                                       |
| [No, Keep Running]         [Yes, Cancel Agent Run]    |
+-------------------------------------------------------+
```

## Agent Run Resume Form

When a user clicks "Resume" on a completed or failed agent:

```
+-------------------------------------------------------+
| Resume Agent Run #125                               ✕ |
+-------------------------------------------------------+
| Add additional instructions for the agent:            |
|                                                       |
| +---------------------------------------------------+ |
| | Please modify the function to handle negative     | |
| | inputs by raising a ValueError with an            | |
| | appropriate message.                              | |
| |                                                   | |
| +---------------------------------------------------+ |
|                                                       |
| [+ Add Image]                                         |
|                                                       |
| [Cancel]                              [Resume Agent]  |
+-------------------------------------------------------+
```

## Pull Requests Section (With PRs)

When pull requests have been created:

```
+-------------------------------------------------------+
| Pull Requests                                         |
+-------------------------------------------------------+
| #42: Add Fibonacci sequence calculator                |
| Created: 10 minutes ago                               |
| Status: Open                                          |
| Files changed: 2 (+25, -0)                            |
| [View on GitHub]                                      |
|                                                       |
| #43: Add error handling for negative inputs           |
| Created: 2 minutes ago                                |
| Status: Open                                          |
| Files changed: 1 (+5, -1)                             |
| [View on GitHub]                                      |
+-------------------------------------------------------+
```

## Batch Actions

When multiple agent runs are selected:

```
+-------------------------------------------------------+
| Selected: 3 agent runs                                |
+-------------------------------------------------------+
| [Cancel Selected] [Download Logs] [Clear Selection]   |
+-------------------------------------------------------+
```

## Responsive Behavior

On smaller screens:
- Table columns adapt or become expandable rows
- Action buttons collapse into a menu
- Log entries show less information with expandable details
- Timeline visualization simplifies to show fewer steps

