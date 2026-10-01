#!/usr/bin/env bash
set -uo pipefail

LOG_FILE="${CLAUDE_PLUGIN_ROOT}/log-prompt.log"

INPUT="$(cat)"

# jq fails on non-JSON input; fall back to the raw input
PROMPT="$(echo "$INPUT" | jq -r '.prompt // empty' 2>/dev/null)"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ${PROMPT:-$INPUT}" >> "$LOG_FILE"

exit 0
