# Ophanic Plugin for Claude Code

Visual layout diagrams for React components using Unicode box-drawing characters.

## Features

- **`/diagram` command**: Generate layout diagrams from React components
- **`ophanic` agent**: Specialized agent for layout analysis and responsive design

## Installation

### Option 1: Symlink (Development)

```bash
# Create the local plugins directory if it doesn't exist
mkdir -p ~/.claude/plugins/cache/local

# Symlink the plugin
ln -s /path/to/ophanic/plugin ~/.claude/plugins/cache/local/ophanic
```

### Option 2: Manual Registration

Add to `~/.claude/plugins/installed_plugins.json`:

```json
{
  "ophanic@local": [{
    "scope": "user",
    "installPath": "/path/to/ophanic/plugin",
    "version": "1.0.0",
    "installedAt": "2024-01-01T00:00:00.000Z",
    "lastUpdated": "2024-01-01T00:00:00.000Z",
    "isLocal": true
  }]
}
```

## Requirements

The `ophanic` Python package must be installed:

```bash
pip install -e /path/to/ophanic
```

## Usage

### /diagram Command

```bash
# Generate diagram from a React component
/diagram src/pages/Dashboard.tsx

# Specify output file
/diagram src/pages/Chat.tsx -o layouts/chat.oph

# Custom width
/diagram src/components/Layout.tsx --width 100
```

### Ophanic Agent

The agent can be invoked for complex layout tasks:
- Batch diagram generation
- Responsive design planning
- Round-trip editing (diagram ↔ code)

## License

MIT
