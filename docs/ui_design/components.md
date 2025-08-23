# Agent Management Interface - Components

## Core UI Components

### Cards

Cards are used throughout the interface to display information in a consistent format:

```
+-----------------------------------+
| Card Title                     ⋮ |
+-----------------------------------+
|                                   |
| Card content goes here with text, |
| data, charts, or other elements   |
|                                   |
+-----------------------------------+
| Footer / Actions                  |
+-----------------------------------+
```

Variants:
- Standard card (shown above)
- Status card (with color-coded borders based on status)
- Metric card (for displaying KPIs with large numbers and trends)
- Action card (with prominent buttons)

### Tables

Tables display structured data with sorting, filtering, and pagination:

```
+-------------------------------------------------------+
| Title                                  Filter | Sort ▼ |
+-------+---------------+---------------+---------------+
| Col 1 | Column 2      | Column 3      | Actions       |
+-------+---------------+---------------+---------------+
| Data  | Data          | Data          | ✏️ 🗑️ ℹ️       |
+-------+---------------+---------------+---------------+
| Data  | Data          | Data          | ✏️ 🗑️ ℹ️       |
+-------+---------------+---------------+---------------+
| 1-10 of 42 items                    < 1 2 3 ... 5 >  |
+-------------------------------------------------------+
```

Features:
- Sortable columns (click header to sort)
- Filterable columns (filter dropdown in header)
- Pagination controls
- Row selection with checkboxes
- Bulk actions for selected rows
- Responsive design (horizontal scrolling on small screens)

### Forms

Forms use a consistent layout for data entry:

```
+-------------------------------------------------------+
| Form Title                                            |
+-------------------------------------------------------+
| Field Label                                           |
| +---------------------------------------------------+ |
| | Input field                                       | |
| +---------------------------------------------------+ |
| Helper text or error message                          |
|                                                       |
| Field Label                                           |
| +---------------------------------------------------+ |
| | Dropdown                                      ▼   | |
| +---------------------------------------------------+ |
|                                                       |
| [ ] Checkbox option with label                        |
|                                                       |
| [Cancel]                              [Save Changes]  |
+-------------------------------------------------------+
```

Features:
- Inline validation with error messages
- Required field indicators
- Consistent spacing and alignment
- Responsive layout (stacks on small screens)
- Accessible labels and ARIA attributes

### Buttons

Button hierarchy:
- Primary: Filled background, used for main actions
- Secondary: Outlined, used for alternative actions
- Tertiary: Text only, used for minor actions
- Icon buttons: For compact UI areas

```
[Primary Button]  [Secondary Button]  [Tertiary Button]
```

States:
- Default
- Hover
- Active/Pressed
- Focused
- Disabled
- Loading

### Alerts and Notifications

Alert types:
- Success (green)
- Info (blue)
- Warning (yellow)
- Error (red)

```
+-------------------------------------------------------+
| ✓ Success Alert: Operation completed successfully   ✕ |
+-------------------------------------------------------+

+-------------------------------------------------------+
| ℹ️ Info Alert: Additional information available      ✕ |
+-------------------------------------------------------+

+-------------------------------------------------------+
| ⚠️ Warning Alert: This action requires attention     ✕ |
+-------------------------------------------------------+

+-------------------------------------------------------+
| ❌ Error Alert: An error occurred during processing  ✕ |
+-------------------------------------------------------+
```

Toast notifications appear temporarily:

```
+-----------------------------------+
| ✓ Agent run completed successfully|
+-----------------------------------+
```

### Modals

Modals for focused interactions:

```
+-------------------------------------------------------+
|                                                     ✕ |
| Modal Title                                           |
+-------------------------------------------------------+
|                                                       |
| Modal content goes here. This could be a form,        |
| confirmation message, or detailed information.        |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
| [Secondary Action]                  [Primary Action]  |
+-------------------------------------------------------+
```

### Tabs

Tabs for switching between related content:

```
+-------------------------------------------------------+
| [Active Tab] | Inactive Tab | Inactive Tab |          |
+-------------------------------------------------------+
|                                                       |
| Content for the active tab is displayed here.         |
|                                                       |
+-------------------------------------------------------+
```

### Progress Indicators

For long-running operations:

```
Linear progress:
[===============----------------] 45%

Circular progress:
   ╭───╮
  ╭┘   └╮
 ╭┘     │
 │      │
 │      │
 │      ╰╮
  │      │
   ╰────╯
```

### Data Visualization

Chart components:
- Line charts (for time series data)
- Bar charts (for comparisons)
- Pie/Donut charts (for proportions)
- Area charts (for cumulative values)
- Heatmaps (for frequency or intensity)

### Code Display

For displaying code snippets and logs:

```
+-------------------------------------------------------+
| filename.py                                    [Copy] |
+-------------------------------------------------------+
| 1 | def example_function():                           |
| 2 |     """                                           |
| 3 |     This is an example function.                  |
| 4 |     """                                           |
| 5 |     return "Hello, world!"                        |
+-------------------------------------------------------+
```

Features:
- Syntax highlighting
- Line numbers
- Copy button
- Code folding
- Search within code

## Specialized Components

### Agent Status Badge

Compact indicator of agent status:

```
⚪ Pending   🔵 Running   ✅ Completed   ❌ Failed   ⚫ Cancelled
```

### Agent Run Timeline

Visual representation of agent run progress:

```
+-------------------------------------------------------+
| Start                                           End   |
| ●───────●───────●───────●───────○───────○             |
| Init    Fetch    Plan    Execute  Review   Complete   |
+-------------------------------------------------------+
```

### Repository Selector

For choosing repositories:

```
+---------------------------------------------------+
| Select Repository                              ▼  |
+---------------------------------------------------+
| ● repository-name                                 |
| ○ another-repository                              |
| ○ third-repository                                |
+---------------------------------------------------+
```

### Log Viewer

For viewing and filtering agent logs:

```
+-------------------------------------------------------+
| Logs                                    [Filter] [⟳]  |
+-------------------------------------------------------+
| 12:34:56 | INFO  | Agent initialized                  |
| 12:35:01 | INFO  | Fetching repository data           |
| 12:35:15 | DEBUG | Repository data received           |
| 12:36:02 | ERROR | Failed to access file: permission  |
+-------------------------------------------------------+
| Show: [✓] INFO [✓] DEBUG [✓] WARN [✓] ERROR          |
+-------------------------------------------------------+
```

### Prompt Builder

For creating and editing agent prompts:

```
+-------------------------------------------------------+
| Prompt Builder                                        |
+-------------------------------------------------------+
| +---------------------------------------------------+ |
| | Enter your prompt here...                         | |
| |                                                   | |
| | The agent will use this text to understand what   | |
| | you want it to do.                               | |
| |                                                   | |
| +---------------------------------------------------+ |
|                                                       |
| Attachments:                                          |
| [+ Add Image]  [+ Add File]                           |
|                                                       |
| Options:                                              |
| Model: [GPT-4 ▼]                                      |
| Repository: [Select Repository ▼]                     |
|                                                       |
| [Cancel]                                  [Run Agent] |
+-------------------------------------------------------+
```

### Pull Request Card

For displaying pull requests created by agents:

```
+-------------------------------------------------------+
| PR #123: Add input validation to login form           |
+-------------------------------------------------------+
| Created: 2 hours ago                                  |
| Status: Open                                          |
|                                                       |
| 3 files changed (+45, -12)                            |
|                                                       |
| [View on GitHub]                                      |
+-------------------------------------------------------+
```

