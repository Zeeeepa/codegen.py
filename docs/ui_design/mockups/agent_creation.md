# Agent Management Interface - Agent Creation Mockup

The agent creation interface allows users to configure and launch new agent runs.

## Agent Creation Form

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------------------------------+ |
|               | | Create New Agent Run              | |
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
|               | | [Cancel]            [Create Run]  | |
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
| Metadata:                                             |
| +---------------------------------------------------+ |
| | {"key": "value"}                                  | |
| +---------------------------------------------------+ |
| Helper text: JSON metadata to attach to the agent run |
|                                                       |
| Priority:                                             |
| ○ Low   ● Normal   ○ High                            |
|                                                       |
| Timeout:                                              |
| +--------+  minutes                                   |
| |   30   |                                            |
| +--------+                                            |
|                                                       |
| Notification:                                         |
| [✓] Email me when completed                           |
| [✓] Slack notification                                |
|                                                       |
| [- Hide Advanced Options]                             |
+-------------------------------------------------------+
```

## Image Attachment Preview

When the user adds an image attachment:

```
+-------------------------------------------------------+
| 3. Attachments                                        |
+-------------------------------------------------------+
| +-------------------+  [+ Add Image]  [+ Add File]    |
| | [Image Thumbnail] |                                 |
| | example.jpg       |                                 |
| | [Remove]          |                                 |
| +-------------------+                                 |
+-------------------------------------------------------+
```

## File Attachment Preview

When the user adds a file attachment:

```
+-------------------------------------------------------+
| 3. Attachments                                        |
+-------------------------------------------------------+
| +-------------------+  [+ Add Image]  [+ Add File]    |
| | 📄 document.pdf   |                                 |
| | 2.3 MB            |                                 |
| | [Remove]          |                                 |
| +-------------------+                                 |
+-------------------------------------------------------+
```

## Repository Selection Dropdown

When the user clicks the repository dropdown:

```
+-------------------------------------------------------+
| Repository:                                           |
+-------------------------------------------------------+
| +---------------------------------------------------+ |
| | Search repositories...                            | |
| +---------------------------------------------------+ |
| | ● repository-name                                 | |
| | Organization: Org Name                            | |
| |                                                   | |
| | ○ another-repository                              | |
| | Organization: Org Name                            | |
| |                                                   | |
| | ○ third-repository                                | |
| | Organization: Another Org                         | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
```

## Model Selection Dropdown

When the user clicks the model dropdown:

```
+-------------------------------------------------------+
| Model:                                                |
+-------------------------------------------------------+
| +---------------------------------------------------+ |
| | ● GPT-4                                           | |
| | Best for complex tasks and reasoning              | |
| |                                                   | |
| | ○ GPT-3.5 Turbo                                   | |
| | Faster, more economical                           | |
| |                                                   | |
| | ○ Claude                                          | |
| | Alternative model with different capabilities     | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
```

## Prompt Templates

The interface also offers prompt templates to help users get started:

```
+-------------------------------------------------------+
| 2. Prompt                                             |
+-------------------------------------------------------+
| [Load Template ▼]                                     |
|  ├ Code Review                                        |
|  ├ Bug Fix                                            |
|  ├ Feature Implementation                             |
|  ├ Documentation                                      |
|  └ Custom...                                          |
|                                                       |
| +---------------------------------------------------+ |
| | Review the code in the repository and identify    | |
| | potential security vulnerabilities, focusing on   | |
| | input validation and authentication.              | |
| |                                                   | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+
```

## Creation Confirmation

After clicking "Create Run", a confirmation is shown:

```
+-------------------------------------------------------+
| ✓ Agent Run Created Successfully                    ✕ |
+-------------------------------------------------------+
| Agent run #124 has been created and is now pending.   |
|                                                       |
| [View Agent Run]  [Create Another]                    |
+-------------------------------------------------------+
```

## Responsive Behavior

On smaller screens:
- Form sections stack vertically
- Dropdowns expand to full width
- Buttons stack or adapt to available space
- Text areas adjust height based on content

