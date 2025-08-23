# Agent Management Interface - Layout Design

## Main Application Layout

The Agent Management Interface follows a responsive layout with three main sections:

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               |                                       |
|               |                                       |
|  Navigation   |  Main Content Area                   |
|  Sidebar      |  (Dashboard/Agent Details/Logs)      |
|               |                                       |
|               |                                       |
|               |                                       |
|               |                                       |
+---------------+---------------------------------------+
|                       Footer                          |
+-------------------------------------------------------+
```

### Header

The header contains:
- Logo and application name
- Organization selector dropdown
- Search bar for finding agents, repositories, or users
- User profile menu with settings, help, and logout options
- Notification bell with counter for alerts

```
+-------------------------------------------------------+
| Logo | Org Selector | Search                | 🔔 | 👤 |
+-------------------------------------------------------+
```

### Navigation Sidebar

The sidebar provides access to the main sections of the application:

```
+---------------+
| Dashboard     |
+---------------+
| Agents        |
|  ├ Active     |
|  ├ Completed  |
|  ├ Failed     |
|  └ All        |
+---------------+
| Repositories  |
+---------------+
| Organizations |
+---------------+
| Users         |
+---------------+
| Settings      |
+---------------+
| Help          |
+---------------+
```

### Main Content Area

The main content area displays the selected view:
- Dashboard with overview statistics and recent activity
- Agent listings with filtering and sorting options
- Agent details with logs, status, and actions
- Repository, organization, and user management views
- Settings and configuration panels

### Footer

The footer contains:
- Copyright information
- Version number
- Links to documentation, API reference, and support
- Status indicator showing API health

## Responsive Design

The layout adapts to different screen sizes:

### Desktop (>1200px)
- Full three-column layout as shown above
- Expanded navigation sidebar
- Rich dashboard visualizations

### Tablet (768px-1200px)
- Collapsible navigation sidebar (toggle button in header)
- Simplified dashboard visualizations
- Responsive tables with horizontal scrolling

### Mobile (<768px)
- Bottom navigation bar instead of sidebar
- Stacked card layout for all content
- Simplified header with essential controls
- Modal dialogs for detailed views

```
+-------------------------------------------------------+
| Logo |                               | 🔍 | 🔔 | ≡ |
+-------------------------------------------------------+
|                                                       |
|                                                       |
|                                                       |
|                 Main Content Area                     |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
+-------------------------------------------------------+
| 🏠 | 🤖 | 📊 | 📁 | 👥 |
+-------------------------------------------------------+
```

## Theme Support

The interface supports both light and dark themes:
- Light theme (default): White background, blue accents, dark text
- Dark theme: Dark background, blue accents, light text
- High contrast theme: For accessibility

Theme selection is available in the user settings and respects system preferences.

