# Agent Management Interface - Dashboard Mockup

The dashboard provides a high-level overview of agent activity and system status.

## Dashboard Layout

```
+-------------------------------------------------------+
|                       Header                          |
+---------------+---------------------------------------+
|               |                                       |
|               | +-----------+ +-----------+ +-------+ |
|               | | Active    | | Completed | | Failed| |
|  Navigation   | | Agents    | | Today     | | Today | |
|  Sidebar      | | 12        | | 45        | | 3     | |
|               | +-----------+ +-----------+ +-------+ |
|               |                                       |
|               | +-----------------------------------+ |
|               | | Agent Activity (Last 7 Days)      | |
|               | |                                   | |
|               | | [Line chart showing agent runs]   | |
|               | |                                   | |
|               | +-----------------------------------+ |
|               |                                       |
|               | +-------------------+ +-------------+ |
|               | | Recent Agent Runs | | Top Repos   | |
|               | | • Run #123 (2m)   | | • repo-1    | |
|               | | • Run #122 (15m)  | | • repo-2    | |
|               | | • Run #121 (1h)   | | • repo-3    | |
|               | | • Run #120 (3h)   | | • repo-4    | |
|               | | [View All]        | | [View All]  | |
|               | +-------------------+ +-------------+ |
|               |                                       |
+---------------+---------------------------------------+
```

## Key Metrics Section

The top section displays key metrics as cards with numbers and trends:

```
+-----------+ +-----------+ +-----------+ +-----------+
| Active    | | Completed | | Failed    | | Success   |
| Agents    | | Today     | | Today     | | Rate      |
| 12 ↑2     | | 45 ↑10    | | 3 ↓1      | | 93.8% ↑   |
+-----------+ +-----------+ +-----------+ +-----------+
```

Each metric card includes:
- Metric name
- Current value
- Change indicator (↑ for increase, ↓ for decrease)
- Color coding (green for positive, red for negative trends)

## Agent Activity Chart

A line chart showing agent activity over time:

```
+-------------------------------------------------------+
| Agent Activity (Last 7 Days)                    ⋮    |
+-------------------------------------------------------+
|    ^                                                  |
|    |                                                  |
|    |                 •                                |
|    |                / \                               |
|    |               /   \       •                      |
|    |              /     \     / \                     |
|    |        •    /       \   /   \                    |
|    |       / \  /         \ /     \                   |
|    |      /   \/           •       \                  |
|    |     /                          \                 |
|    |    •                            •                |
|    +------------------------------------------------> |
|      Mon   Tue   Wed   Thu   Fri   Sat   Sun          |
|                                                       |
| Legend: ── Completed  ── Failed  ── Total            |
+-------------------------------------------------------+
```

Features:
- Toggle between daily, weekly, and monthly views
- Hover tooltips with detailed metrics
- Color-coded lines for different statuses
- Option to filter by repository or organization

## Recent Agent Runs

A table showing the most recent agent runs:

```
+-------------------------------------------------------+
| Recent Agent Runs                               ⋮    |
+-------------------------------------------------------+
| ID    | Status    | Repository   | Created    | Actions|
+-------+----------+-------------+------------+--------+
| #123  | ⚪ Pending | repo-name   | 2m ago     | ℹ️ ⏹️   |
| #122  | 🔵 Running | repo-name   | 15m ago    | ℹ️ ⏹️   |
| #121  | ✅ Success | repo-name   | 1h ago     | ℹ️      |
| #120  | ❌ Failed  | repo-name   | 3h ago     | ℹ️ 🔄   |
+-------+----------+-------------+------------+--------+
| [View All Agent Runs]                                 |
+-------------------------------------------------------+
```

Features:
- Status indicators with colors
- Quick access to agent run details
- Action buttons for common operations
- "View All" link to the full agent runs list

## Repository Activity

A card showing the most active repositories:

```
+-------------------------------------------------------+
| Top Repositories                                 ⋮    |
+-------------------------------------------------------+
| Repository        | Runs Today | Success Rate | Trend |
+------------------+-----------+-------------+-------+
| repository-name   | 15        | 93%         | ↗️     |
| another-repo      | 12        | 87%         | →     |
| third-repo        | 8         | 100%        | ↗️     |
| fourth-repo       | 5         | 80%         | ↘️     |
+------------------+-----------+-------------+-------+
| [View All Repositories]                               |
+-------------------------------------------------------+
```

## System Status

A card showing the system status:

```
+-------------------------------------------------------+
| System Status                                    ⋮    |
+-------------------------------------------------------+
| API: ● Online (99.9% uptime)                          |
| Agent Service: ● Online (99.8% uptime)                |
| Database: ● Online (100% uptime)                      |
|                                                       |
| Last Incident: 2 days ago - Scheduled maintenance     |
+-------------------------------------------------------+
```

## Quick Actions

A card with buttons for common actions:

```
+-------------------------------------------------------+
| Quick Actions                                         |
+-------------------------------------------------------+
| [+ New Agent Run] [View Active Runs] [System Settings]|
+-------------------------------------------------------+
```

## Responsive Behavior

On smaller screens, the dashboard adapts:
- Cards stack vertically
- Charts become scrollable horizontally
- Tables show fewer columns with expandable rows
- Quick actions become a dropdown menu

