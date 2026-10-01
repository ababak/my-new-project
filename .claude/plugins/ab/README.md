# ab plugin

## Purpose
To learn how to create Claude Code plugins from scratch.

## Install

### Claude Code
Run from the project root (plugin only lives for this session):
```bash
claude --plugin-dir .claude/plugins/ab
```

### VS Code (Copilot)
Add to the **user** `settings.json` (`chat.pluginLocations` is machine-scoped, so the workspace file ignores it; the workspace must be trusted):
```json
"chat.pluginLocations": {
    ".claude/plugins/ab": true
}
```
Relative paths resolve against each open workspace folder. Then reload the window and check Extensions → `@agentPlugins` → Installed.

## Commands
—

## Skills
- **version-up** — triggered when you ask Claude to bump the version number. It opens `resource/version.yml`, increments the minor version (skipping 13), and saves the file.

## Hooks
Logs are written to the plugin root (`$CLAUDE_PLUGIN_ROOT`, i.e. `.claude/plugins/ab/`).
- **UserPromptSubmit** — `log-prompt.sh` appends a timestamp and the submitted prompt to `log-prompt.log`.
- **PreToolUse** — `log-tool.sh` appends the event, tool name, input and environment (secret-looking values redacted) to `log-tool.log`.
