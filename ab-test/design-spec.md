# A/B Test: Dashboard Layout

## Design Requirements (Traditional Spec)

Build a dashboard with the following structure:

### Header
- Full width, fixed height
- Logo on the left, user avatar and notification bell on the right
- Notification bell should have a badge counter

### Main Layout
- Left sidebar (roughly 20% width) with navigation items stacked vertically
- Main content area (remaining width) with:
  - Top row: 3 metric cards of equal width
  - Middle section: A large chart (roughly 65% width) next to a smaller activity feed (35% width)
  - Bottom row: A wide table (70% width) next to a compact calendar widget (30% width)

### Metric Cards (x3)
- Icon on the left, vertically centered
- Label above the value on the right
- Small trend indicator (up/down arrow with percentage) below the value

### Activity Feed
- Header with title and "View All" link on opposite ends
- List of activity items, each with:
  - Avatar on left
  - Description text and timestamp stacked on the right

### Calendar Widget
- Month/year header with nav arrows on each side
- 7-column grid for days
- Today highlighted

### Responsive Behavior
- On tablet: sidebar collapses to icons only
- On mobile: sidebar becomes bottom nav, metric cards stack vertically, chart and activity feed stack vertically
