# Agent Management Interface - MultiRunAgent Mockup

The MultiRunAgent interface allows users to run multiple agent instances concurrently and synthesize their outputs for better results.

## MultiRunAgent Creation Form

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Create MultiRunAgent              | |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | 1. Basic Configuration            | |
|               | |                                   | |
|               | | Repository:                       | |
|               | | +-------------------------------+ | |
|               | | | Select Repository          ▼  | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Model:                            | |
|               | | +-------------------------------+ | |
|               | | | GPT-4                      ▼  | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Concurrency:                      | |
|               | | +-------------------------------+ | |
|               | | | 3                           ▼  | | |
|               | | +-------------------------------+ | |
|               | | Number of parallel agent runs     | |
|               | |                                   | |
|               | | 2. Prompt                         | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Enter your prompt here...     | | |
|               | | |                               | | |
|               | | | The agent will use this text  | | |
|               | | | to understand what you want   | | |
|               | | | it to do.                     | | |
|               | | |                               | | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | 3. Attachments (Optional)         | |
|               | |                                   | |
|               | | [+ Add Image]  [+ Add File]       | |
|               | |                                   | |
|               | | 4. Advanced Options               | |
|               | |                                   | |
|               | | [+ Show Advanced Options]         | |
|               | |                                   | |
|               | | [Cancel]         [Create MultiRun]| |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Advanced Options Panel (Expanded)

When the user clicks "Show Advanced Options", the form expands to show additional configuration options:

```
+-------------------------------------------------------+
| 4. Advanced Options                                   |
+-------------------------------------------------------+
| Temperature:                                          |
| +---------------------------------------------------+ |
| | 0.0                  0.7                      1.0 | |
| | [-----------|----------O-----------|------------] | |
| +---------------------------------------------------+ |
| Higher values produce more diverse outputs             |
|                                                       |
| Synthesis Temperature:                                |
| +---------------------------------------------------+ |
| | 0.0        0.2                                1.0 | |
| | [-----O----|-----------------------------------|] | |
| +---------------------------------------------------+ |
| Lower values produce more focused synthesis            |
|                                                       |
| Custom Synthesis Prompt:                              |
| +---------------------------------------------------+ |
| | (Optional) Enter a custom prompt for the         | |
| | synthesis agent that will combine the outputs    | |
| | from the parallel runs.                          | |
| +---------------------------------------------------+ |
|                                                       |
| Timeout:                                              |
| +--------+  seconds                                   |
| |   600  |                                            |
| +--------+                                            |
|                                                       |
| Metadata:                                             |
| +---------------------------------------------------+ |
| | {"key": "value"}                                  | |
| +---------------------------------------------------+ |
| Helper text: JSON metadata to attach to the agent runs |
|                                                       |
| Notification:                                         |
| [✓] Email me when completed                           |
| [✓] Slack notification                                |
|                                                       |
| [- Hide Advanced Options]                             |
+-------------------------------------------------------+
```

## MultiRunAgent Progress View

When a MultiRunAgent is running, the user sees a progress view:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | MultiRunAgent #125              [↩] |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Status: 🔵 Running                 | |
|               | | Created: 2023-08-22 14:30:45 UTC  | |
|               | | Repository: repository-name       | |
|               | | Model: GPT-4                      | |
|               | | Concurrency: 3                    | |
|               | |                                   | |
|               | | +---------------------------+     | |
|               | | | Progress                  |     | |
|               | | | Agent 1: ●───●───●───○───○      | |
|               | | | Agent 2: ●───●───○───○───○      | |
|               | | | Agent 3: ●───●───●───●───○      | |
|               | | | Synthesis: ○───○───○───○───○    | |
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
|               | | [Cancel] [View Logs]              | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## MultiRunAgent Results View

When a MultiRunAgent completes, the user sees the results:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | MultiRunAgent #125 > Results    [↩] |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Status: ✅ Completed               | |
|               | | Created: 2023-08-22 14:30:45 UTC  | |
|               | | Completed: 2023-08-22 14:35:12 UTC| |
|               | | Duration: 4m 27s                  | |
|               | |                                   | |
|               | | Final Synthesized Output:         | |
|               | | +---------------------------+     | |
|               | | | def fibonacci(n: int) -> int:  | |
|               | | |     """                        | |
|               | | |     Calculate the nth Fibonacci| |
|               | | |     number.                    | |
|               | | |                                | |
|               | | |     Args:                      | |
|               | | |         n: The position in the | |
|               | | |            sequence (0-indexed)| |
|               | | |                                | |
|               | | |     Returns:                   | |
|               | | |         The nth Fibonacci number| |
|               | | |                                | |
|               | | |     Raises:                    | |
|               | | |         ValueError: If n is    | |
|               | | |         negative               | |
|               | | |     """                        | |
|               | | |     if n < 0:                  | |
|               | | |         raise ValueError(      | |
|               | | |             "Input must be non-| |
|               | | |             negative")         | |
|               | | |     if n <= 1:                 | |
|               | | |         return n               | |
|               | | |                                | |
|               | | |     a, b = 0, 1                | |
|               | | |     for _ in range(2, n + 1):  | |
|               | | |         a, b = b, a + b        | |
|               | | |     return b                   | |
|               | | +---------------------------+     | |
|               | |                                   | |
|               | | [View Candidate Outputs]          | |
|               | | [Download Results]                | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Candidate Outputs View

When the user clicks "View Candidate Outputs":

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | MultiRunAgent #125 > Candidates [↩] |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Candidate 1 | Candidate 2 | Candidate 3 | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | Candidate 1:                      | |
|               | | +---------------------------+     | |
|               | | | def fibonacci(n):              | |
|               | | |     """Calculate the nth       | |
|               | | |     Fibonacci number."""       | |
|               | | |     if n <= 0:                 | |
|               | | |         return 0               | |
|               | | |     elif n == 1:               | |
|               | | |         return 1               | |
|               | | |     else:                      | |
|               | | |         return fibonacci(n-1)  | |
|               | | |             + fibonacci(n-2)   | |
|               | | +---------------------------+     | |
|               | |                                   | |
|               | | Agent Run ID: #126                | |
|               | | Status: ✅ Completed               | |
|               | | Duration: 2m 15s                  | |
|               | |                                   | |
|               | | [View Full Output] [View Logs]    | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## MultiRunAgent Comparison View

The interface also offers a comparison view to see differences between candidate outputs:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | MultiRunAgent #125 > Compare    [↩] |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Compare:                           | |
|               | | [✓] Candidate 1                    | |
|               | | [✓] Candidate 2                    | |
|               | | [✓] Candidate 3                    | |
|               | | [✓] Final Synthesis                | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Implementation Approach:       | |
|               | | |                               | |
|               | | | Candidate 1: Recursive        | |
|               | | | Candidate 2: Iterative        | |
|               | | | Candidate 3: Dynamic Programming| |
|               | | | Final: Iterative              | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Error Handling:                | |
|               | | |                               | |
|               | | | Candidate 1: Returns 0 for n≤0 | |
|               | | | Candidate 2: Raises ValueError | |
|               | | | Candidate 3: Raises ValueError | |
|               | | | Final: Raises ValueError       | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Documentation:                 | |
|               | | |                               | |
|               | | | Candidate 1: Basic docstring  | |
|               | | | Candidate 2: Detailed docstring| |
|               | | | Candidate 3: Type hints       | |
|               | | | Final: Detailed + Type hints  | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | [View Side-by-Side Code Comparison]| |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## MultiRunAgent Analytics View

The interface provides analytics on the MultiRunAgent runs:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | MultiRunAgent #125 > Analytics  [↩] |
|  Navigation   | +-----------------------------------+ |
|  Sidebar      | |                                   | |
|               | | Performance Metrics:               | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Agent Run Times:               | |
|               | | | [Bar chart showing run times]  | |
|               | | |                               | |
|               | | | Agent 1: 2m 15s               | |
|               | | | Agent 2: 1m 58s               | |
|               | | | Agent 3: 2m 42s               | |
|               | | | Synthesis: 52s                | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Output Similarity:             | |
|               | | | [Heatmap showing similarity]   | |
|               | | |                               | |
|               | | | Candidate 1 ↔ Candidate 2: 68%| |
|               | | | Candidate 1 ↔ Candidate 3: 72%| |
|               | | | Candidate 2 ↔ Candidate 3: 75%| |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | +-------------------------------+ | |
|               | | | Unique Contributions:          | |
|               | | | [Pie chart showing unique     | |
|               | | |  elements from each candidate]| |
|               | | |                               | |
|               | | | Candidate 1: 15%              | |
|               | | | Candidate 2: 45%              | |
|               | | | Candidate 3: 40%              | |
|               | | +-------------------------------+ | |
|               | |                                   | |
|               | | [Export Analytics]                | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Responsive Behavior

On smaller screens:
- Form sections stack vertically
- Progress indicators simplify to show fewer details
- Tabs become a dropdown menu
- Comparison views adapt to show one candidate at a time
- Charts resize to fit available width

