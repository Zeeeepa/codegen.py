# Multi-Run Agent Feature UI Mockups

## Multi-Run Toggle Component

The Multi-Run Toggle component allows users to enable/disable the multi-run feature and configure thread count:

```
+-------------------------------------------------------+
| [✓] Multi-Agent Run                              [⚙️] |
+-------------------------------------------------------+
| Thread Count: [3] [1 ----O---- 5 ---- 10 ---- 20]     |
+-------------------------------------------------------+
```

When expanded with advanced settings:

```
+-------------------------------------------------------+
| [✓] Multi-Agent Run                              [⚙️] |
+-------------------------------------------------------+
| Thread Count: [3] [1 ----O---- 5 ---- 10 ---- 20]     |
+-------------------------------------------------------+
| Advanced Settings:                                    |
| [Diverse Models] [Temperature Variation] [Custom]     |
+-------------------------------------------------------+
```

During execution, it shows progress:

```
+-------------------------------------------------------+
| [✓] Multi-Agent Run                              [⚙️] |
+-------------------------------------------------------+
| Thread Count: [3] [1 ----O---- 5 ---- 10 ---- 20]     |
+-------------------------------------------------------+
| Progress: 2/3 threads complete                    66% |
| [████████████████████████████------]                  |
+-------------------------------------------------------+
```

## Create Agent Run with Multi-Run Enabled

```
+-------------------------------------------------------+
| Create Agent Run                                      |
+-------------------------------------------------------+
| [✓] Multi-Agent Run                              [⚙️] |
+-------------------------------------------------------+
| Thread Count: [7] [1 ---- 5 --O-- 10 ---- 20]         |
| Progress: 5/7 threads complete                    71% |
| [███████████████████████████-----]                    |
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
|                                                       |
| [Run Multi-Agent]                                     |
+-------------------------------------------------------+
```

## Multi-Run Results View

```
+-------------------------------------------------------+
| Multi-Agent Results                                   |
+-------------------------------------------------------+
| Final Synthesized Response:                   [Copy]  |
| +---------------------------------------------------+ |
| |                                                   | |
| | This is the final synthesized response that       | |
| | combines the best elements from all agent threads.| |
| |                                                   | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
| Original Prompt:                                      |
| +---------------------------------------------------+ |
| | This is the original user prompt that was sent    | |
| | to all agent threads.                             | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
| Individual Thread Results (7):                        |
| +-------------+ +-------------+ +-------------+       |
| | Thread #1   | | Thread #2   | | Thread #3   |       |
| | ✅ Completed | | ✅ Completed | | ✅ Completed |       |
| | [View]      | | [View]      | | [View]      |       |
| +-------------+ +-------------+ +-------------+       |
|                                                       |
| +-------------+ +-------------+ +-------------+       |
| | Thread #4   | | Thread #5   | | Thread #6   |       |
| | ✅ Completed | | ✅ Completed | | ❌ Failed    |       |
| | [View]      | | [View]      | | [View]      |       |
| +-------------+ +-------------+ +-------------+       |
|                                                       |
| +-------------+ +-------------+                       |
| | Thread #7   | | Synthesis   |                       |
| | ✅ Completed | | ✅ Completed |                       |
| | [View]      | | [View]      |                       |
| +-------------+ +-------------+                       |
+-------------------------------------------------------+
```

## Thread Detail Expansion

When a thread result is expanded:

```
+-------------------------------------------------------+
| Thread #1                                      [Copy] |
+-------------------------------------------------------+
| Status: ✅ Completed                                   |
+-------------------------------------------------------+
| Response:                                             |
| +---------------------------------------------------+ |
| |                                                   | |
| | This is the response from thread #1.              | |
| |                                                   | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
| [View Full Details]                                   |
+-------------------------------------------------------+
```

## Multi-Run Progress Modal

A modal dialog can appear during processing to show detailed progress:

```
+-------------------------------------------------------+
|                  Multi-Run Progress                   |
+-------------------------------------------------------+
| Overall Progress: 5/8 complete                    62% |
| [█████████████████████-------]                        |
+-------------------------------------------------------+
| Thread #1: ✅ Completed                               |
| Thread #2: ✅ Completed                               |
| Thread #3: ✅ Completed                               |
| Thread #4: ✅ Completed                               |
| Thread #5: ✅ Completed                               |
| Thread #6: ⏳ Running                                 |
| Thread #7: ⏳ Running                                 |
| Synthesis: ⏳ Waiting                                 |
+-------------------------------------------------------+
|                      [Cancel]                         |
+-------------------------------------------------------+
```

## WebSocket Status Updates

The multi-run feature uses WebSockets to provide real-time status updates:

```
// Example WebSocket message format
{
  "type": "multi_run_status",
  "multi_run_id": "12345",
  "status": {
    "status": "running",
    "completed_runs": 5,
    "total_runs": 8,
    "agent_runs": [
      {
        "id": "run1",
        "status": "completed",
        "result": "..."
      },
      {
        "id": "run2",
        "status": "completed",
        "result": "..."
      },
      // ...
    ]
  }
}
```

## Mobile View

On mobile devices, the layout adapts to a more compact format:

```
+-------------------------------------------------------+
| [✓] Multi-Agent Run                                   |
+-------------------------------------------------------+
| Thread Count: [3]                                     |
| [1 ----O---- 5 ---- 10 ---- 20]                       |
+-------------------------------------------------------+
| Progress: 2/3 threads complete                        |
| [████████████████████████████------]              66% |
+-------------------------------------------------------+
```

## Dark Mode

All UI components support both light and dark modes:

```
+-------------------------------------------------------+
| [✓] Multi-Agent Run                              [⚙️] |
+-------------------------------------------------------+
| Thread Count: [3] [1 ----O---- 5 ---- 10 ---- 20]     |
+-------------------------------------------------------+
| Progress: 2/3 threads complete                    66% |
| [████████████████████████████------]                  |
+-------------------------------------------------------+
```

Dark mode features:
- Dark backgrounds with light text
- Adjusted color palette for better contrast
- Preserved status color indicators (green for success, red for error)
- Progress bar with appropriate contrast

