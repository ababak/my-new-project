#!/usr/bin/env bash
set -uo pipefail

LOG_FILE="${CLAUDE_PLUGIN_ROOT}/log-tool.log"

INPUT="$(cat)"

# jq fails on malformed/non-JSON input and fields may be absent, hence the fallbacks
HOOK_TYPE="$(echo "$INPUT" | jq -r '.hook_event_name // empty' 2>/dev/null)"
HOOK_TYPE="${HOOK_TYPE:-unknown}"

# tool_name is only present for tool-related events (PreToolUse/PostToolUse)
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)"
TOOL_NAME="${TOOL_NAME:-n/a}"

{
  printf -- '-%.0s' $(seq 1 80); echo
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) [$HOOK_TYPE] [$TOOL_NAME]"
  echo "$INPUT"
  # echo "env:"
  # # Values of secret-looking variables are masked so the log never holds credentials
  # env | sort | sed -E 's/^([^=]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[^=]*)=.*/\1=***REDACTED***/' | sed 's/^/  /'
} >> "$LOG_FILE"

exit 0
