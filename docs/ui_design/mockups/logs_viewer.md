# Agent Management Interface - Logs Viewer Mockup

The logs viewer provides a detailed interface for examining agent run logs with advanced filtering and analysis capabilities.

## Logs Viewer Layout

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Agent Run #125 > Logs             | |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Filters | Timeline | Analysis | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Filters:                          | |
|               | | Level: [All ▼]  Tool: [All ▼]     | |
|               | | Time Range: [Last Hour ▼]         | |
|               | | Search: [                    ]    | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Time     | Level | Tool  | Msg | | |
|               | | |---------+-------+-------+-----| | |
|               | | | 14:30:45 | INFO  | init  | ... | | |
|               | | | 14:30:47 | INFO  | fetch | ... | | |
|               | | | 14:30:52 | DEBUG | fetch | ... | | |
|               | | | 14:31:05 | INFO  | plan  | ... | | |
|               | | | 14:31:20 | DEBUG | plan  | ... | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Showing 1-5 of 42 log entries    | |
|               | | [< Prev]  Page 1 of 9  [Next >]  | |
|               | |                                   | |
|               | | Auto-refresh: [✓] Every 5s        | |
|               | | [Download Logs] [Share View]      | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Timeline Tab

When the user clicks on the "Timeline" tab:

```
+-------------------------------------------------------+
| +-----------------------------------+                 |
| | Filters | Timeline | Analysis     |                 |
| +-----------------------------------+                 |
|                                                       |
| +---------------------------------------------------+ |
| | 14:30:00          14:31:00          14:32:00     | |
| | |-----------|-----------|-----------|----------| | |
| | |   ●   ●       ●           ●           ●      | | |
| | |-----------|-----------|-----------|----------| | |
| | | Init  Fetch    Plan      Execute    Review   | | |
| +---------------------------------------------------+ |
|                                                       |
| Event Details:                                        |
| Time: 14:31:05                                        |
| Phase: Planning                                       |
| Duration: 25 seconds                                  |
| Description: Agent analyzed repository structure and  |
| developed implementation plan for Fibonacci function. |
|                                                       |
| [Zoom In] [Zoom Out] [Reset] [Export Timeline]        |
+-------------------------------------------------------+
```

## Analysis Tab

When the user clicks on the "Analysis" tab:

```
+-------------------------------------------------------+
| +-----------------------------------+                 |
| | Filters | Timeline | Analysis     |                 |
| +-----------------------------------+                 |
|                                                       |
| Time Distribution by Phase:                           |
| +---------------------------------------------------+ |
| | [Bar chart showing time spent in each phase]      | |
| |                                                   | |
| | Init: 5s (2%)                                     | |
| | Fetch: 18s (7%)                                   | |
| | Plan: 25s (10%)                                   | |
| | Execute: 180s (72%)                               | |
| | Review: 22s (9%)                                  | |
| +---------------------------------------------------+ |
|                                                       |
| Log Entry Types:                                      |
| +---------------------------------------------------+ |
| | [Pie chart showing distribution of log levels]    | |
| |                                                   | |
| | INFO: 65%                                         | |
| | DEBUG: 25%                                        | |
| | WARN: 8%                                          | |
| | ERROR: 2%                                         | |
| +---------------------------------------------------+ |
|                                                       |
| [Generate Report] [Export Data]                       |
+-------------------------------------------------------+
```

## Log Entry Detail Panel

When a user clicks on a log entry, a detail panel slides in from the right:

```
+-------------------------------------------------------+
| Log Entry Detail                                    ✕ |
+-------------------------------------------------------+
| Time: 2023-08-22 14:31:05 UTC                         |
| Level: INFO                                           |
| Tool: planning                                        |
| Message: Planning implementation strategy              |
|                                                       |
| Context:                                              |
| Phase: Plan (2 of 5)                                  |
| Previous action: Repository structure analysis        |
| Next action: Code generation                          |
|                                                       |
| Thought Process:                                      |
| +---------------------------------------------------+ |
| | "I need to determine the best approach for       | |
| | implementing the Fibonacci sequence function.    | |
| | I'll consider both recursive and iterative       | |
| | approaches, weighing their pros and cons."       | |
| +---------------------------------------------------+ |
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
| [View Related Logs] [Add Note] [Close]                |
+-------------------------------------------------------+
```

## Advanced Filtering Options

When the user expands the filtering options:

```
+-------------------------------------------------------+
| Advanced Filters                                      |
+-------------------------------------------------------+
| Level:                                                |
| [✓] INFO  [✓] DEBUG  [✓] WARN  [✓] ERROR  [✓] TRACE  |
|                                                       |
| Tools:                                                |
| [✓] init    [✓] fetch   [✓] plan                     |
| [✓] execute [✓] review  [✓] other                    |
|                                                       |
| Time Range:                                           |
| ○ Last Hour                                           |
| ○ Last 24 Hours                                       |
| ○ Custom Range:                                       |
|   From: [2023-08-22 14:00] To: [2023-08-22 15:00]    |
|                                                       |
| Content Search:                                       |
| [                                                  ]  |
| ○ Message only  ○ All fields  ○ JSON data            |
|                                                       |
| Show entries with:                                    |
| [✓] Thought process                                   |
| [✓] Tool input/output                                 |
| [✓] Code changes                                      |
|                                                       |
| [Reset Filters] [Apply Filters]                       |
+-------------------------------------------------------+
```

## Log Comparison View

When a user selects multiple log entries to compare:

```
+-------------------------------------------------------+
| Log Comparison (2 entries)                          ✕ |
+-------------------------------------------------------+
| +-------------------+ | +-------------------+         |
| | Time: 14:31:05    | | | Time: 14:31:20    |         |
| | Level: INFO       | | | Level: DEBUG      |         |
| | Tool: planning    | | | Tool: planning    |         |
| | Phase: Plan       | | | Phase: Plan       |         |
| +-------------------+ | +-------------------+         |
|                       |                               |
| Thought:              | Thought:                      |
| "I need to determine  | "After analysis, I've        |
| the best approach..." | decided to implement..."      |
|                       |                               |
| Input:                | Input:                        |
| {"prompt": "Create... | {"plan": ["Implement...      |
|                       |                               |
| Output:               | Output:                       |
| {"plan": ["Implement..| {"code": "def fib(n):...     |
|                       |                               |
| [View Diff] [Export Comparison] [Close]               |
+-------------------------------------------------------+
```

## Log Search Results

When a user searches for specific content:

```
+-------------------------------------------------------+
| Search Results: "error handling"                      |
+-------------------------------------------------------+
| 3 matches found                                       |
|                                                       |
| 14:31:05 | INFO | planning                            |
| "...Add error handling for negative inputs..."        |
| [View Context]                                        |
|                                                       |
| 14:32:15 | DEBUG | execute                            |
| "...Implementing error handling logic for edge cases.."|
| [View Context]                                        |
|                                                       |
| 14:32:40 | INFO | execute                             |
| "...Added ValueError for negative inputs as part of   |
| error handling strategy..."                           |
| [View Context]                                        |
|                                                       |
| [Refine Search] [Save Search] [Close]                 |
+-------------------------------------------------------+
```

## Log Export Options

When a user clicks "Download Logs":

```
+-------------------------------------------------------+
| Export Logs                                         ✕ |
+-------------------------------------------------------+
| Format:                                               |
| ○ JSON (complete data)                                |
| ○ CSV (tabular format)                                |
| ○ Plain text (readable)                               |
| ○ HTML (formatted report)                             |
|                                                       |
| Content:                                              |
| ○ All log entries                                     |
| ○ Current filtered view                               |
| ○ Selected entries only                               |
|                                                       |
| Include:                                              |
| [✓] Metadata (timestamps, levels, etc.)               |
| [✓] Thought processes                                 |
| [✓] Tool inputs/outputs                               |
| [✓] Generated code                                    |
|                                                       |
| [Cancel] [Export]                                     |
+-------------------------------------------------------+
```

## Responsive Behavior

On smaller screens:
- Tabs stack vertically
- Table columns adapt or become expandable rows
- Charts resize to fit available width
- Detail panels take full screen width
- Filter options collapse into an expandable accordion

